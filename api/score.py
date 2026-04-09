"""
Vercel Serverless Function: GEOスコアリングAPI
完全ステートレスな一問一答形式で動作
"""
import json
import os
from http.server import BaseHTTPRequestHandler

# 環境変数の設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", "0.1"))


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function ハンドラー"""

    def do_POST(self):
        """
        POSTリクエストを処理

        リクエスト形式:
        {
            "query": "検索クエリ",
            "ai_response": "評価対象のAI応答",
            "brand_name": "評価対象のブランド名",
            "reference_info": "正確性評価用の参照情報（任意）"
        }

        レスポンス形式:
        {
            "visibility_score": 0-10,
            "sentiment_score": -10-30,
            "positioning_score": 0-20,
            "accuracy_score": 0-40,
            "total_score": 合計,
            "reasoning": "スコアリングの根拠"
        }
        """
        try:
            # リクエストボディを読み取り
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))

            # 必須パラメータの確認
            required_fields = ["query", "ai_response", "brand_name"]
            for field in required_fields:
                if field not in request_data:
                    self._send_error(400, f"必須フィールドが不足: {field}")
                    return

            # APIキーの確認
            if not GEMINI_API_KEY:
                self._send_error(500, "GEMINI_API_KEY が設定されていません")
                return

            # スコアリング実行（完全ステートレス）
            result = self._score_geo_response(
                query=request_data["query"],
                ai_response=request_data["ai_response"],
                brand_name=request_data["brand_name"],
                reference_info=request_data.get("reference_info")
            )

            # 成功レスポンス
            self._send_json(200, result)

        except json.JSONDecodeError:
            self._send_error(400, "無効なJSONフォーマット")
        except Exception as e:
            self._send_error(500, str(e))

    def do_GET(self):
        """GETリクエスト（ヘルスチェック用）"""
        self._send_json(200, {
            "status": "ok",
            "message": "GEOスコアリングAPI",
            "version": "1.0.0"
        })

    def _score_geo_response(
        self,
        query: str,
        ai_response: str,
        brand_name: str,
        reference_info: str = None
    ) -> dict:
        """
        GEOスコアリングを実行（完全ステートレス）

        重要: 過去の会話履歴は一切使用しない。
        毎回、システムプロンプトと評価プロンプトのみを送信。
        """
        from google import genai
        from google.genai import types

        # Gemini クライアント初期化（毎回新規）
        client = genai.Client(api_key=GEMINI_API_KEY)

        # システム指示（毎回同じ内容を送信）
        system_instruction = """あなたはGEO（Generative Engine Optimization）の専門家です。
AI検索エンジンの応答を分析し、指定されたブランドの可視性と評価を測定します。
客観的かつ一貫した基準でスコアリングを行ってください。

必ず以下のJSON形式のみで回答してください。余計な説明は不要です。
{
  "visibility_score": 数値,
  "sentiment_score": 数値,
  "positioning_score": 数値,
  "accuracy_score": 数値,
  "total_score": 数値,
  "reasoning": "文字列"
}"""

        # 評価プロンプト（今回の1回分のみ）
        prompt = self._build_scoring_prompt(
            query=query,
            ai_response=ai_response,
            brand_name=brand_name,
            reference_info=reference_info
        )

        # API設定（ステートレス - 履歴なし）
        config = types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            system_instruction=system_instruction,
            response_mime_type="application/json"
        )

        # API呼び出し（単一リクエスト、履歴なし）
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,  # 文字列のみ、messages配列ではない
            config=config
        )

        # レスポンスをパース
        if not response.text:
            raise ValueError("空のレスポンスが返されました")

        return json.loads(response.text)

    def _build_scoring_prompt(
        self,
        query: str,
        ai_response: str,
        brand_name: str,
        reference_info: str = None
    ) -> str:
        """評価プロンプトを構築（今回分のみ）"""
        prompt = f"""以下のAI検索応答を分析し、「{brand_name}」のGEOスコアを評価してください。

## 検索クエリ
{query}

## AI検索応答
{ai_response}

## 評価対象ブランド
{brand_name}
"""
        if reference_info:
            prompt += f"""
## 参照情報（正確性評価用）
{reference_info}
"""

        prompt += """
## 評価基準

### 1. visibility_score（言及の有無）: 0 または 10
- ブランドが言及されていれば 10
- 言及されていなければ 0

### 2. sentiment_score（感情評価）: -10 〜 30
- 強く否定的: -10
- やや否定的: 0
- 中立的: 10
- やや肯定的: 20
- 強く肯定的: 30

### 3. positioning_score（競合内位置づけ）: 0 〜 20
- 言及なし: 0
- リストの下位: 5
- リストの中位: 10
- リストの上位: 15
- 最優先・最初に推薦: 20

### 4. accuracy_score（情報正確性）: 0 〜 40
- 重大な誤情報あり: 0
- 一部不正確: 10〜20
- 概ね正確: 30
- 完全に正確: 40

### 5. total_score
- 上記4つのスコアの合計

### 6. reasoning
- 各スコアを付けた具体的な根拠を日本語で説明
"""
        return prompt

    def _send_json(self, status_code: int, data: dict):
        """JSONレスポンスを送信"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error(self, status_code: int, message: str):
        """エラーレスポンスを送信"""
        self._send_json(status_code, {"error": message})

    def do_OPTIONS(self):
        """CORSプリフライトリクエストを処理"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

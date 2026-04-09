"""
Gemini APIクライアントモジュール
GEOスコアリングのためのGemini API連携を管理
"""
import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel, Field, ValidationError

# google-genai ライブラリを使用
from google import genai
from google.genai import types

# 内部モジュール
from config.settings import settings
from src.api.rate_limiter import RateLimiter, default_rate_limiter

# ログ設定
logger = logging.getLogger(__name__)

# 型変数（Pydanticモデルの型を保持するため）
T = TypeVar("T", bound=BaseModel)


# =============================================================================
# スコアリング用Pydanticスキーマ
# =============================================================================

class GEOScoring(BaseModel):
    """
    GEOスコアリング結果のスキーマ

    各指標:
    - visibility_score: 言及の有無（0 または 10点）
    - sentiment_score: 感情評価（-10 〜 30点）
    - positioning_score: 競合内での位置づけ（0 〜 20点）
    - accuracy_score: 情報の正確性（0 〜 40点）
    - total_score: 合計点数
    - reasoning: スコアの根拠説明
    """
    visibility_score: int = Field(
        ge=0, le=10,
        description="言及の有無スコア: 言及されていれば10、なければ0"
    )
    sentiment_score: int = Field(
        ge=-10, le=30,
        description="感情評価スコア: 否定的(-10)〜中立(0)〜肯定的(30)"
    )
    positioning_score: int = Field(
        ge=0, le=20,
        description="競合内位置づけスコア: 言及なし(0)〜最優先推薦(20)"
    )
    accuracy_score: int = Field(
        ge=0, le=40,
        description="情報正確性スコア: 誤情報(-点数)〜完全正確(40)"
    )
    total_score: int = Field(
        description="合計スコア: 各指標の合計"
    )
    reasoning: str = Field(
        description="スコアリングの根拠・理由の説明"
    )


# =============================================================================
# 例外クラス
# =============================================================================

class GeminiAPIError(Exception):
    """Gemini API関連のエラー"""
    pass


class GeminiConfigError(GeminiAPIError):
    """設定エラー（APIキー未設定など）"""
    pass


class GeminiRequestError(GeminiAPIError):
    """API呼び出しエラー"""
    pass


class GeminiResponseError(GeminiAPIError):
    """レスポンス解析エラー"""
    pass


# =============================================================================
# Gemini APIクライアント
# =============================================================================

class GeminiClient:
    """
    Gemini APIクライアント

    機能:
    - テキスト生成
    - JSON形式での構造化回答取得
    - Pydanticスキーマによるバリデーション
    - レート制限とリトライ機構
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        """
        初期化

        引数:
            api_key: Gemini APIキー（省略時は設定から取得）
            model: 使用するモデル名（省略時は設定から取得）
            temperature: 生成時の温度パラメータ（省略時は設定から取得）
            rate_limiter: レート制限管理（省略時はデフォルトを使用）
        """
        # 設定の読み込み
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE

        # レート制限
        self.rate_limiter = rate_limiter or default_rate_limiter

        # 設定の検証
        self._validate_config()

        # クライアントの初期化
        self._client = genai.Client(api_key=self.api_key)

        logger.info(f"GeminiClient初期化完了: model={self.model}, temperature={self.temperature}")

    def _validate_config(self) -> None:
        """設定の検証"""
        if not self.api_key:
            raise GeminiConfigError(
                "GEMINI_API_KEY が設定されていません。"
                ".envファイルに GEMINI_API_KEY を設定してください。"
            )

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        テキストを生成

        引数:
            prompt: プロンプト（質問・指示）
            system_instruction: システム指示（AIの役割設定）

        戻り値:
            生成されたテキスト

        例外:
            GeminiRequestError: API呼び出しに失敗した場合
        """
        def _call_api() -> str:
            try:
                # 生成設定
                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    system_instruction=system_instruction
                )

                # API呼び出し
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )

                # レスポンスからテキストを抽出
                if response.text:
                    return response.text
                else:
                    raise GeminiResponseError("空のレスポンスが返されました")

            except Exception as e:
                if isinstance(e, (GeminiAPIError,)):
                    raise
                raise GeminiRequestError(f"API呼び出しエラー: {e}") from e

        # リトライ付きで実行
        return self.rate_limiter.with_retry(
            _call_api,
            retryable_exceptions=(GeminiRequestError,)
        )

    def generate_json(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        """
        JSON形式で構造化された回答を生成

        引数:
            prompt: プロンプト（質問・指示）
            response_schema: 期待するレスポンスのPydanticスキーマ
            system_instruction: システム指示（AIの役割設定）

        戻り値:
            指定したスキーマに基づくPydanticモデルインスタンス

        例外:
            GeminiRequestError: API呼び出しに失敗した場合
            GeminiResponseError: レスポンスの解析に失敗した場合
        """
        def _call_api() -> T:
            try:
                # 生成設定（JSON出力モード）
                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema
                )

                # API呼び出し
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )

                # レスポンスからJSONを抽出してパース
                if not response.text:
                    raise GeminiResponseError("空のレスポンスが返されました")

                try:
                    json_data = json.loads(response.text)
                    return response_schema.model_validate(json_data)
                except json.JSONDecodeError as e:
                    raise GeminiResponseError(f"JSONパースエラー: {e}") from e
                except ValidationError as e:
                    raise GeminiResponseError(f"スキーマ検証エラー: {e}") from e

            except Exception as e:
                if isinstance(e, (GeminiAPIError,)):
                    raise
                raise GeminiRequestError(f"API呼び出しエラー: {e}") from e

        # リトライ付きで実行
        return self.rate_limiter.with_retry(
            _call_api,
            retryable_exceptions=(GeminiRequestError,)
        )

    def score_geo_response(
        self,
        query: str,
        ai_response: str,
        brand_name: str,
        reference_info: Optional[str] = None
    ) -> GEOScoring:
        """
        AI応答のGEOスコアリングを実行

        引数:
            query: 元の検索クエリ
            ai_response: 評価対象のAI応答テキスト
            brand_name: 評価対象のブランド名
            reference_info: 正確性評価のための参照情報（任意）

        戻り値:
            GEOScoringモデルインスタンス
        """
        # スコアリング用プロンプトの構築
        prompt = self._build_scoring_prompt(
            query=query,
            ai_response=ai_response,
            brand_name=brand_name,
            reference_info=reference_info
        )

        # システム指示
        system_instruction = """
あなたはGEO（Generative Engine Optimization）の専門家です。
AI検索エンジンの応答を分析し、指定されたブランドの可視性と評価を測定します。
客観的かつ一貫した基準でスコアリングを行ってください。
"""

        # JSON形式でスコアリング結果を取得
        result = self.generate_json(
            prompt=prompt,
            response_schema=GEOScoring,
            system_instruction=system_instruction
        )

        logger.info(
            f"GEOスコアリング完了: brand={brand_name}, total_score={result.total_score}"
        )

        return result

    def evaluate_with_prompt(
        self,
        evaluation_prompt: str,
        text: str,
        context: Optional[dict] = None
    ) -> dict:
        """
        評価プロンプトを使ってテキストを評価（汎用メソッド）

        引数:
            evaluation_prompt: 評価基準を含むプロンプトテンプレート
            text: 評価対象のテキスト
            context: 追加のコンテキスト情報（ブランド名など）

        戻り値:
            評価結果のJSON辞書
        """
        # コンテキストをフォーマット
        context_str = ""
        if context:
            context_items = [f"- {k}: {v}" for k, v in context.items()]
            context_str = "\n".join(context_items)

        # 完全なプロンプトを構築
        full_prompt = f"""## 評価対象テキスト
{text}

## 追加情報
{context_str if context_str else "なし"}

## 評価指示
{evaluation_prompt}

重要: 必ずJSON形式のみで回答してください。余計な説明は不要です。
"""

        def _call_api() -> dict:
            try:
                # 生成設定（JSON出力モード）
                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json"
                )

                # API呼び出し
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config
                )

                # レスポンスからJSONを抽出してパース
                if not response.text:
                    raise GeminiResponseError("空のレスポンスが返されました")

                try:
                    return json.loads(response.text)
                except json.JSONDecodeError as e:
                    raise GeminiResponseError(f"JSONパースエラー: {e}") from e

            except Exception as e:
                if isinstance(e, (GeminiAPIError,)):
                    raise
                raise GeminiRequestError(f"API呼び出しエラー: {e}") from e

        # リトライ付きで実行
        return self.rate_limiter.with_retry(
            _call_api,
            retryable_exceptions=(GeminiRequestError,)
        )

    def _build_scoring_prompt(
        self,
        query: str,
        ai_response: str,
        brand_name: str,
        reference_info: Optional[str] = None
    ) -> str:
        """スコアリング用プロンプトを構築"""
        prompt = f"""
以下のAI検索応答を分析し、「{brand_name}」のGEOスコアを評価してください。

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
- 各スコアを付けた具体的な根拠を日本語で説明してください

各項目を評価し、JSON形式で回答してください。
"""
        return prompt


# =============================================================================
# シングルトンインスタンス
# =============================================================================

# 遅延初期化用の変数
_client_instance: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    GeminiClientのシングルトンインスタンスを取得

    初回呼び出し時にインスタンスを作成し、以降は同じインスタンスを返す
    """
    global _client_instance

    if _client_instance is None:
        _client_instance = GeminiClient()

    return _client_instance

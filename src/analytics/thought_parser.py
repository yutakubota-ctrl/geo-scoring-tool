"""
思考プロセス解析モジュール

ChatGPT o1の思考プロセス（reasoning_content）をClaude APIで構造化分析する。
7ステップの推論プロセスを抽出し、各ステップで参照した情報源を特定する。

v2.1_video_implementation_guide.md 手法#10に基づく実装
"""

import json
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ThoughtParser:
    """
    ChatGPT o1の思考プロセスを7ステップに構造化するパーサー
    """

    def __init__(self, anthropic_api_key: str):
        """
        初期化

        Args:
            anthropic_api_key: Anthropic APIキー
        """
        self.claude_client = Anthropic(api_key=anthropic_api_key)
        self.model = "claude-sonnet-4-5"

    def parse_thinking(
        self,
        thinking_content: str,
        final_answer: str,
        query: str
    ) -> Dict:
        """
        思考プロセスを7ステップに構造化

        Args:
            thinking_content: ChatGPT o1のreasoning_content
            final_answer: ChatGPTの最終回答
            query: 元の検索クエリ

        Returns:
            7ステップに構造化された思考プロセス
        """
        logger.info(f"[ThoughtParser] 思考プロセス分析開始: {query}")

        try:
            # Claude APIで思考プロセスを構造化
            analysis = self._analyze_with_claude(
                thinking_content,
                final_answer,
                query
            )

            logger.info(f"[ThoughtParser] 分析完了: {len(analysis.get('7ステップの分解', {}))}ステップ抽出")
            return analysis

        except Exception as e:
            logger.error(f"[ThoughtParser] 分析エラー: {str(e)}")
            raise

    def _analyze_with_claude(
        self,
        thinking: str,
        answer: str,
        query: str
    ) -> Dict:
        """
        Claudeで思考プロセスを構造化（内部メソッド）

        Args:
            thinking: 思考プロセステキスト
            answer: 最終回答
            query: 検索クエリ

        Returns:
            構造化された分析結果
        """
        prompt = self._build_analysis_prompt(thinking, answer, query)

        logger.debug(f"[ThoughtParser] Claude API呼び出し（モデル: {self.model}）")

        response = self.claude_client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # レスポンスからJSONを抽出
        analysis_text = response.content[0].text
        return self._extract_json(analysis_text)

    def _build_analysis_prompt(
        self,
        thinking: str,
        answer: str,
        query: str
    ) -> str:
        """
        Claude分析用のプロンプトを構築

        Args:
            thinking: 思考プロセス
            answer: 最終回答
            query: 検索クエリ

        Returns:
            分析プロンプト
        """
        return f"""
以下はChatGPT o1の推論プロセスです。

【検索クエリ】
{query}

【ChatGPTの思考プロセス】
{thinking[:3000]}

【ChatGPTの最終回答】
{answer[:1000]}

この推論プロセスを分析し、以下をJSON形式で抽出してください：

1. **7ステップの分解**:
   - step_1: 候補ブランド・サービスの列挙
   - step_2: 公式サイトの確認
   - step_3: 第三者レビューサイトの参照
   - step_4: 公的機関・信頼できる情報源の確認
   - step_5: 料金・機能の比較
   - step_6: 口コミ・評判の確認
   - step_7: 最終判断・推薦順位の決定

   各ステップには、具体的な内容を1-2文で記述してください。
   該当するステップがない場合は「該当なし」と記述してください。

2. **検索クエリ候補**: ChatGPTが内部で使用したと推測される検索クエリ（5件程度）

3. **参照URL**: 言及されたドメイン・サイト（完全なURLでなくドメイン名でOK）

4. **最終推論**: なぜそのブランドを選んだか（1-2文）

5. **ブランドメンション**: 言及されたブランド名とその評価（ポジティブ/ニュートラル/ネガティブ）

以下のJSON形式で返してください：

```json
{{
  "7ステップの分解": {{
    "step_1": "説明文",
    "step_2": "説明文",
    "step_3": "説明文",
    "step_4": "説明文",
    "step_5": "説明文",
    "step_6": "説明文",
    "step_7": "説明文"
  }},
  "検索クエリ候補": ["クエリ1", "クエリ2", ...],
  "参照URL": ["domain1.com", "domain2.com", ...],
  "最終推論": "推論文",
  "ブランドメンション": [
    {{"brand": "ブランド名", "sentiment": "positive/neutral/negative"}}
  ]
}}
```

JSONのみを返してください。説明文は不要です。
"""

    def _extract_json(self, text: str) -> Dict:
        """
        テキストからJSON部分を抽出してパース

        Args:
            text: Claude APIのレスポンステキスト

        Returns:
            パース済みのJSON辞書
        """
        try:
            # ```json ... ``` ブロックを探す
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                json_str = text[json_start:json_end].strip()
            elif "```" in text:
                # 単純な ```...``` ブロック
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                json_str = text[json_start:json_end].strip()
            else:
                # JSONブロックがない場合はテキスト全体を試行
                json_str = text.strip()

            # JSONパース
            parsed = json.loads(json_str)
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"[ThoughtParser] JSON解析エラー: {str(e)}")
            logger.debug(f"[ThoughtParser] 問題のテキスト: {text[:500]}")

            # フォールバック: デフォルト構造を返す
            return {
                "7ステップの分解": {
                    "step_1": "解析失敗",
                    "step_2": "解析失敗",
                    "step_3": "解析失敗",
                    "step_4": "解析失敗",
                    "step_5": "解析失敗",
                    "step_6": "解析失敗",
                    "step_7": "解析失敗"
                },
                "検索クエリ候補": [],
                "参照URL": [],
                "最終推論": "解析エラーが発生しました",
                "ブランドメンション": []
            }

    def validate_analysis(self, analysis: Dict) -> bool:
        """
        分析結果が有効な構造を持っているか検証

        Args:
            analysis: 分析結果

        Returns:
            有効な場合True
        """
        required_keys = [
            "7ステップの分解",
            "検索クエリ候補",
            "参照URL",
            "最終推論",
            "ブランドメンション"
        ]

        # 必須キーの存在確認
        for key in required_keys:
            if key not in analysis:
                logger.warning(f"[ThoughtParser] 必須キー不足: {key}")
                return False

        # 7ステップの確認
        steps = analysis["7ステップの分解"]
        if not isinstance(steps, dict):
            logger.warning("[ThoughtParser] 7ステップがdict型ではない")
            return False

        # 少なくとも5ステップは抽出できているか
        non_empty_steps = sum(
            1 for v in steps.values()
            if v and v != "該当なし" and v != "解析失敗"
        )
        if non_empty_steps < 5:
            logger.warning(f"[ThoughtParser] 抽出ステップが不足: {non_empty_steps}/7")
            return False

        logger.info("[ThoughtParser] 分析結果は有効な構造を持っています")
        return True


class MockThoughtParser:
    """
    モックパーサー（開発・テスト用）

    実際のAPIを呼ばずにダミーデータを返す
    """

    def parse_thinking(
        self,
        thinking_content: str,
        final_answer: str,
        query: str
    ) -> Dict:
        """
        モック分析結果を返す

        Args:
            thinking_content: 思考プロセス（未使用）
            final_answer: 最終回答（未使用）
            query: 検索クエリ

        Returns:
            ダミーの分析結果
        """
        logger.info(f"[MockThoughtParser] モック分析実行: {query}")

        return {
            "7ステップの分解": {
                "step_1": "HubSpot, Marketo, Salesforce等を候補として列挙",
                "step_2": "HubSpot公式サイト（hubspot.com）を確認し、機能概要を把握",
                "step_3": "G2.com、Capterra等のレビューサイトで評価を参照",
                "step_4": "該当なし",
                "step_5": "各ツールの料金プランを比較し、中小企業向けかエンタープライズ向けかを判断",
                "step_6": "Twitter、Redditでの口コミを確認",
                "step_7": "HubSpotは中小企業向け、Marketoは大企業向けと判断し、推奨順位を決定"
            },
            "検索クエリ候補": [
                "marketing automation tools comparison",
                "HubSpot pricing 2026",
                "Marketo vs HubSpot",
                "Salesforce Marketing Cloud review",
                "best marketing tools for small business"
            ],
            "参照URL": [
                "hubspot.com",
                "g2.com",
                "capterra.com",
                "salesforce.com",
                "marketo.com"
            ],
            "最終推論": "HubSpotは中小企業向けで使いやすく、Marketoはエンタープライズ向けで高機能だが複雑と判断",
            "ブランドメンション": [
                {"brand": "HubSpot", "sentiment": "positive"},
                {"brand": "Marketo", "sentiment": "neutral"},
                {"brand": "Salesforce", "sentiment": "positive"}
            ]
        }

    def validate_analysis(self, analysis: Dict) -> bool:
        """常にTrueを返す"""
        return True

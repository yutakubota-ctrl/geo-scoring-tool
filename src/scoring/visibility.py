"""
認知スコアラー（Visibility Scorer）
ブランドがAI回答に含まれているかを評価
"""
import logging
from typing import Optional

from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.scoring.base_scorer import BaseScorer, ScoringResult, ScoringError

# ログ設定
logger = logging.getLogger(__name__)


class VisibilityScorer(BaseScorer):
    """
    認知スコアを計算するクラス

    評価基準:
    - ブランド名がテキストに含まれているか（0 or 10点）
    - 単純な文字列マッチングではなく、文脈を考慮した判定を行う
    """

    # 評価プロンプトテンプレート
    EVALUATION_PROMPT = """
あなたは「ブランド認知度評価」の専門家です。
以下のテキストを分析し、指定されたブランドが言及されているかを判定してください。

## 評価対象ブランド
{brand_name}

## 判定基準
1. ブランド名が直接言及されている（正式名称、略称、通称を含む）
2. ブランドの製品・サービスが明確に識別可能な形で言及されている
3. 文脈からブランドを特定できる記述がある

## 出力形式（JSON）
{{
    "is_mentioned": true または false,
    "mention_type": "direct"（直接言及）/ "indirect"（間接的言及）/ "none"（言及なし）,
    "found_mentions": ["発見された言及のリスト"],
    "reasoning": "判定理由の説明"
}}

注意:
- 類似名称や競合ブランドとの混同に注意してください
- 曖昧な場合は言及なしと判定してください
"""

    def __init__(self, client: Optional[GeminiClient] = None):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
        """
        super().__init__(
            client=client,
            max_score=settings.MAX_VISIBILITY_SCORE,
            min_score=0
        )

    @property
    def scorer_name(self) -> str:
        """スコアラー名"""
        return "認知スコアラー"

    def score(self, text: str, brand_name: str, **kwargs) -> ScoringResult:
        """
        認知スコアを計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名

        戻り値:
            ScoringResult: スコア（0 or 10）と評価詳細
        """
        # 評価プロンプトを構築
        prompt = self.EVALUATION_PROMPT.format(brand_name=brand_name)

        try:
            # Gemini APIで評価を実行
            result = self.client.evaluate_with_prompt(
                evaluation_prompt=prompt,
                text=text,
                context={"ブランド名": brand_name}
            )

            # 結果を解析
            is_mentioned = result.get("is_mentioned", False)
            mention_type = result.get("mention_type", "none")
            reasoning = result.get("reasoning", "評価理由が取得できませんでした")
            found_mentions = result.get("found_mentions", [])

            # スコアを決定
            if is_mentioned and mention_type in ["direct", "indirect"]:
                score = self.max_score
            else:
                score = 0

            # 詳細な評価理由を構築
            if found_mentions:
                detail_reasoning = f"{reasoning}\n発見された言及: {', '.join(found_mentions)}"
            else:
                detail_reasoning = reasoning

            return ScoringResult(
                score=score,
                reasoning=detail_reasoning,
                raw_response=result
            )

        except Exception as e:
            logger.error(f"認知スコア評価エラー: {e}")
            raise ScoringError(f"認知スコアの評価に失敗しました: {e}") from e

    def quick_check(self, text: str, brand_name: str) -> bool:
        """
        簡易的なブランド名チェック（API呼び出しなし）

        完全一致または部分一致で素早く判定する
        正確性が必要な場合はscore()メソッドを使用すること

        引数:
            text: 評価対象のテキスト
            brand_name: ブランド名

        戻り値:
            ブランド名が含まれている可能性がある場合はTrue
        """
        # 大文字小文字を無視して検索
        text_lower = text.lower()
        brand_lower = brand_name.lower()

        # 直接一致
        if brand_lower in text_lower:
            return True

        # スペースやハイフンを除去して検索
        text_normalized = text_lower.replace(" ", "").replace("-", "").replace("_", "")
        brand_normalized = brand_lower.replace(" ", "").replace("-", "").replace("_", "")

        return brand_normalized in text_normalized

"""
推奨度・感情スコアラー（Sentiment Scorer）
テキストの感情極性とブランドへの推奨度を評価
"""
import logging
from typing import Optional

from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.scoring.base_scorer import BaseScorer, ScoringResult, ScoringError

# ログ設定
logger = logging.getLogger(__name__)


class SentimentScorer(BaseScorer):
    """
    推奨度・感情スコアを計算するクラス

    評価基準:
    - 強い推奨: 30点（「最もおすすめ」「絶対に」などの強い表現）
    - 中程度の推奨: 20点（「おすすめ」「良い選択肢」など）
    - 弱い推奨: 10点（「検討に値する」「選択肢の一つ」など）
    - 中立: 0点（事実のみの記述、評価なし）
    - 軽い否定: -5点（「やや注意が必要」「いくつか課題がある」など）
    - 強い否定: -10点（「おすすめしない」「避けるべき」など）
    """

    # 評価プロンプトテンプレート
    EVALUATION_PROMPT = """
あなたは「感情分析・推奨度評価」の専門家です。
以下のテキストを分析し、指定されたブランドに対する感情と推奨度を評価してください。

## 評価対象ブランド
{brand_name}

## 評価基準
以下の段階で評価してください：

1. **強い推奨（30点）**
   - 「最もおすすめ」「絶対に選ぶべき」「間違いない選択」
   - 他の選択肢よりも明確に優れていると述べている
   - 熱心に推奨している

2. **中程度の推奨（20点）**
   - 「おすすめ」「良い選択肢」「検討する価値あり」
   - ポジティブな評価だが、最上級ではない

3. **弱い推奨（10点）**
   - 「選択肢の一つ」「条件次第では良い」
   - 限定的な推奨や条件付きの肯定

4. **中立（0点）**
   - 事実のみの記述で評価がない
   - ブランドへの言及がない場合も含む

5. **軽い否定（-5点）**
   - 「いくつか課題がある」「注意が必要」
   - ネガティブな点に言及しているが強くない

6. **強い否定（-10点）**
   - 「おすすめしない」「避けるべき」「問題が多い」
   - 明確に否定的な評価

## 出力形式（JSON）
{{
    "sentiment_level": "strong_positive" / "moderate_positive" / "weak_positive" / "neutral" / "weak_negative" / "strong_negative",
    "score": 数値（-10〜30）,
    "positive_phrases": ["ポジティブな表現のリスト"],
    "negative_phrases": ["ネガティブな表現のリスト"],
    "reasoning": "評価理由の詳細な説明"
}}

注意:
- ブランドに関する記述のみを評価対象としてください
- 文脈を考慮し、皮肉や反語表現に注意してください
- 複数の感情が混在する場合は、全体的な印象で判断してください
"""

    # 感情レベルとスコアのマッピング
    SENTIMENT_SCORES = {
        "strong_positive": 30,
        "moderate_positive": 20,
        "weak_positive": 10,
        "neutral": 0,
        "weak_negative": -5,
        "strong_negative": -10
    }

    def __init__(self, client: Optional[GeminiClient] = None):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
        """
        super().__init__(
            client=client,
            max_score=settings.MAX_SENTIMENT_SCORE,
            min_score=settings.MIN_SENTIMENT_SCORE
        )

    @property
    def scorer_name(self) -> str:
        """スコアラー名"""
        return "推奨度・感情スコアラー"

    def score(self, text: str, brand_name: str, **kwargs) -> ScoringResult:
        """
        推奨度・感情スコアを計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名

        戻り値:
            ScoringResult: スコア（-10〜30）と評価詳細
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
            sentiment_level = result.get("sentiment_level", "neutral")
            raw_score = result.get("score")
            reasoning = result.get("reasoning", "評価理由が取得できませんでした")
            positive_phrases = result.get("positive_phrases", [])
            negative_phrases = result.get("negative_phrases", [])

            # スコアを決定
            if raw_score is not None:
                score = int(raw_score)
            else:
                score = self.SENTIMENT_SCORES.get(sentiment_level, 0)

            # 詳細な評価理由を構築
            detail_parts = [reasoning]
            if positive_phrases:
                detail_parts.append(f"ポジティブ表現: {', '.join(positive_phrases)}")
            if negative_phrases:
                detail_parts.append(f"ネガティブ表現: {', '.join(negative_phrases)}")

            return ScoringResult(
                score=score,
                reasoning="\n".join(detail_parts),
                raw_response=result
            )

        except Exception as e:
            logger.error(f"感情スコア評価エラー: {e}")
            raise ScoringError(f"感情スコアの評価に失敗しました: {e}") from e

    def get_sentiment_label(self, score: int) -> str:
        """
        スコアから感情ラベルを取得

        引数:
            score: 感情スコア

        戻り値:
            感情ラベル（日本語）
        """
        if score >= 25:
            return "強い推奨"
        elif score >= 15:
            return "中程度の推奨"
        elif score >= 5:
            return "弱い推奨"
        elif score >= -2:
            return "中立"
        elif score >= -7:
            return "軽い否定"
        else:
            return "強い否定"

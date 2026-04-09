"""
掲載ポジションスコアラー（Positioning Scorer）
テキスト内でのブランド言及位置を評価
"""
import logging
from typing import Optional

from config.settings import settings
from src.api.gemini_client import GeminiClient
from src.scoring.base_scorer import BaseScorer, ScoringResult, ScoringError

# ログ設定
logger = logging.getLogger(__name__)


class PositioningScorer(BaseScorer):
    """
    掲載ポジションスコアを計算するクラス

    評価基準:
    - 最初に言及（最上位）: 20点
    - 上位に言及（2〜3番目）: 15点
    - 中位に言及（4〜5番目）: 10点
    - 下位に言及（6番目以降）: 5点
    - 言及なし: 0点

    先頭に近いほど、読者に認識されやすく影響力が大きい
    """

    # 評価プロンプトテンプレート
    EVALUATION_PROMPT = """
あなたは「コンテンツ配置分析」の専門家です。
以下のテキストを分析し、指定されたブランドの掲載位置を評価してください。

## 評価対象ブランド
{brand_name}

## 評価基準

### リスト形式の場合
複数のブランドや製品がリスト形式で紹介されている場合：
1. **最上位（20点）**: 1番目に言及されている
2. **上位（15点）**: 2〜3番目に言及されている
3. **中位（10点）**: 4〜5番目に言及されている
4. **下位（5点）**: 6番目以降に言及されている
5. **言及なし（0点）**: リストに含まれていない

### 文章形式の場合
段落や文章で紹介されている場合：
1. **冒頭（20点）**: テキストの最初の1/4以内で言及
2. **前半（15点）**: テキストの1/4〜1/2で言及
3. **中盤（10点）**: テキストの1/2〜3/4で言及
4. **後半（5点）**: テキストの3/4以降で言及
5. **言及なし（0点）**: テキストに含まれていない

### 強調表示の考慮
- 見出しに含まれる場合は+追加評価
- 「特におすすめ」等の強調がある場合は+追加評価

## 出力形式（JSON）
{{
    "is_mentioned": true または false,
    "format_type": "list"（リスト形式）/ "paragraph"（文章形式）/ "mixed"（混合）,
    "position_rank": 順位（1から始まる数値、言及なしの場合は0）,
    "position_category": "top"（最上位）/ "high"（上位）/ "middle"（中位）/ "low"（下位）/ "none"（言及なし）,
    "total_items": リスト内の総アイテム数（文章形式の場合は0）,
    "text_position_percentage": テキスト内での出現位置（0-100%、言及なしの場合はnull）,
    "has_emphasis": true または false（見出しや強調があるか）,
    "score": 最終スコア（0〜20）,
    "reasoning": "評価理由の詳細な説明"
}}
"""

    # ポジションカテゴリとスコアのマッピング
    POSITION_SCORES = {
        "top": 20,
        "high": 15,
        "middle": 10,
        "low": 5,
        "none": 0
    }

    def __init__(self, client: Optional[GeminiClient] = None):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
        """
        super().__init__(
            client=client,
            max_score=settings.MAX_POSITIONING_SCORE,
            min_score=0
        )

    @property
    def scorer_name(self) -> str:
        """スコアラー名"""
        return "掲載ポジションスコアラー"

    def score(self, text: str, brand_name: str, **kwargs) -> ScoringResult:
        """
        掲載ポジションスコアを計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名

        戻り値:
            ScoringResult: スコア（0〜20）と評価詳細
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
            format_type = result.get("format_type", "paragraph")
            position_rank = result.get("position_rank", 0)
            position_category = result.get("position_category", "none")
            total_items = result.get("total_items", 0)
            text_position = result.get("text_position_percentage")
            has_emphasis = result.get("has_emphasis", False)
            raw_score = result.get("score")
            reasoning = result.get("reasoning", "評価理由が取得できませんでした")

            # スコアを決定
            if raw_score is not None:
                score = int(raw_score)
            else:
                score = self.POSITION_SCORES.get(position_category, 0)

            # 詳細な評価理由を構築
            detail_parts = [reasoning]

            if is_mentioned:
                if format_type == "list" and position_rank > 0:
                    detail_parts.append(f"形式: リスト、順位: {position_rank}/{total_items}")
                elif text_position is not None:
                    detail_parts.append(f"形式: 文章、出現位置: テキストの{text_position}%付近")

                if has_emphasis:
                    detail_parts.append("強調表示: あり")
            else:
                detail_parts.append("ブランドの言及: なし")

            return ScoringResult(
                score=score,
                reasoning="\n".join(detail_parts),
                raw_response=result
            )

        except Exception as e:
            logger.error(f"ポジションスコア評価エラー: {e}")
            raise ScoringError(f"ポジションスコアの評価に失敗しました: {e}") from e

    def get_position_label(self, score: int) -> str:
        """
        スコアからポジションラベルを取得

        引数:
            score: ポジションスコア

        戻り値:
            ポジションラベル（日本語）
        """
        if score >= 18:
            return "最上位（1位）"
        elif score >= 13:
            return "上位（2-3位）"
        elif score >= 8:
            return "中位（4-5位）"
        elif score >= 3:
            return "下位（6位以降）"
        else:
            return "言及なし"

    def estimate_position_simple(self, text: str, brand_name: str) -> Optional[float]:
        """
        簡易的な位置推定（API呼び出しなし）

        テキスト内でのブランド名の出現位置を0-100%で返す

        引数:
            text: 評価対象のテキスト
            brand_name: ブランド名

        戻り値:
            出現位置（0-100%）、見つからない場合はNone
        """
        text_lower = text.lower()
        brand_lower = brand_name.lower()

        # ブランド名の出現位置を検索
        position = text_lower.find(brand_lower)

        if position == -1:
            return None

        # テキスト全体における位置を%で計算
        percentage = (position / len(text)) * 100
        return round(percentage, 1)

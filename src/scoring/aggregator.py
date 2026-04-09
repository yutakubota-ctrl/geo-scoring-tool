"""
総合スコア集計モジュール（Score Aggregator）
4つのスコアラーを統合し、一括スコアリングを実行
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from src.api.gemini_client import GeminiClient, get_gemini_client
from src.scoring.base_scorer import ScoringResult
from src.scoring.visibility import VisibilityScorer
from src.scoring.sentiment import SentimentScorer
from src.scoring.positioning import PositioningScorer
from src.scoring.accuracy import AccuracyScorer

# ログ設定
logger = logging.getLogger(__name__)


@dataclass
class AggregatedScore:
    """
    集計されたスコアを格納するデータクラス

    属性:
        visibility: 認知スコア結果
        sentiment: 推奨度・感情スコア結果
        positioning: 掲載ポジションスコア結果
        accuracy: 情報正確性スコア結果
        total_score: 総合スコア
        brand_name: 評価対象ブランド名
        evaluated_at: 評価日時
        errors: 発生したエラーのリスト
    """
    visibility: ScoringResult
    sentiment: ScoringResult
    positioning: ScoringResult
    accuracy: ScoringResult
    total_score: int
    brand_name: str
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    errors: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """すべての評価が成功したかどうか"""
        return (
            self.visibility.is_success and
            self.sentiment.is_success and
            self.positioning.is_success and
            self.accuracy.is_success
        )

    @property
    def visibility_score(self) -> int:
        """認知スコア"""
        return self.visibility.score

    @property
    def sentiment_score(self) -> int:
        """推奨度・感情スコア"""
        return self.sentiment.score

    @property
    def positioning_score(self) -> int:
        """掲載ポジションスコア"""
        return self.positioning.score

    @property
    def accuracy_score(self) -> int:
        """情報正確性スコア"""
        return self.accuracy.score

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "brand_name": self.brand_name,
            "total_score": self.total_score,
            "visibility_score": self.visibility_score,
            "sentiment_score": self.sentiment_score,
            "positioning_score": self.positioning_score,
            "accuracy_score": self.accuracy_score,
            "visibility_detail": {
                "score": self.visibility.score,
                "reasoning": self.visibility.reasoning,
                "error": self.visibility.error
            },
            "sentiment_detail": {
                "score": self.sentiment.score,
                "reasoning": self.sentiment.reasoning,
                "error": self.sentiment.error
            },
            "positioning_detail": {
                "score": self.positioning.score,
                "reasoning": self.positioning.reasoning,
                "error": self.positioning.error
            },
            "accuracy_detail": {
                "score": self.accuracy.score,
                "reasoning": self.accuracy.reasoning,
                "error": self.accuracy.error
            },
            "evaluated_at": self.evaluated_at.isoformat(),
            "is_complete": self.is_complete,
            "errors": self.errors
        }


class ScoreAggregator:
    """
    複数のスコアラーを統合し、一括スコアリングを実行するクラス

    機能:
    - 4つのスコアラー（認知・感情・ポジション・正確性）の統合
    - 一括スコアリングの実行
    - 結果のScoreモデルへの変換
    """

    def __init__(self, client: Optional[GeminiClient] = None):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
        """
        self._client = client

        # 各スコアラーの初期化（遅延初期化）
        self._visibility_scorer: Optional[VisibilityScorer] = None
        self._sentiment_scorer: Optional[SentimentScorer] = None
        self._positioning_scorer: Optional[PositioningScorer] = None
        self._accuracy_scorer: Optional[AccuracyScorer] = None

        logger.info("ScoreAggregator初期化完了")

    @property
    def client(self) -> GeminiClient:
        """Geminiクライアントを取得（遅延初期化）"""
        if self._client is None:
            self._client = get_gemini_client()
        return self._client

    @property
    def visibility_scorer(self) -> VisibilityScorer:
        """認知スコアラーを取得（遅延初期化）"""
        if self._visibility_scorer is None:
            self._visibility_scorer = VisibilityScorer(client=self.client)
        return self._visibility_scorer

    @property
    def sentiment_scorer(self) -> SentimentScorer:
        """感情スコアラーを取得（遅延初期化）"""
        if self._sentiment_scorer is None:
            self._sentiment_scorer = SentimentScorer(client=self.client)
        return self._sentiment_scorer

    @property
    def positioning_scorer(self) -> PositioningScorer:
        """ポジションスコアラーを取得（遅延初期化）"""
        if self._positioning_scorer is None:
            self._positioning_scorer = PositioningScorer(client=self.client)
        return self._positioning_scorer

    @property
    def accuracy_scorer(self) -> AccuracyScorer:
        """正確性スコアラーを取得（遅延初期化）"""
        if self._accuracy_scorer is None:
            self._accuracy_scorer = AccuracyScorer(client=self.client)
        return self._accuracy_scorer

    def score_all(
        self,
        text: str,
        brand_name: str,
        reference_info: Optional[str] = None
    ) -> AggregatedScore:
        """
        すべてのスコアを一括計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名
            reference_info: 正確性検証用の参照情報（オプション）

        戻り値:
            AggregatedScore: 集計されたスコア
        """
        logger.info(f"一括スコアリング開始: brand={brand_name}")
        errors = []

        # 1. 認知スコア
        visibility_result = self.visibility_scorer.safe_score(text, brand_name)
        if not visibility_result.is_success:
            errors.append(f"認知スコア: {visibility_result.error}")

        # 2. 感情スコア
        sentiment_result = self.sentiment_scorer.safe_score(text, brand_name)
        if not sentiment_result.is_success:
            errors.append(f"感情スコア: {sentiment_result.error}")

        # 3. ポジションスコア
        positioning_result = self.positioning_scorer.safe_score(text, brand_name)
        if not positioning_result.is_success:
            errors.append(f"ポジションスコア: {positioning_result.error}")

        # 4. 正確性スコア
        accuracy_result = self.accuracy_scorer.safe_score(
            text, brand_name, reference_info=reference_info
        )
        if not accuracy_result.is_success:
            errors.append(f"正確性スコア: {accuracy_result.error}")

        # 総合スコアを計算
        total_score = (
            visibility_result.score +
            sentiment_result.score +
            positioning_result.score +
            accuracy_result.score
        )

        aggregated = AggregatedScore(
            visibility=visibility_result,
            sentiment=sentiment_result,
            positioning=positioning_result,
            accuracy=accuracy_result,
            total_score=total_score,
            brand_name=brand_name,
            errors=errors
        )

        logger.info(
            f"一括スコアリング完了: brand={brand_name}, "
            f"total={total_score}, complete={aggregated.is_complete}"
        )

        return aggregated

    def score_visibility_only(self, text: str, brand_name: str) -> ScoringResult:
        """認知スコアのみを計算"""
        return self.visibility_scorer.safe_score(text, brand_name)

    def score_sentiment_only(self, text: str, brand_name: str) -> ScoringResult:
        """感情スコアのみを計算"""
        return self.sentiment_scorer.safe_score(text, brand_name)

    def score_positioning_only(self, text: str, brand_name: str) -> ScoringResult:
        """ポジションスコアのみを計算"""
        return self.positioning_scorer.safe_score(text, brand_name)

    def score_accuracy_only(
        self,
        text: str,
        brand_name: str,
        reference_info: Optional[str] = None
    ) -> ScoringResult:
        """正確性スコアのみを計算"""
        return self.accuracy_scorer.safe_score(
            text, brand_name, reference_info=reference_info
        )


def create_score_model_from_aggregated(
    aggregated: AggregatedScore,
    response_id: int,
    brand_id: int
) -> dict:
    """
    AggregatedScoreからScoreモデル用の辞書を作成

    引数:
        aggregated: 集計されたスコア
        response_id: 関連するResponseのID
        brand_id: 関連するBrandのID

    戻り値:
        Scoreモデル作成用の辞書
    """
    return {
        "response_id": response_id,
        "brand_id": brand_id,
        "visibility_score": aggregated.visibility_score,
        "sentiment_score": aggregated.sentiment_score,
        "positioning_score": aggregated.positioning_score,
        "accuracy_score": aggregated.accuracy_score,
        "total_score": aggregated.total_score,
        "visibility_detail": {
            "score": aggregated.visibility.score,
            "reasoning": aggregated.visibility.reasoning,
            "raw_response": aggregated.visibility.raw_response
        },
        "sentiment_detail": {
            "score": aggregated.sentiment.score,
            "reasoning": aggregated.sentiment.reasoning,
            "raw_response": aggregated.sentiment.raw_response
        },
        "positioning_detail": {
            "score": aggregated.positioning.score,
            "reasoning": aggregated.positioning.reasoning,
            "raw_response": aggregated.positioning.raw_response
        },
        "accuracy_detail": {
            "score": aggregated.accuracy.score,
            "reasoning": aggregated.accuracy.reasoning,
            "raw_response": aggregated.accuracy.raw_response
        }
    }


# シングルトンインスタンス（遅延初期化）
_aggregator_instance: Optional[ScoreAggregator] = None


def get_score_aggregator() -> ScoreAggregator:
    """
    ScoreAggregatorのシングルトンインスタンスを取得

    戻り値:
        ScoreAggregatorインスタンス
    """
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = ScoreAggregator()
    return _aggregator_instance

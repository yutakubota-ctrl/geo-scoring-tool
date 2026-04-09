"""
スコアリングパッケージ
GEOスコアリングの各指標を評価するモジュール群
"""

# 基底クラス
from src.scoring.base_scorer import (
    BaseScorer,
    ScoringResult,
    ScoringError
)

# 各スコアラー
from src.scoring.visibility import VisibilityScorer
from src.scoring.sentiment import SentimentScorer
from src.scoring.positioning import PositioningScorer
from src.scoring.accuracy import AccuracyScorer

# 集計
from src.scoring.aggregator import (
    ScoreAggregator,
    AggregatedScore,
    get_score_aggregator,
    create_score_model_from_aggregated
)

__all__ = [
    # 基底クラス
    "BaseScorer",
    "ScoringResult",
    "ScoringError",
    # スコアラー
    "VisibilityScorer",
    "SentimentScorer",
    "PositioningScorer",
    "AccuracyScorer",
    # 集計
    "ScoreAggregator",
    "AggregatedScore",
    "get_score_aggregator",
    "create_score_model_from_aggregated",
]

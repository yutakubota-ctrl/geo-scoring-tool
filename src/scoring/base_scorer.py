"""
スコアラー基底クラス
すべてのスコアリングロジックの共通基盤を提供
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import logging

from src.api.gemini_client import GeminiClient, get_gemini_client

# ログ設定
logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    """
    スコアリング結果を格納するデータクラス

    属性:
        score: 計算されたスコア値
        reasoning: 評価の根拠・説明
        raw_response: APIからの生のレスポンス（デバッグ用）
        error: エラーが発生した場合のメッセージ
    """
    score: int
    reasoning: str
    raw_response: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """評価が成功したかどうか"""
        return self.error is None


class ScoringError(Exception):
    """スコアリング処理のエラー"""
    pass


class BaseScorer(ABC):
    """
    スコアラーの抽象基底クラス

    すべてのスコアラーはこのクラスを継承し、
    score()メソッドを実装する必要がある
    """

    def __init__(
        self,
        client: Optional[GeminiClient] = None,
        max_score: int = 100,
        min_score: int = 0
    ):
        """
        初期化

        引数:
            client: Gemini APIクライアント（省略時は共有インスタンスを使用）
            max_score: このスコアラーの最大スコア
            min_score: このスコアラーの最小スコア
        """
        self._client = client
        self.max_score = max_score
        self.min_score = min_score

    @property
    def client(self) -> GeminiClient:
        """Geminiクライアントを取得（遅延初期化）"""
        if self._client is None:
            self._client = get_gemini_client()
        return self._client

    @property
    @abstractmethod
    def scorer_name(self) -> str:
        """スコアラーの名前（ログ出力用）"""
        pass

    @abstractmethod
    def score(self, text: str, brand_name: str, **kwargs) -> ScoringResult:
        """
        テキストを評価してスコアを計算

        引数:
            text: 評価対象のテキスト（AIの回答など）
            brand_name: 評価対象のブランド名
            **kwargs: スコアラー固有の追加パラメータ

        戻り値:
            ScoringResult: スコアと評価詳細を含む結果オブジェクト
        """
        pass

    def validate_inputs(self, text: str, brand_name: str) -> None:
        """
        入力値の検証

        引数:
            text: 評価対象のテキスト
            brand_name: ブランド名

        例外:
            ValueError: 入力値が不正な場合
        """
        if not text or not isinstance(text, str):
            raise ValueError("評価対象のテキストが空か、文字列ではありません")

        if not brand_name or not isinstance(brand_name, str):
            raise ValueError("ブランド名が空か、文字列ではありません")

        if len(text.strip()) == 0:
            raise ValueError("評価対象のテキストが空白のみです")

        if len(brand_name.strip()) == 0:
            raise ValueError("ブランド名が空白のみです")

    def clamp_score(self, score: int) -> int:
        """
        スコアを有効範囲内に制限

        引数:
            score: 元のスコア値

        戻り値:
            min_score〜max_scoreの範囲に制限されたスコア
        """
        return max(self.min_score, min(self.max_score, score))

    def create_error_result(self, error_message: str) -> ScoringResult:
        """
        エラー結果を作成

        引数:
            error_message: エラーメッセージ

        戻り値:
            エラー情報を含むScoringResult（スコアは最小値）
        """
        logger.error(f"{self.scorer_name}: {error_message}")
        return ScoringResult(
            score=self.min_score,
            reasoning=f"評価エラー: {error_message}",
            error=error_message
        )

    def safe_score(self, text: str, brand_name: str, **kwargs) -> ScoringResult:
        """
        例外をキャッチしてスコアリングを実行

        score()メソッドをラップし、予期せぬエラーが発生しても
        エラー結果を返すようにする

        引数:
            text: 評価対象のテキスト
            brand_name: ブランド名
            **kwargs: 追加パラメータ

        戻り値:
            ScoringResult: 成功またはエラーの結果
        """
        try:
            # 入力値の検証
            self.validate_inputs(text, brand_name)

            # スコアリング実行
            logger.info(f"{self.scorer_name}: スコアリング開始 (brand={brand_name})")
            result = self.score(text, brand_name, **kwargs)

            # スコアの範囲チェック
            result.score = self.clamp_score(result.score)

            logger.info(f"{self.scorer_name}: スコアリング完了 (score={result.score})")
            return result

        except ValueError as e:
            return self.create_error_result(f"入力値エラー: {e}")

        except ScoringError as e:
            return self.create_error_result(str(e))

        except Exception as e:
            return self.create_error_result(f"予期せぬエラー: {e}")

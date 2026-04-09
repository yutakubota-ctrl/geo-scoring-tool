"""
レート制限管理モジュール
APIの呼び出し間隔と指数バックオフによるリトライを管理
"""
import time
import logging
import random
from functools import wraps
from typing import Callable, Any, TypeVar

# ログ設定
logger = logging.getLogger(__name__)

# 型変数（関数の戻り値の型を保持するため）
T = TypeVar("T")


class RateLimiter:
    """
    APIレート制限を管理するクラス

    機能:
    - 呼び出し間隔の制御（連続呼び出しを防ぐ）
    - 指数バックオフによるリトライ（エラー時に待機時間を増やしながら再試行）
    """

    def __init__(
        self,
        min_interval: float = 1.0,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        初期化

        引数:
            min_interval: API呼び出しの最小間隔（秒）
            max_retries: 最大リトライ回数
            base_delay: リトライ時の基本待機時間（秒）
            max_delay: リトライ時の最大待機時間（秒）
            exponential_base: 指数バックオフの底（倍率）
            jitter: ランダムな揺らぎを追加するか
        """
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

        # 最後のAPI呼び出し時刻
        self._last_call_time: float = 0

    def wait_if_needed(self) -> None:
        """
        必要に応じてAPI呼び出し前に待機
        最小間隔が経過していない場合は待機する
        """
        current_time = time.time()
        elapsed = current_time - self._last_call_time

        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logger.debug(f"レート制限: {wait_time:.2f}秒待機します")
            time.sleep(wait_time)

        self._last_call_time = time.time()

    def calculate_backoff_delay(self, attempt: int) -> float:
        """
        指数バックオフによる待機時間を計算

        引数:
            attempt: 現在の試行回数（0から開始）

        戻り値:
            待機時間（秒）
        """
        # 指数バックオフ: base_delay * (exponential_base ^ attempt)
        delay = self.base_delay * (self.exponential_base ** attempt)

        # 最大待機時間で制限
        delay = min(delay, self.max_delay)

        # ジッター（ランダムな揺らぎ）を追加
        # これにより、複数のクライアントが同時にリトライすることを防ぐ
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay

    def with_retry(
        self,
        func: Callable[..., T],
        retryable_exceptions: tuple = (Exception,),
        *args,
        **kwargs
    ) -> T:
        """
        リトライ付きで関数を実行

        引数:
            func: 実行する関数
            retryable_exceptions: リトライ対象の例外タイプ
            *args, **kwargs: 関数に渡す引数

        戻り値:
            関数の実行結果

        例外:
            最大リトライ回数を超えた場合、最後の例外を再発生
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # 呼び出し間隔の制御
                self.wait_if_needed()

                # 関数を実行
                return func(*args, **kwargs)

            except retryable_exceptions as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = self.calculate_backoff_delay(attempt)
                    logger.warning(
                        f"API呼び出しエラー（試行 {attempt + 1}/{self.max_retries + 1}）: {e}"
                    )
                    logger.info(f"{delay:.2f}秒後にリトライします...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"最大リトライ回数に達しました（{self.max_retries + 1}回）: {e}"
                    )

        # 最後の例外を再発生
        raise last_exception


def with_rate_limit(rate_limiter: RateLimiter, retryable_exceptions: tuple = (Exception,)):
    """
    レート制限とリトライを適用するデコレータ

    使用例:
        rate_limiter = RateLimiter()

        @with_rate_limit(rate_limiter, retryable_exceptions=(APIError,))
        def call_api():
            return api.request()

    引数:
        rate_limiter: RateLimiterインスタンス
        retryable_exceptions: リトライ対象の例外タイプ
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return rate_limiter.with_retry(
                func,
                retryable_exceptions,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


# デフォルトのレート制限インスタンス
# Gemini APIのレート制限に対応した設定
default_rate_limiter = RateLimiter(
    min_interval=1.0,      # 1秒の最小間隔
    max_retries=5,         # 最大5回リトライ
    base_delay=1.0,        # 基本待機1秒
    max_delay=60.0,        # 最大待機60秒
    exponential_base=2.0,  # 2倍ずつ増加
    jitter=True            # ランダム揺らぎあり
)

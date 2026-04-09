# api パッケージ
"""
API連携モジュール
Gemini APIクライアントとレート制限機能を提供
"""
from src.api.gemini_client import (
    GeminiClient,
    get_gemini_client,
    GEOScoring,
    GeminiAPIError,
    GeminiConfigError,
    GeminiRequestError,
    GeminiResponseError,
)
from src.api.rate_limiter import (
    RateLimiter,
    with_rate_limit,
    default_rate_limiter,
)

__all__ = [
    # Geminiクライアント
    "GeminiClient",
    "get_gemini_client",
    "GEOScoring",
    # 例外クラス
    "GeminiAPIError",
    "GeminiConfigError",
    "GeminiRequestError",
    "GeminiResponseError",
    # レート制限
    "RateLimiter",
    "with_rate_limit",
    "default_rate_limiter",
]

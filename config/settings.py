"""
設定管理モジュール
環境変数の読み込みとアプリケーション設定を管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# .envファイルを読み込み
load_dotenv(BASE_DIR / ".env")


class Settings:
    """アプリケーション設定"""

    # Gemini API設定
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))

    # データベース設定
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'data' / 'geo_scoring.db'}"
    )

    # バッチ設定
    BATCH_SCHEDULE: str = os.getenv("BATCH_SCHEDULE", "weekly")
    BATCH_DAY: str = os.getenv("BATCH_DAY", "monday")

    # ログ設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = BASE_DIR / "logs"

    # スコアリング設定（各指標の最大点数）
    MAX_VISIBILITY_SCORE: int = 10
    MAX_SENTIMENT_SCORE: int = 30
    MIN_SENTIMENT_SCORE: int = -10
    MAX_POSITIONING_SCORE: int = 20
    MAX_ACCURACY_SCORE: int = 40

    @classmethod
    def validate(cls) -> list[str]:
        """設定の検証を行い、エラーメッセージのリストを返す"""
        errors = []

        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY が設定されていません")

        return errors


# シングルトンインスタンス
settings = Settings()

"""
データベース接続管理
SQLAlchemyエンジンとセッション管理
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import sys
from pathlib import Path

# プロジェクトルートをパスに追加（クロスプラットフォーム対応）
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.database.models import Base


class DatabaseConnection:
    """データベース接続を管理するクラス"""

    def __init__(self, database_url: str = None):
        """
        初期化

        Args:
            database_url: データベースURL（省略時は設定から取得）
        """
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            echo=settings.LOG_LEVEL == "DEBUG",
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """全テーブルを作成"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """全テーブルを削除（注意: データが消えます）"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self):
        """
        セッションを取得するコンテキストマネージャー

        使用例:
            with db.get_session() as session:
                session.query(Brand).all()
        """
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """
        セッションを直接取得（手動でcloseが必要）

        Returns:
            Session: SQLAlchemyセッション
        """
        return self.SessionLocal()


# デフォルトの接続インスタンス
db = DatabaseConnection()


def init_database():
    """データベースを初期化（テーブル作成）"""
    db.create_tables()
    print(f"データベースを初期化しました: {settings.DATABASE_URL}")


if __name__ == "__main__":
    # 直接実行時はデータベースを初期化
    init_database()

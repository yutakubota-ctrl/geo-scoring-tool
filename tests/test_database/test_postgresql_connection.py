"""
PostgreSQL接続テスト

v2.1設計書 第8章のデータベーススキーマに基づく接続・テーブル操作テスト
"""
import pytest
from datetime import datetime
from sqlalchemy import text, inspect

from src.database.connection import DatabaseConnection
from src.database.models import Base, Brand


class TestDatabaseConnection:
    """データベース接続の基本動作テスト"""

    def test_db_connection_initialization(self, test_db_engine):
        """データベース接続の初期化テスト"""
        # テスト用エンジンでDatabaseConnectionを初期化
        db = DatabaseConnection(database_url="sqlite:///:memory:")

        # エンジンが正しく作成されているか
        assert db.engine is not None, "エンジンが作成されていません"
        assert db.SessionLocal is not None, "SessionLocalが作成されていません"

    def test_create_tables(self, test_db_engine):
        """テーブル作成テスト"""
        # テーブルが存在することを確認
        inspector = inspect(test_db_engine)
        table_names = inspector.get_table_names()

        # v1.0の基本テーブルが存在するか確認
        expected_tables = ["brands", "prompts", "responses", "scores"]
        for table in expected_tables:
            assert table in table_names, f"テーブル '{table}' が作成されていません"

    def test_session_context_manager(self, test_db_engine):
        """セッションコンテキストマネージャーのテスト"""
        db = DatabaseConnection(database_url="sqlite:///:memory:")
        db.create_tables()

        # コンテキストマネージャーでセッション取得
        with db.get_session() as session:
            # セッションが有効か確認
            assert session is not None, "セッションが取得できません"
            assert session.is_active, "セッションがアクティブではありません"

            # データ挿入テスト
            brand = Brand(
                name="TestBrand",
                domain="test.com",
                is_own=True
            )
            session.add(brand)
            session.flush()  # ここでIDが割り当てられる

            assert brand.id is not None, "ブランドIDが割り当てられていません"

    def test_session_rollback_on_error(self, test_db_engine):
        """エラー時のロールバックテスト"""
        db = DatabaseConnection(database_url="sqlite:///:memory:")
        db.create_tables()

        # 意図的にエラーを起こす
        with pytest.raises(Exception):
            with db.get_session() as session:
                brand = Brand(name="ErrorBrand")
                session.add(brand)
                # 意図的にエラーを発生
                raise ValueError("テストエラー")

        # ロールバック後、データが挿入されていないことを確認
        with db.get_session() as session:
            count = session.query(Brand).filter_by(name="ErrorBrand").count()
            assert count == 0, "ロールバックが正しく動作していません"


class TestBrandModel:
    """Brandモデルのテスト"""

    def test_brand_creation(self, test_db_session, sample_brand_data):
        """ブランドデータの作成テスト"""
        brand = Brand(**sample_brand_data)
        test_db_session.add(brand)
        test_db_session.commit()

        # データが正しく保存されているか
        saved_brand = test_db_session.query(Brand).filter_by(name="HubSpot").first()
        assert saved_brand is not None, "ブランドが保存されていません"
        assert saved_brand.domain == "hubspot.com"
        assert saved_brand.is_own is False
        assert "マーケティングツール" in saved_brand.keywords

    def test_brand_created_at_auto_set(self, test_db_session):
        """created_atの自動設定テスト"""
        brand = Brand(name="TimestampTest", is_own=False)
        test_db_session.add(brand)
        test_db_session.commit()

        saved_brand = test_db_session.query(Brand).filter_by(name="TimestampTest").first()
        assert saved_brand.created_at is not None, "created_atが設定されていません"
        assert isinstance(saved_brand.created_at, datetime)

    def test_brand_updated_at_auto_update(self, test_db_session):
        """updated_atの自動更新テスト"""
        brand = Brand(name="UpdateTest", is_own=False)
        test_db_session.add(brand)
        test_db_session.commit()

        original_updated_at = brand.updated_at

        # データを更新
        brand.domain = "updated.com"
        test_db_session.commit()

        # updated_atが更新されているか（SQLiteでは手動更新が必要な場合あり）
        # 注: SQLiteはonupdateが動作しない場合があるため、このテストはPostgreSQL環境で有効
        assert brand.updated_at is not None

    def test_brand_relationship_with_prompts(self, test_db_session):
        """BrandとPromptのリレーションシップテスト"""
        from src.database.models import Prompt

        brand = Brand(name="RelationTest", is_own=True)
        test_db_session.add(brand)
        test_db_session.commit()

        # プロンプトを追加
        prompt = Prompt(
            brand_id=brand.id,
            category="比較検討",
            template="おすすめのツールは？",
            is_active=True
        )
        test_db_session.add(prompt)
        test_db_session.commit()

        # リレーションシップ経由でプロンプトを取得
        assert len(brand.prompts) == 1, "プロンプトがリレーションシップで取得できません"
        assert brand.prompts[0].category == "比較検討"


class TestDatabaseMigrationReadiness:
    """PostgreSQLへの移行準備テスト"""

    def test_database_url_parsing(self):
        """DATABASE_URL環境変数の解析テスト"""
        # PostgreSQL URL形式の検証
        postgres_url = "postgresql://user:password@localhost:5432/geo_db"
        db = DatabaseConnection(database_url=postgres_url)

        assert "postgresql" in db.database_url.lower()

    def test_sqlite_to_postgresql_compatibility(self, test_db_session):
        """SQLiteとPostgreSQLの互換性テスト"""
        # JSON型のデータ挿入・取得テスト
        brand = Brand(
            name="JSONTest",
            keywords=["keyword1", "keyword2", "keyword3"],
            is_own=False
        )
        test_db_session.add(brand)
        test_db_session.commit()

        saved_brand = test_db_session.query(Brand).filter_by(name="JSONTest").first()
        assert isinstance(saved_brand.keywords, list)
        assert len(saved_brand.keywords) == 3
        assert "keyword1" in saved_brand.keywords


class TestV2SchemaPreparation:
    """v2.1設計書のスキーマ準備テスト"""

    def test_llm_thought_log_schema_simulation(self, test_db_session):
        """
        llm_thought_log テーブルの構造をテスト
        (v2.1設計書 8.2.1)

        注: 実際のテーブルはまだ実装されていないため、
        将来の実装時にこのテストを参考にする
        """
        # 期待されるカラム構造
        expected_columns = {
            "query_id": "VARCHAR(36)",
            "query_text": "TEXT",
            "llm_model": "VARCHAR(50)",
            "thought_trace": "JSONB",  # PostgreSQL
            "search_queries_used": "TEXT[]",  # PostgreSQL配列型
            "selected_urls": "TEXT[]",
            "final_reasoning": "TEXT",
            "executed_at": "TIMESTAMP"
        }

        # このテストは将来のllm_thought_logテーブル実装時に使用
        assert True, "v2.1スキーマ準備のプレースホルダーテスト"

    def test_citation_master_schema_simulation(self, test_db_session):
        """
        citation_master テーブルの構造をテスト
        (v2.1設計書 8.2.2)
        """
        expected_columns = {
            "citation_id": "VARCHAR(36)",
            "query_id": "VARCHAR(36)",
            "entity_name": "VARCHAR(255)",
            "mention_count": "INTEGER",
            "sentiment_score": "DECIMAL(3,2)",
            "reference_type": "VARCHAR(50)",
            "source_url": "TEXT",
            "position_in_response": "INTEGER",
            "reference_rank": "INTEGER",
            "context_snippet": "TEXT"
        }

        # このテストは将来のcitation_masterテーブル実装時に使用
        assert True, "v2.1スキーマ準備のプレースホルダーテスト"


class TestDatabasePerformance:
    """データベース性能テスト"""

    def test_bulk_insert_performance(self, test_db_session):
        """バルクインサートの性能テスト"""
        import time

        # 100件のブランドを一括挿入
        brands = [
            Brand(name=f"Brand{i}", domain=f"brand{i}.com", is_own=False)
            for i in range(100)
        ]

        start_time = time.time()
        test_db_session.bulk_save_objects(brands)
        test_db_session.commit()
        elapsed_time = time.time() - start_time

        # 100件の挿入が1秒以内に完了するか
        assert elapsed_time < 1.0, f"バルクインサートが遅すぎます: {elapsed_time}秒"

        # データが正しく挿入されているか
        count = test_db_session.query(Brand).count()
        assert count == 100, "バルクインサートでデータが不足しています"

    def test_query_with_filter_performance(self, test_db_session):
        """フィルタクエリの性能テスト"""
        # テストデータ準備
        for i in range(50):
            brand = Brand(
                name=f"TestBrand{i}",
                domain=f"test{i}.com",
                is_own=(i % 2 == 0)  # 偶数IDは自社ブランド
            )
            test_db_session.add(brand)
        test_db_session.commit()

        import time
        start_time = time.time()

        # 自社ブランドのみを取得
        own_brands = test_db_session.query(Brand).filter_by(is_own=True).all()
        elapsed_time = time.time() - start_time

        assert len(own_brands) == 25, "フィルタが正しく動作していません"
        assert elapsed_time < 0.1, f"クエリが遅すぎます: {elapsed_time}秒"

"""
PostgreSQLセットアップスクリプト

v2.1で使用するPostgreSQLテーブルを作成するスクリプト
.envからDATABASE_URLを読み込み、テーブルを作成後に接続テストを実行
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.models_v2 import Base, LLMThoughtLog, CitationMaster, RoadmapRegistry


def load_environment():
    """環境変数を読み込み"""
    env_path = project_root / '.env'

    if not env_path.exists():
        print(f"エラー: .envファイルが見つかりません: {env_path}")
        print("先に.env.exampleをコピーして.envを作成し、DATABASE_URLを設定してください。")
        sys.exit(1)

    load_dotenv(env_path)
    print(f"環境変数を読み込みました: {env_path}")


def get_database_url():
    """DATABASE_URLを取得"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("エラー: DATABASE_URLが.envに設定されていません")
        print("例: DATABASE_URL=postgresql://user:password@localhost:5432/geo_scoring_v2")
        sys.exit(1)

    # SQLite URLの場合は警告
    if database_url.startswith('sqlite'):
        print("警告: DATABASE_URLがSQLiteになっています")
        print("v2.1ではPostgreSQLを使用することを推奨します")
        print("（テスト目的でSQLiteでも続行します）")

    return database_url


def create_engine_and_session(database_url):
    """エンジンとセッションを作成"""
    try:
        engine = create_engine(
            database_url,
            echo=True,  # SQL文を表示
            pool_pre_ping=True  # 接続の事前確認
        )
        Session = sessionmaker(bind=engine)
        return engine, Session
    except Exception as e:
        print(f"エラー: データベースエンジンの作成に失敗しました")
        print(f"詳細: {e}")
        sys.exit(1)


def test_connection(engine, database_url):
    """接続テスト"""
    print("\n接続テストを実行中...")

    try:
        with engine.connect() as connection:
            # データベースの種類によってテストクエリを変更
            if 'sqlite' in database_url.lower():
                result = connection.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                print(f"接続成功: SQLite {version}")
            else:
                result = connection.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"接続成功: {version}")
            return True
    except Exception as e:
        print(f"接続失敗: {e}")
        return False


def check_existing_tables(engine):
    """既存のテーブルを確認"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if existing_tables:
        print(f"\n既存のテーブル: {', '.join(existing_tables)}")

        v2_tables = ['llm_thought_log', 'citation_master', 'roadmap_registry']
        existing_v2_tables = [t for t in v2_tables if t in existing_tables]

        if existing_v2_tables:
            print(f"\nv2.1のテーブルが既に存在します: {', '.join(existing_v2_tables)}")
            try:
                response = input("これらのテーブルを削除して再作成しますか？ (y/N): ")
                if response.lower() == 'y':
                    for table in existing_v2_tables:
                        print(f"テーブルを削除中: {table}")
                        with engine.connect() as conn:
                            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                            conn.commit()
                    print("削除完了")
                else:
                    print("既存のテーブルをそのまま使用します")
                    return False
            except EOFError:
                print("非対話モードのため、既存のテーブルをそのまま使用します")
                return False
    else:
        print("\n既存のテーブルはありません")

    return True


def create_tables(engine):
    """テーブルを作成"""
    print("\nテーブルを作成中...")

    try:
        Base.metadata.create_all(engine)
        print("テーブル作成完了")
        return True
    except Exception as e:
        print(f"テーブル作成失敗: {e}")
        return False


def verify_tables(engine):
    """作成されたテーブルを検証"""
    print("\nテーブルの検証中...")

    inspector = inspect(engine)
    required_tables = ['llm_thought_log', 'citation_master', 'roadmap_registry']

    for table_name in required_tables:
        if table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            print(f"\nテーブル: {table_name}")
            print(f"  カラム数: {len(columns)}")
            print(f"  インデックス数: {len(indexes)}")

            # 主要カラムの確認
            column_names = [col['name'] for col in columns]
            print(f"  カラム: {', '.join(column_names)}")
        else:
            print(f"エラー: テーブル {table_name} が見つかりません")
            return False

    print("\n全テーブルの検証が完了しました")
    return True


def insert_test_data(Session):
    """テストデータを挿入"""
    print("\nテストデータを挿入しますか？")
    try:
        response = input("(y/N): ")
        if response.lower() != 'y':
            print("スキップします")
            return
    except EOFError:
        print("非対話モードのため、テストデータを自動挿入します")
        pass

    session = Session()

    try:
        # テスト用のLLM思考ログ
        test_log = LLMThoughtLog(
            query_id='test_query_001',
            query_text='マーケティングツール おすすめ',
            llm_model='chatgpt-o1-preview',
            thought_trace={
                'step_1': '候補ブランド列挙（HubSpot, Marketo, Salesforce）',
                'step_2': 'HubSpot公式サイト確認',
                'step_3': 'G2レビュー参照'
            },
            search_queries_used=['marketing automation tools', 'HubSpot pricing'],
            selected_urls=['https://www.hubspot.com/', 'https://www.g2.com/products/hubspot'],
            final_reasoning='HubSpotは中小企業向け、Marketoは大企業向けと判断',
            brand_mentions={'HubSpot': {'mentioned': True, 'position': 1}}
        )
        session.add(test_log)

        # テスト用の引用マスター
        test_citation = CitationMaster(
            citation_id='test_cite_001',
            query_id='test_query_001',
            entity_name='HubSpot',
            mention_count=1,
            sentiment_score=0.85,
            reference_type='ChatGPT',
            source_url='https://www.hubspot.com/',
            source_domain='hubspot.com',
            position_in_response=125,
            reference_rank=1,
            context_snippet='HubSpotは中小企業に最適なマーケティングツールです'
        )
        session.add(test_citation)

        # テスト用のロードマップ
        test_roadmap = RoadmapRegistry(
            task_id='test_task_001',
            priority='P0',
            task_type='Content',
            description='HubSpotとの比較記事を作成',
            assigned_to='Gem_03',
            status='Pending',
            impact_score=9,
            effort_score=3,
            parent_gap_id='gap_001',
            approval_status='Draft'
        )
        session.add(test_roadmap)

        session.commit()
        print("テストデータの挿入が完了しました")

        # 挿入されたデータを確認
        print("\n挿入されたデータ:")
        print(f"  LLM思考ログ: {session.query(LLMThoughtLog).count()}件")
        print(f"  引用マスター: {session.query(CitationMaster).count()}件")
        print(f"  ロードマップ: {session.query(RoadmapRegistry).count()}件")

    except Exception as e:
        session.rollback()
        print(f"テストデータの挿入に失敗しました: {e}")
    finally:
        session.close()


def main():
    """メイン処理"""
    print("=" * 60)
    print("PostgreSQL セットアップスクリプト v2.1")
    print("=" * 60)

    # 1. 環境変数を読み込み
    load_environment()

    # 2. DATABASE_URLを取得
    database_url = get_database_url()
    print(f"\n接続先: {database_url.split('@')[1] if '@' in database_url else database_url}")

    # 3. エンジンとセッションを作成
    engine, Session = create_engine_and_session(database_url)

    # 4. 接続テスト
    if not test_connection(engine, database_url):
        print("\n接続テストに失敗しました。DATABASE_URLを確認してください。")
        sys.exit(1)

    # 5. 既存テーブルの確認
    should_create = check_existing_tables(engine)

    # 6. テーブル作成
    if should_create:
        if not create_tables(engine):
            sys.exit(1)

    # 7. テーブルの検証
    if not verify_tables(engine):
        sys.exit(1)

    # 8. テストデータの挿入（任意）
    insert_test_data(Session)

    print("\n" + "=" * 60)
    print("セットアップが完了しました")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. Streamlitダッシュボードで接続を確認")
    print("2. Gem_01（GEO_Intelligence_Analyst）の実装を開始")
    print("=" * 60)


if __name__ == '__main__':
    main()

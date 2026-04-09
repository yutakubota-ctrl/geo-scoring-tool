"""
pytest設定とフィクスチャ

テスト全体で共有する設定やモックオブジェクトを定義します。
v2.1設計書に基づく基盤コンポーネントのテスト環境を構築します。
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.database.models import Base


# ================================================================================
# テスト用環境変数
# ================================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """テスト用環境変数の設定（全テストで自動実行）"""
    # テスト用のAPIキー設定（実際のキーは使わない）
    os.environ.setdefault("GEMINI_API_KEY", "test_gemini_key_dummy")
    os.environ.setdefault("OPENAI_API_KEY", "test_openai_key_dummy")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test_anthropic_key_dummy")
    os.environ.setdefault("SERP_API_KEY", "test_serp_key_dummy")
    os.environ.setdefault("AHREFS_API_KEY", "test_ahrefs_key_dummy")

    # テスト用データベースURL（インメモリSQLite）
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    yield

    # テスト後のクリーンアップ（必要に応じて）


# ================================================================================
# データベース関連フィクスチャ
# ================================================================================

@pytest.fixture(scope="function")
def test_db_engine():
    """テスト用インメモリデータベースエンジン"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # テーブル作成
    Base.metadata.create_all(bind=engine)

    yield engine

    # テーブル削除
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """テスト用データベースセッション"""
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def sample_brand_data():
    """テスト用ブランドデータ"""
    return {
        "name": "HubSpot",
        "domain": "hubspot.com",
        "keywords": ["マーケティングツール", "MA", "CRM"],
        "is_own": False,
        "reference_facts": "HubSpotは中小企業向けマーケティングツールです。"
    }


# ================================================================================
# API クライアントモック
# ================================================================================

@pytest.fixture
def mock_openai_client():
    """モックOpenAI APIクライアント"""
    mock_client = MagicMock()

    # ChatGPT o1のレスポンスをモック
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.reasoning_content = """
    1. 候補ブランドの列挙: HubSpot, Marketo, Salesforce Marketing Cloud
    2. 公式サイトの確認: hubspot.com を確認、中小企業向けと判断
    3. 第三者レビュー参照: G2.com でHubSpotが高評価
    4. 公的機関確認: 特定商取引法表記を確認
    5. 料金比較: HubSpot無料プランあり、Marketoは要見積もり
    6. 口コミ確認: Twitter、Reddit等でHubSpotが好評
    7. 最終判断: 中小企業には HubSpot が最適と判断
    """
    mock_response.choices[0].message.content = """
    おすすめのマーケティングツールは以下の3つです：

    1. HubSpot - 中小企業向け、無料プランあり
    2. Marketo - 大企業向け、高機能
    3. Salesforce Marketing Cloud - エンタープライズ向け
    """

    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_claude_client():
    """モックClaude APIクライアント"""
    mock_client = MagicMock()

    # Claudeの分析結果をモック
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = """```json
    {
        "7ステップの分解": {
            "step_1": "候補ブランドの列挙（HubSpot, Marketo, Salesforce）",
            "step_2": "公式サイトの確認（hubspot.com）",
            "step_3": "第三者レビューサイトの参照（g2.com）",
            "step_4": "公的機関の確認（特定商取引法）",
            "step_5": "料金・機能比較（HubSpot無料プラン）",
            "step_6": "口コミ・評判の確認（Twitter, Reddit）",
            "step_7": "最終判断（HubSpot推奨）"
        },
        "検索クエリ候補": [
            "marketing automation tools comparison",
            "HubSpot pricing 2026",
            "Marketo vs HubSpot"
        ],
        "参照URL": [
            "https://www.hubspot.com/",
            "https://www.g2.com/products/hubspot",
            "https://www.marketo.com/"
        ],
        "最終推論": "HubSpotは中小企業向けで無料プランもあり、最適と判断"
    }
    ```"""

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_serp_api_client():
    """モックSerp APIクライアント"""
    mock_client = MagicMock()

    # AI Overviewsのレスポンスをモック
    mock_result = {
        "ai_overview": {
            "answer": "マーケティングツールのおすすめは、HubSpot、Marketo、Salesforceです。HubSpotは中小企業向けで無料プランがあります。",
            "references": [
                {
                    "title": "HubSpot公式サイト",
                    "link": "https://www.hubspot.com/",
                    "domain": "hubspot.com"
                },
                {
                    "title": "G2 - HubSpotレビュー",
                    "link": "https://www.g2.com/products/hubspot",
                    "domain": "g2.com"
                }
            ]
        },
        "organic_results": [
            {
                "position": 1,
                "title": "HubSpot - Marketing, Sales, and Service Software",
                "link": "https://www.hubspot.com/",
                "domain": "hubspot.com"
            }
        ]
    }

    mock_client.search.return_value = mock_result
    mock_client.get_dict.return_value = mock_result

    return mock_client


@pytest.fixture
def mock_mcp_client():
    """モックMCPクライアント（Ahrefs用）"""
    mock_client = MagicMock()

    # キーワードギャップのレスポンスをモック
    mock_gap_keywords = [
        {
            "keyword": "マーケティングツール 比較",
            "volume": 2400,
            "kd": 35,
            "traffic_potential": 960
        },
        {
            "keyword": "MA ツール おすすめ",
            "volume": 1800,
            "kd": 28,
            "traffic_potential": 720
        }
    ]

    mock_client.get_keyword_gap.return_value = mock_gap_keywords

    return mock_client


# ================================================================================
# Gem_01 関連フィクスチャ
# ================================================================================

@pytest.fixture
def sample_chatgpt_thinking_process():
    """Gem_01テスト用のChatGPT思考プロセスサンプル"""
    return {
        "query": "マーケティングツール おすすめ",
        "thinking_steps": """
        1. 候補列挙: HubSpot, Marketo, Salesforce
        2. 公式確認: hubspot.com 確認済み
        3. レビュー参照: G2.com でHubSpot高評価
        4. 公的確認: 特商法OK
        5. 料金比較: HubSpot無料あり
        6. 口コミ: Twitter好評
        7. 判断: HubSpot最適
        """,
        "final_answer": "おすすめは HubSpot です。",
        "expected_output": {
            "thought_trace": {
                "step_1": "候補ブランド列挙",
                "step_2": "公式サイト確認",
                "step_3": "レビューサイト参照",
                "step_4": "公的機関確認",
                "step_5": "料金・機能比較",
                "step_6": "口コミ確認",
                "step_7": "最終判断"
            },
            "search_queries_used": [
                "marketing automation tools",
                "HubSpot pricing"
            ],
            "selected_urls": [
                "https://www.hubspot.com/",
                "https://www.g2.com/products/hubspot"
            ]
        }
    }


# ================================================================================
# ユーティリティ関数
# ================================================================================

@pytest.fixture
def assert_valid_query_id():
    """クエリIDフォーマット検証関数"""
    def validator(query_id: str):
        """
        クエリIDが正しいフォーマットか検証
        期待フォーマット: q_YYYYMMDD_HHMMSS
        """
        assert query_id.startswith("q_"), "クエリIDは 'q_' で始まる必要があります"
        parts = query_id.split("_")
        assert len(parts) == 3, "クエリIDは 'q_日付_時刻' の形式である必要があります"
        assert len(parts[1]) == 8, "日付部分は8桁（YYYYMMDD）である必要があります"
        assert parts[1].isdigit(), "日付部分は数字である必要があります"

    return validator

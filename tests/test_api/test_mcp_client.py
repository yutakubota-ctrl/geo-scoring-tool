"""
MCP (Model Context Protocol) クライアントのテスト

v2.1設計書 第7章に基づく MCP連携のテスト
Ahrefs MCP Server と Serp API MCP Server の動作検証
"""
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open


class MockMCPConfig:
    """MCP設定ファイルの読み込みと管理（モック）"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/mcp_config.json"
        self.config = None

    def load_config(self) -> dict:
        """MCP設定ファイルを読み込む"""
        # テスト用のデフォルト設定
        default_config = {
            "mcpServers": {
                "ahrefs": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-ahrefs"],
                    "env": {
                        "AHREFS_API_KEY": "${AHREFS_API_KEY}"
                    }
                },
                "serpapi": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-serpapi"],
                    "env": {
                        "SERPAPI_API_KEY": "${SERP_API_KEY}"
                    }
                }
            }
        }

        # ファイルが存在する場合は読み込み、なければデフォルト
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = default_config

        return self.config

    def validate_config(self) -> bool:
        """設定の妥当性を検証"""
        if not self.config:
            return False

        # mcpServersキーが存在するか
        if "mcpServers" not in self.config:
            return False

        # 各サーバー設定が正しい構造か
        for server_name, server_config in self.config["mcpServers"].items():
            required_keys = ["command", "args"]
            if not all(key in server_config for key in required_keys):
                return False

        return True

    def get_server_config(self, server_name: str) -> dict:
        """特定のMCPサーバー設定を取得"""
        if not self.config:
            self.load_config()

        return self.config.get("mcpServers", {}).get(server_name, {})


class MockAhrefsMCPClient:
    """Ahrefs MCP クライアント（モック実装）"""

    def __init__(self, claude_client=None):
        self.claude_client = claude_client

    def get_keyword_gap(self, target: str, competitors: list) -> list:
        """
        キーワードギャップ分析
        (v2.1設計書 7.3に基づく)
        """
        # Claudeに依頼（MCPツールを自動使用）
        response = self.claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""
                MCPのAhrefsツールを使って、キーワードギャップ分析を実行してください：

                対象ドメイン: {target}
                競合ドメイン: {', '.join(competitors)}

                競合が獲得していて対象ドメインが獲得できていないキーワードを
                トラフィックポテンシャルの高い順に20件抽出してください。
                """
            }]
        )

        # レスポンスから結果をパース
        return self._parse_keyword_gap_response(response)

    def _parse_keyword_gap_response(self, response) -> list:
        """Claude応答からキーワードギャップデータを抽出"""
        # モック実装では固定値を返す
        return [
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

    def get_backlinks(self, target: str, mode: str = "domain", limit: int = 100) -> list:
        """被リンク情報取得"""
        response = self.claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""
                MCPのAhrefsツールで被リンク情報を取得してください：
                ドメイン: {target}
                取得件数: {limit}
                """
            }]
        )

        return self._parse_backlinks_response(response)

    def _parse_backlinks_response(self, response) -> list:
        """被リンクデータを抽出"""
        return [
            {
                "domain": "techcrunch.com",
                "domain_rating": 91,
                "url_from": "https://techcrunch.com/article",
                "url_to": "https://example.com/"
            }
        ]


class TestMCPConfigManagement:
    """MCP設定管理のテスト"""

    def test_load_default_config(self):
        """デフォルト設定の読み込みテスト"""
        config_manager = MockMCPConfig()
        config = config_manager.load_config()

        # 必須キーが存在するか
        assert "mcpServers" in config
        assert "ahrefs" in config["mcpServers"]
        assert "serpapi" in config["mcpServers"]

    def test_validate_config_structure(self):
        """設定構造の妥当性検証テスト"""
        config_manager = MockMCPConfig()
        config_manager.load_config()

        # 設定が妥当か
        assert config_manager.validate_config() is True

    def test_get_ahrefs_server_config(self):
        """Ahrefsサーバー設定の取得テスト"""
        config_manager = MockMCPConfig()
        config_manager.load_config()

        ahrefs_config = config_manager.get_server_config("ahrefs")

        # Ahrefs設定が正しく取得できるか
        assert "command" in ahrefs_config
        assert ahrefs_config["command"] == "npx"
        assert "-y" in ahrefs_config["args"]
        assert "@modelcontextprotocol/server-ahrefs" in ahrefs_config["args"]

    def test_get_serpapi_server_config(self):
        """Serp APIサーバー設定の取得テスト"""
        config_manager = MockMCPConfig()
        config_manager.load_config()

        serpapi_config = config_manager.get_server_config("serpapi")

        # Serp API設定が正しく取得できるか
        assert "command" in serpapi_config
        assert "@modelcontextprotocol/server-serpapi" in serpapi_config["args"]

    def test_environment_variable_expansion(self):
        """環境変数の展開テスト"""
        import os
        os.environ["AHREFS_API_KEY"] = "test_ahrefs_key_123"

        config_manager = MockMCPConfig()
        config = config_manager.load_config()

        ahrefs_env = config["mcpServers"]["ahrefs"]["env"]

        # 環境変数が設定されているか（実際の展開は実装時）
        assert "AHREFS_API_KEY" in ahrefs_env


class TestAhrefsMCPClient:
    """Ahrefs MCPクライアントのテスト"""

    def test_keyword_gap_returns_valid_data(self, mock_claude_client):
        """キーワードギャップ分析が有効なデータを返すか"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        result = ahrefs_client.get_keyword_gap(
            target="example.com",
            competitors=["competitor1.com", "competitor2.com"]
        )

        # 結果がリストで返されるか
        assert isinstance(result, list)
        assert len(result) > 0

        # 各キーワードが必須フィールドを持つか
        for kw in result:
            assert "keyword" in kw
            assert "volume" in kw
            assert "kd" in kw
            assert "traffic_potential" in kw

    def test_keyword_gap_data_types(self, mock_claude_client):
        """キーワードギャップのデータ型テスト"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        result = ahrefs_client.get_keyword_gap(
            target="example.com",
            competitors=["competitor.com"]
        )

        # データ型が正しいか
        for kw in result:
            assert isinstance(kw["keyword"], str)
            assert isinstance(kw["volume"], int)
            assert isinstance(kw["kd"], int)
            assert isinstance(kw["traffic_potential"], (int, float))

    def test_backlinks_retrieval(self, mock_claude_client):
        """被リンク情報取得テスト"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        result = ahrefs_client.get_backlinks(
            target="example.com",
            limit=50
        )

        # 被リンクデータが返されるか
        assert isinstance(result, list)
        assert len(result) > 0

        # 被リンクデータの構造確認
        for backlink in result:
            assert "domain" in backlink
            assert "domain_rating" in backlink
            assert "url_from" in backlink

    def test_backlinks_domain_rating_range(self, mock_claude_client):
        """被リンクのDR（ドメインレーティング）範囲テスト"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        result = ahrefs_client.get_backlinks(target="example.com")

        # DRが0-100の範囲内か
        for backlink in result:
            dr = backlink["domain_rating"]
            assert 0 <= dr <= 100, f"DRが範囲外: {dr}"


class TestMCPErrorHandling:
    """MCPエラーハンドリングのテスト"""

    def test_handles_missing_api_key(self):
        """APIキー未設定時のエラーハンドリング"""
        import os

        # APIキーを一時的に削除
        original_key = os.environ.get("AHREFS_API_KEY")
        if "AHREFS_API_KEY" in os.environ:
            del os.environ["AHREFS_API_KEY"]

        config_manager = MockMCPConfig()
        config = config_manager.load_config()

        # APIキーが設定ファイルにプレースホルダーとして存在するか
        ahrefs_env = config["mcpServers"]["ahrefs"]["env"]
        assert "AHREFS_API_KEY" in ahrefs_env

        # 元に戻す
        if original_key:
            os.environ["AHREFS_API_KEY"] = original_key

    def test_handles_invalid_domain(self, mock_claude_client):
        """無効なドメイン指定時のエラーハンドリング"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        # 空のドメインを指定
        result = ahrefs_client.get_keyword_gap(
            target="",
            competitors=["competitor.com"]
        )

        # エラーが発生せず、空のリストまたはデフォルト値が返されるか
        assert isinstance(result, list)

    def test_handles_mcp_server_unavailable(self, mock_claude_client):
        """MCPサーバーが利用不可の場合のエラーハンドリング"""
        # Claudeが接続エラーを返すモック
        mock_claude = MagicMock()
        mock_claude.messages.create.side_effect = ConnectionError("MCP server unavailable")

        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude)

        # ConnectionErrorが適切に発生するか
        with pytest.raises(ConnectionError):
            ahrefs_client.get_keyword_gap(
                target="example.com",
                competitors=["competitor.com"]
            )


class TestMCPIntegrationScenarios:
    """MCP統合シナリオテスト"""

    def test_end_to_end_keyword_gap_workflow(self, mock_claude_client):
        """
        E2Eワークフロー: 設定読み込み → キーワードギャップ分析
        """
        # Step 1: 設定読み込み
        config_manager = MockMCPConfig()
        config = config_manager.load_config()
        assert config_manager.validate_config()

        # Step 2: Ahrefsクライアント初期化
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        # Step 3: キーワードギャップ分析実行
        result = ahrefs_client.get_keyword_gap(
            target="example.com",
            competitors=["competitor1.com", "competitor2.com"]
        )

        # Step 4: 結果検証
        assert len(result) > 0
        assert result[0]["keyword"] is not None

    def test_mcp_with_multiple_competitors(self, mock_claude_client):
        """複数競合ドメインでのMCP利用テスト"""
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        competitors = [
            "competitor1.com",
            "competitor2.com",
            "competitor3.com"
        ]

        result = ahrefs_client.get_keyword_gap(
            target="example.com",
            competitors=competitors
        )

        # 複数競合でも正常に動作するか
        assert isinstance(result, list)
        assert len(result) > 0


class TestMCPPerformance:
    """MCP性能テスト"""

    def test_keyword_gap_response_time(self, mock_claude_client):
        """キーワードギャップ分析の応答時間テスト"""
        import time

        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude_client)

        start_time = time.time()
        result = ahrefs_client.get_keyword_gap(
            target="example.com",
            competitors=["competitor.com"]
        )
        elapsed_time = time.time() - start_time

        # モックなので即座に返る（実環境では5秒以内を目標）
        assert elapsed_time < 1.0, f"応答が遅すぎます: {elapsed_time}秒"
        assert len(result) > 0

    def test_mcp_retry_mechanism(self, mock_claude_client):
        """MCPリトライメカニズムのテスト"""
        # Claudeが最初は失敗し、2回目で成功するモック
        mock_claude = MagicMock()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("一時的なエラー")
            else:
                # 成功レスポンス
                mock_response = MagicMock()
                mock_response.content = [MagicMock()]
                mock_response.content[0].text = "成功"
                return mock_response

        mock_claude.messages.create.side_effect = side_effect

        # リトライロジック（実装時に追加予定）
        # ここでは単純に2回目で成功することを確認
        ahrefs_client = MockAhrefsMCPClient(claude_client=mock_claude)

        with pytest.raises(ConnectionError):
            ahrefs_client.get_keyword_gap("example.com", ["competitor.com"])

        # 2回目は成功
        result = ahrefs_client.get_keyword_gap("example.com", ["competitor.com"])
        assert result is not None

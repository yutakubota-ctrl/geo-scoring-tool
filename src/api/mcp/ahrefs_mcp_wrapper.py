"""
Ahrefs MCP ラッパー

Ahrefsの各種SEOデータをMCP経由で取得するためのラッパークラス
"""

from .mcp_client import MCPClient
from typing import List, Dict, Optional


class AhrefsMCPWrapper:
    """
    Ahrefs MCP ラッパー

    AhrefsのMCPサーバーを介してSEOデータを取得します。
    キーワードギャップ、被リンク分析などの機能を提供します。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Ahrefs MCPラッパーの初期化

        Args:
            api_key: Anthropic APIキー（省略時は環境変数から取得）
        """
        self.mcp = MCPClient(api_key=api_key)

    def get_keyword_gap(
        self,
        target_domain: str,
        competitor_domains: List[str],
        limit: int = 20,
        mode: str = "missing"
    ) -> Dict:
        """
        キーワードギャップ取得

        競合他社が獲得していて、自社が獲得していないキーワードを取得します。

        Args:
            target_domain: 対象ドメイン（自社サイト）
            competitor_domains: 競合ドメインリスト
            limit: 取得件数（デフォルト: 20）
            mode: ギャップモード
                - "missing": 競合が持っていて自社が持っていない
                - "weak": 競合の方が順位が高い
                - "common": 両方が持っている

        Returns:
            キーワードギャップデータ
            {
                "keywords": [
                    {
                        "keyword": "キーワード",
                        "volume": 検索ボリューム,
                        "difficulty": 難易度,
                        "traffic_potential": トラフィックポテンシャル,
                        "competitor_positions": {...}
                    },
                    ...
                ]
            }
        """
        arguments = {
            "target": target_domain,
            "competitors": competitor_domains,
            "limit": limit,
            "mode": mode,
            "order_by": "traffic_potential",
            "order": "desc"
        }

        result = self.mcp.call_tool(
            tool_name="get_keyword_gap",
            server_name="ahrefs",
            arguments=arguments
        )

        return result

    def get_backlinks(
        self,
        target_domain: str,
        limit: int = 100,
        min_dr: int = 50,
        mode: str = "domain"
    ) -> List[Dict]:
        """
        被リンク取得

        Args:
            target_domain: 対象ドメイン
            limit: 取得件数（デフォルト: 100）
            min_dr: 最小DR（Domain Rating）
            mode: 取得モード
                - "domain": ドメイン単位
                - "page": ページ単位

        Returns:
            被リンクリスト
            [
                {
                    "url_from": "リンク元URL",
                    "domain_rating": DR値,
                    "url_rating": UR値,
                    "anchor": "アンカーテキスト",
                    "first_seen": "初回検出日",
                    "last_check": "最終確認日"
                },
                ...
            ]
        """
        arguments = {
            "target": target_domain,
            "mode": mode,
            "limit": limit,
            "order_by": "domain_rating",
            "order": "desc"
        }

        result = self.mcp.call_tool(
            tool_name="get_backlinks",
            server_name="ahrefs",
            arguments=arguments
        )

        # DR フィルタ
        backlinks = result.get("backlinks", [])
        if isinstance(backlinks, list):
            filtered = [
                bl for bl in backlinks
                if bl.get("domain_rating", 0) >= min_dr
            ]
            return filtered
        else:
            # MCPからのレスポンスが期待と異なる場合
            return []

    def get_organic_keywords(
        self,
        target_domain: str,
        limit: int = 100,
        min_volume: int = 100
    ) -> List[Dict]:
        """
        オーガニックキーワード取得

        Args:
            target_domain: 対象ドメイン
            limit: 取得件数（デフォルト: 100）
            min_volume: 最小検索ボリューム

        Returns:
            オーガニックキーワードリスト
            [
                {
                    "keyword": "キーワード",
                    "position": 順位,
                    "volume": 検索ボリューム,
                    "traffic": 推定トラフィック,
                    "url": "ランディングページURL"
                },
                ...
            ]
        """
        arguments = {
            "target": target_domain,
            "limit": limit,
            "order_by": "traffic",
            "order": "desc"
        }

        result = self.mcp.call_tool(
            tool_name="get_organic_keywords",
            server_name="ahrefs",
            arguments=arguments
        )

        # ボリュームフィルタ
        keywords = result.get("keywords", [])
        if isinstance(keywords, list):
            filtered = [
                kw for kw in keywords
                if kw.get("volume", 0) >= min_volume
            ]
            return filtered
        else:
            return []

    def get_domain_overview(
        self,
        target_domain: str
    ) -> Dict:
        """
        ドメイン概要取得

        Args:
            target_domain: 対象ドメイン

        Returns:
            ドメイン概要データ
            {
                "domain_rating": DR値,
                "url_rating": UR値,
                "organic_keywords": オーガニックキーワード数,
                "organic_traffic": オーガニックトラフィック推定値,
                "backlinks": 被リンク数,
                "referring_domains": 参照ドメイン数
            }
        """
        arguments = {
            "target": target_domain,
        }

        result = self.mcp.call_tool(
            tool_name="get_domain_overview",
            server_name="ahrefs",
            arguments=arguments
        )

        return result

    def get_top_pages(
        self,
        target_domain: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        トップページ取得

        Args:
            target_domain: 対象ドメイン
            limit: 取得件数（デフォルト: 50）

        Returns:
            トップページリスト
            [
                {
                    "url": "ページURL",
                    "traffic": 推定トラフィック,
                    "keywords": キーワード数,
                    "backlinks": 被リンク数,
                    "top_keyword": "主要キーワード"
                },
                ...
            ]
        """
        arguments = {
            "target": target_domain,
            "limit": limit,
            "order_by": "traffic",
            "order": "desc"
        }

        result = self.mcp.call_tool(
            tool_name="get_top_pages",
            server_name="ahrefs",
            arguments=arguments
        )

        return result.get("pages", [])

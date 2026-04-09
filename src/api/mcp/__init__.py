"""
MCP (Model Context Protocol) 統合モジュール

MCPを介してAhrefs、Serp API、Screaming Frogなどの外部APIに
Claudeモデルから直接アクセスする機能を提供します。
"""

from .mcp_client import MCPClient
from .ahrefs_mcp_wrapper import AhrefsMCPWrapper

__all__ = [
    'MCPClient',
    'AhrefsMCPWrapper',
]

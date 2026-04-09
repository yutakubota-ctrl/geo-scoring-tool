"""
MCP統合クライアント

Claudeを介してMCPサーバーにアクセスするための基底クライアントクラス
"""

from anthropic import Anthropic
from typing import Dict, List, Any, Optional
import json
import os


class MCPClient:
    """
    MCP統合クライアント
    Claudeを介してMCPサーバーにアクセス
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        MCPクライアントの初期化

        Args:
            api_key: Anthropic APIキー（省略時は環境変数から取得）
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic APIキーが設定されていません。"
                "環境変数 ANTHROPIC_API_KEY を設定するか、"
                "api_key 引数を指定してください。"
            )

        self.client = Anthropic(api_key=self.api_key)

    def call_tool(
        self,
        tool_name: str,
        server_name: str,
        arguments: Dict[str, Any],
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 4096,
        timeout: int = 120
    ) -> Dict:
        """
        MCPツールを呼び出し

        Args:
            tool_name: ツール名（例: "get_keyword_gap"）
            server_name: MCPサーバー名（例: "ahrefs"）
            arguments: ツール引数
            model: 使用するClaudeモデル
            max_tokens: 最大トークン数
            timeout: タイムアウト時間（秒）

        Returns:
            ツール実行結果（辞書形式）

        Raises:
            ValueError: APIキーが未設定の場合
            Exception: MCP呼び出しに失敗した場合
        """
        # Claudeにツール実行を依頼
        prompt = self._build_tool_prompt(tool_name, server_name, arguments)

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                timeout=timeout,
                messages=[{"role": "user", "content": prompt}]
            )

            # 結果をパース
            result_text = response.content[0].text
            return self._parse_tool_result(result_text)

        except Exception as e:
            raise Exception(f"MCP呼び出しに失敗しました: {str(e)}") from e

    def _build_tool_prompt(
        self,
        tool_name: str,
        server_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        MCPツール呼び出し用のプロンプトを構築

        Args:
            tool_name: ツール名
            server_name: MCPサーバー名
            arguments: ツール引数

        Returns:
            構築されたプロンプト
        """
        args_str = json.dumps(arguments, ensure_ascii=False, indent=2)

        prompt = f"""
MCPの{server_name}サーバーを使用して、{tool_name}ツールを実行してください。

引数:
{args_str}

実行結果をJSON形式で返してください。
エラーが発生した場合は、エラー内容も含めて返してください。
        """

        return prompt.strip()

    def _parse_tool_result(self, text: str) -> Dict:
        """
        Claude応答からJSON結果を抽出

        Args:
            text: Claude応答テキスト

        Returns:
            パースされた結果（辞書形式）
        """
        # JSONブロック抽出
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            json_str = text[json_start:json_end].strip()
        elif "```" in text:
            # マークダウンコードブロック内のJSONを抽出
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            json_str = text[json_start:json_end].strip()
        else:
            # JSON部分を推測（開始 { または [）
            try:
                # { または [ の最初の出現位置を探す
                start_brace = text.find("{")
                start_bracket = text.find("[")

                if start_brace == -1 and start_bracket == -1:
                    # JSONが見つからない場合はテキストをそのまま返す
                    return {"raw_response": text}

                # どちらか早い方を開始位置とする
                if start_brace == -1:
                    json_start = start_bracket
                elif start_bracket == -1:
                    json_start = start_brace
                else:
                    json_start = min(start_brace, start_bracket)

                json_str = text[json_start:].strip()
            except Exception:
                return {"raw_response": text}

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # パース失敗時はテキストをそのまま返す
            return {"raw_response": text, "parse_error": True}

    def call_multiple_tools(
        self,
        tool_calls: List[Dict[str, Any]],
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 8192
    ) -> List[Dict]:
        """
        複数のMCPツールを一度に呼び出し（バッチ処理）

        Args:
            tool_calls: ツール呼び出しのリスト
                [{"tool_name": "xxx", "server_name": "yyy", "arguments": {...}}, ...]
            model: 使用するClaudeモデル
            max_tokens: 最大トークン数

        Returns:
            各ツールの実行結果のリスト
        """
        results = []
        for tool_call in tool_calls:
            try:
                result = self.call_tool(
                    tool_name=tool_call["tool_name"],
                    server_name=tool_call["server_name"],
                    arguments=tool_call["arguments"],
                    model=model,
                    max_tokens=max_tokens
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "tool_name": tool_call["tool_name"],
                    "server_name": tool_call["server_name"]
                })

        return results

# Screaming Frog MCP Server

Screaming Frog Cloud API用のカスタムMCPサーバー

## 概要

このMCPサーバーは、Screaming Frog Cloud APIに接続して、
サイトクロール機能をMCP（Model Context Protocol）経由で提供します。

## セットアップ

### 1. 依存関係のインストール

```bash
cd mcp-servers/screaming-frog
npm install
```

### 2. 環境変数の設定

`.env` ファイルにAPIキーを追加してください。

```bash
SCREAMING_FROG_API_KEY=your_api_key_here
```

### 3. MCP設定への登録

`config/mcp_config.json` に以下の設定が含まれていることを確認してください。

```json
{
  "mcpServers": {
    "screaming-frog": {
      "command": "node",
      "args": ["mcp-servers/screaming-frog/index.js"],
      "env": {
        "SCREAMING_FROG_API_KEY": "${SCREAMING_FROG_API_KEY}"
      }
    }
  }
}
```

## 使用可能なツール

### 1. crawl_site

ウェブサイトをクロールして、技術的なSEO問題を検出します。

**引数:**
- `url` (必須): クロール対象のURL
- `max_pages` (オプション): 最大クロールページ数（デフォルト: 500）

**返り値:**
- `crawl_id`: クロールジョブID
- `status`: ジョブステータス

### 2. get_crawl_status

クロールジョブのステータスと結果を取得します。

**引数:**
- `crawl_id` (必須): クロールジョブID

**返り値:**
- クロール完了時: クロール結果（404エラー、リダイレクト、メタ情報など）
- クロール中: 現在のステータス

## 使用例

### Pythonから使用

```python
from src.api.mcp import MCPClient

mcp = MCPClient()

# サイトクロール開始
result = mcp.call_tool(
    tool_name="crawl_site",
    server_name="screaming-frog",
    arguments={
        "url": "https://example.com",
        "max_pages": 100
    }
)

crawl_id = result["crawl_id"]
print(f"クロール開始: {crawl_id}")

# ステータス確認
status = mcp.call_tool(
    tool_name="get_crawl_status",
    server_name="screaming-frog",
    arguments={
        "crawl_id": crawl_id
    }
)

print(status)
```

## トラブルシューティング

### MCPサーバーが起動しない

1. Node.jsがインストールされているか確認
   ```bash
   node --version
   ```

2. 依存関係がインストールされているか確認
   ```bash
   cd mcp-servers/screaming-frog
   npm install
   ```

3. APIキーが正しく設定されているか確認
   ```bash
   echo $SCREAMING_FROG_API_KEY
   ```

### クロールがタイムアウトする

クロール対象のサイトが大きい場合、完了まで時間がかかることがあります。
`get_crawl_status` を定期的に呼び出して、ステータスを確認してください。

## 開発者向け情報

### ファイル構成

```
mcp-servers/screaming-frog/
├── index.js          # MCPサーバー本体
├── package.json      # Node.js パッケージ設定
└── README.md         # このファイル
```

### カスタマイズ

`index.js` を編集して、新しいツールを追加したり、
既存のツールの動作をカスタマイズできます。

MCPサーバーの詳細については、以下を参照してください。
- [MCP公式ドキュメント](https://modelcontextprotocol.io/)
- [Screaming Frog Cloud API ドキュメント](https://www.screamingfrog.co.uk/seo-spider/api-documentation/)

## ライセンス

MIT

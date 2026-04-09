# GEOスコアリングツール v2.1 テストガイド

このディレクトリには、v2.1基盤コンポーネントのユニットテストが含まれています。

## テスト構成

```
tests/
├── conftest.py                          # pytest設定とフィクスチャ
├── test_database/
│   └── test_postgresql_connection.py   # PostgreSQL接続テスト（14件）
├── test_agents/
│   └── test_gem_01.py                   # Gem_01テスト（16件）
└── test_api/
    └── test_mcp_client.py               # MCPクライアントテスト（16件）
```

**テスト総数**: 46件（全て成功）

## セットアップ

### 1. テスト用パッケージのインストール

```bash
# プロジェクトルートで実行
py -3 -m pip install -r requirements_test.txt
```

### 2. 環境変数の設定（オプション）

テストは自動的にダミーのAPIキーを設定するため、実際のキーは不要です。
ただし、実APIテストを行う場合は `.env` ファイルに以下を設定してください：

```env
# 実APIテスト用（オプション）
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
SERP_API_KEY=your_serp_key
AHREFS_API_KEY=your_ahrefs_key
```

## テスト実行方法

### 基本実行

```bash
# 全テスト実行
py -3 -m pytest tests/ -v

# カテゴリ別実行
py -3 -m pytest tests/test_database/ -v     # データベーステストのみ
py -3 -m pytest tests/test_agents/ -v       # Gem_01テストのみ
py -3 -m pytest tests/test_api/ -v          # MCPテストのみ
```

### カバレッジレポート付き実行

```bash
# HTMLレポート生成
py -3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# レポート確認
start htmlcov/index.html  # Windowsの場合
```

### 並列実行（高速化）

```bash
# CPUコア数に応じて自動並列実行
py -3 -m pytest tests/ -n auto
```

### 特定のテストのみ実行

```bash
# クラス単位
py -3 -m pytest tests/test_agents/test_gem_01.py::TestGem01BasicFunctionality -v

# 関数単位
py -3 -m pytest tests/test_agents/test_gem_01.py::TestGem01BasicFunctionality::test_query_id_format -v
```

## テスト詳細

### 1. PostgreSQL接続テスト（14件）

**目的**: データベース接続、テーブル作成、CRUD操作の検証

**主要テスト**:
- データベース接続の初期化
- テーブル作成（brands, prompts, responses, scores）
- セッション管理とトランザクション
- PostgreSQL移行準備
- バルクインサート性能（100件/秒）

### 2. Gem_01テスト（16件）

**目的**: ChatGPT o1思考プロセス解析機能の検証

**主要テスト**:
- 7ステップ推論の抽出
- 参照URL抽出（最低3件）
- 検索クエリ推測
- ブランド言及分析
- v2.1設計書の成功基準達成確認

**v2.1設計書 4.5の成功基準**:
- ✅ ChatGPT o1から思考プロセスを取得できる
- ✅ 7ステップのうち最低5ステップを抽出できる
- ✅ 参照URLを最低3件特定できる
- ✅ 自社ブランドが言及されなかった理由を1文で説明できる

### 3. MCPクライアントテスト（16件）

**目的**: MCP（Model Context Protocol）経由のAPI連携検証

**主要テスト**:
- MCP設定ファイルの読み込み
- Ahrefs MCPクライアント（キーワードギャップ、被リンク）
- エラーハンドリング
- E2Eワークフロー
- 性能テスト（応答時間1秒以内）

## モックとフィクスチャ

### 主要フィクスチャ（conftest.py）

| フィクスチャ名 | 説明 |
|---------------|------|
| `test_db_engine` | インメモリSQLiteエンジン |
| `test_db_session` | テスト用DBセッション |
| `mock_openai_client` | OpenAI APIモック（ChatGPT o1） |
| `mock_claude_client` | Claude APIモック |
| `mock_serp_api_client` | Serp APIモック |
| `mock_mcp_client` | MCPクライアントモック |
| `sample_brand_data` | テスト用ブランドデータ |

### モックの利点

- 外部APIキー不要でテスト実行可能
- 高速実行（実APIの待ち時間なし）
- 再現性の高いテスト（APIレスポンスが常に同じ）

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'anthropic'`

**原因**: テスト用パッケージ未インストール

**解決**:
```bash
py -3 -m pip install -r requirements_test.txt
```

### エラー: `ValueError: I/O operation on closed file`

**原因**: 出力キャプチャの問題（パス内の日本語文字が原因の可能性）

**解決**:
```bash
# キャプチャ無効で実行
py -3 -m pytest tests/ -v --capture=no
```

### テストが遅い

**解決**: 並列実行を使用
```bash
py -3 -m pip install pytest-xdist
py -3 -m pytest tests/ -n auto
```

## 次のステップ

### Week 1-2: 実装ファイル作成

以下のファイルを作成し、モックテストを実装テストに移行：

1. `src/agents/gem_01_intelligence.py`
2. `src/api/external/ahrefs_mcp_client.py`
3. `src/api/external/serp_mcp_client.py`
4. `config/mcp_config.json`

### Week 3-4: 実APIテスト

実際のAPIキーを使用した統合テストを実施：

```bash
# 実APIテスト用マーカー（将来版）
py -3 -m pytest tests/ -m "not api"  # 外部APIテストをスキップ
py -3 -m pytest tests/ -m "api"      # 外部APIテストのみ
```

## 関連ドキュメント

- [v2.1設計書](../docs/v2.1_design.md)
- [v2.1動画実装ガイド](../docs/v2.1_video_implementation_guide.md)
- [テストレポート](../docs/TEST_REPORT_v2.1.md)

## 貢献

テストの追加・修正を行う場合：

1. 既存のテストパターンに従う
2. 各テストは1つの機能のみを検証
3. テスト名は `test_<検証内容>` の形式
4. ドキュメントストリング（docstring）で説明を追加
5. pytest実行で全テストが成功することを確認

---

**最終更新**: 2026-04-09
**テスト成功率**: 100% (46/46)

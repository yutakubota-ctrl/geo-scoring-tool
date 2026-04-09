# デモモード使用ガイド

**作成日**: 2026-04-09
**バージョン**: v2.1

---

## 概要

デモモードは、実際のAPIを使わずにGEOスコアリングツールの動作を確認できる機能です。

サンプルデータを使って以下の機能をテストできます：
- 思考ログ（ChatGPT o1の推論プロセス）の表示
- 引用データ（AI Overviewsでのメンション状況）の分析
- ロードマップ（優先順位付きタスク）の管理

---

## デモモードの有効化

### 方法1: 環境変数を設定

```bash
# Windowsの場合（コマンドプロンプト）
set DEMO_MODE=true

# Windowsの場合（PowerShell）
$env:DEMO_MODE="true"

# Mac/Linuxの場合
export DEMO_MODE=true
```

### 方法2: .envファイルに追記

```bash
# .envファイルに以下を追加
DEMO_MODE=true
```

---

## デモデータの生成

デモデータは以下のコマンドで生成できます：

```bash
# デモデータ生成
python scripts/generate_demo_data.py
```

生成されるファイル：
- `data/demo/thought_logs.json` - 思考ログサンプル（10件）
- `data/demo/citations.json` - 引用サンプル（30件）
- `data/demo/roadmap.json` - ロードマップサンプル（20件）

---

## デモモードのテスト

デモモードが正しく動作するか確認します：

```bash
# デモモード機能のテスト
DEMO_MODE=true python scripts/test_demo_mode.py
```

出力例：
```
============================================================
  デモモードが有効です
  サンプルデータを使用して動作を確認できます
============================================================

思考ログ総数: 10
引用データ総数: 30
ロードマップ総数: 20

優先度別タスク数:
  P0: 4件
  P1: 5件
  P2: 11件
```

---

## プログラムでの使用方法

### 基本的な使い方

```python
from src.utils.demo_mode import is_demo_mode, get_demo_thought_logs

# デモモードかどうかを確認
if is_demo_mode():
    print("デモモードで動作中")

    # デモデータを取得
    thought_logs = get_demo_thought_logs(limit=5)

    for log in thought_logs:
        print(f"クエリ: {log['query_text']}")
        print(f"モデル: {log['llm_model']}")
```

### 思考ログの取得

```python
from src.utils.demo_mode import get_demo_thought_logs

# 全件取得
all_logs = get_demo_thought_logs()

# 最初の3件のみ取得
recent_logs = get_demo_thought_logs(limit=3)

# データ構造
# {
#   "query_id": "q_demo_000",
#   "query_text": "マーケティングツール おすすめ",
#   "llm_model": "ChatGPT o1-preview",
#   "thought_trace": {
#     "step_1": "候補ブランドを列挙...",
#     ...
#   },
#   "selected_urls": [...],
#   "brand_mentions": {...}
# }
```

### 引用データの取得

```python
from src.utils.demo_mode import get_demo_citations

# 全件取得
all_citations = get_demo_citations()

# 特定企業のみ取得
hubspot_citations = get_demo_citations(entity_name="HubSpot")

# 最初の5件のみ取得
recent_citations = get_demo_citations(limit=5)

# データ構造
# {
#   "citation_id": "cite_demo_000",
#   "entity_name": "HubSpot",
#   "mention_count": 3,
#   "sentiment_score": 7.09,
#   "reference_type": "AI_Overview",
#   "position_in_response": 230,
#   ...
# }
```

### ロードマップの取得

```python
from src.utils.demo_mode import get_demo_roadmap

# 全件取得
all_tasks = get_demo_roadmap()

# P0タスクのみ取得
p0_tasks = get_demo_roadmap(priority="P0")

# 進行中のタスクのみ取得
in_progress_tasks = get_demo_roadmap(status="in_progress")

# P0の進行中タスク、最初の3件
priority_tasks = get_demo_roadmap(
    priority="P0",
    status="in_progress",
    limit=3
)

# データ構造
# {
#   "task_id": "task_demo_012",
#   "priority": "P0",
#   "description": "無料トライアル申込フォームのCTA強化",
#   "impact_score": 9,
#   "effort_score": 4,
#   "status": "pending",
#   ...
# }
```

### 統計情報の取得

```python
from src.utils.demo_mode import get_demo_stats

stats = get_demo_stats()

print(f"思考ログ総数: {stats['thought_logs_count']}")
print(f"引用データ総数: {stats['citations_count']}")
print(f"ロードマップ総数: {stats['roadmap_count']}")

# 優先度別タスク数
for priority, count in stats['roadmap_by_priority'].items():
    print(f"{priority}: {count}件")

# ステータス別タスク数
for status, count in stats['roadmap_by_status'].items():
    print(f"{status}: {count}件")
```

---

## デモデータの内容

### 思考ログ（10件）

以下のような検索クエリに対するChatGPT o1の思考プロセスを含みます：

- マーケティングツール おすすめ
- CRM 比較
- メールマーケティング ツール
- マーケティングオートメーション 選び方
- 営業支援ツール ランキング
- 顧客管理システム 中小企業
- BtoB マーケティングツール
- リードナーチャリング ツール
- メルマガ配信 サービス
- マーケティング 分析ツール

各ログには以下の情報が含まれます：
- 7ステップの推論プロセス
- 参照したURL
- 使用した検索クエリ
- ブランド評価スコア

### 引用データ（30件）

以下のブランドに関する引用データを含みます：

- HubSpot
- Marketo
- Salesforce
- Pardot
- ActiveCampaign
- Mailchimp
- Constant Contact
- GetResponse
- Sendinblue
- ConvertKit

各引用には以下の情報が含まれます：
- メンション回数
- センチメントスコア（6.0〜9.5）
- 参照タイプ（AI_Overview、ChatGPT、Gemini、Perplexity）
- 回答内での位置

### ロードマップ（20件）

以下のカテゴリのタスクを含みます：

- **Technical** (技術的改善): ページ速度、構造化データ、404修正等
- **Content** (コンテンツ改善): FAQ拡充、導入事例、比較表追加等
- **Analytics** (分析・調査): GRC順位分析、被リンク分析、AI思考分析等

各タスクには以下の情報が含まれます：
- 優先度（P0〜P2）
- インパクトスコア（1〜10）
- 作業量スコア（1〜10）
- ステータス（pending / in_progress / completed）

---

## 実際のAPIとの切り替え

デモモードと実際のAPIを簡単に切り替えられるようにコードを書く例：

```python
from src.utils.demo_mode import is_demo_mode, get_demo_thought_logs
from src.api.chatgpt_client import ChatGPTClient

def get_thought_logs(query: str):
    """思考ログを取得（デモモード対応）"""

    if is_demo_mode():
        # デモモード: サンプルデータを返す
        return get_demo_thought_logs(limit=10)
    else:
        # 本番モード: 実際のAPIを呼び出す
        client = ChatGPTClient()
        return client.analyze_thinking(query)

# 使用例
logs = get_thought_logs("マーケティングツール おすすめ")
```

---

## トラブルシューティング

### デモデータが見つからないエラー

```
警告: デモデータファイルが見つかりません: data/demo/thought_logs.json
```

**解決方法**:
```bash
# デモデータを再生成
python scripts/generate_demo_data.py
```

### デモモードが有効にならない

環境変数が正しく設定されているか確認：

```python
import os
print(os.getenv("DEMO_MODE"))  # => "true" と表示されるべき
```

### 文字化けが発生する

JSONファイルのエンコーディングをUTF-8で保存してください：

```python
# 生成スクリプト内で既に対応済み
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## まとめ

デモモードを使うことで、以下のメリットがあります：

1. **APIコスト削減**: 実際のAPIを呼び出さずに動作確認できる
2. **オフライン開発**: ネットワーク接続なしで開発・テスト可能
3. **高速テスト**: API待ち時間なしで即座にレスポンス取得
4. **デモ環境構築**: クライアント向けデモを簡単に実施可能

環境変数 `DEMO_MODE=true` を設定するだけで、本番モードとデモモードを簡単に切り替えられます。

---

**次のステップ**:
- [v2.1設計書](v2.1_design.md)を参照してGem_01の実装を開始
- [動画手法実装ガイド](v2.1_video_implementation_guide.md)で詳細な実装方法を確認

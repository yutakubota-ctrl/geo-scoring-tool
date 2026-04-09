# GEOスコアリングツール v2.1 ダッシュボード

**実装日**: 2026-04-09
**バージョン**: 2.1
**実装内容**: 3つの新機能画面（思考ログ、ロードマップ、エコー監視）

---

## クイックスタート

### 1. デモモードで起動

```bash
# Windowsの場合
cd "C:\Users\yutak\OneDrive\デスクトップ\GEOスコアリングツール"
scripts\start_dashboard_demo.bat

# Mac/Linuxの場合
cd "C:\Users\yutak\OneDrive\デスクトップ\GEOスコアリングツール"
export DEMO_MODE=true
streamlit run src/dashboard/app.py
```

### 2. ブラウザでアクセス

ブラウザで以下のURLにアクセスします。

```
http://localhost:8501
```

### 3. 新機能画面の確認

サイドバーから以下の画面にアクセスできます。

- **4_thought_log**: ChatGPT o1の7ステップ推論プロセス
- **5_roadmap**: Impact × Effort マトリクスによる優先度管理
- **6_echo_monitor**: AI Overviewsでのメンション追跡

---

## 実装内容

### 新規作成ファイル

#### ダッシュボード画面

| ファイル | 説明 | サイズ |
|---------|------|--------|
| `src/dashboard/pages/4_thought_log.py` | 思考ログ画面 | 9,133 bytes |
| `src/dashboard/pages/5_roadmap.py` | ロードマップ画面 | 13,485 bytes |
| `src/dashboard/pages/6_echo_monitor.py` | エコー監視画面 | 17,323 bytes |

#### デモデータ

| ファイル | 説明 |
|---------|------|
| `data/demo/thought_log_sample.json` | 思考ログのサンプルデータ |
| `data/demo/roadmap_sample.json` | ロードマップのサンプルデータ |
| `data/demo/echo_monitor_sample.json` | エコー監視のサンプルデータ |

#### ドキュメント・スクリプト

| ファイル | 説明 |
|---------|------|
| `docs/v2.1_dashboard_implementation.md` | 実装ドキュメント |
| `scripts/verify_dashboard.py` | 検証スクリプト |
| `scripts/start_dashboard_demo.bat` | 起動スクリプト（Windows） |
| `README_v2.1_dashboard.md` | このファイル |

---

## 画面別機能

### 1. 思考ログ画面（4_thought_log.py）

**目的**: ChatGPT o1の推論プロセスを可視化

**主要機能**:
- 7ステップの推論プロセス（折りたたみ可能）
- 参照URL一覧（クリック可能）
- 検索クエリ候補
- ブランド評価（推薦順位とセンチメント）

**デザイン特徴**:
- 紫系グラデーションカード
- タイムライン形式
- センチメント別色分け

### 2. ロードマップ画面（5_roadmap.py）

**目的**: Impact × Effort マトリクスで優先度管理

**主要機能**:
- Impact × Effortの散布図（4象限分析）
- 優先度別タスクリスト（P0/P1/P2）
- ステータス別フィルタ（Pending/In_Progress/Done）
- 統計情報（優先度分布、ステータス分布）

**デザイン特徴**:
- 優先度別バッジ（P0: 赤、P1: 黄、P2: 青）
- インタラクティブな散布図
- ホバーアニメーション

### 3. エコー監視画面（6_echo_monitor.py）

**目的**: AI Overviewsでのメンション追跡

**主要機能**:
- メンション数推移（過去4週間）
- センチメント分析（ゲージチャート）
- 参照順位の変化
- LLMカバレッジ（ChatGPT/Gemini/Claude/Perplexity）
- 最新引用一覧

**デザイン特徴**:
- エコーステータスバナー（成功/部分成功/失敗）
- センチメントゲージ（-1.0〜1.0）
- 引用コンテキストカード

---

## デザインガイドライン

### 美的方向性

**コンセプト**: "Data-Driven Elegance"

- **目的**: 複雑なAI分析データを美しく直感的に表示
- **トーン**: プロフェッショナル × モダン × アクセシブル
- **差別化**: グラデーションカード + インタラクティブチャート

### カラーパレット

**プライマリーカラー**:
- 紫系グラデーション: `#667eea → #764ba2`
- 緑系グラデーション: `#11998e → #38ef7d`

**優先度カラー**:
- P0（最優先）: `#f5576c`（赤）
- P1（重要）: `#fee140`（黄）
- P2（通常）: `#a8edea`（水色）

**センチメントカラー**:
- ポジティブ: `#4CAF50`
- 中立: `#FF9800`
- ネガティブ: `#F44336`

---

## 技術スタック

| 技術 | バージョン | 用途 |
|------|----------|------|
| **Streamlit** | 最新版 | Webフレームワーク |
| **Plotly** | 最新版 | グラフ描画 |
| **Pandas** | 最新版 | データ処理 |
| **SQLAlchemy** | 最新版 | データベースORM |

---

## 検証

### 検証スクリプトの実行

```bash
# 検証スクリプトを実行
DEMO_MODE=true py -3 scripts/verify_dashboard.py
```

### 検証項目

- [x] デモデータファイルが存在する
- [x] JSONファイルの妥当性
- [x] 必要なライブラリがインストールされている
- [x] ダッシュボードページファイルが存在する
- [x] 環境変数が設定されている

---

## トラブルシューティング

### 1. 画面が表示されない

**原因**: デモデータファイルが見つからない

**解決策**:
```bash
ls -la data/demo/
# ファイルが存在するか確認
```

### 2. グラフが表示されない

**原因**: Plotlyがインストールされていない

**解決策**:
```bash
pip install plotly
```

### 3. 環境変数エラー

**原因**: DEMO_MODEが設定されていない

**解決策**:
```bash
# Windows
set DEMO_MODE=true

# Mac/Linux
export DEMO_MODE=true
```

---

## 本番環境への移行

### データベース統合

現在はデモモードでJSONファイルを読み込んでいます。本番環境では以下のように変更します。

```python
# デモモード
if demo_mode:
    with open("data/demo/thought_log_sample.json") as f:
        data = json.load(f)

# 本番モード
else:
    from src.database.connection import db
    from src.database.models_v2.llm_thought_log import LLMThoughtLog

    with db.get_session() as session:
        latest_log = session.query(LLMThoughtLog).order_by(
            LLMThoughtLog.executed_at.desc()
        ).first()
        data = latest_log.to_dict()
```

### 環境変数設定

```bash
export DEMO_MODE=false
export DATABASE_URL=postgresql://user:password@localhost:5432/geo_scoring
```

---

## スクリーンショット

### 思考ログ画面

![思考ログ画面](スクリーンショットのパス)

- 7ステップの推論プロセス
- タイムライン形式
- 参照URL一覧

### ロードマップ画面

![ロードマップ画面](スクリーンショットのパス)

- Impact × Effort マトリクス
- 優先度別タスクリスト
- 統計情報

### エコー監視画面

![エコー監視画面](スクリーンショットのパス)

- メンション数推移
- センチメントゲージ
- 最新引用一覧

---

## 次のステップ

### Phase 1: MVP開発（Week 3-8）

- [ ] Gem_01（GEO_Intelligence_Analyst）の実装
- [ ] Gem_02（Gap_Strategist）の実装
- [ ] Gem_05（Echo_Monitor）の実装
- [ ] データベース統合
- [ ] リアルタイムデータ更新

### Phase 2: 自社検証（Week 9-12）

- [ ] 自社サイトでの実運用
- [ ] 引用率の向上検証
- [ ] ケーススタディ作成

### Phase 3: 代理店展開（将来版）

- [ ] マルチテナント対応
- [ ] OEM契約
- [ ] 営業開始

---

## ライセンス

（プロジェクトのライセンスに従う）

---

## お問い合わせ

質問や問題がある場合は、プロジェクトの管理者に連絡してください。

---

**実装完了日**: 2026-04-09
**最終更新**: 2026-04-09

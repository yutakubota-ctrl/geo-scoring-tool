# GEOスコアリングツール

AI検索（Google Gemini）における自社ブランドの認知度・推奨度を定点観測し、競合と比較分析するためのツールです。

## 機能概要

- **定期モニタリング**: 週1回または月2回の自動スコアリング
- **4つの評価指標**: 認知度、推奨度、掲載位置、情報正確性
- **競合比較**: 最大5社との比較分析
- **ダッシュボード**: 3つの画面で異なる視点から分析

## 評価指標

| 指標 | 点数 | 説明 |
|------|------|------|
| 認知スコア | 0-10点 | ブランド名が回答に含まれているか |
| 推奨度スコア | -10〜30点 | どのように推奨されているか |
| ポジションスコア | 0-20点 | 回答のどの位置で言及されているか |
| 正確性スコア | 0-40点 | 情報が正確かどうか |

**合計: 最大100点**

## セットアップ

### クイックスタート（デモモード）

APIキーなしでデモを試すには、以下の手順でローカル起動できます。

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. 環境変数を設定（デモモード）
echo "DEMO_MODE=true" > .env

# 3. ダッシュボードを起動
streamlit run src/dashboard/app.py
```

### 本番環境セットアップ

#### 1. 必要条件

- Python 3.10以上
- Google Gemini API キー（本番環境のみ）

#### 2. インストール

```bash
# 依存パッケージをインストール
pip install -r requirements_v2.txt  # フル機能版
# または
pip install -r requirements.txt     # デモモード用（最小構成）
```

### 3. 環境設定

`.env.example` をコピーして `.env` を作成し、APIキーを設定します。

```bash
cp .env.example .env
```

`.env` ファイルを編集:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///data/geo_scoring.db
BATCH_SCHEDULE=weekly
BATCH_DAY=monday
LOG_LEVEL=INFO
```

### 4. ブランド設定

`config/brands.yaml` を編集して、自社ブランドと競合を設定します。

```yaml
own_brand:
  name: "自社ブランド名"
  domain: "example.com"
  keywords:
    - "キーワード1"
    - "キーワード2"

competitors:
  - name: "競合A社"
    domain: "competitor-a.com"
```

### 5. データベース初期化

```bash
python -c "from src.database.connection import init_database; init_database()"
```

## 使い方

### デモモード（Streamlit Cloud）

**デモモード** では、本番APIキーなしでサンプルデータを使って動作を確認できます。

Streamlit Cloud でのデプロイ方法は、[Streamlit Cloud デプロイガイド](docs/STREAMLIT_CLOUD_DEPLOY.md) を参照してください。

### ローカルでのダッシュボード起動

```bash
streamlit run src/dashboard/app.py
```

ブラウザで `http://localhost:8501` を開きます。

### バッチ処理の実行

**1回だけ実行:**

```bash
python src/batch/scheduler.py --once
```

**スケジューラーとして常駐:**

```bash
python src/batch/scheduler.py --daemon
```

## ダッシュボード画面

### 1. サマリー画面（経営向け）

- 総合スコアの表示
- 前回との比較
- 競合ランキング
- アラート通知

### 2. トレンド画面（マーケター向け）

- 4指標のレーダーチャート
- 時系列推移グラフ
- 競合との比較表

### 3. 生データ画面（実務担当者向け）

- 個別回答の確認
- フィルター機能
- CSV/Excelエクスポート

## プロジェクト構造

```
geo-scoring-tool/
├── config/
│   ├── settings.py       # 設定管理
│   ├── prompts.yaml      # 評価プロンプト
│   └── brands.yaml       # ブランド設定
├── src/
│   ├── api/              # Gemini API連携
│   ├── scoring/          # スコアリングエンジン
│   ├── database/         # データベース
│   ├── dashboard/        # Streamlitダッシュボード
│   └── batch/            # バッチ処理
├── data/                 # SQLiteデータベース
├── logs/                 # ログファイル
├── requirements.txt
└── README.md
```

## トラブルシューティング

### APIエラーが発生する

- `GEMINI_API_KEY` が正しく設定されているか確認
- APIの利用制限に達していないか確認

### ダッシュボードが表示されない

- Streamlitが正しくインストールされているか確認
- ポート8501が使用可能か確認

### データが表示されない

- バッチ処理を実行してデータを生成
- データベースファイルが存在するか確認

## ライセンス

MIT License

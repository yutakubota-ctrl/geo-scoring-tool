# Streamlit Community Cloud デプロイガイド

このガイドでは、GEOスコアリングツールをStreamlit Community Cloud（無料）にデプロイする手順を説明します。

## デモモードについて

デプロイされるアプリは **デモモード** で動作します。
- 本番APIキー不要
- サンプルデータで動作
- すべての画面を確認可能

本番環境（実際のAPI連携）での運用が必要な場合は、別途環境構築が必要です。

---

## 前提条件

以下のアカウントが必要です（すべて無料）:

1. **GitHub アカウント**
2. **Streamlit Community Cloud アカウント**（GitHubでサインイン可能）

---

## 手順1: GitHubリポジトリの作成

### 1-1. GitHub上でリポジトリを作成

1. https://github.com にアクセス
2. 右上の「+」→「New repository」をクリック
3. 以下のように設定:
   - **Repository name**: `geo-scoring-tool`（任意の名前）
   - **Public** または **Private**（Publicを推奨）
   - README, .gitignore, license は **追加しない**（既に存在するため）

4. 「Create repository」をクリック

### 1-2. ローカルコードをGitHubにプッシュ

作成されたリポジトリのURLが表示されるので、以下のコマンドを実行します。

```bash
# プロジェクトディレクトリに移動
cd "C:\Users\yutak\OneDrive\デスクトップ\GEOスコアリングツール"

# リモートリポジトリを追加（YOUR_USERNAME を実際のユーザー名に置き換え）
git remote add origin https://github.com/YOUR_USERNAME/geo-scoring-tool.git

# すべてのファイルをステージング
git add .

# 初回コミット
git commit -m "feat: v2.1 dashboard with demo mode for Streamlit Cloud"

# GitHubにプッシュ
git branch -M main
git push -u origin main
```

**注意**: `.gitignore` により、以下のファイルは自動的に除外されます:
- `.env`（APIキー）
- `data/geo_scoring.db`（SQLiteデータベース）
- `.streamlit/secrets.toml`（ローカルシークレット）

---

## 手順2: Streamlit Community Cloud でアプリをデプロイ

### 2-1. Streamlit Cloud にサインイン

1. https://share.streamlit.io/ にアクセス
2. 「Sign up」または「Sign in with GitHub」をクリック
3. GitHubアカウントで認証

### 2-2. 新しいアプリをデプロイ

1. ダッシュボードで「New app」をクリック
2. 以下の情報を入力:

| 項目 | 入力内容 |
|------|----------|
| Repository | `YOUR_USERNAME/geo-scoring-tool` |
| Branch | `main` |
| Main file path | `src/dashboard/app.py` |

3. 「Advanced settings」をクリック（オプション）
   - Python version: `3.10` を選択

4. 「Deploy!」をクリック

---

## 手順3: 環境変数の設定

デプロイが開始されると、アプリの設定画面が表示されます。

### 3-1. Secrets（環境変数）の設定

1. アプリの設定画面で「Settings」→「Secrets」を開く
2. 以下のように入力:

```toml
DEMO_MODE = true
DEBUG_MODE = false
```

3. 「Save」をクリック

これで、デモモードでアプリが起動します。

---

## 手順4: デプロイ完了を確認

1. デプロイが完了すると、アプリのURLが表示されます
   - 例: `https://geo-scoring-tool.streamlit.app/`

2. URLにアクセスして動作を確認

**確認項目**:
- サマリー画面が表示される
- サンプルデータが表示される
- すべてのページ（1〜6）が動作する

---

## トラブルシューティング

### デプロイが失敗する

**原因**: requirements.txt の依存関係エラー

**解決策**:
1. Streamlit Cloud のログを確認
2. エラーメッセージに従ってパッケージバージョンを調整
3. 変更をコミット&プッシュ → 自動的に再デプロイされる

### アプリが起動しない

**原因**: `DEMO_MODE` が設定されていない

**解決策**:
1. Streamlit Cloud の「Settings」→「Secrets」を開く
2. `DEMO_MODE = true` を追加
3. アプリを再起動

### データが表示されない

**原因**: デモデータが生成されていない

**解決策**:
デモモードでは、初回起動時に自動的にサンプルデータが生成されます。
`src/utils/demo_mode.py` が正しく動作しているか確認してください。

---

## 本番環境への移行（オプション）

デモモードから本番環境に移行する場合:

1. **requirements.txt を変更**:
   - `requirements_v2.txt` の内容に置き換え

2. **Secrets に本番APIキーを追加**:

```toml
DEMO_MODE = false
GEMINI_API_KEY = "your_actual_api_key"
DATABASE_URL = "postgresql://..."
```

3. **データベースを変更**:
   - SQLite → PostgreSQL（外部ホスティング）
   - 例: Supabase, Neon, Render など

---

## 参考リンク

- [Streamlit Community Cloud 公式ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [Secrets管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub連携](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

---

## まとめ

これで、Streamlit Community Cloud へのデプロイが完了しました。

デプロイされたアプリは:
- 無料で公開可能
- 自動的に更新（GitHubにプッシュするたびに再デプロイ）
- デモモードで動作（APIキー不要）

本番運用が必要な場合は、上記「本番環境への移行」セクションを参照してください。

"""
GEOスコアリングダッシュボード
Streamlitエントリーポイント
"""
import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db, init_database

# ページ設定
st.set_page_config(
    page_title="GEOスコアリング",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データベース初期化
@st.cache_resource
def setup_database():
    """データベースをセットアップ"""
    init_database()
    return True

# 初期化
setup_database()

# サイドバー
st.sidebar.title("GEOスコアリング")
st.sidebar.markdown("---")
st.sidebar.markdown("""
### ナビゲーション
- **サマリー**: 経営向け概要
- **トレンド**: 競合比較分析
- **生データ**: 詳細データ確認
""")

# メインページ
st.title("GEOスコアリングダッシュボード")
st.markdown("---")

st.markdown("""
## ようこそ

このダッシュボードでは、AI検索（Gemini）における自社ブランドの認知度・推奨度を
定点観測し、競合と比較分析することができます。

### 機能概要

| 画面 | 対象ユーザー | 内容 |
|------|-------------|------|
| サマリー | 経営層 | 総合スコア、前回比較、アラート |
| トレンド | マーケター | 時系列分析、競合比較 |
| 生データ | 実務担当者 | 個別回答の確認、エクスポート |

### 評価指標

1. **認知スコア** (0-10点): ブランド名が言及されているか
2. **推奨度スコア** (-10〜30点): どのように推奨されているか
3. **ポジションスコア** (0-20点): 回答のどこで言及されているか
4. **正確性スコア** (0-40点): 情報が正確かどうか

**合計: 最大100点**

---

左のサイドバーから各画面に移動してください。
""")

# フッター
st.markdown("---")
st.caption("GEOスコアリングツール v1.0")

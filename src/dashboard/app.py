"""
GEOスコアリングダッシュボード
Streamlitエントリーポイント

デザインシステム v2.1適用
"""
import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db, init_database
from src.dashboard.styles.common import (
    get_common_css,
    get_page_header,
    COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle

# ページ設定
st.set_page_config(
    page_title="GEOスコアリング",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# データベース初期化
@st.cache_resource
def setup_database():
    """データベースをセットアップ"""
    init_database()
    return True

# 初期化
setup_database()

# サイドバー
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 1rem 0.5rem;">
        <div style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.5rem;">
            GEOスコアリング
        </div>
        <div style="font-size: 0.875rem; color: rgba(255,255,255,0.7);">
            AI検索最適化ダッシュボード
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="padding: 0 0.5rem;">
        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.5); margin-bottom: 0.75rem;">
            ナビゲーション
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ナビゲーションリンクは自動生成される

# ================================
# メインコンテンツ
# ================================

# ヒーローセクション
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 50%, #3B82F6 100%);
    border-radius: 16px;
    padding: 3rem;
    margin-bottom: 2rem;
    color: white;
    position: relative;
    overflow: hidden;
">
    <div style="position: relative; z-index: 1;">
        <div style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8; margin-bottom: 0.5rem;">
            Welcome to
        </div>
        <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0 0 1rem 0; color: white;">
            GEOスコアリング ダッシュボード
        </h1>
        <p style="font-size: 1.125rem; opacity: 0.9; max-width: 600px; line-height: 1.6; color: white;">
            AI検索（Gemini, ChatGPT）における自社ブランドの認知度・推奨度を定点観測し、
            競合と比較分析するための統合プラットフォームです。
        </p>
    </div>
    <div style="
        position: absolute;
        right: -50px;
        top: -50px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
</div>
""", unsafe_allow_html=True)

# ナビゲーションカード
st.markdown("""
<div style="margin-bottom: 1rem;">
    <h2 style="font-size: 1.25rem; font-weight: 600; color: #1E293B; margin-bottom: 1.5rem;">
        機能一覧
    </h2>
</div>
""", unsafe_allow_html=True)

# 上段: メイン機能 (3カラム)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    " class="nav-card">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
        <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            サマリー
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; line-height: 1.5;">
            経営層向け概要ダッシュボード。総合スコア、前回比較、アラートを一目で確認。
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📈</div>
        <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            トレンド分析
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; line-height: 1.5;">
            マーケター向け詳細分析。時系列推移、競合比較、レーダーチャートで可視化。
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📋</div>
        <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            生データ
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; line-height: 1.5;">
            実務担当者向け。個別回答の確認、フィルタリング、CSV/Excelエクスポート。
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# 下段: v2.1新機能 (3カラム)
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0F172A 0%, #1E40AF 100%);
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        color: white;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🧠</div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.7rem;
                font-weight: 600;
            ">NEW v2.1</div>
        </div>
        <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">
            思考ログ
        </div>
        <div style="font-size: 0.875rem; opacity: 0.9; line-height: 1.5;">
            ChatGPT o1の7ステップ推論プロセスを可視化。AIの判断根拠を詳細に分析。
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        color: white;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🗺</div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.7rem;
                font-weight: 600;
            ">NEW v2.1</div>
        </div>
        <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">
            ロードマップ
        </div>
        <div style="font-size: 0.875rem; opacity: 0.9; line-height: 1.5;">
            Impact x Effortマトリクスで施策を優先順位付け。タスク管理と進捗追跡。
        </div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        color: white;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">👁</div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.7rem;
                font-weight: 600;
            ">NEW v2.1</div>
        </div>
        <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">
            エコー監視
        </div>
        <div style="font-size: 0.875rem; opacity: 0.9; line-height: 1.5;">
            AI Overviewsでのメンション状況をリアルタイム追跡。センチメント分析も。
        </div>
    </div>
    """, unsafe_allow_html=True)

# 評価指標セクション
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
">
    <h2 style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1.5rem;">
        評価指標
    </h2>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;">
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['secondary']} 0%, #60A5FA 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 1.5rem;
            ">👁</div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">認知スコア</div>
            <div style="font-size: 2rem; font-weight: 700; color: {COLORS['secondary']}; margin: 0.5rem 0;">0-10</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">ブランド名の言及有無</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['accent']} 0%, #34D399 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 1.5rem;
            ">💬</div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">推奨度</div>
            <div style="font-size: 2rem; font-weight: 700; color: {COLORS['accent']}; margin: 0.5rem 0;">-10~30</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">推奨の度合い・文脈</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['warning']} 0%, #FBBF24 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 1.5rem;
            ">📍</div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">ポジション</div>
            <div style="font-size: 2rem; font-weight: 700; color: {COLORS['warning']}; margin: 0.5rem 0;">0-20</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">回答内での言及位置</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                font-size: 1.5rem;
            ">✓</div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">正確性</div>
            <div style="font-size: 2rem; font-weight: 700; color: #8B5CF6; margin: 0.5rem 0;">0-40</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">情報の正確さ</div>
        </div>
    </div>
    <div style="
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0,0,0,0.05);
        text-align: center;
    ">
        <span style="font-size: 1rem; color: {COLORS['text_secondary']};">合計スコア: </span>
        <span style="font-size: 1.5rem; font-weight: 700; color: {COLORS['primary']};">最大100点</span>
    </div>
</div>
""", unsafe_allow_html=True)

# フッター
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid rgba(0,0,0,0.05);
">
    <span style="font-size: 0.75rem; color: {COLORS['text_muted']};">
        GEOスコアリングツール v2.1 | Powered by Streamlit
    </span>
</div>
""", unsafe_allow_html=True)

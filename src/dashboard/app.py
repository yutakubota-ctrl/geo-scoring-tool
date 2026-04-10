"""
GEOスコアリングダッシュボード
Streamlitエントリーポイント

デザインシステム v3.0 - AEO Premium Dark Theme
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
    get_icon,
    COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle

# ページ設定（絵文字なし）
st.set_page_config(
    page_title="GEOスコアリング",
    page_icon=None,
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
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        ">
            <div style="
                width: 40px;
                height: 40px;
                background: {COLORS['gradient_accent']};
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                {get_icon('activity', size=22, color=COLORS['text_inverse'])}
            </div>
            <div>
                <div style="font-size: 1.25rem; font-weight: 700; color: {COLORS['text_primary']};">
                    GEOスコアリング
                </div>
            </div>
        </div>
        <div style="font-size: 0.8rem; color: {COLORS['text_muted']}; padding-left: 0;">
            AI検索最適化ダッシュボード
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        height: 1px;
        background: linear-gradient(to right, transparent, {COLORS['border']}, transparent);
        margin: 0.5rem 0 1rem 0;
    "></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0 0.5rem;">
        <div style="
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {COLORS['text_muted']};
            margin-bottom: 0.75rem;
        ">
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
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 20px;
    padding: 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        right: -100px;
        top: -100px;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(222, 255, 154, 0.08) 0%, transparent 70%);
        pointer-events: none;
    "></div>
    <div style="
        position: absolute;
        left: -50px;
        bottom: -50px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.06) 0%, transparent 70%);
        pointer-events: none;
    "></div>

    <div style="position: relative; z-index: 1;">
        <div style="
            display: inline-block;
            background: rgba(222, 255, 154, 0.15);
            border: 1px solid rgba(222, 255, 154, 0.3);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {COLORS['accent']};
            margin-bottom: 1rem;
        ">
            Welcome to
        </div>
        <h1 style="
            font-size: 2.5rem;
            font-weight: 900;
            margin: 0 0 1rem 0;
            color: {COLORS['text_primary']};
            letter-spacing: -0.03em;
            line-height: 1.1;
        ">
            GEOスコアリング<br>
            <span style="
                background: {COLORS['gradient_accent']};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">ダッシュボード</span>
        </h1>
        <p style="
            font-size: 1.125rem;
            color: {COLORS['text_secondary']};
            max-width: 600px;
            line-height: 1.7;
            margin: 0;
        ">
            AI検索（Gemini, ChatGPT）における自社ブランドの認知度・推奨度を定点観測し、
            競合と比較分析するための統合プラットフォームです。
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ナビゲーションカード
st.markdown(f"""
<div style="margin-bottom: 1rem;">
    <h2 style="
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
    ">
        機能一覧
    </h2>
</div>
""", unsafe_allow_html=True)

# 上段: メイン機能 (3カラム)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    " class="nav-card">
        <div style="
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top right, rgba(222, 255, 154, 0.04), transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        "></div>
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, {COLORS['accent_secondary']} 0%, #60a5fa 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        ">
            {get_icon('chart', size=24, color=COLORS['text_inverse'])}
        </div>
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
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        transition: all 0.3s ease;
    " class="nav-card">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, {COLORS['success']} 0%, #86efac 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        ">
            {get_icon('trend', size=24, color=COLORS['text_inverse'])}
        </div>
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
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        transition: all 0.3s ease;
    " class="nav-card">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, {COLORS['warning']} 0%, #fcd34d 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        ">
            {get_icon('data', size=24, color=COLORS['text_inverse'])}
        </div>
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
        background: {COLORS['gradient_primary']};
        border: 1px solid {COLORS['border_accent']};
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top right, rgba(222, 255, 154, 0.08), transparent 60%);
        "></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 1;">
            <div style="
                width: 48px;
                height: 48px;
                background: {COLORS['gradient_accent']};
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                {get_icon('brain', size=24, color=COLORS['text_inverse'])}
            </div>
            <div style="
                background: {COLORS['accent']};
                color: {COLORS['text_inverse']};
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.65rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">NEW v2.1</div>
        </div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                思考ログ
            </div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; line-height: 1.5;">
                ChatGPT o1の7ステップ推論プロセスを可視化。AIの判断根拠を詳細に分析。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #059669 0%, {COLORS['success']} 100%);
        border: 1px solid rgba(74, 222, 128, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at bottom left, rgba(255, 255, 255, 0.1), transparent 60%);
        "></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 1;">
            <div style="
                width: 48px;
                height: 48px;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                {get_icon('map', size=24, color='white')}
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.65rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">NEW v2.1</div>
        </div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 1.125rem; font-weight: 600; color: white; margin-bottom: 0.5rem;">
                ロードマップ
            </div>
            <div style="font-size: 0.875rem; color: rgba(255,255,255,0.9); line-height: 1.5;">
                Impact x Effortマトリクスで施策を優先順位付け。タスク管理と進捗追跡。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #7c3aed 0%, {COLORS['accent_tertiary']} 100%);
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        height: 200px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.1), transparent 60%);
        "></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 1;">
            <div style="
                width: 48px;
                height: 48px;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                {get_icon('eye', size=24, color='white')}
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.65rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">NEW v2.1</div>
        </div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 1.125rem; font-weight: 600; color: white; margin-bottom: 0.5rem;">
                エコー監視
            </div>
            <div style="font-size: 0.875rem; color: rgba(255,255,255,0.9); line-height: 1.5;">
                AI Overviewsでのメンション状況をリアルタイム追跡。センチメント分析も。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 評価指標セクション
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 20px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        right: -50px;
        top: -50px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.05), transparent 70%);
    "></div>

    <h2 style="
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
    ">
        評価指標
    </h2>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;">
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['accent_secondary']} 0%, #60a5fa 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
            ">
                {get_icon('eye', size=28, color=COLORS['text_inverse'])}
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">認知スコア</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
                background: linear-gradient(90deg, {COLORS['accent_secondary']}, #60a5fa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
            ">0-10</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_muted']};">ブランド名の言及有無</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['success']} 0%, #86efac 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
            ">
                {get_icon('message', size=28, color=COLORS['text_inverse'])}
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">推奨度</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
                background: linear-gradient(90deg, {COLORS['success']}, #86efac);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
            ">-10~30</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_muted']};">推奨の度合い・文脈</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['warning']} 0%, #fcd34d 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
            ">
                {get_icon('target', size=28, color=COLORS['text_inverse'])}
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">ポジション</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
                background: linear-gradient(90deg, {COLORS['warning']}, #fcd34d);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
            ">0-20</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_muted']};">回答内での言及位置</div>
        </div>
        <div style="text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, {COLORS['accent_tertiary']} 0%, #c4b5fd 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
            ">
                {get_icon('check', size=28, color=COLORS['text_inverse'])}
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">正確性</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
                background: linear-gradient(90deg, {COLORS['accent_tertiary']}, #c4b5fd);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0.5rem 0;
            ">0-40</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_muted']};">情報の正確さ</div>
        </div>
    </div>
    <div style="
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid {COLORS['border']};
        text-align: center;
    ">
        <span style="font-size: 1rem; color: {COLORS['text_muted']};">合計スコア: </span>
        <span style="
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            background: {COLORS['gradient_accent']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">最大100点</span>
    </div>
</div>
""", unsafe_allow_html=True)

# フッター
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid {COLORS['border']};
">
    <span style="font-size: 0.75rem; color: {COLORS['text_muted']};">
        GEOスコアリングツール v3.0 | Powered by Streamlit
    </span>
</div>
""", unsafe_allow_html=True)

"""
デモモード切替トグル

全ページ共通の右上に配置されるトグルスイッチ
session_stateでデモモードのオン/オフを管理

デザインシステム v3.0 - AEO Premium Dark Theme
"""

import streamlit as st
import os
from src.dashboard.styles.common import COLORS, get_icon


def init_demo_mode_state():
    """
    デモモードのsession_stateを初期化

    環境変数 DEMO_MODE の値を初期値として使用
    """
    if "demo_mode_enabled" not in st.session_state:
        # 環境変数から初期値を取得
        demo_mode_env = os.getenv("DEMO_MODE", "false").lower()
        st.session_state.demo_mode_enabled = demo_mode_env in ["true", "1", "yes", "on"]


def render_demo_toggle():
    """
    デモモードトグルを描画

    右上に固定配置されるトグルスイッチ
    状態変更時にページをリロード
    """
    # 状態を初期化
    init_demo_mode_state()

    # トグルスイッチのコンテナ（右上固定）- AEOダークテーマ対応
    st.markdown(f"""
    <style>
    /* デモトグルコンテナ（右上固定） - AEOダークテーマ */
    .demo-toggle-container {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: {COLORS['card']};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 10px 16px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 40px rgba(222, 255, 154, 0.05);
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid {COLORS['border']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .demo-toggle-container:hover {{
        border-color: {COLORS['border_accent']};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 40px rgba(222, 255, 154, 0.1);
    }}

    /* ラベル */
    .demo-toggle-label {{
        font-size: 0.8rem;
        font-weight: 500;
        color: {COLORS['text_secondary']};
        margin: 0;
        user-select: none;
    }}

    /* デモモード有効時のスタイル */
    .demo-toggle-container.active {{
        background: linear-gradient(135deg, rgba(222, 255, 154, 0.15) 0%, rgba(56, 189, 248, 0.1) 100%);
        border-color: rgba(222, 255, 154, 0.4);
    }}

    .demo-toggle-container.active .demo-toggle-label {{
        color: {COLORS['accent']};
    }}

    /* バッジ */
    .demo-badge {{
        background: {COLORS['warning']};
        color: {COLORS['text_inverse']};
        font-size: 0.65rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .demo-badge.live {{
        background: {COLORS['success']};
    }}

    /* Streamlitデフォルトスタイルの上書き */
    .demo-toggle-container .stCheckbox {{
        margin: 0 !important;
    }}

    .demo-toggle-container label {{
        margin: 0 !important;
    }}

    /* チェックボックスカスタマイズ */
    [data-testid="stCheckbox"] {{
        background: transparent !important;
    }}

    [data-testid="stCheckbox"] label span {{
        color: {COLORS['text_secondary']} !important;
        font-size: 0.8rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # トグルスイッチの描画（Streamlitのcolsを使って右寄せ）
    col1, col2 = st.columns([8, 2])

    with col2:
        # トグルの状態を表示するバッジ
        if st.session_state.demo_mode_enabled:
            badge_html = '<span class="demo-badge">DEMO</span>'
            container_class = "demo-toggle-container active"
            status_text = "デモデータを表示中"
        else:
            badge_html = '<span class="demo-badge live">LIVE</span>'
            container_class = "demo-toggle-container"
            status_text = "本番データを表示中"

        # トグルスイッチ
        new_state = st.checkbox(
            "デモモード",
            value=st.session_state.demo_mode_enabled,
            key="demo_mode_toggle",
            help="デモモードをオンにすると、サンプルデータを使用します"
        )

        # 状態が変更された場合
        if new_state != st.session_state.demo_mode_enabled:
            st.session_state.demo_mode_enabled = new_state
            # ページをリロードして変更を反映
            st.rerun()

    # バッジを表示（SVGアイコン付き）
    icon_name = "zap" if st.session_state.demo_mode_enabled else "activity"
    icon_color = COLORS['warning'] if st.session_state.demo_mode_enabled else COLORS['success']

    st.markdown(f"""
    <div class="{container_class}" style="position: fixed; top: 20px; right: 20px;">
        {badge_html}
        <span class="demo-toggle-label">
            {status_text}
        </span>
    </div>
    """, unsafe_allow_html=True)


def is_demo_mode_active() -> bool:
    """
    現在デモモードが有効かどうかを返す

    session_stateの値を優先的に使用
    session_stateが未初期化の場合は環境変数を参照

    Returns:
        デモモードが有効な場合 True
    """
    init_demo_mode_state()
    return st.session_state.get("demo_mode_enabled", False)

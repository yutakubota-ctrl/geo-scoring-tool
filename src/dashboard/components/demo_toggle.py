"""
デモモード切替トグル

全ページ共通の右上に配置されるトグルスイッチ
session_stateでデモモードのオン/オフを管理
"""

import streamlit as st
import os


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

    # トグルスイッチのコンテナ（右上固定）
    st.markdown("""
    <style>
    /* デモトグルコンテナ（右上固定） */
    .demo-toggle-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }

    /* ラベル */
    .demo-toggle-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
        user-select: none;
    }

    /* デモモード有効時のスタイル */
    .demo-toggle-container.active {
        background: linear-gradient(135deg, #deff9a 0%, #a7f3d0 100%);
        border-color: #10b981;
    }

    .demo-toggle-container.active .demo-toggle-label {
        color: #064e3b;
    }

    /* バッジ */
    .demo-badge {
        background: #f59e0b;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .demo-badge.live {
        background: #10b981;
    }

    /* Streamlitデフォルトスタイルの上書き */
    .demo-toggle-container .stCheckbox {
        margin: 0 !important;
    }

    .demo-toggle-container label {
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # トグルスイッチの描画（Streamlitのcolsを使って右寄せ）
    col1, col2 = st.columns([8, 2])

    with col2:
        # トグルの状態を表示するバッジ
        if st.session_state.demo_mode_enabled:
            badge_html = '<span class="demo-badge">DEMO</span>'
            container_class = "demo-toggle-container active"
        else:
            badge_html = '<span class="demo-badge live">LIVE</span>'
            container_class = "demo-toggle-container"

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

    # バッジを表示
    st.markdown(f"""
    <div class="{container_class}" style="position: fixed; top: 20px; right: 20px;">
        {badge_html}
        <span class="demo-toggle-label">
            {"デモデータを表示中" if st.session_state.demo_mode_enabled else "本番データを表示中"}
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

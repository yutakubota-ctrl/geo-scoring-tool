"""
思考ログ画面（Gem_01専用）

ChatGPT o1の7ステップ推論プロセスを可視化
- タイムライン形式での推論フロー
- 参照URL一覧
- ブランド評価カード

デザインシステム v3.0 - AEO Premium Dark Theme
"""
import streamlit as st
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.dashboard.styles.common import (
    get_common_css,
    get_page_header,
    get_page_footer,
    get_timeline_step,
    get_icon,
    COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle, is_demo_mode_active

st.set_page_config(page_title="思考ログ - GEOスコアリング", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# ページヘッダー
st.markdown(get_page_header(
    "思考ログ",
    "ChatGPT o1の7ステップ推論プロセスを可視化"
), unsafe_allow_html=True)

# デモモードの確認
demo_mode = is_demo_mode_active()

def load_thought_log_data():
    """思考ログデータを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "thought_log_sample.json"
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    else:
        return None

# データ読み込み
thought_log = load_thought_log_data()

if thought_log:
    # ================================
    # ヘッダー情報カード
    # ================================
    st.markdown(f"""
    <div style="
        background: {COLORS['card']};
        border: 1px solid {COLORS['border_accent']};
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            right: -50px;
            top: -50px;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(222, 255, 154, 0.08), transparent 70%);
        "></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; position: relative; z-index: 1;">
            <div style="flex: 1; min-width: 300px;">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <div style="color: {COLORS['accent']};">
                        {get_icon('activity', size=16, color=COLORS['accent'])}
                    </div>
                    <span style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: {COLORS['text_muted']};">
                        検索クエリ
                    </span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 600; color: {COLORS['text_primary']};">
                    {thought_log['query_text']}
                </div>
            </div>
            <div style="display: flex; gap: 2rem;">
                <div>
                    <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: {COLORS['text_muted']}; margin-bottom: 0.25rem;">
                        モデル
                    </div>
                    <div style="font-size: 1rem; font-weight: 500; color: {COLORS['text_primary']};">
                        {thought_log['llm_model']}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: {COLORS['text_muted']}; margin-bottom: 0.25rem;">
                        実行日時
                    </div>
                    <div style="font-size: 1rem; font-weight: 500; color: {COLORS['text_primary']};">
                        {datetime.fromisoformat(thought_log['executed_at']).strftime('%Y-%m-%d %H:%M')}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs(["7ステップ推論", "参照URL", "検索クエリ", "ブランド評価"])

    with tab1:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 2rem;
        ">
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {COLORS['accent']};">
                        {get_icon('brain', size=20, color=COLORS['accent'])}
                    </div>
                    <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">推論プロセスタイムライン</span>
                </div>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    AIが最終判断に至るまでの思考の流れを段階的に表示します
                </p>
            </div>
        """, unsafe_allow_html=True)

        thought_trace = thought_log.get('thought_trace', {})

        # タイムライン表示
        for i in range(1, 8):
            step_key = f"step_{i}"
            if step_key in thought_trace:
                step = thought_trace[step_key]
                is_last = (i == 7)

                # 信頼度の色を決定
                confidence = step.get('confidence', 0)
                if confidence >= 0.9:
                    conf_color = COLORS['success']
                elif confidence >= 0.8:
                    conf_color = COLORS['accent_secondary']
                elif confidence >= 0.7:
                    conf_color = COLORS['warning']
                else:
                    conf_color = COLORS['text_muted']

                # タイムラインのステップを表示
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin-bottom: {0 if is_last else '0.5rem'};">
                    <div style="display: flex; flex-direction: column; align-items: center; margin-right: 1.5rem;">
                        <div style="
                            width: 48px;
                            height: 48px;
                            border-radius: 50%;
                            background: {COLORS['gradient_accent']};
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: {COLORS['text_inverse']};
                            font-family: 'JetBrains Mono', monospace;
                            font-weight: 700;
                            font-size: 1.125rem;
                            flex-shrink: 0;
                        ">{i}</div>
                        {'<div style="width: 2px; height: 80px; background: linear-gradient(to bottom, ' + COLORS['accent'] + ', rgba(222, 255, 154, 0.2)); margin: 0.5rem 0;"></div>' if not is_last else ''}
                    </div>
                    <div style="
                        flex: 1;
                        background: {COLORS['card_elevated']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                        padding: 1.25rem;
                        margin-bottom: {'1rem' if not is_last else '0'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">
                                {step.get('title', 'タイトルなし')}
                            </div>
                            <div style="
                                background: rgba({int(conf_color[1:3], 16)}, {int(conf_color[3:5], 16)}, {int(conf_color[5:7], 16)}, 0.15);
                                color: {conf_color};
                                padding: 0.25rem 0.75rem;
                                border-radius: 9999px;
                                font-size: 0.75rem;
                                font-weight: 600;
                                font-family: 'JetBrains Mono', monospace;
                            ">
                                {confidence * 100:.0f}%
                            </div>
                        </div>
                        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; line-height: 1.6;">
                            {step.get('description', '')}
                        </div>
                """, unsafe_allow_html=True)

                # 参照URLがあれば表示
                if 'urls' in step and step['urls']:
                    st.markdown(f"""
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid {COLORS['border']};">
                            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; margin-bottom: 0.5rem;">参照した情報源:</div>
                    """, unsafe_allow_html=True)
                    for url in step['urls']:
                        st.markdown(f"""
                            <a href="{url}" target="_blank" style="
                                display: inline-block;
                                background: {COLORS['card']};
                                padding: 0.25rem 0.75rem;
                                border-radius: 6px;
                                font-size: 0.75rem;
                                color: {COLORS['accent_secondary']};
                                text-decoration: none;
                                margin-right: 0.5rem;
                                margin-bottom: 0.25rem;
                                border: 1px solid {COLORS['border']};
                            ">{url[:50]}...</a>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

        # 最終判断
        st.markdown(f"""
        <div style="
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 2px solid {COLORS['accent']};
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="color: {COLORS['accent']};">
                    {get_icon('check_circle', size=20, color=COLORS['accent'])}
                </div>
                <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">最終判断</span>
            </div>
            <div style="
                background: linear-gradient(135deg, rgba(222, 255, 154, 0.1) 0%, rgba(56, 189, 248, 0.1) 100%);
                border-left: 4px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 1rem 1.25rem;
            ">
                <div style="font-size: 0.9375rem; color: {COLORS['text_primary']}; line-height: 1.7;">
                    {thought_log.get('final_reasoning', '最終判断が記録されていません')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 2rem;
        ">
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {COLORS['accent_secondary']};">
                        {get_icon('layers', size=20, color=COLORS['accent_secondary'])}
                    </div>
                    <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">参照URL一覧</span>
                </div>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    AIが情報収集に使用したWebページの一覧です
                </p>
            </div>
        """, unsafe_allow_html=True)

        selected_urls = thought_log.get('selected_urls', [])

        if selected_urls:
            for idx, url in enumerate(selected_urls, 1):
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 1rem;
                    background: {COLORS['card_elevated']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    margin-bottom: 0.75rem;
                ">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 8px;
                        background: {COLORS['accent_secondary']};
                        color: {COLORS['text_inverse']};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                        font-size: 0.875rem;
                        margin-right: 1rem;
                        flex-shrink: 0;
                    ">{idx}</div>
                    <a href="{url}" target="_blank" style="
                        color: {COLORS['text_primary']};
                        text-decoration: none;
                        font-size: 0.9375rem;
                        word-break: break-all;
                    ">{url}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("参照URLが記録されていません")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 2rem;
        ">
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {COLORS['accent_tertiary']};">
                        {get_icon('activity', size=20, color=COLORS['accent_tertiary'])}
                    </div>
                    <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">検索クエリ候補</span>
                </div>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    AIが内部的に実行した検索クエリの一覧です
                </p>
            </div>
        """, unsafe_allow_html=True)

        search_queries = thought_log.get('search_queries_used', [])

        if search_queries:
            for idx, query in enumerate(search_queries, 1):
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 0.875rem 1rem;
                    background: {COLORS['card_elevated']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                ">
                    <div style="
                        width: 24px;
                        height: 24px;
                        border-radius: 6px;
                        background: {COLORS['card']};
                        color: {COLORS['text_primary']};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                        font-size: 0.75rem;
                        margin-right: 0.75rem;
                        flex-shrink: 0;
                        border: 1px solid {COLORS['border']};
                    ">{idx}</div>
                    <div style="font-size: 0.9375rem; color: {COLORS['text_primary']}; font-weight: 500;">
                        {query}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("検索クエリが記録されていません")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 2rem;
        ">
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="color: {COLORS['success']};">
                        {get_icon('chart', size=20, color=COLORS['success'])}
                    </div>
                    <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">ブランド言及状況</span>
                </div>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    各ブランドの推薦順位と理由を分析します
                </p>
            </div>
        """, unsafe_allow_html=True)

        brand_mentions = thought_log.get('brand_mentions', {})

        if brand_mentions:
            mentioned = []
            not_mentioned = []

            for brand_name, info in brand_mentions.items():
                if info.get('mentioned', False):
                    mentioned.append((brand_name, info))
                else:
                    not_mentioned.append((brand_name, info))

            mentioned.sort(key=lambda x: x[1].get('position', 999))

            # 言及されたブランド
            if mentioned:
                st.markdown(f"""
                <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                    推薦されたブランド
                </div>
                """, unsafe_allow_html=True)

                for brand_name, info in mentioned:
                    sentiment = info.get('sentiment', 'neutral')
                    position = info.get('position', '不明')
                    reasoning = info.get('reasoning', '理由が記録されていません')

                    # 感情による色設定
                    if sentiment == 'positive':
                        gradient = f"linear-gradient(135deg, {COLORS['success']} 0%, #86efac 100%)"
                        sentiment_label = "ポジティブ"
                    elif sentiment == 'negative':
                        gradient = f"linear-gradient(135deg, {COLORS['danger']} 0%, #fca5a5 100%)"
                        sentiment_label = "ネガティブ"
                    else:
                        gradient = f"linear-gradient(135deg, {COLORS['accent_secondary']} 0%, #7dd3fc 100%)"
                        sentiment_label = "中立"

                    st.markdown(f"""
                    <div style="
                        background: {gradient};
                        border-radius: 12px;
                        padding: 1.25rem;
                        margin-bottom: 0.75rem;
                        color: white;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="font-size: 1.125rem; font-weight: 600;">
                                <span style="
                                    background: rgba(255,255,255,0.2);
                                    padding: 0.25rem 0.5rem;
                                    border-radius: 6px;
                                    font-size: 0.875rem;
                                    margin-right: 0.5rem;
                                ">{position}位</span>
                                {brand_name}
                            </div>
                            <div style="
                                background: rgba(255,255,255,0.2);
                                padding: 0.25rem 0.75rem;
                                border-radius: 9999px;
                                font-size: 0.75rem;
                            ">{sentiment_label}</div>
                        </div>
                        <div style="font-size: 0.875rem; opacity: 0.95; line-height: 1.5;">
                            {reasoning}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 言及されなかったブランド
            if not_mentioned:
                st.markdown(f"""
                <div style="
                    margin-top: 2rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid {COLORS['border']};
                ">
                    <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                        推薦されなかったブランド
                    </div>
                """, unsafe_allow_html=True)

                for brand_name, info in not_mentioned:
                    reasoning = info.get('reasoning', '理由が記録されていません')

                    st.markdown(f"""
                    <div style="
                        background: {COLORS['card_elevated']};
                        border-left: 4px solid {COLORS['warning']};
                        border-radius: 8px;
                        padding: 1rem 1.25rem;
                        margin-bottom: 0.75rem;
                    ">
                        <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.25rem;">
                            {brand_name}
                        </div>
                        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">
                            {reasoning}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("ブランド言及データが記録されていません")

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
    ">
        <div style="
            width: 80px;
            height: 80px;
            background: {COLORS['card_elevated']};
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
        ">
            {get_icon('brain', size=40, color=COLORS['text_muted'])}
        </div>
        <div style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            思考ログデータが見つかりません
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">
            デモモードを有効化するか、データを取得してください
        </div>
        <div style="
            background: {COLORS['card_elevated']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 1rem;
            display: inline-block;
        ">
            <code style="color: {COLORS['accent']};">DEMO_MODE=true</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

# フッター
st.markdown(get_page_footer(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), unsafe_allow_html=True)

"""
思考ログ画面（Gem_01専用）

ChatGPT o1の7ステップ推論プロセスを可視化
- タイムライン形式での推論フロー
- 参照URL一覧
- ブランド評価カード

デザインシステム v2.1適用
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
    COLORS
)

st.set_page_config(page_title="思考ログ - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# ページヘッダー
st.markdown(get_page_header(
    "思考ログ",
    "ChatGPT o1の7ステップ推論プロセスを可視化"
), unsafe_allow_html=True)

# デモモードの確認
demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

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
        background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 300px;">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.7; margin-bottom: 0.5rem;">
                    検索クエリ
                </div>
                <div style="font-size: 1.5rem; font-weight: 600;">
                    {thought_log['query_text']}
                </div>
            </div>
            <div style="display: flex; gap: 2rem;">
                <div>
                    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.7; margin-bottom: 0.25rem;">
                        モデル
                    </div>
                    <div style="font-size: 1rem; font-weight: 500;">
                        {thought_log['llm_model']}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.7; margin-bottom: 0.25rem;">
                        実行日時
                    </div>
                    <div style="font-size: 1rem; font-weight: 500;">
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
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 1.5rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">推論プロセスタイムライン</span>
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
                    conf_color = COLORS['accent']
                elif confidence >= 0.8:
                    conf_color = COLORS['secondary']
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
                            background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%);
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-family: 'JetBrains Mono', monospace;
                            font-weight: 700;
                            font-size: 1.125rem;
                            flex-shrink: 0;
                        ">{i}</div>
                        {'<div style="width: 2px; height: 80px; background: linear-gradient(to bottom, ' + COLORS['secondary'] + ', rgba(59, 130, 246, 0.2)); margin: 0.5rem 0;"></div>' if not is_last else ''}
                    </div>
                    <div style="
                        flex: 1;
                        background: {COLORS['bg_primary']};
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
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.05);">
                            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; margin-bottom: 0.5rem;">参照した情報源:</div>
                    """, unsafe_allow_html=True)
                    for url in step['urls']:
                        st.markdown(f"""
                            <a href="{url}" target="_blank" style="
                                display: inline-block;
                                background: white;
                                padding: 0.25rem 0.75rem;
                                border-radius: 6px;
                                font-size: 0.75rem;
                                color: {COLORS['secondary']};
                                text-decoration: none;
                                margin-right: 0.5rem;
                                margin-bottom: 0.25rem;
                                border: 1px solid rgba(59, 130, 246, 0.2);
                            ">{url[:50]}...</a>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

        # 最終判断
        st.markdown(f"""
        <div style="
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 2px solid {COLORS['secondary']};
        ">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                最終判断
            </div>
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
                border-left: 4px solid {COLORS['secondary']};
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
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 1.5rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">参照URL一覧</span>
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
                    background: {COLORS['bg_primary']};
                    border-radius: 8px;
                    margin-bottom: 0.75rem;
                ">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 8px;
                        background: {COLORS['secondary']};
                        color: white;
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
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 1.5rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">検索クエリ候補</span>
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
                    background: {COLORS['bg_primary']};
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                ">
                    <div style="
                        width: 24px;
                        height: 24px;
                        border-radius: 6px;
                        background: {COLORS['primary']};
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 600;
                        font-size: 0.75rem;
                        margin-right: 0.75rem;
                        flex-shrink: 0;
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
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 1.5rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">ブランド言及状況</span>
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
                        gradient = f"linear-gradient(135deg, {COLORS['accent']} 0%, #34D399 100%)"
                        sentiment_label = "ポジティブ"
                    elif sentiment == 'negative':
                        gradient = f"linear-gradient(135deg, {COLORS['danger']} 0%, #F87171 100%)"
                        sentiment_label = "ネガティブ"
                    else:
                        gradient = f"linear-gradient(135deg, {COLORS['secondary']} 0%, #60A5FA 100%)"
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
                    border-top: 1px solid rgba(0,0,0,0.05);
                ">
                    <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                        推薦されなかったブランド
                    </div>
                """, unsafe_allow_html=True)

                for brand_name, info in not_mentioned:
                    reasoning = info.get('reasoning', '理由が記録されていません')

                    st.markdown(f"""
                    <div style="
                        background: {COLORS['bg_primary']};
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
        background: white;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🧠</div>
        <div style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            思考ログデータが見つかりません
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">
            デモモードを有効化するか、データを取得してください
        </div>
        <div style="
            background: {COLORS['bg_primary']};
            border-radius: 8px;
            padding: 1rem;
            display: inline-block;
        ">
            <code style="color: {COLORS['secondary']};">DEMO_MODE=true</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

# フッター
st.markdown(get_page_footer(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), unsafe_allow_html=True)

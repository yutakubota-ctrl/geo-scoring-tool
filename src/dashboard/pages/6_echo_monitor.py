"""
エコー監視画面（Gem_05専用）

AI Overviewsでのメンション状況をリアルタイム追跡
- メンション数推移
- センチメントスコア
- 参照順位の変化
- 最新引用一覧

デザインシステム v2.1適用
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.dashboard.styles.common import (
    get_common_css,
    get_page_header,
    get_page_footer,
    get_plotly_layout,
    COLORS,
    PLOTLY_COLORS
)

st.set_page_config(page_title="エコー監視 - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# ページヘッダー
st.markdown(get_page_header(
    "エコー監視",
    "AI Overviewsでのブランドメンション状況をリアルタイム追跡"
), unsafe_allow_html=True)

# デモモードの確認
demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

def load_echo_monitor_data():
    """エコー監視データを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "echo_monitor_sample.json"
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    else:
        return None

# データ読み込み
echo_data = load_echo_monitor_data()

if echo_data:
    current_status = echo_data.get('current_status', {})
    timeline_data = echo_data.get('timeline_data', [])
    recent_citations = echo_data.get('recent_citations', [])

    # ================================
    # エコーステータスバナー
    # ================================
    echo_success = current_status.get('echo_success', '失敗')

    if echo_success == '成功':
        status_gradient = f"linear-gradient(135deg, {COLORS['accent']} 0%, #34D399 100%)"
        status_icon = "check_circle"
    elif echo_success == '部分成功':
        status_gradient = f"linear-gradient(135deg, {COLORS['warning']} 0%, #FBBF24 100%)"
        status_icon = "info"
    else:
        status_gradient = f"linear-gradient(135deg, {COLORS['danger']} 0%, #F87171 100%)"
        status_icon = "error"

    st.markdown(f"""
    <div style="
        background: {status_gradient};
        border-radius: 16px;
        padding: 1.25rem 2rem;
        margin-bottom: 1.5rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2rem;">{'✅' if echo_success == '成功' else '⚡' if echo_success == '部分成功' else '❌'}</div>
            <div>
                <div style="font-size: 0.875rem; opacity: 0.9;">エコーステータス</div>
                <div style="font-size: 1.5rem; font-weight: 700;">{echo_success}</div>
            </div>
        </div>
        <div style="font-size: 0.875rem; opacity: 0.9;">
            最終チェック: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ================================
    # サマリーメトリクス
    # ================================
    col1, col2, col3, col4 = st.columns(4)

    mention_count = current_status.get('mention_count', 0)
    sentiment_score = current_status.get('sentiment_score', 0)
    reference_rank = current_status.get('reference_rank', '圏外')
    llm_coverage = current_status.get('llm_coverage', {})
    active_llms = sum(1 for v in llm_coverage.values() if v)

    with col1:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        ">
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">メンション数</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['secondary']}; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {mention_count}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">過去7日間</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # センチメントの色を決定
        if sentiment_score >= 0.5:
            sent_color = COLORS['accent']
        elif sentiment_score >= 0:
            sent_color = COLORS['warning']
        else:
            sent_color = COLORS['danger']

        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        ">
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">センチメント</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {sent_color}; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {sentiment_score:.2f}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">-1.0 ~ 1.0</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # 参照順位の色
        if isinstance(reference_rank, int) and reference_rank <= 3:
            rank_color = COLORS['accent']
        elif isinstance(reference_rank, int) and reference_rank <= 5:
            rank_color = COLORS['warning']
        else:
            rank_color = COLORS['text_secondary']

        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        ">
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">参照順位</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {rank_color}; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {reference_rank}<span style="font-size: 1rem; opacity: 0.7;">位</span>
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">平均順位</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        ">
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">LLMカバレッジ</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['primary']}; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {active_llms}<span style="font-size: 1rem; opacity: 0.7;">/4</span>
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">引用ありLLM</div>
        </div>
        """, unsafe_allow_html=True)

    # ================================
    # LLMカバレッジ詳細
    # ================================
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    ">
        <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
            LLM別カバレッジ
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
    """, unsafe_allow_html=True)

    llm_icons = {'ChatGPT': '🤖', 'Gemini': '✨', 'Claude': '🧠', 'Perplexity': '🔍'}

    for llm_name, is_active in llm_coverage.items():
        bg_color = COLORS['accent'] if is_active else COLORS['bg_primary']
        text_color = 'white' if is_active else COLORS['text_secondary']
        status_text = "引用あり" if is_active else "引用なし"
        icon = llm_icons.get(llm_name, '🤖')

        st.markdown(f"""
        <div style="
            background: {bg_color if is_active else COLORS['bg_primary']};
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            {'border: 2px solid ' + COLORS['accent'] if is_active else 'border: 1px solid rgba(0,0,0,0.05)'};
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 0.9375rem; font-weight: 600; color: {text_color if is_active else COLORS['text_primary']};">
                {llm_name}
            </div>
            <div style="
                font-size: 0.75rem;
                color: {text_color if is_active else COLORS['text_muted']};
                margin-top: 0.25rem;
            ">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs(["メンション推移", "センチメント分析", "最新引用", "統計サマリー"])

    with tab1:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">メンション数推移</span>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    過去4週間のAI Overviewsでのメンション数をトラッキング
                </p>
            </div>
        """, unsafe_allow_html=True)

        df_timeline = pd.DataFrame(timeline_data)
        df_timeline['date'] = pd.to_datetime(df_timeline['date'])

        fig_timeline = go.Figure()

        fig_timeline.add_trace(go.Scatter(
            x=df_timeline['date'],
            y=df_timeline['mention_count'],
            mode='lines+markers',
            name='メンション数',
            line=dict(color=COLORS['secondary'], width=3),
            marker=dict(size=10, color=COLORS['secondary']),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>メンション数: %{y}<extra></extra>'
        ))

        layout_timeline = get_plotly_layout("", height=350)
        layout_timeline.update({
            "xaxis_title": "日付",
            "yaxis_title": "メンション数",
            "margin": dict(l=50, r=20, t=20, b=50),
        })
        fig_timeline.update_layout(**layout_timeline)

        st.plotly_chart(fig_timeline, use_container_width=True)

        # 参照順位推移
        st.markdown(f"""
        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(0,0,0,0.05);">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                参照順位推移
            </div>
        </div>
        """, unsafe_allow_html=True)

        # nullを除外
        df_rank = df_timeline[df_timeline['reference_rank'].notna()]

        fig_rank = go.Figure()

        fig_rank.add_trace(go.Scatter(
            x=df_rank['date'],
            y=df_rank['reference_rank'],
            mode='lines+markers',
            name='参照順位',
            line=dict(color=COLORS['warning'], width=3),
            marker=dict(size=10, color=COLORS['warning']),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>順位: %{y}位<extra></extra>'
        ))

        layout_rank = get_plotly_layout("", height=300)
        layout_rank.update({
            "xaxis_title": "日付",
            "yaxis_title": "参照順位",
            "yaxis": dict(autorange='reversed', gridcolor='rgba(0,0,0,0.05)'),
            "margin": dict(l=50, r=20, t=20, b=50),
        })
        fig_rank.update_layout(**layout_rank)

        st.plotly_chart(fig_rank, use_container_width=True)

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
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">センチメント分析</span>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    AIによる言及のポジティブ度を分析
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ゲージチャート
        sentiment_percentage = (sentiment_score + 1) * 50  # -1~1を0~100に変換

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 48, 'color': COLORS['text_primary'], 'family': 'JetBrains Mono'}, 'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLORS['text_muted']},
                'bar': {'color': COLORS['secondary'], 'thickness': 0.3},
                'bgcolor': COLORS['bg_primary'],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 33], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [33, 67], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [67, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                ],
            }
        ))

        fig_gauge.update_layout(
            height=300,
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

        # センチメント推移
        st.markdown(f"""
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(0,0,0,0.05);">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                センチメント推移
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_sent = df_timeline[df_timeline['sentiment_score'].notna()]

        fig_sentiment = go.Figure()

        fig_sentiment.add_trace(go.Scatter(
            x=df_sent['date'],
            y=df_sent['sentiment_score'],
            mode='lines+markers',
            name='センチメント',
            line=dict(color=COLORS['accent'], width=3),
            marker=dict(size=10, color=COLORS['accent']),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>スコア: %{y:.2f}<extra></extra>'
        ))

        # 基準線
        fig_sentiment.add_hline(y=0, line_dash="dash", line_color=COLORS['text_muted'], line_width=1)

        layout_sentiment = get_plotly_layout("", height=300)
        layout_sentiment.update({
            "xaxis_title": "日付",
            "yaxis_title": "センチメントスコア",
            "yaxis_range": [-1, 1],
            "margin": dict(l=50, r=20, t=20, b=50),
        })
        fig_sentiment.update_layout(**layout_sentiment)

        st.plotly_chart(fig_sentiment, use_container_width=True)

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
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">最新引用一覧</span>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    直近の引用状況とコンテキストを確認
                </p>
            </div>
        """, unsafe_allow_html=True)

        if recent_citations:
            for citation in recent_citations:
                query_text = citation.get('query_text', '')
                sentiment_score = citation.get('sentiment_score', 0)
                reference_type = citation.get('reference_type', '')
                reference_rank = citation.get('reference_rank', '不明')
                context_snippet = citation.get('context_snippet', '')
                source_url = citation.get('source_url', '')
                created_at = citation.get('created_at', '')

                # センチメント判定
                if sentiment_score >= 0.5:
                    sent_color = COLORS['accent']
                    sent_label = "ポジティブ"
                elif sentiment_score >= 0:
                    sent_color = COLORS['warning']
                    sent_label = "中立"
                else:
                    sent_color = COLORS['danger']
                    sent_label = "ネガティブ"

                created_datetime = datetime.fromisoformat(created_at)

                st.markdown(f"""
                <div style="
                    background: {COLORS['bg_primary']};
                    border-radius: 12px;
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid {COLORS['secondary']};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']};">
                            {query_text}
                        </div>
                        <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">
                            {created_datetime.strftime('%Y-%m-%d %H:%M')}
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap;">
                        <span style="
                            background: {COLORS['secondary']};
                            color: white;
                            padding: 0.2rem 0.6rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        ">{reference_type}</span>
                        <span style="
                            background: white;
                            color: {COLORS['text_secondary']};
                            padding: 0.2rem 0.6rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            border: 1px solid rgba(0,0,0,0.1);
                        ">順位: {reference_rank}位</span>
                        <span style="
                            background: rgba({int(sent_color[1:3], 16)}, {int(sent_color[3:5], 16)}, {int(sent_color[5:7], 16)}, 0.15);
                            color: {sent_color};
                            padding: 0.2rem 0.6rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        ">{sent_label} ({sentiment_score:.2f})</span>
                    </div>
                    <div style="
                        background: white;
                        border-radius: 8px;
                        padding: 0.75rem 1rem;
                        font-size: 0.875rem;
                        color: {COLORS['text_primary']};
                        font-style: italic;
                        line-height: 1.6;
                        border-left: 3px solid {COLORS['secondary']};
                    ">
                        "{context_snippet}"
                    </div>
                    <div style="margin-top: 0.75rem; font-size: 0.8125rem;">
                        <span style="color: {COLORS['text_muted']};">参照元: </span>
                        <a href="{source_url}" target="_blank" style="color: {COLORS['secondary']}; text-decoration: none;">
                            {source_url}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("引用データがまだありません。")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        col_stat1, col_stat2 = st.columns(2)

        with col_stat1:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                    センチメント分布
                </div>
            """, unsafe_allow_html=True)

            sentiment_dist = echo_data.get('sentiment_distribution', {})

            fig_sent_dist = go.Figure(data=[
                go.Pie(
                    labels=['ポジティブ', '中立', 'ネガティブ'],
                    values=[
                        sentiment_dist.get('positive', 0),
                        sentiment_dist.get('neutral', 0),
                        sentiment_dist.get('negative', 0)
                    ],
                    marker=dict(colors=[COLORS['accent'], COLORS['warning'], COLORS['danger']]),
                    textinfo='label+percent',
                    textfont=dict(size=12),
                    hole=0.4,
                    hovertemplate='<b>%{label}</b><br>件数: %{value}<br>割合: %{percent}<extra></extra>'
                )
            ])

            layout_sent_dist = get_plotly_layout("", height=280)
            layout_sent_dist.update({
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": False
            })
            fig_sent_dist.update_layout(**layout_sent_dist)

            st.plotly_chart(fig_sent_dist, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_stat2:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                    参照順位分布
                </div>
            """, unsafe_allow_html=True)

            rank_dist = echo_data.get('reference_rank_distribution', {})

            fig_rank_dist = go.Figure(data=[
                go.Bar(
                    x=['Top 3', 'Top 5', 'Top 10'],
                    y=[rank_dist.get('top_3', 0), rank_dist.get('top_5', 0), rank_dist.get('top_10', 0)],
                    marker=dict(
                        color=[COLORS['accent'], COLORS['warning'], COLORS['secondary']],
                        cornerradius=8
                    ),
                    text=[rank_dist.get('top_3', 0), rank_dist.get('top_5', 0), rank_dist.get('top_10', 0)],
                    textposition='outside',
                    textfont=dict(size=14, color=COLORS['text_primary'], family="JetBrains Mono")
                )
            ])

            layout_rank_dist = get_plotly_layout("", height=280)
            layout_rank_dist.update({
                "yaxis_title": "引用件数",
                "margin": dict(l=50, r=20, t=20, b=40),
            })
            fig_rank_dist.update_layout(**layout_rank_dist)

            st.plotly_chart(fig_rank_dist, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # 成功基準
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                エコー成功の定義
            </div>
        """, unsafe_allow_html=True)

        success_criteria = [
            ("配信から72時間以内に3つ以上のLLMで引用される", active_llms >= 3),
            ("センチメントスコアが0.5以上", sentiment_score >= 0.5),
            ("参照順位がトップ5以内", reference_rank <= 5 if isinstance(reference_rank, int) else False)
        ]

        for criteria, met in success_criteria:
            icon = "✅" if met else "⚠"
            bg_color = f"rgba(16, 185, 129, 0.1)" if met else f"rgba(245, 158, 11, 0.1)"
            text_color = COLORS['accent'] if met else COLORS['warning']

            st.markdown(f"""
            <div style="
                background: {bg_color};
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            ">
                <span style="font-size: 1.25rem;">{icon}</span>
                <span style="font-size: 0.9375rem; color: {COLORS['text_primary']};">{criteria}</span>
            </div>
            """, unsafe_allow_html=True)

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
        <div style="font-size: 4rem; margin-bottom: 1rem;">👁</div>
        <div style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            エコー監視データが見つかりません
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

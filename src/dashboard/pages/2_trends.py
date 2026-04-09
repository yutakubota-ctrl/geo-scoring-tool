"""
トレンド・競合比較画面（マーケター向け）
時系列分析と競合比較を表示

デザインシステム v2.1適用
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.database.repository import BrandRepository, ScoreRepository
from src.dashboard.styles.common import (
    get_common_css,
    get_page_header,
    get_page_footer,
    get_plotly_layout,
    COLORS,
    PLOTLY_COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle

st.set_page_config(page_title="トレンド分析 - GEOスコアリング", layout="wide")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# ページヘッダー
st.markdown(get_page_header(
    "トレンド・競合分析",
    "マーケター向けの詳細分析 - 時系列推移、レーダーチャート、競合比較"
), unsafe_allow_html=True)

# ================================
# フィルターセクション
# ================================
st.markdown(f"""
<div style="
    background: white;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
">
    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: {COLORS['text_muted']}; margin-bottom: 0.75rem;">
        フィルター設定
    </div>
</div>
""", unsafe_allow_html=True)

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    period = st.selectbox(
        "分析期間",
        options=[30, 60, 90, 180],
        format_func=lambda x: f"過去{x}日",
        index=2
    )

with col_filter2:
    with db.get_session() as session:
        all_brands = BrandRepository.get_all(session)
        brand_options = {b.name: b.id for b in all_brands}

    selected_brands = st.multiselect(
        "比較ブランド",
        options=list(brand_options.keys()),
        default=list(brand_options.keys())[:4]
    )

# ================================
# メインコンテンツ
# ================================
with db.get_session() as session:
    if selected_brands:
        brand_ids = [brand_options[name] for name in selected_brands]

        # レーダーチャート用データ
        radar_data = []
        for brand_name in selected_brands:
            brand_id = brand_options[brand_name]
            avg = ScoreRepository.get_average_scores(session, brand_id, days=period)

            radar_data.append({
                "ブランド": brand_name,
                "認知": (avg['visibility'] / 10) * 100,
                "推奨度": ((avg['sentiment'] + 10) / 40) * 100,
                "ポジション": (avg['positioning'] / 20) * 100,
                "正確性": (avg['accuracy'] / 40) * 100
            })

        # 2カラムレイアウト: レーダーチャート & 達成率
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                    4指標レーダーチャート
                </div>
                <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1rem;">
                    各指標の達成率を100%基準で比較
                </div>
            """, unsafe_allow_html=True)

            categories = ["認知", "推奨度", "ポジション", "正確性"]

            fig_radar = go.Figure()

            for i, item in enumerate(radar_data):
                fig_radar.add_trace(go.Scatterpolar(
                    r=[item["認知"], item["推奨度"], item["ポジション"], item["正確性"], item["認知"]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=item["ブランド"],
                    line=dict(color=PLOTLY_COLORS[i % len(PLOTLY_COLORS)], width=2),
                    fillcolor=f"rgba({int(PLOTLY_COLORS[i % len(PLOTLY_COLORS)][1:3], 16)}, {int(PLOTLY_COLORS[i % len(PLOTLY_COLORS)][3:5], 16)}, {int(PLOTLY_COLORS[i % len(PLOTLY_COLORS)][5:7], 16)}, 0.15)"
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10, color=COLORS['text_muted']),
                        gridcolor='rgba(0,0,0,0.05)'
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12, color=COLORS['text_primary']),
                        gridcolor='rgba(0,0,0,0.05)'
                    ),
                    bgcolor='rgba(0,0,0,0)'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11)
                ),
                height=400,
                margin=dict(l=60, r=60, t=40, b=60),
                paper_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig_radar, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_chart2:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                    指標別達成率（自社）
                </div>
                <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1rem;">
                    各指標の目標達成度を棒グラフで表示
                </div>
            """, unsafe_allow_html=True)

            own_brand = BrandRepository.get_own_brand(session)
            if own_brand:
                avg = ScoreRepository.get_average_scores(session, own_brand.id, days=period)

                metrics = {
                    "認知": (avg['visibility'] / 10) * 100,
                    "推奨度": ((avg['sentiment'] + 10) / 40) * 100,
                    "ポジション": (avg['positioning'] / 20) * 100,
                    "正確性": (avg['accuracy'] / 40) * 100
                }

                # 色を指標ごとに設定
                bar_colors = [COLORS['secondary'], COLORS['accent'], COLORS['warning'], '#8B5CF6']

                fig_bar = go.Figure()

                fig_bar.add_trace(go.Bar(
                    x=list(metrics.keys()),
                    y=list(metrics.values()),
                    marker=dict(
                        color=bar_colors,
                        cornerradius=8
                    ),
                    text=[f"{v:.0f}%" for v in metrics.values()],
                    textposition='outside',
                    textfont=dict(size=14, color=COLORS['text_primary'], family="JetBrains Mono"),
                    hovertemplate='<b>%{x}</b><br>達成率: %{y:.1f}%<extra></extra>'
                ))

                layout_bar = get_plotly_layout("", height=350)
                layout_bar.update({
                    "yaxis_range": [0, 120],
                    "margin": {"l": 40, "r": 20, "t": 20, "b": 40},
                    "xaxis_title": "",
                    "yaxis_title": "達成率 (%)",
                })
                fig_bar.update_layout(**layout_bar)

                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ================================
        # 競合比較表
        # ================================
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        ">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                競合比較表
            </div>
        """, unsafe_allow_html=True)

        comparison_df = pd.DataFrame(radar_data)
        comparison_df = comparison_df.set_index("ブランド")

        # カスタムスタイリング
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: rgba(16, 185, 129, 0.2); font-weight: 600;' if v else '' for v in is_max]

        styled_df = comparison_df.style.format("{:.1f}%").apply(highlight_max)

        st.dataframe(
            styled_df,
            use_container_width=True,
            height=200
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # ================================
        # 時系列比較グラフ
        # ================================
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                スコア推移比較
            </div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1rem;">
                選択したブランドの総合スコアを時系列で比較
            </div>
        """, unsafe_allow_html=True)

        # 全ブランドのトレンドデータを取得
        all_trend_data = []
        for brand_name in selected_brands:
            brand_id = brand_options[brand_name]
            trend = ScoreRepository.get_score_trend(session, brand_id, days=period)
            for item in trend:
                item["ブランド"] = brand_name
                all_trend_data.append(item)

        if all_trend_data:
            trend_df = pd.DataFrame(all_trend_data)

            fig_trend = go.Figure()

            for i, brand_name in enumerate(selected_brands):
                brand_df = trend_df[trend_df["ブランド"] == brand_name]
                fig_trend.add_trace(go.Scatter(
                    x=brand_df["date"],
                    y=brand_df["total"],
                    mode='lines+markers',
                    name=brand_name,
                    line=dict(color=PLOTLY_COLORS[i % len(PLOTLY_COLORS)], width=2),
                    marker=dict(size=6),
                    hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<extra></extra>'
                ))

            layout_trend = get_plotly_layout("", height=400)
            layout_trend.update({
                "yaxis_range": [0, 100],
                "margin": {"l": 50, "r": 20, "t": 20, "b": 50},
                "xaxis_title": "日付",
                "yaxis_title": "総合スコア",
                "legend": dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            })
            fig_trend.update_layout(**layout_trend)

            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("スコアデータがありません。バッチ処理を実行してください。")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("比較するブランドを選択してください。")

# フッター
st.markdown(get_page_footer(f"分析期間: 過去{period}日間"), unsafe_allow_html=True)

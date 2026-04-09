"""
サマリー画面（経営向け）
総合スコア、前回比較、アラートを表示

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
    get_kpi_card,
    get_section_divider,
    get_page_footer,
    get_plotly_layout,
    COLORS,
    PLOTLY_COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle

st.set_page_config(page_title="サマリー - GEOスコアリング", layout="wide")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# ページヘッダー
st.markdown(get_page_header(
    "サマリー",
    "経営層向けの概要ダッシュボード - 総合スコア、競合比較、アラート"
), unsafe_allow_html=True)

# データ取得
with db.get_session() as session:
    own_brand = BrandRepository.get_own_brand(session)
    competitors = BrandRepository.get_competitors(session)

    if own_brand:
        # 自社の最新スコアと平均
        latest_score = ScoreRepository.get_latest_by_brand(session, own_brand.id)
        avg_scores = ScoreRepository.get_average_scores(session, own_brand.id, days=30)

        # ================================
        # KPIカード セクション
        # ================================
        st.markdown("""
        <div style="margin-bottom: 0.5rem;">
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #64748B;">
                主要指標
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        current_total = latest_score.total_score if latest_score else 0
        visibility_rate = (avg_scores['visibility'] / 10) * 100
        sentiment_value = avg_scores['sentiment']

        with col1:
            # 総合スコア（メインカード）
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%);
                border-radius: 16px;
                padding: 1.5rem;
                color: white;
                position: relative;
                overflow: hidden;
            ">
                <div style="position: relative; z-index: 1;">
                    <div style="font-size: 0.875rem; opacity: 0.8; margin-bottom: 0.25rem;">総合スコア</div>
                    <div style="font-size: 3rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                        {current_total}<span style="font-size: 1.5rem; opacity: 0.7;">/100</span>
                    </div>
                    <div style="font-size: 0.875rem; margin-top: 0.5rem;">
                        <span style="
                            background: rgba(16, 185, 129, 0.3);
                            padding: 0.2rem 0.5rem;
                            border-radius: 4px;
                        ">+5pt vs 先週</span>
                    </div>
                </div>
                <div style="
                    position: absolute;
                    right: -20px;
                    top: -20px;
                    width: 100px;
                    height: 100px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 50%;
                "></div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 認知率
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 0.25rem;">認知率</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['secondary']}; font-family: 'JetBrains Mono', monospace;">
                    {visibility_rate:.0f}%
                </div>
                <div style="margin-top: 0.75rem;">
                    <div style="height: 8px; background: {COLORS['bg_primary']}; border-radius: 4px; overflow: hidden;">
                        <div style="height: 100%; width: {visibility_rate}%; background: linear-gradient(90deg, {COLORS['secondary']}, #60A5FA); border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # 推奨度
            sentiment_color = COLORS['accent'] if sentiment_value >= 0 else COLORS['danger']
            sentiment_sign = "+" if sentiment_value >= 0 else ""
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 0.25rem;">推奨度</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {sentiment_color}; font-family: 'JetBrains Mono', monospace;">
                    {sentiment_sign}{sentiment_value:.0f}pt
                </div>
                <div style="font-size: 0.875rem; color: {COLORS['text_muted']}; margin-top: 0.5rem;">
                    範囲: -10 ~ +30
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # 30日平均
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 0.25rem;">30日平均</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {COLORS['text_primary']}; font-family: 'JetBrains Mono', monospace;">
                    {avg_scores['total']:.1f}
                </div>
                <div style="font-size: 0.875rem; color: {COLORS['accent']}; margin-top: 0.5rem;">
                    ↗ 安定上昇中
                </div>
            </div>
            """, unsafe_allow_html=True)

        # セクションディバイダー
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

        # ================================
        # スコア推移グラフ
        # ================================
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        ">
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">スコア推移</span>
                <span style="font-size: 0.875rem; color: {COLORS['text_muted']}; margin-left: 0.5rem;">過去90日</span>
            </div>
        """, unsafe_allow_html=True)

        # トレンドデータ取得
        trend_data = ScoreRepository.get_score_trend(session, own_brand.id, days=90)

        if trend_data:
            df = pd.DataFrame(trend_data)

            fig = go.Figure()

            # エリアチャート
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["total"],
                mode='lines',
                name='総合スコア',
                line=dict(color=COLORS['secondary'], width=3),
                fill='tozeroy',
                fillcolor=f"rgba(59, 130, 246, 0.1)",
                hovertemplate='<b>%{x}</b><br>スコア: %{y:.1f}<extra></extra>'
            ))

            # レイアウト設定
            layout = get_plotly_layout("", height=350)
            layout.update({
                "xaxis_title": "",
                "yaxis_title": "スコア",
                "yaxis_range": [0, 100],
                "margin": {"l": 40, "r": 20, "t": 20, "b": 40},
            })
            fig.update_layout(**layout)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("まだスコアデータがありません。バッチ処理を実行してください。")

        st.markdown("</div>", unsafe_allow_html=True)

        # ================================
        # 競合比較 & アラート
        # ================================
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="margin-bottom: 1rem;">
                    <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">競合ランキング</span>
                </div>
            """, unsafe_allow_html=True)

            # 競合データ取得
            all_brands = [own_brand] + competitors
            ranking_data = []

            for brand in all_brands:
                avg = ScoreRepository.get_average_scores(session, brand.id, days=30)
                ranking_data.append({
                    "brand": brand.name,
                    "score": avg['total'],
                    "is_own": brand.is_own
                })

            ranking_data.sort(key=lambda x: x['score'], reverse=True)

            # 横棒グラフで表示
            fig_ranking = go.Figure()

            colors = [COLORS['secondary'] if d['is_own'] else '#CBD5E1' for d in ranking_data]
            labels = [f"{'★ ' if d['is_own'] else ''}{d['brand']}" for d in ranking_data]

            fig_ranking.add_trace(go.Bar(
                y=labels[::-1],
                x=[d['score'] for d in ranking_data][::-1],
                orientation='h',
                marker=dict(
                    color=colors[::-1],
                    cornerradius=8
                ),
                text=[f"{d['score']:.1f}" for d in ranking_data][::-1],
                textposition='inside',
                textfont=dict(color='white', size=14, family="JetBrains Mono"),
                hovertemplate='<b>%{y}</b><br>スコア: %{x:.1f}<extra></extra>'
            ))

            layout_ranking = get_plotly_layout("", height=250)
            layout_ranking.update({
                "xaxis_range": [0, 100],
                "margin": {"l": 120, "r": 20, "t": 10, "b": 30},
                "xaxis_title": "スコア",
                "yaxis_title": "",
            })
            fig_ranking.update_layout(**layout_ranking)

            st.plotly_chart(fig_ranking, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="margin-bottom: 1rem;">
                    <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">アラート</span>
                </div>
            """, unsafe_allow_html=True)

            # アラート条件をチェック
            alerts = []

            if avg_scores['visibility'] < 5:
                alerts.append(("danger", "認知率が50%を下回っています", "認知率向上施策を検討してください"))

            if avg_scores['sentiment'] < 0:
                alerts.append(("warning", "推奨度がマイナスです", "ネガティブな言及を分析してください"))

            if avg_scores['accuracy'] < 20:
                alerts.append(("warning", "情報正確性が低下しています", "公式情報の更新を推奨します"))

            if alerts:
                for alert_type, title, description in alerts:
                    bg_color = "rgba(239, 68, 68, 0.1)" if alert_type == "danger" else "rgba(245, 158, 11, 0.1)"
                    border_color = COLORS['danger'] if alert_type == "danger" else COLORS['warning']
                    icon = "⚠" if alert_type == "danger" else "⚡"
                    st.markdown(f"""
                    <div style="
                        background: {bg_color};
                        border-left: 4px solid {border_color};
                        border-radius: 8px;
                        padding: 1rem;
                        margin-bottom: 0.75rem;
                    ">
                        <div style="font-size: 0.875rem; font-weight: 600; color: {border_color};">
                            {icon} {title}
                        </div>
                        <div style="font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                            {description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.1);
                    border-left: 4px solid {COLORS['accent']};
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 0.875rem; font-weight: 600; color: {COLORS['accent']};">
                        全て正常です
                    </div>
                    <div style="font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                        現在、重要なアラートはありません
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("自社ブランドが登録されていません。設定画面でブランドを登録してください。")

# フッター
st.markdown(get_page_footer(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), unsafe_allow_html=True)

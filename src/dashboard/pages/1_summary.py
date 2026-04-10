"""
サマリー画面（経営向け）
総合スコア、前回比較、アラートを表示

デザインシステム v3.0 - AEO Premium Dark Theme
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
    get_alert_card,
    get_icon,
    COLORS,
    PLOTLY_COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle, is_demo_mode_active

st.set_page_config(page_title="サマリー - GEOスコアリング", page_icon=None, layout="wide")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# ページヘッダー
st.markdown(get_page_header(
    "サマリー",
    "経営層向けの概要ダッシュボード - 総合スコア、競合比較、アラート"
), unsafe_allow_html=True)

# デモモード対応: データ取得
if is_demo_mode_active():
    # デモモード: ダミーデータを作成
    class DemoBrand:
        def __init__(self, brand_id, name, is_own=False):
            self.id = brand_id
            self.name = name
            self.is_own = is_own

    class DemoScore:
        def __init__(self):
            self.total_score = 72
            self.visibility = 8
            self.sentiment = 15
            self.positioning = 12
            self.accuracy = 37

    own_brand = DemoBrand(1, "HubSpot", is_own=True)
    competitors = [
        DemoBrand(2, "Marketo"),
        DemoBrand(3, "Salesforce"),
        DemoBrand(4, "Pardot")
    ]
    latest_score = DemoScore()
    avg_scores = {
        'visibility': 7.5,
        'sentiment': 14.2,
        'positioning': 11.8,
        'accuracy': 35.5,
        'total': 69.0
    }
else:
    # 本番モード: データベースから取得
    with db.get_session() as session:
        own_brand = BrandRepository.get_own_brand(session)
        competitors = BrandRepository.get_competitors(session)

        if own_brand:
            # 自社の最新スコアと平均
            latest_score = ScoreRepository.get_latest_by_brand(session, own_brand.id)
            avg_scores = ScoreRepository.get_average_scores(session, own_brand.id, days=30)
        else:
            latest_score = None
            avg_scores = None

# データの表示
if own_brand and latest_score and avg_scores:
    # ================================
    # KPIカード セクション
    # ================================
        st.markdown(f"""
        <div style="margin-bottom: 0.75rem;">
            <span style="
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: {COLORS['text_muted']};
            ">
                主要指標
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        current_total = latest_score.total_score if latest_score else 0
        visibility_rate = (avg_scores['visibility'] / 10) * 100
        sentiment_value = avg_scores['sentiment']

        with col1:
            # 総合スコア（プレミアムカード）
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border_accent']};
                border-radius: 20px;
                padding: 1.75rem;
                position: relative;
                overflow: hidden;
            ">
                <!-- グローエフェクト -->
                <div style="
                    position: absolute;
                    right: -30px;
                    top: -30px;
                    width: 120px;
                    height: 120px;
                    background: radial-gradient(circle, rgba(222, 255, 154, 0.12), transparent 70%);
                    pointer-events: none;
                "></div>
                <div style="position: relative; z-index: 1;">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        margin-bottom: 0.5rem;
                    ">
                        <div style="color: {COLORS['accent']};">
                            {get_icon('layers', size=18, color=COLORS['accent'])}
                        </div>
                        <span style="
                            font-size: 0.75rem;
                            text-transform: uppercase;
                            letter-spacing: 0.1em;
                            color: {COLORS['text_muted']};
                        ">総合スコア</span>
                    </div>
                    <div style="
                        font-size: 3.5rem;
                        font-weight: 700;
                        font-family: 'JetBrains Mono', monospace;
                        background: {COLORS['gradient_accent']};
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        line-height: 1;
                    ">
                        {current_total}<span style="
                            font-size: 1.5rem;
                            -webkit-text-fill-color: {COLORS['text_muted']};
                        ">/100</span>
                    </div>
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 0.25rem;
                        margin-top: 0.75rem;
                        padding: 0.25rem 0.75rem;
                        background: rgba(74, 222, 128, 0.15);
                        border: 1px solid rgba(74, 222, 128, 0.3);
                        border-radius: 9999px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        color: {COLORS['success']};
                    ">
                        {get_icon('arrow_up', size=14, color=COLORS['success'])}
                        +5pt vs 先週
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # 認知率
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 1.75rem;
                height: 100%;
                transition: all 0.3s ease;
            " class="kpi-card">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <div style="color: {COLORS['accent_secondary']};">
                        {get_icon('eye', size=18, color=COLORS['accent_secondary'])}
                    </div>
                    <span style="
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        color: {COLORS['text_muted']};
                    ">認知率</span>
                </div>
                <div style="
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: {COLORS['accent_secondary']};
                    font-family: 'JetBrains Mono', monospace;
                    line-height: 1.1;
                ">
                    {visibility_rate:.0f}%
                </div>
                <div style="margin-top: 1rem;">
                    <div style="
                        height: 6px;
                        background: {COLORS['card_elevated']};
                        border-radius: 3px;
                        overflow: hidden;
                    ">
                        <div style="
                            height: 100%;
                            width: {visibility_rate}%;
                            background: linear-gradient(90deg, {COLORS['accent_secondary']}, #60a5fa);
                            border-radius: 3px;
                            transition: width 0.6s ease;
                        "></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # 推奨度
            sentiment_color = COLORS['success'] if sentiment_value >= 0 else COLORS['danger']
            sentiment_sign = "+" if sentiment_value >= 0 else ""
            sentiment_icon = "arrow_up" if sentiment_value >= 0 else "arrow_down"
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 1.75rem;
                height: 100%;
                transition: all 0.3s ease;
            " class="kpi-card">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <div style="color: {sentiment_color};">
                        {get_icon('message', size=18, color=sentiment_color)}
                    </div>
                    <span style="
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        color: {COLORS['text_muted']};
                    ">推奨度</span>
                </div>
                <div style="
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: {sentiment_color};
                    font-family: 'JetBrains Mono', monospace;
                    line-height: 1.1;
                ">
                    {sentiment_sign}{sentiment_value:.0f}pt
                </div>
                <div style="
                    font-size: 0.8rem;
                    color: {COLORS['text_muted']};
                    margin-top: 0.75rem;
                ">
                    範囲: -10 ~ +30
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # 30日平均
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 1.75rem;
                height: 100%;
                transition: all 0.3s ease;
            " class="kpi-card">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.5rem;
                ">
                    <div style="color: {COLORS['accent']};">
                        {get_icon('activity', size=18, color=COLORS['accent'])}
                    </div>
                    <span style="
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        color: {COLORS['text_muted']};
                    ">30日平均</span>
                </div>
                <div style="
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: {COLORS['text_primary']};
                    font-family: 'JetBrains Mono', monospace;
                    line-height: 1.1;
                ">
                    {avg_scores['total']:.1f}
                </div>
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 0.25rem;
                    font-size: 0.8rem;
                    color: {COLORS['success']};
                    margin-top: 0.75rem;
                ">
                    {get_icon('trend', size=14, color=COLORS['success'])}
                    安定上昇中
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
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
            ">
                <div style="color: {COLORS['accent_secondary']};">
                    {get_icon('trend', size=20, color=COLORS['accent_secondary'])}
                </div>
                <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">スコア推移</span>
                <span style="
                    background: {COLORS['card_elevated']};
                    padding: 0.25rem 0.75rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    color: {COLORS['text_muted']};
                ">過去90日</span>
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
                line=dict(color=COLORS['accent'], width=3),
                fill='tozeroy',
                fillcolor=f"rgba(222, 255, 154, 0.1)",
                hovertemplate='<b>%{x}</b><br>スコア: %{y:.1f}<extra></extra>'
            ))

            # レイアウト設定
            layout = get_plotly_layout("", height=350)
            layout.update({
                "xaxis_title": "",
                "yaxis_title": "スコア",
                "yaxis_range": [0, 100],
                "margin": {"l": 50, "r": 20, "t": 20, "b": 40},
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
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 1.5rem;
                height: 100%;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    margin-bottom: 1rem;
                ">
                    <div style="color: {COLORS['accent_tertiary']};">
                        {get_icon('chart', size=20, color=COLORS['accent_tertiary'])}
                    </div>
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

            colors = [COLORS['accent'] if d['is_own'] else COLORS['border'] for d in ranking_data]
            text_colors = [COLORS['text_inverse'] if d['is_own'] else COLORS['text_primary'] for d in ranking_data]
            labels = [f"{'*' if d['is_own'] else ''}{d['brand']}" for d in ranking_data]

            fig_ranking.add_trace(go.Bar(
                y=labels[::-1],
                x=[d['score'] for d in ranking_data][::-1],
                orientation='h',
                marker=dict(
                    color=colors[::-1],
                    cornerradius=8,
                    line=dict(width=0)
                ),
                text=[f"{d['score']:.1f}" for d in ranking_data][::-1],
                textposition='inside',
                textfont=dict(color=[COLORS['text_inverse'] if d['is_own'] else COLORS['text_primary'] for d in ranking_data][::-1], size=13, family="'JetBrains Mono', monospace"),
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
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 1.5rem;
                height: 100%;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    margin-bottom: 1rem;
                ">
                    <div style="color: {COLORS['warning']};">
                        {get_icon('alert_triangle', size=20, color=COLORS['warning'])}
                    </div>
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
                    st.markdown(get_alert_card(title, description, alert_type), unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: rgba(74, 222, 128, 0.1);
                    border: 1px solid rgba(74, 222, 128, 0.3);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                ">
                    <div style="
                        width: 48px;
                        height: 48px;
                        background: linear-gradient(135deg, {COLORS['success']} 0%, #86efac 100%);
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 0.75rem;
                    ">
                        {get_icon('check_circle', size=24, color=COLORS['text_inverse'])}
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; color: {COLORS['success']};">
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

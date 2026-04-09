"""
サマリー画面（経営向け）
総合スコア、前回比較、アラートを表示
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

st.set_page_config(page_title="サマリー - GEOスコアリング", layout="wide")

st.title("サマリー")
st.markdown("経営層向けの概要ダッシュボード")
st.markdown("---")

# データ取得
with db.get_session() as session:
    own_brand = BrandRepository.get_own_brand(session)
    competitors = BrandRepository.get_competitors(session)

    if own_brand:
        # 自社の最新スコアと平均
        latest_score = ScoreRepository.get_latest_by_brand(session, own_brand.id)
        avg_scores = ScoreRepository.get_average_scores(session, own_brand.id, days=30)

        # KPIカード表示
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            current_total = latest_score.total_score if latest_score else 0
            st.metric(
                label="総合スコア",
                value=f"{current_total}/100",
                delta=None
            )

        with col2:
            # 前回比較（仮の値）
            st.metric(
                label="前回比較",
                value=f"{avg_scores['total']:.1f}",
                delta="+5pt"
            )

        with col3:
            visibility_rate = (avg_scores['visibility'] / 10) * 100
            st.metric(
                label="認知率",
                value=f"{visibility_rate:.0f}%"
            )

        with col4:
            st.metric(
                label="推奨度",
                value=f"+{avg_scores['sentiment']:.0f}pt"
            )

        st.markdown("---")

        # スコア推移グラフ
        st.subheader("スコア推移")

        # トレンドデータ取得
        trend_data = ScoreRepository.get_score_trend(session, own_brand.id, days=90)

        if trend_data:
            df = pd.DataFrame(trend_data)
            fig = px.line(
                df,
                x="date",
                y="total",
                title="総合スコア推移（過去90日）",
                labels={"date": "日付", "total": "総合スコア"}
            )
            fig.update_layout(
                xaxis_title="日付",
                yaxis_title="スコア",
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("まだスコアデータがありません。バッチ処理を実行してください。")

        # 競合比較
        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("競合ランキング")

            # 競合データ取得
            all_brands = [own_brand] + competitors
            ranking_data = []

            for brand in all_brands:
                avg = ScoreRepository.get_average_scores(session, brand.id, days=30)
                ranking_data.append({
                    "ブランド": brand.name,
                    "スコア": avg['total'],
                    "自社": "★" if brand.is_own else ""
                })

            ranking_df = pd.DataFrame(ranking_data)
            ranking_df = ranking_df.sort_values("スコア", ascending=False)
            ranking_df["順位"] = range(1, len(ranking_df) + 1)
            ranking_df = ranking_df[["順位", "ブランド", "スコア", "自社"]]

            st.dataframe(ranking_df, hide_index=True, use_container_width=True)

        with col_right:
            st.subheader("アラート")

            # アラート条件をチェック
            alerts = []

            if avg_scores['visibility'] < 5:
                alerts.append("認知率が50%を下回っています")

            if avg_scores['sentiment'] < 0:
                alerts.append("推奨度がマイナスです")

            if avg_scores['accuracy'] < 20:
                alerts.append("情報正確性が低下しています")

            if alerts:
                for alert in alerts:
                    st.warning(alert)
            else:
                st.success("現在、重要なアラートはありません")

    else:
        st.warning("自社ブランドが登録されていません。設定画面でブランドを登録してください。")

# フッター
st.markdown("---")
st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

"""
トレンド・競合比較画面（マーケター向け）
時系列分析と競合比較を表示
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

st.set_page_config(page_title="トレンド分析 - GEOスコアリング", layout="wide")

st.title("トレンド・競合分析")
st.markdown("マーケター向けの詳細分析ダッシュボード")
st.markdown("---")

# フィルター
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

st.markdown("---")

# データ取得
with db.get_session() as session:
    if selected_brands:
        brand_ids = [brand_options[name] for name in selected_brands]

        # レーダーチャート用データ
        st.subheader("4指標レーダーチャート")

        radar_data = []
        for brand_name in selected_brands:
            brand_id = brand_options[brand_name]
            avg = ScoreRepository.get_average_scores(session, brand_id, days=period)

            # 各指標を0-100%に正規化
            radar_data.append({
                "ブランド": brand_name,
                "認知": (avg['visibility'] / 10) * 100,
                "推奨度": ((avg['sentiment'] + 10) / 40) * 100,  # -10〜30を0〜100に
                "ポジション": (avg['positioning'] / 20) * 100,
                "正確性": (avg['accuracy'] / 40) * 100
            })

        # レーダーチャート作成
        categories = ["認知", "推奨度", "ポジション", "正確性"]

        fig = go.Figure()

        for item in radar_data:
            fig.add_trace(go.Scatterpolar(
                r=[item["認知"], item["推奨度"], item["ポジション"], item["正確性"], item["認知"]],
                theta=categories + [categories[0]],
                fill='toself',
                name=item["ブランド"]
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="指標別パフォーマンス比較"
        )

        st.plotly_chart(fig, use_container_width=True)

        # 指標別トレンドと比較
        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("指標別達成率")

            # 自社の達成率を棒グラフで表示
            own_brand = BrandRepository.get_own_brand(session)
            if own_brand:
                avg = ScoreRepository.get_average_scores(session, own_brand.id, days=period)

                metrics = {
                    "認知": (avg['visibility'] / 10) * 100,
                    "推奨度": ((avg['sentiment'] + 10) / 40) * 100,
                    "ポジション": (avg['positioning'] / 20) * 100,
                    "正確性": (avg['accuracy'] / 40) * 100
                }

                fig_bar = px.bar(
                    x=list(metrics.keys()),
                    y=list(metrics.values()),
                    labels={"x": "指標", "y": "達成率(%)"},
                    title="自社の指標別達成率"
                )
                fig_bar.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("競合比較表")

            comparison_df = pd.DataFrame(radar_data)
            comparison_df = comparison_df.set_index("ブランド")

            # スタイリング
            st.dataframe(
                comparison_df.style.format("{:.1f}%").background_gradient(
                    cmap="RdYlGn",
                    vmin=0,
                    vmax=100
                ),
                use_container_width=True
            )

        # 時系列比較グラフ
        st.markdown("---")
        st.subheader("スコア推移比較")

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

            fig_trend = px.line(
                trend_df,
                x="date",
                y="total",
                color="ブランド",
                title="総合スコア推移比較",
                labels={"date": "日付", "total": "総合スコア"}
            )
            fig_trend.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("スコアデータがありません。バッチ処理を実行してください。")

    else:
        st.warning("比較するブランドを選択してください。")

# フッター
st.markdown("---")
st.caption(f"分析期間: 過去{period}日間")

"""
生データ分析画面（実務担当者向け）
個別回答の確認とエクスポート
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import json

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.database.models import Response, Score, Prompt, Brand
from src.database.repository import BrandRepository, ResponseRepository

st.set_page_config(page_title="生データ分析 - GEOスコアリング", layout="wide")

st.title("生データ分析")
st.markdown("実務担当者向けの詳細データ確認画面")
st.markdown("---")

# フィルターパネル
st.subheader("フィルター")
col1, col2, col3, col4 = st.columns(4)

with col1:
    start_date = st.date_input(
        "開始日",
        value=datetime.now() - timedelta(days=30)
    )

with col2:
    end_date = st.date_input(
        "終了日",
        value=datetime.now()
    )

with col3:
    with db.get_session() as session:
        all_brands = BrandRepository.get_all(session)
        brand_options = ["すべて"] + [b.name for b in all_brands]

    selected_brand = st.selectbox("ブランド", options=brand_options)

with col4:
    score_range = st.slider(
        "スコア範囲",
        min_value=0,
        max_value=100,
        value=(0, 100)
    )

st.markdown("---")

# データ取得と表示
with db.get_session() as session:
    # クエリ構築
    query = session.query(
        Response.id.label("response_id"),
        Response.executed_at,
        Response.raw_response,
        Prompt.category,
        Brand.name.label("brand_name"),
        Score.total_score,
        Score.visibility_score,
        Score.sentiment_score,
        Score.positioning_score,
        Score.accuracy_score,
        Score.visibility_detail,
        Score.sentiment_detail,
        Score.positioning_detail,
        Score.accuracy_detail
    ).join(
        Prompt, Response.prompt_id == Prompt.id
    ).join(
        Score, Response.id == Score.response_id
    ).join(
        Brand, Score.brand_id == Brand.id
    ).filter(
        Response.executed_at >= datetime.combine(start_date, datetime.min.time()),
        Response.executed_at <= datetime.combine(end_date, datetime.max.time())
    )

    # ブランドフィルター
    if selected_brand != "すべて":
        query = query.filter(Brand.name == selected_brand)

    # スコアフィルター
    query = query.filter(
        Score.total_score >= score_range[0],
        Score.total_score <= score_range[1]
    )

    # 結果取得
    results = query.order_by(Response.executed_at.desc()).limit(500).all()

    if results:
        # データテーブル表示
        st.subheader("回答データ一覧")

        table_data = []
        for r in results:
            table_data.append({
                "ID": r.response_id,
                "日時": r.executed_at.strftime("%Y-%m-%d %H:%M") if r.executed_at else "",
                "カテゴリ": r.category,
                "ブランド": r.brand_name,
                "総合": r.total_score,
                "認知": r.visibility_score,
                "推奨": r.sentiment_score,
                "位置": r.positioning_score,
                "正確": r.accuracy_score
            })

        df = pd.DataFrame(table_data)

        # テーブル表示（選択可能）
        selected_row = st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "総合": st.column_config.ProgressColumn(
                    "総合",
                    min_value=0,
                    max_value=100
                )
            }
        )

        # エクスポートボタン
        col_export1, col_export2, col_export3 = st.columns([1, 1, 4])

        with col_export1:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="CSVダウンロード",
                data=csv,
                file_name=f"geo_scores_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with col_export2:
            # Excel形式
            try:
                import io
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine="openpyxl")
                st.download_button(
                    label="Excelダウンロード",
                    data=buffer.getvalue(),
                    file_name=f"geo_scores_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.info("Excel出力にはopenpyxlが必要です")

        # 詳細表示
        st.markdown("---")
        st.subheader("詳細表示")

        # IDで詳細を選択
        if results:
            selected_id = st.selectbox(
                "詳細を表示するID",
                options=[r.response_id for r in results],
                format_func=lambda x: f"ID: {x}"
            )

            # 選択された回答の詳細を表示
            selected_result = next((r for r in results if r.response_id == selected_id), None)

            if selected_result:
                col_detail1, col_detail2 = st.columns(2)

                with col_detail1:
                    st.markdown("**AI回答（原文）**")
                    st.text_area(
                        "回答内容",
                        value=selected_result.raw_response or "回答なし",
                        height=300,
                        disabled=True
                    )

                with col_detail2:
                    st.markdown("**スコア内訳**")

                    # スコアバー
                    st.markdown(f"認知: {selected_result.visibility_score}/10")
                    st.progress(selected_result.visibility_score / 10 if selected_result.visibility_score else 0)

                    st.markdown(f"推奨度: {selected_result.sentiment_score}/30")
                    sentiment_normalized = (selected_result.sentiment_score + 10) / 40 if selected_result.sentiment_score else 0
                    st.progress(sentiment_normalized)

                    st.markdown(f"ポジション: {selected_result.positioning_score}/20")
                    st.progress(selected_result.positioning_score / 20 if selected_result.positioning_score else 0)

                    st.markdown(f"正確性: {selected_result.accuracy_score}/40")
                    st.progress(selected_result.accuracy_score / 40 if selected_result.accuracy_score else 0)

                # 評価詳細
                st.markdown("---")
                st.markdown("**評価詳細**")

                tab1, tab2, tab3, tab4 = st.tabs(["認知", "推奨度", "ポジション", "正確性"])

                with tab1:
                    if selected_result.visibility_detail:
                        detail = selected_result.visibility_detail
                        if isinstance(detail, str):
                            detail = json.loads(detail)
                        st.json(detail)
                    else:
                        st.info("詳細情報なし")

                with tab2:
                    if selected_result.sentiment_detail:
                        detail = selected_result.sentiment_detail
                        if isinstance(detail, str):
                            detail = json.loads(detail)
                        st.json(detail)
                    else:
                        st.info("詳細情報なし")

                with tab3:
                    if selected_result.positioning_detail:
                        detail = selected_result.positioning_detail
                        if isinstance(detail, str):
                            detail = json.loads(detail)
                        st.json(detail)
                    else:
                        st.info("詳細情報なし")

                with tab4:
                    if selected_result.accuracy_detail:
                        detail = selected_result.accuracy_detail
                        if isinstance(detail, str):
                            detail = json.loads(detail)
                        st.json(detail)
                    else:
                        st.info("詳細情報なし")

    else:
        st.info("条件に一致するデータがありません。フィルターを調整するか、バッチ処理を実行してください。")

# フッター
st.markdown("---")
st.caption(f"表示件数: {len(results) if results else 0}件 / 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

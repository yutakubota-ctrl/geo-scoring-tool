"""
生データ分析画面（実務担当者向け）
個別回答の確認とエクスポート

デザインシステム v2.1適用
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
from src.dashboard.styles.common import (
    get_common_css,
    get_page_header,
    get_page_footer,
    COLORS
)

st.set_page_config(page_title="生データ分析 - GEOスコアリング", layout="wide")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# ページヘッダー
st.markdown(get_page_header(
    "生データ分析",
    "実務担当者向け - 個別回答の確認、フィルタリング、エクスポート"
), unsafe_allow_html=True)

# ================================
# フィルターパネル
# ================================
st.markdown(f"""
<div style="
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
">
    <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: {COLORS['text_muted']}; margin-bottom: 1rem;">
        フィルター設定
    </div>
""", unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

# ================================
# データ取得と表示
# ================================
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
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">回答データ一覧</span>
                    <span style="
                        background: {COLORS['bg_primary']};
                        color: {COLORS['text_secondary']};
                        padding: 0.25rem 0.75rem;
                        border-radius: 9999px;
                        font-size: 0.75rem;
                        margin-left: 0.5rem;
                    ">{len(results)}件</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

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

        # テーブル表示
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "総合": st.column_config.ProgressColumn(
                    "総合",
                    min_value=0,
                    max_value=100,
                    format="%d"
                ),
                "認知": st.column_config.NumberColumn("認知", format="%d/10"),
                "推奨": st.column_config.NumberColumn("推奨", format="%d"),
                "位置": st.column_config.NumberColumn("位置", format="%d/20"),
                "正確": st.column_config.NumberColumn("正確", format="%d/40"),
            },
            height=400
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # ================================
        # エクスポートボタン
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
            <div style="font-size: 0.875rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.75rem;">
                データエクスポート
            </div>
        """, unsafe_allow_html=True)

        col_export1, col_export2, col_export3 = st.columns([1, 1, 4])

        with col_export1:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="CSV",
                data=csv,
                file_name=f"geo_scores_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_export2:
            try:
                import io
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine="openpyxl")
                st.download_button(
                    label="Excel",
                    data=buffer.getvalue(),
                    file_name=f"geo_scores_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except ImportError:
                st.info("Excel出力にはopenpyxlが必要です")

        st.markdown("</div>", unsafe_allow_html=True)

        # ================================
        # 詳細表示
        # ================================
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
        ">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                詳細表示
            </div>
        """, unsafe_allow_html=True)

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
                col_detail1, col_detail2 = st.columns([3, 2])

                with col_detail1:
                    st.markdown(f"""
                    <div style="
                        background: {COLORS['bg_primary']};
                        border-radius: 12px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    ">
                        <div style="font-size: 0.875rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                            AI回答（原文）
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.text_area(
                        "回答内容",
                        value=selected_result.raw_response or "回答なし",
                        height=250,
                        disabled=True,
                        label_visibility="collapsed"
                    )

                with col_detail2:
                    st.markdown(f"""
                    <div style="
                        background: {COLORS['bg_primary']};
                        border-radius: 12px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    ">
                        <div style="font-size: 0.875rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                            スコア内訳
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # スコアバー（カスタムHTML）
                    scores = [
                        ("認知", selected_result.visibility_score or 0, 10, COLORS['secondary']),
                        ("推奨度", (selected_result.sentiment_score or 0) + 10, 40, COLORS['accent']),
                        ("ポジション", selected_result.positioning_score or 0, 20, COLORS['warning']),
                        ("正確性", selected_result.accuracy_score or 0, 40, '#8B5CF6'),
                    ]

                    for name, value, max_val, color in scores:
                        percentage = (value / max_val) * 100 if max_val > 0 else 0
                        st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                <span style="font-size: 0.875rem; color: {COLORS['text_primary']};">{name}</span>
                                <span style="font-size: 0.875rem; font-family: 'JetBrains Mono', monospace; color: {COLORS['text_secondary']};">
                                    {value if name != '推奨度' else value - 10}/{max_val if name != '推奨度' else '30'}
                                </span>
                            </div>
                            <div style="height: 8px; background: {COLORS['bg_primary']}; border-radius: 4px; overflow: hidden;">
                                <div style="height: 100%; width: {percentage}%; background: {color}; border-radius: 4px; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # 評価詳細タブ
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-size: 0.875rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.75rem;">
                    評価詳細
                </div>
                """, unsafe_allow_html=True)

                tab1, tab2, tab3, tab4 = st.tabs(["認知", "推奨度", "ポジション", "正確性"])

                def display_detail(detail_data):
                    if detail_data:
                        detail = detail_data
                        if isinstance(detail, str):
                            detail = json.loads(detail)

                        # カード形式で表示
                        for key, value in detail.items():
                            st.markdown(f"""
                            <div style="
                                background: {COLORS['bg_primary']};
                                border-radius: 8px;
                                padding: 0.75rem 1rem;
                                margin-bottom: 0.5rem;
                            ">
                                <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; margin-bottom: 0.25rem;">{key}</div>
                                <div style="font-size: 0.875rem; color: {COLORS['text_primary']};">{value}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("詳細情報なし")

                with tab1:
                    display_detail(selected_result.visibility_detail)

                with tab2:
                    display_detail(selected_result.sentiment_detail)

                with tab3:
                    display_detail(selected_result.positioning_detail)

                with tab4:
                    display_detail(selected_result.accuracy_detail)

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
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                データが見つかりません
            </div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">
                条件に一致するデータがありません。フィルターを調整するか、バッチ処理を実行してください。
            </div>
        </div>
        """, unsafe_allow_html=True)

# フッター
st.markdown(get_page_footer(f"表示件数: {len(results) if results else 0}件 / 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), unsafe_allow_html=True)

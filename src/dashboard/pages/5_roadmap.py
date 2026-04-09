"""
ロードマップ画面（Gem_02専用）

Impact x Effort マトリクスで優先度を可視化
- 散布図（X軸: Effort, Y軸: Impact）
- タスクリスト（優先度P0/P1/P2別）
- ステータス別フィルタ

デザインシステム v2.1適用
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
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
    get_plotly_layout,
    COLORS,
    PLOTLY_COLORS
)
from src.dashboard.components.demo_toggle import render_demo_toggle, is_demo_mode_active

st.set_page_config(page_title="ロードマップ - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# 共通CSSの適用
st.markdown(get_common_css(), unsafe_allow_html=True)

# デモモードトグル（右上固定）
render_demo_toggle()

# ページヘッダー
st.markdown(get_page_header(
    "ロードマップ",
    "Impact x Effort マトリクスで施策の優先順位を可視化"
), unsafe_allow_html=True)

# デモモードの確認
demo_mode = is_demo_mode_active()

def load_roadmap_data():
    """ロードマップデータを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "roadmap_sample.json"
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    else:
        return None

# データ読み込み
roadmap_data = load_roadmap_data()

if roadmap_data:
    tasks = roadmap_data.get('tasks', [])
    summary = roadmap_data.get('summary', {})

    # ================================
    # サマリーメトリクス
    # ================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #1E40AF 100%);
            border-radius: 16px;
            padding: 1.5rem;
            color: white;
            text-align: center;
        ">
            <div style="font-size: 0.875rem; opacity: 0.8;">総タスク数</div>
            <div style="font-size: 2.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {summary.get('total_tasks', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['danger']} 0%, #F87171 100%);
            border-radius: 16px;
            padding: 1.5rem;
            color: white;
            text-align: center;
        ">
            <div style="font-size: 0.875rem; opacity: 0.9;">P0（最優先）</div>
            <div style="font-size: 2.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {summary.get('p0_count', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['secondary']} 0%, #60A5FA 100%);
            border-radius: 16px;
            padding: 1.5rem;
            color: white;
            text-align: center;
        ">
            <div style="font-size: 0.875rem; opacity: 0.9;">進行中</div>
            <div style="font-size: 2.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {summary.get('status_breakdown', {}).get('In_Progress', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['accent']} 0%, #34D399 100%);
            border-radius: 16px;
            padding: 1.5rem;
            color: white;
            text-align: center;
        ">
            <div style="font-size: 0.875rem; opacity: 0.9;">完了済み</div>
            <div style="font-size: 2.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 0.25rem 0;">
                {summary.get('status_breakdown', {}).get('Done', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # タブ構成
    tab1, tab2, tab3 = st.tabs(["Impact x Effort マトリクス", "タスクリスト", "統計情報"])

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
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">Impact x Effort マトリクス</span>
                <p style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-top: 0.25rem;">
                    右上（高Impact・低Effort）のタスクを優先的に実施
                </p>
            </div>
        """, unsafe_allow_html=True)

        # データフレーム作成
        df = pd.DataFrame(tasks)

        # 優先度別の色とサイズ
        priority_config = {
            'P0': {'color': COLORS['danger'], 'size': 24, 'name': 'P0 最優先'},
            'P1': {'color': COLORS['warning'], 'size': 20, 'name': 'P1 重要'},
            'P2': {'color': COLORS['secondary'], 'size': 16, 'name': 'P2 通常'}
        }

        fig = go.Figure()

        for priority in ['P0', 'P1', 'P2']:
            df_filtered = df[df['priority'] == priority]

            fig.add_trace(go.Scatter(
                x=df_filtered['effort_score'],
                y=df_filtered['impact_score'],
                mode='markers+text',
                name=priority_config[priority]['name'],
                marker=dict(
                    size=priority_config[priority]['size'],
                    color=priority_config[priority]['color'],
                    line=dict(width=2, color='white'),
                    opacity=0.9
                ),
                text=df_filtered['task_id'].str.replace('task_', 'T'),
                textposition='middle center',
                textfont=dict(size=9, color='white', family="JetBrains Mono"),
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                              'Impact: %{y}/10<br>' +
                              'Effort: %{x}/10<br>' +
                              'Priority: %{customdata[1]}<br>' +
                              '<extra></extra>',
                customdata=df_filtered[['description', 'priority']].values
            ))

        # 象限の背景色
        fig.add_shape(type="rect", x0=0, y0=5, x1=5, y1=10.5,
                      fillcolor="rgba(16, 185, 129, 0.08)", line=dict(width=0))
        fig.add_shape(type="rect", x0=5, y0=5, x1=10.5, y1=10.5,
                      fillcolor="rgba(245, 158, 11, 0.08)", line=dict(width=0))
        fig.add_shape(type="rect", x0=0, y0=0, x1=5, y1=5,
                      fillcolor="rgba(59, 130, 246, 0.08)", line=dict(width=0))
        fig.add_shape(type="rect", x0=5, y0=0, x1=10.5, y1=5,
                      fillcolor="rgba(239, 68, 68, 0.08)", line=dict(width=0))

        # 中心線
        fig.add_shape(type="line", x0=5, y0=0, x1=5, y1=10.5,
                      line=dict(color=COLORS['text_muted'], width=1, dash="dot"))
        fig.add_shape(type="line", x0=0, y0=5, x1=10.5, y1=5,
                      line=dict(color=COLORS['text_muted'], width=1, dash="dot"))

        # 象限ラベル
        annotations = [
            dict(x=2.5, y=9.5, text="Quick Wins", font=dict(size=12, color=COLORS['accent']), showarrow=False),
            dict(x=7.5, y=9.5, text="Strategic", font=dict(size=12, color=COLORS['warning']), showarrow=False),
            dict(x=2.5, y=1.5, text="Fill-ins", font=dict(size=12, color=COLORS['secondary']), showarrow=False),
            dict(x=7.5, y=1.5, text="Time Sinks", font=dict(size=12, color=COLORS['danger']), showarrow=False),
        ]

        layout = get_plotly_layout("", height=500)
        layout.update({
            "xaxis": dict(
                title="Effort (実装難易度)",
                range=[0, 10.5],
                dtick=2,
                gridcolor='rgba(0,0,0,0.05)',
                title_font=dict(size=12, color=COLORS['text_secondary'])
            ),
            "yaxis": dict(
                title="Impact (インパクト)",
                range=[0, 10.5],
                dtick=2,
                gridcolor='rgba(0,0,0,0.05)',
                title_font=dict(size=12, color=COLORS['text_secondary'])
            ),
            "margin": dict(l=60, r=20, t=20, b=60),
            "legend": dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            "annotations": annotations
        })
        fig.update_layout(**layout)

        st.plotly_chart(fig, use_container_width=True)

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
                <span style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']};">タスクリスト</span>
            </div>
        """, unsafe_allow_html=True)

        # フィルター
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            priority_filter = st.multiselect(
                "優先度",
                options=['P0', 'P1', 'P2'],
                default=['P0', 'P1', 'P2']
            )

        with col_filter2:
            status_filter = st.multiselect(
                "ステータス",
                options=['Pending', 'In_Progress', 'Done'],
                default=['Pending', 'In_Progress'],
                format_func=lambda x: {'Pending': '未着手', 'In_Progress': '進行中', 'Done': '完了'}.get(x, x)
            )

        with col_filter3:
            type_filter = st.multiselect(
                "タイプ",
                options=['Content', 'Technical', 'Analytics'],
                default=['Content', 'Technical', 'Analytics']
            )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # フィルタリング
        filtered_tasks = [
            task for task in tasks
            if task['priority'] in priority_filter
            and task['status'] in status_filter
            and task['task_type'] in type_filter
        ]

        st.markdown(f"""
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; margin-bottom: 1rem;">
            該当タスク: <strong>{len(filtered_tasks)}件</strong>
        </div>
        """, unsafe_allow_html=True)

        # タスク表示
        for task in filtered_tasks:
            # 優先度バッジの色
            priority_colors = {
                'P0': COLORS['danger'],
                'P1': COLORS['warning'],
                'P2': COLORS['secondary']
            }
            priority_color = priority_colors.get(task['priority'], COLORS['text_muted'])

            # ステータスバッジの色と日本語
            status_config = {
                'Pending': {'color': COLORS['text_muted'], 'label': '未着手'},
                'In_Progress': {'color': COLORS['secondary'], 'label': '進行中'},
                'Done': {'color': COLORS['accent'], 'label': '完了'}
            }
            status_info = status_config.get(task['status'], {'color': COLORS['text_muted'], 'label': task['status']})

            st.markdown(f"""
            <div style="
                background: {COLORS['bg_primary']};
                border-left: 4px solid {priority_color};
                border-radius: 8px;
                padding: 1rem 1.25rem;
                margin-bottom: 0.75rem;
                transition: box-shadow 0.2s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span style="
                            background: {priority_color};
                            color: white;
                            padding: 0.2rem 0.6rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 700;
                        ">{task['priority']}</span>
                        <span style="
                            background: rgba({int(status_info['color'][1:3], 16)}, {int(status_info['color'][3:5], 16)}, {int(status_info['color'][5:7], 16)}, 0.15);
                            color: {status_info['color']};
                            padding: 0.2rem 0.6rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        ">{status_info['label']}</span>
                        <span style="
                            color: {COLORS['text_muted']};
                            font-size: 0.75rem;
                        ">{task['task_type']}</span>
                    </div>
                    <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">
                        {task['task_id']}
                    </div>
                </div>
                <div style="font-size: 1rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
                    {task['description']}
                </div>
                <div style="display: flex; gap: 1.5rem; font-size: 0.8125rem; color: {COLORS['text_secondary']};">
                    <span>担当: {task['assigned_to']}</span>
                    <span>期限: {task['due_date']}</span>
                    <span>Impact: {task['impact_score']}/10</span>
                    <span>Effort: {task['effort_score']}/10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if not filtered_tasks:
            st.info("該当するタスクがありません。フィルターを変更してください。")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
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
                    優先度別分布
                </div>
            """, unsafe_allow_html=True)

            fig_priority = go.Figure(data=[
                go.Bar(
                    x=['P0 最優先', 'P1 重要', 'P2 通常'],
                    y=[summary.get('p0_count', 0), summary.get('p1_count', 0), summary.get('p2_count', 0)],
                    marker=dict(
                        color=[COLORS['danger'], COLORS['warning'], COLORS['secondary']],
                        cornerradius=8
                    ),
                    text=[summary.get('p0_count', 0), summary.get('p1_count', 0), summary.get('p2_count', 0)],
                    textposition='outside',
                    textfont=dict(size=14, color=COLORS['text_primary'], family="JetBrains Mono")
                )
            ])

            layout_priority = get_plotly_layout("", height=280)
            layout_priority.update({
                "yaxis_title": "タスク数",
                "margin": dict(l=50, r=20, t=20, b=40),
            })
            fig_priority.update_layout(**layout_priority)

            st.plotly_chart(fig_priority, use_container_width=True)

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
                    ステータス別分布
                </div>
            """, unsafe_allow_html=True)

            status_breakdown = summary.get('status_breakdown', {})

            fig_status = go.Figure(data=[
                go.Pie(
                    labels=['未着手', '進行中', '完了'],
                    values=[
                        status_breakdown.get('Pending', 0),
                        status_breakdown.get('In_Progress', 0),
                        status_breakdown.get('Done', 0)
                    ],
                    marker=dict(
                        colors=[COLORS['text_muted'], COLORS['secondary'], COLORS['accent']]
                    ),
                    textinfo='label+percent',
                    textfont=dict(size=12),
                    hole=0.4,
                    hovertemplate='<b>%{label}</b><br>タスク数: %{value}<br>割合: %{percent}<extra></extra>'
                )
            ])

            layout_status = get_plotly_layout("", height=280)
            layout_status.update({
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": False
            })
            fig_status.update_layout(**layout_status)

            st.plotly_chart(fig_status, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # 平均スコア
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
                平均スコア
            </div>
            <div style="display: flex; gap: 2rem;">
                <div style="
                    background: {COLORS['bg_primary']};
                    border-radius: 12px;
                    padding: 1rem 1.5rem;
                    flex: 1;
                    text-align: center;
                ">
                    <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">平均インパクト</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: {COLORS['accent']}; font-family: 'JetBrains Mono', monospace;">
                        {summary.get('avg_impact', 0):.1f}<span style="font-size: 1rem; opacity: 0.7;">/10</span>
                    </div>
                </div>
                <div style="
                    background: {COLORS['bg_primary']};
                    border-radius: 12px;
                    padding: 1rem 1.5rem;
                    flex: 1;
                    text-align: center;
                ">
                    <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">平均難易度</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: {COLORS['warning']}; font-family: 'JetBrains Mono', monospace;">
                        {summary.get('avg_effort', 0):.1f}<span style="font-size: 1rem; opacity: 0.7;">/10</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
        <div style="font-size: 4rem; margin-bottom: 1rem;">🗺</div>
        <div style="font-size: 1.25rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            ロードマップデータが見つかりません
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

"""
ロードマップ画面（Gem_02専用）

Impact × Effort マトリクスで優先度を可視化
- 散布図（X軸: Effort, Y軸: Impact）
- タスクリスト（優先度P0/P1/P2別）
- ステータス別フィルタ
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

st.set_page_config(page_title="ロードマップ - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# カスタムCSS
st.markdown("""
<style>
    .priority-badge-p0 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .priority-badge-p1 {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .priority-badge-p2 {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .status-badge-pending {
        background: #B0BEC5;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-badge-in-progress {
        background: #42A5F5;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-badge-done {
        background: #66BB6A;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .task-card {
        background: white;
        border-left: 5px solid #667eea;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    .task-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transition: box-shadow 0.2s;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

st.title("ロードマップ")
st.markdown("優先順位付きタスク管理 - Impact × Effort マトリクス")
st.markdown("---")

# デモモードの確認
demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

def load_roadmap_data():
    """ロードマップデータを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "roadmap_sample.json"
        with open(demo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # TODO: 本番環境ではデータベースから取得
        return None

# データ読み込み
roadmap_data = load_roadmap_data()

if roadmap_data:
    tasks = roadmap_data.get('tasks', [])
    summary = roadmap_data.get('summary', {})

    # サマリーメトリクス
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>総タスク数</div>
            <div class='metric-value'>{summary.get('total_tasks', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
            <div class='metric-label'>P0（最優先）</div>
            <div class='metric-value'>{summary.get('p0_count', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
            <div class='metric-label'>進行中</div>
            <div class='metric-value'>{summary.get('status_breakdown', {}).get('In_Progress', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'>
            <div class='metric-label'>完了済み</div>
            <div class='metric-value'>{summary.get('status_breakdown', {}).get('Done', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # タブ構成
    tab1, tab2, tab3 = st.tabs(["Impact × Effort マトリクス", "タスクリスト", "統計情報"])

    with tab1:
        st.markdown("## Impact × Effort マトリクス")
        st.markdown("右上（高Impact・低Effort）のタスクを優先的に実施します。")
        st.markdown("")

        # データフレーム作成
        df = pd.DataFrame(tasks)

        # 色分け設定
        color_map = {
            'P0': '#f5576c',
            'P1': '#fee140',
            'P2': '#a8edea'
        }
        df['color'] = df['priority'].map(color_map)

        # 散布図作成
        fig = go.Figure()

        for priority in ['P0', 'P1', 'P2']:
            df_filtered = df[df['priority'] == priority]

            fig.add_trace(go.Scatter(
                x=df_filtered['effort_score'],
                y=df_filtered['impact_score'],
                mode='markers+text',
                name=priority,
                marker=dict(
                    size=20,
                    color=color_map[priority],
                    line=dict(width=2, color='white')
                ),
                text=df_filtered['task_id'],
                textposition='top center',
                textfont=dict(size=10, color='#333'),
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                              'Impact: %{y}<br>' +
                              'Effort: %{x}<br>' +
                              'Priority: %{customdata[1]}<br>' +
                              '<extra></extra>',
                customdata=df_filtered[['description', 'priority']].values
            ))

        # レイアウト設定
        fig.update_layout(
            title="タスク優先度マトリクス",
            xaxis_title="実装難易度（Effort）",
            yaxis_title="インパクト（Impact）",
            xaxis=dict(range=[0, 11], dtick=1),
            yaxis=dict(range=[0, 11], dtick=1),
            height=600,
            hovermode='closest',
            plot_bgcolor='rgba(240, 240, 240, 0.5)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # グリッド線追加
        fig.add_shape(
            type="line",
            x0=5, y0=0, x1=5, y1=11,
            line=dict(color="gray", width=1, dash="dash")
        )
        fig.add_shape(
            type="line",
            x0=0, y0=5, x1=11, y1=5,
            line=dict(color="gray", width=1, dash="dash")
        )

        # 象限ラベル
        fig.add_annotation(x=2.5, y=9, text="高Impact<br>低Effort<br>(優先)", showarrow=False, font=dict(size=12, color="green"))
        fig.add_annotation(x=8, y=9, text="高Impact<br>高Effort<br>(計画的)", showarrow=False, font=dict(size=12, color="orange"))
        fig.add_annotation(x=2.5, y=2, text="低Impact<br>低Effort<br>(隙間時間)", showarrow=False, font=dict(size=12, color="blue"))
        fig.add_annotation(x=8, y=2, text="低Impact<br>高Effort<br>(後回し)", showarrow=False, font=dict(size=12, color="red"))

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("## タスクリスト")

        # フィルター
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            priority_filter = st.multiselect(
                "優先度フィルタ",
                options=['P0', 'P1', 'P2'],
                default=['P0', 'P1', 'P2']
            )

        with col_filter2:
            status_filter = st.multiselect(
                "ステータスフィルタ",
                options=['Pending', 'In_Progress', 'Done'],
                default=['Pending', 'In_Progress', 'Done']
            )

        with col_filter3:
            type_filter = st.multiselect(
                "タイプフィルタ",
                options=['Content', 'Technical', 'Analytics'],
                default=['Content', 'Technical', 'Analytics']
            )

        # フィルタリング
        filtered_tasks = [
            task for task in tasks
            if task['priority'] in priority_filter
            and task['status'] in status_filter
            and task['task_type'] in type_filter
        ]

        st.markdown(f"**該当タスク: {len(filtered_tasks)}件**")
        st.markdown("")

        # タスク表示
        for task in filtered_tasks:
            priority_badge_class = f"priority-badge-{task['priority'].lower()}"
            status_badge_class = f"status-badge-{task['status'].lower().replace('_', '-')}"

            st.markdown(f"""
            <div class='task-card'>
                <div style='margin-bottom: 0.5rem;'>
                    <span class='{priority_badge_class}'>{task['priority']}</span>
                    <span class='{status_badge_class}' style='margin-left: 0.5rem;'>{task['status']}</span>
                    <span style='margin-left: 0.5rem; color: #666; font-size: 0.85rem;'>{task['task_type']}</span>
                </div>
                <div style='font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>
                    {task['description']}
                </div>
                <div style='color: #666; font-size: 0.9rem;'>
                    <strong>担当:</strong> {task['assigned_to']} |
                    <strong>期限:</strong> {task['due_date']} |
                    <strong>Impact:</strong> {task['impact_score']}/10 |
                    <strong>Effort:</strong> {task['effort_score']}/10
                </div>
            </div>
            """, unsafe_allow_html=True)

        if not filtered_tasks:
            st.info("該当するタスクがありません。フィルターを変更してください。")

    with tab3:
        st.markdown("## 統計情報")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("### 優先度別分布")
            priority_counts = summary.get('status_breakdown', {})

            fig_priority = go.Figure(data=[
                go.Bar(
                    x=['P0', 'P1', 'P2'],
                    y=[summary.get('p0_count', 0), summary.get('p1_count', 0), summary.get('p2_count', 0)],
                    marker=dict(
                        color=['#f5576c', '#fee140', '#a8edea']
                    ),
                    text=[summary.get('p0_count', 0), summary.get('p1_count', 0), summary.get('p2_count', 0)],
                    textposition='auto'
                )
            ])

            fig_priority.update_layout(
                xaxis_title="優先度",
                yaxis_title="タスク数",
                height=300,
                showlegend=False
            )

            st.plotly_chart(fig_priority, use_container_width=True)

        with col_chart2:
            st.markdown("### ステータス別分布")
            status_breakdown = summary.get('status_breakdown', {})

            fig_status = go.Figure(data=[
                go.Pie(
                    labels=list(status_breakdown.keys()),
                    values=list(status_breakdown.values()),
                    marker=dict(
                        colors=['#B0BEC5', '#42A5F5', '#66BB6A']
                    ),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>タスク数: %{value}<br>割合: %{percent}<extra></extra>'
                )
            ])

            fig_status.update_layout(height=300, showlegend=False)

            st.plotly_chart(fig_status, use_container_width=True)

        # 平均スコア
        st.markdown("### 平均スコア")
        col_avg1, col_avg2 = st.columns(2)

        with col_avg1:
            avg_impact = summary.get('avg_impact', 0)
            st.metric("平均インパクト", f"{avg_impact:.1f}/10")

        with col_avg2:
            avg_effort = summary.get('avg_effort', 0)
            st.metric("平均難易度", f"{avg_effort:.1f}/10")

else:
    st.error("ロードマップデータが見つかりません。デモモードを有効化してください。")
    st.info("環境変数 `DEMO_MODE=true` を設定してください。")

# フッター
st.markdown("---")
st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

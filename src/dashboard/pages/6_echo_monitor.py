"""
エコー監視画面（Gem_05専用）

AI Overviewsでのメンション状況をリアルタイム追跡
- メンション数推移（折れ線グラフ）
- センチメントスコア（ゲージチャート）
- 参照順位の変化（トレンド分析）
- 最新引用一覧（テーブル表示）
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

st.set_page_config(page_title="エコー監視 - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# カスタムCSS
st.markdown("""
<style>
    .echo-status-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    .echo-status-partial {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    .echo-status-fail {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    .llm-badge-active {
        background: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .llm-badge-inactive {
        background: #BDBDBD;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .citation-card {
        background: white;
        border-left: 5px solid #667eea;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    .citation-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transition: box-shadow 0.2s;
    }
    .sentiment-positive {
        color: #4CAF50;
        font-weight: 700;
    }
    .sentiment-neutral {
        color: #FF9800;
        font-weight: 700;
    }
    .sentiment-negative {
        color: #F44336;
        font-weight: 700;
    }
    .metric-card-eco {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value-eco {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label-eco {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

st.title("エコー監視")
st.markdown("AI Overviewsでのブランドメンション状況をリアルタイム追跡")
st.markdown("---")

# デモモードの確認
demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

def load_echo_monitor_data():
    """エコー監視データを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "echo_monitor_sample.json"
        with open(demo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # TODO: 本番環境ではデータベースから取得
        return None

# データ読み込み
echo_data = load_echo_monitor_data()

if echo_data:
    current_status = echo_data.get('current_status', {})
    timeline_data = echo_data.get('timeline_data', [])
    recent_citations = echo_data.get('recent_citations', [])

    # エコー成功ステータス
    echo_success = current_status.get('echo_success', '失敗')
    status_class = {
        '成功': 'echo-status-success',
        '部分成功': 'echo-status-partial',
        '失敗': 'echo-status-fail'
    }.get(echo_success, 'echo-status-fail')

    st.markdown(f"<div class='{status_class}'>エコーステータス: {echo_success}</div>", unsafe_allow_html=True)

    # サマリーメトリクス
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mention_count = current_status.get('mention_count', 0)
        st.markdown(f"""
        <div class='metric-card-eco'>
            <div class='metric-label-eco'>メンション数</div>
            <div class='metric-value-eco'>{mention_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        sentiment_score = current_status.get('sentiment_score', 0)
        st.markdown(f"""
        <div class='metric-card-eco' style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);'>
            <div class='metric-label-eco'>センチメント</div>
            <div class='metric-value-eco'>{sentiment_score:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        reference_rank = current_status.get('reference_rank', '圏外')
        st.markdown(f"""
        <div class='metric-card-eco' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
            <div class='metric-label-eco'>参照順位</div>
            <div class='metric-value-eco' style='color: #333;'>{reference_rank}位</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        llm_coverage = current_status.get('llm_coverage', {})
        active_llms = sum(1 for v in llm_coverage.values() if v)
        st.markdown(f"""
        <div class='metric-card-eco' style='background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);'>
            <div class='metric-label-eco'>LLMカバレッジ</div>
            <div class='metric-value-eco'>{active_llms}/4</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # LLMカバレッジ詳細
    st.markdown("### LLM別カバレッジ")
    llm_coverage = current_status.get('llm_coverage', {})

    col_llm1, col_llm2, col_llm3, col_llm4 = st.columns(4)

    for col, (llm_name, is_active) in zip([col_llm1, col_llm2, col_llm3, col_llm4], llm_coverage.items()):
        with col:
            badge_class = "llm-badge-active" if is_active else "llm-badge-inactive"
            status_text = "引用あり" if is_active else "引用なし"
            st.markdown(f"<div class='{badge_class}'>{llm_name}: {status_text}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs(["メンション推移", "センチメント分析", "最新引用", "統計サマリー"])

    with tab1:
        st.markdown("## メンション数推移")
        st.markdown("過去4週間のAI Overviewsでのメンション数をトラッキングします。")
        st.markdown("")

        # データフレーム作成
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline['date'] = pd.to_datetime(df_timeline['date'])

        # 折れ線グラフ
        fig_timeline = go.Figure()

        fig_timeline.add_trace(go.Scatter(
            x=df_timeline['date'],
            y=df_timeline['mention_count'],
            mode='lines+markers',
            name='メンション数',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10, color='#667eea'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>メンション数: %{y}<extra></extra>'
        ))

        fig_timeline.update_layout(
            title="メンション数推移（過去4週間）",
            xaxis_title="日付",
            yaxis_title="メンション数",
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        # 参照順位推移
        st.markdown("### 参照順位推移")

        fig_rank = go.Figure()

        fig_rank.add_trace(go.Scatter(
            x=df_timeline['date'],
            y=df_timeline['reference_rank'],
            mode='lines+markers',
            name='参照順位',
            line=dict(color='#f5576c', width=3),
            marker=dict(size=10, color='#f5576c'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>順位: %{y}位<extra></extra>'
        ))

        fig_rank.update_layout(
            title="参照順位推移（数値が小さいほど上位）",
            xaxis_title="日付",
            yaxis_title="参照順位",
            yaxis=dict(autorange='reversed'),
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )

        st.plotly_chart(fig_rank, use_container_width=True)

    with tab2:
        st.markdown("## センチメント分析")
        st.markdown("AIによる言及のポジティブ度を分析します。")
        st.markdown("")

        # ゲージチャート
        sentiment_score = current_status.get('sentiment_score', 0)
        sentiment_percentage = (sentiment_score + 1) * 50  # -1〜1を0〜100に変換

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "センチメントスコア", 'font': {'size': 24}},
            delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': '#ffcdd2'},
                    {'range': [33, 67], 'color': '#fff9c4'},
                    {'range': [67, 100], 'color': '#c8e6c9'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))

        fig_gauge.update_layout(
            height=400,
            font={'color': "darkblue", 'family': "Noto Sans JP"}
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

        # センチメント推移
        st.markdown("### センチメント推移")

        fig_sentiment = go.Figure()

        fig_sentiment.add_trace(go.Scatter(
            x=df_timeline['date'],
            y=df_timeline['sentiment_score'],
            mode='lines+markers',
            name='センチメント',
            line=dict(color='#38ef7d', width=3),
            marker=dict(size=10, color='#38ef7d'),
            fill='tozeroy',
            fillcolor='rgba(56, 239, 125, 0.2)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>スコア: %{y:.2f}<extra></extra>'
        ))

        fig_sentiment.update_layout(
            title="センチメントスコア推移（-1.0〜1.0）",
            xaxis_title="日付",
            yaxis_title="センチメントスコア",
            yaxis=dict(range=[-1, 1]),
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )

        # 基準線
        fig_sentiment.add_shape(
            type="line",
            x0=df_timeline['date'].min(), y0=0, x1=df_timeline['date'].max(), y1=0,
            line=dict(color="gray", width=1, dash="dash")
        )

        st.plotly_chart(fig_sentiment, use_container_width=True)

    with tab3:
        st.markdown("## 最新引用一覧")
        st.markdown("直近の引用状況とコンテキストを確認します。")
        st.markdown("")

        if recent_citations:
            for citation in recent_citations:
                entity_name = citation.get('entity_name', '')
                query_text = citation.get('query_text', '')
                sentiment_score = citation.get('sentiment_score', 0)
                reference_type = citation.get('reference_type', '')
                reference_rank = citation.get('reference_rank', '不明')
                context_snippet = citation.get('context_snippet', '')
                source_url = citation.get('source_url', '')
                created_at = citation.get('created_at', '')

                # センチメント判定
                if sentiment_score >= 0.5:
                    sentiment_class = "sentiment-positive"
                    sentiment_label = "ポジティブ"
                elif sentiment_score >= 0:
                    sentiment_class = "sentiment-neutral"
                    sentiment_label = "中立"
                else:
                    sentiment_class = "sentiment-negative"
                    sentiment_label = "ネガティブ"

                created_datetime = datetime.fromisoformat(created_at)

                st.markdown(f"""
                <div class='citation-card'>
                    <div style='margin-bottom: 0.5rem;'>
                        <strong style='font-size: 1.1rem;'>{query_text}</strong>
                        <span style='float: right; color: #666;'>{created_datetime.strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                    <div style='margin: 0.5rem 0;'>
                        <span style='background: #667eea; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;'>{reference_type}</span>
                        <span style='margin-left: 0.5rem; color: #666;'>順位: {reference_rank}位</span>
                        <span class='{sentiment_class}' style='margin-left: 0.5rem;'>{sentiment_label} ({sentiment_score:.2f})</span>
                    </div>
                    <div style='color: #333; margin: 0.8rem 0; font-style: italic; border-left: 3px solid #667eea; padding-left: 1rem;'>
                        "{context_snippet}"
                    </div>
                    <div style='color: #666; font-size: 0.85rem;'>
                        参照元: <a href='{source_url}' target='_blank' style='color: #667eea;'>{source_url}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("引用データがまだありません。")

    with tab4:
        st.markdown("## 統計サマリー")

        col_stat1, col_stat2 = st.columns(2)

        with col_stat1:
            st.markdown("### センチメント分布")
            sentiment_dist = echo_data.get('sentiment_distribution', {})

            fig_sentiment_dist = go.Figure(data=[
                go.Pie(
                    labels=['ポジティブ', '中立', 'ネガティブ'],
                    values=[sentiment_dist.get('positive', 0), sentiment_dist.get('neutral', 0), sentiment_dist.get('negative', 0)],
                    marker=dict(colors=['#4CAF50', '#FF9800', '#F44336']),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>件数: %{value}<br>割合: %{percent}<extra></extra>'
                )
            ])

            fig_sentiment_dist.update_layout(height=300, showlegend=False)

            st.plotly_chart(fig_sentiment_dist, use_container_width=True)

        with col_stat2:
            st.markdown("### 参照順位分布")
            rank_dist = echo_data.get('reference_rank_distribution', {})

            fig_rank_dist = go.Figure(data=[
                go.Bar(
                    x=['トップ3', 'トップ5', 'トップ10'],
                    y=[rank_dist.get('top_3', 0), rank_dist.get('top_5', 0), rank_dist.get('top_10', 0)],
                    marker=dict(color=['#4CAF50', '#FF9800', '#2196F3']),
                    text=[rank_dist.get('top_3', 0), rank_dist.get('top_5', 0), rank_dist.get('top_10', 0)],
                    textposition='auto'
                )
            ])

            fig_rank_dist.update_layout(
                yaxis_title="引用件数",
                height=300,
                showlegend=False
            )

            st.plotly_chart(fig_rank_dist, use_container_width=True)

        # 成功基準の確認
        st.markdown("---")
        st.markdown("### エコー成功の定義")

        success_criteria = [
            ("配信から72時間以内に3つ以上のLLMで引用される", active_llms >= 3),
            ("センチメントスコアが0.5以上", sentiment_score >= 0.5),
            ("参照順位がトップ5以内", reference_rank <= 5 if reference_rank != '圏外' else False)
        ]

        for criteria, met in success_criteria:
            icon = "✅" if met else "⚠️"
            st.markdown(f"{icon} {criteria}")

else:
    st.error("エコー監視データが見つかりません。デモモードを有効化してください。")
    st.info("環境変数 `DEMO_MODE=true` を設定してください。")

# フッター
st.markdown("---")
st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

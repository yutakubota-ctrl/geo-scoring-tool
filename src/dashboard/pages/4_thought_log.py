"""
思考ログ画面（Gem_01専用）

ChatGPT o1の7ステップ推論プロセスを可視化
- ステップバイステップの表示（折りたたみ可能）
- 参照URL一覧（クリック可能リンク）
- タイムライン形式での推論フロー
"""
import streamlit as st
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(page_title="思考ログ - GEOスコアリング", layout="wide", initial_sidebar_state="expanded")

# カスタムCSS - モダンなデザイン
st.markdown("""
<style>
    .step-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .step-description {
        font-size: 0.95rem;
        line-height: 1.6;
        opacity: 0.95;
    }
    .confidence-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    .url-link {
        color: #4FC3F7;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }
    .url-link:hover {
        color: #29B6F6;
        text-decoration: underline;
    }
    .brand-mention-positive {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .brand-mention-neutral {
        background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);
    }
    .brand-mention-negative {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .timeline-connector {
        border-left: 3px solid #667eea;
        height: 30px;
        margin-left: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("思考ログ")
st.markdown("ChatGPT o1の推論プロセスを7ステップで可視化")
st.markdown("---")

# デモモードの確認
demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

def load_thought_log_data():
    """思考ログデータを読み込み"""
    if demo_mode:
        demo_file = project_root / "data" / "demo" / "thought_log_sample.json"
        with open(demo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # TODO: 本番環境ではデータベースから取得
        return None

# データ読み込み
thought_log = load_thought_log_data()

if thought_log:
    # ヘッダー情報
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### クエリ: {thought_log['query_text']}")

    with col2:
        st.markdown(f"**モデル**: {thought_log['llm_model']}")

    with col3:
        executed_time = datetime.fromisoformat(thought_log['executed_at'])
        st.markdown(f"**実行日時**: {executed_time.strftime('%Y-%m-%d %H:%M')}")

    st.markdown("---")

    # タブ構成
    tab1, tab2, tab3, tab4 = st.tabs(["7ステップ推論", "参照URL", "検索クエリ", "ブランド評価"])

    with tab1:
        st.markdown("## 推論プロセスタイムライン")
        st.markdown("AIが最終判断に至るまでの思考の流れを段階的に表示します。")
        st.markdown("")

        thought_trace = thought_log.get('thought_trace', {})

        for i in range(1, 8):
            step_key = f"step_{i}"
            if step_key in thought_trace:
                step = thought_trace[step_key]

                # ステップカード
                with st.expander(f"**ステップ {i}: {step.get('title', 'タイトルなし')}**", expanded=(i <= 3)):
                    st.markdown(f"<div class='step-card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='step-title'>ステップ {i}: {step.get('title', '')}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='step-description'>{step.get('description', '')}</div>", unsafe_allow_html=True)

                    # 信頼度スコア
                    if 'confidence' in step:
                        confidence = step['confidence'] * 100
                        st.markdown(f"<div class='confidence-badge'>信頼度: {confidence:.0f}%</div>", unsafe_allow_html=True)

                    # 参照URL
                    if 'urls' in step:
                        st.markdown("**参照した情報源:**")
                        for url in step['urls']:
                            st.markdown(f"- <a href='{url}' target='_blank' class='url-link'>{url}</a>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                # タイムライン接続線（最後以外）
                if i < 7:
                    st.markdown("<div class='timeline-connector'></div>", unsafe_allow_html=True)

        # 最終判断
        st.markdown("---")
        st.markdown("## 最終判断")
        st.info(thought_log.get('final_reasoning', '最終判断が記録されていません'))

    with tab2:
        st.markdown("## 参照URL一覧")
        st.markdown("AIが情報収集に使用したWebページの一覧です。")
        st.markdown("")

        selected_urls = thought_log.get('selected_urls', [])

        if selected_urls:
            for idx, url in enumerate(selected_urls, 1):
                col_idx, col_url = st.columns([0.5, 9.5])
                with col_idx:
                    st.markdown(f"**{idx}**")
                with col_url:
                    st.markdown(f"<a href='{url}' target='_blank' class='url-link'>{url}</a>", unsafe_allow_html=True)
        else:
            st.warning("参照URLが記録されていません")

    with tab3:
        st.markdown("## 検索クエリ候補")
        st.markdown("AIが内部的に実行した検索クエリの一覧です。")
        st.markdown("")

        search_queries = thought_log.get('search_queries_used', [])

        if search_queries:
            for idx, query in enumerate(search_queries, 1):
                st.markdown(f"{idx}. **{query}**")
        else:
            st.warning("検索クエリが記録されていません")

    with tab4:
        st.markdown("## ブランド言及状況")
        st.markdown("各ブランドの推薦順位と理由を分析します。")
        st.markdown("")

        brand_mentions = thought_log.get('brand_mentions', {})

        if brand_mentions:
            # 言及されたブランドと言及されなかったブランドを分離
            mentioned = []
            not_mentioned = []

            for brand_name, info in brand_mentions.items():
                if info.get('mentioned', False):
                    mentioned.append((brand_name, info))
                else:
                    not_mentioned.append((brand_name, info))

            # ポジション順にソート
            mentioned.sort(key=lambda x: x[1].get('position', 999))

            # 言及されたブランド
            if mentioned:
                st.markdown("### 推薦されたブランド")
                for brand_name, info in mentioned:
                    sentiment = info.get('sentiment', 'neutral')
                    position = info.get('position', '不明')
                    reasoning = info.get('reasoning', '理由が記録されていません')

                    card_class = f"brand-mention-{sentiment}"

                    with st.container():
                        st.markdown(f"""
                        <div class='step-card {card_class}'>
                            <div class='step-title'>
                                {position}位: {brand_name}
                                <span style='float: right; opacity: 0.8;'>感情: {sentiment}</span>
                            </div>
                            <div class='step-description'>{reasoning}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # 言及されなかったブランド
            if not_mentioned:
                st.markdown("---")
                st.markdown("### 推薦されなかったブランド")
                for brand_name, info in not_mentioned:
                    reasoning = info.get('reasoning', '理由が記録されていません')

                    st.warning(f"**{brand_name}**: {reasoning}")
        else:
            st.warning("ブランド言及データが記録されていません")

else:
    st.error("思考ログデータが見つかりません。デモモードを有効化してください。")
    st.info("環境変数 `DEMO_MODE=true` を設定してください。")

# フッター
st.markdown("---")
st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

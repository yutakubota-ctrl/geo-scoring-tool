"""
AEOインスパイア ビジュアルコンポーネント

AEO戦略資料（https://fde-aeo-strategy.vercel.app/）のデザイン要素を
GEOスコアリングダッシュボードに適用するためのコンポーネント集。

デザインシステム v3.0対応
- common.pyから統一カラーパレットを使用
- ダークスレート背景 (#020617)
- ライムグリーンアクセント (#deff9a)
- ガラスモーフィズム、多層シャドウ
"""

import plotly.graph_objects as go
from typing import Dict, List, Optional

# common.pyから統一カラーパレットをインポート
from src.dashboard.styles.common import (
    COLORS,
    COLORS_AEO,
    PLOTLY_COLORS,
    PLOTLY_COLORS_AEO,
    get_icon,
    get_plotly_layout
)


# ================================
# CSS定義
# ================================
def get_aeo_css() -> str:
    """AEOスタイルのCSSを返す（common.pyの拡張）"""
    return f'''
<style>
    /* ================================
       KPIカード（Before/After形式）
       ================================ */
    .kpi-card-aeo {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}

    .kpi-card-aeo:hover {{
        border-color: {COLORS["border_accent"]};
        box-shadow: 0 0 20px rgba(222, 255, 154, 0.1);
    }}

    .kpi-card-aeo::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top right, rgba(222, 255, 154, 0.04), transparent 70%);
        pointer-events: none;
    }}

    .kpi-label-aeo {{
        font-size: 0.75rem;
        color: {COLORS["text_muted"]};
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
    }}

    .kpi-before-after {{
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        margin-bottom: 0.25rem;
    }}

    .kpi-before {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.25rem;
        color: {COLORS["text_muted"]};
        text-decoration: line-through;
        opacity: 0.7;
    }}

    .kpi-arrow {{
        font-size: 1rem;
        color: {COLORS["text_muted"]};
    }}

    .kpi-after {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS["text_primary"]};
    }}

    .kpi-delta-aeo {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }}

    .kpi-delta-positive {{
        color: {COLORS["accent"]};
    }}

    .kpi-delta-negative {{
        color: {COLORS["danger"]};
    }}

    .kpi-progress-bar {{
        height: 6px;
        background: {COLORS["card_elevated"]};
        border-radius: 3px;
        margin-top: 1rem;
        overflow: hidden;
    }}

    .kpi-progress-fill {{
        height: 100%;
        background: {COLORS["gradient_accent"]};
        border-radius: 3px;
        transition: width 0.5s ease-out;
    }}

    /* ================================
       タイムライン（ガントチャート風）
       ================================ */
    .timeline-container-aeo {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 16px;
        padding: 1.5rem;
    }}

    .timeline-phase {{
        margin-bottom: 2rem;
    }}

    .timeline-phase:last-child {{
        margin-bottom: 0;
    }}

    .phase-header {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }}

    .phase-badge {{
        background: {COLORS["accent"]};
        color: {COLORS["text_inverse"]};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .phase-title {{
        color: {COLORS["text_primary"]};
        font-size: 1.125rem;
        font-weight: 600;
    }}

    .month-grid {{
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 2px;
        margin-bottom: 0.5rem;
        padding-left: 140px;
    }}

    .month-cell {{
        text-align: center;
        font-size: 0.7rem;
        color: {COLORS["text_muted"]};
        padding: 0.25rem 0;
    }}

    .task-row {{
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }}

    .task-name {{
        width: 140px;
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        padding-right: 1rem;
        flex-shrink: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .task-bar-container {{
        flex: 1;
        height: 24px;
        background: {COLORS["card_elevated"]};
        border-radius: 4px;
        position: relative;
    }}

    .task-bar {{
        position: absolute;
        height: 100%;
        border-radius: 4px;
        transition: all 0.3s ease;
    }}

    .task-bar.status-completed {{
        background: linear-gradient(90deg, {COLORS["success"]}, #86efac);
    }}

    .task-bar.status-in_progress {{
        background: {COLORS["gradient_accent"]};
        animation: pulse-bar 2s infinite;
    }}

    .task-bar.status-pending {{
        background: {COLORS["border"]};
    }}

    @keyframes pulse-bar {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    /* ================================
       SOVチャートカード
       ================================ */
    .sov-card-aeo {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 16px;
        padding: 1.5rem;
    }}

    .sov-header {{
        margin-bottom: 1rem;
    }}

    .sov-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
    }}

    .sov-subtitle {{
        font-size: 0.875rem;
        color: {COLORS["text_muted"]};
        margin-top: 0.25rem;
    }}

    .sov-position {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid {COLORS["border"]};
    }}

    .sov-rank {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS["accent"]};
        font-family: 'JetBrains Mono', monospace;
    }}

    .sov-change {{
        font-size: 0.875rem;
    }}

    .sov-change-positive {{
        color: {COLORS["success"]};
    }}

    .sov-change-negative {{
        color: {COLORS["danger"]};
    }}

    /* ================================
       プロセスステップ（AEOスタイル）
       ================================ */
    .process-step-aeo {{
        border-left: 4px solid {COLORS["accent"]};
        background: {COLORS["card_elevated"]};
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 0 12px 12px 0;
        position: relative;
    }}

    .process-step-aeo::before {{
        content: attr(data-step);
        position: absolute;
        left: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 36px;
        height: 36px;
        background: {COLORS["accent"]};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 700;
        color: {COLORS["text_inverse"]};
    }}

    .process-step-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .process-step-description {{
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
    }}
</style>
'''


# ================================
# コンポーネント関数
# ================================

def render_before_after_kpi(
    before: float,
    after: float,
    label: str,
    unit: str = "pt",
    max_value: float = 100,
    show_progress: bool = True
) -> str:
    """Before/After形式のKPIカードを生成

    Args:
        before: 変更前の値
        after: 変更後の値（現在値）
        label: ラベル名
        unit: 単位（pt, %, 件 など）
        max_value: 最大値（プログレスバー用）
        show_progress: プログレスバーを表示するか

    Returns:
        HTML文字列
    """
    delta = after - before
    delta_sign = "+" if delta >= 0 else ""
    delta_class = "kpi-delta-positive" if delta >= 0 else "kpi-delta-negative"
    progress_pct = min((after / max_value) * 100, 100)

    # SVGアイコン
    icon_name = "arrow_up" if delta >= 0 else "arrow_down"
    icon_color = COLORS["success"] if delta >= 0 else COLORS["danger"]
    icon_svg = get_icon(icon_name, size=16, color=icon_color)

    progress_html = ""
    if show_progress:
        progress_html = f'''
        <div class="kpi-progress-bar">
            <div class="kpi-progress-fill" style="width: {progress_pct}%;"></div>
        </div>
        '''

    return f'''
    <div class="kpi-card-aeo">
        <div class="kpi-label-aeo">{label}</div>
        <div class="kpi-before-after">
            <span class="kpi-before">{before:.0f}</span>
            <span class="kpi-arrow">{icon_svg}</span>
            <span class="kpi-after">{after:.0f}</span>
        </div>
        <div class="kpi-delta-aeo {delta_class}">
            {delta_sign}{delta:.0f}{unit}
        </div>
        {progress_html}
    </div>
    '''


def render_engine_scores(scores: Dict[str, Dict[str, float]]) -> go.Figure:
    """エンジン別スコアの横棒グラフを生成

    Args:
        scores: エンジン名をキー、current/previousを値とする辞書
            例: {
                "ChatGPT": {"current": 78, "previous": 66},
                "Claude": {"current": 65, "previous": 68},
                "Gemini": {"current": 72, "previous": 64},
                "Perplexity": {"current": 82, "previous": 67},
            }

    Returns:
        Plotly Figure
    """
    engines = list(scores.keys())
    current_scores = [scores[e]["current"] for e in engines]
    previous_scores = [scores[e]["previous"] for e in engines]
    deltas = [c - p for c, p in zip(current_scores, previous_scores)]

    # 色の決定（変化に応じて）
    colors = [
        COLORS["accent"] if d >= 0 else COLORS["danger"]
        for d in deltas
    ]

    fig = go.Figure()

    # 現在のスコア（メインバー）
    fig.add_trace(go.Bar(
        y=engines[::-1],
        x=current_scores[::-1],
        orientation='h',
        marker=dict(
            color=colors[::-1],
            line=dict(width=0),
            cornerradius=8
        ),
        text=[f"{s} ({'+' if d >= 0 else ''}{d})"
              for s, d in zip(current_scores[::-1], deltas[::-1])],
        textposition='inside',
        textfont=dict(
            color=COLORS["text_inverse"],
            size=13,
            family="'JetBrains Mono', monospace"
        ),
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Current: %{x}<br>'
            'Previous: %{customdata[0]}<br>'
            'Change: %{customdata[1]:+.0f}<extra></extra>'
        ),
        customdata=list(zip(previous_scores[::-1], deltas[::-1]))
    ))

    # 前回スコア（マーカー）
    fig.add_trace(go.Scatter(
        y=engines[::-1],
        x=previous_scores[::-1],
        mode='markers',
        marker=dict(
            symbol='line-ns-open',
            size=20,
            line=dict(width=2, color=COLORS["text_muted"]),
            color='rgba(0,0,0,0)'
        ),
        name='前回',
        hoverinfo='skip'
    ))

    layout = get_plotly_layout("", height=min(80 + len(engines) * 50, 400))
    layout.update({
        "margin": dict(l=100, r=40, t=10, b=40),
        "xaxis": dict(
            range=[0, 100],
            gridcolor='rgba(148, 163, 184, 0.1)',
            zeroline=False,
            tickfont=dict(size=11, color=COLORS["text_muted"]),
            title=dict(
                text='スコア',
                font=dict(size=11, color=COLORS["text_muted"])
            )
        ),
        "yaxis": dict(
            tickfont=dict(size=13, color=COLORS["text_primary"]),
        ),
        "showlegend": False,
        "bargap": 0.3
    })
    fig.update_layout(**layout)

    return fig


def render_sov_chart(
    market_data: Dict[str, float],
    category: str = "推薦カテゴリ",
    own_brand_key: str = "自社"
) -> go.Figure:
    """SOV（Share of Voice）チャートを生成

    Args:
        market_data: ブランド名をキー、シェア（%）を値とする辞書
            例: {
                "自社": 32,
                "競合A": 18,
                "競合B": 15,
                "競合C": 12,
                "その他": 23
            }
        category: カテゴリ名
        own_brand_key: 自社ブランドのキー名

    Returns:
        Plotly Figure
    """
    brands = list(market_data.keys())
    shares = list(market_data.values())

    # 色の割り当て（自社のみアクセントカラー）
    colors = []
    for i, brand in enumerate(brands):
        if brand == own_brand_key:
            colors.append(COLORS["accent"])
        else:
            # グレースケールで段階的に薄く
            opacity = max(0.3, 0.8 - i * 0.12)
            colors.append(f"rgba(148, 163, 184, {opacity})")

    fig = go.Figure()

    cumulative = 0
    for brand, share, color in zip(brands, shares, colors):
        text_color = COLORS["text_inverse"] if brand == own_brand_key else COLORS["text_primary"]

        fig.add_trace(go.Bar(
            name=brand,
            x=[share],
            y=[category],
            orientation='h',
            marker=dict(
                color=color,
                line=dict(width=0)
            ),
            text=f"{brand}<br>{share}%" if share >= 10 else f"{share}%",
            textposition='inside',
            textfont=dict(
                size=11 if share >= 15 else 9,
                color=text_color,
                family="'Noto Sans JP', sans-serif"
            ),
            hovertemplate=f'<b>{brand}</b><br>シェア: {share}%<extra></extra>',
            base=cumulative
        ))
        cumulative += share

    layout = get_plotly_layout("", height=100)
    layout.update({
        "barmode": 'stack',
        "margin": dict(l=20, r=20, t=10, b=10),
        "xaxis": dict(
            range=[0, 100],
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        "yaxis": dict(
            showticklabels=False
        ),
        "showlegend": False,
        "bargap": 0
    })
    fig.update_layout(**layout)

    return fig


def render_progress_timeline(months_data: List[Dict]) -> str:
    """段階的進捗タイムラインを生成

    Args:
        months_data: フェーズごとのタスクデータ
            [
                {
                    "phase": "Phase 1",
                    "title": "基盤構築",
                    "tasks": [
                        {"name": "技術SEO監査", "start": 1, "end": 2, "status": "completed"},
                        {"name": "コンテンツ最適化", "start": 2, "end": 4, "status": "in_progress"},
                        {"name": "E-E-A-T強化", "start": 3, "end": 5, "status": "pending"},
                    ]
                },
                ...
            ]

    Returns:
        HTML文字列
    """
    html = '<div class="timeline-container-aeo">'

    for phase_data in months_data:
        html += f'''
        <div class="timeline-phase">
            <div class="phase-header">
                <span class="phase-badge">{phase_data["phase"]}</span>
                <span class="phase-title">{phase_data["title"]}</span>
            </div>
            <div class="month-grid">
                {''.join([f'<div class="month-cell">M{i}</div>' for i in range(1, 13)])}
            </div>
            <div class="timeline-bars">
        '''

        for task in phase_data.get("tasks", []):
            status_class = f"status-{task.get('status', 'pending')}"
            start = task.get("start", 1)
            end = task.get("end", start)

            # 位置とサイズの計算（12ヶ月基準）
            left_pct = (start - 1) / 12 * 100
            width_pct = max((end - start + 1) / 12 * 100, 8.33)  # 最小1ヶ月分

            html += f'''
                <div class="task-row">
                    <div class="task-name" title="{task.get('name', '')}">{task.get('name', '')}</div>
                    <div class="task-bar-container">
                        <div class="task-bar {status_class}"
                             style="left: {left_pct}%; width: {width_pct}%;">
                        </div>
                    </div>
                </div>
            '''

        html += '''
            </div>
        </div>
        '''

    html += '</div>'
    return html


def render_sov_card(
    market_data: Dict[str, float],
    category: str,
    rank: int,
    change: float,
    own_brand_key: str = "自社"
) -> str:
    """SOVカード全体を生成（チャート + 順位表示）

    Args:
        market_data: シェアデータ
        category: カテゴリ名
        rank: 現在の順位
        change: 前回からの変化（%ポイント）
        own_brand_key: 自社ブランドのキー名

    Returns:
        HTML文字列
    """
    change_sign = "+" if change >= 0 else ""
    change_class = "sov-change-positive" if change >= 0 else "sov-change-negative"
    icon_name = "arrow_up" if change >= 0 else "arrow_down"
    icon_color = COLORS["success"] if change >= 0 else COLORS["danger"]
    icon_svg = get_icon(icon_name, size=14, color=icon_color)

    return f'''
    <div class="sov-card-aeo">
        <div class="sov-header">
            <div class="sov-title">Share of Voice</div>
            <div class="sov-subtitle">{category}</div>
        </div>
        <div id="sov-chart-placeholder"></div>
        <div class="sov-position">
            <div class="sov-rank">#{rank}</div>
            <div class="sov-change {change_class}">
                {icon_svg} {change_sign}{change}% vs 前月
            </div>
        </div>
    </div>
    '''


def get_plotly_layout_aeo(title: str = "", height: int = 400) -> dict:
    """AEOスタイルのPlotlyレイアウト設定を返す（common.pyの関数を使用）"""
    return get_plotly_layout(title, height)


# ================================
# デモ用サンプルデータ
# ================================

DEMO_ENGINE_SCORES = {
    "ChatGPT": {"current": 78, "previous": 66},
    "Claude": {"current": 65, "previous": 68},
    "Gemini": {"current": 72, "previous": 64},
    "Perplexity": {"current": 82, "previous": 67},
}

DEMO_SOV_DATA = {
    "自社": 32,
    "競合A": 18,
    "競合B": 15,
    "競合C": 12,
    "その他": 23,
}

DEMO_TIMELINE_DATA = [
    {
        "phase": "Phase 1",
        "title": "基盤構築",
        "tasks": [
            {"name": "技術SEO監査", "start": 1, "end": 2, "status": "completed"},
            {"name": "コンテンツ最適化", "start": 2, "end": 4, "status": "in_progress"},
            {"name": "E-E-A-T強化", "start": 3, "end": 5, "status": "pending"},
        ]
    },
    {
        "phase": "Phase 2",
        "title": "拡大",
        "tasks": [
            {"name": "FAQ拡充", "start": 4, "end": 6, "status": "pending"},
            {"name": "外部リンク施策", "start": 5, "end": 8, "status": "pending"},
        ]
    },
    {
        "phase": "Phase 3",
        "title": "維持・最適化",
        "tasks": [
            {"name": "継続モニタリング", "start": 8, "end": 12, "status": "pending"},
            {"name": "年間レビュー", "start": 11, "end": 12, "status": "pending"},
        ]
    },
]

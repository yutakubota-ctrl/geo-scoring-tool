"""
GEOスコアリング ダッシュボード共通スタイル

デザインシステム:
- カラーパレット: ダークネイビー基調 + ブルーアクセント
- タイポグラフィ: IBM Plex Sans (見出し), Noto Sans JP (本文)
- 余白: 8pxグリッドシステム
- 角丸: 12px (カード), 8px (ボタン)
"""

# ================================
# カラーパレット
# ================================
COLORS = {
    # 基本色
    "primary": "#0F172A",      # ダークネイビー（メイン）
    "secondary": "#3B82F6",    # ブライトブルー（アクセント）
    "accent": "#10B981",       # エメラルドグリーン（成功）
    "warning": "#F59E0B",      # アンバー（警告）
    "danger": "#EF4444",       # レッド（エラー）

    # 背景色
    "bg_primary": "#F8FAFC",   # 淡いグレー（メイン背景）
    "bg_surface": "#FFFFFF",   # 白（カード背景）
    "bg_dark": "#1E293B",      # ダークグレー（ダーク要素）

    # テキスト色
    "text_primary": "#1E293B",    # メインテキスト
    "text_secondary": "#64748B",  # サブテキスト
    "text_muted": "#94A3B8",      # ミュートテキスト
    "text_inverse": "#FFFFFF",    # 反転テキスト

    # グラデーション
    "gradient_primary": "linear-gradient(135deg, #0F172A 0%, #1E40AF 100%)",
    "gradient_success": "linear-gradient(135deg, #059669 0%, #10B981 100%)",
    "gradient_warning": "linear-gradient(135deg, #D97706 0%, #F59E0B 100%)",
    "gradient_danger": "linear-gradient(135deg, #DC2626 0%, #EF4444 100%)",
    "gradient_info": "linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)",

    # チャート用カラー（区別しやすい6色）
    "chart_1": "#3B82F6",  # ブルー
    "chart_2": "#10B981",  # グリーン
    "chart_3": "#F59E0B",  # アンバー
    "chart_4": "#EF4444",  # レッド
    "chart_5": "#8B5CF6",  # パープル
    "chart_6": "#EC4899",  # ピンク
}

# Plotly用カラーパレット
PLOTLY_COLORS = [
    COLORS["chart_1"],
    COLORS["chart_2"],
    COLORS["chart_3"],
    COLORS["chart_4"],
    COLORS["chart_5"],
    COLORS["chart_6"],
]

# ================================
# タイポグラフィ
# ================================
FONTS = {
    "heading": "'IBM Plex Sans', 'Noto Sans JP', sans-serif",
    "body": "'Noto Sans JP', 'Inter', sans-serif",
    "mono": "'JetBrains Mono', 'Consolas', monospace",
}

# ================================
# 共通CSS
# ================================
def get_common_css():
    """全画面共通のCSSを返す"""
    return f"""
<style>
    /* ================================
       Google Fonts インポート
       ================================ */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ================================
       ルート変数定義
       ================================ */
    :root {{
        --color-primary: {COLORS["primary"]};
        --color-secondary: {COLORS["secondary"]};
        --color-accent: {COLORS["accent"]};
        --color-warning: {COLORS["warning"]};
        --color-danger: {COLORS["danger"]};
        --color-bg-primary: {COLORS["bg_primary"]};
        --color-bg-surface: {COLORS["bg_surface"]};
        --color-text-primary: {COLORS["text_primary"]};
        --color-text-secondary: {COLORS["text_secondary"]};
        --font-heading: {FONTS["heading"]};
        --font-body: {FONTS["body"]};
        --font-mono: {FONTS["mono"]};
    }}

    /* ================================
       Streamlit デフォルトの上書き
       ================================ */
    .stApp {{
        background-color: {COLORS["bg_primary"]};
    }}

    /* メインコンテンツエリア */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    /* ページタイトル */
    h1 {{
        font-family: {FONTS["heading"]};
        font-weight: 700;
        color: {COLORS["primary"]};
        font-size: 2.25rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }}

    h2 {{
        font-family: {FONTS["heading"]};
        font-weight: 600;
        color: {COLORS["text_primary"]};
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }}

    h3 {{
        font-family: {FONTS["heading"]};
        font-weight: 600;
        color: {COLORS["text_primary"]};
        font-size: 1.125rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}

    /* 本文 */
    p, li, span {{
        font-family: {FONTS["body"]};
        color: {COLORS["text_primary"]};
        line-height: 1.6;
    }}

    /* サイドバー */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["primary"]};
    }}

    [data-testid="stSidebar"] * {{
        color: {COLORS["text_inverse"]} !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {COLORS["text_inverse"]} !important;
    }}

    /* ================================
       カスタムコンポーネント
       ================================ */

    /* KPIカード */
    .kpi-card {{
        background: {COLORS["bg_surface"]};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }}

    .kpi-card:hover {{
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }}

    .kpi-card-primary {{
        background: {COLORS["gradient_primary"]};
        color: {COLORS["text_inverse"]};
    }}

    .kpi-card-success {{
        background: {COLORS["gradient_success"]};
        color: {COLORS["text_inverse"]};
    }}

    .kpi-card-warning {{
        background: {COLORS["gradient_warning"]};
        color: {COLORS["text_inverse"]};
    }}

    .kpi-card-danger {{
        background: {COLORS["gradient_danger"]};
        color: {COLORS["text_inverse"]};
    }}

    .kpi-label {{
        font-family: {FONTS["body"]};
        font-size: 0.875rem;
        font-weight: 500;
        opacity: 0.8;
        margin-bottom: 0.25rem;
    }}

    .kpi-value {{
        font-family: {FONTS["mono"]};
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    .kpi-delta {{
        font-family: {FONTS["mono"]};
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }}

    .kpi-delta-positive {{
        color: {COLORS["accent"]};
    }}

    .kpi-delta-negative {{
        color: {COLORS["danger"]};
    }}

    /* ステータスバッジ */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-family: {FONTS["body"]};
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .status-success {{
        background: rgba(16, 185, 129, 0.15);
        color: #059669;
    }}

    .status-warning {{
        background: rgba(245, 158, 11, 0.15);
        color: #D97706;
    }}

    .status-danger {{
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
    }}

    .status-info {{
        background: rgba(59, 130, 246, 0.15);
        color: #2563EB;
    }}

    /* データカード */
    .data-card {{
        background: {COLORS["bg_surface"]};
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border-left: 4px solid {COLORS["secondary"]};
        transition: all 0.2s ease;
    }}

    .data-card:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left-color: {COLORS["primary"]};
    }}

    .data-card-title {{
        font-family: {FONTS["heading"]};
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .data-card-content {{
        font-family: {FONTS["body"]};
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.5;
    }}

    /* タイムラインコンポーネント */
    .timeline-step {{
        display: flex;
        align-items: flex-start;
        margin-bottom: 0;
    }}

    .timeline-indicator {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-right: 1rem;
    }}

    .timeline-dot {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: {COLORS["gradient_primary"]};
        display: flex;
        align-items: center;
        justify-content: center;
        color: {COLORS["text_inverse"]};
        font-family: {FONTS["mono"]};
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
    }}

    .timeline-line {{
        width: 2px;
        height: 60px;
        background: linear-gradient(to bottom, {COLORS["secondary"]}, transparent);
        margin: 0.5rem 0;
    }}

    .timeline-content {{
        flex: 1;
        background: {COLORS["bg_surface"]};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }}

    .timeline-title {{
        font-family: {FONTS["heading"]};
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.25rem;
    }}

    .timeline-description {{
        font-family: {FONTS["body"]};
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
    }}

    /* プログレスリング（信頼度表示用） */
    .progress-ring {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: conic-gradient(
            {COLORS["secondary"]} var(--progress),
            {COLORS["bg_primary"]} var(--progress)
        );
        position: relative;
    }}

    .progress-ring::after {{
        content: attr(data-value);
        position: absolute;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: {COLORS["bg_surface"]};
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: {FONTS["mono"]};
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
    }}

    /* セクションディバイダー */
    .section-divider {{
        height: 1px;
        background: linear-gradient(to right, transparent, {COLORS["text_muted"]}, transparent);
        margin: 2rem 0;
    }}

    /* ナビゲーションカード（ホーム用） */
    .nav-card {{
        background: {COLORS["bg_surface"]};
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
        cursor: pointer;
    }}

    .nav-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
        border-color: {COLORS["secondary"]};
    }}

    .nav-card-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }}

    .nav-card-title {{
        font-family: {FONTS["heading"]};
        font-size: 1.125rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .nav-card-description {{
        font-family: {FONTS["body"]};
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
    }}

    /* テーブルスタイリング */
    .styled-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: {FONTS["body"]};
    }}

    .styled-table th {{
        background: {COLORS["primary"]};
        color: {COLORS["text_inverse"]};
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
    }}

    .styled-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        font-size: 0.875rem;
    }}

    .styled-table tr:nth-child(even) {{
        background: {COLORS["bg_primary"]};
    }}

    .styled-table tr:hover {{
        background: rgba(59, 130, 246, 0.05);
    }}

    /* URLリンク */
    .url-link {{
        color: {COLORS["secondary"]};
        text-decoration: none;
        font-family: {FONTS["body"]};
        font-size: 0.875rem;
        transition: color 0.2s ease;
    }}

    .url-link:hover {{
        color: {COLORS["primary"]};
        text-decoration: underline;
    }}

    /* フッター */
    .page-footer {{
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
        text-align: center;
    }}

    .page-footer-text {{
        font-family: {FONTS["body"]};
        font-size: 0.75rem;
        color: {COLORS["text_muted"]};
    }}

    /* アニメーション */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .animate-fade-in {{
        animation: fadeIn 0.3s ease-out forwards;
    }}

    /* レスポンシブ調整 */
    @media (max-width: 768px) {{
        .kpi-value {{
            font-size: 1.75rem;
        }}

        h1 {{
            font-size: 1.75rem;
        }}

        h2 {{
            font-size: 1.25rem;
        }}
    }}
</style>
"""


def get_page_header(title: str, subtitle: str = "") -> str:
    """ページヘッダーHTMLを返す"""
    subtitle_html = f"<p style='color: {COLORS['text_secondary']}; font-size: 1rem; margin-top: 0.25rem;'>{subtitle}</p>" if subtitle else ""
    return f"""
<div style="margin-bottom: 2rem;">
    <h1 style="margin-bottom: 0;">{title}</h1>
    {subtitle_html}
</div>
"""


def get_kpi_card(label: str, value: str, delta: str = None, variant: str = "default") -> str:
    """KPIカードHTMLを返す

    Args:
        label: カードラベル
        value: メイン値
        delta: 変化量（オプション）
        variant: "default", "primary", "success", "warning", "danger"
    """
    variant_class = f"kpi-card-{variant}" if variant != "default" else ""

    delta_html = ""
    if delta:
        delta_class = "kpi-delta-positive" if delta.startswith("+") else "kpi-delta-negative"
        delta_html = f"<div class='kpi-delta {delta_class}'>{delta}</div>"

    return f"""
<div class="kpi-card {variant_class}">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    {delta_html}
</div>
"""


def get_status_badge(text: str, status: str = "info") -> str:
    """ステータスバッジHTMLを返す

    Args:
        text: バッジテキスト
        status: "success", "warning", "danger", "info"
    """
    return f'<span class="status-badge status-{status}">{text}</span>'


def get_data_card(title: str, content: str, border_color: str = None) -> str:
    """データカードHTMLを返す"""
    style = f"border-left-color: {border_color};" if border_color else ""
    return f"""
<div class="data-card" style="{style}">
    <div class="data-card-title">{title}</div>
    <div class="data-card-content">{content}</div>
</div>
"""


def get_timeline_step(step_number: int, title: str, description: str, is_last: bool = False) -> str:
    """タイムラインステップHTMLを返す"""
    line_html = "" if is_last else '<div class="timeline-line"></div>'
    return f"""
<div class="timeline-step">
    <div class="timeline-indicator">
        <div class="timeline-dot">{step_number}</div>
        {line_html}
    </div>
    <div class="timeline-content">
        <div class="timeline-title">{title}</div>
        <div class="timeline-description">{description}</div>
    </div>
</div>
"""


def get_section_divider() -> str:
    """セクションディバイダーHTMLを返す"""
    return '<div class="section-divider"></div>'


def get_page_footer(text: str) -> str:
    """ページフッターHTMLを返す"""
    return f"""
<div class="page-footer">
    <span class="page-footer-text">{text}</span>
</div>
"""


# ================================
# Plotlyレイアウト設定
# ================================
def get_plotly_layout(title: str = "", height: int = 400) -> dict:
    """Plotlyグラフ用の統一レイアウト設定を返す"""
    return {
        "title": {
            "text": title,
            "font": {
                "family": FONTS["heading"],
                "size": 16,
                "color": COLORS["text_primary"]
            },
            "x": 0,
            "xanchor": "left"
        },
        "font": {
            "family": FONTS["body"],
            "color": COLORS["text_primary"]
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "height": height,
        "margin": {"l": 40, "r": 20, "t": 60, "b": 40},
        "xaxis": {
            "gridcolor": "rgba(0,0,0,0.05)",
            "zerolinecolor": "rgba(0,0,0,0.1)",
            "title_font": {"size": 12, "color": COLORS["text_secondary"]}
        },
        "yaxis": {
            "gridcolor": "rgba(0,0,0,0.05)",
            "zerolinecolor": "rgba(0,0,0,0.1)",
            "title_font": {"size": 12, "color": COLORS["text_secondary"]}
        },
        "legend": {
            "font": {"size": 12},
            "bgcolor": "rgba(255,255,255,0.8)",
            "bordercolor": "rgba(0,0,0,0.1)",
            "borderwidth": 1
        },
        "hoverlabel": {
            "bgcolor": COLORS["bg_surface"],
            "bordercolor": COLORS["text_muted"],
            "font": {"family": FONTS["body"], "size": 12}
        }
    }


def get_gauge_colors() -> list:
    """ゲージチャート用の色リストを返す"""
    return [
        {"range": [0, 33], "color": "rgba(239, 68, 68, 0.2)"},
        {"range": [33, 67], "color": "rgba(245, 158, 11, 0.2)"},
        {"range": [67, 100], "color": "rgba(16, 185, 129, 0.2)"}
    ]

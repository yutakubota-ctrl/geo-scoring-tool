"""
GEOスコアリング ダッシュボード共通スタイル

デザインシステム v3.0 - AEO Premium Dark Theme

配色: ダークスレート基調 + ライムグリーン/スカイブルーアクセント
タイポグラフィ: IBM Plex Sans (見出し), Noto Sans JP (本文), JetBrains Mono (数値)
特徴: ガラスモーフィズム、多層シャドウ、マイクロインタラクション
"""

# ================================
# SVGアイコン定義（絵文字置換用）
# ================================
ICONS = {
    "chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>''',
    "trend": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>''',
    "data": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>''',
    "brain": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.54Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.54Z"></path></svg>''',
    "map": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>''',
    "eye": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>''',
    "message": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>''',
    "target": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>''',
    "check": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>''',
    "alert_triangle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>''',
    "zap": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>''',
    "check_circle": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>''',
    "arrow_up": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>''',
    "arrow_down": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>''',
    "activity": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>''',
    "layers": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>''',
}

def get_icon(name: str, size: int = 24, color: str = "currentColor") -> str:
    """SVGアイコンを取得

    Args:
        name: アイコン名 (chart, trend, data, brain, map, eye, message, target, check, alert_triangle, zap, check_circle, arrow_up, arrow_down, activity, layers)
        size: アイコンサイズ（px）
        color: アイコン色

    Returns:
        SVG文字列
    """
    icon_svg = ICONS.get(name, ICONS["chart"])
    # サイズと色を置換
    icon_svg = icon_svg.replace('width="24"', f'width="{size}"')
    icon_svg = icon_svg.replace('height="24"', f'height="{size}"')
    icon_svg = icon_svg.replace('width="16"', f'width="{size}"')
    icon_svg = icon_svg.replace('height="16"', f'height="{size}"')
    if color != "currentColor":
        icon_svg = icon_svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return icon_svg


# ================================
# AEOカラーパレット（Primary）
# ================================
COLORS = {
    # 背景系（ダークモード基調）
    "background": "#020617",      # Very Dark Slate (メイン背景)
    "card": "#0f172a",            # Slate 900 (カード背景)
    "card_elevated": "#1e293b",   # Slate 800 (ホバー/アクティブ)
    "card_glass": "rgba(15, 23, 42, 0.8)",  # ガラスモーフィズム用

    # ボーダー系
    "border": "#334155",          # Slate 700 (通常ボーダー)
    "border_light": "rgba(255, 255, 255, 0.1)",  # 微細ボーダー
    "border_accent": "rgba(222, 255, 154, 0.3)",  # アクセントボーダー

    # プライマリカラー（従来との互換性）
    "primary": "#0f172a",         # ダークネイビー（メイン）
    "secondary": "#38bdf8",       # スカイブルー（アクセント）

    # アクセント（高コントラスト）
    "accent": "#deff9a",          # Lime Green (主要アクセント)
    "accent_primary": "#deff9a",  # Lime Green (主要アクセント)
    "accent_secondary": "#38bdf8", # Sky Blue (補助アクセント)
    "accent_tertiary": "#a78bfa",  # Purple (第三アクセント)

    # ステータス
    "success": "#4ade80",         # Green 400
    "warning": "#fbbf24",         # Amber 400
    "danger": "#f43f5e",          # Rose 500
    "error": "#f43f5e",           # Rose 500

    # テキスト（ダークモード用）
    "text_primary": "#f8fafc",    # Slate 50 (見出し)
    "text_secondary": "#cbd5e1",  # Slate 400 (本文)
    "text_muted": "#94a3b8",      # Slate 500 (サブテキスト)
    "text_inverse": "#020617",    # 反転テキスト
    "text_accent": "#deff9a",     # Lime (強調テキスト)

    # 旧カラー（互換性用）
    "bg_primary": "#020617",
    "bg_surface": "#0f172a",
    "bg_dark": "#020617",

    # グラデーション
    "gradient_primary": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
    "gradient_accent": "linear-gradient(90deg, #deff9a 0%, #38bdf8 100%)",
    "gradient_glow": "radial-gradient(circle, rgba(222, 255, 154, 0.06), transparent 70%)",
    "gradient_success": "linear-gradient(135deg, #059669 0%, #4ade80 100%)",
    "gradient_warning": "linear-gradient(135deg, #d97706 0%, #fbbf24 100%)",
    "gradient_danger": "linear-gradient(135deg, #dc2626 0%, #f43f5e 100%)",
    "gradient_info": "linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)",

    # チャート用カラー
    "chart_1": "#deff9a",  # ライムグリーン
    "chart_2": "#38bdf8",  # スカイブルー
    "chart_3": "#a78bfa",  # パープル
    "chart_4": "#4ade80",  # グリーン
    "chart_5": "#fbbf24",  # アンバー
    "chart_6": "#f43f5e",  # ローズ
}

# AEOカラーパレット（エイリアス）
COLORS_AEO = COLORS

# Plotly用カラーパレット
PLOTLY_COLORS = [
    COLORS["chart_1"],
    COLORS["chart_2"],
    COLORS["chart_3"],
    COLORS["chart_4"],
    COLORS["chart_5"],
    COLORS["chart_6"],
]

PLOTLY_COLORS_AEO = PLOTLY_COLORS

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
    """全画面共通のCSSを返す（AEO Premium Dark Theme）"""
    return f"""
<style>
    /* ================================
       Google Fonts インポート
       ================================ */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;900&family=Noto+Sans+JP:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* ================================
       CSS変数定義
       ================================ */
    :root {{
        /* カラーパレット */
        --color-bg-base: {COLORS["background"]};
        --color-bg-card: {COLORS["card"]};
        --color-bg-elevated: {COLORS["card_elevated"]};
        --color-border: {COLORS["border"]};
        --color-border-light: {COLORS["border_light"]};
        --color-accent: {COLORS["accent"]};
        --color-accent-secondary: {COLORS["accent_secondary"]};
        --color-accent-tertiary: {COLORS["accent_tertiary"]};
        --color-success: {COLORS["success"]};
        --color-warning: {COLORS["warning"]};
        --color-danger: {COLORS["danger"]};
        --color-text-primary: {COLORS["text_primary"]};
        --color-text-secondary: {COLORS["text_secondary"]};
        --color-text-muted: {COLORS["text_muted"]};

        /* フォント */
        --font-heading: {FONTS["heading"]};
        --font-body: {FONTS["body"]};
        --font-mono: {FONTS["mono"]};

        /* スペーシング（8px基準） */
        --space-1: 8px;
        --space-2: 16px;
        --space-3: 24px;
        --space-4: 32px;
        --space-6: 48px;

        /* 角丸 */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;

        /* シャドウ */
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.4), 0 4px 6px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 20px rgba(222, 255, 154, 0.15);
    }}

    /* ================================
       Streamlit デフォルトの上書き
       ================================ */
    .stApp {{
        background: {COLORS["background"]};
        background-image: radial-gradient(circle at 50% 0%, rgba(222, 255, 154, 0.03) 0%, transparent 50%);
    }}

    /* メインコンテンツエリア */
    .main .block-container {{
        padding-top: var(--space-4);
        padding-bottom: var(--space-4);
        max-width: 1400px;
    }}

    /* スクロールバー */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {COLORS["background"]};
    }}

    ::-webkit-scrollbar-thumb {{
        background: {COLORS["border"]};
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS["accent_secondary"]};
    }}

    /* ================================
       タイポグラフィ
       ================================ */
    h1 {{
        font-family: var(--font-heading);
        font-weight: 900;
        color: {COLORS["text_primary"]};
        font-size: 2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}

    h2 {{
        font-family: var(--font-heading);
        font-weight: 700;
        color: {COLORS["text_primary"]};
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }}

    h3 {{
        font-family: var(--font-heading);
        font-weight: 600;
        color: {COLORS["text_primary"]};
        font-size: 1.125rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }}

    p, li, span, div {{
        font-family: var(--font-body);
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
    }}

    /* 数値表示用 */
    .mono-value {{
        font-family: var(--font-mono);
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    /* ================================
       サイドバー
       ================================ */
    [data-testid="stSidebar"] {{
        background: {COLORS["card"]};
        border-right: 1px solid {COLORS["border"]};
    }}

    [data-testid="stSidebar"] * {{
        color: {COLORS["text_secondary"]} !important;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {COLORS["text_primary"]} !important;
    }}

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {{
        color: {COLORS["text_muted"]} !important;
    }}

    /* ================================
       フォーム要素
       ================================ */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: {COLORS["card_elevated"]} !important;
        border: 1px solid {COLORS["border"]} !important;
        border-radius: var(--radius-sm) !important;
        color: {COLORS["text_primary"]} !important;
    }}

    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {{
        border-color: {COLORS["accent_secondary"]} !important;
    }}

    .stCheckbox label span {{
        color: {COLORS["text_secondary"]} !important;
    }}

    /* ================================
       ガラスモーフィズムカード
       ================================ */
    .glass-card {{
        background: {COLORS["card_glass"]};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {COLORS["border_light"]};
        border-radius: var(--radius-lg);
        padding: var(--space-3);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .glass-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: {COLORS["gradient_glow"]};
        pointer-events: none;
    }}

    .glass-card:hover {{
        border-color: {COLORS["border_accent"]};
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }}

    /* ================================
       KPIカード
       ================================ */
    .kpi-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: var(--radius-lg);
        padding: var(--space-3);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: {COLORS["gradient_glow"]};
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    }}

    .kpi-card:hover {{
        border-color: {COLORS["border_accent"]};
        transform: translateY(-2px) scale(1.02);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }}

    .kpi-card:hover::before {{
        opacity: 1;
    }}

    .kpi-card-primary {{
        background: {COLORS["gradient_primary"]};
        border-color: {COLORS["border_accent"]};
    }}

    .kpi-card-primary::before {{
        background: radial-gradient(circle at top right, rgba(222, 255, 154, 0.08), transparent 60%);
        opacity: 1;
    }}

    .kpi-card-success {{
        background: {COLORS["gradient_success"]};
    }}

    .kpi-card-warning {{
        background: {COLORS["gradient_warning"]};
    }}

    .kpi-card-danger {{
        background: {COLORS["gradient_danger"]};
    }}

    .kpi-label {{
        font-family: var(--font-body);
        font-size: 0.75rem;
        font-weight: 500;
        color: {COLORS["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }}

    .kpi-value {{
        font-family: var(--font-mono);
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        line-height: 1.1;
    }}

    .kpi-delta {{
        font-family: var(--font-mono);
        font-size: 0.875rem;
        font-weight: 600;
        margin-top: 0.5rem;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }}

    .kpi-delta-positive {{
        color: {COLORS["success"]};
    }}

    .kpi-delta-negative {{
        color: {COLORS["danger"]};
    }}

    /* プログレスバー */
    .kpi-progress {{
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
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* ================================
       ステータスバッジ
       ================================ */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-family: var(--font-body);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .status-success {{
        background: rgba(74, 222, 128, 0.15);
        color: {COLORS["success"]};
        border: 1px solid rgba(74, 222, 128, 0.3);
    }}

    .status-warning {{
        background: rgba(251, 191, 36, 0.15);
        color: {COLORS["warning"]};
        border: 1px solid rgba(251, 191, 36, 0.3);
    }}

    .status-danger {{
        background: rgba(244, 63, 94, 0.15);
        color: {COLORS["danger"]};
        border: 1px solid rgba(244, 63, 94, 0.3);
    }}

    .status-info {{
        background: rgba(56, 189, 248, 0.15);
        color: {COLORS["accent_secondary"]};
        border: 1px solid rgba(56, 189, 248, 0.3);
    }}

    .status-accent {{
        background: rgba(222, 255, 154, 0.15);
        color: {COLORS["accent"]};
        border: 1px solid rgba(222, 255, 154, 0.3);
    }}

    /* ================================
       データカード
       ================================ */
    .data-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: var(--radius-md);
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid {COLORS["accent_secondary"]};
        transition: all 0.3s ease;
    }}

    .data-card:hover {{
        border-color: {COLORS["border_accent"]};
        border-left-color: {COLORS["accent"]};
        box-shadow: var(--shadow-md);
        transform: translateX(4px);
    }}

    .data-card-title {{
        font-family: var(--font-heading);
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .data-card-content {{
        font-family: var(--font-body);
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
    }}

    /* ================================
       ナビゲーションカード
       ================================ */
    .nav-card {{
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: var(--radius-lg);
        padding: var(--space-3);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}

    .nav-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: {COLORS["gradient_glow"]};
        opacity: 0;
        transition: opacity 0.3s ease;
    }}

    .nav-card:hover {{
        transform: translateY(-4px) scale(1.02);
        border-color: {COLORS["accent"]};
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }}

    .nav-card:hover::before {{
        opacity: 1;
    }}

    .nav-card-icon {{
        width: 48px;
        height: 48px;
        margin: 0 auto 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        background: {COLORS["gradient_accent"]};
        border-radius: var(--radius-md);
        color: {COLORS["text_inverse"]};
    }}

    .nav-card-title {{
        font-family: var(--font-heading);
        font-size: 1.125rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.5rem;
    }}

    .nav-card-description {{
        font-family: var(--font-body);
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.5;
    }}

    /* ================================
       タイムラインコンポーネント
       ================================ */
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
        background: {COLORS["gradient_accent"]};
        display: flex;
        align-items: center;
        justify-content: center;
        color: {COLORS["text_inverse"]};
        font-family: var(--font-mono);
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
    }}

    .timeline-line {{
        width: 2px;
        height: 60px;
        background: linear-gradient(to bottom, {COLORS["accent"]}, transparent);
        margin: 0.5rem 0;
    }}

    .timeline-content {{
        flex: 1;
        background: {COLORS["card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: var(--radius-md);
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }}

    .timeline-title {{
        font-family: var(--font-heading);
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin-bottom: 0.25rem;
    }}

    .timeline-description {{
        font-family: var(--font-body);
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
        line-height: 1.6;
    }}

    /* ================================
       アラートカード
       ================================ */
    .alert-card {{
        background: {COLORS["card"]};
        border-radius: var(--radius-sm);
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        position: relative;
        overflow: hidden;
    }}

    .alert-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        opacity: 0.1;
        pointer-events: none;
    }}

    .alert-danger {{
        border-left-color: {COLORS["danger"]};
    }}

    .alert-danger::before {{
        background: {COLORS["danger"]};
    }}

    .alert-warning {{
        border-left-color: {COLORS["warning"]};
    }}

    .alert-warning::before {{
        background: {COLORS["warning"]};
    }}

    .alert-success {{
        border-left-color: {COLORS["success"]};
    }}

    .alert-success::before {{
        background: {COLORS["success"]};
    }}

    .alert-title {{
        font-family: var(--font-heading);
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .alert-description {{
        font-size: 0.8rem;
        color: {COLORS["text_secondary"]};
    }}

    /* ================================
       テーブルスタイリング
       ================================ */
    .styled-table {{
        width: 100%;
        border-collapse: collapse;
        font-family: var(--font-body);
    }}

    .styled-table th {{
        background: {COLORS["card_elevated"]};
        color: {COLORS["text_primary"]};
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        border-bottom: 1px solid {COLORS["border"]};
    }}

    .styled-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid {COLORS["border"]};
        font-size: 0.875rem;
        color: {COLORS["text_secondary"]};
    }}

    .styled-table tr:hover {{
        background: rgba(56, 189, 248, 0.05);
    }}

    /* ================================
       セクションディバイダー
       ================================ */
    .section-divider {{
        height: 1px;
        background: linear-gradient(to right, transparent, {COLORS["border"]}, transparent);
        margin: 2rem 0;
    }}

    /* ================================
       フッター
       ================================ */
    .page-footer {{
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid {COLORS["border"]};
        text-align: center;
    }}

    .page-footer-text {{
        font-family: var(--font-body);
        font-size: 0.75rem;
        color: {COLORS["text_muted"]};
    }}

    /* ================================
       アニメーション
       ================================ */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    .animate-fade-in {{
        animation: fadeIn 0.4s ease-out forwards;
    }}

    .animate-pulse {{
        animation: pulse 2s infinite;
    }}

    /* ================================
       レスポンシブ調整
       ================================ */
    @media (max-width: 768px) {{
        .kpi-value {{
            font-size: 1.75rem;
        }}

        h1 {{
            font-size: 1.5rem;
        }}

        h2 {{
            font-size: 1.25rem;
        }}

        .nav-card {{
            padding: var(--space-2);
        }}
    }}
</style>
"""


def get_page_header(title: str, subtitle: str = "") -> str:
    """ページヘッダーHTMLを返す"""
    subtitle_html = f"<p style='color: {COLORS['text_secondary']}; font-size: 1rem; margin-top: 0.25rem;'>{subtitle}</p>" if subtitle else ""
    return f"""
<div style="margin-bottom: 2rem;">
    <h1 style="margin-bottom: 0; color: {COLORS['text_primary']};">{title}</h1>
    {subtitle_html}
</div>
"""


def get_kpi_card(label: str, value: str, delta: str = None, variant: str = "default", icon: str = None) -> str:
    """KPIカードHTMLを返す

    Args:
        label: カードラベル
        value: メイン値
        delta: 変化量（オプション）
        variant: "default", "primary", "success", "warning", "danger"
        icon: アイコン名（オプション）
    """
    variant_class = f"kpi-card-{variant}" if variant != "default" else ""

    icon_html = ""
    if icon:
        icon_svg = get_icon(icon, size=20, color=COLORS["text_muted"])
        icon_html = f'<div style="margin-bottom: 0.5rem;">{icon_svg}</div>'

    delta_html = ""
    if delta:
        is_positive = delta.startswith("+")
        delta_class = "kpi-delta-positive" if is_positive else "kpi-delta-negative"
        arrow_icon = get_icon("arrow_up" if is_positive else "arrow_down", size=14)
        delta_html = f"<div class='kpi-delta {delta_class}'>{arrow_icon} {delta}</div>"

    return f"""
<div class="kpi-card {variant_class}">
    {icon_html}
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    {delta_html}
</div>
"""


def get_status_badge(text: str, status: str = "info") -> str:
    """ステータスバッジHTMLを返す

    Args:
        text: バッジテキスト
        status: "success", "warning", "danger", "info", "accent"
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


def get_alert_card(title: str, description: str, alert_type: str = "warning", icon: str = None) -> str:
    """アラートカードHTMLを返す

    Args:
        title: アラートタイトル
        description: 説明文
        alert_type: "danger", "warning", "success"
        icon: アイコン名（オプション）
    """
    icon_name = icon or ("alert_triangle" if alert_type == "danger" else "zap" if alert_type == "warning" else "check_circle")
    icon_color = COLORS["danger"] if alert_type == "danger" else COLORS["warning"] if alert_type == "warning" else COLORS["success"]
    icon_svg = get_icon(icon_name, size=18, color=icon_color)

    return f"""
<div class="alert-card alert-{alert_type}">
    <div class="alert-title" style="color: {icon_color};">
        {icon_svg} {title}
    </div>
    <div class="alert-description">{description}</div>
</div>
"""


# ================================
# Plotlyレイアウト設定
# ================================
def get_plotly_layout(title: str = "", height: int = 400) -> dict:
    """Plotlyグラフ用の統一レイアウト設定を返す（AEOダークテーマ）"""
    return {
        "title": {
            "text": title,
            "font": {
                "family": FONTS["heading"],
                "size": 14,
                "color": COLORS["text_primary"]
            },
            "x": 0,
            "xanchor": "left"
        },
        "font": {
            "family": FONTS["body"],
            "color": COLORS["text_secondary"]
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "height": height,
        "margin": {"l": 40, "r": 20, "t": 60, "b": 40},
        "xaxis": {
            "gridcolor": "rgba(148, 163, 184, 0.1)",
            "zerolinecolor": "rgba(148, 163, 184, 0.2)",
            "title_font": {"size": 11, "color": COLORS["text_muted"]},
            "tickfont": {"size": 11, "color": COLORS["text_muted"]}
        },
        "yaxis": {
            "gridcolor": "rgba(148, 163, 184, 0.1)",
            "zerolinecolor": "rgba(148, 163, 184, 0.2)",
            "title_font": {"size": 11, "color": COLORS["text_muted"]},
            "tickfont": {"size": 11, "color": COLORS["text_muted"]}
        },
        "legend": {
            "font": {"size": 11, "color": COLORS["text_secondary"]},
            "bgcolor": "rgba(15, 23, 42, 0.9)",
            "bordercolor": COLORS["border"],
            "borderwidth": 1
        },
        "hoverlabel": {
            "bgcolor": COLORS["card"],
            "bordercolor": COLORS["border"],
            "font": {"family": FONTS["body"], "size": 12, "color": COLORS["text_primary"]}
        }
    }


def get_gauge_colors() -> list:
    """ゲージチャート用の色リストを返す"""
    return [
        {"range": [0, 33], "color": "rgba(244, 63, 94, 0.2)"},
        {"range": [33, 67], "color": "rgba(251, 191, 36, 0.2)"},
        {"range": [67, 100], "color": "rgba(74, 222, 128, 0.2)"}
    ]

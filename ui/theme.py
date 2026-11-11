"""
GlucoShield CDSS — Centralized Theme & Design System
Minimal, professional clinical styling. Plotly 7.x compatible.
"""

LIGHT_THEME = {
    "primary": "#1E40AF",
    "primary_light": "#EFF6FF",
    "secondary": "#0F766E",
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "text": "#0F172A",
    "text_muted": "#64748B",
    "border": "#E2E8F0",
    "border_focus": "#94A3B8",
    "risk_low_bg": "#F0FDF4",
    "risk_low_border": "#16A34A",
    "risk_low_text": "#166534",
    "risk_mod_bg": "#FFFBEB",
    "risk_mod_border": "#D97706",
    "risk_mod_text": "#92400E",
    "risk_high_bg": "#FEF2F2",
    "risk_high_border": "#DC2626",
    "risk_high_text": "#991B1B",
    "card_shadow": "0 1px 3px rgba(15,23,42,0.06), 0 0 0 1px rgba(15,23,42,0.04)",
    "brand_bg": "#1E40AF",
    "brand_text": "#FFFFFF",
    "gauge_step_low": "#F0FDF4",
    "gauge_step_mod": "#FFFBEB",
    "gauge_step_high": "#FEF2F2",
}

DARK_THEME = {
    "primary": "#60A5FA",
    "primary_light": "#1E293B",
    "secondary": "#2DD4BF",
    "bg": "#0B1220",
    "surface": "#111827",
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "border": "#1F2937",
    "border_focus": "#374151",
    "risk_low_bg": "#052E16",
    "risk_low_border": "#16A34A",
    "risk_low_text": "#86EFAC",
    "risk_mod_bg": "#451A03",
    "risk_mod_border": "#D97706",
    "risk_mod_text": "#FDE68A",
    "risk_high_bg": "#450A0A",
    "risk_high_border": "#DC2626",
    "risk_high_text": "#FCA5A5",
    "card_shadow": "0 1px 4px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04)",
    "brand_bg": "#2563EB",
    "brand_text": "#FFFFFF",
    "gauge_step_low": "#052E16",
    "gauge_step_mod": "#451A03",
    "gauge_step_high": "#450A0A",
}


def get_theme(dark: bool) -> dict:
    return DARK_THEME if dark else LIGHT_THEME


def inject_global_css(t: dict) -> str:
    """
    Returns clean, professional CSS.
    Targets specific Streamlit data-testid selectors to avoid specificity conflicts.
    Compatible with Streamlit 1.32+ and Plotly 7.x.
    """
    is_dark = t["bg"] != "#F8FAFC"
    input_bg = t["surface"]
    input_text = t["text"]
    # Sidebar link/radio active bg
    nav_active_bg = t["primary_light"]

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   BASE — Page & Background
═══════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main {{
    background-color: {t['bg']};
}}
[data-testid="stAppViewContainer"] > .main .block-container {{
    background-color: {t['bg']};
    color: {t['text']};
    max-width: 1280px;
    padding-top: 0.5rem;
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {t['surface']};
    border-right: 1px solid {t['border']};
}}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{
    color: {t['text']};
}}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY — Explicit overrides to ensure visibility
═══════════════════════════════════════════════════════════════ */
.block-container h1,
.block-container h2,
.block-container h3,
.block-container h4,
.block-container h5,
.block-container h6 {{
    color: {t['text']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-weight: 600;
    letter-spacing: -0.015em;
}}
.block-container p,
.block-container li,
.block-container .stMarkdown {{
    color: {t['text']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}
.stCaption, .block-container small {{
    color: {t['text_muted']};
}}

/* ═══════════════════════════════════════════════════════════════
   FORM INPUTS — Light & Dark visible
═══════════════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea {{
    background-color: {input_bg};
    color: {input_text};
    border-color: {t['border']};
}}
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {{
    color: {t['text']};
    font-size: 0.84rem;
    font-weight: 500;
}}

/* ═══════════════════════════════════════════════════════════════
   METRIC WIDGETS
═══════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 12px 16px;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {t['text']};
}}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
    color: {t['text_muted']};
}}

/* ═══════════════════════════════════════════════════════════════
   DATAFRAME TABLE
═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid {t['border']};
    border-radius: 6px;
}}
[data-testid="stDataFrame"] th {{
    background-color: {'#F1F5F9' if not is_dark else '#1E293B'};
    color: {t['text']};
}}

/* ═══════════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background-color: {t['bg']};
    border-bottom: 1px solid {t['border']};
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    color: {t['text_muted']};
    font-size: 0.86rem;
    font-weight: 500;
    background-color: transparent;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    color: {t['primary']};
    border-bottom: 2px solid {t['primary']};
    font-weight: 600;
}}

/* ═══════════════════════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {{
    border: 1px solid {t['border']};
    border-radius: 6px;
    background-color: {t['surface']};
}}
[data-testid="stExpander"] summary {{
    color: {t['text']};
    font-weight: 500;
}}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════ */
[data-testid="stButton"] > button {{
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.84rem;
    border: 1px solid {t['border']};
    background-color: {t['surface']};
    color: {t['text']};
    transition: border-color 0.15s, background-color 0.15s;
}}
[data-testid="stButton"] > button:hover {{
    border-color: {t['primary']};
    color: {t['primary']};
}}
[data-testid="stButton"] > button[kind="primary"] {{
    background-color: {t['primary']};
    color: #FFFFFF;
    border-color: {t['primary']};
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{
    background-color: {'#1D4ED8' if not is_dark else '#3B82F6'};
    color: #FFFFFF;
}}

/* ═══════════════════════════════════════════════════════════════
   ALERTS / CALLOUTS
═══════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    border-radius: 6px;
}}

/* ═══════════════════════════════════════════════════════════════
   CODE BLOCKS
═══════════════════════════════════════════════════════════════ */
[data-testid="stCode"] {{
    background-color: {'#F1F5F9' if not is_dark else '#1E293B'};
    border: 1px solid {t['border']};
    border-radius: 6px;
}}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES (defined inline in app.py)
═══════════════════════════════════════════════════════════════ */

/* App Header */
.gs-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    background-color: {t['surface']};
    border-bottom: 1px solid {t['border']};
    padding: 13px 22px;
    margin: -1rem -1rem 1.4rem -1rem;
    box-shadow: {t['card_shadow']};
}}
.gs-brand-mark {{
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 6px;
    background-color: {t['brand_bg']};
    color: {t['brand_text']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.88rem;
    letter-spacing: 0.03em;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.gs-title h1 {{
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: {t['text']} !important;
    margin: 0 !important;
    line-height: 1.25 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}
.gs-title p {{
    font-size: 0.78rem;
    color: {t['text_muted']};
    margin: 2px 0 0 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.gs-title {{
    flex: 1;
}}
.gs-badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.gs-badge-sys {{
    background-color: {t['primary_light']};
    color: {t['primary']};
    border: 1px solid {'#BFDBFE' if not is_dark else '#3B82F644'};
}}
.gs-badge-proto {{
    background-color: {'#F1F5F9' if not is_dark else '#374151'};
    color: {t['text_muted']};
    border: 1px solid {t['border']};
}}

/* Notice/Disclaimer Banner */
.gs-disclaimer {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-left: 3px solid {t['primary']};
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 0.82rem;
    color: {t['text_muted']};
    margin-bottom: 1.2rem;
    line-height: 1.55;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.gs-disclaimer strong {{
    color: {t['text']};
}}

/* Section Headers */
.gs-section-title {{
    font-size: 1.0rem;
    font-weight: 600;
    color: {t['text']};
    margin: 1.2rem 0 0.65rem 0;
    padding-bottom: 6px;
    border-bottom: 1px solid {t['border']};
    letter-spacing: -0.01em;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

/* Form Section Labels */
.gs-form-section-title {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['primary']};
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid {t['border']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

/* KPI Cards */
.kpi-card {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-top: 2px solid {t['primary']};
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: {t['card_shadow']};
    height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.kpi-label {{
    font-size: 0.7rem;
    font-weight: 600;
    color: {t['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.kpi-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {t['text']};
    margin: 3px 0;
    letter-spacing: -0.02em;
}}
.kpi-desc {{
    font-size: 0.72rem;
    color: {t['text_muted']};
}}

/* Info Boxes */
.gs-info-box {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 15px 18px;
    margin-bottom: 12px;
    font-size: 0.84rem;
    color: {t['text']};
    line-height: 1.6;
    box-shadow: {t['card_shadow']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.gs-info-box h4 {{
    color: {t['text']};
    font-size: 0.93rem;
    font-weight: 600;
    margin: 0 0 8px 0;
}}
.gs-info-box code {{
    background-color: {'#F1F5F9' if not is_dark else '#1E293B'};
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.82em;
    color: {'#1E40AF' if not is_dark else '#60A5FA'};
}}

/* Risk Result Panels */
.risk-low {{
    background-color: {t['risk_low_bg']};
    border: 1px solid {t['risk_low_border']};
    border-left: 4px solid {t['risk_low_border']};
    border-radius: 8px;
    padding: 18px 20px;
    color: {t['risk_low_text']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.risk-moderate {{
    background-color: {t['risk_mod_bg']};
    border: 1px solid {t['risk_mod_border']};
    border-left: 4px solid {t['risk_mod_border']};
    border-radius: 8px;
    padding: 18px 20px;
    color: {t['risk_mod_text']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.risk-high {{
    background-color: {t['risk_high_bg']};
    border: 1px solid {t['risk_high_border']};
    border-left: 4px solid {t['risk_high_border']};
    border-radius: 8px;
    padding: 18px 20px;
    color: {t['risk_high_text']};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.risk-panel-label {{
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 2px;
}}
.risk-panel-prob {{
    font-size: 2.8rem;
    font-weight: 700;
    line-height: 1;
    margin: 4px 0 8px 0;
    letter-spacing: -0.03em;
}}
.risk-panel-pred {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.pred-positive {{
    background-color: #DC262614;
    color: #DC2626;
    border: 1px solid #DC262640;
}}
.pred-negative {{
    background-color: #16A34A14;
    color: #16A34A;
    border: 1px solid #16A34A40;
}}
.threshold-info {{
    font-size: 0.78rem;
    margin-top: 10px;
    opacity: 0.85;
    line-height: 1.4;
}}

/* Scenario Cards */
.scenario-card {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: {t['card_shadow']};
    height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.scenario-pill {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 8px;
}}
.pill-low  {{ background-color: #DCFCE7; color: #166534; }}
.pill-high {{ background-color: #FEE2E2; color: #991B1B; }}
.pill-border {{ background-color: #FEF3C7; color: #92400E; }}

/* Professional Footer */
.gs-footer {{
    border-top: 1px solid {t['border']};
    padding: 16px 0;
    margin-top: 2.4rem;
    text-align: center;
    font-size: 0.75rem;
    color: {t['text_muted']};
    line-height: 1.8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
</style>
"""

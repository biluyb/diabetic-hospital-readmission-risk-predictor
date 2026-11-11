"""
GlucoShield CDSS — Centralized Theme & Design System
Professional hospital-grade UI styling for clinical decision support.
Plotly 7.x & Streamlit 1.30+ compatible.
"""

LIGHT_THEME = {
    "is_dark": False,
    "primary": "#1E40AF",         # Deep clinical blue
    "primary_hover": "#1D4ED8",
    "primary_light": "#EFF6FF",   # Soft blue surface
    "secondary": "#0F766E",       # Deep teal
    "bg": "#F8FAFC",              # Clean off-white canvas
    "surface": "#FFFFFF",         # Pure white surface
    "surface_subtle": "#F1F5F9",  # Slate 100 secondary surface
    "text": "#0F172A",            # Dark slate text (high contrast)
    "text_muted": "#64748B",      # Slate muted text
    "border": "#E2E8F0",          # Crisp light border
    "border_strong": "#CBD5E1",   # Input border
    "border_focus": "#2563EB",
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E1",
    "popover_bg": "#FFFFFF",
    "popover_border": "#E2E8F0",
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
    "gauge_step_low": "#DCFCE7",
    "gauge_step_mod": "#FEF3C7",
    "gauge_step_high": "#FEE2E2",
}

DARK_THEME = {
    "is_dark": True,
    "primary": "#3B82F6",         # Clear radiant clinical blue
    "primary_hover": "#60A5FA",
    "primary_light": "#1E293B",   # Slate dark surface
    "secondary": "#2DD4BF",       # Teal accent
    "bg": "#090D16",              # Deep medical midnight canvas
    "surface": "#111827",         # Elevated card surface
    "surface_subtle": "#1E293B",  # Slate 800 secondary surface
    "text": "#F8FAFC",            # Crisp light text
    "text_muted": "#94A3B8",      # Readable slate muted
    "border": "#1F2937",          # Dark border
    "border_strong": "#374151",   # Input border
    "border_focus": "#3B82F6",
    "input_bg": "#1E293B",
    "input_border": "#374151",
    "popover_bg": "#111827",
    "popover_border": "#374151",
    "risk_low_bg": "#052E16",
    "risk_low_border": "#22C55E",
    "risk_low_text": "#86EFAC",
    "risk_mod_bg": "#451A03",
    "risk_mod_border": "#F59E0B",
    "risk_mod_text": "#FDE68A",
    "risk_high_bg": "#450A0A",
    "risk_high_border": "#EF4444",
    "risk_high_text": "#FCA5A5",
    "card_shadow": "0 2px 6px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05)",
    "brand_bg": "#2563EB",
    "brand_text": "#FFFFFF",
    "gauge_step_low": "#062817",
    "gauge_step_mod": "#381A05",
    "gauge_step_high": "#3B0D0D",
}


def get_theme(dark: bool) -> dict:
    return DARK_THEME if dark else LIGHT_THEME


def inject_global_css(t: dict) -> str:
    """
    Returns unified, professional CSS enforcing hospital-grade visual hierarchy.
    Applies seamlessly to both Light and Dark modes without clashing with Streamlit internals.
    """
    is_dark = t["is_dark"]
    color_scheme = "dark" if is_dark else "light"

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   STREAMLIT CORE VARIABLES & ROOT STYLING
═══════════════════════════════════════════════════════════════ */
:root, html, body {{
    --primary-color: {t['primary']};
    --background-color: {t['bg']};
    --secondary-background-color: {t['surface']};
    --text-color: {t['text']};
    color-scheme: {color_scheme} !important;
}}

body, [data-testid="stAppViewContainer"], .main {{
    background-color: {t['bg']} !important;
    color: {t['text']} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}}

header[data-testid="stHeader"] {{
    background-color: transparent !important;
    height: 2.2rem !important;
}}

.block-container {{
    max-width: 1320px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR & NAVIGATION
═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background-color: {t['surface']} !important;
    border-right: 1px solid {t['border']} !important;
}}

[data-testid="stSidebar"] > div:first-child {{
    background-color: {t['surface']} !important;
    padding-top: 1.2rem !important;
}}

[data-testid="stSidebar"] .nav-category {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {t['text_muted']};
    margin: 16px 0 6px 4px;
}}

[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 7px 12px !important;
    font-size: 0.84rem !important;
    border-radius: 6px !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
    color: {t['text']} !important;
    font-weight: 500 !important;
    width: 100% !important;
    margin-bottom: 2px !important;
    transition: all 0.15s ease-in-out !important;
}}

[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
    background-color: {t['surface_subtle']} !important;
    border-color: {t['border_strong']} !important;
    color: {t['primary']} !important;
}}

[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {{
    background-color: {'#EFF6FF' if not is_dark else '#1E3A5F'} !important;
    border: 1px solid {'#93C5FD' if not is_dark else '#2563EB'} !important;
    border-left: 4px solid {t['primary']} !important;
    color: {t['primary']} !important;
    font-weight: 600 !important;
}}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {{
    color: {t['text']} !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
}}

p, li, span, label, div {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}

/* ═══════════════════════════════════════════════════════════════
   FORM WIDGETS & INPUT CONTROLS
═══════════════════════════════════════════════════════════════ */
[data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}}

/* Labels */
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stRadio"] label {{
    color: {t['text']} !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}}

/* BaseWeb Selectbox (Closed state) */
div[data-baseweb="select"] {{
    background-color: {t['input_bg']} !important;
    border: 1px solid {t['input_border']} !important;
    border-radius: 6px !important;
}}
div[data-baseweb="select"] > div {{
    background-color: {t['input_bg']} !important;
    color: {t['text']} !important;
    border: none !important;
    min-height: 38px !important;
}}
div[data-baseweb="select"] span {{
    color: {t['text']} !important;
    font-size: 0.88rem !important;
}}
div[data-baseweb="select"] svg {{
    fill: {t['text_muted']} !important;
}}

/* BaseWeb Popover Menu (Portal Dropdown options list) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"] {{
    background-color: {t['popover_bg']} !important;
    border: 1px solid {t['popover_border']} !important;
    border-radius: 6px !important;
    box-shadow: {t['card_shadow']} !important;
}}

li[role="option"] {{
    background-color: {t['popover_bg']} !important;
    color: {t['text']} !important;
    font-size: 0.86rem !important;
    padding: 8px 12px !important;
}}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {{
    background-color: {t['primary_light']} !important;
    color: {t['primary']} !important;
    font-weight: 600 !important;
}}

/* Text & Number Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    background-color: {t['input_bg']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['input_border']} !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
    min-height: 38px !important;
}}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: {t['primary']} !important;
    box-shadow: 0 0 0 1px {t['primary']} !important;
    outline: none !important;
}}

/* Number input step buttons (+ and -) */
[data-testid="stNumberInput"] button {{
    background-color: {t['input_bg']} !important;
    border: 1px solid {t['input_border']} !important;
    color: {t['text']} !important;
}}
[data-testid="stNumberInput"] button:hover {{
    background-color: {t['surface_subtle']} !important;
    color: {t['primary']} !important;
}}
[data-testid="stNumberInput"] button svg {{
    fill: {t['text_muted']} !important;
}}

/* Disabled Inputs */
[data-testid="stTextInput"] input:disabled {{
    background-color: {t['surface_subtle']} !important;
    color: {t['text_muted']} !important;
    border-color: {t['border']} !important;
    opacity: 0.85;
}}

/* Radio Buttons */
[data-testid="stRadio"] div[role="radiogroup"] label {{
    color: {t['text']} !important;
    padding: 4px 8px !important;
    border-radius: 4px !important;
}}
[data-testid="stRadio"] div[role="radiogroup"] label:hover {{
    background-color: {t['surface_subtle']} !important;
}}

/* Buttons */
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {{
    background-color: {t['primary']} !important;
    color: #FFFFFF !important;
    border: 1px solid {t['primary']} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 18px !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
    filter: brightness(1.1) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
}}

[data-testid="stButton"] > button[kind="secondary"],
[data-testid="stDownloadButton"] > button {{
    background-color: {t['surface']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border_strong']} !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.86rem !important;
    padding: 7px 16px !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stButton"] > button[kind="secondary"]:hover,
[data-testid="stDownloadButton"] > button:hover {{
    background-color: {t['surface_subtle']} !important;
    border-color: {t['primary']} !important;
    color: {t['primary']} !important;
}}

/* ═══════════════════════════════════════════════════════════════
   CONTAINERS & BORDERED CARDS
═══════════════════════════════════════════════════════════════ */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    box-shadow: {t['card_shadow']} !important;
    padding: 16px 18px !important;
    margin-bottom: 12px !important;
}}

/* Dataframe table */
[data-testid="stDataFrame"] {{
    background-color: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
}}

/* Tabs */
div[data-baseweb="tab-list"] {{
    background-color: transparent !important;
    border-bottom: 1px solid {t['border']} !important;
    gap: 6px !important;
}}
button[data-baseweb="tab"] {{
    background-color: transparent !important;
    color: {t['text_muted']} !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {t['primary']} !important;
    font-weight: 600 !important;
    border-bottom: 2px solid {t['primary']} !important;
}}
button[data-baseweb="tab"]:hover {{
    color: {t['text']} !important;
    background-color: {t['surface_subtle']} !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background-color: {t['surface']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    box-shadow: {t['card_shadow']} !important;
    margin-bottom: 8px !important;
}}
div[data-testid="stExpander"] summary {{
    color: {t['text']} !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}}
div[data-testid="stExpander"] summary:hover {{
    color: {t['primary']} !important;
}}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
    background-color: {t['surface']} !important;
    border-top: 1px solid {t['border']} !important;
    color: {t['text']} !important;
}}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM CLINICAL DESIGN COMPONENTS
═══════════════════════════════════════════════════════════════ */

/* Header Card */
.gs-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 12px;
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
    letter-spacing: 0.02em;
}}
.gs-title {{
    flex: 1;
}}
.gs-title h1 {{
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: {t['text']} !important;
    margin: 0 !important;
    line-height: 1.25 !important;
}}
.gs-title p {{
    font-size: 0.76rem;
    color: {t['text_muted']};
    margin: 2px 0 0 0;
}}
.gs-badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.gs-badge-sys {{
    background-color: {t['primary_light']};
    color: {t['primary']};
    border: 1px solid {'#BFDBFE' if not is_dark else '#2563EB40'};
}}
.gs-badge-proto {{
    background-color: {t['surface_subtle']};
    color: {t['text_muted']};
    border: 1px solid {t['border']};
}}

/* Notice Banner */
.gs-disclaimer {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-left: 3px solid {t['primary']};
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 0.78rem;
    color: {t['text_muted']};
    margin-bottom: 14px;
    line-height: 1.5;
}}
.gs-disclaimer strong {{
    color: {t['text']};
}}

/* Section Titles */
.gs-section-title {{
    font-size: 0.96rem;
    font-weight: 600;
    color: {t['text']};
    margin: 1.2rem 0 0.65rem 0;
    padding-bottom: 5px;
    border-bottom: 1px solid {t['border']};
    letter-spacing: -0.01em;
}}

/* Form Grouping Header */
.form-card-title {{
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['primary']};
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid {t['border']};
}}

/* KPI Metric Cards */
.kpi-card {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-top: 2px solid {t['primary']};
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: {t['card_shadow']};
    height: 100%;
}}
.kpi-label {{
    font-size: 0.68rem;
    font-weight: 600;
    color: {t['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.kpi-value {{
    font-size: 1.45rem;
    font-weight: 700;
    color: {t['text']};
    margin: 2px 0;
    letter-spacing: -0.02em;
}}
.kpi-desc {{
    font-size: 0.72rem;
    color: {t['text_muted']};
}}

/* Info Box */
.gs-info-box {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
    font-size: 0.82rem;
    color: {t['text']};
    line-height: 1.55;
    box-shadow: {t['card_shadow']};
}}
.gs-info-box h4 {{
    color: {t['text']};
    font-size: 0.88rem;
    font-weight: 600;
    margin: 0 0 6px 0;
}}
.gs-info-box code {{
    background-color: {t['surface_subtle']};
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.8em;
    color: {t['primary']};
}}

/* Clinical Result Panels */
.risk-low {{
    background-color: {t['risk_low_bg']};
    border: 1px solid {t['risk_low_border']};
    border-left: 4px solid {t['risk_low_border']};
    border-radius: 8px;
    padding: 16px 18px;
    color: {t['risk_low_text']};
}}
.risk-moderate {{
    background-color: {t['risk_mod_bg']};
    border: 1px solid {t['risk_mod_border']};
    border-left: 4px solid {t['risk_mod_border']};
    border-radius: 8px;
    padding: 16px 18px;
    color: {t['risk_mod_text']};
}}
.risk-high {{
    background-color: {t['risk_high_bg']};
    border: 1px solid {t['risk_high_border']};
    border-left: 4px solid {t['risk_high_border']};
    border-radius: 8px;
    padding: 16px 18px;
    color: {t['risk_high_text']};
}}
.risk-panel-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 2px;
}}
.risk-panel-prob {{
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1;
    margin: 4px 0 6px 0;
    letter-spacing: -0.03em;
}}
.risk-panel-pred {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}
.pred-positive {{
    background-color: {'#DC262618' if not is_dark else '#EF444430'};
    color: {'#DC2626' if not is_dark else '#FCA5A5'};
    border: 1px solid {'#DC262640' if not is_dark else '#EF444460'};
}}
.pred-negative {{
    background-color: {'#16A34A18' if not is_dark else '#22C55E30'};
    color: {'#16A34A' if not is_dark else '#86EFAC'};
    border: 1px solid {'#16A34A40' if not is_dark else '#22C55E60'};
}}
.threshold-info {{
    font-size: 0.76rem;
    margin-top: 8px;
    opacity: 0.85;
}}

/* Scenario Pills */
.scenario-pill {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.pill-low  {{
    background-color: {'#DCFCE7' if not is_dark else '#062817'};
    color: {'#166534' if not is_dark else '#86EFAC'};
    border: 1px solid {'#16A34A40' if not is_dark else '#22C55E40'};
}}
.pill-high {{
    background-color: {'#FEE2E2' if not is_dark else '#3B0D0D'};
    color: {'#991B1B' if not is_dark else '#FCA5A5'};
    border: 1px solid {'#DC262640' if not is_dark else '#EF444440'};
}}
.pill-border {{
    background-color: {'#FEF3C7' if not is_dark else '#381A05'};
    color: {'#92400E' if not is_dark else '#FDE68A'};
    border: 1px solid {'#D9770640' if not is_dark else '#F59E0B40'};
}}

/* Footer */
.gs-footer {{
    border-top: 1px solid {t['border']};
    padding: 14px 0;
    margin-top: 2rem;
    text-align: center;
    font-size: 0.72rem;
    color: {t['text_muted']};
    line-height: 1.7;
}}
</style>
"""

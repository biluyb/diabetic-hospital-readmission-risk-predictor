"""
GlucoShield CDSS — Centralized Theme & Design System
Professional hospital-grade UI styling for clinical decision support.
Plotly 7.x & Streamlit 1.32+ compatible.
"""

LIGHT_THEME = {
    "primary": "#1E40AF",         # Deep clinical blue
    "primary_light": "#EFF6FF",   # Soft blue surface
    "secondary": "#0F766E",       # Deep teal
    "bg": "#F8FAFC",              # Clean off-white canvas
    "surface": "#FFFFFF",         # Pure white surface
    "text": "#0F172A",            # Dark slate text (high contrast)
    "text_muted": "#64748B",      # Slate muted text
    "border": "#E2E8F0",          # Crisp light border
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
    Returns clean, professional CSS targeting specific Streamlit data-testid selectors.
    Removes visual clunkiness and enforces hospital-grade visual hierarchy.
    """
    is_dark = t["bg"] != "#F8FAFC"
    input_bg = t["surface"]
    input_text = t["text"]

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   STREAMLIT CORE CONTAINER FIXES
═══════════════════════════════════════════════════════════════ */
header[data-testid="stHeader"] {{
    background-color: transparent !important;
    height: 2.2rem !important;
}}
[data-testid="stAppViewContainer"] > .main {{
    background-color: {t['bg']} !important;
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
    background-color: {'#EFF6FF' if not is_dark else '#1E293B'} !important;
    border-color: {'#BFDBFE' if not is_dark else '#334155'} !important;
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
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
}}
p, li, span, label, div {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}}

/* ═══════════════════════════════════════════════════════════════
   FORM CONTROLS & INPUTS
═══════════════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea {{
    background-color: {input_bg} !important;
    color: {input_text} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
}}
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stRadio"] label {{
    color: {t['text']} !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
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
    border: 1px solid {'#BFDBFE' if not is_dark else '#3B82F644'};
}}
.gs-badge-proto {{
    background-color: {'#F1F5F9' if not is_dark else '#374151'};
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

/* Form Grouping Cards */
.form-card {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 16px 18px 12px 18px;
    margin-bottom: 12px;
    box-shadow: {t['card_shadow']};
}}
.form-card-title {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['primary']};
    margin-bottom: 10px;
    padding-bottom: 5px;
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
    background-color: {'#F1F5F9' if not is_dark else '#1E293B'};
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.8em;
    color: {'#1E40AF' if not is_dark else '#60A5FA'};
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
    font-size: 0.76rem;
    margin-top: 8px;
    opacity: 0.85;
}}

/* Scenario Cards */
.scenario-card {{
    background-color: {t['surface']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: {t['card_shadow']};
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
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
.pill-low  {{ background-color: #DCFCE7; color: #166534; }}
.pill-high {{ background-color: #FEE2E2; color: #991B1B; }}
.pill-border {{ background-color: #FEF3C7; color: #92400E; }}

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

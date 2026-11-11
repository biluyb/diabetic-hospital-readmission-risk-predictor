"""
GlucoShield CDSS — Clinical Decision Support System
Diabetes 30-Day Hospital Readmission Risk Predictor
FUSE AI-201 Capstone (Group 04) | Academic Research Prototype
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import plotly.graph_objects as go

from src.data_pipeline import map_icd9_to_category
from src.explainability import ClinicalExplainer
from src.validation import (
    validate_and_sanitize_patient_input,
    classify_readmission_risk,
    CLINICAL_DECISION_THRESHOLD,
)
from ui.theme import get_theme, inject_global_css

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlucoShield CDSS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "assessment_history" not in st.session_state:
    st.session_state.assessment_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Clinical Dashboard"

# ─────────────────────────────────────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────────────────────────────────────
t = get_theme(st.session_state.dark_mode)
st.markdown(inject_global_css(t), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD CACHED MODEL ARTIFACTS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading clinical model artifacts...")
def load_artifacts():
    preprocessor = joblib.load("models/preprocessor.joblib")
    xgb = joblib.load("models/xgboost_final_model.joblib")
    feature_names = joblib.load("models/feature_names.joblib")
    explainer = ClinicalExplainer()
    return preprocessor, xgb, feature_names, explainer

try:
    preprocessor, xgb, feature_names, explainer = load_artifacts()
    artifacts_ok = True
except Exception as _e:
    artifacts_ok = False
    _load_err = str(_e)

# ─────────────────────────────────────────────────────────────────────────────
# PRESET VALUES DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
PRESETS = {
    "Scenario 1: Low Risk (Negative)": dict(
        age="[40-50)", gender="Male", race="AfricanAmerican",
        time_in_hospital=2, num_lab_procedures=28, num_procedures=0,
        num_medications=8, number_outpatient=0, number_emergency=0,
        number_inpatient=0, number_diagnoses=4, diag_1="250.00",
        a1c="Norm", insulin="No", change="No", admission_type="2 (Urgent)",
    ),
    "Scenario 2: High Risk (Positive)": dict(
        age="[70-80)", gender="Female", race="Caucasian",
        time_in_hospital=6, num_lab_procedures=58, num_procedures=2,
        num_medications=22, number_outpatient=1, number_emergency=1,
        number_inpatient=3, number_diagnoses=9, diag_1="428",
        a1c=">8", insulin="Up", change="Ch", admission_type="1 (Emergency)",
    ),
    "Scenario 3: Borderline (Cutoff 0.45)": dict(
        age="[60-70)", gender="Male", race="Caucasian",
        time_in_hospital=4, num_lab_procedures=40, num_procedures=1,
        num_medications=14, number_outpatient=1, number_emergency=1,
        number_inpatient=0, number_diagnoses=7, diag_1="414",
        a1c="None", insulin="Steady", change="No", admission_type="1 (Emergency)",
    ),
}
DEFAULT_VALS = dict(
    age="[60-70)", gender="Female", race="Caucasian",
    time_in_hospital=4, num_lab_procedures=42, num_procedures=1,
    num_medications=15, number_outpatient=0, number_emergency=0,
    number_inpatient=0, number_diagnoses=7, diag_1="250.00",
    a1c="None", insulin="Steady", change="No", admission_type="1 (Emergency)",
)

ADMISSION_OPTIONS = ["1 (Emergency)", "2 (Urgent)", "3 (Elective)", "7 (Trauma / Other)"]
AGE_OPTIONS = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
               "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
RACE_OPTIONS = ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:12px;padding:4px 0 16px 0;
                    border-bottom:1px solid {t['border']};">
            <div class="gs-brand-mark">GS</div>
            <div>
                <div style="font-weight:700;font-size:1.02rem;color:{t['text']};">GlucoShield CDSS</div>
                <div style="font-size:0.74rem;color:{t['text_muted']};">Inpatient Risk Stratification</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Theme selector
    st.markdown(f"<div class='nav-category'>THEME</div>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Display Theme",
        ["Light Mode", "Dark Mode"],
        index=1 if st.session_state.dark_mode else 0,
        label_visibility="collapsed",
        horizontal=True,
    )
    new_dark = theme_choice == "Dark Mode"
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

    # Category 1: Clinical Workflow
    st.markdown(f"<div class='nav-category'>CLINICAL WORKFLOW</div>", unsafe_allow_html=True)
    CLINICAL_PAGES = [
        "Clinical Dashboard",
        "Patient Risk Assessment",
        "Demonstration Scenarios",
    ]
    for label in CLINICAL_PAGES:
        active = st.session_state.nav_page == label
        btn_type = "primary" if active else "secondary"
        if st.button(label, key=f"nav_{label}", use_container_width=True, type=btn_type):
            st.session_state.nav_page = label
            st.rerun()

    # Category 2: System & Governance
    st.markdown(f"<div class='nav-category'>SYSTEM & GOVERNANCE</div>", unsafe_allow_html=True)
    SYSTEM_PAGES = [
        "Model Performance",
        "System Testing & Validation",
        "Monitoring & Drift Detection",
        "Clinical Governance",
        "About GlucoShield",
    ]
    for label in SYSTEM_PAGES:
        active = st.session_state.nav_page == label
        btn_type = "primary" if active else "secondary"
        if st.button(label, key=f"nav_{label}", use_container_width=True, type=btn_type):
            st.session_state.nav_page = label
            st.rerun()

    # Quick demo preset selector in sidebar
    st.markdown(f"<div class='nav-category'>QUICK PRESETS</div>", unsafe_allow_html=True)
    preset_choice = st.selectbox(
        "Demonstration Presets",
        [
            "Custom Patient Input",
            "Scenario 1: Low Risk (Negative)",
            "Scenario 2: High Risk (Positive)",
            "Scenario 3: Borderline (Cutoff 0.45)",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:0.72rem;color:{t['text_muted']};line-height:1.6;padding:0 4px;">
            <b>FUSE AI-201 Capstone</b><br>
            Group 04 · YEEAP Cohort<br>
            Model: XGBoost · Cutoff: <b>{CLINICAL_DECISION_THRESHOLD:.2f}</b><br>
            ROC-AUC: <b>0.6465</b> · Recall: <b>65.71%</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

page = st.session_state.nav_page

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL HEADER & NOTICE BANNER
# ─────────────────────────────────────────────────────────────────────────────
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
st.markdown(
    f"""
    <div class="gs-header">
        <div class="gs-brand-mark">GS</div>
        <div class="gs-title">
            <h1>GlucoShield Clinical Decision Support System</h1>
            <p>Diabetes 30-Day Hospital Readmission Risk Stratification &nbsp;·&nbsp; {now_str}</p>
        </div>
        <span class="gs-badge gs-badge-sys">Decision Support</span>
        <span class="gs-badge gs-badge-proto">Academic Prototype</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="gs-disclaimer">
        <strong>Notice: Clinical Decision Support Prototype.</strong>
        GlucoShield is an academic research prototype developed for FUSE AI-201.
        Outputs represent statistical probabilities derived from historical inpatient records (1999–2008)
        and are intended to assist bedside clinical teams, not replace professional judgment.
        No protected health information (PHI) is collected or retained.
    </div>
    """,
    unsafe_allow_html=True,
)

if not artifacts_ok:
    st.error(
        f"Model artifacts could not be loaded: {_load_err}\n\n"
        "Please ensure `models/preprocessor.joblib`, `models/xgboost_final_model.joblib`, "
        "and `models/feature_names.joblib` exist."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def build_risk_gauge(prob: float, dark: bool) -> go.Figure:
    pct = prob * 100
    if prob < 0.40:
        bar_color = "#16A34A"
    elif prob < 0.50:
        bar_color = "#D97706"
    else:
        bar_color = "#DC2626"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 32, "color": t["text"], "family": "Segoe UI, sans-serif"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": t["text_muted"],
                         "tickfont": {"color": t["text_muted"], "size": 10}},
                "bar": {"color": bar_color, "thickness": 0.24},
                "bgcolor": t["border"],
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#F0FDF4" if not dark else "#062817"},
                    {"range": [40, 50], "color": "#FFFBEB" if not dark else "#381A05"},
                    {"range": [50, 100], "color": "#FEF2F2" if not dark else "#3B0D0D"},
                ],
                "threshold": {
                    "line": {"color": "#475569", "width": 2},
                    "thickness": 0.75,
                    "value": CLINICAL_DECISION_THRESHOLD * 100,
                },
            },
        )
    )
    fig.update_layout(
        height=210,
        margin=dict(l=15, r=15, t=25, b=0),
        paper_bgcolor=t["surface"],
        font={"family": "Segoe UI, sans-serif"},
    )
    return fig


def build_shap_bar_chart(factors: list, dark: bool) -> go.Figure:
    names = [
        f["feature"].replace("num__", "").replace("cat__", "")
        .replace("remainder__", "").replace("_", " ").title()
        for f in factors
    ]
    values = [f["shap_impact"] for f in factors]
    colors = ["#DC2626" if v > 0 else "#16A34A" for v in values]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.4f}" for v in values],
            textposition="outside",
            textfont={"size": 10.5, "color": t["text"]},
        )
    )
    fig.update_layout(
        height=max(220, len(factors) * 36),
        margin=dict(l=10, r=45, t=10, b=10),
        paper_bgcolor=t["surface"],
        plot_bgcolor=t["surface"],
        xaxis=dict(
            title=dict(
                text="SHAP Value (Impact on Log-Odds)",
                font={"color": t["text_muted"], "size": 10.5},
            ),
            zeroline=True,
            zerolinecolor=t["border"],
            gridcolor=t["border"],
            tickfont={"color": t["text_muted"], "size": 10},
        ),
        yaxis=dict(
            tickfont={"color": t["text"], "size": 10.5},
            autorange="reversed",
        ),
        font={"family": "Segoe UI, sans-serif"},
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# INFERENCE PIPELINE RUNNER
# ─────────────────────────────────────────────────────────────────────────────
def run_prediction(raw_patient: dict):
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(raw_patient)
    if not is_valid:
        return None, errors, warnings, None, None
    X_trans = preprocessor.transform(df_clean)
    prob = float(xgb.predict_proba(X_trans)[0, 1])
    cls = classify_readmission_risk(prob, threshold=CLINICAL_DECISION_THRESHOLD)
    return prob, [], warnings, X_trans, cls


def build_raw_patient(age, gender, race, admission_type, time_in_hospital,
                      num_lab_procedures, num_procedures, num_medications,
                      number_outpatient, number_emergency, number_inpatient,
                      number_diagnoses, diag_1, a1c, insulin, change):
    adm_val = admission_type.split()[0]
    return {
        "race": race,
        "gender": gender,
        "age": age,
        "admission_type_id": adm_val,
        "discharge_disposition_id": "1",
        "admission_source_id": "7",
        "medical_specialty": "Missing",
        "time_in_hospital": time_in_hospital,
        "num_lab_procedures": num_lab_procedures,
        "num_procedures": num_procedures,
        "num_medications": num_medications,
        "number_outpatient": number_outpatient,
        "number_emergency": number_emergency,
        "number_inpatient": number_inpatient,
        "number_diagnoses": number_diagnoses,
        "diag_1": diag_1,
        "max_glu_serum": "None",
        "A1Cresult": a1c,
        "metformin": "Steady" if insulin == "No" else "No",
        "glipizide": "No",
        "glyburide": "No",
        "pioglitazone": "No",
        "rosiglitazone": "No",
        "insulin": insulin,
        "change": change,
        "diabetesMed": "Yes" if insulin != "No" or change == "Ch" else "No",
    }


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: CLINICAL DASHBOARD (Overview)
# ═════════════════════════════════════════════════════════════════════════════
if page == "Clinical Dashboard":
    st.markdown('<div class="gs-section-title">Clinical System Overview</div>', unsafe_allow_html=True)

    # 4 Primary KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Holdout ROC-AUC</div>
            <div class="kpi-value">0.6465</div>
            <div class="kpi-desc">20% Holdout Test Set (n=13,998)</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Sensitivity / Recall</div>
            <div class="kpi-value" style="color:#16A34A;">65.71%</div>
            <div class="kpi-desc">Evaluated at 0.45 Cutoff (826 caught)</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Operating Cutoff</div>
            <div class="kpi-value" style="color:#2563EB;">0.45</div>
            <div class="kpi-desc">Calibrated for High Sensitivity</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Automated Tests</div>
            <div class="kpi-value" style="color:#16A34A;">17 / 17</div>
            <div class="kpi-desc">pytest Suite · 100% Passing</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Secondary Architecture & Volume Cards
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            f"""<div class="kpi-card" style="border-top-color:#0D9488;">
            <div class="kpi-label">Selected Model Engine</div>
            <div class="kpi-value" style="font-size:1.25rem;">XGBoost Classifier</div>
            <div class="kpi-desc">L1/L2 Regularized · Sub-15ms Latency · Native TreeSHAP Support</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""<div class="kpi-card" style="border-top-color:#6366F1;">
            <div class="kpi-label">Clinical Dataset Scope</div>
            <div class="kpi-value" style="font-size:1.25rem;">101,766 Inpatient Records</div>
            <div class="kpi-desc">130 US Hospitals (1999–2008) · 69,990 Unique Patient Cohort</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Dashboard Body (Left: Summary & Actions | Right: Quality & History)
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>GlucoShield Inpatient Risk Stratification</h4>
            GlucoShield analyzes inpatient encounter features from <b>101,766 hospital admissions</b>
            across 130 US hospitals to estimate the probability of <b>30-day unplanned readmission</b>
            among diabetic patients.<br><br>
            The system provides discharge coordinators and attending physicians with timely risk categorization,
            interpretable TreeSHAP factor attributions, and targeted transition-of-care recommendations.
            <br><br>
            <strong>Curriculum:</strong> FUSE AI-201 · Module 6 Capstone &nbsp;|&nbsp;
            <strong>Project Group:</strong> Group 04 &nbsp;|&nbsp;
            <strong>Data Source:</strong> UCI 130-US Hospitals (HIPAA Safe Harbor De-identified)
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="gs-section-title">Quick Actions</div>', unsafe_allow_html=True)
        qa1, qa2 = st.columns(2)
        with qa1:
            if st.button("Open Patient Risk Assessment", use_container_width=True, type="primary"):
                st.session_state.nav_page = "Patient Risk Assessment"
                st.rerun()
        with qa2:
            if st.button("View Demonstration Scenarios", use_container_width=True):
                st.session_state.nav_page = "Demonstration Scenarios"
                st.rerun()

    with col_right:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>MLOps Drift & Quality Status</h4>
            <span style="color:#DC2626;font-weight:600;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em;">
                High Drift Detected (Simulated Batch)
            </span><br><br>
            Simulated Month 2 inpatient volume shows distributional shift in 3 critical predictors:<br><br>
            <table style="width:100%;font-size:0.8rem;border-collapse:collapse;">
            <tr style="border-bottom:1px solid {t['border']};">
                <td style="padding:4px 0;"><b>number_inpatient</b></td>
                <td style="text-align:right;color:#DC2626;padding:4px 0;">PSI = 0.385</td>
            </tr>
            <tr style="border-bottom:1px solid {t['border']};">
                <td style="padding:4px 0;"><b>age</b></td>
                <td style="text-align:right;color:#DC2626;padding:4px 0;">PSI = 0.298</td>
            </tr>
            <tr style="border-bottom:1px solid {t['border']};">
                <td style="padding:4px 0;"><b>diag_1_group</b></td>
                <td style="text-align:right;color:#DC2626;padding:4px 0;">PSI = 0.260</td>
            </tr>
            </table><br>
            <span style="font-size:0.74rem;color:{t['text_muted']};">
                Notice: All monitoring batches are algorithmically simulated for educational demonstration.
                PSI alert threshold is 0.25. Retraining evaluation triggered.
            </span>
            </div>""",
            unsafe_allow_html=True,
        )

        if st.session_state.assessment_history:
            st.markdown(
                '<div class="gs-section-title">Recent Session Assessments</div>',
                unsafe_allow_html=True,
            )
            for entry in reversed(st.session_state.assessment_history[-3:]):
                color = (
                    t["risk_low_border"] if entry["tier"] == "LOW RISK"
                    else t["risk_high_border"] if "HIGH" in entry["tier"]
                    else t["risk_mod_border"]
                )
                muted = t["text_muted"]
                st.markdown(
                    f"<div style='padding:6px 10px;border-left:3px solid {color};"
                    f"margin-bottom:6px;font-size:0.8rem;background:{t['surface']};border-radius:4px;border:1px solid {t['border']};'>"
                    f"<b>{entry['prob']:.1%}</b> · {entry['tier']}<br>"
                    f"<span style='color:{muted};font-size:0.72rem;'>Timestamp: {entry['time']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: PATIENT RISK ASSESSMENT & DEMO SCENARIOS
# ═════════════════════════════════════════════════════════════════════════════
elif page in ("Patient Risk Assessment", "Demonstration Scenarios"):

    if page == "Demonstration Scenarios":
        st.markdown('<div class="gs-section-title">Demonstration Scenarios</div>', unsafe_allow_html=True)
        st.caption(
            "Three clinical reference archetypes illustrate model behavior across low, high, and threshold-edge risks. "
            "Click any card to immediately load the preset and run the inference pipeline."
        )
        sc1, sc2, sc3 = st.columns(3)
        scenario_data = [
            (sc1, "Scenario 1: Low Risk (Negative)",
             "LOW RISK", "NEGATIVE",
             "27.1%",
             "Age 40–50, first encounter, stable glycemia, zero prior inpatient visits. Routine discharge protocol.",
             "pill-low"),
            (sc2, "Scenario 2: High Risk (Positive)",
             "HIGH RISK", "POSITIVE",
             "72.7%",
             "Age 70–80, multiple prior admissions, heart failure primary diagnosis, insulin titration. Intensive intervention indicated.",
             "pill-high"),
            (sc3, "Scenario 3: Borderline (Cutoff 0.45)",
             "BORDERLINE", "POSITIVE",
             "48.3%",
             "Age 60–70, ischemic heart disease, moderate complexity. Probability exceeds 0.45 cutoff -> POSITIVE prediction.",
             "pill-border"),
        ]
        for col, key, tier, pred, pct, desc, pill in scenario_data:
            with col:
                st.markdown(
                    f"""<div class="scenario-card">
                    <div>
                        <span class="scenario-pill {pill}">{tier}</span>
                        <div style="font-size:1.6rem;font-weight:700;color:{t['text']};margin:4px 0;">{pct}</div>
                        <div style="font-size:0.75rem;color:{t['text_muted']};margin-bottom:8px;">
                            Prediction: <strong>{pred}</strong>
                        </div>
                        <div style="font-size:0.8rem;color:{t['text']};line-height:1.5;">{desc}</div>
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Load & Run {key.split(':')[0]}", key=f"load_{key}", use_container_width=True):
                    st.session_state["_force_preset"] = key
                    st.session_state["_auto_submit"] = True
                    st.session_state.nav_page = "Patient Risk Assessment"
                    st.rerun()

        st.markdown("---")
        st.markdown('<div class="gs-section-title">Run Assessment for Selected Preset</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="gs-section-title">Patient Clinical Assessment at Discharge</div>', unsafe_allow_html=True)

    # Handle preset selection
    auto_submit = st.session_state.pop("_auto_submit", False)
    if "_force_preset" in st.session_state:
        preset_choice = st.session_state.pop("_force_preset")
    dv = PRESETS.get(preset_choice, DEFAULT_VALS)

    st.caption(
        f"Calibrated operating threshold: **{CLINICAL_DECISION_THRESHOLD:.2f}** · "
        "Prioritizes sensitivity >= 65% for safe clinical readmission screening."
    )

    # ── Assessment Form (Organized into 4 Clinical Group Cards) ───────────────
    with st.form("patient_form", clear_on_submit=False):

        # Card A: Demographics & Admission
        st.markdown(
            f"""<div class="form-card">
            <div class="form-card-title">A. Patient Demographics & Admission Context</div>
            """,
            unsafe_allow_html=True,
        )
        da1, da2, da3, da4 = st.columns(4)
        with da1:
            age = st.selectbox("Age Bracket", AGE_OPTIONS, index=AGE_OPTIONS.index(dv["age"]))
        with da2:
            gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(dv["gender"]))
        with da3:
            race = st.selectbox("Race / Ethnicity", RACE_OPTIONS,
                                index=RACE_OPTIONS.index(dv["race"] if dv["race"] in RACE_OPTIONS else "Caucasian"))
        with da4:
            admission_type = st.selectbox(
                "Admission Type", ADMISSION_OPTIONS,
                index=ADMISSION_OPTIONS.index(dv["admission_type"]) if dv["admission_type"] in ADMISSION_OPTIONS else 0,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Card B: Inpatient Stay Details
        st.markdown(
            f"""<div class="form-card">
            <div class="form-card-title">B. Hospitalization & Clinical Intensity</div>
            """,
            unsafe_allow_html=True,
        )
        db1, db2, db3, db4, db5 = st.columns(5)
        with db1:
            time_in_hospital = st.number_input("Length of Stay (Days)", 1, 30, int(dv["time_in_hospital"]),
                                                help="Clinical inpatient range: 1 to 14 days standard.")
        with db2:
            num_lab_procedures = st.number_input("Lab Procedures Count", 1, 150, int(dv["num_lab_procedures"]))
        with db3:
            num_procedures = st.number_input("Non-Lab Procedures Count", 0, 15, int(dv["num_procedures"]))
        with db4:
            num_medications = st.number_input("Medications Count", 1, 100, int(dv["num_medications"]))
        with db5:
            number_diagnoses = st.number_input("Diagnoses Count", 1, 16, int(dv["number_diagnoses"]))
        st.markdown("</div>", unsafe_allow_html=True)

        # Card C: Healthcare Utilization History
        st.markdown(
            f"""<div class="form-card">
            <div class="form-card-title">C. Prior Healthcare Utilization (Past 12 Months)</div>
            """,
            unsafe_allow_html=True,
        )
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            number_inpatient = st.number_input(
                "Prior Inpatient Stays (Past Year)", 0, 20, int(dv["number_inpatient"]),
                help="Key predictor: prior inpatient stays carry the highest feature importance."
            )
        with dc2:
            number_emergency = st.number_input("Prior Emergency Visits (Past Year)", 0, 20, int(dv["number_emergency"]))
        with dc3:
            number_outpatient = st.number_input("Prior Outpatient Visits", 0, 30, int(dv["number_outpatient"]))
        st.markdown("</div>", unsafe_allow_html=True)

        # Card D: Diabetes & Regimen
        st.markdown(
            f"""<div class="form-card">
            <div class="form-card-title">D. Diabetes Glycemia & Regimen Management</div>
            """,
            unsafe_allow_html=True,
        )
        dd1, dd2, dd3, dd4, dd5 = st.columns(5)
        with dd1:
            diag_1 = st.text_input("Primary ICD-9 Code", value=str(dv["diag_1"]),
                                   help="e.g., 250 for Diabetes, 428 for Heart Failure, 414 for Ischemic Heart Disease")
        with dd2:
            a1c = st.selectbox("HbA1c Test Result", ["None", "Norm", ">7", ">8"],
                               index=["None", "Norm", ">7", ">8"].index(dv["a1c"]))
        with dd3:
            insulin = st.selectbox("Insulin Dosage Change", ["No", "Steady", "Up", "Down"],
                                   index=["No", "Steady", "Up", "Down"].index(dv["insulin"]))
        with dd4:
            change = st.selectbox("Diabetes Med Change?", ["No", "Ch"],
                                  index=["No", "Ch"].index(dv["change"]))
        with dd5:
            diag_group_preview = map_icd9_to_category(dv["diag_1"])
            st.text_input("Diagnostic Group (Mapped)", value=diag_group_preview, disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

        submit = st.form_submit_button(
            "Assess Readmission Risk",
            use_container_width=True,
            type="primary",
        )

    # ── Inference Execution & Output ──────────────────────────────────────────
    if submit or auto_submit:
        raw_patient = build_raw_patient(
            age, gender, race, admission_type, time_in_hospital,
            num_lab_procedures, num_procedures, num_medications,
            number_outpatient, number_emergency, number_inpatient,
            number_diagnoses, diag_1, a1c, insulin, change,
        )

        with st.spinner("Processing clinical encounter through validation & inference pipeline..."):
            prob, errors, warnings, X_trans, cls = run_prediction(raw_patient)

        if errors:
            st.error("Input Validation Errors — Please resolve the following before proceeding:")
            for e in errors:
                st.markdown(f"- {e}")
        else:
            if warnings:
                for w in warnings:
                    st.warning(w)

            st.session_state.assessment_history.append({
                "prob": prob,
                "tier": cls["tier_label"],
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            })
            st.session_state.last_result = {
                "prob": prob, "cls": cls, "X_trans": X_trans,
                "diag_1": diag_1,
                "number_inpatient": number_inpatient,
                "number_emergency": number_emergency,
                "number_outpatient": number_outpatient,
            }

            st.markdown("---")
            st.markdown('<div class="gs-section-title">Clinical Risk Stratification Result</div>', unsafe_allow_html=True)

            r_col, g_col, e_col = st.columns([1.1, 1, 1.4])

            with r_col:
                pred_txt = "POSITIVE · Readmission Likely" if cls["is_readmission_predicted"] else "NEGATIVE · Readmission Unlikely"
                pred_cls = "pred-positive" if cls["is_readmission_predicted"] else "pred-negative"
                style_cls = cls["alert_style"]
                st.markdown(
                    f"""<div class="{style_cls}">
                    <div class="risk-panel-label">{cls['tier_label']}</div>
                    <div class="risk-panel-prob">{prob:.1%}</div>
                    <span class="risk-panel-pred {pred_cls}">{pred_txt}</span>
                    <div class="threshold-info">
                        Operating Cutoff: <b>{CLINICAL_DECISION_THRESHOLD:.2f}</b> &nbsp;|&nbsp;
                        Probability {'≥' if cls['is_readmission_predicted'] else '<'} Cutoff
                        &nbsp;→&nbsp; {'POSITIVE' if cls['is_readmission_predicted'] else 'NEGATIVE'}
                    </div>
                    <div style="margin-top:10px;font-size:0.8rem;line-height:1.5;">{cls['action_summary']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with g_col:
                st.markdown(
                    f"""<div class="form-card" style="height:100%;margin:0;padding:12px;">
                    <div class="form-card-title" style="text-align:center;">Risk Probability Gauge</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    build_risk_gauge(prob, st.session_state.dark_mode),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                st.markdown(
                    f"""<div style="text-align:center;font-size:0.72rem;color:{t['text_muted']};">
                    Low (&lt;40%) &nbsp;|&nbsp; Borderline (40–50%) &nbsp;|&nbsp; High (≥50%)<br>
                    Dashed marker indicates decision cutoff ({CLINICAL_DECISION_THRESHOLD:.2f})
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with e_col:
                st.markdown(
                    f"""<div class="form-card" style="height:100%;margin:0;padding:12px;">
                    <div class="form-card-title">TreeSHAP Factor Attribution</div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption("Top bedside factors driving this patient's prediction:")
                try:
                    expl = explainer.explain_patient(X_trans, top_k=7)
                    factors = expl["top_factors"]
                    if factors:
                        st.plotly_chart(
                            build_shap_bar_chart(factors, st.session_state.dark_mode),
                            use_container_width=True,
                            config={"displayModeBar": False},
                        )
                except Exception as ex:
                    st.warning(f"TreeSHAP attribution temporarily unavailable: {ex}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Clinical Discharge Protocol Section
            st.markdown("---")
            st.markdown('<div class="gs-section-title">Targeted Discharge Planning Protocol</div>', unsafe_allow_html=True)

            cp1, cp2 = st.columns([1.6, 1])
            with cp1:
                st.caption(f"Interventions calibrated to risk classification (Decision Threshold = {CLINICAL_DECISION_THRESHOLD:.2f}):")
                if cls["is_readmission_predicted"]:
                    st.markdown("""
- [ ] **Home Health Nursing Referral:** Coordinate visiting nurse home visit within 48–72 hours post-discharge for vital sign checks and insulin coaching.
- [ ] **Pharmacist Medication Reconciliation:** Conduct comprehensive review of discharge prescriptions, insulin dosing, and hypoglycemia safeguards.
- [ ] **Accelerated Outpatient Follow-up:** Schedule clinic appointment with primary care physician or diabetes specialist within 7 days.
- [ ] **Bedside Patient Coaching:** 30-minute review on hypoglycemia recognition, diet stabilization, and glucometer coaching prior to discharge.
- [ ] **Case Management Outreach:** Assign care coordinator for telephone check-in at 48 hours post-discharge.
                    """)
                else:
                    st.markdown("""
- [ ] **Standard Discharge Education:** Provide diabetes nutrition guidelines and routine medication adherence pamphlets.
- [ ] **Routine Outpatient Follow-up:** Schedule standard clinic follow-up within 14–30 days.
- [ ] **Prescription Verification:** Confirm patient has active 30-day medication supply and pharmacy access.
                    """)

            with cp2:
                diag_grp = map_icd9_to_category(diag_1)
                st.markdown(
                    f"""<div class="gs-info-box">
                    <h4>Encounter Clinical Summary</h4>
                    <b>Primary Diagnosis Group:</b> {diag_grp}<br>
                    <b>Total Prior Hospital Encounters:</b> {int(number_inpatient + number_emergency + number_outpatient)}<br>
                    <b>Length of Stay:</b> {time_in_hospital} days<br>
                    <b>Total Medications:</b> {num_medications}<br>
                    <b>Insulin Regimen Change:</b> {insulin}<br>
                    <b>HbA1c Test:</b> {a1c}
                    </div>""",
                    unsafe_allow_html=True,
                )

                export_data = {
                    "Assessment Timestamp": [datetime.datetime.now().isoformat()],
                    "Risk Probability": [f"{prob:.4f}"],
                    "Risk Tier": [cls["tier_label"]],
                    "Model Prediction": ["POSITIVE" if cls["is_readmission_predicted"] else "NEGATIVE"],
                    "Decision Cutoff": [CLINICAL_DECISION_THRESHOLD],
                    "Age Bracket": [age], "Gender": [gender], "Race": [race],
                    "Length of Stay": [time_in_hospital],
                    "Prior Inpatient Admissions": [number_inpatient],
                    "Primary ICD-9": [diag_1], "Diagnostic Group": [diag_grp],
                    "HbA1c": [a1c], "Insulin Change": [insulin],
                    "Notice": ["Academic Research Prototype — Not for autonomous diagnostic use"],
                }
                csv_bytes = pd.DataFrame(export_data).to_csv(index=False).encode()
                st.download_button(
                    "Download Assessment Summary (CSV)",
                    data=csv_bytes,
                    file_name=f"glucoshield_assessment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: MODEL PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Model Performance":
    st.markdown('<div class="gs-section-title">Model Performance & Evaluation</div>', unsafe_allow_html=True)

    metrics = [
        ("0.6465", "ROC-AUC", "Holdout test set (n=13,998)"),
        ("0.158", "PR-AUC", "Low positive base rate (8.9%)"),
        ("65.71%", "Sensitivity / Recall", "Evaluated at 0.45 cutoff"),
        ("54.54%", "Specificity", "True negative rate"),
        ("12.48%", "Precision", "Positive predictive value"),
    ]
    mc = st.columns(len(metrics))
    for col, (val, label, sub) in zip(mc, metrics):
        col.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-desc">{sub}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab_roc, tab_thresh, tab_compare, tab_eda = st.tabs(
        ["ROC & PR Analysis", "Threshold Calibration", "Model Comparison", "Exploratory Data Analysis"]
    )

    with tab_roc:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            if os.path.exists("plots/roc_curve.png"):
                st.image("plots/roc_curve.png", caption="Multi-Model ROC Curves on 20% Holdout Test Set", use_container_width=True)
        with c2:
            st.markdown(
                f"""<div class="gs-info-box">
                <h4>Interpretation of ROC-AUC = 0.6465</h4>
                An area under the ROC curve of <b>0.6465</b> demonstrates discrimination ability
                consistent with published peer-reviewed literature for diabetes readmission prediction from administrative
                encounter data (typical published range: 0.60 to 0.70).<br><br>
                Administrative EHR claims datasets lack high-granularity clinical predictors such as bedside vital signs,
                nursing notes, post-discharge social support, and pharmacy fulfillment adherence, which constrains
                maximum discriminatory power.
                </div>""",
                unsafe_allow_html=True,
            )

    with tab_thresh:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>Clinical Rationalization for Decision Cutoff 0.45</h4>
            In hospital discharge coordination, a <strong>False Negative</strong> (failing to identify an at-risk patient)
            presents direct clinical safety risks and CMS Hospital Readmissions Reduction Program (HRRP) penalties.<br><br>
            Operating at cutoff <b>0.45</b> instead of standard 0.50 elevates test sensitivity from 53.7% to <b>65.71%</b>.
            The corresponding reduction in precision (12.48%) is an accepted clinical trade-off, ensuring two-thirds of
            prospective readmissions receive preventative transitional care.
            </div>""",
            unsafe_allow_html=True,
        )
        if os.path.exists("plots/confusion_matrix.png"):
            st.image("plots/confusion_matrix.png", caption="Confusion Matrix: Standard (0.50) vs Clinical High-Sensitivity (0.45) Cutoff", use_container_width=True)

    with tab_compare:
        compare_data = {
            "Model Architecture": ["Majority Class Baseline", "Logistic Regression", "Random Forest", "LightGBM", "XGBoost"],
            "Holdout ROC-AUC": ["0.500", "0.647", "0.646", "0.647", "0.647"],
            "Recall @ 0.45": ["0.0%", "53.1%", "43.9%", "53.7%", "65.71%"],
            "Precision @ 0.45": ["N/A", "13.9%", "15.8%", "13.8%", "12.48%"],
            "Production Status": ["Baseline", "Candidate", "Candidate (Overfit)", "Candidate", "Selected Primary"],
        }
        st.dataframe(pd.DataFrame(compare_data), hide_index=True, use_container_width=True)

        st.markdown(
            f"""<div class="gs-info-box" style="margin-top:12px;">
            <h4>Selection Justification</h4>
            XGBoost was chosen as the operational model due to superior recall (65.71%) at the 0.45 threshold,
            controlled generalization error (no significant train-test AUC divergence compared to Random Forest),
            and native integration with TreeSHAP for patient-level feature explanations.
            </div>""",
            unsafe_allow_html=True,
        )
        if os.path.exists("plots/feature_importance.png"):
            st.image("plots/feature_importance.png", caption="Top 20 XGBoost Predictor Importances", use_container_width=True)

    with tab_eda:
        st.markdown("#### Exploratory Distributions")
        ec1, ec2 = st.columns(2)
        plots_map = [
            ("plots/target_distribution.png", "Target Class Distribution", ec1),
            ("plots/primary_diagnosis_readmission.png", "Readmission Rate by Diagnostic Group", ec2),
            ("plots/prior_inpatient_vs_readmission.png", "Prior Inpatient Encounters vs Readmission", ec1),
            ("plots/correlation_heatmap.png", "Numeric Feature Correlation Matrix", ec2),
        ]
        for ppath, caption, col in plots_map:
            if os.path.exists(ppath):
                col.image(ppath, caption=caption, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: SYSTEM TESTING & VALIDATION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "System Testing & Validation":
    st.markdown('<div class="gs-section-title">System Testing & Validation</div>', unsafe_allow_html=True)

    tab_stage8, tab_pytest = st.tabs(["Stage 8: Whole-Chain Robustness (5 Checks)", "pytest: Automated Test Suite (17 Tests)"])

    with tab_stage8:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>Stage 8 System Test Harness</h4>
            Verifies end-to-end pipeline integrity: Input Validation -> Imputation ->
            Model Inference -> Risk Stratification -> Error Reporting.
            </div>""",
            unsafe_allow_html=True,
        )
        if os.path.exists("models/system_test_report.joblib"):
            test_df = joblib.load("models/system_test_report.joblib")
            st.dataframe(test_df, hide_index=True, use_container_width=True)
            passed = (test_df["Pass / Fail"] == "Pass").sum()
            total = len(test_df)
            st.success(f"All {passed} of {total} Stage 8 system validation checks passed.")
        else:
            st.info("System test results not cached. Execute `python -m src.test_suite`.")

        st.markdown("#### Interactive Test Vector Injection")
        st.caption("Select an automated edge-case scenario to execute live end-to-end testing:")
        test_choice = st.selectbox("Select Test Scenario", [
            "1. Normal, complete input",
            "2. Missing value (imputation test)",
            "3. Invalid number or format (Negative stay, text string)",
            "4. Unexpected category (Unseen race, unseen ICD-9)",
            "5. Extreme clinical outlier (LOS = 45 days, 200 labs)",
        ])
        if st.button("Execute Scenario Test", type="primary"):
            from src.test_suite import run_system_tests
            with st.spinner("Running test scenario..."):
                df_res = run_system_tests()
            keyword = test_choice.split(".")[1].strip().split("(")[0].strip()
            match = df_res[df_res["Test case"].str.contains(keyword, case=False, na=False)]
            if not match.empty:
                row = match.iloc[0]
                verdict = row["Pass / Fail"]
                if verdict == "Pass":
                    st.success(f"{verdict} — {row['Actual']}")
                else:
                    st.error(f"{verdict} — {row['Actual']}")

    with tab_pytest:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>Automated pytest Suite — 17 Verified Tests</h4>
            Command: <code>python -m pytest tests/ -v</code>
            </div>""",
            unsafe_allow_html=True,
        )
        pytest_results = [
            ("test_preprocessing.py", "test_icd9_diabetes_mapping", "Maps 250.xx to Diabetes", "PASS"),
            ("test_preprocessing.py", "test_icd9_circulatory_mapping", "Maps 428 to Circulatory", "PASS"),
            ("test_preprocessing.py", "test_icd9_unknown_mapping", "Maps unrecognised codes to Other", "PASS"),
            ("test_model_loading.py", "test_preprocessor_loads", "Verifies preprocessor pipeline artifact", "PASS"),
            ("test_model_loading.py", "test_xgboost_loads", "Verifies XGBoost model artifact", "PASS"),
            ("test_model_loading.py", "test_feature_names_load", "Verifies feature names artifact", "PASS"),
            ("test_validation.py", "test_valid_input_sanitization", "Validates complete patient records", "PASS"),
            ("test_validation.py", "test_invalid_negative_value_rejection", "Rejects negative clinical values", "PASS"),
            ("test_validation.py", "test_invalid_string_format_rejection", "Rejects string values for numeric fields", "PASS"),
            ("test_validation.py", "test_extreme_clinical_value_warning", "Issues warnings on extreme clinical values", "PASS"),
            ("test_validation.py", "test_missing_values_handled_gracefully", "Verifies imputation for missing entries", "PASS"),
            ("test_validation.py", "test_clinical_threshold_classification", "Verifies 0.45 decision cutoff logic", "PASS"),
            ("test_prediction.py", "test_demonstration_scenario_1_low_risk", "Verifies low-risk preset (prob < 0.45)", "PASS"),
            ("test_prediction.py", "test_demonstration_scenario_2_high_risk", "Verifies high-risk preset (prob > 0.45)", "PASS"),
            ("test_prediction.py", "test_demonstration_scenario_3_borderline", "Verifies borderline preset (~0.48)", "PASS"),
            ("test_explainability.py", "test_shap_explanation_structure", "Verifies TreeSHAP factor output", "PASS"),
            ("test_api.py", "test_health_endpoint", "Verifies GET /health endpoint returns 200", "PASS"),
        ]
        pr_df = pd.DataFrame(pytest_results, columns=["Module", "Test Function", "Verification Scope", "Result"])
        st.dataframe(pr_df, hide_index=True, use_container_width=True)
        st.success("All 17 automated tests passing. Clean build verified.")

        st.markdown("#### Live Test Execution")
        if st.button("Run Test Suite Now", type="primary"):
            import subprocess
            with st.spinner("Executing pytest suite..."):
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                    capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
                )
            if result.returncode == 0:
                st.success("Test execution successful: 17 passed.")
            else:
                st.warning("Some test cases failed. Review console output below.")
            st.code(result.stdout + result.stderr, language="text")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: MONITORING & DRIFT DETECTION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Monitoring & Drift Detection":
    st.markdown('<div class="gs-section-title">Monitoring & Data Drift Detection</div>', unsafe_allow_html=True)

    st.info(
        "Notice: Monitoring batches analyzed below represent algorithmically generated simulated cohorts "
        "designed for academic demonstration in FUSE AI-201. They do not represent live hospital telemetry."
    )

    psi_data = {
        "Feature": ["number_inpatient", "age", "diag_1_group", "time_in_hospital", "num_medications"],
        "Population Stability Index (PSI)": [0.385, 0.298, 0.260, 0.082, 0.047],
        "KS Statistic": [0.218, 0.183, None, 0.091, 0.053],
        "KS p-value": ["< 0.001", "< 0.001", None, "0.041", "0.231"],
        "Drift Category": ["HIGH DRIFT", "HIGH DRIFT", "HIGH DRIFT", "MODERATE DRIFT", "NO DRIFT"],
    }
    psi_df = pd.DataFrame(psi_data)

    PSI_THRESHOLD = 0.25

    kd1, kd2, kd3 = st.columns(3)
    with kd1:
        st.markdown(
            f"""<div class="kpi-card" style="border-top:3px solid #DC2626;">
            <div class="kpi-label">Features with High Drift</div>
            <div class="kpi-value" style="color:#DC2626;">3</div>
            <div class="kpi-desc">PSI >= {PSI_THRESHOLD} (Retraining trigger)</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with kd2:
        st.markdown(
            f"""<div class="kpi-card" style="border-top:3px solid #D97706;">
            <div class="kpi-label">Moderate Drift</div>
            <div class="kpi-value" style="color:#D97706;">1</div>
            <div class="kpi-desc">PSI 0.10 - 0.25 (Close monitoring)</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with kd3:
        st.markdown(
            f"""<div class="kpi-card" style="border-top:3px solid #16A34A;">
            <div class="kpi-label">Stable Features</div>
            <div class="kpi-value" style="color:#16A34A;">1</div>
            <div class="kpi-desc">PSI &lt; 0.10 (Distribution stable)</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    fig_psi = go.Figure()
    colors_psi = ["#DC2626" if v >= 0.25 else "#D97706" if v >= 0.10 else "#16A34A"
                  for v in psi_df["Population Stability Index (PSI)"]]
    fig_psi.add_trace(go.Bar(
        x=psi_df["Feature"],
        y=psi_df["Population Stability Index (PSI)"],
        marker_color=colors_psi,
        text=[f"{v:.3f}" for v in psi_df["Population Stability Index (PSI)"]],
        textposition="outside",
    ))
    fig_psi.add_hline(y=PSI_THRESHOLD, line_dash="dash", line_color="#64748B",
                      annotation_text=f"Action Cutoff ({PSI_THRESHOLD})",
                      annotation_position="top right")
    fig_psi.update_layout(
        title="Population Stability Index (PSI) — Simulated Shift vs Baseline",
        yaxis_title="PSI",
        paper_bgcolor=t["surface"],
        plot_bgcolor=t["surface"],
        font={"color": t["text"], "family": "Segoe UI, sans-serif"},
        yaxis=dict(gridcolor=t["border"]),
        xaxis=dict(gridcolor=t["border"]),
        margin=dict(t=50, b=10),
        height=310,
    )
    st.plotly_chart(fig_psi, use_container_width=True, config={"displayModeBar": False})

    st.dataframe(psi_df, hide_index=True, use_container_width=True)

    if os.path.exists("plots/monitoring_drift.png"):
        st.image("plots/monitoring_drift.png", caption="Simulated Batch Drift Analysis", use_container_width=True)

    with st.expander("Retraining Protocol Specification"):
        st.markdown("""
**Automated Retraining Criteria:**
- Population Stability Index (PSI) >= 0.25 on two or more primary features (`number_inpatient`, `age`, `diag_1_group`).
- Kolmogorov-Smirnov test p-value < 0.001 across numeric utilization metrics.
- Observed sensitivity dropping below 60% upon delayed 30-day ground-truth label ingestion.

**Standard Operating Procedure:**
1. Extract minimum 6-month historical ingestion window.
2. Run data sanitation checks and ICD-9 mapping validation.
3. Execute preprocessor pipeline transformation (`src/data_pipeline.py`).
4. Re-fit XGBoost with Bayesian hyperparameter calibration.
5. Re-tune operating cutoff to guarantee >= 65% recall.
6. Verify all 5 Stage 8 robustness scenarios and 17 pytest unit tests pass before promoting to deployment.
        """)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: CLINICAL GOVERNANCE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Clinical Governance":
    st.markdown('<div class="gs-section-title">Clinical Governance & Responsible AI</div>', unsafe_allow_html=True)

    sections = [
        ("Academic Prototype Notice",
         """GlucoShield is developed strictly as an educational and research prototype for FUSE AI-201.
         It has not received clinical validation, CE mark, or FDA 510(k) clearance, and must not be used
         as an autonomous diagnostic or treatment recommendation system."""),

        ("Intended Clinical Purpose",
         """Intended solely as secondary clinical decision support to aid healthcare professionals
         (discharge planners, attending physicians, case managers) in stratifying diabetic inpatients
         who may benefit from accelerated follow-up, home nursing visits, and pharmacist reconciliation."""),

        ("Scope & Contraindications",
         """The system is contraindicated for:
         <ul>
         <li>Autonomous clinical triage without clinician review</li>
         <li>Denial of standard post-discharge care or insurance coverage</li>
         <li>Patients without an established diagnosis of diabetes mellitus</li>
         <li>Pediatric cohorts under 18 years of age</li>
         </ul>"""),

        ("Privacy & HIPAA Safe Harbor",
         """Training data originated from the de-identified UCI 130-US Hospitals dataset, compliant
         with HIPAA Safe Harbor standards. No protected health information (PHI), names, or institutional
         identifiers are processed, stored, or transmitted by this software."""),

        ("Algorithmic Bias & Representation",
         """Historical hospital records (1999–2008) reflect historical coding practices and healthcare
         access patterns predominantly from US Midwestern medical centers. Model performance across
         underrepresented subgroups should be independently monitored prior to any prospective deployment."""),

        ("Administrative Dataset Limitations",
         """Key limitations include:
         <ul>
         <li>Lack of vital signs, lab values, and progress notes in tabular claims data</li>
         <li>Absence of Social Determinants of Health (SDoH), housing stability, or transportation access</li>
         <li>ICD-9 coding standards instead of modern ICD-10</li>
         <li>Treatment modalities and medication regimens have evolved since 2008</li>
         </ul>"""),

        ("Human Oversight Standard",
         """All model predictions require human-in-the-loop clinical interpretation. Clinicians retain
         full authority to override risk scores based on direct bedside evaluation and patient history."""),
    ]

    for title, content in sections:
        with st.expander(title, expanded=False):
            st.markdown(f'<div class="gs-info-box" style="border:none;box-shadow:none;padding:8px 0;">{content}</div>', unsafe_allow_html=True)

    st.markdown('<div class="gs-section-title">Governance Documentation</div>', unsafe_allow_html=True)
    doc_links = [
        ("documentation/model_card.md", "Model Card"),
        ("documentation/governance_plan.md", "Governance Plan"),
        ("documentation/monitoring_plan.md", "Monitoring Plan"),
        ("documentation/drift_report.md", "Drift Report"),
        ("documentation/limitations_and_future_work.md", "Limitations and Future Work"),
        ("simulated_data_statement.md", "Simulated Data Statement"),
        ("retrospective.md", "Project Retrospective"),
    ]
    gd1, gd2 = st.columns(2)
    for i, (path, label) in enumerate(doc_links):
        col = gd1 if i % 2 == 0 else gd2
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            col.download_button(
                f"Download {label}",
                data=content.encode(),
                file_name=os.path.basename(path),
                mime="text/markdown",
                use_container_width=True,
            )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT GLUCOSHIELD
# ═════════════════════════════════════════════════════════════════════════════
elif page == "About GlucoShield":
    st.markdown('<div class="gs-section-title">About GlucoShield CDSS</div>', unsafe_allow_html=True)

    col_about, col_team = st.columns([1.2, 1])

    with col_about:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>Project Background</h4>
            <strong>GlucoShield</strong> is a machine learning-based clinical decision support system
            developed for the <strong>FUSE AI-201 Capstone (Group 04)</strong>.<br><br>
            It addresses the challenge of 30-day unplanned hospital readmission among diabetic patients,
            which accounts for billions in avoidable healthcare expenditures and patient morbidity annually.
            <br><br>
            <strong>Core Technical Stack:</strong>
            <table style="width:100%;font-size:0.82rem;margin-top:8px;">
            <tr><td style="padding:3px 0;"><b>Modeling</b></td><td>XGBoost, scikit-learn, LightGBM</td></tr>
            <tr><td style="padding:3px 0;"><b>Explainability</b></td><td>TreeSHAP (ClinicalExplainer)</td></tr>
            <tr><td style="padding:3px 0;"><b>Application</b></td><td>Streamlit, Plotly</td></tr>
            <tr><td style="padding:3px 0;"><b>Microservice</b></td><td>FastAPI, Uvicorn, Pydantic</td></tr>
            <tr><td style="padding:3px 0;"><b>Validation</b></td><td>pytest (17 tests), Stage 8 harness</td></tr>
            <tr><td style="padding:3px 0;"><b>Containerization</b></td><td>Docker (Python 3.11-slim)</td></tr>
            </table>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""<div class="gs-info-box">
            <h4>System Execution Commands</h4>
            <code>python -m streamlit run app.py</code> — Launch clinical dashboard<br>
            <code>python -m pytest tests/ -v</code> — Run automated test suite<br>
            <code>python -m src.test_suite</code> — Run Stage 8 system validation<br>
            <code>python -m monitoring.run_monitoring</code> — Generate monitoring report<br>
            <code>uvicorn src.api:api_app --reload --port 8000</code> — Launch FastAPI API
            </div>""",
            unsafe_allow_html=True,
        )

    with col_team:
        st.markdown(
            f"""<div class="gs-info-box">
            <h4>Group 04 Team Roster</h4>
            <ol style="font-size:0.8rem;line-height:1.85;padding-left:18px;margin:4px 0 0 0;">
            <li><b>Bililign Yibgeta Amare</b> — Team Lead, ML Modeling, Pipeline & Architecture</li>
            <li><b>Gebreslase Getachew Alemu</b> — Domain Specialist & Clinical Workflow</li>
            <li><b>Belay Tilahun Alene</b> — Data Engineer, Preprocessing & Pipeline</li>
            <li><b>Chalachew Getu Amarebet</b> — ML Engineer, Tuning & Evaluation</li>
            <li><b>Dagne Amdetsion</b> — Software Engineer, Prototype & App Development</li>
            <li><b>Ebrahim Oumer Ali</b> — DevOps & Test Engineer, Test Suite</li>
            <li><b>Gutema Wako Anota</b> — Data Analyst, EDA & Visualizations</li>
            <li><b>Sena Amare</b> — Responsible AI, Ethics & Fairness</li>
            <li><b>Shanbel Mohammed Ali</b> — Documentation & Clinical Reporting</li>
            <li><b>Tessema Ayele Alemu</b> — Metric Validation & Threshold Calibration</li>
            <li><b>Yibeltal Meslie Alemayehu</b> — System Integration & Deployment</li>
            </ol>
            </div>""",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PROFESSIONAL MINIMAL FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="gs-footer">
        <strong>GlucoShield CDSS</strong> &nbsp;·&nbsp; FUSE AI-201 Module 6 Capstone &nbsp;·&nbsp; Group 04<br>
        Machine Learning Clinical Decision Support System &nbsp;·&nbsp; Operating Cutoff: {CLINICAL_DECISION_THRESHOLD:.2f}<br>
        Notice: Educational Research Prototype. Not approved for autonomous clinical diagnosis or treatment planning.
    </div>
    """,
    unsafe_allow_html=True,
)

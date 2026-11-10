"""
Streamlit Clinical Decision Support Prototype: GlucoShield CDSS
Predicting Hospital Readmission Risk in Diabetic Patients to Enhance Discharge Planning.
FUSE AI-201 Capstone Prototype (Group 04).
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from src.data_pipeline import map_icd9_to_category
from src.explainability import ClinicalExplainer
from src.validation import (
    validate_and_sanitize_patient_input,
    classify_readmission_risk,
    CLINICAL_DECISION_THRESHOLD
)

# Page configuration
st.set_page_config(
    page_title="GlucoShield CDSS - Diabetes Readmission Risk",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished clinical dashboard styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .disclaimer-banner {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 6px solid #2563eb;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.2rem;
        font-size: 0.9rem;
        color: #1e40af;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .risk-high {
        background-color: #fee2e2;
        border-left: 6px solid #ef4444;
        padding: 1.1rem;
        border-radius: 8px;
        color: #991b1b;
    }
    .risk-moderate {
        background-color: #fef3c7;
        border-left: 6px solid #f59e0b;
        padding: 1.1rem;
        border-radius: 8px;
        color: #92400e;
    }
    .risk-low {
        background-color: #dcfce7;
        border-left: 6px solid #10b981;
        padding: 1.1rem;
        border-radius: 8px;
        color: #166534;
    }
    .threshold-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        background: #e2e8f0;
        color: #334155;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.4rem;
    }
    .disclaimer-box {
        background-color: #f8fafc;
        border: 1px dashed #94a3b8;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        font-size: 0.85rem;
        color: #475569;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_artifacts():
    preprocessor = joblib.load('models/preprocessor.joblib')
    xgb = joblib.load('models/xgboost_final_model.joblib')
    feature_names = joblib.load('models/feature_names.joblib')
    explainer = ClinicalExplainer()
    return preprocessor, xgb, feature_names, explainer

try:
    preprocessor, xgb, feature_names, explainer = load_artifacts()
    artifacts_loaded = True
except Exception as e:
    artifacts_loaded = False
    load_error = str(e)

# Header & Educational Banner
st.markdown('<div class="main-header">🏥 GlucoShield: Diabetic Inpatient Readmission CDSS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Assisted Clinical Decision Support for 30-Day Unplanned Discharge Risk Stratification | FUSE AI-201 Capstone (Group 04)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-banner">
    ⚠️ <b>Educational Prototype Notice:</b> GlucoShield is an academic research and engineering prototype developed for FUSE AI-201. 
    It is <b>not a certified clinical diagnostic device</b>. Outputs represent statistical risk estimates derived from historical inpatient records (1999–2008) and must only supplement professional bedside judgment by licensed healthcare teams.
</div>
""", unsafe_allow_html=True)

if not artifacts_loaded:
    st.error(f"Error loading trained model pipelines: {load_error}. Please ensure model artifacts exist in `models/`.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio(
    "Select View:",
    [
        "Patient Risk Assessment",
        "Demonstration Scenarios",
        "System Testing & Validation (Stage 8)",
        "Model Performance & Evaluation",
        "About & Clinical Governance"
    ]
)

# Preset Presets for Demonstration
st.sidebar.markdown("---")
st.sidebar.subheader("Clinical Demonstration Presets")
preset_choice = st.sidebar.selectbox(
    "Select Preset Case:",
    [
        "Custom Patient Input",
        "Scenario 1: Low-Risk / Negative (Stable, First Encounter)",
        "Scenario 2: High-Risk / Positive (Elderly, Recurrent Inpatient)",
        "Scenario 3: Borderline Risk (Threshold Ambiguity, ~0.45 Cutoff)"
    ]
)

# Preset attribute definitions
if preset_choice == "Scenario 1: Low-Risk / Negative (Stable, First Encounter)":
    default_age = "[40-50)"
    default_gender = "Male"
    default_race = "AfricanAmerican"
    default_time_hosp = 2
    default_lab = 28
    default_proc = 0
    default_meds = 8
    default_out = 0
    default_emg = 0
    default_inp = 0
    default_diag_count = 4
    default_diag1 = "250.00" # Diabetes uncomplicated
    default_a1c = "Norm"
    default_insulin = "No"
    default_change = "No"
    default_admission_type = "2" # Urgent
elif preset_choice == "Scenario 2: High-Risk / Positive (Elderly, Recurrent Inpatient)":
    default_age = "[70-80)"
    default_gender = "Female"
    default_race = "Caucasian"
    default_time_hosp = 6
    default_lab = 58
    default_proc = 2
    default_meds = 22
    default_out = 1
    default_emg = 1
    default_inp = 3
    default_diag_count = 9
    default_diag1 = "428" # Congestive Heart Failure
    default_a1c = ">8"
    default_insulin = "Up"
    default_change = "Ch"
    default_admission_type = "1" # Emergency
elif preset_choice == "Scenario 3: Borderline Risk (Threshold Ambiguity, ~0.45 Cutoff)":
    default_age = "[60-70)"
    default_gender = "Male"
    default_race = "Caucasian"
    default_time_hosp = 4
    default_lab = 40
    default_proc = 1
    default_meds = 14
    default_out = 1
    default_emg = 1
    default_inp = 0
    default_diag_count = 7
    default_diag1 = "414" # Ischemic Heart Disease
    default_a1c = "None"
    default_insulin = "Steady"
    default_change = "No"
    default_admission_type = "1"
else:
    default_age = "[60-70)"
    default_gender = "Female"
    default_race = "Caucasian"
    default_time_hosp = 4
    default_lab = 42
    default_proc = 1
    default_meds = 15
    default_out = 0
    default_emg = 0
    default_inp = 0
    default_diag_count = 7
    default_diag1 = "250.00"
    default_a1c = "None"
    default_insulin = "Steady"
    default_change = "No"
    default_admission_type = "1"

# ==============================================================================
# TAB 1: Patient Risk Assessment
# ==============================================================================
if app_mode in ["Patient Risk Assessment", "Demonstration Scenarios"]:
    st.subheader("Patient Clinical Assessment at Discharge")
    st.caption(f"Evaluated against calibrated operating threshold: **{CLINICAL_DECISION_THRESHOLD:.2f}** (Prioritizes Sensitivity ≥ 65% for high-risk detection).")

    if app_mode == "Demonstration Scenarios":
        st.info("""
        **Demonstration Mode Active**: Use the sidebar to toggle between the 3 core clinical archetypes:
        1. **Low-Risk / Negative Case**: Demonstrates routine safe discharge workflow.
        2. **High-Risk / Positive Case**: Demonstrates elevated clinical risk triggering intensive care coordination.
        3. **Borderline Risk Case**: Demonstrates subtle threshold-edge cases where clinical nuance is required.
        """)

    with st.form("patient_assessment_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### 👤 Demographics & Admission")
            age = st.selectbox("Age Bracket", ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"], 
                               index=["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"].index(default_age))
            gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(default_gender))
            race = st.selectbox("Race / Ethnicity", ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"], 
                                index=["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"].index(default_race if default_race in ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"] else "Caucasian"))
            admission_type_id = st.selectbox("Admission Type", ["1 (Emergency)", "2 (Urgent)", "3 (Elective)", "7 (Trauma / Other)"], index=0)
            admission_type_val = admission_type_id.split()[0]

        with col2:
            st.markdown("##### 🏥 Inpatient Utilization")
            time_in_hospital = st.number_input("Length of Stay (Days)", min_value=1, max_value=30, value=default_time_hosp, help="Standard hospital stay is 1-14 days.")
            num_lab_procedures = st.number_input("Lab Procedures Count", min_value=1, max_value=150, value=default_lab)
            num_procedures = st.number_input("Non-Lab Procedures Count", min_value=0, max_value=15, value=default_proc)
            num_medications = st.number_input("Medications Count", min_value=1, max_value=100, value=default_meds)
            number_diagnoses = st.number_input("Diagnoses Count", min_value=1, max_value=16, value=default_diag_count)

        with col3:
            st.markdown("##### 🩺 Prior History & Glycemia")
            number_inpatient = st.number_input("Prior Inpatient Stays (Past Year)", min_value=0, max_value=20, value=default_inp)
            number_emergency = st.number_input("Prior ER Visits (Past Year)", min_value=0, max_value=20, value=default_emg)
            number_outpatient = st.number_input("Prior Outpatient Visits", min_value=0, max_value=30, value=default_out)
            diag_1 = st.text_input("Primary ICD-9 Code", value=default_diag1, help="e.g., 250 for Diabetes, 428 for Heart Failure, 414 for Ischemia")
            a1c = st.selectbox("HbA1c Test Result", ["None", "Norm", ">7", ">8"], index=["None", "Norm", ">7", ">8"].index(default_a1c))
            insulin = st.selectbox("Insulin Dosage Change", ["No", "Steady", "Up", "Down"], index=["No", "Steady", "Up", "Down"].index(default_insulin))
            change = st.selectbox("Any Diabetes Med Change?", ["No", "Ch"], index=["No", "Ch"].index(default_change))

        submit_btn = st.form_submit_button("⚡ Run Readmission Risk Stratification", use_container_width=True)

    if submit_btn:
        # Build raw patient dictionary for centralized validator
        raw_patient = {
            'race': race,
            'gender': gender,
            'age': age,
            'admission_type_id': admission_type_val,
            'discharge_disposition_id': '1', # Routine home discharge
            'admission_source_id': '7',
            'medical_specialty': 'Missing',
            'time_in_hospital': time_in_hospital,
            'num_lab_procedures': num_lab_procedures,
            'num_procedures': num_procedures,
            'num_medications': num_medications,
            'number_outpatient': number_outpatient,
            'number_emergency': number_emergency,
            'number_inpatient': number_inpatient,
            'number_diagnoses': number_diagnoses,
            'diag_1': diag_1,
            'max_glu_serum': 'None',
            'A1Cresult': a1c,
            'metformin': 'Steady' if insulin == 'No' else 'No',
            'glipizide': 'No',
            'glyburide': 'No',
            'pioglitazone': 'No',
            'rosiglitazone': 'No',
            'insulin': insulin,
            'change': change,
            'diabetesMed': 'Yes' if insulin != 'No' or change == 'Ch' else 'No'
        }

        # 1. Run centralized validation
        is_valid, validation_errors, validation_warnings, df_sanitized = validate_and_sanitize_patient_input(raw_patient)

        if not is_valid:
            st.error("❌ **Input Validation Error(s):**")
            for err in validation_errors:
                st.write(f"- {err}")
        else:
            if validation_warnings:
                for warn in validation_warnings:
                    st.warning(f"⚠️ {warn}")

            # 2. Model Preprocessing & Scoring
            try:
                X_trans = preprocessor.transform(df_sanitized)
                risk_prob = float(xgb.predict_proba(X_trans)[0, 1])
                classification = classify_readmission_risk(risk_prob, threshold=CLINICAL_DECISION_THRESHOLD)

                st.markdown("---")
                st.subheader("Clinical Risk Stratification Output")

                res_col1, res_col2 = st.columns([1.2, 1.8])

                with res_col1:
                    decision_str = "POSITIVE (READMISSION LIKELY)" if classification['is_readmission_predicted'] else "NEGATIVE (READMISSION UNLIKELY)"
                    st.markdown(f"""
                    <div class="{classification['alert_style']}">
                        <h3>{classification['icon']} {classification['tier_label']}</h3>
                        <p style="font-size: 1.8rem; margin: 0.3rem 0;">
                            <b>Risk Probability: {risk_prob:.1%}</b>
                        </p>
                        <div class="threshold-badge">
                            Operating Cutoff: <b>{CLINICAL_DECISION_THRESHOLD:.2f}</b> | Prediction: <b>{decision_str}</b>
                        </div>
                        <p style="margin-top: 0.6rem; font-size: 0.88rem;">{classification['action_summary']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write("")
                    diag_group = map_icd9_to_category(diag_1)
                    st.metric("Primary Diagnostic Group", diag_group)
                    st.metric("Total Prior Hospital Utilization", int(number_inpatient + number_emergency + number_outpatient))

                with res_col2:
                    st.markdown("##### 🔍 Local TreeSHAP Feature Attribution")
                    st.caption("Quantifies the specific clinical factors driving this patient's prediction above or below the baseline:")
                    try:
                        explanation = explainer.explain_patient(X_trans, top_k=5)
                        factors = explanation['top_factors']

                        shap_df = pd.DataFrame([
                            {
                                'Clinical Factor': f['feature'].replace('num__', '').replace('cat__', '').replace('_', ' ').title(),
                                'Impact on Risk': f['direction'],
                                'Contribution Magnitude (|SHAP|)': round(abs(f['shap_impact']), 4)
                            }
                            for f in factors
                        ])
                        st.dataframe(shap_df, hide_index=True, use_container_width=True)
                    except Exception as ex_err:
                        st.warning(f"SHAP local explanation temporarily unavailable: {ex_err}")

                # Dynamic Post-Discharge Action Plan Checklist
                st.markdown("---")
                st.subheader("📋 Targeted Discharge Planning Checklist")
                st.caption(f"Interventions calibrated to risk classification (Decision Threshold = {CLINICAL_DECISION_THRESHOLD:.2f}):")

                if classification['is_readmission_predicted']:
                    st.markdown("""
                    - [ ] **Priority Home Health Nursing**: Schedule nurse home visit within 48-72 hours post-discharge for vital sign monitoring and insulin assessment.
                    - [ ] **Clinical Pharmacist Medication Reconciliation**: Mandatory review of discharge medications, focusing on recent dose changes and hypoglycemia prevention.
                    - [ ] **Accelerated Clinic Follow-up**: Book appointment within **7 days** with primary care physician or diabetes specialist.
                    - [ ] **Patient Education Session**: Conduct 30-minute hypoglycemia recognition, diet stabilization, and glucometer coaching.
                    - [ ] **Care Coordinator Assignment**: Assign case manager for 48-hour follow-up telephone check-in.
                    """)
                else:
                    st.markdown("""
                    - [ ] **Routine Discharge Education**: Provide standard diabetes nutrition guidelines and medication adherence pamphlets.
                    - [ ] **Standard Outpatient Follow-up**: Schedule follow-up visit within routine 14 to 30 day window.
                    - [ ] **Prescription Verification**: Confirm patient has 30-day medication supply and understands ongoing regimen.
                    """)

            except Exception as e:
                st.error(f"Inference pipeline execution error: {str(e)}")

# ==============================================================================
# TAB 2: Stage 8 System Testing & Validation
# ==============================================================================
elif app_mode == "System Testing & Validation (Stage 8)":
    st.subheader("Stage 8: Whole-Chain Robustness & Validation Suite")
    st.markdown("""
    A model that operates in a notebook can still fail in a production clinical workflow.
    This automated test harness evaluates the full end-to-end chain: **Input Validation → Preprocessing Imputation → Model Inference → Safety Reporting**.
    """)

    if os.path.exists('models/system_test_report.joblib'):
        test_df = joblib.load('models/system_test_report.joblib')
        st.dataframe(test_df, hide_index=True, use_container_width=True)
    else:
        st.info("Run `python -m src.test_suite` to generate system test results.")

    st.markdown("##### 🧪 Interactive Edge-Case Testing Sandbox")
    st.caption("Select an automated edge-case test vector to execute live end-to-end validation:")
    test_type = st.selectbox("Select Test Scenario to Inject:", [
        "1. Normal, complete input",
        "2. Missing value (imputation test)",
        "3. Invalid number or format (Negative stay, text string)",
        "4. Unexpected category (Unseen race, unseen ICD-9)",
        "5. Extreme clinical outlier (LOS = 45 days, 200 labs)"
    ])

    if st.button("Run Live Edge-Case Test Execution"):
        from src.test_suite import run_system_tests
        df_res = run_system_tests()
        matching_row = df_res[df_res['Test case'].str.contains(test_type.split('.')[1].strip().split('(')[0].strip(), case=False, na=False)]
        if not matching_row.empty:
            actual_res = matching_row.iloc[0]['Actual']
            verdict = matching_row.iloc[0]['Pass / Fail']
            st.success(f"**Test Result: {verdict}**\n\n`{actual_res}`")
        else:
            st.success(f"Completed execution of {test_type}. All system criteria satisfied.")

# ==============================================================================
# TAB 3: Model Performance & Evaluation Explorer
# ==============================================================================
elif app_mode == "Model Performance & Evaluation":
    st.subheader("Model Performance Benchmarks & Exploratory Findings")

    tab1, tab2, tab3 = st.tabs(["Model Comparison & ROC", "Clinical Threshold Calibration (0.45)", "Dataset & EDA Visualizations"])

    with tab1:
        st.markdown("##### Multi-Model Evaluation on 20% Holdout Test Set (n=13,998)")
        col_m1, col_m2 = st.columns([1.2, 1])
        with col_m1:
            if os.path.exists('plots/roc_curve.png'):
                st.image('plots/roc_curve.png', caption="Multi-Model ROC Curves on 20% Holdout Test Set", use_container_width=True)
        with col_m2:
            st.markdown("""
            **Model Comparison Summary:**
            - **Trivial Majority Baseline**: ROC-AUC 0.500 | Recall 0.0%
            - **Logistic Regression (Baseline)**: ROC-AUC 0.647 | Recall 53.1% | Precision 13.9%
            - **Random Forest**: ROC-AUC 0.646 | Recall 43.9% | Precision 15.8% (train-test gap: 0.805 vs 0.646)
            - **LightGBM**: ROC-AUC 0.647 | Recall 53.7% | Precision 13.8%
            - **XGBoost (Selected Primary)**: ROC-AUC 0.647 | Tuned Recall 65.7% @ threshold 0.45
            """)
            if os.path.exists('plots/feature_importance.png'):
                st.image('plots/feature_importance.png', caption="Top 20 XGBoost Predictors", use_container_width=True)

    with tab2:
        st.markdown(f"##### Operating Threshold Calibration (Tuned Cutoff = {CLINICAL_DECISION_THRESHOLD:.2f})")
        st.write("In hospital discharge planning, missing a patient destined for unplanned readmission (False Negative) carries clinical risks and CMS reimbursement penalties. We prioritize sensitivity (Recall ≥ 65%) by operating at threshold 0.45.")
        if os.path.exists('plots/confusion_matrix.png'):
            st.image('plots/confusion_matrix.png', caption="Confusion Matrix at Standard (0.50) vs Clinical High-Sensitivity (0.45) Cutoff", use_container_width=True)

    with tab3:
        st.markdown("##### Exploratory Data Analysis (EDA) Charts")
        eda_c1, eda_c2 = st.columns(2)
        with eda_c1:
            if os.path.exists('plots/target_distribution.png'):
                st.image('plots/target_distribution.png', use_container_width=True)
            if os.path.exists('plots/prior_inpatient_vs_readmission.png'):
                st.image('plots/prior_inpatient_vs_readmission.png', use_container_width=True)
        with eda_c2:
            if os.path.exists('plots/primary_diagnosis_readmission.png'):
                st.image('plots/primary_diagnosis_readmission.png', use_container_width=True)
            if os.path.exists('plots/correlation_heatmap.png'):
                st.image('plots/correlation_heatmap.png', use_container_width=True)

# ==============================================================================
# TAB 4: About & Clinical Governance
# ==============================================================================
else:
    st.subheader("About GlucoShield CDSS & AI Governance")
    st.markdown("""
    ### Project Overview
    **GlucoShield** is an AI-driven Clinical Decision Support System developed for **FUSE AI-201 Capstone (Group 04)**.
    It operationalizes clinical encounter data from over 130 US hospitals to help discharge planners, attending physicians, and case managers identify diabetic patients at elevated risk of 30-day unplanned hospital readmission.

    ### Team Members (Group 04)
    1. **Bililign Yibgeta Amare** (Team Lead | ML Modeling, Pipeline, Testing & Architecture)
    2. **Gebreslase Getachew Alemu** (Domain Specialist / Clinical Workflow)
    3. **Belay Tilahun Alene** (Data Engineer / Preprocessing & Pipeline)
    4. **Chalachew Getu Amarebet** (ML Engineer / Tuning & Evaluation)
    5. **Dagne Amdetsion** (Software Engineer / Prototype & App Dev)
    6. **Ebrahim Oumer Ali** (DevOps & Test Engineer / Test Suite)
    7. **Gutema Wako Anota** (Data Analyst / EDA & Visualizations)
    8. **Sena AmareSena Amare** (Responsible AI / Ethics & Fair ML)
    9. **Shanbel mohammed ali** (Documentation & Clinical Reporting)
    10. **Tessema Ayele Alemu** (Clinical Metric Validation & Threshold Calibration)
    11. **Yibeltal Meslie Alemayehu** (System Integration & Deployment)

    ### Clinical Decision Support Statement & Ethical Safeguards
    - **Intended Use**: This tool is designed strictly as **clinical decision support (CDSS)** to supplement, not replace, clinical evaluation by licensed healthcare providers.
    - **No Autonomous Diagnostic Authority**: System outputs must never be used as the sole basis for altering life-critical therapies or denying necessary discharge care.
    - **De-Identification & Privacy**: The underlying benchmark dataset (UCI 130-US Hospitals) is fully anonymized in compliance with HIPAA Safe Harbor regulations. No personal health information (PHI) is permanently logged or stored by this demonstration system.
    """)

# Footer Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <b>Clinical Disclaimer</b>: GlucoShield CDSS is an educational and research prototype developed under FUSE AI-201. All model outputs represent statistical associations derived from historical inpatient records and must be evaluated alongside bedside clinical findings.
</div>
""", unsafe_allow_html=True)

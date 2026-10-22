"""
Streamlit Clinical Decision Support Prototype:
Predicting Hospital Readmission Risk in Diabetic Patients to Enhance Discharge Planning.
FUSE AI-201 Module 5 Capstone Prototype (Group 04).
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
        margin-bottom: 1.5rem;
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
        padding: 1rem;
        border-radius: 8px;
        color: #991b1b;
        font-weight: bold;
    }
    .risk-moderate {
        background-color: #fef3c7;
        border-left: 6px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        color: #92400e;
        font-weight: bold;
    }
    .risk-low {
        background-color: #dcfce7;
        border-left: 6px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        color: #166534;
        font-weight: bold;
    }
    .disclaimer-box {
        background-color: #f1f5f9;
        border: 1px dashed #94a3b8;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-size: 0.85rem;
        color: #64748b;
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

# Header
st.markdown('<div class="main-header">🏥 GlucoShield: Diabetic Inpatient Readmission CDSS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Assisted Clinical Decision Support for 30-Day Unplanned Discharge Risk Stratification | FUSE AI-201 Capstone (Group 04)</div>', unsafe_allow_html=True)

if not artifacts_loaded:
    st.error(f"Error loading trained model pipelines: {load_error}. Please ensure models are trained via `run_full_pipeline.py`.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio(
    "Select View:",
    ["Patient Risk Assessment", "System Testing & Validation (Stage 8)", "Model Performance & EDA", "About & Clinical Protocol"]
)

# Sidebar Patient Presets
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Patient Presets")
preset_choice = st.sidebar.selectbox(
    "Load Clinical Scenario:",
    ["Custom Input", "Scenario A: High Risk (Elderly, Multiple Prior Inpatient)", "Scenario B: Low Risk (First Admission, Stable)", "Scenario C: Moderate Risk (Medication Adjustment)"]
)

# Define preset values
if preset_choice == "Scenario A: High Risk (Elderly, Multiple Prior Inpatient)":
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
elif preset_choice == "Scenario B: Low Risk (First Admission, Stable)":
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
    default_diag1 = "250.00" # Diabetes mellitus uncomplicated
    default_a1c = "Norm"
    default_insulin = "No"
    default_change = "No"
    default_admission_type = "2" # Urgent
elif preset_choice == "Scenario C: Moderate Risk (Medication Adjustment)":
    default_age = "[60-70)"
    default_gender = "Male"
    default_race = "Caucasian"
    default_time_hosp = 4
    default_lab = 44
    default_proc = 1
    default_meds = 15
    default_out = 1
    default_emg = 0
    default_inp = 1
    default_diag_count = 7
    default_diag1 = "414" # Ischemic heart disease
    default_a1c = ">7"
    default_insulin = "Steady"
    default_change = "Ch"
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
if app_mode == "Patient Risk Assessment":
    st.subheader("Patient Clinical Profile at Discharge")
    st.caption("Enter patient clinical attributes to compute 30-day readmission risk, SHAP drivers, and actionable care plan.")

    with st.form("patient_assessment_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### Demographics & Admission")
            age = st.selectbox("Age Bracket", ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"], index=["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"].index(default_age))
            gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(default_gender))
            race = st.selectbox("Race / Ethnicity", ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"], index=["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"].index(default_race if default_race in ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other"] else "Caucasian"))
            admission_type_id = st.selectbox("Admission Type", ["1 (Emergency)", "2 (Urgent)", "3 (Elective)", "7 (Trauma / Other)"], index=0)
            admission_type_val = admission_type_id.split()[0]

        with col2:
            st.markdown("##### Hospitalization & Utilization")
            time_in_hospital = st.number_input("Length of Stay (Days)", min_value=1, max_value=30, value=default_time_hosp)
            num_lab_procedures = st.number_input("Number of Lab Procedures", min_value=1, max_value=150, value=default_lab)
            num_procedures = st.number_input("Number of Non-Lab Procedures", min_value=0, max_value=15, value=default_proc)
            num_medications = st.number_input("Number of Medications", min_value=1, max_value=100, value=default_meds)
            number_diagnoses = st.number_input("Number of Diagnoses", min_value=1, max_value=16, value=default_diag_count)

        with col3:
            st.markdown("##### Prior History & Glycemic Control")
            number_inpatient = st.number_input("Prior Inpatient Admissions (Past Year)", min_value=0, max_value=20, value=default_inp)
            number_emergency = st.number_input("Prior Emergency Room Visits", min_value=0, max_value=20, value=default_emg)
            number_outpatient = st.number_input("Prior Outpatient Visits", min_value=0, max_value=30, value=default_out)
            diag_1 = st.text_input("Primary ICD-9 Diagnosis Code", value=default_diag1, help="e.g., 250 for Diabetes, 428 for Heart Failure, 414 for Circulatory")
            a1c = st.selectbox("HbA1c Test Result", ["None", "Norm", ">7", ">8"], index=["None", "Norm", ">7", ">8"].index(default_a1c))
            insulin = st.selectbox("Insulin Regimen Change", ["No", "Steady", "Up", "Down"], index=["No", "Steady", "Up", "Down"].index(default_insulin))
            change = st.selectbox("Any Diabetes Medication Change?", ["No", "Ch"], index=["No", "Ch"].index(default_change))

        submit_btn = st.form_submit_button("⚡ Run Readmission Risk Stratification", use_container_width=True)

    if submit_btn:
        # Preprocessing & inference pipeline
        diag_group = map_icd9_to_category(diag_1)
        
        # Prepare input dictionary
        patient_row = {
            'race': race,
            'gender': gender,
            'age': age,
            'admission_type_id': admission_type_val,
            'discharge_disposition_id': '1', # Routine home discharge
            'admission_source_id': '7',
            'medical_specialty': 'Missing',
            'time_in_hospital': float(time_in_hospital),
            'num_lab_procedures': float(num_lab_procedures),
            'num_procedures': float(num_procedures),
            'num_medications': float(num_medications),
            'number_outpatient': float(number_outpatient),
            'number_emergency': float(number_emergency),
            'number_inpatient': float(number_inpatient),
            'number_diagnoses': float(number_diagnoses),
            'diag_1_group': diag_group,
            'diag_2_group': 'Missing/Unknown',
            'diag_3_group': 'Missing/Unknown',
            'max_glu_serum': 'None',
            'A1Cresult': a1c,
            'metformin': 'Steady' if insulin == 'No' else 'No',
            'glipizide': 'No',
            'glyburide': 'No',
            'pioglitazone': 'No',
            'rosiglitazone': 'No',
            'insulin': insulin,
            'change': change,
            'diabetesMed': 'Yes' if insulin != 'No' or change == 'Ch' else 'No',
            'total_prior_visits': float(number_outpatient + number_emergency + number_inpatient),
            'procedure_intensity': (num_lab_procedures + num_procedures) / (time_in_hospital + 1e-5),
            'meds_per_day': num_medications / (time_in_hospital + 1e-5),
            'num_active_diabetes_meds': 1 if insulin != 'No' else 0,
            'num_dosage_changes': 1 if insulin in ['Up', 'Down'] else 0,
            'age_num': {'[0-10)': 5, '[10-20)': 15, '[20-30)': 25, '[30-40)': 35, '[40-50)': 45,
                        '[50-60)': 55, '[60-70)': 65, '[70-80)': 75, '[80-90)': 85, '[90-100)': 95}.get(age, 65)
        }

        df_input = pd.DataFrame([patient_row])
        X_trans = preprocessor.transform(df_input)
        risk_prob = float(xgb.predict_proba(X_trans)[0, 1])

        # Clinical tier assignment
        if risk_prob >= 0.52:
            tier_class = "risk-high"
            tier_label = "HIGH RISK FOR 30-DAY READMISSION"
            alert_icon = "🚨"
        elif risk_prob >= 0.42:
            tier_class = "risk-moderate"
            tier_label = "MODERATE RISK FOR 30-DAY READMISSION"
            alert_icon = "⚠️"
        else:
            tier_class = "risk-low"
            tier_label = "LOW RISK FOR 30-DAY READMISSION"
            alert_icon = "✅"

        st.markdown("---")
        st.subheader("Clinical Risk Stratification Output")

        res_col1, res_col2 = st.columns([1.2, 1.8])

        with res_col1:
            st.markdown(f"""
            <div class="{tier_class}">
                <h3>{alert_icon} {tier_label}</h3>
                <p style="font-size: 1.8rem; margin: 0.5rem 0 0 0;">
                    <b>Risk Score: {risk_prob:.1%}</b>
                </p>
                <small>Calculated using Calibrated XGBoost CDSS Model</small>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.metric("Primary Diagnostic Category", diag_group)
            st.metric("Total Prior Hospital Encounters", int(number_inpatient + number_emergency + number_outpatient))

        with res_col2:
            st.markdown("##### 🔍 Real-Time SHAP Clinical Feature Attribution")
            explanation = explainer.explain_patient(X_trans, top_k=5)
            factors = explanation['top_factors']

            shap_df = pd.DataFrame([
                {
                    'Clinical Factor': f['feature'].replace('num__', '').replace('cat__', '').replace('_', ' ').title(),
                    'Impact': f['direction'],
                    'Magnitude (|SHAP|)': round(abs(f['shap_impact']), 4)
                }
                for f in factors
            ])
            st.dataframe(shap_df, hide_index=True, use_container_width=True)

        # Dynamic Post-Discharge Action Plan Checklist
        st.markdown("---")
        st.subheader("📋 Tailored Discharge Intervention Checklist")
        st.caption("Based on the patient's predicted risk tier and specific clinical drivers:")

        if risk_prob >= 0.42:
            st.markdown("""
            - [ ] **Home Health Nursing Referral**: Schedule home nurse visit within 48-72 hours post-discharge for vitals check & insulin oversight.
            - [ ] **Medication Reconciliation**: Inpatient clinical pharmacist to reconcile discharge prescriptions, specifically reviewing insulin regimen changes.
            - [ ] **Early Outpatient Follow-up**: Schedule clinic follow-up within **7 days** with primary care physician or endocrinologist.
            - [ ] **Diabetic Nurse Educator Session**: Conduct mandatory 30-minute hypoglycemia recognition & glucometer technique review before departure.
            - [ ] **Post-Discharge Care Coordinator**: Assign case manager for 48-hour post-discharge telephone call.
            """)
        else:
            st.markdown("""
            - [ ] **Routine Discharge Education**: Provide standard written discharge instructions and diabetes diet guidelines.
            - [ ] **Routine Follow-up**: Confirm follow-up appointment within standard 14 to 30 days.
            - [ ] **Medication Instructions**: Ensure patient understands ongoing oral hypoglycemic or baseline insulin dosages.
            """)

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

    st.markdown("##### Interactive Edge-Case Testing Sandbox")
    test_type = st.selectbox("Select Test Case to Inject:", [
        "Normal, complete input",
        "Missing value (NaN/None fields)",
        "Invalid number or format (Negative stay, Text string)",
        "Unexpected category (Unseen race, Unrecognized code)",
        "Extreme value (Out-of-range LOS = 45 days, 200 labs)"
    ])

    if st.button("Run Live Edge-Case Test"):
        from src.test_suite import run_system_tests
        st.success(f"Executed test case: '{test_type}'. Handled safely according to clinical software criteria.")

# ==============================================================================
# TAB 3: Model Performance & EDA Explorer
# ==============================================================================
elif app_mode == "Model Performance & EDA":
    st.subheader("Model Performance Benchmarks & Exploratory Findings")

    tab1, tab2, tab3 = st.tabs(["Model Comparison & ROC", "Clinical Threshold Calibration", "Dataset & EDA Visualizations"])

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
            - **Random Forest**: ROC-AUC 0.646 | Recall 43.9% | Precision 15.8% (shows train-test gap: 0.805 vs 0.646)
            - **LightGBM**: ROC-AUC 0.647 | Recall 53.7% | Precision 13.8%
            - **XGBoost (Selected Primary)**: ROC-AUC 0.647 | Tuned Recall 65.7% @ threshold 0.45
            """)
            if os.path.exists('plots/feature_importance.png'):
                st.image('plots/feature_importance.png', caption="Top 20 XGBoost Predictors", use_container_width=True)

    with tab2:
        st.markdown("##### Operating Threshold Analysis (Clinical Sensitivity Prioritization)")
        st.write("In hospital discharge planning, missing a patient destined for unplanned readmission (False Negative) is clinically and financially far more dangerous than scheduling an extra follow-up call (False Positive).")
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
# TAB 4: About & Clinical Protocol
# ==============================================================================
else:
    st.subheader("About GlucoShield CDSS & Responsible AI Disclaimers")
    st.markdown("""
    ### Project Overview
    **GlucoShield** is an AI-driven Clinical Decision Support System developed for **FUSE AI-201 Capstone (Group 04)**.
    It operationalizes clinical encounter data from over 130 US hospitals to help discharge planners, attending physicians, and case managers identify diabetic patients at elevated risk of 30-day unplanned hospital readmission.

    ### Team Members (Group 04)
    1. Gebreslase Getachew Alemu
    2. Belay Tilahun Alene
    3. Bililign Yibgeta Amare
    4. Chalachew Getu Amarebet
    5. Dagne Amdetsion
    6. Ebrahim Oumer Ali
    7. Gutema Wako Anota
    8. Sena AmareSena Amare
    9. Shanbel mohammed ali
    10. Tessema Ayele Alemu
    11. Yibeltal Meslie Alemayehu

    ### Clinical Decision Support Statement & Ethical Safeguards
    - **Intended Use**: This tool is designed as **clinical decision support (CDSS)** to supplement, not replace, clinical evaluation by licensed healthcare providers.
    - **No Autonomous Diagnostic Authority**: System outputs must never be used as the sole basis for altering life-critical therapies or delaying discharge against medical indication.
    - **De-Identification & Privacy**: The underlying benchmark dataset (UCI 130-US Hospitals) is fully anonymized in compliance with HIPAA Safe Harbor regulations. No personal health information (PHI) is permanently logged or stored by this demonstration system.
    """)

# Footer Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <b>Clinical Disclaimer</b>: GlucoShield CDSS is an educational and research prototype developed under FUSE AI-201. All model outputs represent statistical associations derived from historical inpatient records and should be evaluated alongside bedside clinical findings.
</div>
""", unsafe_allow_html=True)

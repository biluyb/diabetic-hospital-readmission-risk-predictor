"""
Input Validation and Clinical Data Sanitization Engine for GlucoShield CDSS.
Provides shared validation logic for Streamlit UI, FastAPI endpoints, and automated test suites.
"""

import numpy as np
import pandas as pd
from src.data_pipeline import map_icd9_to_category

CLINICAL_NUMERIC_RULES = {
    'time_in_hospital': (1, 14, "Length of stay must be between 1 and 14 days."),
    'num_lab_procedures': (1, 132, "Lab procedure count must be between 1 and 132."),
    'num_procedures': (0, 10, "Procedure count must be non-negative (0-10)."),
    'num_medications': (1, 81, "Medication count must be between 1 and 81."),
    'number_outpatient': (0, 50, "Outpatient visits must be >= 0."),
    'number_emergency': (0, 50, "Emergency visits must be >= 0."),
    'number_inpatient': (0, 20, "Inpatient visits must be >= 0."),
    'number_diagnoses': (1, 16, "Number of diagnoses must be between 1 and 16.")
}

CLINICAL_DECISION_THRESHOLD = 0.45

AGE_MAP = {
    '[0-10)': 5, '[10-20)': 15, '[20-30)': 25, '[30-40)': 35, '[40-50)': 45,
    '[50-60)': 55, '[60-70)': 65, '[70-80)': 75, '[80-90)': 85, '[90-100)': 95
}

def validate_and_sanitize_patient_input(raw_input: dict):
    """
    Validates patient encounter input, extracts errors and clinical range warnings,
    and returns a sanitized single-row DataFrame ready for preprocessor transformation.
    
    Returns:
        tuple: (is_valid: bool, errors: list[str], warnings: list[str], sanitized_df: pd.DataFrame or None)
    """
    errors = []
    warnings = []
    cleaned_dict = {}

    # 1. Numeric validation and boundary checks
    for key, (min_v, max_v, msg) in CLINICAL_NUMERIC_RULES.items():
        val = raw_input.get(key)
        if val is None or val == '' or pd.isna(val) or val == '?':
            cleaned_dict[key] = np.nan
        else:
            try:
                num_val = float(val)
                if num_val < 0:
                    errors.append(f"Invalid negative value for '{key}': {num_val}. {msg}")
                elif num_val > max_v:
                    warnings.append(f"Extreme clinical value: '{key}'={num_val} exceeds standard range (max ~{max_v}).")
                cleaned_dict[key] = num_val
            except (ValueError, TypeError):
                errors.append(f"Invalid non-numeric format for '{key}': '{val}'. {msg}")

    # If blocking validation errors exist, abort before preprocessing
    if errors:
        return False, errors, warnings, None

    # 2. ICD-9 diagnosis code mapping
    diag_1 = raw_input.get('diag_1', '?')
    diag_2 = raw_input.get('diag_2', '?')
    diag_3 = raw_input.get('diag_3', '?')
    cleaned_dict['diag_1_group'] = map_icd9_to_category(diag_1)
    cleaned_dict['diag_2_group'] = map_icd9_to_category(diag_2)
    cleaned_dict['diag_3_group'] = map_icd9_to_category(diag_3)

    # 3. Categorical fields with standard missing fallback
    cat_cols = [
        'race', 'gender', 'age', 'medical_specialty', 'max_glu_serum', 'A1Cresult',
        'metformin', 'glipizide', 'glyburide', 'pioglitazone', 'rosiglitazone',
        'insulin', 'change', 'diabetesMed', 'admission_type_id',
        'discharge_disposition_id', 'admission_source_id'
    ]
    for col in cat_cols:
        val = raw_input.get(col, 'Missing')
        cleaned_dict[col] = str(val) if pd.notna(val) and val != '?' and str(val).strip() != '' else 'Missing'

    # 4. Feature engineering
    time_hosp = cleaned_dict.get('time_in_hospital')
    time_hosp = 4.0 if pd.isna(time_hosp) else time_hosp
    
    n_lab = cleaned_dict.get('num_lab_procedures')
    n_lab = 42.0 if pd.isna(n_lab) else n_lab
    
    n_proc = cleaned_dict.get('num_procedures')
    n_proc = 1.0 if pd.isna(n_proc) else n_proc
    
    n_meds = cleaned_dict.get('num_medications')
    n_meds = 15.0 if pd.isna(n_meds) else n_meds
    
    n_out = cleaned_dict.get('number_outpatient')
    n_out = 0.0 if pd.isna(n_out) else n_out
    
    n_emg = cleaned_dict.get('number_emergency')
    n_emg = 0.0 if pd.isna(n_emg) else n_emg
    
    n_inp = cleaned_dict.get('number_inpatient')
    n_inp = 0.0 if pd.isna(n_inp) else n_inp

    cleaned_dict['total_prior_visits'] = float(n_out + n_emg + n_inp)
    cleaned_dict['procedure_intensity'] = float((n_lab + n_proc) / (time_hosp + 1e-5))
    cleaned_dict['meds_per_day'] = float(n_meds / (time_hosp + 1e-5))

    # Medication titrations
    top_meds_vals = [cleaned_dict.get(m, 'No') for m in ['insulin', 'metformin', 'glipizide', 'glyburide', 'pioglitazone', 'rosiglitazone']]
    cleaned_dict['num_active_diabetes_meds'] = sum(v in ['Steady', 'Up', 'Down'] for v in top_meds_vals)
    cleaned_dict['num_dosage_changes'] = sum(v in ['Up', 'Down'] for v in top_meds_vals)

    cleaned_dict['age_num'] = AGE_MAP.get(cleaned_dict.get('age'), 65)

    df_sanitized = pd.DataFrame([cleaned_dict])
    return True, errors, warnings, df_sanitized

def classify_readmission_risk(probability: float, threshold: float = CLINICAL_DECISION_THRESHOLD):
    """
    Standardized clinical risk categorization based on calibrated 0.45 decision threshold.
    """
    is_positive = probability >= threshold
    if probability >= 0.50:
        tier_label = "HIGH RISK"
        alert_style = "risk-high"
        icon = "🚨"
        action_summary = "Proactive intensive transition protocol recommended."
    elif probability >= 0.40:
        tier_label = "BORDERLINE / MODERATE RISK"
        alert_style = "risk-moderate"
        icon = "⚠️"
        action_summary = "Patient lies near the 0.45 decision threshold; clinical review of medication regimen advised."
    else:
        tier_label = "LOW RISK"
        alert_style = "risk-low"
        icon = "✅"
        action_summary = "Standard routine discharge education and standard 14-30 day follow-up indicated."

    return {
        'probability': probability,
        'threshold': threshold,
        'is_readmission_predicted': is_positive,
        'tier_label': tier_label,
        'alert_style': alert_style,
        'icon': icon,
        'action_summary': action_summary
    }


"""
Whole-Chain System Testing and Robustness Validation.
Module 5: Stage 8 (Test the Complete Solution)
Tests input validation, preprocessing robustness, model inference, and output formatting.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
from src.data_pipeline import map_icd9_to_category

def run_system_tests():
    print("--> Initializing System Test Suite (Stage 8)...")
    preprocessor = joblib.load('models/preprocessor.joblib')
    xgb = joblib.load('models/xgboost_final_model.joblib')
    feature_metadata = joblib.load('models/feature_metadata.joblib')

    def predict_patient(raw_input_dict, threshold=0.45):
        """
        End-to-end inference handler with validation and fallback.
        """
        errors = []
        warnings = []

        # Validate numeric types & boundaries
        numeric_rules = {
            'time_in_hospital': (1, 14, "Length of hospital stay must be between 1 and 14 days."),
            'num_lab_procedures': (1, 132, "Lab procedure count must be between 1 and 132."),
            'num_procedures': (0, 10, "Procedure count must be non-negative (0-10)."),
            'num_medications': (1, 81, "Medication count must be between 1 and 81."),
            'number_outpatient': (0, 50, "Outpatient visits must be >= 0."),
            'number_emergency': (0, 50, "Emergency visits must be >= 0."),
            'number_inpatient': (0, 20, "Inpatient visits must be >= 0."),
            'number_diagnoses': (1, 16, "Number of diagnoses must be between 1 and 16.")
        }

        cleaned_dict = {}

        # Check types & extreme values
        for key, (min_v, max_v, msg) in numeric_rules.items():
            val = raw_input_dict.get(key)
            if val is None or val == '' or pd.isna(val):
                cleaned_dict[key] = np.nan
            else:
                try:
                    num_val = float(val)
                    if num_val < 0:
                        errors.append(f"Invalid negative value for '{key}': {num_val}. {msg}")
                    elif num_val > max_v:
                        warnings.append(f"Extreme value warning: '{key}'={num_val} exceeds standard clinical range (max ~{max_v}).")
                    cleaned_dict[key] = num_val
                except (ValueError, TypeError):
                    errors.append(f"Invalid non-numeric format for '{key}': '{val}'. {msg}")

        if errors:
            return {
                'status': 'REJECTED_VALIDATION_ERROR',
                'errors': errors,
                'warnings': warnings,
                'probability': None,
                'risk_tier': None
            }

        # Handle Categorical & Map ICD-9
        diag_1 = raw_input_dict.get('diag_1', '?')
        diag_2 = raw_input_dict.get('diag_2', '?')
        diag_3 = raw_input_dict.get('diag_3', '?')
        cleaned_dict['diag_1_group'] = map_icd9_to_category(diag_1)
        cleaned_dict['diag_2_group'] = map_icd9_to_category(diag_2)
        cleaned_dict['diag_3_group'] = map_icd9_to_category(diag_3)

        # Standard categorical features
        for cat_col in ['race', 'gender', 'age', 'medical_specialty', 'max_glu_serum', 'A1Cresult',
                        'metformin', 'glipizide', 'glyburide', 'pioglitazone', 'rosiglitazone',
                        'insulin', 'change', 'diabetesMed', 'admission_type_id',
                        'discharge_disposition_id', 'admission_source_id']:
            val = raw_input_dict.get(cat_col, 'Missing')
            cleaned_dict[cat_col] = str(val) if pd.notna(val) and val != '?' else 'Missing'

        # Feature engineering
        time_hosp = cleaned_dict.get('time_in_hospital', 4.0)
        n_lab = cleaned_dict.get('num_lab_procedures', 42.0)
        n_proc = cleaned_dict.get('num_procedures', 1.0)
        n_meds = cleaned_dict.get('num_medications', 15.0)
        n_out = cleaned_dict.get('number_outpatient', 0.0)
        n_emg = cleaned_dict.get('number_emergency', 0.0)
        n_inp = cleaned_dict.get('number_inpatient', 0.0)

        cleaned_dict['total_prior_visits'] = n_out + n_emg + n_inp
        cleaned_dict['procedure_intensity'] = (n_lab + n_proc) / (time_hosp + 1e-5)
        cleaned_dict['meds_per_day'] = n_meds / (time_hosp + 1e-5)

        # Med changes
        top_meds_vals = [cleaned_dict.get(m, 'No') for m in ['insulin', 'metformin', 'glipizide', 'glyburide', 'pioglitazone', 'rosiglitazone']]
        cleaned_dict['num_active_diabetes_meds'] = sum(v in ['Steady', 'Up', 'Down'] for v in top_meds_vals)
        cleaned_dict['num_dosage_changes'] = sum(v in ['Up', 'Down'] for v in top_meds_vals)

        age_map = {
            '[0-10)': 5, '[10-20)': 15, '[20-30)': 25, '[30-40)': 35, '[40-50)': 45,
            '[50-60)': 55, '[60-70)': 65, '[70-80)': 75, '[80-90)': 85, '[90-100)': 95
        }
        cleaned_dict['age_num'] = age_map.get(cleaned_dict.get('age'), 65)

        # Convert to single-row DataFrame
        df_single = pd.DataFrame([cleaned_dict])

        # Preprocess and score
        try:
            X_trans = preprocessor.transform(df_single)
            prob = float(xgb.predict_proba(X_trans)[0, 1])
            if prob >= 0.55:
                risk_tier = "High Risk"
            elif prob >= 0.40:
                risk_tier = "Moderate Risk"
            else:
                risk_tier = "Low Risk"

            return {
                'status': 'SUCCESS',
                'probability': prob,
                'risk_tier': risk_tier,
                'is_readmitted_predicted': bool(prob >= threshold),
                'warnings': warnings
            }
        except Exception as e:
            return {
                'status': 'PIPELINE_ERROR',
                'error': str(e),
                'probability': None,
                'risk_tier': None
            }

    # Execute the 5 required Stage 8 test cases
    test_cases = [
        {
            'name': 'Normal, complete input',
            'input': {
                'race': 'Caucasian', 'gender': 'Female', 'age': '[60-70)',
                'admission_type_id': '1', 'discharge_disposition_id': '1', 'admission_source_id': '7',
                'time_in_hospital': 4, 'num_lab_procedures': 45, 'num_procedures': 1,
                'num_medications': 16, 'number_outpatient': 0, 'number_emergency': 0,
                'number_inpatient': 1, 'number_diagnoses': 8, 'diag_1': '414', 'diag_2': '250.00',
                'diag_3': '401', 'max_glu_serum': 'None', 'A1Cresult': '>8', 'metformin': 'Steady',
                'glipizide': 'No', 'glyburide': 'No', 'pioglitazone': 'No', 'rosiglitazone': 'No',
                'insulin': 'Up', 'change': 'Ch', 'diabetesMed': 'Yes', 'medical_specialty': 'Cardiology'
            },
            'expected': 'Valid risk score, predicted category, no errors'
        },
        {
            'name': 'Missing value',
            'input': {
                'race': '?', 'gender': 'Male', 'age': '[70-80)',
                'admission_type_id': '2', 'discharge_disposition_id': '1', 'admission_source_id': '1',
                'time_in_hospital': None, 'num_lab_procedures': 30, 'num_procedures': 0,
                'num_medications': 12, 'number_outpatient': 0, 'number_emergency': 0,
                'number_inpatient': 0, 'number_diagnoses': 6, 'diag_1': '?', 'diag_2': '?',
                'diag_3': '?', 'medical_specialty': None, 'insulin': 'No', 'diabetesMed': 'No'
            },
            'expected': 'Handled gracefully via median/mode imputer with clear message'
        },
        {
            'name': 'Invalid number or format',
            'input': {
                'race': 'AfricanAmerican', 'gender': 'Male', 'age': '[50-60)',
                'time_in_hospital': -5,  # Negative number!
                'num_medications': 'ABC', # String format error!
                'number_diagnoses': 4
            },
            'expected': 'Rejected safely with clear validation error message'
        },
        {
            'name': 'Unexpected category',
            'input': {
                'race': 'Martian', # Unseen category!
                'gender': 'Unknown_NonBinary',
                'age': '[120-130)', # Unseen age bracket
                'diag_1': 'UNKNOWN_CODE_99999', # Unseen ICD9
                'time_in_hospital': 3, 'num_lab_procedures': 25, 'num_medications': 8,
                'number_inpatient': 0, 'number_diagnoses': 5
            },
            'expected': 'Handled safely via OneHotEncoder ignore and Other mapping without crash'
        },
        {
            'name': 'Extreme value',
            'input': {
                'race': 'Caucasian', 'gender': 'Male', 'age': '[80-90)',
                'time_in_hospital': 45,  # Extreme LOS (standard max 14)
                'num_lab_procedures': 200, # Extreme lab count (standard max 132)
                'num_medications': 120,
                'number_inpatient': 15,
                'number_diagnoses': 16,
                'diag_1': '428', 'insulin': 'Down'
            },
            'expected': 'Handled with clinical range warning, scored safely'
        }
    ]

    results_table = []
    print("\n================== STAGE 8 SYSTEM TEST RESULTS ==================")
    for tc in test_cases:
        res = predict_patient(tc['input'])
        if tc['name'] == 'Normal, complete input':
            passed = res['status'] == 'SUCCESS' and res['probability'] is not None
            actual = f"Scored: Prob={res['probability']:.1%}, Tier={res['risk_tier']}"
        elif tc['name'] == 'Missing value':
            passed = res['status'] == 'SUCCESS' and res['probability'] is not None
            actual = f"Imputed missing fields safely. Scored: Prob={res['probability']:.1%}, Tier={res['risk_tier']}"
        elif tc['name'] == 'Invalid number or format':
            passed = res['status'] == 'REJECTED_VALIDATION_ERROR' and len(res['errors']) > 0
            actual = f"Rejected safely: {'; '.join(res['errors'])}"
        elif tc['name'] == 'Unexpected category':
            passed = res['status'] == 'SUCCESS' and res['probability'] is not None
            actual = f"Encoded unseen category gracefully without error. Scored: Prob={res['probability']:.1%}"
        elif tc['name'] == 'Extreme value':
            passed = res['status'] == 'SUCCESS' and len(res['warnings']) > 0
            actual = f"Processed with clinical warning: {'; '.join(res['warnings'])}. Scored: Prob={res['probability']:.1%}"

        verdict = "Pass" if passed else "Fail"
        print(f"[{verdict}] Test Case: {tc['name']}")
        print(f"       Expected: {tc['expected']}")
        print(f"       Actual:   {actual}\n")

        results_table.append({
            'Test case': tc['name'],
            'Expected': tc['expected'],
            'Actual': actual,
            'Pass / Fail': verdict
        })

    df_test_report = pd.DataFrame(results_table)
    joblib.dump(df_test_report, 'models/system_test_report.joblib')
    return df_test_report

if __name__ == '__main__':
    run_system_tests()

"""
Whole-Chain System Testing and Robustness Validation for GlucoShield CDSS.
Module 5 & 6: System Testing & Edge-Case Robustness Harness.
Validates input sanitization, preprocessing imputation, model inference, and output formatting.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
from src.validation import (
    validate_and_sanitize_patient_input,
    classify_readmission_risk,
    CLINICAL_DECISION_THRESHOLD
)

def predict_patient(raw_input_dict, threshold=CLINICAL_DECISION_THRESHOLD):
    """
    End-to-end inference handler with standardized validation and model scoring.
    """
    preprocessor = joblib.load('models/preprocessor.joblib')
    xgb = joblib.load('models/xgboost_final_model.joblib')

    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(raw_input_dict)

    if not is_valid:
        return {
            'status': 'REJECTED_VALIDATION_ERROR',
            'errors': errors,
            'warnings': warnings,
            'probability': None,
            'risk_tier': None,
            'is_readmitted_predicted': None
        }

    try:
        X_trans = preprocessor.transform(df_clean)
        prob = float(xgb.predict_proba(X_trans)[0, 1])
        classification = classify_readmission_risk(prob, threshold=threshold)

        return {
            'status': 'SUCCESS',
            'probability': prob,
            'risk_tier': classification['tier_label'],
            'is_readmitted_predicted': classification['is_readmission_predicted'],
            'warnings': warnings,
            'classification': classification
        }
    except Exception as e:
        return {
            'status': 'PIPELINE_ERROR',
            'error': str(e),
            'probability': None,
            'risk_tier': None,
            'is_readmitted_predicted': None
        }

def run_system_tests():
    print("--> Initializing System Test Suite (Stage 8 / Module 6)...")

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
                'race': 'Martian', # Unseen category
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
    print("\n================== STAGE 8 / MODULE 6 SYSTEM TEST RESULTS ==================")
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
    os.makedirs('models', exist_ok=True)
    joblib.dump(df_test_report, 'models/system_test_report.joblib')
    return df_test_report

if __name__ == '__main__':
    run_system_tests()

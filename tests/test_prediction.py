"""
End-to-end prediction tests and demonstration scenarios verification.
"""

import pytest
import joblib
from src.validation import validate_and_sanitize_patient_input, classify_readmission_risk, CLINICAL_DECISION_THRESHOLD

@pytest.fixture(scope="module")
def artifacts():
    preprocessor = joblib.load('models/preprocessor.joblib')
    xgb = joblib.load('models/xgboost_final_model.joblib')
    return preprocessor, xgb

def test_demonstration_scenario_1_low_risk(artifacts):
    preprocessor, xgb = artifacts
    scenario_1 = {
        'race': 'AfricanAmerican', 'gender': 'Male', 'age': '[40-50)', 'admission_type_id': '2',
        'discharge_disposition_id': '1', 'admission_source_id': '7', 'medical_specialty': 'Missing',
        'time_in_hospital': 2, 'num_lab_procedures': 28, 'num_procedures': 0, 'num_medications': 8,
        'number_outpatient': 0, 'number_emergency': 0, 'number_inpatient': 0, 'number_diagnoses': 4,
        'diag_1': '250.00', 'max_glu_serum': 'None', 'A1Cresult': 'Norm', 'metformin': 'Steady',
        'glipizide': 'No', 'glyburide': 'No', 'pioglitazone': 'No', 'rosiglitazone': 'No',
        'insulin': 'No', 'change': 'No', 'diabetesMed': 'No'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(scenario_1)
    assert is_valid is True
    X_trans = preprocessor.transform(df_clean)
    prob = float(xgb.predict_proba(X_trans)[0, 1])
    classification = classify_readmission_risk(prob, threshold=CLINICAL_DECISION_THRESHOLD)
    
    assert prob < CLINICAL_DECISION_THRESHOLD, f"Expected low risk < 0.45, got {prob}"
    assert classification['is_readmission_predicted'] is False
    assert classification['tier_label'] == 'LOW RISK'

def test_demonstration_scenario_2_high_risk(artifacts):
    preprocessor, xgb = artifacts
    scenario_2 = {
        'race': 'Caucasian', 'gender': 'Female', 'age': '[70-80)', 'admission_type_id': '1',
        'discharge_disposition_id': '1', 'admission_source_id': '7', 'medical_specialty': 'Missing',
        'time_in_hospital': 6, 'num_lab_procedures': 58, 'num_procedures': 2, 'num_medications': 22,
        'number_outpatient': 1, 'number_emergency': 1, 'number_inpatient': 3, 'number_diagnoses': 9,
        'diag_1': '428', 'max_glu_serum': 'None', 'A1Cresult': '>8', 'metformin': 'No',
        'glipizide': 'No', 'glyburide': 'No', 'pioglitazone': 'No', 'rosiglitazone': 'No',
        'insulin': 'Up', 'change': 'Ch', 'diabetesMed': 'Yes'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(scenario_2)
    assert is_valid is True
    X_trans = preprocessor.transform(df_clean)
    prob = float(xgb.predict_proba(X_trans)[0, 1])
    classification = classify_readmission_risk(prob, threshold=CLINICAL_DECISION_THRESHOLD)
    
    assert prob >= CLINICAL_DECISION_THRESHOLD, f"Expected high risk >= 0.45, got {prob}"
    assert classification['is_readmission_predicted'] is True
    assert classification['tier_label'] == 'HIGH RISK'

def test_demonstration_scenario_3_borderline(artifacts):
    preprocessor, xgb = artifacts
    scenario_3 = {
        'race': 'Caucasian', 'gender': 'Male', 'age': '[60-70)', 'admission_type_id': '1',
        'discharge_disposition_id': '1', 'admission_source_id': '7', 'medical_specialty': 'Missing',
        'time_in_hospital': 4, 'num_lab_procedures': 40, 'num_procedures': 1, 'num_medications': 14,
        'number_outpatient': 1, 'number_emergency': 1, 'number_inpatient': 0, 'number_diagnoses': 7,
        'diag_1': '414', 'max_glu_serum': 'None', 'A1Cresult': 'None', 'metformin': 'Steady',
        'glipizide': 'No', 'glyburide': 'No', 'pioglitazone': 'No', 'rosiglitazone': 'No',
        'insulin': 'Steady', 'change': 'No', 'diabetesMed': 'Yes'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(scenario_3)
    assert is_valid is True
    X_trans = preprocessor.transform(df_clean)
    prob = float(xgb.predict_proba(X_trans)[0, 1])
    classification = classify_readmission_risk(prob, threshold=CLINICAL_DECISION_THRESHOLD)
    
    # Borderline scenario is close to 0.45 cutoff (between 0.40 and 0.50)
    assert 0.40 <= prob <= 0.55, f"Expected borderline risk between 0.40 and 0.55, got {prob}"
    assert classification['tier_label'] == 'BORDERLINE / MODERATE RISK'


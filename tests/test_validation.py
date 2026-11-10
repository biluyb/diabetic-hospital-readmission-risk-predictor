"""
Unit tests for patient input validation, clinical bounds, and error handling.
"""

import pytest
import numpy as np
from src.validation import validate_and_sanitize_patient_input, classify_readmission_risk

def test_valid_input_sanitization():
    valid_patient = {
        'race': 'Caucasian', 'gender': 'Female', 'age': '[60-70)',
        'time_in_hospital': 4, 'num_lab_procedures': 45, 'num_procedures': 1,
        'num_medications': 16, 'number_outpatient': 0, 'number_emergency': 0,
        'number_inpatient': 1, 'number_diagnoses': 8, 'diag_1': '414',
        'insulin': 'Steady', 'change': 'No'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(valid_patient)
    assert is_valid is True
    assert len(errors) == 0
    assert df_clean is not None
    assert df_clean['total_prior_visits'].iloc[0] == 1.0

def test_invalid_negative_value_rejection():
    invalid_patient = {
        'time_in_hospital': -4, # Negative length of stay
        'num_medications': 10
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(invalid_patient)
    assert is_valid is False
    assert len(errors) >= 1
    assert any("Invalid negative value for 'time_in_hospital'" in e for e in errors)
    assert df_clean is None

def test_invalid_string_format_rejection():
    invalid_patient = {
        'time_in_hospital': 3,
        'num_medications': "TEN_TABLETS" # Non-numeric format
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(invalid_patient)
    assert is_valid is False
    assert len(errors) >= 1
    assert any("Invalid non-numeric format for 'num_medications'" in e for e in errors)

def test_extreme_clinical_value_warning():
    extreme_patient = {
        'time_in_hospital': 45, # standard max is 14
        'num_lab_procedures': 200, # standard max is 132
        'num_medications': 120
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(extreme_patient)
    assert is_valid is True
    assert len(warnings) >= 3
    assert df_clean is not None

def test_missing_values_handled_gracefully():
    sparse_patient = {
        'time_in_hospital': None,
        'num_lab_procedures': np.nan,
        'race': '?',
        'diag_1': '?'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(sparse_patient)
    assert is_valid is True
    assert len(errors) == 0
    assert df_clean['time_in_hospital'].isna().iloc[0]

def test_clinical_threshold_classification():
    # Below 0.45 threshold -> Negative / Low Risk
    res_low = classify_readmission_risk(0.25, threshold=0.45)
    assert res_low['is_readmission_predicted'] is False
    assert res_low['tier_label'] == 'LOW RISK'

    # Near 0.45 threshold -> Borderline
    res_borderline = classify_readmission_risk(0.46, threshold=0.45)
    assert res_borderline['is_readmission_predicted'] is True
    assert res_borderline['tier_label'] == 'BORDERLINE / MODERATE RISK'

    # Well above 0.50 -> High Risk
    res_high = classify_readmission_risk(0.72, threshold=0.45)
    assert res_high['is_readmission_predicted'] is True
    assert res_high['tier_label'] == 'HIGH RISK'


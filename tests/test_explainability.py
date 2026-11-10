"""
Unit tests for TreeSHAP local feature attribution.
"""

import pytest
import joblib
from src.explainability import ClinicalExplainer
from src.validation import validate_and_sanitize_patient_input

def test_shap_explanation_structure():
    preprocessor = joblib.load('models/preprocessor.joblib')
    explainer = ClinicalExplainer()

    patient = {
        'race': 'Caucasian', 'gender': 'Female', 'age': '[70-80)', 'admission_type_id': '1',
        'discharge_disposition_id': '1', 'admission_source_id': '7', 'medical_specialty': 'Missing',
        'time_in_hospital': 6, 'num_lab_procedures': 58, 'num_procedures': 2, 'num_medications': 22,
        'number_outpatient': 1, 'number_emergency': 1, 'number_inpatient': 3, 'number_diagnoses': 9,
        'diag_1': '428', 'insulin': 'Up', 'change': 'Ch', 'diabetesMed': 'Yes'
    }
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(patient)
    assert is_valid is True

    X_trans = preprocessor.transform(df_clean)
    explanation = explainer.explain_patient(X_trans, top_k=5)

    assert 'top_factors' in explanation
    assert len(explanation['top_factors']) == 5
    for f in explanation['top_factors']:
        assert 'feature' in f
        assert 'shap_impact' in f
        assert 'direction' in f
        assert f['direction'] in ['Increases Risk', 'Decreases Risk']


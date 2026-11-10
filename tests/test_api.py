"""
Integration tests for FastAPI endpoints: GET /health and POST /predict.
"""

import pytest
from fastapi.testclient import TestClient
from src.api import api_app, load_model_artifacts

@pytest.fixture(scope="module")
def client():
    load_model_artifacts()
    with TestClient(api_app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["selected_model"] == "XGBoost Classifier"
    assert data["decision_threshold"] == 0.45

def test_predict_endpoint_valid_patient(client):
    payload = {
        "race": "Caucasian",
        "gender": "Female",
        "age": "[70-80)",
        "time_in_hospital": 6,
        "num_lab_procedures": 58,
        "num_procedures": 2,
        "num_medications": 22,
        "number_outpatient": 1,
        "number_emergency": 1,
        "number_inpatient": 3,
        "number_diagnoses": 9,
        "diag_1": "428",
        "insulin": "Up",
        "change": "Ch",
        "diabetesMed": "Yes"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["is_readmission_predicted"] is True
    assert data["probability"] >= 0.45
    assert data["decision_threshold"] == 0.45

def test_predict_endpoint_boundary_violation(client):
    payload = {
        "time_in_hospital": 999, # Out of pydantic bounds
        "num_lab_procedures": 40,
        "num_medications": 10,
        "number_diagnoses": 5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422 # Unprocessable Entity

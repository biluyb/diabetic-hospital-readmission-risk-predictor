"""
FastAPI REST API Microservice for GlucoShield CDSS.
Provides machine-to-machine prediction endpoints for hospital EHR integration.
Endpoints:
  GET  /health   -> Service health check and loaded artifact status
  POST /predict  -> Validated patient encounter risk prediction and classification
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import joblib
import pandas as pd
from src.validation import (
    validate_and_sanitize_patient_input,
    classify_readmission_risk,
    CLINICAL_DECISION_THRESHOLD
)

api_app = FastAPI(
    title="GlucoShield CDSS API",
    description="RESTful Clinical Decision Support API for 30-Day Hospital Readmission Risk Prediction",
    version="1.0.0"
)

# Global artifacts cache
artifacts = {}

@api_app.on_event("startup")
def load_model_artifacts():
    try:
        artifacts['preprocessor'] = joblib.load('models/preprocessor.joblib')
        artifacts['xgb'] = joblib.load('models/xgboost_final_model.joblib')
        artifacts['feature_names'] = joblib.load('models/feature_names.joblib')
        artifacts['status'] = 'READY'
    except Exception as e:
        artifacts['status'] = f'ERROR: {str(e)}'

class PatientEncounterRequest(BaseModel):
    race: Optional[str] = Field("Caucasian", description="Racial background")
    gender: Optional[str] = Field("Female", description="Biological sex")
    age: Optional[str] = Field("[60-70)", description="Age bracket")
    admission_type_id: Optional[str] = Field("1", description="1: Emergency, 2: Urgent, 3: Elective")
    discharge_disposition_id: Optional[str] = Field("1", description="Discharge destination code")
    admission_source_id: Optional[str] = Field("7", description="Admission source code")
    time_in_hospital: float = Field(..., ge=1, le=30, description="Length of stay (1-30 days)")
    num_lab_procedures: float = Field(..., ge=1, le=150, description="Lab procedure count")
    num_procedures: float = Field(0, ge=0, le=15, description="Non-lab procedure count")
    num_medications: float = Field(..., ge=1, le=100, description="Medication count")
    number_outpatient: float = Field(0, ge=0, le=50, description="Outpatient visits in past year")
    number_emergency: float = Field(0, ge=0, le=50, description="ER visits in past year")
    number_inpatient: float = Field(0, ge=0, le=20, description="Inpatient stays in past year")
    number_diagnoses: float = Field(..., ge=1, le=16, description="Diagnoses count (1-16)")
    diag_1: Optional[str] = Field("250.00", description="Primary ICD-9 diagnosis code")
    diag_2: Optional[str] = Field("?", description="Secondary ICD-9 code")
    diag_3: Optional[str] = Field("?", description="Tertiary ICD-9 code")
    A1Cresult: Optional[str] = Field("None", description="HbA1c test result")
    max_glu_serum: Optional[str] = Field("None", description="Serum glucose test result")
    insulin: Optional[str] = Field("Steady", description="Insulin dosage adjustment: No, Steady, Up, Down")
    change: Optional[str] = Field("No", description="Medication change indicator: Ch, No")
    diabetesMed: Optional[str] = Field("Yes", description="Prescribed diabetes med: Yes, No")
    medical_specialty: Optional[str] = Field("Missing", description="Admitting medical specialty")

class PredictionResponse(BaseModel):
    status: str
    probability: float
    decision_threshold: float
    is_readmission_predicted: bool
    risk_tier: str
    action_summary: str
    warnings: List[str]

@api_app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Returns system status and model readiness."""
    is_ready = artifacts.get('status') == 'READY'
    return {
        "status": "HEALTHY" if is_ready else "UNHEALTHY",
        "service": "GlucoShield CDSS API",
        "model_status": artifacts.get('status', 'NOT_INITIALIZED'),
        "selected_model": "XGBoost Classifier",
        "decision_threshold": CLINICAL_DECISION_THRESHOLD
    }

@api_app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict_readmission(payload: PatientEncounterRequest):
    """
    Accepts patient encounter parameters, validates clinical bounds,
    and returns 30-day readmission risk probability and tier.
    """
    if artifacts.get('status') != 'READY':
        load_model_artifacts()
        if artifacts.get('status') != 'READY':
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model artifacts are not ready or failed to load."
            )

    raw_dict = payload.model_dump()
    is_valid, errors, warnings, df_clean = validate_and_sanitize_patient_input(raw_dict)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )

    try:
        X_trans = artifacts['preprocessor'].transform(df_clean)
        prob = float(artifacts['xgb'].predict_proba(X_trans)[0, 1])
        classification = classify_readmission_risk(prob, threshold=CLINICAL_DECISION_THRESHOLD)

        return PredictionResponse(
            status="SUCCESS",
            probability=round(prob, 4),
            decision_threshold=CLINICAL_DECISION_THRESHOLD,
            is_readmission_predicted=classification['is_readmission_predicted'],
            risk_tier=classification['tier_label'],
            action_summary=classification['action_summary'],
            warnings=warnings
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline execution error: {str(e)}"
        )


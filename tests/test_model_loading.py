"""
Unit tests for serialized model artifacts and metadata integrity.
"""

import os
import joblib
import pytest
from xgboost import XGBClassifier
from sklearn.compose import ColumnTransformer

def test_model_artifact_existence():
    assert os.path.exists('models/xgboost_final_model.joblib'), "XGBoost model artifact missing"
    assert os.path.exists('models/preprocessor.joblib'), "Preprocessor artifact missing"
    assert os.path.exists('models/feature_names.joblib'), "Feature names artifact missing"
    assert os.path.exists('models/feature_metadata.joblib'), "Feature metadata artifact missing"

def test_model_loading_types():
    xgb = joblib.load('models/xgboost_final_model.joblib')
    assert isinstance(xgb, XGBClassifier)
    
    preprocessor = joblib.load('models/preprocessor.joblib')
    assert isinstance(preprocessor, ColumnTransformer)

    feature_names = joblib.load('models/feature_names.joblib')
    assert isinstance(feature_names, list)
    assert len(feature_names) > 20

    metadata = joblib.load('models/feature_metadata.joblib')
    assert 'numeric_features' in metadata
    assert 'categorical_features' in metadata


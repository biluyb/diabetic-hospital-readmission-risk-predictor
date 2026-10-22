"""
SHAP Explainability Module for Diabetes Readmission CDSS.
Provides local and global patient-level feature explanations using TreeSHAP.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
import shap

class ClinicalExplainer:
    def __init__(self, model_path='models/xgboost_final_model.joblib', feature_names_path='models/feature_names.joblib'):
        self.model = joblib.load(model_path)
        self.feature_names = joblib.load(feature_names_path)
        # TreeExplainer is extremely fast for XGBoost
        self.explainer = shap.TreeExplainer(self.model)

    def explain_patient(self, transformed_row, top_k=5):
        """
        Computes patient-specific SHAP values and returns top risk-increasing
        and risk-decreasing factors.
        """
        # Ensure 2D array
        if transformed_row.ndim == 1:
            transformed_row = transformed_row.reshape(1, -1)

        shap_values = self.explainer.shap_values(transformed_row)
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        elif shap_values.ndim == 2:
            sv = shap_values[0]
        else:
            sv = shap_values

        # Pair features with SHAP contributions
        feature_impacts = []
        for name, val, impact in zip(self.feature_names, transformed_row[0], sv):
            if abs(impact) > 1e-4:
                feature_impacts.append({
                    'feature': name,
                    'transformed_value': float(val),
                    'shap_impact': float(impact),
                    'direction': 'Increases Risk' if impact > 0 else 'Decreases Risk'
                })

        # Sort by absolute magnitude of SHAP contribution
        feature_impacts.sort(key=lambda x: abs(x['shap_impact']), reverse=True)
        top_factors = feature_impacts[:top_k]

        return {
            'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
            'top_factors': top_factors,
            'all_impacts': feature_impacts
        }

if __name__ == '__main__':
    explainer = ClinicalExplainer()
    print("ClinicalExplainer successfully initialized with TreeSHAP.")

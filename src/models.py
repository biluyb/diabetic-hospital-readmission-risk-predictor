"""
Model Training, Comparison, and Improvement Module for Diabetes Readmission CDSS.
Module 5: Stage 5 (Baseline) & Stage 6 (Train & Improve the Model)
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    roc_auc_score, recall_score, precision_score, f1_score, accuracy_score,
    confusion_matrix, roc_curve, average_precision_score
)
from src.data_pipeline import prepare_train_test_data

def train_and_evaluate_models():
    print("--> Preparing train and test datasets...")
    data = prepare_train_test_data()
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_train']
    y_test = data['y_test']
    feature_names = data['feature_names']

    # Imbalance scale factor
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    scale_pos_weight = neg_count / pos_count
    print(f"--> Training class counts: Negative (0) = {neg_count}, Positive (1) = {pos_count}, Scale weight = {scale_pos_weight:.2f}")

    results = []

    # -------------------------------------------------------------
    # 0. Trivial Reference: Majority Class Predictor
    # -------------------------------------------------------------
    y_pred_trivial = np.zeros_like(y_test)
    results.append({
        'Model': 'Trivial Majority Baseline',
        'Train ROC-AUC': 0.5000,
        'Test ROC-AUC': 0.5000,
        'Accuracy': accuracy_score(y_test, y_pred_trivial),
        'Precision': 0.0,
        'Recall': 0.0,
        'F1': 0.0,
        'Notes': 'Always predicts 0 (no readmission). High accuracy artifact of imbalance, zero clinical utility.'
    })

    # -------------------------------------------------------------
    # 1. Baseline Model: Regularized Logistic Regression (Balanced)
    # -------------------------------------------------------------
    print("\n--> [1/4] Training Baseline: Logistic Regression (L2, class_weight='balanced')...")
    lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42, solver='lbfgs')
    lr.fit(X_train, y_train)

    train_probs_lr = lr.predict_proba(X_train)[:, 1]
    test_probs_lr = lr.predict_proba(X_test)[:, 1]
    test_preds_lr = (test_probs_lr >= 0.5).astype(int)

    results.append({
        'Model': 'Logistic Regression (Baseline)',
        'Train ROC-AUC': roc_auc_score(y_train, train_probs_lr),
        'Test ROC-AUC': roc_auc_score(y_test, test_probs_lr),
        'Accuracy': accuracy_score(y_test, test_preds_lr),
        'Precision': precision_score(y_test, test_preds_lr, zero_division=0),
        'Recall': recall_score(y_test, test_preds_lr),
        'F1': f1_score(y_test, test_preds_lr),
        'Notes': 'Linear benchmark. Captures additive effects, but misses non-linear medication/diagnosis interactions.'
    })

    # -------------------------------------------------------------
    # 2. Candidate Model 1: Random Forest Classifier
    # -------------------------------------------------------------
    print("\n--> [2/4] Training Candidate 1: Random Forest (class_weight='balanced_subsample')...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    train_probs_rf = rf.predict_proba(X_train)[:, 1]
    test_probs_rf = rf.predict_proba(X_test)[:, 1]
    test_preds_rf = (test_probs_rf >= 0.5).astype(int)

    results.append({
        'Model': 'Random Forest Classifier',
        'Train ROC-AUC': roc_auc_score(y_train, train_probs_rf),
        'Test ROC-AUC': roc_auc_score(y_test, test_probs_rf),
        'Accuracy': accuracy_score(y_test, test_preds_rf),
        'Precision': precision_score(y_test, test_preds_rf, zero_division=0),
        'Recall': recall_score(y_test, test_preds_rf),
        'F1': f1_score(y_test, test_preds_rf),
        'Notes': 'Ensemble of decision trees. Resilient to outliers, but constrained by high tree-bagging memory footprint.'
    })

    # -------------------------------------------------------------
    # 3. Candidate Model 2: XGBoost Classifier (Tuned)
    # -------------------------------------------------------------
    print("\n--> [3/4] Training Candidate 2: XGBoost Classifier (scale_pos_weight tuned)...")
    xgb = XGBClassifier(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=0.5,
        reg_lambda=2.0,
        random_state=42,
        eval_metric='auc',
        n_jobs=-1
    )
    xgb.fit(X_train, y_train)

    train_probs_xgb = xgb.predict_proba(X_train)[:, 1]
    test_probs_xgb = xgb.predict_proba(X_test)[:, 1]
    test_preds_xgb = (test_probs_xgb >= 0.5).astype(int)

    results.append({
        'Model': 'XGBoost Classifier (Proposed Primary)',
        'Train ROC-AUC': roc_auc_score(y_train, train_probs_xgb),
        'Test ROC-AUC': roc_auc_score(y_test, test_probs_xgb),
        'Accuracy': accuracy_score(y_test, test_preds_xgb),
        'Precision': precision_score(y_test, test_preds_xgb, zero_division=0),
        'Recall': recall_score(y_test, test_preds_xgb),
        'F1': f1_score(y_test, test_preds_xgb),
        'Notes': 'Gradient boosted trees with L1/L2 regularization. Best ROC-AUC & Recall balance, fast inference.'
    })

    # -------------------------------------------------------------
    # 4. Candidate Model 3: LightGBM Classifier
    # -------------------------------------------------------------
    print("\n--> [4/4] Training Candidate 3: LightGBM Classifier (scale_pos_weight)...")
    lgbm = LGBMClassifier(
        n_estimators=250,
        max_depth=5,
        num_leaves=25,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=scale_pos_weight,
        reg_alpha=0.5,
        reg_lambda=2.0,
        random_state=42,
        verbose=-1,
        n_jobs=-1
    )
    lgbm.fit(X_train, y_train)

    train_probs_lgbm = lgbm.predict_proba(X_train)[:, 1]
    test_probs_lgbm = lgbm.predict_proba(X_test)[:, 1]
    test_preds_lgbm = (test_probs_lgbm >= 0.5).astype(int)

    results.append({
        'Model': 'LightGBM Classifier',
        'Train ROC-AUC': roc_auc_score(y_train, train_probs_lgbm),
        'Test ROC-AUC': roc_auc_score(y_test, test_probs_lgbm),
        'Accuracy': accuracy_score(y_test, test_preds_lgbm),
        'Precision': precision_score(y_test, test_preds_lgbm, zero_division=0),
        'Recall': recall_score(y_test, test_preds_lgbm),
        'F1': f1_score(y_test, test_preds_lgbm),
        'Notes': 'Histogram-based gradient boosting. Competitive ROC-AUC with ultra-lightweight training memory.'
    })

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)
    print("\n================== MODEL COMPARISON TABLE ==================")
    print(df_results[['Model', 'Train ROC-AUC', 'Test ROC-AUC', 'Accuracy', 'Precision', 'Recall', 'F1']].to_string(index=False))

    # Serialize trained models
    print("\n--> Serializing trained models to models/ ...")
    joblib.dump(lr, 'models/logistic_regression_baseline.joblib')
    joblib.dump(rf, 'models/random_forest_model.joblib')
    joblib.dump(xgb, 'models/xgboost_final_model.joblib')
    joblib.dump(lgbm, 'models/lightgbm_model.joblib')

    # Return trained objects & probabilities for evaluation module
    return {
        'df_results': df_results,
        'models': {'Baseline_LR': lr, 'Random_Forest': rf, 'XGBoost': xgb, 'LightGBM': lgbm},
        'test_probs': {
            'Baseline_LR': test_probs_lr,
            'Random_Forest': test_probs_rf,
            'XGBoost': test_probs_xgb,
            'LightGBM': test_probs_lgbm
        },
        'y_test': y_test,
        'X_test': X_test,
        'X_train': X_train,
        'y_train': y_train,
        'feature_names': feature_names
    }

if __name__ == '__main__':
    train_and_evaluate_models()

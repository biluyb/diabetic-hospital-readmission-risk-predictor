"""
Simulated Production Monitoring Pipeline for GlucoShield CDSS.
Tracks prediction volumes, risk score distributions, input quality, data drift,
and delayed ground-truth model performance degradation.

IMPORTANT TRANSPARENCY NOTICE:
Production batches analyzed in this module are generated as SIMULATED MONITORING DATA
for educational demonstration in FUSE AI-201. They represent realistic clinical scenarios
(e.g., seasonal respiratory surges, elderly demographic shifts) and are NOT claimed as
live production hospital telemetry.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_auc_score, recall_score, precision_score
from monitoring.drift_detector import perform_drift_analysis
from src.validation import CLINICAL_DECISION_THRESHOLD

def generate_simulated_monitoring_batches(base_test_path="data/diabetic_data.csv", n_samples=2500, random_state=42):
    """
    Generates two distinct simulated monitoring batches:
    - Batch 1 (Month 1): Stable Inpatient Flow (Distribution closely mimics reference test set)
    - Batch 2 (Month 2): Winter Respiratory Surge & Demographic Aging (Shifted distribution with higher age and respiratory diagnoses)
    """
    from src.data_pipeline import clean_and_prepare_data
    df = clean_and_prepare_data(csv_path=base_test_path, verbose=False)

    np.random.seed(random_state)
    
    # 1. Baseline Reference Dataset (Holdout split representation)
    ref_df = df.sample(n=min(5000, len(df)), random_state=random_state).copy()

    # 2. Batch 1: Stable Operations (Month 1)
    batch_1 = df.sample(n=n_samples, random_state=random_state + 1).copy()
    batch_1['batch_id'] = 'SIMULATED_MONTH_01_STABLE'

    # 3. Batch 2: Winter Surge / Shifted Operations (Month 2)
    # Simulate realistic demographic aging and seasonal illness drift
    batch_2 = df.sample(n=n_samples, random_state=random_state + 2).copy()
    
    # Induce mild realistic drift:
    # Increased length of stay for seasonal illness (+1.2 days)
    batch_2['time_in_hospital'] = np.clip(batch_2['time_in_hospital'] + np.random.choice([0, 1, 2, 3], size=len(batch_2), p=[0.4, 0.3, 0.2, 0.1]), 1, 14)
    # Increase prior inpatient encounters
    batch_2['number_inpatient'] = np.clip(batch_2['number_inpatient'] + np.random.choice([0, 1, 2], size=len(batch_2), p=[0.7, 0.2, 0.1]), 0, 20)
    # Total prior visits recalculation
    batch_2['total_prior_visits'] = batch_2['number_outpatient'] + batch_2['number_emergency'] + batch_2['number_inpatient']
    batch_2['procedure_intensity'] = (batch_2['num_lab_procedures'] + batch_2['num_procedures']) / (batch_2['time_in_hospital'] + 1e-5)
    # Increase proportion of respiratory primary diagnoses
    resp_mask = np.random.rand(len(batch_2)) < 0.25
    batch_2.loc[resp_mask, 'diag_1_group'] = 'Respiratory'
    # Shift age towards elderly bracket
    elderly_mask = np.random.rand(len(batch_2)) < 0.35
    batch_2.loc[elderly_mask, 'age'] = '[70-80)'
    batch_2.loc[elderly_mask, 'age_num'] = 75
    batch_2['batch_id'] = 'SIMULATED_MONTH_02_WINTER_SURGE'

    return ref_df, batch_1, batch_2

def run_monitoring_evaluation(output_dir="plots"):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")

    print("--> Initializing Monitoring and Model Drift Evaluation...")
    ref_df, batch_1, batch_2 = generate_simulated_monitoring_batches()

    preprocessor = joblib.load('models/preprocessor.joblib')
    xgb = joblib.load('models/xgboost_final_model.joblib')

    # Continuous & Categorical feature subsets for drift tracking
    numeric_cols = ['time_in_hospital', 'num_lab_procedures', 'num_medications', 'number_inpatient', 'total_prior_visits']
    categorical_cols = ['age', 'diag_1_group', 'admission_type_id', 'A1Cresult', 'insulin']

    # 1. Run Drift Detection
    print("--> Computing Drift Metrics (PSI & KS Test)...")
    drift_b1 = perform_drift_analysis(ref_df, batch_1, numeric_cols, categorical_cols)
    drift_b2 = perform_drift_analysis(ref_df, batch_2, numeric_cols, categorical_cols)

    # 2. Score Batches and Track Risk Distributions
    def score_batch(df_batch):
        X_trans = preprocessor.transform(df_batch)
        probs = xgb.predict_proba(X_trans)[:, 1]
        preds = (probs >= CLINICAL_DECISION_THRESHOLD).astype(int)
        
        # Risk tiers
        low_pct = np.mean(probs < 0.40) * 100
        mod_pct = np.mean((probs >= 0.40) & (probs < 0.50)) * 100
        high_pct = np.mean(probs >= 0.50) * 100
        
        # Performance if ground truth is available
        y_true = df_batch['target'].values
        auc = roc_auc_score(y_true, probs)
        rec = recall_score(y_true, preds)
        prec = precision_score(y_true, preds, zero_division=0)

        return {
            'probs': probs,
            'preds': preds,
            'total_encounters': len(df_batch),
            'mean_risk': float(np.mean(probs)),
            'pct_flagged_high_risk': float(np.mean(preds) * 100),
            'tier_low_pct': float(low_pct),
            'tier_mod_pct': float(mod_pct),
            'tier_high_pct': float(high_pct),
            'roc_auc': float(auc),
            'recall_th045': float(rec),
            'precision_th045': float(prec)
        }

    res_ref = score_batch(ref_df)
    res_b1 = score_batch(batch_1)
    res_b2 = score_batch(batch_2)

    # 3. Create Monitoring Comparison Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # A. Predicted Risk Probability Distributions
    sns.kdeplot(res_ref['probs'], ax=axes[0], label="Baseline Holdout (n=5,000)", color="#2b5c8f", linewidth=2)
    sns.kdeplot(res_b1['probs'], ax=axes[0], label="Simulated Month 1: Stable (n=2,500)", color="#70ad47", linestyle="--", linewidth=2)
    sns.kdeplot(res_b2['probs'], ax=axes[0], label="Simulated Month 2: Winter Surge (n=2,500)", color="#d9534f", linewidth=2)
    axes[0].axvline(CLINICAL_DECISION_THRESHOLD, color='black', linestyle=':', label=f"Clinical Threshold ({CLINICAL_DECISION_THRESHOLD})")
    axes[0].set_title("Predicted Risk Distribution Shift Across Monitoring Batches", fontsize=11, fontweight='bold')
    axes[0].set_xlabel("Predicted 30-Day Readmission Probability")
    axes[0].set_ylabel("Density")
    axes[0].legend(loc="upper right", fontsize=8.5)

    # B. Population Stability Index (PSI) per Clinical Feature
    psi_features = ['time_in_hospital', 'number_inpatient', 'total_prior_visits', 'num_lab_procedures', 'age', 'diag_1_group']
    psi_vals_b1 = [drift_b1[f]['psi'] for f in psi_features]
    psi_vals_b2 = [drift_b2[f]['psi'] for f in psi_features]

    x = np.arange(len(psi_features))
    width = 0.35
    axes[1].bar(x - width/2, psi_vals_b1, width, label='Month 1 vs Baseline', color='#70ad47', edgecolor='#4b752f')
    axes[1].bar(x + width/2, psi_vals_b2, width, label='Month 2 Surge vs Baseline', color='#d9534f', edgecolor='#990000')
    axes[1].axhline(0.10, color='orange', linestyle='--', label='Warning Threshold (PSI = 0.10)')
    axes[1].axhline(0.25, color='red', linestyle='--', label='Retraining Alert (PSI = 0.25)')
    axes[1].set_title("Feature Population Stability Index (PSI) Comparison", fontsize=11, fontweight='bold')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f.replace('_', '\n') for f in psi_features], fontsize=8.5)
    axes[1].set_ylabel("PSI Value")
    axes[1].set_ylim(0, max(max(psi_vals_b2), 0.35) * 1.2)
    axes[1].legend(loc="upper left", fontsize=8.5)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'monitoring_drift.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved monitoring visualization: {plot_path}")

    # Retraining Recommendation Logic
    high_drift_features = [f for f, v in drift_b2.items() if v['drift_status'] == 'HIGH_DRIFT']
    retraining_triggered = len(high_drift_features) > 0 or (res_b2['roc_auc'] < (res_ref['roc_auc'] - 0.05))

    monitoring_summary = {
        'baseline': res_ref,
        'month_1_stable': res_b1,
        'month_2_surge': res_b2,
        'drift_month_1': drift_b1,
        'drift_month_2': drift_b2,
        'high_drift_features_month_2': high_drift_features,
        'retraining_recommended': retraining_triggered,
        'plot_path': plot_path
    }
    
    return monitoring_summary

if __name__ == '__main__':
    run_monitoring_evaluation()


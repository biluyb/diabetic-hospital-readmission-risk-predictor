"""
Reproducible Experiment Tracking Engine for GlucoShield CDSS.
Provides structured experiment logging to JSON and CSV formats without heavyweight cloud dependencies.
Records model lineage, hyperparameter configurations, evaluation metrics, thresholds, and artifact references.
"""

import os
import json
import time
import pandas as pd
from datetime import datetime

DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'evaluation')

class ExperimentTracker:
    def __init__(self, log_dir=DEFAULT_LOG_DIR):
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.json_path = os.path.join(self.log_dir, 'experiment_runs.json')
        self.csv_path = os.path.join(self.log_dir, 'experiment_runs.csv')

    def log_run(self, run_id: str, model_name: str, model_family: str, hyperparameters: dict,
                training_config: dict, metrics: dict, artifact_path: str, notes: str = ""):
        """
        Logs a single experiment run.
        """
        run_record = {
            'run_id': run_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'model_name': model_name,
            'model_family': model_family,
            'hyperparameters': hyperparameters,
            'training_config': training_config,
            'metrics': metrics,
            'artifact_path': artifact_path,
            'notes': notes
        }

        # Load existing JSON log
        runs = []
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r') as f:
                    runs = json.load(f)
            except Exception:
                runs = []

        # Update or append
        existing_idx = next((i for i, r in enumerate(runs) if r['run_id'] == run_id), None)
        if existing_idx is not None:
            runs[existing_idx] = run_record
        else:
            runs.append(run_record)

        # Save JSON
        with open(self.json_path, 'w') as f:
            json.dump(runs, f, indent=2)

        # Export flat CSV for easy inspection & tabular display
        flat_records = []
        for r in runs:
            flat_row = {
                'run_id': r['run_id'],
                'timestamp': r['timestamp'],
                'model_name': r['model_name'],
                'model_family': r['model_family'],
                'artifact_path': r['artifact_path'],
                'notes': r['notes']
            }
            # Add metrics
            for k, v in r['metrics'].items():
                flat_row[f'metric_{k}'] = v
            # Add key hyperparams
            for k, v in r['hyperparameters'].items():
                flat_row[f'hp_{k}'] = str(v)
            flat_records.append(flat_row)

        df_flat = pd.DataFrame(flat_records)
        df_flat.to_csv(self.csv_path, index=False)
        return run_record

    def get_runs_table(self):
        """Returns comparison table of all logged runs as a pandas DataFrame."""
        if os.path.exists(self.csv_path):
            return pd.read_csv(self.csv_path)
        return pd.DataFrame()

def populate_default_experiments():
    """
    Populates historical benchmark experiments from verified Module 5 training runs.
    """
    tracker = ExperimentTracker()

    training_config_shared = {
        'dataset': 'UCI Diabetes 130-US Hospitals (1999-2008)',
        'cohort_clean_size': 69990,
        'train_samples': 55989,
        'test_samples': 13998,
        'train_test_split': '80/20 Stratified',
        'random_state': 42,
        'target_variable': 'readmitted (<30d vs >=30d/None)',
        'positive_class_ratio': '8.98%',
        'features_total': 155
    }

    # 1. Trivial Majority Baseline
    tracker.log_run(
        run_id="EXP-001-TRIVIAL",
        model_name="Trivial Majority Baseline",
        model_family="Heuristic / Majority Vote",
        hyperparameters={'strategy': 'predict_constant_zero'},
        training_config=training_config_shared,
        metrics={
            'test_roc_auc': 0.5000,
            'clinical_recall_th045': 0.0000,
            'precision': 0.0000,
            'accuracy': 0.9102,
            'f1_score': 0.0000,
            'decision_threshold': 0.50
        },
        artifact_path="N/A",
        notes="Reference baseline predicting zero readmissions. Demonstrates class imbalance accuracy trap."
    )

    # 2. Logistic Regression
    tracker.log_run(
        run_id="EXP-002-LOGREG",
        model_name="Regularized Logistic Regression",
        model_family="Linear Classifier",
        hyperparameters={'solver': 'lbfgs', 'C': 1.0, 'max_iter': 1000, 'class_weight': 'balanced', 'penalty': 'l2'},
        training_config=training_config_shared,
        metrics={
            'test_roc_auc': 0.6469,
            'clinical_recall_th045': 0.5306,
            'precision': 0.1388,
            'accuracy': 0.6622,
            'f1_score': 0.2201,
            'decision_threshold': 0.45
        },
        artifact_path="models/logistic_regression_baseline.joblib",
        notes="Linear benchmark model with L2 regularization and balanced class weighting."
    )

    # 3. Random Forest
    tracker.log_run(
        run_id="EXP-003-RF",
        model_name="Random Forest Classifier",
        model_family="Ensemble Bagging",
        hyperparameters={'n_estimators': 200, 'max_depth': 12, 'min_samples_split': 20, 'min_samples_leaf': 10, 'class_weight': 'balanced_subsample'},
        training_config=training_config_shared,
        metrics={
            'test_roc_auc': 0.6462,
            'train_roc_auc': 0.8051,
            'clinical_recall_th045': 0.4391,
            'precision': 0.1582,
            'accuracy': 0.7397,
            'f1_score': 0.2326,
            'decision_threshold': 0.45
        },
        artifact_path="models/random_forest_model.joblib",
        notes="Ensemble tree model showing train-test generalization gap (0.805 vs 0.646)."
    )

    # 4. LightGBM
    tracker.log_run(
        run_id="EXP-004-LGBM",
        model_name="LightGBM Classifier",
        model_family="Gradient Boosted Trees",
        hyperparameters={'n_estimators': 250, 'max_depth': 5, 'num_leaves': 25, 'learning_rate': 0.04, 'subsample': 0.85, 'scale_pos_weight': 10.14, 'reg_alpha': 0.5, 'reg_lambda': 2.0},
        training_config=training_config_shared,
        metrics={
            'test_roc_auc': 0.6465,
            'clinical_recall_th045': 0.5370,
            'precision': 0.1384,
            'accuracy': 0.6582,
            'f1_score': 0.2201,
            'decision_threshold': 0.45
        },
        artifact_path="models/lightgbm_model.joblib",
        notes="Fast histogram-based gradient boosting classifier."
    )

    # 5. XGBoost (Selected Primary Model)
    tracker.log_run(
        run_id="EXP-005-XGBOOST-FINAL",
        model_name="XGBoost Classifier (Selected Primary)",
        model_family="Gradient Boosted Trees",
        hyperparameters={'n_estimators': 250, 'max_depth': 5, 'learning_rate': 0.04, 'subsample': 0.85, 'colsample_bytree': 0.85, 'scale_pos_weight': 10.14, 'reg_alpha': 0.5, 'reg_lambda': 2.0, 'eval_metric': 'auc'},
        training_config=training_config_shared,
        metrics={
            'test_roc_auc': 0.6465,
            'pr_auc': 0.1580,
            'clinical_recall_th045': 0.6571,
            'specificity_th045': 0.5454,
            'precision_th045': 0.1248,
            'accuracy_th045': 0.5554,
            'f1_score_th045': 0.2098,
            'decision_threshold': 0.45,
            'true_positives': 826,
            'false_negatives': 431,
            'true_negatives': 6949,
            'false_positives': 5792
        },
        artifact_path="models/xgboost_final_model.joblib",
        notes="Selected primary operational model. Meets clinical safety sensitivity target (Recall >= 65%) at th=0.45."
    )
    print(f"Logged 5 benchmark experiments to {tracker.json_path} and {tracker.csv_path}")

if __name__ == '__main__':
    populate_default_experiments()


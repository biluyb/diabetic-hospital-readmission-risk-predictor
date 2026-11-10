# GlucoShield CDSS — Experiment Tracking & Model Lineage

**FUSE AI-201 Capstone | Module 6: Reproducible Experiment Tracking**  
**Project:** GlucoShield Diabetic Readmission CDSS  
**Group:** Group 04 (YEEAP Capstone)  

---

## 1. Tracking Methodology & Architecture

In educational capstones and clinical research pilots, heavyweight cloud tracking servers (such as hosted MLflow or Weights & Biases) often introduce external network dependencies, authentication hurdles, and credential rot. 

To ensure **100% offline reproducibility, zero-credential portability, and strict version-control alignment**, GlucoShield implements a **structured JSON & CSV Experiment Tracking Engine** (`src/experiment_tracker.py`).

### Key Features
- **Git-Integrated Lineage:** Experiment runs are logged directly into `evaluation/experiment_runs.json` and mirrored in flat `evaluation/experiment_runs.csv`, making model lineage trackable through standard Git commits.
- **Comprehensive Metadata:** Every run records model architecture, hyperparameter dictionary, data split configuration, class weighting factors, decision thresholds, and complete evaluation metrics (ROC-AUC, PR-AUC, Sensitivity @ 0.45, Specificity @ 0.45, Precision, Accuracy, and F1).
- **Artifact Traceability:** Logs exact paths to serialized model weights in `models/` for end-to-end auditability.

---

## 2. Benchmark Experiment Comparison Table

The following runs represent verified holdout evaluations ($n = 13,998$ test encounters) conducted under identical stratified 80/20 train/test conditions (`random_state=42`):

| Run ID | Model Name | Model Family | Test ROC-AUC | PR-AUC | Recall (th=0.45) | Specificity (th=0.45) | Precision (th=0.45) | Model Artifact |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `EXP-001-TRIVIAL` | Trivial Majority Baseline | Heuristic | 0.5000 | 0.0898 | 0.00% | 100.00% | 0.00% | N/A |
| `EXP-002-LOGREG` | Logistic Regression | Linear (L2) | 0.6469 | 0.1572 | 53.06% | 67.51% | 13.88% | `models/logistic_regression_baseline.joblib` |
| `EXP-003-RF` | Random Forest | Bagging Tree | 0.6462 | 0.1554 | 43.91% | 76.92% | 15.82% | `models/random_forest_model.joblib` |
| `EXP-004-LGBM` | LightGBM Classifier | Boosting Tree| 0.6465 | 0.1570 | 53.70% | 67.01% | 13.84% | `models/lightgbm_model.joblib` |
| `EXP-005-XGBOOST-FINAL`| **XGBoost (Selected Primary)**| **Boosting Tree**| **0.6465** | **0.1580** | **65.71%** | **54.54%** | **12.48%** | `models/xgboost_final_model.joblib` |

---

## 3. Detailed Parameter Schema of Selected Primary Model

- **Model Identifier:** `EXP-005-XGBOOST-FINAL`
- **Algorithm:** Extreme Gradient Boosting (`XGBClassifier`)
- **Key Hyperparameters:**
  ```python
  {
      "n_estimators": 250,
      "max_depth": 5,
      "learning_rate": 0.04,
      "subsample": 0.85,
      "colsample_bytree": 0.85,
      "scale_pos_weight": 10.14,
      "reg_alpha": 0.5,
      "reg_lambda": 2.0,
      "eval_metric": "auc",
      "random_state": 42
  }
  ```
- **Clinical Operating Threshold:** `0.45`
- **Confusion Matrix at Operating Cutoff:**
  - True Positives (TP): `826`
  - False Negatives (FN): `431`
  - True Negatives (TN): `6,949`
  - False Positives (FP): `5,792`

---

## 4. How to Log New Experiments

To log an experiment run programmatically:
```python
from src.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker()
tracker.log_run(
    run_id="EXP-006-CANDIDATE",
    model_name="CatBoost Classifier",
    model_family="Gradient Boosted Trees",
    hyperparameters={"depth": 6, "iterations": 300},
    training_config={"train_samples": 55989, "test_samples": 13998},
    metrics={"test_roc_auc": 0.648, "clinical_recall_th045": 0.661},
    artifact_path="models/catboost_candidate.joblib",
    notes="Candidate experiment evaluating alternative tree boosting algorithm."
)
```
Logs are saved automatically to `evaluation/experiment_runs.json` and `evaluation/experiment_runs.csv`.


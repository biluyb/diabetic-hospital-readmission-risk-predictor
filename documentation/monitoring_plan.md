# GlucoShield CDSS — Model Monitoring & Drift Governance Plan

**FUSE AI-201 Capstone | Module 6: Production Monitoring Strategy**  
**System:** GlucoShield Diabetic Readmission CDSS  
**Model Monitored:** Calibrated XGBoost Classifier (`models/xgboost_final_model.joblib`)  
**Operating Decision Threshold:** 0.45  

---

## 1. Objectives of the Monitoring Framework

Clinical machine learning systems operate in dynamic healthcare environments where patient populations, clinical protocols, and hospital practices evolve over time. The GlucoShield monitoring plan establishes an automated, reproducible telemetry framework to ensure:
1. **Input Data Integrity:** Immediate detection of missing values, out-of-range sensor/lab readings, and unexpected categorical coding shifts.
2. **Feature Distribution Stability (Data Drift):** Quantitative tracking of demographic and clinical feature shifts (e.g., changes in inpatient length of stay, elderly cohort surges).
3. **Prediction Stability:** Continuous tracking of predicted risk probability distributions, average risk scores, and the proportion of encounters flagged as high risk.
4. **Model Performance Degradation (Concept Drift):** Periodic reconciliation of predicted risk against 30-day delayed actual readmission outcomes to detect loss of discriminative power (ROC-AUC) or clinical safety (Recall).
5. **Retraining Governance:** Systematic policies for triggering model audits, recalibration, or retraining.

---

## 2. Monitored Telemetry & Quantitative Metrics

### A. Input Data Quality Checks
- **Missing Value Rate:** Monitored per feature across daily/monthly patient batches. Alert triggered if any core clinical feature exceeds 5% missingness (or >55% for sparse fields like `medical_specialty`).
- **Clinical Range Adherence:** Percentage of records triggering boundary warnings (e.g., hospital stays > 14 days, lab tests > 132).
- **Novel Category Ingestion:** Percentage of records with unrecognized categorical inputs (e.g., novel insurance codes, unmapped ICD diagnosis codes) handled by fallback imputers.

### B. Data Drift Metrics
- **Population Stability Index (PSI):**
  - Continuous features: Computed across 10 quantile bins derived from baseline reference data.
  - Categorical features: Computed across shared categorical levels.
  - **Thresholds:**
    - $\text{PSI} < 0.10$: Healthy / Stable (Nominal).
    - $0.10 \le \text{PSI} < 0.25$: Moderate Drift (Warning; heightened monitoring).
    - $\text{PSI} \ge 0.25$: High Drift (Critical Alert; triggers retraining investigation).
- **Two-Sample Kolmogorov-Smirnov (KS) Test:** Evaluates continuous distributions (`time_in_hospital`, `number_inpatient`, `total_prior_visits`). A $p$-value $< 0.01$ indicates statistically significant distribution shift.

### C. Output Prediction Metrics
- **Mean Predicted Risk:** Baseline reference is **53.1%**. A sustained deviation $> \pm 5\%$ signals potential cohort shifts.
- **Positive Flagging Rate:** Proportion of patients scored above the 0.45 clinical cutoff. Baseline reference is **84.7%** (reflecting high sensitivity calibration on inpatient cohorts).

### D. Delayed Ground-Truth Evaluation (30-Day Window)
Hospital readmission labels are subject to a mandatory 30-day lag before reconciliation. Once 30 days elapse:
- **Test ROC-AUC:** Baseline target $\ge 0.65$. An observed drop $> 0.05$ triggers an emergency model review.
- **Clinical Sensitivity (Recall @ 0.45):** Must remain $\ge 65.0\%$. A drop below 60.0% represents a patient safety risk and halts automated inference.

---

## 3. Automated Alerting & Governance Thresholds

| Severity Tier | Trigger Condition | Notification Channel | Required Action |
| :--- | :--- | :--- | :--- |
| **Info (Green)** | $\text{PSI} < 0.10$, missing rate nominal, ROC-AUC stable | Monthly MLOps telemetry dashboard | Routine logging; no operational intervention needed. |
| **Warning (Amber)** | $0.10 \le \text{PSI} < 0.25$ on any key predictor, or missing rate 5–15% | Slack / Email to Lead ML Engineer | Validate data pipelines, check EHR data extraction scripts, monitor cohort characteristics. |
| **Critical Alert (Red)** | $\text{PSI} \ge 0.25$ on key clinical features, or delayed Recall $< 60\%$ | Immediate incident paging to ML Lead & Clinical Board | Freeze model version; activate clinical shadow validation; prepare retrospective retraining dataset. |

---

## 4. Model Retraining and Deployment Workflow

```
[ Drift Alert / Retraining Trigger ]
               │
               ▼
[ 1. Data Ingestion & Causal Hygiene ]
   ├── Extract past 6-12 months of clean inpatient encounters
   ├── Exclude deceased / hospice encounters
   └── Deduplicate repeat admissions (first encounter policy)
               │
               ▼
[ 2. Candidate Model Training & Benchmarking ]
   ├── Train updated XGBoost booster with tuned scale_pos_weight
   ├── Evaluate on independent 20% holdout split
   └── Verify ROC-AUC >= 0.65 and Recall @ 0.45 >= 65%
               │
               ▼
[ 3. Fairness & Subgroup Equity Audit ]
   └── Confirm no degradation across racial or sex demographics
               │
               ▼
[ 4. Clinical Shadow Deployment ]
   └── Run candidate model in parallel with active model for 30 days
               │
               ▼
[ 5. Production Promotion ]
   └── Update models/xgboost_final_model.joblib and log in Experiment Tracker
```

---

## 5. Roles and Responsibilities

- **Lead ML Engineer (Bililign Yibgeta Amare):** Oversees pipeline integrity, reviews drift telemetry, and executes model retraining and validation.
- **Data Engineer:** Maintains EHR ingestion pipelines, monitors missingness, and ensures feature transformation consistency.
- **Clinical Domain Specialist:** Reviews high-drift alerts, validates that clinical feature attributions remain medically sound, and authorizes model promotions.
- **Hospital Quality Officer:** Audits 30-day readmission outcome reconciliation and tracks compliance with hospital readmission reduction programs.


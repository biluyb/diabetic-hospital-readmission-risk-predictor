# GlucoShield CDSS — Model Monitoring & Data Drift Report
**FUSE AI-201 Capstone | Module 6: Production Monitoring & Drift Governance**  
**Model Monitored:** XGBoost Classifier (`models/xgboost_final_model.joblib`)  
**Operating Decision Threshold:** 0.45 (Clinical Recall Target >= 65%)  
**Report Generated:** Real-time Automated Execution  

---

> [!IMPORTANT]
> **Simulated Data Transparency Statement:**  
> In accordance with academic honesty requirements for FUSE AI-201, all production monitoring batches evaluated in this report are **clearly labeled as simulated monitoring data**. Because live clinical EHR streaming telemetry is unavailable outside HIPAA hospital firewalls, realistic clinical shifts (seasonal respiratory infection waves and elderly inpatient demographic changes) were simulated using verified mathematical distributions based on the UCI benchmark. This evidence illustrates the automated monitoring system's detection capability and must not be cited as real hospital deployment outcomes.

---

## 1. Executive Monitoring Summary

| Monitoring Cohort | Sample Size (n) | Mean Predicted Risk | % Flagged High-Risk (>= 0.45) | Holdout ROC-AUC | Clinical Recall @ 0.45 | Overall Drift Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline Reference (Test Set)** | 5,000 | 53.1% | 84.7% | 0.701 | 96.1% | **Baseline (Healthy)** |
| **Simulated Month 1 (Stable Flow)** | 2,500 | 53.1% | 83.8% | 0.696 | 95.9% | **🟢 NO DRIFT (Stable)** |
| **Simulated Month 2 (Winter Surge)** | 2,500 | 57.2% | 89.8% | 0.641 | 97.4% | **🔴 DRIFT DETECTED (Alert)** |

---

## 2. Feature-Level Population Stability Index (PSI) Analysis

Industry drift benchmarks:
- **PSI < 0.10**: Stable distribution; normal operations.
- **0.10 <= PSI < 0.25**: Moderate shift; heightened telemetry logging.
- **PSI >= 0.25**: Significant distributional shift; triggers automated clinical review and model retraining evaluation.

### Feature Drift Breakdown

| Clinical Feature | Type | Month 1 PSI | Month 1 Status | Month 2 PSI | Month 2 Status | Month 2 KS-Stat (p-val) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `time_in_hospital` | Numeric | 0.0021 | NO_DRIFT | 0.1639 | MODERATE_DRIFT | 0.175 (0.0e+00) |
| `number_inpatient` | Numeric | 0.0000 | NO_DRIFT | 0.3851 | HIGH_DRIFT | 0.254 (0.0e+00) |
| `total_prior_visits` | Numeric | 0.0020 | NO_DRIFT | 0.2006 | MODERATE_DRIFT | 0.213 (0.0e+00) |
| `num_lab_procedures` | Numeric | 0.0045 | NO_DRIFT | 0.0016 | NO_DRIFT | 0.016 (8.0e-01) |
| `age` | Categorical | 0.0029 | NO_DRIFT | 0.2983 | HIGH_DRIFT | N/A (Categorical) |
| `diag_1_group` | Categorical | 0.0039 | NO_DRIFT | 0.2601 | HIGH_DRIFT | N/A (Categorical) |

---

## 3. Data Quality & Missing Value Auditing

| Feature | Baseline Missing % | Month 1 Missing % | Month 2 Missing % | Status |
| :--- | :---: | :---: | :---: | :--- |
| `time_in_hospital` | 0.00% | 0.00% | 0.00% | Nominal |
| `number_inpatient` | 0.00% | 0.00% | 0.00% | Nominal |
| `num_lab_procedures` | 0.00% | 0.00% | 0.00% | Nominal |
| `race` | 2.21% | 2.15% | 2.28% | Nominal (<5% threshold) |
| `medical_specialty` | 49.08% | 48.80% | 49.30% | Expected sparsity handled by imputer |

---

## 4. Retraining Trigger Assessment & Governance Action

- **High-Drift Features Identified in Month 2:** `number_inpatient, age, diag_1_group`
- **Retraining Trigger Policy:** Triggered if any primary clinical feature reaches PSI >= 0.25 or if 30-day delayed ROC-AUC degrades by >= 0.05.
- **Recommendation:** **RETRAINING TRIGGER ACTIVATED**.
- **Governance Protocol:**
  1. Notify Lead ML Engineer and Clinical Governance Board.
  2. Assemble recent 6-month encounter records and run causal data audit.
  3. Validate candidate updated model weights against historical benchmark holdout before clinical shadow deployment.

---

*Report generated automatically by `monitoring/run_monitoring.py`.*

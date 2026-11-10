# 🏥 GlucoShield CDSS — Diabetes Hospital Readmission Risk Predictor

**FUSE AI-201 Capstone: AI Model Development, Implementation & MLOps (Modules 4, 5 & 6)**  
**Group:** Group 04 | **Cohort:** Youth Empowerment and Employment in AI Program (YEEAP)  
**Selected Primary Model:** Calibrated XGBoost Classifier (`models/xgboost_final_model.joblib`)  
**Clinical Decision Threshold:** 0.45 (Prioritizing Sensitivity $\ge 65\%$ for patient safety)  

---

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.15-blue.svg)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/model-XGBoost%20v3.4-orange.svg)](https://xgboost.readthedocs.io/)
[![SHAP](https://img.shields.io/badge/explainability-TreeSHAP-brightgreen.svg)](https://shap.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/container-Docker-blue.svg)](https://www.docker.com/)
[![Tests Passing](https://img.shields.io/badge/tests-17%2F17%20passed-success.svg)](tests/)

---

## 📌 Executive Summary

**GlucoShield** is an AI-powered Clinical Decision Support System (CDSS) designed to assist hospital discharge planners, attending physicians, and case managers in predicting the risk of **30-day unplanned hospital readmission** among diabetic inpatients.

Unplanned hospital readmissions in diabetic populations impose severe clinical morbidity on patients and heavy financial penalties on healthcare systems under frameworks like the CMS Hospital Readmissions Reduction Program (HRRP). By coupling calibrated gradient-boosted decision trees with **TreeSHAP local feature attribution**, GlucoShield delivers an interpretable risk score alongside a tailored post-discharge care checklist (home health nursing, medication reconciliation, and accelerated 7-day clinic follow-ups) before the patient departs the hospital.

---

## 👥 Team Members (Group 04)

| # | Name | Core Responsibilities & Contributions |
|---|---|---|
| 1 | **Bililign Yibgeta Amare** ⭐ | **Team Lead \| Architecture, ML Modeling, Pipeline, Validation, Testing & Documentation** |
| 2 | **Gebreslase Getachew Alemu** | Domain Specialist / Clinical Workflow & ICD-9 Grouping |
| 3 | **Belay Tilahun Alene** | Data Engineer / Preprocessing, Imputation & Pipeline |
| 4 | **Chalachew Getu Amarebet** | ML Engineer / Hyperparameter Tuning & Model Selection |
| 5 | **Dagne Amdetsion** | Software Engineer / Streamlit Prototype & UI Development |
| 6 | **Ebrahim Oumer Ali** | DevOps & Test Engineer / Test Suite & Verification |
| 7 | **Gutema Wako Anota** | Data Analyst / EDA & Clinical Visualizations |
| 8 | **Sena AmareSena Amare** | Responsible AI / Ethics, Fairness Auditing & Governance |
| 9 | **Shanbel mohammed ali** | Documentation & Clinical Protocol Reporting |
| 10 | **Tessema Ayele Alemu** | Clinical Metric Validation & Decision Threshold Calibration |
| 11 | **Yibeltal Meslie Alemayehu** | System Integration, Deployment & Maintenance Planning |

---

## 🏗️ System Architecture & Workflow

```
Patient Clinical Data at Discharge
               │
               ▼
┌────────────────────────────────────────────────┐
│ Input Validation & Sanitization Engine         │
│ (src/validation.py)                            │
│  - Bounds checking (LOS 1-14, labs 1-132)      │
│  - Rejection of malformed / negative inputs    │
│  - Graceful missing value imputation           │
└───────────────────────┬────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────┐
│ Preprocessing & Feature Engineering            │
│ (src/data_pipeline.py / preprocessor.joblib)   │
│  - Causal cohort filter (removes deceased)     │
│  - Patient deduplication (first admission only)│
│  - ICD-9 diagnosis mapping (9 clinical buckets)│
│  - Total visits, procedure intensity, med tags │
└───────────────────────┬────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────┐
│ Trained Primary Classifier: XGBoost            │
│ (models/xgboost_final_model.joblib)            │
│  - scale_pos_weight = 10.14 for class balance  │
│  - Output: 30-day readmission probability P    │
└───────────────────────┬────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│ Clinical Threshold   │  │ TreeSHAP Explainer   │
│ Classification (0.45)│  │ (src/explainability) │
│  - Low Risk (< 0.40) │  │  - Top-5 patient risk│
│  - Borderline (0.45) │  │    drivers & offsets │
│  - High Risk (>=0.50)│  │  - Fast <15ms render │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           └────────────┬────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────┐
│ Tailored Post-Discharge Action Plan Checklist  │
│  - Priority home nursing visit within 48h      │
│  - Clinical pharmacist medication review       │
│  - Accelerated 7-day clinic follow-up          │
└────────────────────────────────────────────────┘
```

Detailed architecture specifications, including Mermaid diagrams and MLOps component flows, are documented in [`documentation/architecture.md`](documentation/architecture.md).

---

## 📊 Benchmark Evaluation & Results

Evaluated on an independent **20% holdout test set ($n = 13,998$ encounters)** under stratified splitting (`random_state=42`):

| Model | Test ROC-AUC | PR-AUC | Sensitivity / Recall (th=0.45) | Specificity (th=0.45) | Precision (th=0.45) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Trivial Majority Baseline** | 0.5000 | 0.0898 | 0.00% | 100.00% | 0.00% | Reference only |
| **Logistic Regression (L2, Balanced)** | 0.6469 | 0.1572 | 53.06% | 67.51% | 13.88% | Linear benchmark |
| **Random Forest (Balanced)** | 0.6462 | 0.1554 | 43.91% | 76.92% | 15.82% | Overfits training set |
| **LightGBM Classifier** | 0.6465 | 0.1570 | 53.70% | 67.01% | 13.84% | Competitive |
| **XGBoost Classifier (Selected)** | **0.6465** | **0.1580** | **65.71%** | **54.54%** | **12.48%** | **✅ Meets clinical target ($\ge 65\%$)** |

### Confusion Matrix Breakdown (Tuned Threshold = 0.45)
- **True Positives (TP): 826** — High-risk patients correctly identified for intensive transition care.
- **False Negatives (FN): 431** — High-risk patients missed by the model.
- **True Negatives (TN): 6,949** — Stable patients correctly cleared for routine discharge.
- **False Positives (FP): 5,792** — Low-risk patients flagged for follow-up (clinically safe failure mode).

---

## 🧪 Automated Testing & Robustness Suite

GlucoShield includes a 17-test automated verification suite (`tests/`):
- **Preprocessing & ICD-9 Mapping:** [`tests/test_preprocessing.py`](tests/test_preprocessing.py)
- **Model Artifact Integrity:** [`tests/test_model_loading.py`](tests/test_model_loading.py)
- **Validation & Bounds:** [`tests/test_validation.py`](tests/test_validation.py)
- **Prediction & Demonstration Scenarios:** [`tests/test_prediction.py`](tests/test_prediction.py)
- **Explainability Structure:** [`tests/test_explainability.py`](tests/test_explainability.py)
- **FastAPI Endpoints:** [`tests/test_api.py`](tests/test_api.py)

Run the test suite:
```bash
python -m pytest tests/ -v
```

---

## 🚀 Quickstart Guide

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/biluyb/diabetic-hospital-readmission-risk-predictor.git
cd diabetic-hospital-readmission-risk-predictor

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full End-to-End Pipeline
Executes data download, cleaning, training, evaluation, testing, experiment logging, and drift monitoring:
```bash
python run_full_pipeline.py
```

### 3. Launch the Streamlit Interactive Dashboard
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

### 4. Launch the Optional FastAPI Microservice
```bash
uvicorn src.api:api_app --host 0.0.0.0 --port 8000 --reload
```
- Swagger UI Documentation: **http://localhost:8000/docs**
- Health Check: `curl http://localhost:8000/health`

### 5. Run with Docker
```bash
docker build -t glucoshield:latest .
docker run -p 8501:8501 -p 8000:8000 glucoshield:latest
```

---

## 🧭 Project Portfolio Directory Layout

```
GlucoShield/
├── app.py                            # Streamlit Clinical Decision Support Dashboard
├── run_full_pipeline.py              # Master end-to-end pipeline runner
├── download_data.py                  # Automated UCI dataset acquisition script
├── Dockerfile                        # Production container specification
├── .dockerignore                     # Docker build exclusions
├── requirements.txt                  # Pinned Python dependencies
├── retrospective.md                  # One-page capstone student reflection
├── simulated_data_statement.md       # Real vs. simulated data declaration
│
├── src/
│   ├── data_pipeline.py              # Data cleaning, deduplication, ICD-9 mapping
│   ├── validation.py                 # Centralized clinical input validation engine
│   ├── models.py                     # Baseline and ensemble model training
│   ├── evaluate.py                   # Holdout evaluation, ROC curves, error audit
│   ├── explainability.py             # TreeSHAP feature attribution engine
│   ├── experiment_tracker.py         # JSON/CSV experiment tracking system
│   ├── test_suite.py                 # 5-case system robustness test harness
│   └── api.py                        # FastAPI REST microservice (GET /health, POST /predict)
│
├── tests/
│   ├── test_preprocessing.py         # Preprocessing & ICD-9 unit tests
│   ├── test_model_loading.py         # Model artifact loading tests
│   ├── test_validation.py            # Input validation & bounds tests
│   ├── test_prediction.py            # Inference & demonstration scenario tests
│   ├── test_explainability.py        # TreeSHAP structure tests
│   └── test_api.py                   # FastAPI integration tests
│
├── monitoring/
│   ├── drift_detector.py             # PSI & Kolmogorov-Smirnov drift detection
│   ├── monitor.py                    # Simulated production monitoring pipeline
│   ├── run_monitoring.py             # Monitoring report generator
│   └── drift_report.md               # Generated drift audit report
│
├── evaluation/
│   ├── experiment_runs.json          # Reproducible experiment runs log (JSON)
│   └── experiment_runs.csv           # Tabular experiment comparison (CSV)
│
├── models/                           # Serialized model artifacts (.joblib)
│   ├── xgboost_final_model.joblib
│   ├── preprocessor.joblib
│   ├── feature_names.joblib
│   ├── feature_metadata.joblib
│   ├── evaluation_summary.joblib
│   └── system_test_report.joblib
│
├── plots/                            # Auto-generated ROC, CM, EDA & Drift plots (.png)
│   ├── roc_curve.png
│   ├── confusion_matrix.png
│   ├── feature_importance.png
│   ├── monitoring_drift.png
│   └── [EDA distribution plots]
│
└── documentation/                    # Complete 8-document governance suite
    ├── model_card.md                 # Complete 8-section Model Card (Mitchell et al.)
    ├── architecture.md               # Detailed technical architecture & Mermaids
    ├── monitoring_plan.md            # Production monitoring strategy & retraining
    ├── drift_report.md               # Real-time generated drift report
    ├── governance_plan.md            # Clinical ethics, HIPAA privacy, bias audits
    ├── support_and_maintenance.md    # SLA, bug triage, fallback operations
    ├── deployment_guide.md           # Local, Docker, & Streamlit Cloud guides
    ├── experiment_tracking.md        # Lineage schemas & historical run logs
    └── limitations_and_future_work.md # SDoH, ICD-10 crosswalk, research roadmap
```

---

## 📚 Complete Documentation Suite

- 📋 [**Model Card**](documentation/model_card.md) — 8-section clinical model card covering intended use, inputs, ethical considerations, and results.
- 📐 [**System Architecture**](documentation/architecture.md) — Detailed ASCII and Mermaid diagrams covering client flow and MLOps components.
- 📈 [**Monitoring Plan**](documentation/monitoring_plan.md) — Production drift detection, metric definitions, and retraining policies.
- 🔍 [**Drift Report**](documentation/drift_report.md) — Empirical PSI and KS test statistics on simulated production cohorts.
- 🛡️ [**Governance Plan**](documentation/governance_plan.md) — Responsible AI principles, HIPAA privacy, and demographic fairness audits.
- 🛠️ [**Support & Maintenance**](documentation/support_and_maintenance.md) — SLOs, incident response, fallback operations, and model lifecycle.
- 🚀 [**Deployment Guide**](documentation/deployment_guide.md) — Step-by-step local, Docker, and Streamlit Cloud instructions.
- 🔬 [**Experiment Tracking**](documentation/experiment_tracking.md) — Tracking architecture, parameter schemas, and reproducible run logs.
- 🔮 [**Limitations & Future Work**](documentation/limitations_and_future_work.md) — In-depth analysis of dataset boundaries and clinical research roadmap.
- 📝 [**Student Retrospective**](retrospective.md) — Comprehensive one-page capstone reflection.
- ⚖️ [**Simulated Data Statement**](simulated_data_statement.md) — Formal declaration clarifying real vs. simulated data.

---

## ⚕️ Clinical Disclaimer

> **IMPORTANT CLINICAL NOTICE:**  
> GlucoShield is an educational and research prototype developed as part of the FUSE AI-201 capstone project. It is **not a certified medical diagnostic device or clinical treatment planning tool**. All model predictions and risk probabilities represent statistical associations derived from historical inpatient encounters (1999–2008) and must be evaluated alongside bedside clinical findings by licensed healthcare professionals. The tool must never be used as the sole basis for clinical decision-making or altering patient care plans.

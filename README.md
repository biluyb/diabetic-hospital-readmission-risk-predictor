# GlucoShield CDSS — Diabetes Hospital Readmission Risk Predictor
**FUSE AI-201 Capstone | Module 5: AI Project Implementation**  
**Group 04 | Cohort: YEEAP**

---

## Project Overview
**GlucoShield** is an AI-powered Clinical Decision Support System (CDSS) that predicts whether a diabetic inpatient patient is at risk of **unplanned hospital readmission within 30 days** of discharge.

It enables discharge planners, case managers, and attending physicians to identify high-risk patients in advance and allocate targeted post-acute interventions — such as home health nurse visits, clinical pharmacist medication reconciliation, and priority 7-day clinic follow-ups — before the patient leaves the hospital.

**Dataset:** [UCI Diabetes 130-US Hospitals 1999–2008](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)  
**Final Model:** XGBoost Classifier (Test ROC-AUC: 0.647, Clinical Recall @ th=0.45: 65.7%)

---

## Team Members (Group 04)
| # | Name | Role |
|---|---|---|
| 1 | **Bililign Yibgeta Amare** ⭐ | **Team Lead \| Data Engineering, ML Modeling, Evaluation, Prototype, Testing & Documentation** |
| 2 | Gebreslase Getachew Alemu | Domain Specialist / Clinical Workflow |
| 3 | Belay Tilahun Alene | Data Engineer / Preprocessing & Pipeline |
| 4 | Chalachew Getu Amarebet | ML Engineer / Hyperparameter Tuning & Evaluation |
| 5 | Dagne Amdetsion | Software Engineer / Prototype & App Dev |
| 6 | Ebrahim Oumer Ali | DevOps & Test Engineer / Edge-case Suite |
| 7 | Gutema Wako Anota | Data Analyst / EDA & Visualizations |
| 8 | Sena AmareSena Amare | Responsible AI / Ethics & Fair ML |
| 9 | Shanbel mohammed ali | Documentation & Clinical Reporting |
| 10 | Tessema Ayele Alemu | Clinical Metric Validation & Threshold Calibration |
| 11 | Yibeltal Meslie Alemayehu | System Integration & Deployment |

---

## Repository Structure
```
.
├── data/
│   ├── diabetic_data.csv           # UCI dataset (auto-downloaded)
│   └── IDS_mapping.csv             # ICD/Admission code mapping definitions
├── src/
│   ├── data_pipeline.py            # Task 3: Data cleaning, feature engineering, train/test split
│   ├── eda.py                      # Task 4: Exploratory Data Analysis & chart generation
│   ├── models.py                   # Tasks 5 & 6: Baseline + candidate model training
│   ├── evaluate.py                 # Task 7: Evaluation metrics, ROC curves, error audit
│   ├── test_suite.py               # Task 8: Whole-chain edge-case system tests
│   └── explainability.py           # TreeSHAP patient-level feature attribution engine
├── models/                         # Serialized trained models (.joblib)
├── plots/                          # Auto-generated evaluation & EDA charts (.png)
├── app.py                          # Interactive Streamlit Clinical Dashboard
├── run_full_pipeline.py            # Master pipeline runner (executes all 8 tasks)
├── download_data.py                # Automated UCI dataset download script
├── CAPSTONE_MODULE5_REPORT.md      # Full 17-section written project report
├── requirements.txt                # Python dependency list
└── README.md                       # This file
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Internet connection (for initial dataset download)

### Step 1: Install Dependencies
Open a terminal in the project root directory and run:

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Option A: Run the Complete Pipeline (Recommended)
This single command executes all 8 Module 5 tasks in sequence:

```bash
python run_full_pipeline.py
```

This will:
1. Download and verify the UCI dataset
2. Clean, deduplicate, and preprocess the data
3. Generate all EDA visualizations → saved to `plots/`
4. Train Baseline (Logistic Regression), Random Forest, XGBoost, and LightGBM models
5. Evaluate all models on the holdout test set
6. Run the Stage 8 robustness test suite
7. Save all trained models → saved to `models/`

### Option B: Run Individual Stages
Each task can also be run independently as a Python module:

```bash
# Task 3: Data preparation
python -m src.data_pipeline

# Task 4: Exploratory Data Analysis
python -m src.eda

# Tasks 5 & 6: Model training
python -m src.models

# Task 7: Model evaluation
python -m src.evaluate

# Task 8: System testing
python -m src.test_suite
```

---

## Launching the Interactive Prototype

After running the pipeline at least once (to train models), launch the web dashboard:

```bash
streamlit run app.py
```

Then open your browser at **http://localhost:8501**

### Dashboard Features
| Feature | Description |
|---|---|
| **Patient Risk Assessment** | Enter patient clinical parameters or load a preset scenario to get instant 30-day readmission risk prediction |
| **SHAP Explainability** | Real-time top-5 feature attribution showing what's driving each individual patient's score |
| **Risk Tier Color Coding** | 🔴 High Risk (≥52%) / 🟡 Moderate Risk (40–52%) / 🟢 Low Risk (<40%) |
| **Discharge Checklist** | Dynamically generated post-discharge care intervention checklist tailored to risk tier |
| **Stage 8 Validation Sandbox** | Live edge-case testing within the browser |
| **Model Performance Explorer** | ROC curves, Confusion Matrices, Feature Importance charts, EDA visualizations |

### Preset Clinical Scenarios
The sidebar offers three pre-built patient scenarios:
- **Scenario A:** High-Risk Elderly Patient (3 prior inpatient stays, insulin up-titrated)
- **Scenario B:** Low-Risk Stable Patient (first admission, well-controlled HbA1c)
- **Scenario C:** Moderate-Risk Patient (recent medication adjustment, 1 prior inpatient)

---

## Key Results

| Model | Test ROC-AUC | Recall (Clinical th=0.45) | Status |
|---|:---:|:---:|---|
| Trivial Majority Baseline | 0.500 | 0.0% | Reference only |
| Logistic Regression (Baseline) | 0.647 | 53.1% | First working model |
| Random Forest | 0.646 | 43.9% | Overfits training set |
| LightGBM | 0.647 | 53.7% | Competitive |
| **XGBoost (Selected)** | **0.647** | **65.7%** | **✅ Meets clinical safety target** |

---

## Evaluation Plots
All plots are saved automatically to the `plots/` directory:
- `target_distribution.png` — Class imbalance visualization
- `prior_inpatient_vs_readmission.png` — Prior admissions vs readmission rate
- `primary_diagnosis_readmission.png` — Readmission by ICD-9 disease category
- `length_of_stay_distribution.png` — Hospital stay stratified by outcome
- `correlation_heatmap.png` — Clinical feature correlation matrix
- `roc_curve.png` — Multi-model ROC comparison on holdout test set
- `confusion_matrix.png` — Side-by-side at standard (0.50) and clinical (0.45) thresholds
- `feature_importance.png` — Top 20 XGBoost clinical predictors

---

## Dataset Reference
> Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. N. (2014).  
> *Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records.*  
> BioMed Research International, 2014.  
> UCI Repository Dataset ID: 296

---

## Clinical Disclaimer
GlucoShield CDSS is an educational and research prototype developed for the FUSE AI-201 capstone. All model outputs represent statistical associations derived from historical inpatient records and must be evaluated alongside bedside clinical findings by licensed healthcare providers. This tool must not be used as the sole basis for clinical decision-making or altering patient care plans.

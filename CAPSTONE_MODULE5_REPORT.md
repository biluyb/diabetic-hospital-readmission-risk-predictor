# FUSE AI-201 | Module 5: AI Project Implementation Report

**Project Title:** Predicting Hospital Readmission Risk in Diabetic Patients to Enhance Discharge Planning  
**Domain:** Healthcare (Clinical Decision Support Systems)  
**Cohort & Group:** YEEAP & FUSE Capstone Project — Group 04  
**Date:** October 2026  

---

### Team Members & Contributions
1. **Bililign Yibgeta Amare** ⭐ **(Team Lead | Full-Stack Contributor: Data Engineering, ML Modeling, Evaluation, Prototype Development, Testing & Documentation)**
2. **Gebreslase Getachew Alemu** (Domain Specialist / Clinical Workflow)
3. **Belay Tilahun Alene** (Data Engineer / Preprocessing & Pipeline)
4. **Chalachew Getu Amarebet** (ML Engineer / Hyperparameter Tuning & Evaluation)
5. **Dagne Amdetsion** (Software Engineer / Prototype & App Dev)
6. **Ebrahim Oumer Ali** (DevOps & Test Engineer / Edge-case Suite)
7. **Gutema Wako Anota** (Data Analyst / EDA & Visualizations)
8. **Sena AmareSena Amare** (Responsible AI / Ethics & Fair ML)
9. **Shanbel mohammed ali** (Documentation & Clinical Reporting)
10. **Tessema Ayele Alemu** (Clinical Metric Validation & Threshold Calibration)
11. **Yibeltal Meslie Alemayehu** (System Integration & Deployment)

---

## 1. Project Title
**Predicting Hospital Readmission Risk in Diabetic Patients to Enhance Discharge Planning (GlucoShield CDSS)**

---

## 2. Problem Statement
Unplanned 30-day hospital readmissions among diabetic patients create acute clinical morbidity and substantial financial strain on global healthcare systems. Inpatient management of diabetes mellitus involves balancing glycemic control, complex polypharmacy (insulin regimens and oral hypoglycemic agents), and frequent multi-system comorbidities (e.g., congestive heart failure, chronic kidney disease). 

Under quality and value-based care frameworks, such as the Centers for Medicare & Medicaid Services (CMS) Hospital Readmissions Reduction Program (HRRP), hospitals face heavy reimbursement penalties for excessive 30-day readmissions. Currently, discharge planning teams rely on static, generic scoring tools (such as the LACE Index or HOSPITAL score) or informal clinician intuition. These traditional approaches fail to capture dynamic interactions among inpatient medication adjustments, glycemic laboratory trends, and complex secondary diagnoses, and they are typically conducted too late in the discharge workflow to mobilize personalized post-acute interventions.

---

## 3. Target Users and Stakeholders
* **Primary System Users:** Hospital discharge planners, case managers, and inpatient nurse coordinators who conduct pre-discharge risk reviews and allocate post-acute transition resources (e.g., home health nursing, 7-day clinic follow-ups, and tailored diabetes self-management education).
* **Clinical Decision-Makers:** Attending physicians, hospitalists, and endocrinologists who make discharge authorization decisions, adjust prescription regimens, or order clinical pharmacist medication reconciliations.
* **Organizational Beneficiaries:** Hospital quality officers, chief medical officers, and healthcare payers seeking to reduce 30-day readmission penalty rates, alleviate emergency department crowding, and improve patient longevity.

### Input Table
| Input | Type | Description |
| :--- | :--- | :--- |
| `age` | Categorical | 10-year age bracket of patient (e.g., `[60-70)`, `[70-80)`) |
| `gender` | Categorical | Biological sex (`Male`, `Female`) |
| `race` | Categorical | Patient racial/ethnic background |
| `time_in_hospital` | Integer | Total length of current inpatient stay in days (1 to 14) |
| `num_lab_procedures` | Integer | Total number of lab diagnostic tests performed during stay |
| `num_procedures` | Integer | Total non-laboratory medical/surgical procedures performed |
| `num_medications` | Integer | Total count of distinct medications administered during stay |
| `number_inpatient` | Integer | Count of prior acute inpatient admissions in past 12 months |
| `number_emergency` | Integer | Count of emergency room visits in past 12 months |
| `number_outpatient` | Integer | Count of outpatient medical visits in past 12 months |
| `number_diagnoses` | Integer | Total diagnoses entered into the encounter chart (1 to 16) |
| `diag_1` | Categorical / String | Primary ICD-9 diagnosis code (e.g., `250.xx`, `428`, `414`) |
| `diag_2`, `diag_3` | Categorical / String | Secondary and tertiary ICD-9 diagnosis codes |
| `A1Cresult` | Categorical | Glycated hemoglobin test status (`>7`, `>8`, `Norm`, `None`) |
| `max_glu_serum` | Categorical | Peak blood glucose serum test result (`>200`, `>300`, `Norm`, `None`) |
| `insulin` | Categorical | Inpatient insulin status change (`No`, `Steady`, `Up`, `Down`) |
| `metformin`, `glipizide`, etc. | Categorical | Status of 23 specific oral hypoglycemic medications |
| `change` | Categorical | Indicator if any diabetes medication regimen was altered (`Ch`, `No`) |
| `diabetesMed` | Categorical | Whether any diabetes prescription was prescribed (`Yes`, `No`) |

### Success Criteria Table
| Criterion | Target / Expected Result |
| :--- | :--- |
| **Model Performance** | Primary: $\text{ROC-AUC} \ge 0.65$; Secondary: Positive-class Recall (Sensitivity) $\ge 0.65$ at clinical operating threshold. |
| **Prediction / Output** | Calibrated readmission probability ($P \in [0, 1]$), 3-tier risk classification (Low, Moderate, High), and top SHAP local feature attributions. |
| **User Input** | Clean structured interface accepting patient encounter parameters with immediate type & boundary validation. |
| **System Functionality** | End-to-end automated inference pipeline linking input forms, preprocessing, imputation, tree scoring, and tailored discharge checklist. |
| **Testing** | 100% pass rate across normal, missing, invalid-format, unexpected-category, and out-of-range clinical edge cases. |

### Is AI Appropriate?
Yes. The clinical encounter data contains complex non-linear interactions across medication titrations, diagnostic combinations, and prior healthcare utilization that cannot be modeled by simple linear cutoff heuristics like the LACE index. The UCI 130-US Hospitals dataset provides over 100,000 real-world encounters across 10 years, offering sufficient clinical breadth for machine learning algorithms to learn predictive patterns.

---

## 4. Proposed AI Solution
We formulate the task as **Supervised Binary Classification**: predicting whether an inpatient diabetic encounter will lead to an unplanned readmission within 30 days of discharge ($y = 1$) versus after 30 days or no readmission ($y = 0$).

### System Workflow and Architecture Diagram
```
[ Clinical User / EHR ]
          │
          ▼ (Patient Parameters at Discharge)
[ Input Validation Layer ] ────(Negative / Format Errors)───> [ Rejection & Alert ]
          │
          ▼ (Cleaned Parameters)
[ Preprocessing & Feature Engineering ]
  ├── Missing Imputation (Median / Mode)
  ├── ICD-9 Category Mapping (9 Clinical Groups)
  ├── Composite Feature Derivation (Total Visits, Med Intensity)
  └── One-Hot & Scaling Transformation
          │
          ▼ (Standardized Feature Vector [155 columns])
[ Trained Ensemble Model: XGBoost ]
          │
          ▼
[ Clinical Risk Post-Processor ]
  ├── Readmission Risk Probability (%)
  ├── Calibrated Operating Threshold (th = 0.45)
  ├── TreeSHAP Local Feature Attribution (Top 5 Drivers)
  └── Dynamic Post-Discharge Care Plan Allocation
          │
          ▼
[ Interactive Clinical Dashboard (Streamlit Web UI) ]
```

### Feature and Target Table
| Variable | Feature or Target? | Data Type | Purpose |
| :--- | :--- | :--- | :--- |
| `target` | **Target** | Binary ($0, 1$) | Indicates readmission within 30 days ($1 = \text{Readmitted} <30$, $0 = \text{Otherwise}$) |
| `number_inpatient` | Feature | Integer | Direct marker of historical disease instability and frequent hospital contact |
| `time_in_hospital` | Feature | Continuous / Int | Surrogate for illness severity and acute medical complexity |
| `num_lab_procedures` | Feature | Continuous / Int | Reflects intensity of diagnostic investigation during admission |
| `diag_1_group` | Feature | Categorical | Primary underlying organ system failure (Circulatory, Respiratory, Diabetes, etc.) |
| `total_prior_visits` | Feature (Engineered)| Continuous | Composite score combining outpatient, emergency, and inpatient utilization |
| `num_dosage_changes` | Feature (Engineered)| Integer | Identifies recent medication instability (titration of insulin/oral drugs) |
| `procedure_intensity`| Feature (Engineered)| Continuous | Ratio of total clinical interventions to length of hospital stay |
| `A1Cresult` | Feature | Categorical | Laboratory metric of baseline chronic glycemic regulation |
| `insulin` | Feature | Categorical | Specific insulin dosage adjustment during current admission |

---

## 5. Dataset Identification & Source Documentation
* **Dataset Name:** Diabetes 130-US Hospitals for Years 1999–2008
* **Source:** UCI Machine Learning Repository (Dataset ID: 296) / Strack et al. (2014)
* **Access Method:** Automated API extraction via direct UCI data repository endpoint
* **Number of Raw Records / Variables:** 101,766 clinical encounters, 50 variables
* **Target Variable:** `readmitted` (`<30`, `>30`, `NO`) transformed to binary `target`
* **Format:** Comma-Separated Values (CSV)
* **License & Privacy:** Public benchmark dataset, fully de-identified under HIPAA Safe Harbor regulations; approved for academic research and clinical decision support modeling.

---

## 6. Data Preparation and Cleaning
Data preparation strictly adhered to clinical domain principles and prevented data leakage:

### Data Quality & Preprocessing Record
| Step | Problem / Decision | Evidence | Action Taken & Reason |
| :--- | :--- | :--- | :--- |
| **Hospice / Expired Removal** | Patients who expired or entered hospice cannot logically be readmitted. | 2,423 encounters had `discharge_disposition_id` in {11, 13, 14, 19, 20, 21}. | **Excluded 2,423 records** (Cohort reduced from 101,766 to 99,343). Preserves causal validity. |
| **Patient Deduplication** | Multiple admissions per patient violate sample independence and induce test leakage. | 29,353 records were repeat encounters from already observed patients. | **Retained only first admission** per unique `patient_nbr` (Cohort reduced to 69,990). Eliminates patient-level test leakage. |
| **High Missingness Features** | Features missing >50% data or non-clinical billing codes. | `weight` (>95% missing `?`), `payer_code` (~52% missing). | **Dropped `weight` and `payer_code`**. Imputing >95% missing values introduces false clinical variance. |
| **Sparse Diagnoses Mapping** | Over 800 discrete 3-digit ICD-9 codes caused high-cardinality dimensionality explosion. | `diag_1`, `diag_2`, `diag_3` contain extensive individual codes. | **Mapped into 9 clinical categories** (Circulatory, Respiratory, Digestive, Diabetes, Injury, Musculoskeletal, Genitourinary, Neoplasms, Other). |
| **Missing Value Encoding** | Missing data represented as `'?'` in raw dataset. | `medical_specialty` missing ~49%, `race` missing ~3%. | Replaced `'?'` with `NaN`, followed by median imputation for numeric features and constant `'Missing'` category for categoricals. |
| **Data Splitting** | Need rigorous holdout evaluation that preserves minority class ratio. | Class imbalance (~8.98% positive class). | **Stratified 80/20 split** (`random_state=42`). 55,989 training records, 13,998 test records. |

---

## 7. Exploratory Data Analysis (EDA)
EDA was conducted to identify key clinical patterns, distributions, and collinearity:

### Descriptive Statistics of Core Numeric Features (n = 69,990 clean encounters)
| Variable | Mean | Std Dev | Min | Median | Max |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `time_in_hospital` (days) | 4.27 | 2.93 | 1.00 | 3.00 | 14.00 |
| `num_lab_procedures` | 42.88 | 19.89 | 1.00 | 44.00 | 132.00 |
| `num_procedures` | 1.43 | 1.76 | 0.00 | 1.00 | 6.00 |
| `num_medications` | 15.67 | 8.29 | 1.00 | 14.00 | 81.00 |
| `number_inpatient` (prior visits) | 0.18 | 0.60 | 0.00 | 0.00 | 12.00 |
| `number_diagnoses` | 7.22 | 2.00 | 1.00 | 8.00 | 16.00 |
| `total_prior_visits` | 0.56 | 1.43 | 0.00 | 0.00 | 49.00 |
| `procedure_intensity` | 15.19 | 12.49 | 0.07 | 11.50 | 93.00 |

### Key EDA Findings
| Finding | Evidence | Possible Impact on Modeling |
| :--- | :--- | :--- |
| **Severe Class Imbalance** | Positive readmissions within 30 days account for only **8.98%** (6,285 cases) vs **91.02%** (63,702 non-readmitted/late). | Unweighted models will succumb to majority-class collapse, predicting 0 for all patients. Requires `scale_pos_weight` or class weighting. |
| **Prior Inpatient Admissions as Dominant Risk Driver** | 30-day readmission rate jumps from **7.8%** for patients with 0 prior inpatient stays to **22.5%** for patients with $\ge 4$ prior stays. | Historical acute care utilization is the single strongest predictor of recurrent readmission risk. |
| **High Diagnosis-Specific Variance** | Circulatory diseases (30.1% of cohort) and Respiratory diseases exhibited above-average readmission rates (>9.5%). | Categorical grouping of ICD-9 codes effectively captures systemic clinical morbidity without high-cardinality noise. |
| **Weak Linear Correlations with Target** | Individual Pearson correlations between raw numeric features and target are $< 0.12$. | Complex non-linear combinations and interaction effects (e.g. polypharmacy $\times$ length of stay) are essential, favoring gradient-boosted trees. |

---

## 8. Baseline Model Construction
To benchmark subsequent modeling improvements, we constructed two baseline models:
1. **Trivial Reference Model:** Predicts the majority class ($y = 0$) for every sample.
2. **First Working Model (Baseline):** Regularized L2 Logistic Regression with `class_weight='balanced'`.

### Baseline Performance on Holdout Test Set (n = 13,998)
| Model | Test ROC-AUC | Recall (High-Risk) | Precision | Accuracy | F1-Score | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Trivial Majority** | 0.5000 | 0.00% | 0.00% | 91.02% | 0.000 | Zero predictive capacity; misleading accuracy artifact of imbalance. |
| **Logistic Regression (Baseline)** | 0.6469 | 53.06% | 13.88% | 66.22% | 0.2201 | Establishes linear lower bound. Catches 53.1% of readmissions with balanced weighting. |

---

## 9. Model Improvement and Comparison
We evaluated three advanced non-linear ensemble candidate models: **Random Forest**, **XGBoost Classifier**, and **LightGBM Classifier**, using identical stratified training sets and feature transformations.

### Model Comparison Table (Holdout Test Set)
| Model | Train ROC-AUC | Test ROC-AUC | Accuracy | Precision | Recall | F1-Score | Architectural Characterization |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Trivial Majority Baseline** | 0.5000 | 0.5000 | 91.02% | 0.0000 | 0.0000 | 0.0000 | Zero clinical value |
| **Logistic Regression (Baseline)** | 0.6610 | 0.6469 | 66.22% | 0.1388 | 0.5306 | 0.2201 | Simple linear benchmark |
| **Random Forest Classifier** | 0.8051 | 0.6462 | 73.97% | 0.1582 | 0.4391 | 0.2326 | Overfits training data (0.805 vs 0.646); lower recall |
| **LightGBM Classifier** | 0.7451 | 0.6465 | 65.82% | 0.1384 | 0.5370 | 0.2201 | Fast histogram boosting; competitive discrimination |
| **XGBoost Classifier (Primary)** | **0.7625** | **0.6465** | **67.08%** | **0.1401** | **0.5187** | **0.2206** | **Best balance; lowest inference latency; native TreeSHAP support** |

### Tuning Log
| Parameter | Before | After | Reason / Impact |
| :--- | :---: | :---: | :--- |
| `max_depth` (XGBoost) | 8 | 5 | Constrained tree depth to prevent clinical feature overfitting. Reduced train-test AUC gap from 0.18 to 0.11. |
| `scale_pos_weight` | 1.0 (unweighted) | 10.14 | Corrected for 10:1 class imbalance. Raised baseline positive class recall from 2.1% to >51%. |
| `learning_rate` / `n_estimators` | 0.10 / 100 | 0.04 / 250 | Smoothed gradient descent updates, improving generalizability across hospital sub-populations. |
| `reg_alpha` (L1) / `reg_lambda` (L2)| 0.0 / 1.0 | 0.5 / 2.0 | Regularized against noise from high-cardinality secondary diagnoses. |

### Record of Failed Experiments
* **Unweighted Decision Tree / Random Forest:** Initial experiments without class weighting achieved 91% accuracy but 0.02 recall (missing 98% of high-risk patients), proving that accuracy is an invalid clinical metric under severe class imbalance.
* **Deep Random Forest (`max_depth=16`):** Yielded 0.94 Train ROC-AUC but only 0.63 Test ROC-AUC, demonstrating severe overfitting on hospital-specific noise and discharge disposition IDs.

---

## 10. Final Model Selection
**XGBoost Classifier** was selected as the final operational model. While LightGBM and regularized Logistic Regression exhibited comparable test ROC-AUC, XGBoost demonstrated superior training stability, optimal regularization parameters (`reg_alpha=0.5`, `reg_lambda=2.0`), robust resilience to outlier values, and seamless integration with **TreeSHAP** for instantaneous clinical explainability.

---

## 11. Model Evaluation on Untouched Holdout Test Set
The final XGBoost model was evaluated on the independent 20% holdout test set (n = 13,998 patients):

### Test Evaluation Metrics
| Metric | Result | What it Means for This Project |
| :--- | :---: | :--- |
| **ROC-AUC** | **0.647** | Demonstrates solid discriminative power across decision thresholds on deduplicated clinical encounter data. |
| **PR-AUC (Avg Precision)** | **0.158** | Nearly double the random baseline (0.0898), confirming effective risk concentration in the top predicted percentiles. |
| **Clinical Operating Recall** | **65.71%** | At tuned clinical decision threshold $th = 0.45$, the model successfully intercepts **826 out of 1,257** true 30-day readmissions. |
| **Clinical Operating Specificity**| **54.54%** | Successfully clears **6,949 low-risk patients** from unnecessary high-cost post-discharge intensive interventions. |
| **Operating Precision** | **12.48%** | 1 out of every 8 flagged patients will be readmitted within 30 days (a 40% enrichment over the general 8.98% hospital baseline). |

### Confusion Matrix Breakdown (Tuned Threshold = 0.45)
* **True Positives (TP): 826** — High-risk patients correctly identified for proactive care management.
* **False Negatives (FN): 431** — High-risk patients missed by the model.
* **True Negatives (TN): 6,949** — Stable patients correctly cleared for standard discharge.
* **False Positives (FP): 5,792** — Low-risk patients flagged for follow-up (clinically safe failure mode).

### Clinical Error Audit (False Negatives vs. True Positives)
Our diagnostic audit revealed why the 431 False Negatives were misclassified:
* **Prior Inpatient Admissions:** Missed cases had an average of only **0.04** prior inpatient admissions (vs. **0.57** for True Positives).
* **Length of Stay:** Missed cases had significantly shorter hospitalizations (**3.53 days** vs. **5.34 days** for True Positives).
* **Diagnostic Complexity:** Missed cases presented with fewer documented diagnoses (**7.09** vs. **7.81**).  
* **Clinical Conclusion:** False Negatives represent patients who appeared clinically stable during their index stay but suffered unobserved outpatient complications (e.g., social isolation, diet non-compliance, medication unaffordability) that are not captured in hospital EHR records.

---

## 12. Testing the Complete Solution (Stage 8)
We validated the entire operational chain: **User Input → Input Validation → Preprocessing Imputation → Model Inference → Safety Reporting**.

### System Test Suite Results
| Test Case | Input Characteristics | Expected Behavior | Actual Behavior | Pass / Fail |
| :--- | :--- | :--- | :--- | :---: |
| **1. Normal Complete Input** | Routine clinical values: 65yo female, 4 days in hospital, 45 labs, 1 prior inpatient stay, diabetes with circulatory comorbidity. | Valid risk score, predicted category, zero errors. | Scored: **Prob = 52.1%, Tier = Moderate Risk**. Complete SHAP breakdown produced. | **PASS** |
| **2. Missing Value** | Missing race (`?`), missing length of stay (`None`), unmeasured HbA1c, missing diagnosis codes. | Handled gracefully via median/mode imputation with clear message. | Handled via median imputation. Scored: **Prob = 32.4%, Tier = Low Risk**. | **PASS** |
| **3. Invalid Number or Format** | Negative length of stay (`-5`), string in numeric field (`num_medications = 'ABC'`). | Rejected safely with descriptive validation error message. | Safely rejected: *"Invalid negative value for 'time_in_hospital': -5.0. Invalid non-numeric format for 'num_medications': 'ABC'"*. | **PASS** |
| **4. Unexpected Category** | Unseen race (`Martian`), invalid gender, unrecognized diagnosis code (`99999`). | Handled safely via one-hot `handle_unknown='ignore'` without system crash. | Safely encoded unrecognized values to default categories. Scored: **Prob = 46.8%**. | **PASS** |
| **5. Extreme Outlier Value** | Extreme stay (`time_in_hospital = 45`), excessive labs (`200`), 120 medications. | Processed safely with clinical out-of-range warnings. | Executed safely with clinical range warnings: *"Extreme value warning: 'time_in_hospital'=45.0 exceeds standard clinical range (max 14)"*. Scored: **Prob = 66.9%**. | **PASS** |

---

## 13. Working Prototype
The working prototype is implemented in `app.py` using **Streamlit**:
* **Web UI:** Interactive clinical dashboard allowing physicians and discharge planners to enter patient parameters or load pre-built clinical patient scenarios.
* **Instantaneous Risk Scoring:** Computes calibrated 30-day readmission risk probability and assigns clear color-coded tiers (**High Risk: Red**, **Moderate Risk: Amber**, **Low Risk: Green**).
* **Explainability Engine:** Embeds **TreeSHAP** to display the top 5 patient-specific clinical features driving that individual's risk score.
* **Tailored Care Checklist:** Dynamically populates an actionable discharge checklist (e.g., home nursing visit within 48h, clinical pharmacist medication reconciliation, 7-day clinic follow-up) tailored to the patient's predicted risk profile.
* **Validation Sandbox:** Contains an interactive test tab to execute edge-case and robustness tests live in the browser.

---

## 14. Limitations and Responsible AI Principles
1. **Clinical Decision Support Framing:** GlucoShield is strictly a decision support tool designed to assist discharge planners; it must never be used as an autonomous diagnostic device or as justification to deny necessary inpatient care.
2. **Historical Data Bias (1999–2008):** The underlying dataset reflects US inpatient practice patterns from 1999–2008 and utilizes ICD-9 codes. Clinical guidelines (such as newer SGLT2 inhibitors and GLP-1 receptor agonists) have evolved.
3. **Unobserved Social Determinants of Health (SDoH):** The dataset does not include outpatient pharmacy adherence, health literacy, family caregiver support, or transportation access—factors that heavily influence 30-day readmissions.
4. **Demographic Equity:** We verified that decision thresholds are calibrated to prevent systematically higher false negative rates in underrepresented patient cohorts.

---

## 15. Future Improvements
1. **Direct EHR Interoperability (HL7 / FHIR APIs):** Integrate automated real-time patient chart parsing directly from hospital Epic and Cerner EHR systems.
2. **Clinical NLP on Unstructured Progress Notes:** Utilize clinical language models (e.g., BioClinicalBERT) to extract social determinants and nursing discharge notes.
3. **Longitudinal Trajectory Modeling:** Implement recurrent or temporal transformer architectures to model patient physiological trajectories across multiple successive hospitalizations.

---

## 16. Conclusion
The FUSE AI-201 Module 5 implementation successfully translated the approved Module 4 capstone proposal into a tested, functional, and explainable Clinical Decision Support System. By deduplicating patient encounters, mapping complex ICD-9 codes, engineering clinical utilization features, and training an ensemble XGBoost model with TreeSHAP interpretability, the system achieves the target clinical sensitivity ($\ge 65\%$) while providing actionable post-discharge checklists. The prototype stands ready for pilot demonstration and Module 6 cloud deployment.

---

## 17. Team Contributions
* **⭐ Team Lead & Full-Stack Contributor — Bililign Yibgeta Amare:**  
  Served as Team Lead and actively participated in **every stage** of the project from end to end:
  - **Problem Definition (Stage 1 & 2):** Formulated the clinical problem statement, selected XGBoost as the primary AI approach, and designed the complete system architecture.
  - **Data Engineering (Stage 3):** Developed the full data cleaning pipeline including patient deduplication, hospice exclusion, ICD-9 disease category mapping, and feature engineering (`data_pipeline.py`).
  - **Exploratory Data Analysis (Stage 4):** Performed descriptive statistical analysis and produced all 5 EDA visualizations (`eda.py`).
  - **Baseline & Model Training (Stage 5 & 6):** Built the Logistic Regression baseline, trained all candidate models (Random Forest, XGBoost, LightGBM), and conducted hyperparameter tuning with `scale_pos_weight = 10.14` to address class imbalance.
  - **Evaluation (Stage 7):** Performed threshold calibration (th = 0.45) achieving ≥65% clinical sensitivity, generated ROC curves, confusion matrices, and the False Negative error audit.
  - **Prototype Development:** Built the full interactive Streamlit clinical dashboard (`app.py`) including SHAP explainability and the dynamic discharge checklist.
  - **System Testing (Stage 8):** Authored and executed all 5 edge-case robustness tests (`test_suite.py`), achieving 100% pass rate.
  - **Documentation:** Authored the complete 17-section Module 5 Capstone Report and the project README.
* **Member 2 (Domain Specialist - Gebreslase Getachew Alemu):** Led clinical problem formulation, ICD-9 disease category mapping rules, and discharge intervention checklist design based on hospital readmission reduction protocols.
* **Member 3 (Data Engineer - Belay Tilahun Alene):** Developed `data_pipeline.py`, implemented patient deduplication logic, and built the missing value imputation and feature engineering transformers.
* **Member 4 (App Developer - Chalachew Getu Amarebet & Dagne Amdetsion):** Developed the interactive Streamlit clinical dashboard (`app.py`), pre-built patient scenario presets, and the real-time SHAP attribution display.
* **Member 5 (DevOps & Testing - Ebrahim Oumer Ali & Gutema Wako Anota):** Created `test_suite.py`, executed all Stage 8 robustness edge-case validations, and generated all EDA visualizations.
* **Member 6 (Responsible AI & Ethics - Sena AmareSena Amare):** Conducted ethical review, demographic fairness validation, and responsible AI documentation including the clinical disclaimer framework.
* **Member 7 (Documentation & Reporting - Shanbel Mohammed Ali & Tessema Ayele Alemu):** Authored clinical sections, threshold calibration analysis narrative, and the full capstone report.
* **Member 8 (System Integration - Yibeltal Meslie Alemayehu):** Coordinated module integration, final system testing coordination, and GitHub repository management.
* **All Members:** Actively participated in Capstone report review, threshold tuning discussions, and ethical AI review sessions.

---

## Group Reflection
* **What did we learn?**  
  We learned that raw accuracy in clinical machine learning is often misleading due to severe class imbalance (~9% positive class). Designing models for clinical utility requires prioritizing sensitivity (Recall) and false negative reduction over simple overall accuracy. We also learned that data hygiene—such as excluding deceased patients and deduplicating repeat admissions—is critical to prevent data leakage.
* **What was the most difficult part?**  
  Handling the high cardinality of ICD-9 diagnosis codes and medication dosage permutations without blowing up the feature space. Mapping ICD-9 codes into 9 clinically coherent diagnostic organ systems solved this dilemma effectively.
* **What technical problem did we encounter and how did we solve it?**  
  Initial unweighted tree models suffered from majority-class collapse (predicting 0 for almost all patients). We solved this by calculating the positive class scale factor (`scale_pos_weight = 10.14`) and calibrating the decision threshold to $th = 0.45$, which successfully raised recall to $65.71\%$.
* **What would we improve with more time?**  
  With more time, we would incorporate unstructured physician discharge summaries using clinical NLP and validate the model prospectively on contemporary (ICD-10) hospital data.
* **What did we learn about working as a team?**  
  Clear role specialization (separating data engineering, ML modeling, software prototype development, and clinical validation) enabled rapid, synchronized progress and ensured that every deliverable met the Module 5 standard.

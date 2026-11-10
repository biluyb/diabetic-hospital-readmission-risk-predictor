# Model Card: GlucoShield Inpatient Diabetes Readmission Risk Predictor

**Module 6 AI Governance & Clinical Model Card**  
**Project:** GlucoShield CDSS  
**Group:** Group 04 | FUSE AI-201 Capstone  
**Selected Model:** Calibrated XGBoost Classifier (`models/xgboost_final_model.joblib`)  
**Operating Threshold:** 0.45 (Clinical High-Sensitivity Calibration)  

---

## 1. Model Details

- **Model Name:** GlucoShield XGBoost Clinical Readmission Predictor
- **Model Version:** v1.0.0 (Production Candidate)
- **Model Type:** Extreme Gradient Boosted Decision Tree Ensemble (`xgboost.XGBClassifier`)
- **Developers:** Group 04 — Youth Empowerment and Employment in AI Program (YEEAP) / FUSE AI-201 Capstone:
  - *Lead Engineer & Architect:* Bililign Yibgeta Amare
  - *Clinical Specialists & Contributors:* Gebreslase Getachew Alemu, Belay Tilahun Alene, Chalachew Getu Amarebet, Dagne Amdetsion, Ebrahim Oumer Ali, Gutema Wako Anota, Sena AmareSena Amare, Shanbel mohammed ali, Tessema Ayele Alemu, Yibeltal Meslie Alemayehu.
- **Release Date:** November 2026
- **License:** Open Access Educational & Research Prototype (Apache 2.0 / MIT compatible)
- **Frameworks & Dependencies:** XGBoost 3.4+, Scikit-Learn 1.9+, SHAP 0.54+, Python 3.10+
- **Model Serialization:** Scikit-Learn Pipeline (`models/preprocessor.joblib`) + Serialized XGBoost booster (`models/xgboost_final_model.joblib`)

---

## 2. Intended Use

### Primary Intended Uses
- **Clinical Decision Support (CDSS):** Stratifies the risk of unplanned, all-cause **30-day hospital readmission** among diabetic inpatients at the time of discharge summary preparation.
- **Post-Acute Resource Allocation:** Assists discharge planning teams, hospital case managers, and inpatient nurses in targeting intensive transition interventions (home health nurse visits within 48h, clinical pharmacist medication reconciliation, expedited 7-day follow-up appointments).
- **Explainable Bedside Review:** Couples risk probability with local TreeSHAP clinical feature attribution to show attending physicians which clinical factors drove the risk score.

### Primary Intended Users
- Hospital discharge coordinators and case managers.
- Inpatient attending hospitalists and endocrinologists.
- Clinical transition teams and healthcare quality officers.

### Out-of-Scope & Prohibited Uses
- **Autonomous Diagnostic Decision-Making:** This model must never operate autonomously or override a licensed clinician's medical judgment.
- **Discharge Denial or Premature Discharge:** The score must never be used to deny necessary inpatient care, reduce covered bed-days, or restrict emergency care access.
- **Outpatient Walk-in Clinics:** Calibrated strictly for acute inpatient diabetic admissions; not validated for outpatient or emergency triage before admission.

---

## 3. Factors and Inputs

The model consumes **155 transformed features** derived from patient demographics, hospital encounter metrics, laboratory findings, medication adjustments, and primary/secondary diagnosis categories.

| Category | Input Variables | Clinical Significance |
| :--- | :--- | :--- |
| **Demographics** | `age` (10-yr brackets), `gender`, `race` | Risk baseline and subgroup physiological vulnerability |
| **Encounter Metrics** | `time_in_hospital`, `admission_type_id`, `admission_source_id`, `discharge_disposition_id` | Acuity of index hospitalization |
| **Utilization History** | `number_inpatient`, `number_emergency`, `number_outpatient`, `total_prior_visits` | Disease chronicity and historical healthcare reliance |
| **Clinical Intensity** | `num_lab_procedures`, `num_procedures`, `num_medications`, `procedure_intensity`, `meds_per_day` | Diagnostic complexity and therapeutic intensity |
| **Diagnostic Groups** | `diag_1_group`, `diag_2_group`, `diag_3_group` (Mapped to 9 ICD-9 systems: Circulatory, Respiratory, Diabetes, Digestive, etc.) | Underlying multi-organ dysfunction and acute etiology |
| **Glycemic Markers** | `A1Cresult` (`>7`, `>8`, `Norm`, `None`), `max_glu_serum` | Chronic vs acute glycemic instability |
| **Pharmacotherapy** | `insulin`, `metformin`, `glipizide`, `glyburide`, `pioglitazone`, `rosiglitazone`, `change`, `diabetesMed`, `num_dosage_changes` | Inpatient medication titrations and stability |

---

## 4. Training Data

- **Data Source:** UCI Machine Learning Repository — *Diabetes 130-US Hospitals for Years 1999–2008 Dataset* (Strack et al., 2014; Dataset ID: 296).
- **Raw Encounter Count:** 101,766 clinical encounters across 71,518 unique patients.
- **Causal Cohort Filtering:**
  - Excluded 2,423 encounters where the patient expired in-hospital or transitioned to hospice care (`discharge_disposition_id` $\in \{11, 13, 14, 19, 20, 21\}$), because readmission is logically impossible.
  - Deduplicated multiple encounters per patient, retaining strictly the **first indexed admission** ($n = 69,990$). This prevents patient-level test leakage.
- **Cleaned Dataset Size:** 69,990 unique patient encounters.
- **Class Distribution:** 6,285 positive cases (<30 days readmitted; 8.98%) vs. 63,705 negative cases (>=30 days or no readmission; 91.02%).
- **Class Imbalance Handling:** Applied `scale_pos_weight = 10.14` in the XGBoost objective function to prevent majority-class collapse.

---

## 5. Evaluation Data

- **Evaluation Split:** Independent **20% holdout test set** ($n = 13,998$ encounters), stratified by the target label (`random_state=42`).
- **Data Leakage Safeguards:** Preprocessor transformations (median imputers, standard scalers, and one-hot encoders) were fitted strictly on the 80% training set ($n = 55,989$) and evaluated blindly on the holdout test set.

---

## 6. Evaluation Results

### Multi-Model Benchmark Comparison (Holdout Test Set)

| Model | Test ROC-AUC | PR-AUC | Recall @ th=0.45 | Specificity @ th=0.45 | Precision @ th=0.45 | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trivial Majority Baseline** | 0.5000 | 0.0898 | 0.00% | 100.00% | 0.00% | 0.0000 |
| **Logistic Regression (L2, Balanced)** | 0.6469 | 0.1572 | 53.06% | 67.51% | 13.88% | 0.2201 |
| **Random Forest (Balanced Subsample)**| 0.6462 | 0.1554 | 43.91% | 76.92% | 15.82% | 0.2326 |
| **LightGBM Classifier** | 0.6465 | 0.1570 | 53.70% | 67.01% | 13.84% | 0.2201 |
| **XGBoost Classifier (Selected)** | **0.6465** | **0.1580** | **65.71%** | **54.54%** | **12.48%** | **0.2098** |

### Decision Threshold Calibration (0.45 Cutoff)
- **Rationale:** In clinical inpatient discharge, missing a preventable unplanned readmission (**False Negative**) leads to clinical deterioration and financial penalties under the CMS Hospital Readmissions Reduction Program (HRRP). Conversely, scheduling an unnecessary nurse check-in (**False Positive**) is benign.
- At the standard 0.50 cutoff, XGBoost achieves only 51.87% recall.
- Calibrating the operating threshold to **0.45** raises sensitivity to **65.71%**, successfully intercepting **826 out of 1,257** true 30-day readmissions.

### Holdout Confusion Matrix Breakdown (th = 0.45)
- **True Positives (TP):** 826
- **False Negatives (FN):** 431
- **True Negatives (TN):** 6,949
- **False Positives (FP):** 5,792

### False Negative Error Audit
Clinical investigation into the 431 missed cases revealed that False Negatives presented with:
1. Significantly lower prior inpatient utilization (0.04 average prior stays vs. 0.57 for True Positives).
2. Shorter hospitalizations (3.53 days vs. 5.34 days for True Positives).
3. Fewer recorded secondary comorbidities (7.09 vs. 7.81).
*Clinical takeaway:* False Negatives reflect patients who appeared clinically stable upon discharge but suffered unrecorded outpatient complications (e.g. social determinants, prescription unaffordability, diet non-compliance).

---

## 7. Ethical Considerations

- **HIPAA Compliance & De-identification:** The dataset is fully de-identified in accordance with HIPAA Safe Harbor standards. No direct Protected Health Information (names, medical record numbers, addresses, social security numbers) is stored, processed, or logged.
- **Fairness & Demographic Subgroup Parity:**
  - Evaluated across racial cohorts (Caucasian, African American, Hispanic, Asian, Other) and sex (Female, Male).
  - Decision thresholding was audited to confirm that false-negative rates do not systematically penalize underrepresented demographic groups.
- **Explainability as a Safety Measure:** Black-box predictions are prohibited. Every prediction is paired with real-time TreeSHAP feature attributions, allowing attending physicians to verify clinical plausibility.
- **Human Oversight:** The system operates strictly as decision support. No post-acute resource order is executed without licensed clinician confirmation.

---

## 8. Limitations and Recommendations

1. **Historical Practice Gap (1999–2008):** Inpatient care protocols, glucose monitoring technologies (e.g., continuous glucose monitors), and modern pharmaceutical agents (GLP-1 receptor agonists, SGLT2 inhibitors) have expanded significantly since 2008.
2. **ICD-9 Diagnostic Coding:** The dataset utilizes ICD-9 codes. Clinical deployment requires mapping contemporary ICD-10-CM codes into the 9 established diagnostic organ system buckets.
3. **Absence of Social Determinants of Health (SDoH):** The model lacks visibility into health literacy, income stability, primary caregiver support, and pharmacy transportation—known non-clinical drivers of hospital readmission.
4. **Recommendation for Clinical Teams:** Treat the model's score as an initial risk filter. Combine model predictions with bedside clinical frailty assessments and direct patient social work evaluations before finalizing discharge plans.


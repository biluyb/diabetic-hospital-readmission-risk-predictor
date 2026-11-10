# GlucoShield CDSS — Statement on Real vs. Simulated Data

**FUSE AI-201 Capstone | Module 6: Academic and Research Integrity Declaration**  
**Project:** GlucoShield — Diabetes Hospital Readmission Risk Predictor  
**Author / Team Lead:** Bililign Yibgeta Amare (on behalf of Group 04)  
**Date:** November 2026  

---

## 1. Purpose of This Statement

In strict adherence to academic honesty, research ethics, and professional MLOps standards, this document explicitly details the origin, nature, and usage of all data within the GlucoShield project repository. It distinguishes verified historical benchmark data from simulated monitoring data.

---

## 2. Authentic Real-World Benchmark Dataset

### Identification & Source
- **Dataset Name:** Diabetes 130-US Hospitals for Years 1999–2008
- **Repository:** UCI Machine Learning Repository (Dataset ID: 296)
- **Primary Literature Reference:** Strack, C., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., & Clore, J. N. (2014). *Impact of HbA1c Measurement on Hospital Readmissions in Diabetes: Analysis of 70,000 Clinical Database Records.* BioMed Research International, 2014, 781670.
- **Nature of Data:** Real-world clinical inpatient encounters extracted from 130 commercial and community hospitals across the United States between 1999 and 2008.
- **De-Identification:** Fully anonymized in compliance with HIPAA Safe Harbor regulations. No names, addresses, social security numbers, or Medical Record Numbers (MRNs) are present.
- **Cohort Usage in GlucoShield:**
  - Raw records: 101,766 encounters across 71,518 unique patients.
  - Excluded expired/hospice cases: 2,423 records excluded for causal validity.
  - Deduplicated encounters: 69,990 unique patient index encounters retained.
  - **All model training, baseline benchmarking, hyperparameter tuning, holdout test evaluations (ROC-AUC = 0.647), and TreeSHAP calculations are conducted strictly on this authentic historical dataset.**

---

## 3. Simulated Production Monitoring Data

### Rationale for Simulation
In hospital software engineering, access to live production streaming Electronic Health Record (EHR) telemetry is strictly gated behind institutional HIPAA firewalls and clinical enterprise contracts. To demonstrate and validate the operational readiness of our **Data Drift Detection and Model Monitoring Pipeline** (`monitoring/`), realistic production data streams had to be simulated.

### Scope of Simulated Data
- **Simulated Batch 1 (Month 1 - Stable Flow):** A sample of 2,500 patient encounters drawn from the historical distribution to represent routine, stable hospital operations ($PSI < 0.10$).
- **Simulated Batch 2 (Month 2 - Winter Respiratory Surge & Demographic Aging):** A mathematically shifted sample of 2,500 patient encounters where length of stay was increased (+1.2 days on average), elderly demographic representation was shifted towards age bracket `[70-80)`, and respiratory primary diagnoses were elevated.
- **Usage:** Used solely to validate the sensitivity of the **Population Stability Index (PSI)** and **Kolmogorov-Smirnov (KS)** drift algorithms (`monitoring/drift_detector.py`) and to verify that automated alerts trigger when distribution shifts occur.

---

## 4. Explicit Integrity Declarations

1. **No Real-World Telemetry Claimed:** The project team **does not claim** that simulated monitoring batches represent actual hospital traffic, real patient records, or live streaming clinical telemetry from an active hospital partner.
2. **Authentic Performance Reporting:** All evaluation metrics reported in the project documentation (Test ROC-AUC = 0.647, Recall = 65.71%, Specificity = 54.54%, Precision = 12.48%) were computed from actual model predictions on the independent 20% holdout test set ($n = 13,998$) of the authentic UCI benchmark dataset.
3. **No Manufactured Evidence:** Neither model metrics, confusion matrix values, nor test suite results have been fabricated.

---

*Declared and signed on behalf of Group 04:*  
**Bililign Yibgeta Amare** — Team Lead & Full-Stack Contributor  
**Sena AmareSena Amare** — Responsible AI & Ethics Lead  


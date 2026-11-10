# GlucoShield CDSS — AI Governance, Ethics & Risk Management Plan

**FUSE AI-201 Capstone | Module 6: Responsible AI and Clinical Governance**  
**Project:** GlucoShield Diabetic Readmission CDSS  
**Group:** Group 04 (YEEAP Capstone)  
**Governance Lead:** Bililign Yibgeta Amare (Lead) & Sena AmareSena Amare (Responsible AI Lead)  

---

## 1. Governance Principles & Ethical Framework

GlucoShield adheres to internationally recognized guidelines for **Trustworthy AI in Healthcare**, including the WHO Ethics and Governance of AI for Health, FDA Clinical Decision Support Guidance, and the HIPAA Security Rule.

The system is governed by five foundational pillars:
1. **Clinical Primacy:** The tool assists and informs; licensed healthcare practitioners retain ultimate clinical and legal authority over patient care plans.
2. **Patient Privacy & Confidentiality:** Absolute de-identification and minimization of patient data.
3. **Safety & High-Sensitivity Thresholding:** Calibration prioritizing sensitivity ($\ge 65\%$) to minimize dangerous False Negatives in vulnerable patients.
4. **Algorithmic Transparency:** Full explainability via local TreeSHAP attribution on every prediction.
5. **Continuous Accountability:** Regular auditing of drift, data quality, and demographic equity.

---

## 2. Patient Privacy and HIPAA Compliance

- **De-Identification by Design:** In accordance with the HIPAA Safe Harbor standard (45 CFR § 164.514(b)(2)), all direct identifiers—including patient names, social security numbers, street addresses, phone numbers, and Medical Record Numbers (MRNs)—are excluded.
- **In-Memory Session Processing:** The interactive web dashboard and API endpoints evaluate patient parameters in transient volatile memory. No patient encounter records, IP addresses, or session payloads are stored to persistent database disks during routine inference.
- **Data Transmission Security:** In production deployment, all web traffic and REST API calls are enforced over encrypted HTTPS / TLS 1.3 tunnels to protect clinical payloads in transit.

---

## 3. Algorithmic Fairness & Bias Mitigation

Historical healthcare datasets inherently encode societal, socioeconomic, and healthcare access disparities. To prevent the propagation of historical bias:

### A. Subgroup Parity Auditing
The model's discriminative ability (ROC-AUC) and error rates (False Negative Rate, False Positive Rate) were evaluated across demographic subgroups:
- **Sex / Gender:** Audited across Male and Female cohorts.
- **Race / Ethnicity:** Audited across Caucasian, African American, Hispanic, Asian, and Other categories.
- **Age Brackets:** Evaluated across young adults, middle-aged patients, and elderly inpatients ($\ge 70$ years).

### B. Mitigation of False Negative Disparities
In healthcare, a False Negative (failing to identify a patient at risk of acute readmission) can lead to preventable morbidity and hospital emergency returns. The decision threshold was calibrated down from the generic 0.50 cutoff to **0.45**, raising positive-class recall to **65.71%** and ensuring that underrepresented patient cohorts receive proactive post-discharge support rather than being systematically overlooked.

---

## 4. Human-in-the-Loop Clinical Safeguards

1. **Mandatory Educational Disclaimer:** Every UI page, report, and API response explicitly states that GlucoShield is an educational research prototype and not a diagnostic device.
2. **Non-Autonomous Actions:** System recommendations (e.g., home nursing visits, pharmacist medication reviews) appear as a suggested clinical checklist. The discharge planner must review and authorize each item.
3. **Dual-Signal Bedside Integration:** Attending hospitalists are instructed to evaluate the model's statistical score alongside bedside clinical findings, vital signs, physical frailty, and outpatient caregiver availability.

---

## 5. Security & Artifact Integrity

- **Model Serialization Integrity:** Model pipelines (`models/preprocessor.joblib`, `models/xgboost_final_model.joblib`) are write-protected and loaded only from verified repository locations.
- **Dependency Vulnerability Management:** Project dependencies are pinned with version constraints in `requirements.txt` and audited for known Common Vulnerabilities and Exposures (CVEs).
- **Graceful Failure Handling:** Malformed inputs, negative numbers, or corrupted clinical codes are caught by `src/validation.py` and rejected safely with informative error messages, preventing system crashes or silent data corruption.


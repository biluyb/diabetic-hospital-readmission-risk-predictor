# FUSE AI-201 Capstone Retrospective — Student Reflection

**Project:** GlucoShield — Diabetes Hospital Readmission Risk Predictor  
**Cohort & Group:** YEEAP Capstone | Group 04  
**Author / Team Lead:** Bililign Yibgeta Amare (on behalf of Group 04)  
**Date:** November 2026  

---

## 1. Executive Summary & Overview of the Journey

Completing the FUSE AI-201 Capstone across Modules 4, 5, and 6 transformed our understanding of applied machine learning in high-stakes domains. Moving from initial industry problem formulation (Module 4) to data engineering and model training (Module 5), and ultimately to MLOps, monitoring, containerization, and clinical governance (Module 6) demonstrated that building an effective AI solution requires far more than achieving high validation accuracy. It demands rigorous causal data hygiene, deep domain alignment, honest error analysis, and robust operational safeguards.

---

## 2. Technical Challenges Encountered and Solutions Engineered

### The Class Imbalance Accuracy Trap
Our first major technical obstacle was severe class imbalance (~8.98% positive 30-day readmissions). When we first trained standard unweighted classifiers, models achieved deceptively high accuracy (>91%) but near-zero clinical recall (<3%). In hospital discharge planning, missing a patient destined for readmission (**False Negative**) carries severe clinical consequences, whereas a **False Positive** merely triggers an extra telephone call. 
- *Solution:* We calculated the positive class scale factor (`scale_pos_weight = 10.14`), incorporated cost-sensitive loss weighting, and calibrated the operating decision threshold down from the default 0.50 to **0.45**, raising positive-class recall to **65.71%** (capturing 826 of 1,257 true readmissions).

### Causal Data Hygiene & Preventing Leakage
In initial exploratory passes, patients with multiple admissions risked leaking clinical patterns between training and testing splits. Furthermore, records included patients who expired during hospitalization or entered hospice care.
- *Solution:* We enforced strict domain exclusions—filtering out 2,423 expired/hospice encounters where readmission is logically impossible, and deduplicating records to retain strictly the index first admission per unique patient ($n = 69,990$).

### High-Cardinality Dimensionality Explosion
Raw ICD-9 codes contained over 800 distinct diagnostic entries, threatening severe dimensionality explosion and tree overfitting.
- *Solution:* We mapped ICD-9 codes into 9 clinically coherent diagnostic organ systems (Circulatory, Respiratory, Digestive, Diabetes, Musculoskeletal, etc.), preserving diagnostic meaning while drastically reducing noise.

### Real-Time Explainability at the Bedside
Black-box tree predictions cannot earn physician trust in hospital settings.
- *Solution:* We integrated native TreeSHAP local attribution (`src/explainability.py`), decomposing predictions into the top 5 clinical contributors within ~12 milliseconds.

---

## 3. Responsible AI and Governance Lessons

The most significant conceptual shift in Module 6 was realizing that ethical AI is not an afterthought or a boilerplate disclaimer—it is an engineering discipline:
- **Calibrating for Safety:** Traditional ML seeks the balance point maximizing F1 or accuracy. Clinical ML must prioritize sensitivity (Recall $\ge 65\%$) to minimize missed patients.
- **Data Limitations & SDoH:** We recognized that our model's performance ceiling ($\text{ROC-AUC} \approx 0.65$) is not an algorithmic defect, but a fundamental reflection of tabular hospital data missing outpatient social determinants of health (income, caregiver support, pharmacy access).
- **Honesty in Telemetry:** Labeling our monitoring drift cohorts transparently as simulated data reinforced the principle of academic and professional integrity.

---

## 4. Team Collaboration & Project Leadership

Leading Group 04 taught me that role specialization and synchronized git-based workflows are essential for multi-disciplinary AI teams:
- Coordinating data engineers, clinical domain specialists, app developers, and test engineers ensured that every deliverable—from `src/validation.py` to `monitoring/monitor.py`—was thoroughly validated.
- Authoring comprehensive unit tests (17 automated tests passing in under 6 seconds) created confidence that our codebase could be improved without breaking existing working prototypes.

---

## 5. Conclusion & Next Steps

GlucoShield stands as a complete, honest, and reproducible capstone portfolio that satisfies every requirement of FUSE AI-201 Module 6. It proves that responsible AI engineering can bridge complex tree boosting algorithms and actionable bedside clinical decision support.


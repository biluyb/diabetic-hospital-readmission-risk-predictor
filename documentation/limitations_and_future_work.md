# GlucoShield CDSS — Limitations and Future Work

**FUSE AI-201 Capstone | Module 6: Critical Analysis & Research Roadmap**  
**Project:** GlucoShield Diabetic Readmission CDSS  
**Group:** Group 04 (YEEAP Capstone)  

---

## 1. Technical & Clinical Limitations

While GlucoShield successfully demonstrates an end-to-end clinical decision support pipeline achieving $\ge 65\%$ sensitivity on holdout encounters, rigorous evaluation highlights several real-world limitations:

### A. Historical Cohort Temporal Drift (1999–2008 Data)
The underlying benchmark dataset (UCI Diabetes 130-US Hospitals) spans 1999 to 2008. Over the past two decades:
- Inpatient glycemic targets and diabetes standards of care have evolved.
- Newer, highly effective pharmacological classes—such as SGLT2 inhibitors (e.g., empagliflozin, dapagliflozin) and GLP-1 receptor agonists (e.g., semaglutide, liraglutide)—are unrepresented in historical records.
- Continuous Glucose Monitoring (CGM) systems have altered ambulatory and inpatient monitoring workflows.

### B. Legacy ICD-9 Diagnostic Coding
The dataset utilizes ICD-9-CM diagnostic codes. Although our pipeline maps these codes into 9 clinical organ systems (Circulatory, Respiratory, Digestive, Diabetes, etc.), modern health systems internationally utilize ICD-10-CM or SNOMED-CT. Prospective deployment requires implementing an ICD-10 mapping crosswalk.

### C. Absence of Social Determinants of Health (SDoH)
Hospital readmission is heavily governed by non-clinical factors that exist outside the EHR:
- Patient health literacy and numeracy.
- Outpatient prescription copay affordability and insurance gaps.
- Availability of home caregiver support.
- Food security and refrigeration access for insulin storage.
Because these factors are unrecorded in the benchmark dataset, models operating solely on inpatient tabular labs will encounter an inherent predictive ceiling (typically $\text{ROC-AUC} \approx 0.65 - 0.70$).

### D. Lack of Unstructured Clinical Narratives
Physician progress notes, nursing shift handover summaries, and discharge summaries contain rich, nuanced qualitative observations (e.g., patient frailty, cognitive decline, uncooperative behaviors) that are not captured in structured numerical/categorical tables.

---

## 2. Research Roadmap & Future Work

```
+───────────────────────────────────────────────────────────────────────────────+
|                           FUTURE WORK ROADMAP                                 |
+───────────────────────────────────────────────────────────────────────────────+

PHASE 1: Modern Data Crosswalk & EHR Standards
  ├── Map ICD-10-CM diagnosis codes to established 9 clinical organ systems
  └── Implement HL7 FHIR (Fast Healthcare Interoperability Resources) data models

PHASE 2: Multimodal Clinical NLP Integration
  ├── Fine-tune domain clinical language models (BioClinicalBERT / ClinicalLongformer)
  └── Extract SDoH indicators, social frailty, and medication compliance barriers from
      unstructured physician discharge summaries

PHASE 3: Longitudinal Patient Trajectory Modeling
  ├── Transition from static single-encounter cross-sectional representations to
      temporal sequence architectures (Recurrent Neural Networks / Transformers)
  └── Model multi-year HbA1c fluctuations and progressive microvascular complications

PHASE 4: Prospective Multi-Center Clinical Trial
  ├── Deploy in silent shadow mode across partner hospital discharge planning teams
  └── Measure real-world clinical utility: reduction in 30-day readmissions,
      physician alert fatigue, and case manager checklist adoption rates
```

---

## 3. Concluding Assessment

GlucoShield demonstrates that transparent, explainable machine learning models calibrated with clinical sensitivity in mind provide significant value over static scoring indices like LACE. By acknowledging its current boundaries and outlining a concrete future roadmap, the project bridges academic AI development and realistic hospital implementation.


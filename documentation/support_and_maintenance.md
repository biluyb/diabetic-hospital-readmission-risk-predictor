# GlucoShield CDSS — Support, Maintenance & Operations Plan

**FUSE AI-201 Capstone | Module 6: System Reliability and Lifecycle Operations**  
**Project:** GlucoShield Diabetic Readmission CDSS  
**Group:** Group 04 (YEEAP Capstone)  
**Maintenance Lead:** Ebrahim Oumer Ali & Yibeltal Meslie Alemayehu  

---

## 1. Service Level Objectives (SLOs) and Performance Targets

| Metric | Target | Rationale |
| :--- | :---: | :--- |
| **Inference Latency** | $< 250\text{ ms}$ (p95) | Real-time response during hospital discharge review without blocking clinical workflow. |
| **System Availability** | $99.5\%$ uptime | Critical clinical support availability during standard daytime discharge hours (07:00 – 19:00). |
| **Automated Test Pass Rate** | $100\%$ | Zero tolerance for regressions across the 17 automated unit and integration tests. |
| **SHAP Attribution Latency**| $< 50\text{ ms}$ | TreeSHAP fast path must render top-5 features instantaneously alongside score. |

---

## 2. Bug Triage & Incident Response Workflow

```
[ Incident / Bug Reported ]
            │
            ▼
[ Severity Classification ]
    ├── P1 (Critical): App crash, model loading failure, corrupted predictions
    ├── P2 (Major): Validation false rejection, SHAP rendering timeout
    └── P3 (Minor): UI styling alignment, typo in checklist recommendation
            │
            ▼
[ Root Cause Analysis & Diagnostic Audit ]
    ├── Reproduce via `tests/` or `src/test_suite.py`
    ├── Check input payloads against `src/validation.py` rules
    └── Inspect model artifact checksums in `models/`
            │
            ▼
[ Hotfix & Verification ]
    ├── Execute full automated pytest suite (`python -m pytest tests/ -v`)
    └── Re-verify demonstration scenarios
            │
            ▼
[ Promotion & Release ]
    └── Deploy verified container or update production repository
```

---

## 3. Fallback Operations (Graceful Degradation)

If an unexpected runtime failure occurs:
1. **Model Loading Failure:** If `models/xgboost_final_model.joblib` fails to load, `app.py` catches the exception on startup and presents a clear diagnostic alert with recovery instructions (`run_full_pipeline.py`) rather than crashing unhandled.
2. **Input Validation Failures:** If a clinician enters malformed or negative values, the system safely halts prediction, highlights the offending fields, and provides plain-English correction instructions.
3. **SHAP Tree Explainer Timeout:** If the TreeSHAP engine encounters an unexpected memory constraint, the main risk score and discharge checklist are rendered immediately, and a non-blocking warning indicates that local attribution is temporarily deferred.
4. **Clinical Fallback Heuristic:** In the event of total application unavailability, hospital staff revert to standard clinical practice guidelines (routine LACE index calculation and standard clinical pharmacist medication reviews).

---

## 4. Model Retraining and Deprecation Lifecycle

1. **Cadence:** Scheduled retrospective performance audits every **6 months**; event-driven audits triggered whenever drift monitoring flags $\text{PSI} \ge 0.25$ on key clinical predictors.
2. **Retraining Dataset:** Assembled from the latest 12 months of clean inpatient diabetic discharges, deduplicated by patient number and excluding deceased/hospice cases.
3. **Shadow Testing Requirement:** Prior to replacing the active operational model, a candidate model must run in shadow mode for at least **14 business days** and demonstrate non-inferior ROC-AUC ($\Delta \le 0.01$) and clinical recall ($\ge 65.0\%$).
4. **Deprecation Policy:** Deprecated model weights are archived in `models/archive/` alongside complete experiment tracking run logs for 7 years to support clinical retrospective audits.


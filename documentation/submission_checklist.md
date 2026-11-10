# GlucoShield CDSS — Capstone Final Submission Checklist

**FUSE AI-201 Capstone | Module 6: Submission Verification & Audit**  
**Group:** Group 04 | **Lead:** Bililign Yibgeta Amare  

---

## 1. Portfolio Deliverables Checklist

| # | Item / Deliverable | Status | Location in Repository | Verification Method |
| :---: | :--- | :---: | :--- | :--- |
| 1 | **Working Streamlit Prototype** | ✅ **Verified** | `app.py` | Starts via `streamlit run app.py`, loads artifacts, validates inputs, scores patients. |
| 2 | **3 Clinical Demonstration Presets** | ✅ **Verified** | `app.py` (Sidebar dropdown) | Scenario 1 (27.1%), Scenario 2 (72.7%), Scenario 3 (48.3% borderline). |
| 3 | **Calibrated Decision Threshold (0.45)**| ✅ **Verified** | `src/validation.py`, `app.py` | Consistently enforced across UI, tests, API, and evaluation metrics. |
| 4 | **SHAP Local Explainability Engine** | ✅ **Verified** | `src/explainability.py` | Real-time TreeSHAP local attribution rendering top-5 features in <15ms. |
| 5 | **Input Validation & Sanitization** | ✅ **Verified** | `src/validation.py` | Catches negative stays, non-numeric strings, and out-of-range clinical outliers. |
| 6 | **Automated Test Suite (17 Tests)** | ✅ **Verified** | `tests/` | 17/17 passed via `python -m pytest tests/ -v`. |
| 7 | **System Edge-Case Robustness Harness** | ✅ **Verified** | `src/test_suite.py` | 5/5 passed via `python -m src.test_suite`. |
| 8 | **Reproducible Experiment Tracking** | ✅ **Verified** | `evaluation/experiment_runs.json`, `csv` | 5 benchmark model runs logged with hyperparameters and metrics. |
| 9 | **Monitoring & Drift Detection Engine** | ✅ **Verified** | `monitoring/drift_detector.py`, `monitor.py` | PSI & KS test statistics computed; drift report generated. |
| 10 | **Monitoring Visualizations** | ✅ **Verified** | `plots/monitoring_drift.png` | Automated distribution & PSI charts generated. |
| 11 | **FastAPI REST API Microservice** | ✅ **Verified** | `src/api.py` | `GET /health` and `POST /predict` verified via integration tests. |
| 12 | **Production Docker Configuration** | ✅ **Verified** | `Dockerfile`, `.dockerignore` | Pinned Python 3.11-slim container with healthchecks and dependencies. |
| 13 | **Master Pipeline Runner** | ✅ **Verified** | `run_full_pipeline.py` | Runs stages 1 through 8 in sequence without errors. |

---

## 2. Capstone Documentation Suite Checklist

| # | Document | File Path | Core Contents & Compliance |
| :---: | :--- | :--- | :--- |
| 1 | **8-Section Clinical Model Card** | [`documentation/model_card.md`](model_card.md) | Mitchell et al. format: Model Details, Intended Use, Factors, Training Data, Eval Data, Results, Ethics, Limitations. |
| 2 | **System Architecture Specification** | [`documentation/architecture.md`](architecture.md) | End-to-end data flow, ASCII diagram, Mermaid diagrams, MLOps components, Implemented vs Proposed table. |
| 3 | **Production Monitoring Strategy** | [`documentation/monitoring_plan.md`](monitoring_plan.md) | Telemetry metrics, PSI/KS thresholds, automated alerting, retraining workflow, governance roles. |
| 4 | **Empirical Drift Detection Report** | [`documentation/drift_report.md`](drift_report.md) | Baseline vs. Month 1 vs. Month 2 comparison, PSI table, simulated data statement. |
| 5 | **AI Ethics & Governance Plan** | [`documentation/governance_plan.md`](governance_plan.md) | HIPAA Safe Harbor compliance, demographic fairness, clinical human oversight, disclaimer. |
| 6 | **Support & Maintenance Plan** | [`documentation/support_and_maintenance.md`](support_and_maintenance.md) | SLOs (<250ms), P1-P3 bug triage, fallback operations, 6-month retraining schedule. |
| 7 | **Deployment & Operations Guide** | [`documentation/deployment_guide.md`](deployment_guide.md) | Local run, Docker container, Streamlit Community Cloud, FastAPI cURL requests. |
| 8 | **Experiment Tracking Methodology** | [`documentation/experiment_tracking.md`](experiment_tracking.md) | JSON/CSV tracking architecture, benchmark run logs, reproducibility guide. |
| 9 | **Limitations & Research Roadmap** | [`documentation/limitations_and_future_work.md`](limitations_and_future_work.md) | Historical 1999-2008 data, ICD-9/10 crosswalk, SDoH absence, multi-center trials. |
| 10 | **Student Capstone Retrospective** | [`retrospective.md`](../retrospective.md) | One-page reflection on technical challenges, threshold calibration, team learnings. |
| 11 | **Simulated Data Declaration** | [`simulated_data_statement.md`](../simulated_data_statement.md) | Academic honesty declaration separating authentic UCI data from simulated drift cohorts. |
| 12 | **Master Portfolio README** | [`README.md`](../README.md) | Comprehensive overview, badges, team roster, quickstart, evaluation table, directory layout. |

---

## 3. Video Presentation Checklist (<= 10 Minutes)

- [x] **Timing Allocation:** Planned and scripted for exactly 10 minutes (~1,400 words at 140 wpm).
- [x] **Script Reference:** Follow [`documentation/presentation_script.md`](presentation_script.md).
- [x] **Slide Structure:** 10 slides mapped directly to project deliverables.
- [x] **Screen Demonstration:** Includes walkthrough of all 3 demonstration scenarios (Low 27.1%, High 72.7%, Borderline 48.3%).
- [x] **Explainability Spotlight:** Demonstrates real-time TreeSHAP local attribution table.
- [x] **MLOps Evidence:** Shows automated test suite passing (17/17) and drift chart (`plots/monitoring_drift.png`).
- [x] **Disclaimer Visibility:** Prominently points out the educational prototype disclaimer.
- [x] **Speaker:** Bililign Yibgeta Amare (Team Lead) presenting on behalf of Group 04.

---

## 4. Final Verification Signature

*All items listed above have been implemented, tested, verified on disk, and audited for complete academic and technical integrity.*

**Lead Engineer & Team Lead:** Bililign Yibgeta Amare  
**Date of Final Audit:** November 11, 2026  
**Capstone Program:** Youth Empowerment and Employment in AI Program (YEEAP) — FUSE AI-201 Module 6  


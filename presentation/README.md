# GlucoShield CDSS — Capstone Presentation Guide

**FUSE AI-201 Capstone | Module 6: Final Presentation Deliverable**  
**Project:** GlucoShield — Diabetes Hospital Readmission Risk Predictor  
**Team:** Group 04 | **Cohort:** Youth Empowerment and Employment in AI Program (YEEAP)  
**Presenter:** Bililign Yibgeta Amare (Team Lead)  
**Target Duration:** 9 Minutes 30 Seconds (Max 10:00)

---

## 1. Deliverables in This Directory

| File | Purpose |
| :--- | :--- |
| `GlucoShield_Capstone_Presentation.pptx` | **Master 9-slide PowerPoint presentation** in 16:9 widescreen format with embedded speaker notes on every slide. |
| `GlucoShield_Presentation_Script.docx` | **Complete verbatim speaking script**, slide-by-slide cues, timing allocation, live demonstration checklist, and evaluator Q&A defense cheat sheet. |
| `preview/slide_01_preview.png` ... `slide_09_preview.png` | **High-resolution image previews** of all nine slides for instant visual review without requiring Microsoft Office. |
| `preview/presentation_overview.png` | **Composite 3x3 contact sheet** displaying the full presentation narrative at a glance. |
| `README.md` | This technical guide and execution manual. |

---

## 2. Master Slide Timing & Cue Sheet

| Slide | Title | Target Time | Cumulative | Visual / Action |
| :---: | :--- | :---: | :---: | :--- |
| **1** | Title & Project Introduction | 0:30 | 0:30 | Executive cover card, Group 04 roster, system quick facts |
| **2** | Clinical Challenge & Motivation | 0:45 | 1:15 | Clinical burden, HRRP penalties, Problem-to-Solution flow |
| **3** | Dataset Hygiene & Preprocessing | 1:00 | 2:15 | 4-stage pipeline: 101k raw -> 69k clean -> 9 ICD-9 groups |
| **4** | Model Benchmarking & Selection | 1:00 | 3:15 | 5-model comparison table + Holdout ROC curves |
| **5** | Evaluation & Threshold Calibration | 1:00 | 4:15 | 5 KPI cards (65.71% recall) + Confusion Matrix (826 TP) |
| **6** | Live Prototype Demonstration | 2:30 | 6:45 | **Alt-Tab to Streamlit (`http://localhost:8501`)**: Scenarios 1, 2, 3 |
| **7** | TreeSHAP XAI & MLOps Drift | 1:00 | 7:45 | TreeSHAP bedside attribution + PSI drift chart (PSI=0.385) |
| **8** | Testing, Deployment & Governance | 1:00 | 8:45 | 17/17 pytest + 5/5 Stage 8 checks + Docker/FastAPI architecture |
| **9** | Retrospective, Roadmap & Wrap-Up | 0:45 | 9:30 | Learnings, limitations, future FHIR roadmap, thank you |

**Total Presentation Time:** Exactly 9 minutes 30 seconds (leaving 30 seconds buffer under the 10:00 cap).

---

## 3. Pre-Presentation Setup Checklist

### Step 1: Start the Streamlit Application
Open a terminal and start the clinical dashboard:
```powershell
cd D:\Projects\diabets_prediction
python -m streamlit run app.py --server.port 8501
```
Verify the app is active at `http://localhost:8501`.

### Step 2: Have the Automated Test Suite Ready
In a second terminal, verify that all 17 tests pass:
```powershell
python -m pytest tests/ -v
```
Keep this terminal minimized in case evaluators ask to see live automated test execution.

### Step 3: Open PowerPoint in Slide Show Mode
1. Open `GlucoShield_Capstone_Presentation.pptx`.
2. Press `F5` to begin the slide show (or `Alt + F5` for Presenter View with speaker notes).
3. Use the spacebar or right arrow key to advance.

### Step 4: Execute the Live Demo on Slide 6
1. When Slide 6 appears on screen, say your transition cue: *"Let us now examine our working clinical prototype running live in Streamlit."*
2. Press `Alt + Tab` to switch to your browser displaying `http://localhost:8501`.
3. Walk through:
   - **Scenario 1 (Low Risk):** Select from dropdown -> Click *Assess Readmission Risk* -> Show **27.1% score**, green badge, routine discharge checklist.
   - **Scenario 2 (High Risk):** Select from dropdown -> Click *Assess Readmission Risk* -> Show **72.7% score**, red badge, intensive 5-point transition bundle, and the TreeSHAP local attribution table.
   - **Scenario 3 (Borderline):** Select from dropdown -> Show **48.3% score**, explaining why it is POSITIVE (>= 0.45) but marked BORDERLINE (40–50%).
4. Press `Alt + Tab` to return to PowerPoint and advance to Slide 7.

---

## 4. Fallback Contingency Plan

If internet, browser, or server connection drops during the presentation:
- **Slide 6 contains complete scenario cards** with exact probabilities (27.1%, 72.7%, 48.3%), risk tiers, and discharge protocols.
- You can seamlessly present the three scenarios directly from Slide 6 without interrupting your presentation flow.
- Evaluation plots (`plots/roc_curve.png`, `plots/confusion_matrix.png`, `plots/monitoring_drift.png`) are pre-rendered and embedded in the deck.

---

## 5. Verified Metric Reference

All metrics in the presentation and script are verified against the repository source of truth:
- **Test ROC-AUC:** 0.6465 (Holdout test set, n=13,998)
- **PR-AUC:** 0.158
- **Recall @ 0.45 threshold:** 65.71% (Sensitivity)
- **Specificity @ 0.45:** 54.54%
- **Precision @ 0.45:** 12.48%
- **Confusion Matrix at 0.45:** TP: 826 | FN: 431 | TN: 6,949 | FP: 5,792
- **Simulated Drift PSI:** `number_inpatient` = 0.385 | `age` = 0.298 | `diag_1_group` = 0.260 (Threshold = 0.25)
- **Test Verification:** 17/17 pytest tests PASS | 5/5 Stage 8 system checks PASS

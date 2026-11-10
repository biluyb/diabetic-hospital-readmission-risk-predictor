# GlucoShield CDSS — 10-Minute Capstone Presentation Script & Deck Outline

**FUSE AI-201 Capstone | Module 6: Final Presentation Deliverable**  
**Project:** GlucoShield — Predicting Hospital Readmission Risk in Diabetic Patients to Enhance Discharge Planning  
**Group:** Group 04 | **Cohort:** Youth Empowerment and Employment in AI Program (YEEAP)  
**Presenter:** Bililign Yibgeta Amare (Team Lead)  
**Target Duration:** Exactly 10 Minutes (approx. 1,400 words at 140 words/min)  

---

## 1. Slide Deck Structure & Timing Allocation

| Slide | Section Title | Target Timing | Core Visual to Display |
| :---: | :--- | :---: | :--- |
| **1** | Title & Team Cover Page | 0:00 – 0:45 (45s) | Project title, Group 04 roster, FUSE AI-201 affiliation |
| **2** | Clinical Problem & Industry Need | 0:45 – 1:45 (60s) | CMS HRRP readmission penalty diagram, limitations of LACE index |
| **3** | Dataset & Causal Preprocessing Pipeline | 1:45 – 3:00 (75s) | Deduplication flow (101k to 70k), hospice exclusion, 9 ICD-9 categories |
| **4** | Model Exploration, Baseline & XGBoost Selection | 3:00 – 4:15 (75s) | Model comparison table, ROC curves (`plots/roc_curve.png`) |
| **5** | Clinical Threshold Calibration (0.45 Cutoff) | 4:15 – 5:30 (75s) | Side-by-side Confusion Matrix (`plots/confusion_matrix.png`), False Negative audit |
| **6** | Live Prototype Demonstration (3 Scenarios) | 5:30 – 7:30 (120s) | Streamlit UI walkthrough (Scenario 1 Low, Scenario 2 High, Scenario 3 Borderline) |
| **7** | Real-Time TreeSHAP Explainability | 7:30 – 8:30 (60s) | Local attribution table, top-5 clinical risk drivers |
| **8** | MLOps: Monitoring, Drift Detection & Retraining | 8:30 – 9:15 (45s) | Population Stability Index chart (`plots/monitoring_drift.png`), simulated drift statement |
| **9** | Responsible AI, Ethics & Limitations | 9:15 – 9:45 (30s) | HIPAA de-identification, demographic parity, SDoH limitations |
| **10**| Conclusion, Architecture & Capstone Wrap-up | 9:45 – 10:00 (15s) | Architecture summary diagram, GitHub repository link, Q&A invite |

---

## 2. Verbatim 10-Minute Speaking Script

### [0:00 – 0:45] Slide 1: Introduction & Welcome
> "Good morning, respected mentors, evaluators, and colleagues. My name is Bililign Yibgeta Amare, and on behalf of Group 04 in the Youth Empowerment and Employment in AI Program, I am proud to present our FUSE AI-201 Capstone project: **GlucoShield — an AI-powered Clinical Decision Support System for Predicting 30-Day Hospital Readmission Risk in Diabetic Inpatients**.
> 
> Our team brings together data engineers, machine learning specialists, clinical workflow researchers, and software engineers. Over the past six weeks, we moved from identifying an acute industry challenge in healthcare to engineering an end-to-end, tested, containerized, and explainable decision support prototype. Let us examine the clinical problem we set out to address."

---

### [0:45 – 1:45] Slide 2: Clinical Problem & Industry Context
> "Globally, diabetes mellitus affects more than five hundred million individuals. When diabetic patients are hospitalized for acute complications, managing their care is notoriously complex—it demands balancing glycemic fluctuations, adjusting polypharmacy regimens, and treating multi-system comorbidities like heart failure and kidney disease.
> 
> In healthcare systems worldwide, and specifically in the United States under the CMS Hospital Readmissions Reduction Program, hospitals face millions of dollars in financial penalties if diabetic patients experience unplanned readmissions within 30 days of discharge. 
> 
> Currently, hospital discharge planning teams rely either on clinical intuition or static scoring heuristics like the LACE Index. These tools suffer from three fundamental limitations: they are static, they fail to capture non-linear interactions between medications and lab tests, and they are calculated too late in the discharge workflow to mobilize personalized outpatient support. GlucoShield was designed to solve this gap."

---

### [1:45 – 3:00] Slide 3: Dataset Hygiene & Causal Engineering Pipeline
> "To build a robust model, we leveraged the gold-standard UCI Diabetes 130-US Hospitals dataset, comprising over one hundred and one thousand clinical encounters across a ten-year span from 1999 to 2008.
> 
> Machine learning in medicine requires uncompromising data hygiene. First, we conducted a causal cohort audit: we identified and removed 2,423 encounters where the patient expired in the hospital or transitioned to hospice care. Including deceased patients introduces severe causal leakage, because readmission is logically impossible. 
> 
> Second, to prevent patient-level test leakage, we deduplicated repeated encounters, retaining strictly each unique patient’s first indexed admission, yielding a clean cohort of 69,990 encounters.
> 
> Third, raw ICD-9 diagnosis codes spanned over eight hundred discrete categories. To avoid a catastrophic explosion of sparse one-hot columns, we mapped codes into nine clinically sound organ-system categories—such as Circulatory, Respiratory, and Diabetes with comorbidities. Finally, we engineered clinical composite features: total prior utilization, medication titration intensity, and length-of-stay interaction ratios."

---

### [3:00 – 4:15] Slide 4: Model Exploration & Selection
> "Our clean cohort exhibited severe class imbalance: positive readmissions within 30 days accounted for only 8.98% of cases. An unweighted model succumbs to the majority-class trap—it predicts zero for everyone and claims ninety-one percent accuracy while catching zero high-risk patients.
> 
> To benchmark rigorously, we implemented an experiment tracking pipeline and evaluated four model families on an untouched twenty percent holdout test set of 13,998 patients.
> 
> Our trivial baseline scored 0.50 ROC-AUC. Regularized Logistic Regression established a solid linear lower bound at 0.647 ROC-AUC. Random Forest achieved 0.805 on the training set but dropped to 0.646 on holdout test data, demonstrating tree-memorization of hospital noise. LightGBM and XGBoost both achieved 0.647 ROC-AUC.
> 
> We selected **XGBoost** as our primary operational engine because it provided optimal training stability, robust L1 and L2 regularization (`reg_alpha=0.5`, `reg_lambda=2.0`), resilience to clinical outliers, and native compatibility with high-speed TreeSHAP local explainability."

---

### [4:15 – 5:30] Slide 5: Clinical Threshold Calibration & Safety Error Audit
> "In clinical practice, not all errors are equal. Missing a high-risk patient destined for readmission—a **False Negative**—can result in emergency room return or fatal complications. Conversely, scheduling an extra telephone check-in for a patient who might have done fine—a **False Positive**—is a safe, benign clinical action.
> 
> At the standard default threshold of 0.50, our XGBoost model achieved 51.9% recall. By systematically sweeping decision thresholds, we calibrated the operating cutoff to **0.45**. 
> 
> Operating at 0.45 raised our clinical sensitivity to **65.71%**, successfully intercepting **826 out of 1,257** true readmissions on the untouched holdout test set. 
> 
> We then performed an error audit on the 431 False Negatives. Our audit proved that missed cases had an average of only 0.04 prior inpatient stays and shorter hospitalizations, indicating they appeared stable upon discharge but suffered unrecorded outpatient complications—such as medication copay unaffordability or lack of home care. This insight reinforces why AI must assist, not replace, clinical case managers."

---

### [5:30 – 7:30] Slide 6: Interactive Prototype Demonstration
> *(Presenter screen shares the live Streamlit dashboard)*
> 
> "Let us now examine our working clinical prototype running live in Streamlit.
> 
> Notice first our prominent educational disclaimer banner: the application clearly states it is an educational decision support tool and not an autonomous diagnostic device.
> 
> In the sidebar, we have prepared three demonstration scenarios that mirror real hospital discharge cases:
> 
> **First, Scenario 1 — Our Low-Risk, Negative Case:** 
> Here is a 45-year-old male on his first hospital admission, with normal HbA1c, two days length of stay, and steady oral metformin. When we click 'Run Readmission Risk Stratification', the input validation engine checks the bounds, transforms the data, and our XGBoost model outputs a **27.1% readmission risk**. Because this is well below our 0.45 cutoff, the dashboard renders a green **LOW RISK** badge and populates a routine discharge checklist: standard diet education and standard 14-to-30-day primary care follow-up.
> 
> **Next, Scenario 2 — Our High-Risk, Positive Case:** 
> This is a 75-year-old female with congestive heart failure comorbidity, three prior inpatient admissions, and insulin dosage up-titrated during a 6-day stay. Clicking submit produces a **72.7% readmission risk**. The system flags this as **HIGH RISK — POSITIVE**, triggering our intensive transition bundle: scheduling a home health nurse within 48 hours, mandatory clinical pharmacist medication reconciliation, and an expedited 7-day clinic appointment.
> 
> **Finally, Scenario 3 — Our Borderline Case:** 
> A 65-year-old male with ischemic heart disease and 1 prior ER visit, whose probability lands at **48.3%**—right in the borderline region adjacent to our 0.45 cutoff. The system classifies this as **BORDERLINE / MODERATE RISK**, prompting the clinician to conduct a medication review before finalizing discharge."

---

### [7:30 – 8:30] Slide 7: Real-Time TreeSHAP Feature Attribution
> "Clinicians will not adopt a black box. In the right-hand panel of our dashboard, you can see our integrated **TreeSHAP explainability engine**. 
> 
> Within twelve milliseconds, TreeSHAP decomposes the mathematical log-odds contribution of every clinical attribute. For our high-risk patient, it explicitly shows that prior inpatient visits and insulin up-titration contributed the highest positive push toward readmission risk, while her controlled blood pressure partially offset risk. 
> 
> This feature-level transparency enables hospitalists to immediately validate why a patient was flagged and tailor interventions directly to the underlying drivers."

---

### [8:30 – 9:15] Slide 8: MLOps — Monitoring, Drift Detection & Retraining
> "Deploying a model is only day one. In Module 6, we implemented an automated monitoring and data drift module in `monitoring/`.
> 
> Our pipeline continuously calculates the **Population Stability Index (PSI)** and **Kolmogorov-Smirnov statistics** across clinical features. 
> 
> To demonstrate drift detection honestly, we simulated two production cohorts: Month 1 representing stable operations, where PSI remained below 0.01; and Month 2 simulating a realistic winter respiratory surge and elderly demographic shift. 
> 
> As displayed in our drift chart, the system immediately detected high drift on inpatient utilization and age ($\text{PSI} \ge 0.25$), triggering an automated retraining alert. This ensures clinical safety over time."

---

### [9:15 – 9:45] Slide 9: Responsible AI, Security & Governance
> "From an ethics standpoint, GlucoShield complies strictly with HIPAA Safe Harbor standards. No protected health information is stored on disk or exposed via API. 
> 
> Our automated test suite includes seventeen unit and integration tests covering preprocessing, model loading, boundary enforcement, and FastAPI endpoints—all passing with 100% reliability.
> 
> We also audited demographic fairness across sex and racial categories to ensure our 0.45 threshold does not induce disparate false-negative rates in underrepresented groups."

---

### [9:45 – 10:00] Slide 10: Conclusion & Submission Wrap-Up
> "In conclusion, GlucoShield bridges advanced machine learning and practical bedside clinical decision support. We have delivered a working Streamlit dashboard, a containerized Docker configuration, an optional FastAPI microservice, reproducible experiment logs, and a complete nine-document governance suite.
> 
> On behalf of Group 04, thank you for your mentorship and guidance throughout FUSE AI-201. We welcome your feedback and questions."

---

## 3. Demonstration Walkthrough Cue Sheet

When recording the video demonstration, follow this step-by-step checklist:

1. **Terminal Setup:**
   - Have terminal open: `streamlit run app.py` (Dashboard running on `http://localhost:8501`).
   - Have second terminal ready showing passing test suite: `python -m pytest tests/ -v` (17 passed).
2. **Dashboard Overview (0:30):**
   - Point to the Header: *GlucoShield: Diabetic Inpatient Readmission CDSS*.
   - Point to the blue **Educational Prototype Notice** disclaimer banner.
3. **Scenario 1 Walkthrough (1:00):**
   - Select `Scenario 1: Low-Risk / Negative` from sidebar dropdown.
   - Click *Run Readmission Risk Stratification*.
   - Highlight the **27.1% Risk Score**, green **LOW RISK** badge, and standard discharge checklist.
4. **Scenario 2 Walkthrough (1:00):**
   - Select `Scenario 2: High-Risk / Positive` from sidebar.
   - Click *Run Readmission Risk Stratification*.
   - Highlight the **72.7% Risk Score**, red **HIGH RISK** badge, and the intensive 5-point checklist.
   - Show the **TreeSHAP local attribution table** on the right side.
5. **Scenario 3 Walkthrough (0:45):**
   - Select `Scenario 3: Borderline Risk (~0.45 Cutoff)`.
   - Show how the score lands at **48.3%**, triggering a moderate/borderline alert.
6. **Tabs 2 & 3 Quick Tour (0:45):**
   - Click Tab 2 (*System Testing Sandbox*): show live edge-case execution.
   - Click Tab 3 (*Model Performance & Evaluation*): show ROC curves and confusion matrix plots.
7. **Terminal / Drift Report Cue (0:30):**
   - Show `plots/monitoring_drift.png` and `documentation/drift_report.md` proving MLOps drift governance.


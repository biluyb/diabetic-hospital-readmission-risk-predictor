"""
Master Runner for GlucoShield CDSS: End-to-End AI Development & MLOps Pipeline.
FUSE AI-201 Capstone (Group 04).
Executes data preparation, exploratory analysis, modeling, evaluation, testing,
experiment tracking, and production drift monitoring.
"""

import os
import sys

def main():
    print("======================================================================")
    print("🚀 GLUCOSHIELD CDSS: FULL END-TO-END CAPSTONE PIPELINE (MODULES 5 & 6)")
    print("   Project: Predicting Hospital Readmission Risk in Diabetic Patients")
    print("   Group: 04 | YEEAP Capstone")
    print("======================================================================\n")

    # Step 1: Data Download & Verification
    print(">>> STAGE 1: Verifying / Downloading Dataset...")
    import download_data

    # Step 2: Data Pipeline & Split
    print("\n>>> STAGE 2: Cleaning, Deduplicating, & Preprocessing...")
    from src.data_pipeline import prepare_train_test_data
    data_dict = prepare_train_test_data()

    # Step 3: Exploratory Data Analysis & Plots
    print("\n>>> STAGE 3: Running Exploratory Data Analysis & Chart Generation...")
    from src.eda import run_eda
    eda_results = run_eda()

    # Step 4: Baseline & Candidate Models Training
    print("\n>>> STAGE 4: Training Baseline & Candidate Models...")
    from src.models import train_and_evaluate_models
    model_results = train_and_evaluate_models()

    # Step 5: Test Evaluation, ROC curves, Error Audit
    print("\n>>> STAGE 5: Comprehensive Model Evaluation & Error Audit...")
    from src.evaluate import run_evaluation
    eval_results = run_evaluation()

    # Step 6: System Robustness & Edge-Case Testing
    print("\n>>> STAGE 6: System Robustness & Edge-Case Testing...")
    from src.test_suite import run_system_tests
    test_results = run_system_tests()

    # Step 7: Reproducible Experiment Tracking
    print("\n>>> STAGE 7: Logging Benchmark Runs to Experiment Tracker...")
    from src.experiment_tracker import populate_default_experiments
    populate_default_experiments()

    # Step 8: Monitoring & Model Drift Evaluation
    print("\n>>> STAGE 8: Running Production Monitoring & Drift Detection...")
    from monitoring.run_monitoring import main as run_monitoring
    run_monitoring()

    print("\n======================================================================")
    print("✅ All Module 5 & Module 6 Pipeline Stages Successfully Executed!")
    print("   • Trained models saved in:      models/")
    print("   • Evaluation charts saved in:  plots/")
    print("   • Experiment logs saved in:    evaluation/")
    print("   • Drift report saved in:       documentation/drift_report.md")
    print("   • Automated test suite in:     tests/")
    print("   • Launch Interactive UI:       streamlit run app.py")
    print("   • Launch REST API Service:     uvicorn src.api:api_app --port 8000")
    print("======================================================================")

if __name__ == '__main__':
    main()

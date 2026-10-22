"""
Master Runner for FUSE AI-201 Module 5: End-to-End AI Project Implementation.
Executes all stages from data preparation to model improvement, evaluation, and system testing.
"""

import os
import sys

def main():
    print("======================================================================")
    print("🚀 FUSE AI-201 MODULE 5: AI PROJECT IMPLEMENTATION PIPELINE")
    print("   Project: Predicting Hospital Readmission Risk in Diabetic Patients")
    print("   Group: 04")
    print("======================================================================\n")

    # Step 1: Data Download & Verification
    print(">>> STAGE 3.1: Verifying / Downloading Dataset...")
    import download_data

    # Step 2: Data Pipeline & Split
    print("\n>>> STAGE 3.2 - 3.5: Cleaning, Deduplicating, & Preprocessing...")
    from src.data_pipeline import prepare_train_test_data
    data_dict = prepare_train_test_data()

    # Step 3: Exploratory Data Analysis & Plots
    print("\n>>> STAGE 4: Running Exploratory Data Analysis & Chart Generation...")
    from src.eda import run_eda
    eda_results = run_eda()

    # Step 4: Baseline & Candidate Models Training
    print("\n>>> STAGES 5 & 6: Training Baseline & Tuned Candidate Models...")
    from src.models import train_and_evaluate_models
    model_results = train_and_evaluate_models()

    # Step 5: Test Evaluation, ROC curves, Error Audit
    print("\n>>> STAGE 7: Comprehensive Model Evaluation & Error Audit...")
    from src.evaluate import run_evaluation
    eval_results = run_evaluation()

    # Step 6: Stage 8 System Robustness Tests
    print("\n>>> STAGE 8: System Robustness & Edge-Case Testing...")
    from src.test_suite import run_system_tests
    test_results = run_system_tests()

    print("\n======================================================================")
    print("✅ All Module 5 Pipeline Stages Successfully Completed!")
    print("   Trained models saved in: models/")
    print("   Evaluation charts saved in: plots/")
    print("   To launch the interactive prototype, run: streamlit run app.py")
    print("======================================================================")

if __name__ == '__main__':
    main()

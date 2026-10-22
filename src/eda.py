"""
Exploratory Data Analysis (EDA) Module for Diabetes Readmission CDSS.
Module 5: Stage 4 (Exploratory Data Analysis)
Generates descriptive statistics, distribution comparisons, correlation analyses,
and publication-quality visualizations saved to plots/.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from src.data_pipeline import clean_and_prepare_data

def run_eda(csv_path="data/diabetic_data.csv", output_dir="plots"):
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

    print("--> Loading cleaned dataset for EDA...")
    df = clean_and_prepare_data(csv_path=csv_path, verbose=False)
    
    # 1. Descriptive statistics for numeric features
    numeric_cols = [
        'time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications',
        'number_outpatient', 'number_emergency', 'number_inpatient', 'number_diagnoses',
        'total_prior_visits', 'procedure_intensity', 'meds_per_day', 'num_dosage_changes'
    ]
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    desc_stats = df[numeric_cols].describe().T[['mean', 'std', 'min', '50%', 'max']]
    desc_stats.rename(columns={'50%': 'median'}, inplace=True)
    print("\n--- Descriptive Statistics (Key Numeric Variables) ---")
    print(desc_stats.to_string())

    # 2. Target Distribution Visualization
    fig, ax = plt.subplots(figsize=(6, 5))
    target_counts = df['target'].value_counts()
    target_pcts = df['target'].value_counts(normalize=True) * 100
    bars = ax.bar(['No / >30 Days (0)', 'Readmitted <30 Days (1)'], target_counts.values, color=['#2b5c8f', '#d9534f'], width=0.55)
    for bar, pct in zip(bars, target_pcts):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1000, f'{yval:,} ({pct:.1f}%)', ha='center', va='bottom', fontweight='bold')
    ax.set_title('Target Class Distribution (30-Day Readmission)', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Number of Patients')
    ax.set_ylim(0, max(target_counts.values) * 1.15)
    plt.tight_layout()
    fig_path1 = os.path.join(output_dir, 'target_distribution.png')
    plt.savefig(fig_path1, dpi=300)
    plt.close()
    print(f"Saved: {fig_path1}")

    # 3. Prior Inpatient Visits vs Readmission Rate
    fig, ax = plt.subplots(figsize=(8, 5))
    # Cap prior visits at 5+ for clean visualization
    df['inpatient_binned'] = df['number_inpatient'].apply(lambda x: str(x) if x < 4 else '4+')
    order = ['0', '1', '2', '3', '4+']
    readmit_rate_by_inpatient = df.groupby('inpatient_binned')['target'].mean().reindex(order) * 100
    counts = df['inpatient_binned'].value_counts().reindex(order)

    ax.bar(order, readmit_rate_by_inpatient.values, color='#e06666', width=0.55, edgecolor='#990000', linewidth=1)
    for i, (rate, count) in enumerate(zip(readmit_rate_by_inpatient, counts)):
        ax.text(i, rate + 0.8, f'{rate:.1f}%\n(n={count:,})', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_title('30-Day Readmission Rate by Prior Inpatient Admissions', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Number of Prior Inpatient Admissions')
    ax.set_ylabel('30-Day Readmission Rate (%)')
    ax.set_ylim(0, max(readmit_rate_by_inpatient) * 1.25)
    plt.tight_layout()
    fig_path2 = os.path.join(output_dir, 'prior_inpatient_vs_readmission.png')
    plt.savefig(fig_path2, dpi=300)
    plt.close()
    print(f"Saved: {fig_path2}")

    # 4. Readmission Rate by Primary Diagnosis Category
    fig, ax = plt.subplots(figsize=(10, 5))
    diag_summary = df.groupby('diag_1_group')['target'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    diag_summary['rate_pct'] = diag_summary['mean'] * 100
    bars = ax.barh(diag_summary.index, diag_summary['rate_pct'], color='#3d85c6', edgecolor='#0b5394', height=0.6)
    for bar, count in zip(bars, diag_summary['count']):
        w = bar.get_width()
        ax.text(w + 0.3, bar.get_y() + bar.get_height()/2.0, f'{w:.1f}% (n={count:,})', ha='left', va='center', fontsize=9)
    ax.set_title('30-Day Readmission Rate by Primary Diagnosis Category (ICD-9)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Readmission Rate (%)')
    ax.set_xlim(0, max(diag_summary['rate_pct']) + 4)
    plt.tight_layout()
    fig_path3 = os.path.join(output_dir, 'primary_diagnosis_readmission.png')
    plt.savefig(fig_path3, dpi=300)
    plt.close()
    print(f"Saved: {fig_path3}")

    # 5. Length of Stay (Time in Hospital) Distribution
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(data=df, x='time_in_hospital', hue='target', palette=['#2b5c8f', '#d9534f'], ax=ax)
    ax.set_title('Length of Stay Distribution Stratified by 30-Day Readmission', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Time in Hospital (Days)')
    ax.set_ylabel('Number of Patients')
    ax.legend(['No / >30 Days', 'Readmitted <30 Days'], title='Readmission Status')
    plt.tight_layout()
    fig_path4 = os.path.join(output_dir, 'length_of_stay_distribution.png')
    plt.savefig(fig_path4, dpi=300)
    plt.close()
    print(f"Saved: {fig_path4}")

    # 6. Correlation Matrix Heatmap
    corr_cols = [
        'time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications',
        'number_emergency', 'number_inpatient', 'number_diagnoses', 'total_prior_visits', 'target'
    ]
    corr = df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-0.15, vmax=0.6, square=True, ax=ax, cbar_kws={'shrink': 0.8})
    ax.set_title('Correlation Matrix of Clinical Variables and Readmission Target', fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    fig_path5 = os.path.join(output_dir, 'correlation_heatmap.png')
    plt.savefig(fig_path5, dpi=300)
    plt.close()
    print(f"Saved: {fig_path5}")

    return {
        'desc_stats': desc_stats,
        'target_dist': target_counts.to_dict(),
        'diag_summary': diag_summary.to_dict(orient='index')
    }

if __name__ == "__main__":
    results = run_eda()
    print("\nEDA completed successfully and charts generated in plots/.")

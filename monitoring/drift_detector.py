"""
Data Drift Detection Engine for GlucoShield CDSS.
Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) test statistics
to detect distributional shifts between baseline reference data and incoming patient batches.
"""

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

def calculate_psi_numeric(reference_vals: np.ndarray, current_vals: np.ndarray, num_bins: int = 10) -> float:
    """
    Calculates Population Stability Index (PSI) for continuous numerical features.
    PSI < 0.10: No significant drift
    0.10 <= PSI < 0.25: Moderate drift, requires monitoring
    PSI >= 0.25: Significant drift, triggers retraining review
    """
    ref = reference_vals[~np.isnan(reference_vals)]
    curr = current_vals[~np.isnan(current_vals)]
    
    if len(ref) == 0 or len(curr) == 0:
        return 0.0

    # Quantile bin edges based on reference distribution
    quantiles = np.linspace(0, 1, num_bins + 1)
    bin_edges = np.percentile(ref, quantiles * 100)
    bin_edges = np.unique(bin_edges) # remove duplicate edges
    
    if len(bin_edges) <= 1:
        return 0.0
        
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    ref_counts, _ = np.histogram(ref, bins=bin_edges)
    curr_counts, _ = np.histogram(curr, bins=bin_edges)

    # Convert to proportions with small epsilon to prevent division by zero
    ref_pct = (ref_counts + 1e-4) / (len(ref) + 1e-4 * len(ref_counts))
    curr_pct = (curr_counts + 1e-4) / (len(curr) + 1e-4 * len(curr_counts))

    psi = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))
    return float(max(0.0, psi))

def calculate_psi_categorical(reference_series: pd.Series, current_series: pd.Series) -> float:
    """
    Calculates PSI for categorical features across shared categories.
    """
    all_cats = list(set(reference_series.dropna().unique()).union(set(current_series.dropna().unique())))
    if not all_cats:
        return 0.0

    ref_counts = reference_series.value_counts(normalize=True).to_dict()
    curr_counts = current_series.value_counts(normalize=True).to_dict()

    psi = 0.0
    for cat in all_cats:
        ref_p = ref_counts.get(cat, 1e-4)
        curr_p = curr_counts.get(cat, 1e-4)
        psi += (curr_p - ref_p) * np.log(curr_p / ref_p)
    return float(max(0.0, psi))

def perform_drift_analysis(df_reference: pd.DataFrame, df_current: pd.DataFrame, 
                           numeric_cols: list, categorical_cols: list) -> dict:
    """
    Performs comprehensive feature drift analysis between reference and incoming batch.
    """
    results = {}
    
    for col in numeric_cols:
        if col in df_reference.columns and col in df_current.columns:
            ref_vals = pd.to_numeric(df_reference[col], errors='coerce').dropna().values
            curr_vals = pd.to_numeric(df_current[col], errors='coerce').dropna().values
            
            if len(ref_vals) > 5 and len(curr_vals) > 5:
                psi_val = calculate_psi_numeric(ref_vals, curr_vals)
                ks_stat, ks_p = ks_2samp(ref_vals, curr_vals)
                
                # Check missing rate
                ref_missing = df_reference[col].isna().mean()
                curr_missing = df_current[col].isna().mean()

                status = "NO_DRIFT"
                if psi_val >= 0.25:
                    status = "HIGH_DRIFT"
                elif psi_val >= 0.10:
                    status = "MODERATE_DRIFT"

                results[col] = {
                    'type': 'numeric',
                    'psi': round(psi_val, 4),
                    'ks_statistic': round(float(ks_stat), 4),
                    'ks_pvalue': round(float(ks_p), 6),
                    'ref_mean': round(float(np.mean(ref_vals)), 2),
                    'curr_mean': round(float(np.mean(curr_vals)), 2),
                    'ref_missing_pct': round(ref_missing * 100, 2),
                    'curr_missing_pct': round(curr_missing * 100, 2),
                    'drift_status': status
                }

    for col in categorical_cols:
        if col in df_reference.columns and col in df_current.columns:
            ref_s = df_reference[col].astype(str)
            curr_s = df_current[col].astype(str)
            psi_val = calculate_psi_categorical(ref_s, curr_s)

            status = "NO_DRIFT"
            if psi_val >= 0.25:
                status = "HIGH_DRIFT"
            elif psi_val >= 0.10:
                status = "MODERATE_DRIFT"

            results[col] = {
                'type': 'categorical',
                'psi': round(psi_val, 4),
                'ks_statistic': None,
                'ks_pvalue': None,
                'ref_mean': None,
                'curr_mean': None,
                'ref_missing_pct': round(df_reference[col].isna().mean() * 100, 2),
                'curr_missing_pct': round(df_current[col].isna().mean() * 100, 2),
                'drift_status': status
            }

    return results


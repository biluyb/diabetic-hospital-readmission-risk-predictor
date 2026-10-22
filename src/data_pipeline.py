"""
Data Processing and Feature Engineering Pipeline for Diabetes Readmission CDSS.
Module 5: Stage 3 (Collect & Prepare Data) & Stage 4 (EDA Data Preparation)
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib

def map_icd9_to_category(code):
    """
    Standard clinical mapping of ICD-9 diagnosis codes into high-level disease categories:
    - Circulatory: 390-459, 785
    - Respiratory: 460-519, 786
    - Digestive: 520-579, 787
    - Diabetes: 250.xx
    - Injury/Poisoning: 800-999
    - Musculoskeletal: 710-739
    - Genitourinary: 580-629, 788
    - Neoplasms: 140-239
    - Other / Missing
    """
    if pd.isna(code) or code == '?' or code == '':
        return 'Missing/Unknown'
    code = str(code).strip()
    if code.startswith('V') or code.startswith('E'):
        return 'Other'
    try:
        val = float(code)
    except ValueError:
        return 'Other'

    if (390 <= val <= 459) or val == 785:
        return 'Circulatory'
    elif (460 <= val <= 519) or val == 786:
        return 'Respiratory'
    elif (520 <= val <= 579) or val == 787:
        return 'Digestive'
    elif 250 <= val < 251:
        return 'Diabetes'
    elif (800 <= val <= 999):
        return 'Injury'
    elif (710 <= val <= 739):
        return 'Musculoskeletal'
    elif (580 <= val <= 629) or val == 788:
        return 'Genitourinary'
    elif (140 <= val <= 239):
        return 'Neoplasms'
    else:
        return 'Other'

def clean_and_prepare_data(csv_path="data/diabetic_data.csv", verbose=True):
    """
    Cleans raw diabetic encounter data:
    1. Removes expired/hospice patients (readmission logically impossible).
    2. Deduplicates multiple encounters per patient (retains first admission).
    3. Handles '?' as missing.
    4. Drops features with extreme sparsity (>50% missing: weight, payer_code).
    5. Maps ICD-9 diagnoses into high-level categories.
    6. Constructs clinical composite features.
    7. Formulates binary target: 1 if readmitted <30 days, else 0.
    """
    if verbose:
        print("--> Loading raw data from:", csv_path)
    df = pd.read_csv(csv_path)
    initial_shape = df.shape
    if verbose:
        print(f"    Initial encounters: {initial_shape[0]}, features: {initial_shape[1]}")

    # Step 1: Remove hospice / expired patients
    # discharge_disposition_id:
    # 11: Expired, 13: Hospice/home, 14: Hospice/medical facility, 19, 20, 21: Expired
    expired_hospice_ids = [11, 13, 14, 19, 20, 21]
    df = df[~df['discharge_disposition_id'].isin(expired_hospice_ids)].copy()
    after_expired = df.shape[0]
    if verbose:
        print(f"    After excluding expired/hospice: {after_expired} (removed {initial_shape[0] - after_expired})")

    # Step 2: Deduplicate to retain first admission per unique patient
    df = df.drop_duplicates(subset=['patient_nbr'], keep='first').copy()
    after_dedup = df.shape[0]
    if verbose:
        print(f"    After patient deduplication (first encounter only): {after_dedup} (removed {after_expired - after_dedup})")

    # Step 3: Replace '?' with NaN
    df = df.replace('?', np.nan)

    # Step 4: Drop high missingness / non-clinical identifier columns
    cols_to_drop = ['weight', 'payer_code', 'encounter_id', 'patient_nbr']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Step 5: Clean 'gender' - remove rare 'Unknown/Invalid' records (only ~3 records)
    if 'gender' in df.columns:
        df = df[df['gender'].isin(['Male', 'Female'])].copy()

    # Step 6: Define binary target variable: 1 if <30, 0 if >30 or NO
    df['target'] = (df['readmitted'] == '<30').astype(int)
    target_dist = df['target'].value_counts()
    target_pct = df['target'].value_counts(normalize=True) * 100
    if verbose:
        print(f"    Target distribution (<30 readmitted=1 vs 0):")
        print(f"      0 (No / >30 days): {target_dist.get(0, 0)} ({target_pct.get(0, 0):.2f}%)")
        print(f"      1 (<30 days):      {target_dist.get(1, 0)} ({target_pct.get(1, 0):.2f}%)")

    # Step 7: Map ICD-9 codes to categories
    for diag_col in ['diag_1', 'diag_2', 'diag_3']:
        if diag_col in df.columns:
            df[f'{diag_col}_group'] = df[diag_col].apply(map_icd9_to_category)
            df.drop(columns=[diag_col], inplace=True)

    # Step 8: Group medical_specialty (many rare categories, high missingness)
    if 'medical_specialty' in df.columns:
        top_specialties = df['medical_specialty'].value_counts().nlargest(9).index.tolist()
        df['medical_specialty'] = df['medical_specialty'].apply(
            lambda x: x if pd.notna(x) and x in top_specialties else ('Missing' if pd.isna(x) else 'Other_Specialty')
        )

    # Step 9: Feature Engineering
    # Total prior hospital visits
    df['total_prior_visits'] = df['number_outpatient'] + df['number_emergency'] + df['number_inpatient']
    
    # Inpatient history indicator (clinically significant)
    df['has_prior_inpatient'] = (df['number_inpatient'] > 0).astype(int)
    df['has_prior_emergency'] = (df['number_emergency'] > 0).astype(int)

    # Severity index: interaction between length of stay and procedures
    df['procedure_intensity'] = (df['num_lab_procedures'] + df['num_procedures']) / (df['time_in_hospital'] + 1e-5)

    # Medication count ratio
    df['meds_per_day'] = df['num_medications'] / (df['time_in_hospital'] + 1e-5)

    # Medication changes count
    med_cols = [
        'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
        'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
        'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide',
        'examide', 'citoglipton', 'insulin', 'glyburide-metformin', 'glipizide-metformin',
        'glimepiride-pioglitazone', 'metformin-rosiglitazone', 'metformin-pioglitazone'
    ]
    existing_med_cols = [c for c in med_cols if c in df.columns]
    
    # Calculate count of active medications and changes
    df['num_active_diabetes_meds'] = df[existing_med_cols].apply(
        lambda row: sum(val in ['Steady', 'Up', 'Down'] for val in row), axis=1
    )
    df['num_dosage_changes'] = df[existing_med_cols].apply(
        lambda row: sum(val in ['Up', 'Down'] for val in row), axis=1
    )

    # Simplify 23 med columns to reduce massive one-hot explosion:
    # Keep the most prevalent key medications (insulin, metformin, glipizide, glyburide, pioglitazone, rosiglitazone)
    top_meds = ['insulin', 'metformin', 'glipizide', 'glyburide', 'pioglitazone', 'rosiglitazone']
    other_meds = [c for c in existing_med_cols if c not in top_meds]
    df.drop(columns=other_meds, inplace=True)

    # Standardize 'age' brackets to numeric midpoints for continuous analysis if desired, but retain bracket string for categorical
    age_map = {
        '[0-10)': 5, '[10-20)': 15, '[20-30)': 25, '[30-40)': 35, '[40-50)': 45,
        '[50-60)': 55, '[60-70)': 65, '[70-80)': 75, '[80-90)': 85, '[90-100)': 95
    }
    df['age_num'] = df['age'].map(age_map)

    # Drop raw readmitted column as we have 'target'
    df.drop(columns=['readmitted'], inplace=True)

    return df

def get_preprocessor(categorical_features, numeric_features):
    """
    Constructs a ColumnTransformer that imputes and encodes categories,
    and imputes and scales numeric features.
    """
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    return preprocessor

def prepare_train_test_data(csv_path="data/diabetic_data.csv", test_size=0.20, random_state=42):
    """
    Prepares train and test splits with stratification to preserve class balance,
    and fits the preprocessing pipeline.
    """
    df = clean_and_prepare_data(csv_path=csv_path, verbose=True)

    # Separate target
    y = df['target'].values
    X = df.drop(columns=['target'])

    # Identify numeric and categorical columns
    numeric_features = [
        'time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications',
        'number_outpatient', 'number_emergency', 'number_inpatient', 'number_diagnoses',
        'total_prior_visits', 'procedure_intensity', 'meds_per_day',
        'num_active_diabetes_meds', 'num_dosage_changes', 'age_num'
    ]
    numeric_features = [col for col in numeric_features if col in X.columns]

    categorical_features = [
        'race', 'gender', 'age', 'admission_type_id', 'discharge_disposition_id',
        'admission_source_id', 'medical_specialty', 'diag_1_group', 'diag_2_group',
        'diag_3_group', 'max_glu_serum', 'A1Cresult', 'metformin', 'glipizide',
        'glyburide', 'pioglitazone', 'rosiglitazone', 'insulin', 'change', 'diabetesMed'
    ]
    # Ensure IDs are treated as strings/categories
    for col in ['admission_type_id', 'discharge_disposition_id', 'admission_source_id']:
        if col in X.columns:
            X[col] = X[col].astype(str)

    categorical_features = [col for col in categorical_features if col in X.columns]

    print(f"--> Splitting data: {100*(1-test_size):.0f}% train, {100*test_size:.0f}% test (Stratified, random_state={random_state})")
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    preprocessor = get_preprocessor(categorical_features, numeric_features)
    preprocessor.fit(X_train_raw)

    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_feature_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    feature_names = numeric_features + cat_feature_names

    X_train_trans = preprocessor.transform(X_train_raw)
    X_test_trans = preprocessor.transform(X_test_raw)

    print(f"    Transformed X_train shape: {X_train_trans.shape}, X_test shape: {X_test_trans.shape}")
    print(f"    Total engineered feature columns: {len(feature_names)}")

    # Save preprocessor artifact
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.joblib')
    joblib.dump(feature_names, 'models/feature_names.joblib')
    joblib.dump({
        'numeric_features': numeric_features,
        'categorical_features': categorical_features
    }, 'models/feature_metadata.joblib')

    return {
        'df_clean': df,
        'X_train_raw': X_train_raw,
        'X_test_raw': X_test_raw,
        'X_train': X_train_trans,
        'X_test': X_test_trans,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': feature_names,
        'preprocessor': preprocessor,
        'numeric_features': numeric_features,
        'categorical_features': categorical_features
    }

if __name__ == "__main__":
    data_dict = prepare_train_test_data()
    print("Data preparation complete and artifacts saved.")

"""
Unit tests for data preprocessing and ICD-9 mapping logic.
"""

import pytest
import numpy as np
import pandas as pd
from src.data_pipeline import map_icd9_to_category

def test_map_icd9_categories():
    assert map_icd9_to_category('250.00') == 'Diabetes'
    assert map_icd9_to_category('250.6') == 'Diabetes'
    assert map_icd9_to_category('428') == 'Circulatory'
    assert map_icd9_to_category('410.1') == 'Circulatory'
    assert map_icd9_to_category('486') == 'Respiratory'
    assert map_icd9_to_category('530.81') == 'Digestive'
    assert map_icd9_to_category('585') == 'Genitourinary'
    assert map_icd9_to_category('715') == 'Musculoskeletal'
    assert map_icd9_to_category('820') == 'Injury'
    assert map_icd9_to_category('174') == 'Neoplasms'

def test_map_icd9_special_codes():
    assert map_icd9_to_category('V45') == 'Other'
    assert map_icd9_to_category('E880') == 'Other'
    assert map_icd9_to_category('?') == 'Missing/Unknown'
    assert map_icd9_to_category(None) == 'Missing/Unknown'
    assert map_icd9_to_category('') == 'Missing/Unknown'


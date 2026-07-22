"""Single source of truth for model feature and exclusion lists."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


LABEL_COLUMNS = [
    "waist_cm", "bp_systolic_mean", "bp_diastolic_mean", "triglycerides",
    "hdl", "hba1c", "waist_flag", "bp_flag", "triglycerides_flag",
    "hdl_flag", "hba1c_flag", "metabolic_component_count_known",
    "metabolic_component_known_n", "metabolic_syndrome_strict",
    "metabolic_syndrome", "label_basis",
]

RF_FEATURES = [
    "energy_kcal", "protein_g", "carb_g", "sugar_g", "fat_total_g",
    "fat_sat_g", "fiber_g", "sodium_mg", "potassium_mg",
    "moderate_rec_min_week", "sedentary_min",
]

RF_OPTIONAL_FEATURES = [
    "sleep_hours", "vigorous_rec_min_week", "smoked_100_cigs",
    "avg_drinks_per_day",
]

KMEANS_FEATURES = [
    "age", "sex", "race_eth", "education", "income_poverty_ratio",
    "food_security_adult",
]

NEVER_FEATURES = [
    "uid", "SEQN", "cycle", "weight_mec_2yr", "weight_int_2yr",
    "weight_fasting_2yr", "svy_psu", "svy_stratum", "bmi", "ldl",
    "total_chol",
]


def assert_columns_exist(df: pd.DataFrame, columns: Sequence[str], name: str) -> None:
    missing = sorted(set(columns).difference(df.columns))
    if missing:
        raise KeyError(f"{name} contains columns missing from the dataset: {missing}")


def assert_no_leakage(columns: Sequence[str], matrix_name: str = "X") -> None:
    forbidden = sorted(set(columns).intersection(LABEL_COLUMNS + NEVER_FEATURES))
    if forbidden:
        raise ValueError(f"{matrix_name} contains leakage/forbidden columns: {forbidden}")


def build_feature_matrix(df: pd.DataFrame, columns: Sequence[str], name: str = "X") -> pd.DataFrame:
    assert_columns_exist(df, columns, name)
    assert_no_leakage(columns, name)
    return df.loc[:, list(columns)].copy()

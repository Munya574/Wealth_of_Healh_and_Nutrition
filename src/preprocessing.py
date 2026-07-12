"""Cleaning, column decoding, and missing-value handling for NHANES data.

NHANES uses coded categorical values (e.g., ``1 = Male``, ``7 = Refused``,
``9 = Don't know``) and sentinel codes for missing/refused responses. This module
turns the raw merged frame (from :mod:`src.data_loading`) into a curated,
analysis-ready table with readable column names.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

# Identifier columns carried through unchanged (see src.data_loading).
ID_COLS = ("uid", "SEQN", "cycle")

# Curated variable map: raw NHANES column -> friendly name. Only these columns
# are kept in the analysis table. All are verified present across the 2013-2018
# cycles (H/I/J). Sleep is handled separately because its code changed by cycle.
VARIABLE_MAP: dict[str, str] = {
    # --- Demographics (DEMO) ---
    "RIAGENDR": "sex",                    # 1=Male, 2=Female
    "RIDAGEYR": "age",                    # years
    "RIDRETH3": "race_eth",               # race/Hispanic origin
    "DMDEDUC2": "education",              # adult education level
    "INDFMPIR": "income_poverty_ratio",  # ratio of family income to poverty
    # --- Examination: body measures (BMX) ---
    "BMXBMI": "bmi",
    "BMXWAIST": "waist_cm",
    # --- Examination: blood pressure (BPX) ---
    "BPXSY1": "bp_systolic",
    "BPXDI1": "bp_diastolic",
    # --- Laboratory ---
    "LBXGH": "hba1c",                     # GHB: glycohemoglobin %
    "LBDHDD": "hdl",                      # HDL cholesterol mg/dL
    "LBXTC": "total_chol",                # total cholesterol mg/dL
    "LBXTR": "triglycerides",             # TRIGLY (fasting subsample only)
    "LBDLDL": "ldl",                      # LDL (fasting subsample only)
    # --- Dietary, day 1 (DR1TOT) ---
    "DR1TKCAL": "energy_kcal",
    "DR1TPROT": "protein_g",
    "DR1TCARB": "carb_g",
    "DR1TSUGR": "sugar_g",
    "DR1TFIBE": "fiber_g",
    "DR1TTFAT": "fat_total_g",
    "DR1TSFAT": "fat_sat_g",
    "DR1TSODI": "sodium_mg",
    # --- Questionnaire: activity & behavior ---
    "PAQ650": "vigorous_rec_activity",    # yes/no
    "PAQ665": "moderate_rec_activity",    # yes/no
    "PAD680": "sedentary_min",            # minutes/day sedentary
    "SMQ020": "smoked_100_cigs",          # yes/no
    "ALQ130": "avg_drinks_per_day",
    "FSDAD": "food_security_adult",       # household food-security category
    # --- Survey design (keep for optional weighted analysis) ---
    "WTMEC2YR": "weight_mec_2yr",
    "WTINT2YR": "weight_int_2yr",
    "SDMVPSU": "svy_psu",
    "SDMVSTRA": "svy_stratum",
}

# Sleep-hours source columns, newest first. The variable code changed between
# cycles: SLD010H (2013-2014) was renamed SLD012 (2015-2018). We coalesce them.
SLEEP_SOURCES = ("SLD012", "SLD010H")

# Per-variable sentinel codes (Refused / Don't know) to convert to NaN. Keyed by
# the *friendly* name, applied after renaming. Only listed where the code is known
# from the NHANES documentation, to avoid nuking legitimate values.
SENTINEL_CODES: dict[str, list] = {
    "education": [7, 9],
    "vigorous_rec_activity": [7, 9],
    "moderate_rec_activity": [7, 9],
    "smoked_100_cigs": [7, 9],
    "avg_drinks_per_day": [777, 999],
    "sedentary_min": [7777, 9999],
    "sleep_hours": [77, 99],
}


def build_analysis_table(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the full merged frame into a curated, renamed analysis table.

    Keeps the id columns, selects and renames the variables in
    :data:`VARIABLE_MAP`, coalesces the cycle-specific sleep variable into
    ``sleep_hours``, and converts known sentinel codes to ``NaN``.

    Parameters
    ----------
    df
        The full merged dataset from
        :func:`src.data_loading.build_merged_dataset`.

    Returns
    -------
    pandas.DataFrame
        Curated table: ids first, then the mapped feature/target columns.
    """
    out = pd.DataFrame(index=df.index)

    # 1. Identifiers first.
    for col in ID_COLS:
        if col in df.columns:
            out[col] = df[col]

    # 2. Selected + renamed variables (only those actually present).
    for src, name in VARIABLE_MAP.items():
        if src in df.columns:
            out[name] = df[src]

    # 3. Coalesce the cycle-specific sleep variable.
    sleep = None
    for src in SLEEP_SOURCES:
        if src in df.columns:
            sleep = df[src] if sleep is None else sleep.combine_first(df[src])
    if sleep is not None:
        out["sleep_hours"] = sleep

    # 4. Convert known sentinel codes to NaN.
    out = replace_missing_codes(out, SENTINEL_CODES)

    return out


def replace_missing_codes(
    df: pd.DataFrame,
    missing_codes: Mapping[str, list] | None = None,
) -> pd.DataFrame:
    """Replace NHANES sentinel codes (e.g., 7/9, 777/999) with ``NaN``.

    Parameters
    ----------
    df
        DataFrame to clean (with friendly column names).
    missing_codes
        Mapping of ``column -> [codes to treat as missing]``. Defaults to
        :data:`SENTINEL_CODES`.

    Returns
    -------
    pandas.DataFrame
        A copy with sentinel codes replaced by ``NaN``.
    """
    if missing_codes is None:
        missing_codes = SENTINEL_CODES
    out = df.copy()
    for col, codes in missing_codes.items():
        if col in out.columns:
            out[col] = out[col].replace(list(codes), pd.NA)
    return out


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline on a merged NHANES frame.

    Currently: build the curated analysis table (select + rename + coalesce sleep
    + sentinel-to-NaN). Extend with dtype coercion, categorical decoding, and
    missing-value handling as the project develops.

    Parameters
    ----------
    df
        Merged NHANES DataFrame (see
        :func:`src.data_loading.build_merged_dataset`).

    Returns
    -------
    pandas.DataFrame
        Cleaned, analysis-ready DataFrame.
    """
    return build_analysis_table(df)


def decode_columns(
    df: pd.DataFrame,
    codebook: Mapping[str, Mapping],
) -> pd.DataFrame:
    """Decode NHANES coded values into human-readable categories.

    Parameters
    ----------
    df
        DataFrame with raw coded columns.
    codebook
        Mapping of ``column name -> {code: label}`` derived from the NHANES
        variable documentation (e.g. ``{"sex": {1: "Male", 2: "Female"}}``).

    Returns
    -------
    pandas.DataFrame
        DataFrame with decoded columns.
    """
    raise NotImplementedError


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
) -> pd.DataFrame:
    """Impute or drop missing values.

    Parameters
    ----------
    df
        DataFrame with ``NaN`` values.
    strategy
        Missing-data strategy, e.g. ``"drop"``, ``"median"``, ``"knn"``.

    Returns
    -------
    pandas.DataFrame
    """
    raise NotImplementedError


if __name__ == "__main__":
    from src.data_loading import PROCESSED_DATA_DIR, build_merged_dataset

    merged_path = PROCESSED_DATA_DIR / "nhanes_merged.csv"
    if merged_path.exists():
        merged = pd.read_csv(merged_path, low_memory=False)
    else:
        merged = build_merged_dataset(save_path=merged_path)

    clean = clean_dataframe(merged)
    out = PROCESSED_DATA_DIR / "nhanes_clean.csv"
    clean.to_csv(out, index=False)
    print(f"Clean table: {clean.shape[0]:,} rows x {clean.shape[1]:,} columns")
    print(f"Columns: {list(clean.columns)}")
    print(f"Saved to {out}")

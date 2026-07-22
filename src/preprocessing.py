"""Phase 1 NHANES cleaning and derivation helpers.

This module contains reusable transformations.  File paths and writes belong in
``scripts/build_phase1.py`` so notebooks do not implement their own cleaning.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd


ID_COLUMNS = ["uid", "SEQN", "cycle"]
SURVEY_DESIGN_COLUMNS = ["weight_mec_2yr", "weight_int_2yr", "svy_psu", "svy_stratum"]

SENTINEL_CODES: dict[str, list[int]] = {
    "education": [7, 9],
    "vigorous_rec_activity": [7, 9],
    "moderate_rec_activity": [7, 9],
    "smoked_100_cigs": [7, 9],
    "avg_drinks_per_day": [777, 999],
    "sedentary_min": [7777, 9999],
    "sleep_hours": [77, 99],
}


def normalize_xpt_zero_artifact(df: pd.DataFrame, tolerance: float = 1e-70) -> pd.DataFrame:
    """Replace the SAS-XPORT near-zero representation with exact zero."""
    out = df.copy()
    for column in out.select_dtypes(include="number").columns:
        mask = out[column].notna() & out[column].abs().lt(tolerance)
        out.loc[mask, column] = 0.0
    return out


def replace_missing_codes(
    df: pd.DataFrame,
    missing_codes: Mapping[str, list[int]] | None = None,
) -> pd.DataFrame:
    """Replace documented refused/don't-know sentinels with missing values."""
    out = df.copy()
    for column, codes in (missing_codes or SENTINEL_CODES).items():
        if column in out.columns:
            out[column] = out[column].replace(codes, pd.NA)
    return out


def filter_adults(df: pd.DataFrame, minimum_age: int = 20) -> pd.DataFrame:
    """Keep adults and assert that the project UID is unique."""
    if "age" not in df or "uid" not in df:
        raise KeyError("Adult filtering requires age and uid")
    out = df.loc[df["age"].ge(minimum_age)].copy()
    if out["uid"].duplicated().any():
        examples = out.loc[out["uid"].duplicated(keep=False), "uid"].head().tolist()
        raise ValueError(f"Duplicate adult UID values detected, examples: {examples}")
    return out


def derive_bp_means(bpx: pd.DataFrame) -> pd.DataFrame:
    """Return SEQN and means of all available valid repeated BP readings."""
    systolic = [c for c in ("BPXSY1", "BPXSY2", "BPXSY3", "BPXSY4") if c in bpx]
    diastolic = [c for c in ("BPXDI1", "BPXDI2", "BPXDI3", "BPXDI4") if c in bpx]
    if not systolic or not diastolic or "SEQN" not in bpx:
        raise KeyError("BPX data must contain SEQN and repeated systolic/diastolic readings")
    out = bpx[["SEQN"]].copy()
    out["bp_systolic_mean"] = bpx[systolic].mean(axis=1, skipna=True)
    out["bp_diastolic_mean"] = bpx[diastolic].mean(axis=1, skipna=True)
    out["bp_valid_reading_count"] = bpx[systolic].notna().sum(axis=1).astype("Int8")
    return out


def derive_diet_fields(dr1tot: pd.DataFrame) -> pd.DataFrame:
    """Return potassium and Day 1 recall-status fields."""
    required = ["SEQN", "DR1DRSTZ", "DR1TPOTA"]
    missing = sorted(set(required).difference(dr1tot.columns))
    if missing:
        raise KeyError(f"DR1TOT missing required columns: {missing}")
    out = dr1tot[required].rename(columns={
        "DR1DRSTZ": "diet_recall_status",
        "DR1TPOTA": "potassium_mg",
    }).copy()
    out["diet_recall_reliable"] = out["diet_recall_status"].eq(1)
    return out


def derive_activity_minutes(paq: pd.DataFrame) -> pd.DataFrame:
    """Derive weekly recreational minutes and clean sedentary minutes."""
    required = [
        "SEQN", "PAQ650", "PAQ655", "PAD660", "PAQ665", "PAQ670",
        "PAD675", "PAD680",
    ]
    missing = sorted(set(required).difference(paq.columns))
    if missing:
        raise KeyError(f"PAQ missing required columns: {missing}")
    work = paq[required].copy()
    for column, codes in {
        "PAQ650": [7, 9], "PAQ655": [77, 99], "PAD660": [7777, 9999],
        "PAQ665": [7, 9], "PAQ670": [77, 99], "PAD675": [7777, 9999],
        "PAD680": [7777, 9999],
    }.items():
        work[column] = work[column].replace(codes, np.nan)

    out = work[["SEQN"]].copy()
    out["vigorous_rec_min_week"] = np.where(
        work["PAQ650"].eq(1), work["PAQ655"] * work["PAD660"],
        np.where(work["PAQ650"].eq(2), 0, np.nan),
    )
    out["moderate_rec_min_week"] = np.where(
        work["PAQ665"].eq(1), work["PAQ670"] * work["PAD675"],
        np.where(work["PAQ665"].eq(2), 0, np.nan),
    )
    out["sedentary_min"] = work["PAD680"]
    return out


def merge_supplemental_fields(
    adult_df: pd.DataFrame,
    bp_fields: pd.DataFrame,
    diet_fields: pd.DataFrame,
    activity_fields: pd.DataFrame,
) -> pd.DataFrame:
    """Merge one cycle's derived fields onto the corresponding adult rows."""
    out = adult_df.copy()
    for fields in (bp_fields, diet_fields, activity_fields):
        out = out.merge(fields, on="SEQN", how="left", validate="one_to_one")
    return out


def model_ready_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove survey-design fields from the model-ready table."""
    return df.drop(columns=[c for c in SURVEY_DESIGN_COLUMNS if c in df]).copy()

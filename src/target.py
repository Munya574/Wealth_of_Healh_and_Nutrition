"""Metabolic-syndrome component scoring and target construction."""

from __future__ import annotations

import pandas as pd


FLAG_COLUMNS = [
    "waist_flag", "bp_flag", "triglycerides_flag", "hdl_flag", "hba1c_flag",
]
NON_TRIGLYCERIDE_FLAGS = ["waist_flag", "bp_flag", "hdl_flag", "hba1c_flag"]


def _nullable_flag(known: pd.Series, positive: pd.Series) -> pd.Series:
    """Return a nullable Int8 flag: 1/0 when known and NA otherwise."""
    result = pd.Series(pd.NA, index=known.index, dtype="Int8")
    result.loc[known] = positive.loc[known].astype("int8")
    return result


def score_metabolic_components(df: pd.DataFrame) -> pd.DataFrame:
    """Create five nullable metabolic-component flags.

    Sex uses NHANES coding (1=male, 2=female).  A negative blood-pressure
    component requires both systolic and diastolic means to be observed; one
    high observed value is sufficient for a positive component.
    """
    required = {
        "sex", "waist_cm", "bp_systolic_mean", "bp_diastolic_mean",
        "triglycerides", "hdl", "hba1c",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"Missing target-construction columns: {missing}")

    out = pd.DataFrame(index=df.index)
    male = df["sex"].eq(1)
    female = df["sex"].eq(2)
    valid_sex = male | female

    out["waist_flag"] = _nullable_flag(
        valid_sex & df["waist_cm"].notna(),
        (male & df["waist_cm"].ge(102)) | (female & df["waist_cm"].ge(88)),
    )

    bp_positive = df["bp_systolic_mean"].ge(130) | df["bp_diastolic_mean"].ge(85)
    bp_known = bp_positive | df[["bp_systolic_mean", "bp_diastolic_mean"]].notna().all(axis=1)
    out["bp_flag"] = _nullable_flag(bp_known, bp_positive)

    out["triglycerides_flag"] = _nullable_flag(
        df["triglycerides"].notna(), df["triglycerides"].ge(150)
    )
    out["hdl_flag"] = _nullable_flag(
        valid_sex & df["hdl"].notna(),
        (male & df["hdl"].lt(40)) | (female & df["hdl"].lt(50)),
    )
    out["hba1c_flag"] = _nullable_flag(df["hba1c"].notna(), df["hba1c"].ge(5.7))
    return out


def build_metabolic_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Return component flags, strict label, and deterministic primary label.

    The primary label recovers a triglycerides-missing record only when the four
    known components make the final class invariant: 0-1 positives -> 0;
    3-4 positives -> 1; exactly 2 positives remains unresolved.
    """
    out = score_metabolic_components(df)
    out["metabolic_component_count_known"] = out[FLAG_COLUMNS].sum(
        axis=1, min_count=1
    ).astype("Int8")
    out["metabolic_component_known_n"] = out[FLAG_COLUMNS].notna().sum(axis=1).astype("Int8")

    all_five = out[FLAG_COLUMNS].notna().all(axis=1)
    out["metabolic_syndrome_strict"] = _nullable_flag(
        all_five, out[FLAG_COLUMNS].sum(axis=1).ge(3)
    )

    other_four_known = out[NON_TRIGLYCERIDE_FLAGS].notna().all(axis=1)
    triglycerides_only_missing = out["triglycerides_flag"].isna() & other_four_known
    other_sum = out[NON_TRIGLYCERIDE_FLAGS].sum(axis=1)
    determinable = triglycerides_only_missing & (other_sum.le(1) | other_sum.ge(3))

    out["metabolic_syndrome"] = out["metabolic_syndrome_strict"].copy()
    out.loc[determinable, "metabolic_syndrome"] = other_sum.loc[determinable].ge(3).astype("int8")

    out["label_basis"] = pd.Series(pd.NA, index=out.index, dtype="string")
    out.loc[all_five, "label_basis"] = "all_5_observed"
    out.loc[determinable, "label_basis"] = "triglycerides_missing_but_label_determinable"
    out.loc[triglycerides_only_missing & other_sum.eq(2), "label_basis"] = (
        "triglycerides_required_to_resolve"
    )
    return out


def add_metabolic_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with all target fields appended."""
    return df.join(build_metabolic_targets(df))

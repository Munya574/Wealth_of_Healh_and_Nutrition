import pandas as pd

from src.target import build_metabolic_targets


def _row(**overrides):
    row = dict(
        sex=1, waist_cm=90, bp_systolic_mean=120, bp_diastolic_mean=75,
        triglycerides=100, hdl=50, hba1c=5.4,
    )
    row.update(overrides)
    return row


def test_strict_positive_and_negative():
    df = pd.DataFrame([
        _row(waist_cm=110, bp_systolic_mean=140, triglycerides=160),
        _row(),
    ])
    result = build_metabolic_targets(df)
    assert result["metabolic_syndrome_strict"].tolist() == [1, 0]


def test_missing_triglycerides_is_recovered_only_when_determinable():
    df = pd.DataFrame([
        _row(triglycerides=None),
        _row(waist_cm=110, bp_systolic_mean=140, hdl=30, triglycerides=None),
        _row(waist_cm=110, bp_systolic_mean=140, triglycerides=None),
    ])
    result = build_metabolic_targets(df)
    assert result["metabolic_syndrome"].iloc[0] == 0
    assert result["metabolic_syndrome"].iloc[1] == 1
    assert pd.isna(result["metabolic_syndrome"].iloc[2])


def test_missing_bp_counterpart_does_not_create_false_negative():
    df = pd.DataFrame([_row(bp_systolic_mean=120, bp_diastolic_mean=None)])
    result = build_metabolic_targets(df)
    assert pd.isna(result["bp_flag"].iloc[0])


"""Build the metabolic-health composite target.

Instead of predicting BMI, this project defines a composite target from multiple
clinical metabolic markers (e.g., fasting glucose / HbA1c, blood pressure,
triglycerides, HDL, waist circumference). The exact components, thresholds, and
scoring scheme are TBD.

These stubs define the interface; implementations are TBD.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd


def build_metabolic_target(
    df: pd.DataFrame,
    components: Sequence[str] | None = None,
) -> pd.Series:
    """Construct the metabolic-health composite target.

    Parameters
    ----------
    df
        Cleaned DataFrame containing the required clinical marker columns.
    components
        Optional list of marker columns to combine. If ``None``, use the
        project default set (glucose/HbA1c, blood pressure, lipids, waist).

    Returns
    -------
    pandas.Series
        The composite target, indexed like ``df`` (score or class label).
    """
    raise NotImplementedError


def score_metabolic_components(df: pd.DataFrame) -> pd.DataFrame:
    """Score each individual metabolic marker (e.g., normal/at-risk flags).

    Parameters
    ----------
    df
        Cleaned DataFrame with the raw clinical marker columns.

    Returns
    -------
    pandas.DataFrame
        Per-marker component scores used to assemble the composite target.
    """
    raise NotImplementedError


def binarize_target(target: pd.Series, threshold: float) -> pd.Series:
    """Convert a continuous metabolic score into a binary label.

    Parameters
    ----------
    target
        Continuous composite score.
    threshold
        Cutoff separating "healthy" from "at-risk".

    Returns
    -------
    pandas.Series
        Binary (0/1) target.
    """
    raise NotImplementedError

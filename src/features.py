"""Feature selection and engineering for the metabolic-health models.

Focus is on nutrition and physical-activity predictors. This module derives
engineered features and selects the subset fed to the models.

These stubs define the interface; implementations are TBD.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive engineered features (ratios, indices, aggregates, etc.).

    Parameters
    ----------
    df
        Cleaned DataFrame.

    Returns
    -------
    pandas.DataFrame
        DataFrame with additional engineered feature columns.
    """
    raise NotImplementedError


def select_features(
    df: pd.DataFrame,
    target: pd.Series,
    method: str = "model",
) -> list[str]:
    """Select the feature columns to use for modeling.

    Parameters
    ----------
    df
        DataFrame of candidate features.
    target
        The metabolic-health target (see :mod:`src.target`).
    method
        Selection method, e.g. ``"correlation"``, ``"model"`` (importance),
        or ``"rfe"``.

    Returns
    -------
    list of str
        Names of the selected feature columns.
    """
    raise NotImplementedError


def build_feature_matrix(
    df: pd.DataFrame,
    features: Sequence[str],
) -> pd.DataFrame:
    """Assemble the final model-ready feature matrix.

    Parameters
    ----------
    df
        DataFrame containing at least the columns in ``features``.
    features
        Column names to include (see :func:`select_features`).

    Returns
    -------
    pandas.DataFrame
        The ``X`` matrix ready for model training.
    """
    raise NotImplementedError

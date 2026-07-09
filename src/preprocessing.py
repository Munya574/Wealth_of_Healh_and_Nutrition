"""Cleaning, column decoding, and missing-value handling for NHANES data.

NHANES uses coded categorical values (e.g., ``1 = Male``, ``7 = Refused``,
``9 = Don't know``) and sentinel codes for missing/refused responses. This module
turns the raw merged frame into an analysis-ready table.

These stubs define the interface; implementations are TBD.
"""

from __future__ import annotations

from typing import Mapping

import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline on a merged NHANES frame.

    Typically: drop unusable columns, decode categoricals, convert sentinel
    missing codes to ``NaN``, coerce dtypes, and handle missing values.

    Parameters
    ----------
    df
        Merged NHANES DataFrame (see :func:`src.data_loading.merge_on_seqn`).

    Returns
    -------
    pandas.DataFrame
        Cleaned, analysis-ready DataFrame.
    """
    raise NotImplementedError


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
        variable documentation.

    Returns
    -------
    pandas.DataFrame
        DataFrame with decoded columns.
    """
    raise NotImplementedError


def replace_missing_codes(
    df: pd.DataFrame,
    missing_codes: Mapping[str, list] | None = None,
) -> pd.DataFrame:
    """Replace NHANES sentinel codes (e.g., 7/9, 777/999) with ``NaN``.

    Parameters
    ----------
    df
        DataFrame to clean.
    missing_codes
        Optional mapping of ``column -> [codes to treat as missing]``. If
        ``None``, apply project-wide defaults.

    Returns
    -------
    pandas.DataFrame
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

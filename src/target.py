"""Build the metabolic-health composite target (metabolic syndrome).

Instead of predicting BMI, the label is **metabolic syndrome**: a person is flagged
`1` (at-risk) if they meet **3 or more** of the 5 criteria below, else `0`
(healthy). Criteria follow the harmonized definition (Alberti et al., 2009).

Note on blood sugar: the harmonized definition uses *fasting glucose ≥ 100 mg/dL*,
but our data has no fasting-glucose file — so this project uses **HbA1c ≥ 5.7%** as
the glycemic flag instead (team decision; see TASKS.md).

The 5 criteria, mapped to columns in ``nhanes_clean.csv``:

===================  ==========================  ===========================
Criterion            Column(s)                   Flag when
===================  ==========================  ===========================
Waist (elevated)     ``waist_cm`` + ``sex``      Male ≥102 cm, Female ≥88 cm
Blood pressure       ``bp_systolic`` /           systolic ≥130 OR
                     ``bp_diastolic``            diastolic ≥85
Triglycerides        ``triglycerides``           ≥150 mg/dL
HDL (low)            ``hdl`` + ``sex``           Male <40, Female <50 mg/dL
Blood sugar (HbA1c)  ``hba1c``                   ≥5.7%
===================  ==========================  ===========================

``sex`` is coded 1 = Male, 2 = Female (raw NHANES ``RIAGENDR``).

These stubs define the interface; the Task 1 owner fills in the implementations.
"""

from __future__ import annotations

import pandas as pd

# Thresholds for the 5 metabolic-syndrome criteria (harmonized definition, with
# HbA1c standing in for fasting glucose). Sex-specific cutoffs are (male, female),
# where sex is coded 1 = Male, 2 = Female.
MSYN_THRESHOLDS = {
    "waist_cm": {1: 102, 2: 88},      # >= flags elevated waist
    "bp_systolic": 130,               # >= flags high BP (with diastolic)
    "bp_diastolic": 85,               # >=
    "triglycerides": 150,             # >=
    "hdl": {1: 40, 2: 50},            # <  flags low HDL
    "hba1c": 5.7,                     # >= flags high blood sugar
}

# Number of criteria met to be labelled at-risk (metabolic syndrome).
MSYN_FLAG_COUNT = 3


def build_metabolic_target(df: pd.DataFrame) -> pd.Series:
    """Construct the binary metabolic-syndrome label (0 = healthy, 1 = at-risk).

    Expected flow: call :func:`score_metabolic_components` to get the 5 per-criterion
    flags, sum them per person, then label ``1`` where the count is
    ``>= MSYN_FLAG_COUNT`` (3). Rows missing the markers needed to decide should be
    left as ``NaN`` (excluded from modeling), not silently counted as healthy.

    Parameters
    ----------
    df
        Cleaned DataFrame (``nhanes_clean.csv``) with the marker columns and
        ``sex``.

    Returns
    -------
    pandas.Series
        The ``metabolic_syndrome`` label indexed like ``df``.
    """
    raise NotImplementedError


def score_metabolic_components(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the 5 metabolic-syndrome flags (one boolean column each).

    Applies the cutoffs in :data:`MSYN_THRESHOLDS` — waist and HDL use the
    sex-specific values (``sex`` 1 = Male, 2 = Female); blood pressure flags if
    *either* systolic or diastolic is elevated; blood sugar uses HbA1c ≥ 5.7%.

    Parameters
    ----------
    df
        Cleaned DataFrame with the raw marker columns and ``sex``.

    Returns
    -------
    pandas.DataFrame
        One boolean column per criterion (waist, blood pressure, triglycerides,
        HDL, blood sugar), used to assemble the label.
    """
    raise NotImplementedError


def binarize_target(flag_count: pd.Series, threshold: int = MSYN_FLAG_COUNT) -> pd.Series:
    """Convert the per-person flag count into the binary 0/1 label.

    Parameters
    ----------
    flag_count
        Number of metabolic-syndrome criteria met per person (0–5).
    threshold
        Minimum flags to be labelled at-risk. Defaults to
        :data:`MSYN_FLAG_COUNT` (3).

    Returns
    -------
    pandas.Series
        Binary (0/1) label; ``NaN`` preserved where the count is unknown.
    """
    raise NotImplementedError

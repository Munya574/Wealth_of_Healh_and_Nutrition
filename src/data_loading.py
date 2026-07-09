"""Load and merge NHANES component files.

NHANES distributes data as SAS transport (``.XPT``) files, one per component
(Demographics, Dietary, Examination, Laboratory, Questionnaire). Records across
components are linked by the respondent sequence number ``SEQN``.

These stubs define the loading/merging interface; implementations are TBD.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd

# Directory holding the raw NHANES files (gitignored locally).
# Override with the NHANES_RAW_DIR env var — e.g. on Google Colab point it at the
# mounted Drive folder: os.environ["NHANES_RAW_DIR"] = "/content/drive/MyDrive/nhanes".
RAW_DATA_DIR = Path(
    os.environ.get(
        "NHANES_RAW_DIR",
        Path(__file__).resolve().parents[1] / "data" / "raw",
    )
)

# NHANES cycles pooled in this project (2013-2018) and their file suffixes.
CYCLE_SUFFIXES = {"2013-2014": "_H", "2015-2016": "_I", "2017-2018": "_J"}


def load_nhanes_file(path: str | Path) -> pd.DataFrame:
    """Load a single NHANES component file into a DataFrame.

    Parameters
    ----------
    path
        Path to a ``.XPT`` (SAS transport) or ``.csv`` file in ``data/raw/``.

    Returns
    -------
    pandas.DataFrame
        The component's records, including the ``SEQN`` key column.
    """
    raise NotImplementedError


def load_component(name: str, raw_dir: str | Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Load a named NHANES component by resolving its file in ``raw_dir``.

    Parameters
    ----------
    name
        Component/file code (e.g., ``"DEMO_J"``). Exact codes TBD — see
        ``data/README.md``.
    raw_dir
        Directory containing the raw files. Defaults to ``data/raw/``.

    Returns
    -------
    pandas.DataFrame
    """
    raise NotImplementedError


def pool_cycles(
    base_code: str,
    cycles: Iterable[str] = tuple(CYCLE_SUFFIXES.values()),
    raw_dir: str | Path = RAW_DATA_DIR,
) -> pd.DataFrame:
    """Load one NHANES component across cycles and stack the rows.

    For a base code like ``"DEMO"`` this loads ``DEMO_H``, ``DEMO_I``, ``DEMO_J``
    and concatenates them into a single frame (adding a cycle indicator column).

    Parameters
    ----------
    base_code
        Component base code without the cycle suffix (e.g., ``"DEMO"``).
    cycles
        Cycle suffixes to include (defaults to ``_H``, ``_I``, ``_J``).
    raw_dir
        Directory containing the raw files. Defaults to ``data/raw/``.

    Returns
    -------
    pandas.DataFrame
        Row-wise concatenation of the component across the requested cycles.
    """
    raise NotImplementedError


def merge_on_seqn(
    frames: Iterable[pd.DataFrame],
    how: str = "inner",
    key: str = "SEQN",
) -> pd.DataFrame:
    """Merge multiple NHANES component DataFrames on the ``SEQN`` key.

    Parameters
    ----------
    frames
        Component DataFrames to merge, each containing ``key``.
    how
        Join strategy passed to :func:`pandas.merge` (e.g., ``"inner"``,
        ``"outer"``, ``"left"``).
    key
        Join column. Defaults to ``"SEQN"``.

    Returns
    -------
    pandas.DataFrame
        A single wide DataFrame keyed by ``SEQN``.
    """
    raise NotImplementedError


def load_and_merge(
    components: Iterable[str],
    how: str = "inner",
    raw_dir: str | Path = RAW_DATA_DIR,
) -> pd.DataFrame:
    """Convenience wrapper: load each named component and merge on ``SEQN``.

    Parameters
    ----------
    components
        Component/file codes to load (see ``data/README.md``).
    how
        Join strategy for the merge.
    raw_dir
        Directory containing the raw files.

    Returns
    -------
    pandas.DataFrame
    """
    raise NotImplementedError

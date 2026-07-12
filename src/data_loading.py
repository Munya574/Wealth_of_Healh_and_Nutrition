"""Load and merge NHANES component files into one analysis table.

NHANES distributes data as SAS transport (``.xpt``) files, one per component
(Demographics, Dietary, Examination, Laboratory, Questionnaire). Records within a
cycle are linked by the respondent sequence number ``SEQN``.

Important: ``SEQN`` is only unique **within** a cycle — the same value can refer
to different people in different cycles. So the pipeline merges components on
``SEQN`` *within each cycle* (column-wise), then stacks the cycles *row-wise*,
tagging each row with its ``cycle``. The result is keyed by (``cycle``, ``SEQN``).
"""

from __future__ import annotations

import os
from functools import reduce
from pathlib import Path
from typing import Iterable, Mapping

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

# Where the merged output is written.
PROCESSED_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# NHANES cycles pooled in this project (2013-2018). Keys are the per-cycle
# subfolder names under data/raw/; values are the file-code suffixes. So the file
# for component "DEMO" in the 2013-2014 cycle is:
#     data/raw/2013-2014/DEMO_H.xpt
CYCLE_SUFFIXES = {"2013-2014": "_H", "2015-2016": "_I", "2017-2018": "_J"}

# Components present in every cycle (see data/README.md for descriptions).
# DEMO is first so it seeds the within-cycle merge (it holds every respondent).
COMPONENTS = (
    "DEMO", "DR1TOT", "BMX", "BPX", "GHB", "HDL", "TCHOL",
    "TRIGLY", "PAQ", "ALQ", "SMQ", "SLQ", "FSQ",
)

# File extensions tried when resolving a component, in priority order.
_EXTENSIONS = (".xpt", ".XPT", ".csv")


def load_nhanes_file(path: str | Path) -> pd.DataFrame:
    """Load a single NHANES component file into a DataFrame.

    Parameters
    ----------
    path
        Path to a ``.xpt`` (SAS transport) or ``.csv`` file.

    Returns
    -------
    pandas.DataFrame
        The component's records, including the ``SEQN`` key column (cast to a
        nullable integer).
    """
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".xpt":
        df = pd.read_sas(path, format="xport", encoding="latin1")
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file type {path.suffix!r}: {path}")

    if "SEQN" in df.columns:
        df["SEQN"] = df["SEQN"].astype("Int64")
    return df


def _resolve_component_path(
    base_code: str,
    cycle: str,
    raw_dir: str | Path = RAW_DATA_DIR,
) -> Path:
    """Resolve the on-disk path for a component in a given cycle.

    Looks for ``<raw_dir>/<cycle>/<base_code><suffix><ext>``, e.g.
    ``data/raw/2013-2014/DEMO_H.xpt``.
    """
    if cycle not in CYCLE_SUFFIXES:
        raise KeyError(f"Unknown cycle {cycle!r}; expected one of {list(CYCLE_SUFFIXES)}")
    stem = f"{base_code}{CYCLE_SUFFIXES[cycle]}"
    folder = Path(raw_dir) / cycle
    for ext in _EXTENSIONS:
        candidate = folder / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No file for component {base_code!r} in cycle {cycle!r} "
        f"(looked for {stem}{{{','.join(_EXTENSIONS)}}} in {folder})"
    )


def load_component(
    base_code: str,
    cycle: str,
    raw_dir: str | Path = RAW_DATA_DIR,
) -> pd.DataFrame:
    """Load one NHANES component for one cycle.

    Parameters
    ----------
    base_code
        Component base code without the cycle suffix (e.g., ``"DEMO"``).
    cycle
        Cycle subfolder name (a key of :data:`CYCLE_SUFFIXES`, e.g. ``"2013-2014"``).
    raw_dir
        Root directory containing the per-cycle subfolders.

    Returns
    -------
    pandas.DataFrame
    """
    return load_nhanes_file(_resolve_component_path(base_code, cycle, raw_dir))


def pool_cycles(
    base_code: str,
    cycles: Iterable[str] = tuple(CYCLE_SUFFIXES),
    raw_dir: str | Path = RAW_DATA_DIR,
) -> pd.DataFrame:
    """Load one NHANES component across cycles and stack the rows.

    For ``base_code="DEMO"`` this reads one file per cycle from its subfolder
    (``2013-2014/DEMO_H.xpt``, ...) and concatenates them into a single frame with
    a ``cycle`` indicator column.

    Parameters
    ----------
    base_code
        Component base code without the cycle suffix (e.g., ``"DEMO"``).
    cycles
        Cycle subfolder names to include (keys of :data:`CYCLE_SUFFIXES`).
    raw_dir
        Root directory containing the per-cycle subfolders.

    Returns
    -------
    pandas.DataFrame
        Row-wise concatenation of the component across the requested cycles.
    """
    frames = []
    for cycle in cycles:
        df = load_component(base_code, cycle, raw_dir)
        df.insert(1, "cycle", cycle)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def merge_on_seqn(
    frames: Iterable[pd.DataFrame],
    how: str = "left",
    key: str = "SEQN",
) -> pd.DataFrame:
    """Merge component DataFrames (from a single cycle) on the ``SEQN`` key.

    Reduces the frames with successive :meth:`pandas.DataFrame.merge` calls. Only
    ``key`` is expected to be shared; any other colliding column names get a
    ``_dupN`` suffix so nothing is silently overwritten.

    Parameters
    ----------
    frames
        Component DataFrames to merge, each containing ``key``. Should all come
        from the same cycle (SEQN is only unique within a cycle).
    how
        Join strategy passed to :func:`pandas.merge` (``"left"``, ``"inner"``,
        ``"outer"``). The first frame seeds the join, so pass ``DEMO`` first for
        a left join that keeps every respondent.
    key
        Join column. Defaults to ``"SEQN"``.

    Returns
    -------
    pandas.DataFrame
        A single wide DataFrame keyed by ``key``.
    """
    frames = list(frames)
    if not frames:
        raise ValueError("merge_on_seqn requires at least one frame")

    def _merge(left: pd.DataFrame, right_with_i: tuple[int, pd.DataFrame]) -> pd.DataFrame:
        i, right = right_with_i
        return left.merge(right, on=key, how=how, suffixes=("", f"_dup{i}"))

    first, *rest = frames
    return reduce(_merge, enumerate(rest, start=1), first)


def build_merged_dataset(
    components: Iterable[str] = COMPONENTS,
    cycles: Iterable[str] = tuple(CYCLE_SUFFIXES),
    how: str = "left",
    base_component: str = "DEMO",
    raw_dir: str | Path = RAW_DATA_DIR,
    save_path: str | Path | None = None,
) -> pd.DataFrame:
    """Build the full merged dataset: merge within each cycle, then stack cycles.

    For each cycle, every component is loaded and merged on ``SEQN`` (seeded by
    ``base_component`` so a ``how="left"`` join keeps all respondents). Each
    cycle's wide frame gets a ``cycle`` column, then all cycles are concatenated
    row-wise. The result is one row per respondent, keyed by (``cycle``, ``SEQN``).

    Parameters
    ----------
    components
        Component base codes to include (defaults to :data:`COMPONENTS`).
    cycles
        Cycle subfolder names to include (defaults to all of :data:`CYCLE_SUFFIXES`).
    how
        Join strategy for the within-cycle merge (default ``"left"`` from
        ``base_component``).
    base_component
        Component that seeds each within-cycle merge (default ``"DEMO"``).
    raw_dir
        Root directory containing the per-cycle subfolders.
    save_path
        Optional path to write the result. ``.csv`` and ``.parquet`` are
        supported (parquet needs ``pyarrow``). Parent dirs are created.

    Returns
    -------
    pandas.DataFrame
        The merged, cycle-pooled dataset.
    """
    components = list(components)
    if base_component not in components:
        raise ValueError(f"base_component {base_component!r} must be in components")
    # Put the base component first so it seeds each within-cycle merge.
    ordered = [base_component] + [c for c in components if c != base_component]

    cycle_frames = []
    for cycle in cycles:
        loaded = [load_component(code, cycle, raw_dir) for code in ordered]
        merged = merge_on_seqn(loaded, how=how)
        merged.insert(1, "cycle", cycle)
        cycle_frames.append(merged)

    full = pd.concat(cycle_frames, ignore_index=True).copy()  # copy() defragments

    # Globally-unique per-row id: cycle + SEQN (e.g. "2013-2014_73557").
    # Safe to set_index / dedup on, unlike SEQN alone (unique only within a cycle).
    full.insert(0, "uid", full["cycle"] + "_" + full["SEQN"].astype("string"))

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if save_path.suffix.lower() == ".parquet":
            full.to_parquet(save_path, index=False)
        else:
            full.to_csv(save_path, index=False)

    return full


if __name__ == "__main__":
    # Build and save the merged dataset to data/processed/nhanes_merged.csv.
    out = PROCESSED_DATA_DIR / "nhanes_merged.csv"
    df = build_merged_dataset(save_path=out)
    print(f"Merged dataset: {df.shape[0]:,} rows x {df.shape[1]:,} columns")
    print(df["cycle"].value_counts().sort_index().to_string())
    print(f"Saved to {out}")

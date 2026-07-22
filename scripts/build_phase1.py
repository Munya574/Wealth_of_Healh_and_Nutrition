"""Rebuild the updated ``nhanes_clean.csv`` from team Drive inputs.

Example (Colab):

    python scripts/build_phase1.py \
      --input-clean /content/drive/MyDrive/.../Processed/nhanes_clean.csv \
      --raw-root /content/drive/MyDrive/.../Datasets \
      --output /content/nhanes_clean.csv \
      --audit-dir /content/phase1_audit

The output defaults to a new local path and never overwrites the input unless
the caller explicitly supplies the same resolved path.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.preprocessing import (
    derive_activity_minutes,
    derive_bp_means,
    derive_diet_fields,
    filter_adults,
    model_ready_columns,
    normalize_xpt_zero_artifact,
)
from src.target import add_metabolic_targets


CYCLES = {
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J",
}


def resolve_xpt(raw_root: Path, cycle: str, stem: str, suffix: str) -> Path:
    """Resolve either ``root/cycle/FILE.xpt`` or a flat ``root/FILE.xpt``."""
    names = [f"{stem}_{suffix}.xpt", f"{stem}_{suffix}.XPT"]
    candidates = [raw_root / cycle / name for name in names]
    candidates += [raw_root / name for name in names]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    looked = "\n  ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Missing {stem}_{suffix}; looked in:\n  {looked}")


def read_xpt(raw_root: Path, cycle: str, stem: str, suffix: str) -> pd.DataFrame:
    frame = pd.read_sas(resolve_xpt(raw_root, cycle, stem, suffix), format="xport")
    frame["SEQN"] = frame["SEQN"].astype("Int64")
    return normalize_xpt_zero_artifact(frame)


def build_updated_clean(input_clean: Path, raw_root: Path) -> pd.DataFrame:
    old = pd.read_csv(input_clean, low_memory=False)
    old = normalize_xpt_zero_artifact(old)
    adult = filter_adults(old, minimum_age=20)

    cycle_outputs: list[pd.DataFrame] = []
    for cycle, suffix in CYCLES.items():
        current = adult.loc[adult["cycle"].eq(cycle)].copy()
        bp = derive_bp_means(read_xpt(raw_root, cycle, "BPX", suffix))
        diet = derive_diet_fields(read_xpt(raw_root, cycle, "DR1TOT", suffix))
        activity = derive_activity_minutes(read_xpt(raw_root, cycle, "PAQ", suffix))
        activity = activity.rename(columns={"sedentary_min": "sedentary_min_updated"})

        for fields in (bp, diet, activity):
            current = current.merge(fields, on="SEQN", how="left", validate="one_to_one")
        current["sedentary_min"] = current["sedentary_min_updated"].combine_first(
            current["sedentary_min"]
        )
        current = current.drop(columns="sedentary_min_updated")
        cycle_outputs.append(current)

    cleaned = pd.concat(cycle_outputs, ignore_index=True)
    cleaned = add_metabolic_targets(cleaned)
    cleaned = model_ready_columns(cleaned)
    if cleaned["uid"].duplicated().any():
        raise AssertionError("Duplicate UID detected in final cleaned dataset")
    return cleaned


def write_audit(cleaned: pd.DataFrame, audit_dir: Path) -> None:
    audit_dir.mkdir(parents=True, exist_ok=True)
    flow = pd.DataFrame([
        ("adults_age_20_plus", len(cleaned)),
        ("strict_all_5_label", cleaned["metabolic_syndrome_strict"].notna().sum()),
        ("combined_determinable_label", cleaned["metabolic_syndrome"].notna().sum()),
        ("combined_positive", cleaned["metabolic_syndrome"].eq(1).sum()),
        ("combined_negative", cleaned["metabolic_syndrome"].eq(0).sum()),
        ("valid_day1_diet", cleaned["diet_recall_reliable"].eq(True).sum()),
        (
            "combined_label_and_valid_day1_diet",
            (cleaned["metabolic_syndrome"].notna() & cleaned["diet_recall_reliable"].eq(True)).sum(),
        ),
    ], columns=["stage", "n"])
    flow.to_csv(audit_dir / "sample_flow.csv", index=False)
    pd.DataFrame({
        "column": cleaned.columns,
        "missing_n": cleaned.isna().sum().values,
        "missing_pct": (100 * cleaned.isna().mean()).round(3).values,
    }).to_csv(audit_dir / "missingness_summary.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-clean", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.input_clean.resolve() == args.output.resolve():
        raise ValueError("Output must differ from input; verify locally before replacing Drive data")
    cleaned = build_updated_clean(args.input_clean, args.raw_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)
    write_audit(cleaned, args.audit_dir)
    print(f"Saved {len(cleaned):,} rows x {len(cleaned.columns):,} columns to {args.output}")
    print(cleaned["metabolic_syndrome"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()

"""Create and verify the shared stratified 80/20 supervised-model split."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def create_shared_split(
    df: pd.DataFrame,
    output_dir: str | Path,
    *,
    uid_column: str = "uid",
    target_column: str = "metabolic_syndrome",
    require_reliable_diet: bool = True,
    test_size: float = 0.20,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Save train/test UID files after final eligibility is frozen.

    Stratification preserves the overall 0/1 label balance.  It does not use or
    expose predictor values, and it does not guarantee identical demographic
    distributions; those distributions must be checked in the split summary.
    """
    required = {uid_column, target_column}
    if require_reliable_diet:
        required.add("diet_recall_reliable")
    missing = sorted(required.difference(df.columns))
    if missing:
        raise KeyError(f"Cannot create split; missing columns: {missing}")
    if df[uid_column].duplicated().any():
        raise ValueError("UID values must be unique before splitting")

    eligible = df[target_column].notna()
    if require_reliable_diet:
        eligible &= df["diet_recall_reliable"].eq(True)
    sample = df.loc[eligible, [uid_column, target_column]].copy()

    train, test = train_test_split(
        sample,
        test_size=test_size,
        random_state=random_state,
        stratify=sample[target_column].astype(int),
    )
    train = train.sort_values(uid_column).reset_index(drop=True)
    test = test.sort_values(uid_column).reset_index(drop=True)
    verify_shared_split(train, test, sample, uid_column=uid_column)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    train[[uid_column]].to_csv(output / "train_uids.csv", index=False)
    test[[uid_column]].to_csv(output / "test_uids.csv", index=False)
    return train, test


def verify_shared_split(
    train: pd.DataFrame,
    test: pd.DataFrame,
    eligible: pd.DataFrame,
    *,
    uid_column: str = "uid",
) -> None:
    train_ids = set(train[uid_column])
    test_ids = set(test[uid_column])
    eligible_ids = set(eligible[uid_column])
    if train[uid_column].duplicated().any() or test[uid_column].duplicated().any():
        raise AssertionError("Duplicate UID found within a split")
    if train_ids.intersection(test_ids):
        raise AssertionError("Train/test UID overlap detected")
    if train_ids.union(test_ids) != eligible_ids:
        raise AssertionError("Train/test files do not cover every eligible UID exactly once")


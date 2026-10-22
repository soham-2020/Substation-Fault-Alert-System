"""Train and evaluate a Random Forest without resampling leakage."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.utils import resample

from simulate_transformer_data import FAULT_LABELS

FEATURE_COLUMNS = ["Voltage_V", "Current_A", "Temperature_C"]
BUNDLE_VERSION = 1


def prepare_splits(data: pd.DataFrame, test_size: float = 0.2, seed: int = 42):
    """Split original rows first, then upsample only the training partition."""
    required = set(FEATURE_COLUMNS + ["Fault_Status"])
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    data = data.dropna(subset=FEATURE_COLUMNS + ["Fault_Status"]).copy()
    unknown = set(data["Fault_Status"].unique()) - set(FAULT_LABELS)
    if unknown:
        raise ValueError(f"Unknown fault labels: {', '.join(sorted(unknown))}")
    data["Fault_Label"] = data["Fault_Status"].map(FAULT_LABELS).astype(int)
    X, y = data[FEATURE_COLUMNS], data["Fault_Label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )

    train = X_train.copy()
    train["Fault_Label"] = y_train
    majority_size = int(train["Fault_Label"].value_counts().max())
    balanced_parts = []
    for label, group in train.groupby("Fault_Label"):
        balanced_parts.append(resample(group, replace=len(group) < majority_size,
                                       n_samples=majority_size, random_state=seed + int(label)))
    balanced_train = pd.concat(balanced_parts).sample(frac=1, random_state=seed)
    return (
        balanced_train[FEATURE_COLUMNS], balanced_train["Fault_Label"],
        X_test, y_test,
    )


def train_model(data: pd.DataFrame, model_path: str | Path = "model.pkl", seed: int = 42):
    X_train, y_train, X_test, y_test = prepare_splits(data, seed=seed)
    classifier = RandomForestClassifier(
        n_estimators=200, class_weight="balanced", random_state=seed, n_jobs=-1
    )
    classifier.fit(X_train, y_train)
    predictions = classifier.predict(X_test)
    correct = int((predictions == y_test.to_numpy()).sum())
    total = int(len(y_test))
    print(f"Exact holdout accuracy: {correct}/{total} ({correct / total:.2%})")
    target_names = [name for name, _ in sorted(FAULT_LABELS.items(), key=lambda pair: pair[1])]
    print("Evaluation on the untouched, stratified holdout set:")
    print(classification_report(y_test, predictions, labels=list(FAULT_LABELS.values()),
                                target_names=target_names, zero_division=0))
    bundle = {
        "version": BUNDLE_VERSION,
        "model": classifier,
        "feature_columns": FEATURE_COLUMNS,
        "label_mapping": FAULT_LABELS,
    }
    joblib.dump(bundle, model_path)
    print(f"Saved model bundle to {model_path}")
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="transformer_data.csv", help="raw labeled sensor CSV")
    parser.add_argument("--model", default="model.pkl", help="output model bundle")
    args = parser.parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        raise SystemExit(f"{data_path} not found. Run python simulate_transformer_data.py first.")
    train_model(pd.read_csv(data_path), args.model)


if __name__ == "__main__":
    main()

"""Generate deterministic synthetic transformer sensor data for demos and tests.

This is a software simulation, not a connection to transformer hardware.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

FAULT_LABELS = {
    "Normal": 0,
    "Overcurrent": 1,
    "Overtemperature": 2,
    "Overcurrent + Overtemperature": 3,
    "Short Circuit": 4,
}


def generate_sensor_data(rows: int = 960, seed: int = 42) -> pd.DataFrame:
    """Return reproducible simulated measurements with an imbalanced fault mix."""
    if rows < len(FAULT_LABELS):
        raise ValueError(f"rows must be at least {len(FAULT_LABELS)}")
    rng = np.random.default_rng(seed)
    names = np.array(list(FAULT_LABELS))
    probabilities = np.array([0.78, 0.08, 0.07, 0.04, 0.03])
    labels = rng.choice(names, size=rows, p=probabilities)
    readings = []

    for i, label in enumerate(labels):
        voltage = rng.normal(415, 7)
        current = rng.normal(78, 12)
        temperature = rng.normal(40, 6)
        if label == "Overcurrent":
            current, temperature = rng.normal(122, 8), rng.normal(45, 6)
        elif label == "Overtemperature":
            current, temperature = rng.normal(78, 12), rng.normal(72, 5)
        elif label == "Overcurrent + Overtemperature":
            current, temperature = rng.normal(125, 8), rng.normal(74, 5)
        elif label == "Short Circuit":
            voltage, current, temperature = rng.normal(350, 10), rng.normal(145, 12), rng.normal(48, 7)
        readings.append((f"ST{i % 10 + 1:02d}", label, voltage, current, temperature))

    timestamps = pd.date_range("2025-01-01", periods=rows, freq="15min")
    df = pd.DataFrame(readings, columns=["Station_ID", "Fault_Status", "Voltage_V", "Current_A", "Temperature_C"])
    df.insert(1, "Timestamp", timestamps)
    df["Power_kW"] = (df["Voltage_V"] * df["Current_A"] / 1000).round(2)
    for column in ("Voltage_V", "Current_A", "Temperature_C"):
        df[column] = df[column].round(2)
    return df[["Station_ID", "Timestamp", "Voltage_V", "Current_A", "Temperature_C", "Power_kW", "Fault_Status"]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="transformer_data.csv", help="CSV output path")
    parser.add_argument("--rows", type=int, default=960, help="number of simulated readings")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    args = parser.parse_args()
    data = generate_sensor_data(args.rows, args.seed)
    output = Path(args.output)
    data.to_csv(output, index=False)
    print(f"Saved {len(data)} simulated readings to {output}")
    print("Class counts:\n" + data["Fault_Status"].value_counts().to_string())
    print("Synthetic data only; no hardware was read.")


if __name__ == "__main__":
    main()

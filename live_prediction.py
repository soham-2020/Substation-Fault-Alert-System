"""Run model-backed predictions on simulated readings and optionally alert via Telegram.

This script simulates readings; it does not monitor or control real substation equipment.
"""
from __future__ import annotations

import argparse
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd

from simulate_transformer_data import FAULT_LABELS
from train_fault_model import FEATURE_COLUMNS

CRITICAL_LABELS = {"Overtemperature", "Overcurrent + Overtemperature", "Short Circuit"}


def load_local_env(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE entries without replacing existing environment values."""
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_model_bundle(model_path: str | Path = "model.pkl") -> dict:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. Run python train_fault_model.py first.")
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "model" not in bundle or "label_mapping" not in bundle:
        raise ValueError("Model file must be a model bundle created by train_fault_model.py")
    if bundle["label_mapping"] != FAULT_LABELS:
        raise ValueError("Model label mapping does not match this project's fault labels")
    return bundle


def predict_reading(bundle: dict, voltage: float, current: float, temperature: float) -> tuple[int, str]:
    row = pd.DataFrame([[voltage, current, temperature]], columns=bundle["feature_columns"])
    predicted_code = int(bundle["model"].predict(row)[0])
    reverse_mapping = {code: label for label, code in bundle["label_mapping"].items()}
    if predicted_code not in reverse_mapping:
        raise ValueError(f"Model returned unknown class code: {predicted_code}")
    return predicted_code, reverse_mapping[predicted_code]


def send_telegram_alert(message: str) -> bool:
    """Send only when both credentials are configured in the environment."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram alert skipped: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable it.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        if not 200 <= response.status < 300:
            raise RuntimeError(f"Telegram API returned HTTP {response.status}")
        return True


def append_prediction(path: str | Path, row: dict) -> None:
    output = Path(path)
    pd.DataFrame([row]).to_csv(output, mode="a", header=not output.exists(), index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="model.pkl")
    parser.add_argument("--output", default="live_predictions.csv")
    parser.add_argument("--interval", type=float, default=15, help="seconds between simulated readings")
    parser.add_argument("--once", action="store_true", help="generate one reading and exit")
    args = parser.parse_args()
    load_local_env()
    bundle = load_model_bundle(args.model)
    print("SIMULATION MODE: readings are generated in software; no hardware is connected.")
    while True:
        # Keep sample ranges broad; the trained model, not these ranges, decides the label.
        voltage = round(380 + (time.time() % 1) * 60, 2)
        current = round(50 + ((time.time() * 7) % 1) * 80, 2)
        temperature = round(20 + ((time.time() * 13) % 1) * 65, 2)
        code, label = predict_reading(bundle, voltage, current, temperature)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        append_prediction(args.output, {
            "Timestamp": timestamp, "Voltage_V": voltage, "Current_A": current,
            "Temperature_C": temperature, "Pred_Label": code, "Pred_Fault_Status": label,
            "Operation_Mode": "simulation",
        })
        print(f"[{timestamp}] V={voltage} V I={current} A T={temperature} °C -> {code}: {label}")
        if label in CRITICAL_LABELS:
            alert = f"SIMULATED transformer fault at {timestamp}: {label} (model prediction)"
            print(alert)
            send_telegram_alert(alert)
        if args.once:
            break
        time.sleep(max(0, args.interval))


if __name__ == "__main__":
    main()

# Substation Fault Alert System

A Python demonstration of transformer fault classification using a Random Forest, generated sensor data, optional Telegram notifications, and an Excel dashboard.

> **Simulation scope:** the supplied data and live readings are generated in software. This repository does not connect to transformer sensors, a PLC, SCADA, or protection equipment. Predictions and alerts are for demonstration only and must not be used for operational or safety decisions.

## Pipeline

1. `simulate_transformer_data.py` creates a reproducible, intentionally imbalanced synthetic dataset (`transformer_data.csv`).
2. `train_fault_model.py` splits original rows into a stratified training set and untouched test set, then upsamples only the training set. Evaluation therefore uses original, non-duplicated holdout rows.
3. The trainer saves `model.pkl`, a bundle containing the fitted Random Forest, feature order, and label map.
4. `live_prediction.py` loads that bundle and calls the model for each simulated reading. It logs both the numeric code and text label in `live_predictions.csv`. It never uses hand-written rules to choose predictions.
5. Telegram messages are optional and require credentials supplied through environment variables or a local `.env` file. The Excel dashboard can read the prediction CSV.

## Fault label map

These IDs are fixed in the simulator, training bundle, live output, and documentation. They are not assigned alphabetically by an encoder.

| Code | Fault label |
|---:|---|
| 0 | Normal |
| 1 | Overcurrent |
| 2 | Overtemperature |
| 3 | Overcurrent + Overtemperature |
| 4 | Short Circuit |

## Setup and run

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python simulate_transformer_data.py --rows 960 --seed 42
python train_fault_model.py --data transformer_data.csv --model model.pkl
python live_prediction.py --model model.pkl --output live_predictions.csv --once
```

Remove `--once` to continue generating a reading every 15 seconds. Change the cadence with `--interval 30`. Every live reading is simulated; this script does not acquire real sensor measurements.

To create data with a different seed or size:

```bash
python simulate_transformer_data.py --rows 2000 --seed 123 --output transformer_data.csv
```

## Telegram configuration

1. Create a bot with Telegram's `@BotFather` and obtain a bot token and chat ID.
2. Copy `.env.example` to `.env`, then set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
3. Keep `.env` private. It is excluded by `.gitignore`; never paste credentials into source code or commit them.
4. Run `python TEST_FOR_TELEGRAM.py` to send an explicitly labeled test message. Live prediction sends alerts only for model predictions of Overtemperature, combined Overcurrent + Overtemperature, or Short Circuit. Messages say they are simulated predictions.

When credentials are absent, Telegram delivery is skipped and predictions are still logged. Telegram requests use HTTPS, a timeout, and HTTP error checking.

## Excel dashboard

`PIVOT_TABLE.xlsm` is a demonstration dashboard. Open it in desktop Excel and refresh its data connection to `live_predictions.csv`. Excel/VBA refresh behavior depends on the local workbook configuration. The CSV now includes `Pred_Fault_Status` and `Operation_Mode` alongside `Pred_Label`; use the text label for a readable chart.

## Reproducible validation

```bash
python -m unittest tests_pipeline -v
```

The tests use deterministic simulated data and temporary model files. GitHub Actions runs the tests and a one-reading simulated end-to-end smoke test on pushes and pull requests. The trained model is intentionally not committed: regenerate it from the documented command so the data split, training, evaluation, and bundle are reproducible.

## Files

| File | Purpose |
|---|---|
| `simulate_transformer_data.py` | Deterministic synthetic readings with stable labels |
| `train_fault_model.py` | Train-only upsampling, holdout evaluation, and model bundle export |
| `live_prediction.py` | Model-backed simulated inference, CSV logging, optional alerts |
| `TEST_FOR_TELEGRAM.py` | Optional credential-based test message |
| `.env.example` | Credential variable names without secrets |
| `tests_pipeline.py` | Simulation, leakage-sequence, and model-mapping tests |
| `.github/workflows/tests.yml` | CI test and simulated smoke test |
| `PIVOT_TABLE.xlsm` | Excel dashboard artifact |

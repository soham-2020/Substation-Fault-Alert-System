# Substation-Fault-Alert-System

A real-time transformer fault detection system using machine learning and Python, integrated with a live Excel dashboard and Telegram alerts.

---

## Overview

This project implements a complete end-to-end real-time fault prediction system for electrical substations. It simulates realistic sensor data, uses machine learning to classify faults, and provides alerts through Telegram. It also integrates with Microsoft Excel to visualize fault data in real time.

---

## Features

- ✅ **Synthetic data generation** of voltage, current, temperature
- ✅ **Custom fault logic** for Overcurrent, Overtemperature, Short Circuit, and combinations
- ✅ **Data balancing** using upsampling to handle imbalanced classes
- ✅ **ML model training** using Random Forest to classify fault types
- ✅ **Real-time prediction engine** simulating continuous transformer readings
- ✅ **Telegram alert bot** for critical faults
- ✅ **Live-updating Excel dashboard** with Pivot Charts and auto-refresh every 2 minutes

---

## Project Pipeline

### 1. Data Simulation (`simulate_ev_data.py`)
- Simulates readings for 10 transformer stations at 15-minute intervals for 24 hours.
- Applies logical conditions to classify data as:
  - Normal
  - Overcurrent
  - Overtemperature
  - Overcurrent + Overtemperature
  - Short Circuit

### 2. Fault Balancing (`balance_fault_data.py`)
- Balances the dataset by upsampling minority fault classes to prevent model bias.

### 3. Model Training (`train_fault_model.py`)
- Trains a Random Forest classifier using voltage, current, and temperature as features.
- Encodes fault labels and saves the trained model as `model.pkl`.

### 4. Live Prediction and Logging (`live_prediction.py`)
- Simulates real-time readings.
- Loads the trained model and makes predictions.
- Appends results to `live_predictions.csv`.
- Sends **Telegram alerts** for Overtemperature or Short Circuit events.

### 5. Alert System (`TEST_FOR_TELEGRAM.py`)
- Standalone script to verify Telegram bot integration using a test message.
- Uses Bot API and chat ID linked to the developer’s phone.

---

## Excel Dashboard (`PIVOT_TABLE.xlsm`)

- Connected to `live_predictions.csv` using Power Query.
- Auto-refreshes every 2 minutes using VBA macros.
- Displays:
  - Count of each fault type
  - Pivot chart updated in real-time
  - Clean and readable transformer health stats

---

## File Summary

| File | Purpose |
|------|---------|
| `simulate_ev_data.py` | Simulates and labels transformer sensor data |
| `balance_fault_data.py` | Upsamples minority fault classes |
| `train_fault_model.py` | Trains and exports the Random Forest model |
| `live_prediction.py` | Real-time simulation + prediction + logging + alerting |
| `TEST_FOR_TELEGRAM.py` | Verifies Telegram alert delivery |
| `live_predictions.csv` | Stores prediction output for Excel dashboard |
| `PIVOT_TABLE.xlsm` | Excel dashboard with auto-refresh and pivot charts |

---

## Fault Label Map

| Code | Label |
|------|-------|
| 0 | Normal |
| 1 | Overcurrent |
| 2 | Overtemperature |
| 3 | Overcurrent + Overtemperature |
| 4 | Short Circuit |

---

## Tech Stack

- **Python 3.10+**
- pandas, numpy, scikit-learn, joblib, requests
- Microsoft Excel with VBA macros
- Telegram Bot API

---

## Telegram Bot Integration

- A functional Telegram bot is integrated and tested.
- It sends **real-time fault alerts directly to the developer’s phone**.
- This ensures high visibility for critical faults like overtemperature or short circuit.

---

## How to Run

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install pandas scikit-learn requests joblib

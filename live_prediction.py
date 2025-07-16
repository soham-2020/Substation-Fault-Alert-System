import pandas as pd
import time
from datetime import datetime
import random
import requests

# --- Telegram Alert Function ---
def send_telegram_alert(message):
    bot_token = "7950715421:AAE_jUOUwTpXCYXatlHAI_k-LBa1g_Xt_Po"
    chat_id = "1887823793"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.get(url, params=payload)
    except:
        print("Could not send Telegram message.")

# --- Path to Output CSV ---
output_file = "live_predictions.csv"

# --- Start Live Simulation ---
while True:
    # Simulate sensor values
    voltage = round(random.uniform(380, 440), 2)
    current = round(random.uniform(50, 100), 2)
    temp = round(random.uniform(20, 80), 2)

    # Predict faults
    if temp > 65 and current > 90:
        prediction = 3  # Overcurrent + Overtemp
    elif temp > 65:
        prediction = 2  # Overtemperature
    elif current > 90:
        prediction = 1  # Overcurrent
    elif voltage < 390:
        prediction = 4  # Short Circuit
    else:
        prediction = 0  # Normal

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save prediction to CSV
    new_row = pd.DataFrame([[timestamp, voltage, current, temp, prediction]],
                           columns=["Timestamp", "Voltage_V", "Current_A", "Temperature_C", "Pred_Label"])
    new_row.to_csv(output_file, mode='a', header=False, index=False)

    # Print to console
    print(f"[{timestamp}] V={voltage}V  I={current}A  T={temp}°C → Fault: {prediction}")

    # Trigger alerts
    if prediction in [2, 3, 4]:
        alert_msg = f"FAULT at {timestamp}\n"
        if prediction == 2:
            alert_msg += "Overtemperature detected!"
        elif prediction == 4:
            alert_msg += "Short Circuit detected!"
        elif prediction == 3:
            alert_msg += "Overcurrent + Overtemp detected!"
        print(alert_msg)
        send_telegram_alert(alert_msg)

    # Wait before next reading
    time.sleep(15)


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Simulation settings
num_stations = 10
interval_minutes = 15
total_intervals = 24 * 60 // interval_minutes
base_time = datetime(2025, 7, 16, 0, 0)

stations = [f"ST{str(i).zfill(2)}" for i in range(1, num_stations + 1)]

data = []

for station in stations:
    for i in range(total_intervals):
        timestamp = base_time + timedelta(minutes=i * interval_minutes)

        # Simulate readings
        voltage = round(np.random.normal(415, 10), 2)
        current = round(np.random.normal(80, 15), 2)
        temp = round(np.random.normal(40, 8), 2)
        power = round((voltage * current) / 1000, 2)

        # Fault Logic
        if current > 110 and temp > 60:
            fault = "Overcurrent + Overtemp"
        elif current > 110:
            fault = "Overcurrent"
        elif temp > 60:
            fault = "Overtemp"
        elif np.random.rand() < 0.01:  # 1% chance of short-circuit
            fault = "Short Circuit"
        else:
            fault = "Normal"

        data.append([station, timestamp, voltage, current, temp, power, fault])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "Station_ID", "Timestamp", "Voltage_V", "Current_A",
    "Temperature_C", "Power_kW", "Fault_Status"
])

# Save to CSV
df.to_csv("ev_charging_data.csv", index=False)
print("✅ Data simulation complete. Saved as 'ev_charging_data.csv'")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("ev_charging_data.csv")

# Basic Info
print(df.head())
print("\n🔍 Unique Faults:", df['Fault_Status'].unique())
print("\n📊 Class Distribution:\n", df['Fault_Status'].value_counts())

sns.countplot(data=df, x='Fault_Status')
plt.title("Fault Type Distribution")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Current_A', y='Temperature_C', hue='Fault_Status', palette='tab10')
plt.title("Current vs Temperature (Fault Pattern)")
plt.show()

from sklearn.preprocessing import LabelEncoder

# Drop unnecessary columns for ML
df_ml = df.drop(columns=["Station_ID", "Timestamp"])

# Encode Fault Status to numeric
label_encoder = LabelEncoder()
df_ml['Fault_Label'] = label_encoder.fit_transform(df_ml['Fault_Status'])

# Save mapping for later use
label_map = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
print("🔢 Label Mapping:", label_map)

# Drop original Fault_Status
df_ml = df_ml.drop(columns=["Fault_Status"])

# Save clean version
df_ml.to_csv("ev_charging_clean.csv", index=False)
print("✅ Preprocessed data saved as 'ev_charging_clean.csv'")

from sklearn.utils import resample

# Separate majority and minority
df_majority = df[df.Fault_Status == "Normal"]
df_minority = df[df.Fault_Status != "Normal"]

# Upsample minority class
df_minority_upsampled = resample(df_minority,
                                 replace=True,
                                 n_samples=len(df_majority),
                                 random_state=42)

# Combine back
df_balanced = pd.concat([df_majority, df_minority_upsampled])
print("✅ New Class Distribution:\n", df_balanced['Fault_Status'].value_counts())

# Save balanced version
df_balanced.to_csv("ev_charging_balanced.csv", index=False)



import pandas as pd
from sklearn.utils import resample

# Load original dataset
df = pd.read_csv("ev_charging_data.csv")

# Separate majority and minority classes
df_majority = df[df['Fault_Status'] == "Normal"]
df_minority = df[df['Fault_Status'] != "Normal"]

# Upsample minority
df_minority_upsampled = resample(df_minority,
                                 replace=True,
                                 n_samples=len(df_majority),
                                 random_state=42)

# Combine and shuffle
df_balanced = pd.concat([df_majority, df_minority_upsampled]).sample(frac=1, random_state=42)

# Save to CSV
df_balanced.to_csv("ev_charging_balanced.csv", index=False)
print("Balanced dataset saved as 'ev_charging_balanced.csv'")


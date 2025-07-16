import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib

# Load balanced dataset
df = pd.read_csv("ev_charging_balanced.csv")

# Drop unnecessary columns (optional)
df = df.drop(columns=["Station_ID", "Timestamp", "Power_kW"])

# Encode fault labels
le = LabelEncoder()
df['Fault_Label'] = le.fit_transform(df['Fault_Status'])

# Save label mapping for reference (optional)
print("🔢 Label Map:", dict(zip(le.classes_, le.transform(le.classes_))))

# Feature selection
X = df[["Voltage_V", "Current_A", "Temperature_C"]]
y = df["Fault_Label"]

# Split for training/testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("📊 Classification Report:\n", classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "model.pkl")
print("✅ Model saved as model.pkl")


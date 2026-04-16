import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle
from datetime import datetime

print("="*50)
print("WEATHER PREDICTION MODEL - TRAINING")
print("="*50)

# Tumhari CSV file (agar hai to use karo)
csv_file = "weather.csv"

try:
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded: {len(df)} rows from {csv_file}")
except:
    print("⚠️ CSV nahi mili, sample data bana raha hun...")
    # 30 days of hourly data (720 hours)
    dates = pd.date_range(start='2024-01-01', periods=720, freq='h')
    df = pd.DataFrame({
        'date': dates,
        'temperature': 25 + 10 * np.sin(np.arange(720)/100) + np.random.normal(0, 2, 720),
        'humidity': 60 + 15 * np.sin(np.arange(720)/200) + np.random.normal(0, 8, 720),
        'wind_speed': np.random.uniform(0, 25, 720),
        'pressure': 1013 + np.random.normal(0, 6, 720)
    })
    print(f"✅ Sample data banaya: {len(df)} rows")

# Time features
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['date'].dt.hour
df['day'] = df['date'].dt.day
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek

# Features for prediction
features = ['hour', 'day', 'month', 'dayofweek', 'humidity', 'wind_speed', 'pressure']
X = df[features].fillna(0)
y = df['temperature'].fillna(0)

# Train model
print("\n🔄 Training Random Forest model...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\n✅ Model trained successfully!")
print(f"✅ Features used: {features}")
print("✅ Model saved as model.pkl")
print("="*50)
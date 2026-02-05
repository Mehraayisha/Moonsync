import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# Load dataset
df = pd.read_csv("ml/fed_cycle_data.csv")

features = [
    "Age",
    "BMI",
    "LengthofMenses",
    "LengthofLutealPhase",
    "TotalMensesScore",
    "EstimatedDayofOvulation"
]
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

target = "LengthofCycle"

# Keep only needed columns
df = df[features + [target]]

# Replace blank spaces with NaN
df.replace(" ", np.nan, inplace=True)

# Convert everything to numeric (force errors to NaN)
df = df.apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values
df = df.dropna()

X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

print("Mean Absolute Error:", mae)

# Save model
joblib.dump(model, "ml/model.pkl")

print("Model saved successfully.")

import joblib
import numpy as np
import os
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml", "model.pkl")

model = joblib.load(MODEL_PATH)

def predict_cycle_length(age, bmi, menses_length, luteal_length, total_score, ovulation_day):
    features = np.array([[age, bmi, menses_length, luteal_length, total_score, ovulation_day]])
    prediction = model.predict(features)
    return round(prediction[0])

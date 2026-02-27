import joblib
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import MODEL_PATHS, SENSOR_FEATURES

from database.data_access import (
    save_failure_prediction,
    save_rul_prediction,
    save_priority 
)

# Load models
failure_model = joblib.load(MODEL_PATHS["failure"])
rul_model = joblib.load(MODEL_PATHS["rul"])
priority_model = joblib.load(MODEL_PATHS["priority"])
scaler = joblib.load(MODEL_PATHS["scaler"])

def calculate_rul_from_probability(probability):
    """
    Calculate realistic RUL based on failure probability.
    This ensures consistency between probability and RUL predictions.
    """
    if probability < 0.2:
        return 180 
    elif probability < 0.4:
        return 90   
    elif probability < 0.6:
        return 45   
    elif probability < 0.8:
        return 14   
    else:
        return 5    

def run_prediction(machine_id, reading_id, input_data):
    try:
        
        X = np.array([input_data[feature] for feature in SENSOR_FEATURES]).reshape(1, -1)
        X_scaled = scaler.transform(X)

        # 1. Failure Prediction
        will_fail = int(failure_model.predict(X_scaled)[0])
        
        proba = failure_model.predict_proba(X_scaled)
        if len(proba.shape) == 2:
            probability = float(proba[0][1])
        else:
            probability = float(proba[0])
        
        print(f"Failure prediction: will_fail={will_fail}, probability={probability:.3f}")
        save_failure_prediction(machine_id, reading_id, will_fail, probability)

        # 2. RUL Prediction 
        
        ml_days = float(rul_model.predict(X_scaled)[0])
        rule_days = calculate_rul_from_probability(probability)
        
        
        days_remaining = (0.7 * rule_days) + (0.3 * max(0, ml_days))
        days_remaining = max(1, days_remaining)  
        
        print(f"RUL prediction: ml={ml_days:.1f}, rule={rule_days:.1f}, final={days_remaining:.1f}")
        save_rul_prediction(machine_id, reading_id, days_remaining)

    
        priority_idx = int(priority_model.predict(X_scaled)[0])
        priority_map = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
        label = priority_map.get(priority_idx, "Low")
        
        print(f"Priority prediction: idx={priority_idx}, label={label}")
        save_priority(machine_id, label, probability * 100)

        return {
            "will_fail": will_fail,
            "failure_probability": probability,
            "days_until_failure": days_remaining,
            "priority": label
        }
    
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return None
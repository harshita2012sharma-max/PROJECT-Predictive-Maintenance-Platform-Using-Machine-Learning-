import sys
import os
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.data_loader import load_data
from training.preprocessor import preprocess
from training.evaluate import evaluate_classification, evaluate_regression
from models.failure_model import FailureModel
from models.rul_model import RULModel
from models.priority_model import PriorityModel
from config.config import FAILURE_CONFIG, RUL_CONFIG, PRIORITY_CONFIG, MODEL_PATHS

def train_models():
    # Load data
    df = load_data()
    if df.empty:
        print("No data found! Exiting...")
        return
    print(f"Loaded {len(df)} samples")

    # MODEL 1: FAILURE PREDICTION
    X_train, X_test, y_train, y_test, scaler = preprocess(
        df, 
        FAILURE_CONFIG["target"], 
        FAILURE_CONFIG["test_size"], 
        FAILURE_CONFIG["random_state"]
    )
    
    f_model = FailureModel()
    f_model.train(X_train, y_train)
    evaluate_classification(f_model.model, X_test, y_test, "Failure Model")  # ✅ .model added

    # MODEL 2: RUL PREDICTION
    X_train, X_test, y_train, y_test, _ = preprocess(
        df, 
        RUL_CONFIG["target"], 
        RUL_CONFIG["test_size"], 
        RUL_CONFIG["random_state"]
    )
    
    r_model = RULModel()
    r_model.train(X_train, y_train)
    evaluate_regression(r_model.model, X_test, y_test, "RUL Model")  # ✅ .model added

    # MODEL 3: PRIORITY CLASSIFICATION
    X_train, X_test, y_train, y_test, _ = preprocess(
        df, 
        PRIORITY_CONFIG["target"], 
        PRIORITY_CONFIG["test_size"], 
        PRIORITY_CONFIG["random_state"]
    )
    
    p_model = PriorityModel()
    p_model.train(X_train, y_train)
    evaluate_classification(p_model.model, X_test, y_test, "Priority Model")  # ✅ .model added

    # SAVE ALL MODELS
    os.makedirs("saved_models", exist_ok=True)
    
    joblib.dump(f_model, MODEL_PATHS["failure"])
    print(f"Saved: {MODEL_PATHS['failure']}")
    
    joblib.dump(r_model, MODEL_PATHS["rul"])
    print(f"Saved: {MODEL_PATHS['rul']}")
    
    joblib.dump(p_model, MODEL_PATHS["priority"])
    print(f"Saved: {MODEL_PATHS['priority']}")
    
    joblib.dump(scaler, MODEL_PATHS["scaler"])
    print(f"Saved: {MODEL_PATHS['scaler']}")

    print("ALL MODELS TRAINED SUCCESSFULLY!")

if __name__ == "__main__":
    train_models()
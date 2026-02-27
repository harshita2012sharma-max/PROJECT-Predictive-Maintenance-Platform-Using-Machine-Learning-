from sklearn.metrics import accuracy_score, mean_absolute_error

def evaluate_classification(model, X_test, y_test, model_name="Model"):
    
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    
    print(f"{model_name} Accuracy: {acc:.4f}")

def evaluate_regression(model, X_test, y_test, model_name="Model"):
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"{model_name} MAE: {mae:.4f} days")
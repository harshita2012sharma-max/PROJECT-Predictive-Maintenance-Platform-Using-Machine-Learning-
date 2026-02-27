from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from config.config import SENSOR_FEATURES

def preprocess(df, target_column, test_size, random_state):
    # Ensure we only use the features defined in config
    X = df[SENSOR_FEATURES]
    y = df[target_column]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, 
        y, 
        test_size=test_size, 
        random_state=random_state
    )

    return X_train, X_test, y_train, y_test, scaler
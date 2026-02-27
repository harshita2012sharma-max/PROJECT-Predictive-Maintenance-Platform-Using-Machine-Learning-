from sklearn.ensemble import RandomForestRegressor

class RULModel:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=None,
            random_state=42,
            n_jobs=-1
        )

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
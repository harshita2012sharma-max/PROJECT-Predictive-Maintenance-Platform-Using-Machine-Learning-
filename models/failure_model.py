from sklearn.ensemble import RandomForestClassifier

class FailureModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=42,
            class_weight='balanced'
        )

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]
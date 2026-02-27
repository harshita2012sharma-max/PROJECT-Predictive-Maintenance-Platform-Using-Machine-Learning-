from sklearn.tree import DecisionTreeClassifier

class PriorityModel:
    def __init__(self):
        self.model = DecisionTreeClassifier(
            max_depth=6,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42
        )

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
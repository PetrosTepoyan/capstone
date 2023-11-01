import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.model_selection import train_test_split

class ModelReporter:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
    def evaluate(self, model, model_name=None, is_classification=True):
        if model_name:
            print(f"Evaluating {model_name}...")
        else:
            print(f"Evaluating {model}...")
            
        # Train the model
        model.fit(self.X_train, self.y_train)
        
        # Predictions
        y_pred = model.predict(self.X_test)
        
        # Metrics calculation
        if is_classification:
            acc = accuracy_score(self.y_test, y_pred)
            print(f"Accuracy: {acc:.4f}")
            
        else:  # Regression
            mse = mean_squared_error(self.y_test, y_pred)
            print(f"Mean Squared Error: {mse:.4f}")

            # Visualize predictions vs actuals for regression
            plt.scatter(self.y_test, y_pred, alpha=0.5)
            plt.xlabel('Actual')
            plt.ylabel('Predicted')
            plt.title('Actual vs Predicted')
            plt.show()
            
        # Basic Logging
        print(f"Model {model_name if model_name else model} evaluated successfully.\n{'-'*50}")

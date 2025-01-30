# regime_info/regime_classifier.py
from utils.logger import logger
import pandas as pd
from sklearn.ensemble import RandomForestClassifier  # Example ML model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib # To save and load the trained model

class RegimeClassifier:
    def __init__(self, model_type="random_forest", model_path="trained_model.pkl"):
        self.model_type = model_type
        self.model_path = model_path
        if self.model_type == "random_forest":
            self.model = RandomForestClassifier()
        # Add more model types as needed (e.g., "svm", "lstm", etc.)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        self.load_model() # Attempt to load a trained model when initializing

    def train(self, features_df, labels):
        """
        Trains the ML model on the given features and labels.
        Args:
            features_df (pd.DataFrame): DataFrame containing the features (e.g., technical indicators, macro data).
            labels (pd.Series): Series containing the corresponding regime labels (e.g., "bull", "bear", "sideways").
        """
        logger.info(f"Training {self.model_type} model...")

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(features_df, labels, test_size=0.2, random_state=42)

        # Train the model
        self.model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.4f}")

        self.save_model() # Save the trained model
        logger.info(f"Model trained and saved to {self.model_path}")

    def predict(self, features_df):
        """
        Predicts the market regime for the given features.
        Args:
            features_df (pd.DataFrame): DataFrame containing the features.
        Returns:
            np.ndarray: Array of predicted regime labels.
        """
        if self.model is None:
            logger.error("Model not loaded. Cannot make predictions.")
            return None
        try:
            logger.info(f"Predicting regime with the model...")
            predictions = self.model.predict(features_df)
            logger.info(f"Model predicted regimes")
            return predictions
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None

    def save_model(self):
        """Saves the trained model to disk."""
        try:
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Loads a trained model from disk."""
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}. Model will be trained from scratch if train() is called.")
            self.model = None # Reset to None if loading fails

    def classify_regime_sma_crossover(self, close_prices, short_window=50, long_window=200):
        """
        Classifies the market regime based on SMA crossover.
        Args:
            close_prices (pd.Series): Series of closing prices.
            short_window (int): Window for the short SMA.
            long_window (int): Window for the long SMA.
        Returns:
            str: Predicted regime ("bull", "bear", or "sideways").
        """
        if len(close_prices) < max(short_window, long_window):
            logger.warning("Not enough data points to calculate SMAs. Defaulting to 'sideways'.")
            return "sideways"
        short_sma = close_prices.rolling(window=short_window).mean()
        long_sma = close_prices.rolling(window=long_window).mean()
        # Determine the regime based on the last values
        if short_sma.iloc[-1] > long_sma.iloc[-1]:
            return "bull"
        elif short_sma.iloc[-1] < long_sma.iloc[-1]:
            return "bear"
        else:
            return "sideways"

# Example usage (you'll need to adapt this to your data)
if __name__ == '__main__':
    # Create dummy data for demonstration
    data = {
        'SMA50': [50, 51, 52, 53, 54, 55, 54, 53, 52, 51],
        'SMA200': [200, 199, 198, 197, 196, 195, 196, 197, 198, 199],
        'CPI': [2, 2.1, 2.2, 2.3, 2.4, 2.3, 2.2, 2.1, 2, 1.9],
        'Regime': ['sideways', 'bull', 'bull', 'bull', 'bull', 'bear', 'bear', 'bear', 'sideways', 'sideways']
    }
    df = pd.DataFrame(data)

    # Prepare features and labels
    features = df[['SMA50', 'SMA200', 'CPI']]
    labels = df['Regime']

    # Initialize and train the classifier
    classifier = RegimeClassifier(model_type="random_forest")
    classifier.train(features, labels)

    # Make predictions
    predictions = classifier.predict(features)
    print("Predictions:", predictions)
# src/forecast_model.py
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import joblib

class SimpleLSTMForecaster(nn.Module):
    """Simple LSTM-based forecaster for time series prediction"""
    def __init__(self, input_size=1, hidden_size=32, num_layers=2, output_size=7):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class ForecastModel:
    def __init__(self):
        self.model = SimpleLSTMForecaster()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def train(self, price_data: List[float], epochs: int = 10) -> None:
        try:
            if len(price_data) < 14:
                raise ValueError(f"Need at least 14 price points, got {len(price_data)}")

            # Fit scaler on training data
            self.scaler.fit(np.array(price_data).reshape(-1, 1))

            # Prepare sequences: use last 7 days to predict next 7 days
            sequences = []
            targets = []

            for i in range(len(price_data) - 13):  # Need 14 points total (7 input + 7 target)
                seq = price_data[i:i+7]
                tgt = price_data[i+7:i+14]
                if len(seq) == 7 and len(tgt) == 7:
                    sequences.append(seq)
                    targets.append(tgt)

            if not sequences:
                raise ValueError("Not enough valid sequences for training")

            # Convert to tensors and scale
            X = torch.tensor(sequences, dtype=torch.float32).unsqueeze(-1).to(self.device)
            y = torch.tensor(targets, dtype=torch.float32).to(self.device)

            # Training loop
            self.model.train()
            for epoch in range(epochs):
                self.optimizer.zero_grad()
                outputs = self.model(X)
                loss = self.criterion(outputs, y)
                loss.backward()
                self.optimizer.step()

            self.is_trained = True

        except Exception as e:
            print(f"Error training model: {str(e)}")
            raise

    def predict_price(self, price_data: List[float]) -> Dict:
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before prediction")

            if len(price_data) < 7:
                raise ValueError(f"Need at least 7 price points for prediction, got {len(price_data)}")

            # Use last 7 days for prediction
            scaled_input = self.scaler.transform(np.array(price_data[-7:]).reshape(-1, 1)).flatten()
            input_data = torch.tensor(scaled_input, dtype=torch.float32).unsqueeze(0).unsqueeze(-1).to(self.device)

            self.model.eval()
            with torch.no_grad():
                scaled_predictions = self.model(input_data).squeeze().cpu().numpy()

            # Inverse transform predictions back to original scale
            predictions = self.scaler.inverse_transform(scaled_predictions.reshape(-1, 1)).flatten()

            # Calculate trend based on recent price movement
            recent_prices = np.array(price_data[-7:])
            trend = "stable"
            if len(recent_prices) >= 2:
                slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
                if slope > 1.0:
                    trend = "bullish"
                elif slope < -1.0:
                    trend = "bearish"

            return {
                "predictions": [{"predicted_price": float(p)} for p in predictions],
                "trend": trend,
                "confidence": 0.75,
                "model_type": "LSTM"
            }

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            raise

    def prepare_features(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features from historical price data."""
        if not historical_data:
            raise ValueError("Historical data cannot be empty")

        prices = np.array([d['price'] for d in historical_data])
        # Create 5 features: price, price^2, sin(price), cos(price), log(price)
        X = np.column_stack([
            prices,
            prices ** 2,
            np.sin(prices / 100),  # normalize
            np.cos(prices / 100),
            np.log(prices + 1)  # +1 to avoid log(0)
        ])
        y = prices
        return X, y

    def calculate_price_trend(self, historical_data: List[Dict]) -> Dict:
        """Calculate the price trend from historical data."""
        if len(historical_data) < 2:
            raise ValueError("Insufficient data to calculate trend")
        prices = [item['price'] for item in historical_data]
        X = np.arange(len(prices)).reshape(-1, 1)
        y = np.array(prices)
        model = LinearRegression()
        model.fit(X, y)

        # Calculate volatility (standard deviation of price changes)
        price_changes = np.diff(prices)
        volatility = np.std(price_changes) if len(price_changes) > 0 else 0

        return {"trend": model.coef_[0], "slope": model.coef_[0], "volatility": volatility}

    def save_model(self, filepath: str = 'forecast_model.pkl') -> None:
        """Save the model and scaler to a file."""
        joblib.dump(self.model, filepath.replace('.pkl', '_model.pkl'))
        joblib.dump(self.scaler, filepath.replace('.pkl', '_scaler.pkl'))

    def load_model(self, filepath: str = 'forecast_model.pkl') -> None:
        """Load the model and scaler from a file."""
        self.model = joblib.load(filepath.replace('.pkl', '_model.pkl'))
        self.scaler = joblib.load(filepath.replace('.pkl', '_scaler.pkl'))
        self.is_trained = True

import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import List
from src.price_fetcher import BTCPriceFetcher

# Assuming BTCPriceFetcher is already defined and implemented as before

class BTCPricePredictor:
    def __init__(self, seq_length: int = 30, epochs: int = 20, batch_size: int = 32):
        self.seq_length = seq_length
        self.epochs = epochs
        self.batch_size = batch_size
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = self._build_model()
        self.data_scaled = None
        self.dates = []
        self.prices = []

    def _build_model(self) -> tf.keras.Sequential:
        """Builds and compiles the LSTM model."""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(self.seq_length, 1)),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def preprocess_data(self, prices: List[float]) -> None:
        """Scales and prepares price data for model training."""
        self.data_scaled = self.scaler.fit_transform(np.array(prices).reshape(-1, 1))
        self.prices = prices

    def create_sequences(self) -> (np.ndarray, np.ndarray):
        """Creates sequences for training the LSTM model."""
        x, y = [], []
        for i in range(len(self.data_scaled) - self.seq_length):
            x.append(self.data_scaled[i:i + self.seq_length])
            y.append(self.data_scaled[i + self.seq_length])
        return np.array(x), np.array(y)

    def train(self, x_train: np.ndarray, y_train: np.ndarray, x_val: np.ndarray, y_val: np.ndarray) -> None:
        """Trains the LSTM model."""
        self.model.fit(x_train, y_train, epochs=self.epochs, batch_size=self.batch_size, validation_data=(x_val, y_val))

    def forecast(self, forecast_days: int) -> List[float]:
        """Forecasts future prices for the specified number of days."""
        input_seq = self.data_scaled[-self.seq_length:]  # Start with the last known sequence
        predictions = []

        for _ in range(forecast_days):
            pred = self.model.predict(input_seq.reshape(1, self.seq_length, 1))
            predictions.append(pred[0, 0])
            input_seq = np.append(input_seq[1:], pred[0, 0])  # Slide the window

        return self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten().tolist()

    def plot_forecast(self, forecast_dates: List[datetime], forecasted_prices: List[float]) -> None:
        """Plots the historical data and the forecasted data."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.dates, self.prices, label="Historical BTC Price", color="blue")
        plt.plot(forecast_dates, forecasted_prices, label="Predicted BTC Price", color="red")
        plt.xlabel("Date")
        plt.ylabel("Price (EUR)")
        plt.title("BTC Price Forecast")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('btc_price_forecast.png')
        plt.show()
        print("Forecast chart saved as 'btc_price_forecast.png'.")

    def prepare_and_train(self, dates: List[datetime], prices: List[float]) -> None:
        """Handles data preprocessing, splitting, and training."""
        self.dates = dates
        self.preprocess_data(prices)

        # Create sequences
        x, y = self.create_sequences()
        split_index = int(0.8 * len(x))
        x_train, y_train = x[:split_index], y[:split_index]
        x_val, y_val = x[split_index:], y[split_index:]

        # Train model
        self.train(x_train, y_train, x_val, y_val)


# Main script to execute the prediction
def main():
    # Step 1: Fetch BTC historical data
    url = "https://api.exchange.coinbase.com/products/BTC-EUR/candles"
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 10, 1)
    #end_date = datetime.now()

    btc_fetcher = BTCPriceFetcher(url, start_date, end_date)
    btc_fetcher.fetch_30_day_candles()

    # Step 2: Extract dates and prices
    dates = btc_fetcher.get_dates()
    prices = btc_fetcher.get_prices(choice_candle=4)  # Assuming closing prices

    # Step 3: Initialize predictor and train model
    predictor = BTCPricePredictor(seq_length=30, epochs=20, batch_size=32)
    predictor.prepare_and_train(dates, prices)

    # Step 4: Forecast for October 2024
    forecast_days = 31
    forecasted_prices = predictor.forecast(forecast_days)

    # Step 5: Plot forecasted data
    forecast_dates = [dates[-1] + timedelta(days=i + 1) for i in range(forecast_days)]
    predictor.plot_forecast(forecast_dates, forecasted_prices)

if __name__ == "__main__":
    main()
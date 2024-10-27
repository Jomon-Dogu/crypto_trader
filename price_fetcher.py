import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Any

import crypto_trader
from crypto_trader import CryptoTrader

class BTCPriceFetcher:
    def __init__(self, url: str, start_date: datetime, end_date: datetime, granularity: int = 86400):
        self.url = url
        self.start_date = start_date
        self.end_date = end_date
        self.granularity = granularity
        self.data = []

    def fetch_30_day_candles(self) -> List[Any]:
        """Fetches all 30-day period candles within the specified date range."""

        current_date = self.start_date
        while current_date < self.end_date:
            next_date = current_date + timedelta(days=30)
            if next_date > self.end_date:
                next_date = self.end_date

            params = {
                'granularity': self.granularity,
                'start': current_date.strftime('%Y-%m-%d'),
                'end': next_date.strftime('%Y-%m-%d')
            }

            response = requests.get(self.url, params=params)
            if response.status_code == 200:
                btc_data = response.json()
                btc_data.sort(key=lambda x: x[0])
                self.data.extend(btc_data)
            else:
                print(f"Error fetching data: {response.text}")

            current_date = next_date

        # Remove duplicates by timestamp
        self.data = list({item[0]: item for item in self.data}.values())
        return self.data

    def get_dates(self) -> List[datetime]:
        """Extracts date information for plotting."""
        return [datetime.utcfromtimestamp(item[0]) for item in self.data]

    def get_prices(self, choice_candle: int = 4) -> List[float]:
        """Extracts price information for plotting."""
        if choice_candle in range(1, 6):
            return [item[choice_candle] for item in self.data]
        else:
            print("Invalid choice, defaulting to closing prices.")
            return [item[4] for item in self.data]

    def plot_data(self, dates: List[datetime], prices: List[float]) -> None:
        """Plots the fetched data."""
        plt.figure(figsize=(10, 6))
        plt.plot(dates, prices, label="BTC Price", linestyle='-', color='blue')
        plt.xlabel("Date")
        plt.ylabel("Price (EUR)")
        plt.title(
            f"Bitcoin (BTC) Price from {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('btc_price_chart_current.png')
        print("Chart saved as 'btc_price_chart_current.png'.")

    def fetch_and_plot(self) -> None:
        """Fetches data and plots the chart."""
        self.fetch_30_day_candles()
        dates = self.get_dates()
        prices = self.get_prices()
        self.plot_data(dates, prices)

def main():
    url = "https://api.exchange.coinbase.com/products/BTC-EUR/candles"
    start_date = datetime(2014, 1, 1)
    #end_date = datetime(2024, 10, 1)
    end_date = datetime.now()
    btc_fetcher = BTCPriceFetcher(url, start_date, end_date)
    btc_fetcher.fetch_and_plot()

if __name__ == "__main__":
    main()

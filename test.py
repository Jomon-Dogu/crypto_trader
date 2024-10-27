import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Any


def fetch_30_day_candles(start_date: datetime, end_date: datetime, url: str, granularity: int = 86400) -> List[
    Any]:  # 86400s = one day
    """ This function fetch all the 30-Day-periode-candles. It is nessesary because coinbase API gives only
    30 candles per daily data request

    :param start_date: Starting day for your chart
    :param end_date: Last day of your chart
    :return A list for every item(day,respectivley) with its properties (timestamp, low, high, open, close, volume),
            [[1514764800, 11351, 12141, 12139.01, 11799.98, 1923.35129295], # item one
            [1514851200, 11280, 13100, 11799.98, 12545.01, 4707.00437392], e.g. # item two
    """

    # Initialize an empty list to collect all data
    all_data = []

    # Step through the entire date range month by month
    current_date = start_date
    while current_date < end_date:
        # Define the end date for the current request (one month ahead)
        next_date = current_date + timedelta(days=30)
        if next_date > end_date:
            next_date = end_date  # Ensure we don't go beyond today's date

        # Format dates in ISO 8601 format (YYYY-MM-DD)
        params = {
            'granularity': granularity,  # Daily data
            'start': current_date.strftime('%Y-%m-%d'),  # convert into string
            'end': next_date.strftime('%Y-%m-%d')  # convert into string
        }

        # Fetch data from Coinbase Pro API
        response = requests.get(url, params=params)

        if response.status_code == 200:
            btc_data = response.json()
            # Sort the data by timestamp to avoid any potential overlap or ordering issues
            btc_data.sort(key=lambda x: x[0])
            all_data.extend(btc_data)  # Add the fetched data to our list
        #     print(f"Fetched data from {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}")
        else:
            #    print(f"Error fetching data from {current_date.strftime('%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}: {response.status_code}")
            print(response.text)

        # Move to the next month
        current_date = next_date

    # Remove any duplicate timestamps (if any)
    unique_data = list({item[0]: item for item in all_data}.values())
    return unique_data


def print_x(date_price_data: List[Any]) -> datetime:
    """
    Convert data into a list of dates
    item(timestamp, low, high, open, close, volume)
    """
    dates1 = [datetime.utcfromtimestamp(item[0]) for item in date_price_data]  # intervall x achse
    return dates1


def print_y(date_price_data: List[Any], choise_candle: int = None) -> datetime:
    """
    Convert data into a list of closing prices
    item(timestamp, low, high, open, close, volume)
    item(0, 1, 2, 3, 4, 5)
    """
    if choise_candle == 1 | 2 | 3 | 4 | 5:
        prices1 = [item[choise_candle] for item in date_price_data]  # Closing price intervall y achse
    else:
        print("No valide input, choose closing price by default")
        prices1 = [item[4] for item in date_price_data]  # Closing price intervall y achse
    return prices1


def plot_fig(dates: list[int], prices: int):
    """
    Speichert den entsprechenden chart

    :param dates: Lists of dates for x-axis
    :param prices: Price for each point on the x-axis
    """
    plt.figure(figsize=(10, 6))
    plt.plot(dates, prices, label="BTC Price", linestyle='-', color='blue')
    plt.xlabel("Date")
    plt.ylabel("Price (EUR)")
    plt.title(f"Bitcoin (BTC) Price from 2018 to {datetime.now().strftime('%Y-%m-%d')}")
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.savefig('btc_price_chart_current.png')


def main():
    url = "https://api.exchange.coinbase.com/products/BTC-EUR/candles"
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2020, 1, 1)
    # end_date = datetime.now()
    test = fetch_30_day_candles(start_date, end_date, url)
    print(test)
    dates1 = print_x(test)
    prices1 = print_y(test)
    plot_fig(dates1, prices1)


if __name__ == "__main__":
    main()

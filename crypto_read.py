import ccxt
import requests
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from key_manager import APIKeyManager


class CryptoRead:
    def __init__(self, api_key: str, api_secret: str, currencies: List[str] = ['BTC-EUR']):
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currencies = currencies
        self.eur_markets = []
        self.results = []
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data):
        for observer in self.observers:
            observer.update(data)

    def get_supported_markets(self):
        url = "https://api.exchange.coinbase.com/products"
        response = requests.get(url).json()
        self.eur_markets = [market['id'] for market in response if market['quote_currency'] == 'EUR']
        
        supported, unsupported = [], []
        for pair in self.eur_markets:
            try:
                self.client.fetch_ticker(pair)
                supported.append(pair)
            except ccxt.errors.BadSymbol:
                unsupported.append(pair)
            except Exception as e:
                print(f"Fehler für {pair}: {e}")
                unsupported.append(pair)
        
        return supported, unsupported

    def get_current_prices(self) -> List[Tuple[str, float]]:
        prices = []
        for currency in self.currencies:
            try:
                ticker = self.client.fetch_ticker(currency)
                current_price = ticker['last']
                prices.append((currency, current_price))
            except ccxt.errors.BadSymbol:
                print(f"Symbol nicht unterstützt: {currency}")
            except Exception as e:
                print(f"Fehler beim Abrufen des Preises für {currency}: {e}")
        return prices

    def get_past_prices(self, hours_ago: int, max_attempts: int = 3) -> List[Tuple[str, Optional[float]]]:
        past_prices = []
        since = int((datetime.utcnow() - timedelta(hours=hours_ago)).timestamp() * 1000)
        
        for currency in self.currencies:
            attempt, past_price = 0, None
            while attempt < max_attempts and past_price is None:
                try:
                    ohlcv = self.client.fetch_ohlcv(currency, timeframe='1h', since=since, limit=5)
                    if ohlcv:
                        past_price = ohlcv[-1][4]
                        past_prices.append((currency, past_price))
                    else:
                        print(f"Keine Daten für {currency} verfügbar, Versuch {attempt + 1}/{max_attempts}.")
                        attempt += 1
                except ccxt.errors.BadSymbol:
                    print(f"Symbol nicht unterstützt: {currency}")
                    past_prices.append((currency, None))
                    break
                except Exception as e:
                    print(f"Fehler beim Abrufen des Preises für {currency}: {e}")
                    attempt += 1

            if past_price is None:
                print(f"Keine ausreichenden historischen Daten für {currency}")
                past_prices.append((currency, None))

        return past_prices

def main():
    # API-Schlüssel und Informationen
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # APIKeyManager-Instanz erstellen
    key_manager = APIKeyManager(file_dir, file_name)

    # Lade die API-Schlüssel
    key_manager.load_keys()
    
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()
    
 
    crypto_reader = CryptoRead(api_key, api_secret)

    # Ausgabe der verfügbaren EUR-Märkte
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]
    crypto_reader = CryptoRead(api_key, api_secret, all_coins_of_interest_useable)
    print(crypto_reader.currencies)

    current_price = crypto_reader.get_current_prices()
  #  past_price = reader.get_past_prices(6)
    print("##########################################")
  #  print(past_price)
    print("##########################################")
    print(current_price)
    print("##########################################")

 

if __name__ == "__main__":
    main()
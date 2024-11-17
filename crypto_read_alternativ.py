import requests
from datetime import datetime, timezone, timedelta
from key_manager import APIKeyManager
from crypto_read import CryptoPriceAnalyzerCoinbase

class CryptoPriceAnalyzerCryptoCompare:
    def __init__(self, api_key, currency_pairs):
        """
        Initialisiert die Klasse mit API-Schlüssel und einer Liste von Währungspaaren.
        :param api_key: API-Schlüssel für CryptoCompare.
        :param currency_pairs: Liste von Währungspaaren (z. B. ['BTC-EUR', 'ETH-EUR']).
        """
        self.api_key = api_key
        self.currency_pairs = currency_pairs
        self.base_url = "https://min-api.cryptocompare.com/data/v2"

    @staticmethod
    def get_unix_timestamp_for_past_hours(hours_ago):
        """
        Berechnet den Unix-Timestamp für einen Zeitpunkt, der eine bestimmte Anzahl an Stunden in der Vergangenheit liegt.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit.
        :return: Unix-Timestamp
        """
        past_time = datetime.utcnow() - timedelta(hours=hours_ago)
        return int(past_time.replace(tzinfo=timezone.utc).timestamp())

    def get_price_at_time(self, symbol, currency, timestamp):
        """
        Holt den Preis einer Kryptowährung zu einem bestimmten Zeitpunkt.
        :param symbol: Symbol der Kryptowährung (z. B. 'BTC')
        :param currency: Zielwährung (z. B. 'USD')
        :param timestamp: Unix-Timestamp
        :return: Preis (float)
        """
        url = f"{self.base_url}/histominute"
        params = {
            "fsym": symbol,
            "tsym": currency,
            "limit": 1,
            "toTs": timestamp,
            "api_key": self.api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        if "Data" in data and "Data" in data["Data"]:
            return data["Data"]["Data"][-1]["close"]
        else:
            raise ValueError(f"Keine Daten für {symbol}-{currency} gefunden.")

    @staticmethod
    def calculate_price_change(old_price, new_price):
        """
        Berechnet die prozentuale Preisänderung.
        :param old_price: Alter Preis
        :param new_price: Neuer Preis
        :return: Prozentuale Änderung (float)
        """
        return ((new_price - old_price) / old_price) * 100

    def analyze_prices(self, hours_ago):
        """
        Führt die Preisanalyse für alle Währungspaare durch.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit, die abgerufen werden sollen.
        :return: Liste von Tuple: ((currency, past_price), (currency, current_price), (currency, price_change))
        """
        past_timestamp = self.get_unix_timestamp_for_past_hours(hours_ago)

        results = []  # Liste für die Ergebnisse

        for pair in self.currency_pairs:
            try:
                symbol, currency = pair.split("-")  # Zerlege in Symbol und Zielwährung
                symbol = symbol.strip().upper()
                currency = currency.strip().upper()

                # Historischer Preis
                past_price = self.get_price_at_time(symbol, currency, past_timestamp)

                # Aktueller Preis
                current_price = self.get_price_at_time(symbol, currency, int(datetime.now(timezone.utc).timestamp()))

                # Preisänderung berechnen
                price_change = self.calculate_price_change(past_price, current_price)

                # Speichern der Ergebnisse als Tuple
                results.append(((pair, past_price), (pair, current_price), (pair, price_change)))
            except ValueError as e:
                print(f"Fehler für {pair}: {e}")

        return results

# Hauptprogramm
if __name__ == "__main__":
    # API-Schlüssel und Währungspaare
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # APIKeyManager-Instanz erstellen
    key_manager = APIKeyManager(file_dir, file_name)

    # Lade die API-Schlüssel
    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()

    # Initialisiere die Coinbase-Analyseklasse
    analyzer_coinbase = CryptoPriceAnalyzerCoinbase(api_key, api_secret)

    # Unterstützte Märkte von Coinbase
    print(f"Unterstützte Märkte: {analyzer_coinbase.currencies}")

    CURRENCY_PAIRS = analyzer_coinbase.currencies  # Die Liste von Währungspaaren aus Coinbase

    # Eingabe der vergangenen Stunden
    hours_ago = int(input("vergangene Stunden eingeben: "))  # Keine Aufforderung, nur Eingabe der Stundenanzahl

    # Initialisiere die CryptoCompare-Analyseklasse und führe die Analyse durch
    analyzer = CryptoPriceAnalyzerCryptoCompare(api_key, currency_pairs=CURRENCY_PAIRS)
    results = analyzer.analyze_prices(hours_ago)

    print(results)
    # Ausgabe der Ergebnisse
   # print("\nErgebnisse:")
  #  for result in results:
   #     print(result)

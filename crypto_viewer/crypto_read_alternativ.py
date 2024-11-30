import requests
from datetime import datetime, timezone, timedelta
from crypto_viewer.key_manager import APIKeyManager
from crypto_viewer.crypto_read import CryptoPriceAnalyzerCoinbase


class CryptoPriceAnalyzerCryptoCompare:
    def __init__(self, api_key: str):
        """
        Initialisiert die CryptoCompare-Analyseklasse mit dem API-Schlüssel.
        :param api_key: API-Schlüssel für CryptoCompare.
        """
        self.api_key = api_key
        self.base_url = "https://min-api.cryptocompare.com/data/v2"

    @staticmethod
    def get_unix_timestamp_for_past_hours(hours_ago: int = 24) -> int:
        """
        Berechnet den Unix-Timestamp für einen Zeitpunkt vor einer bestimmten Anzahl von Stunden.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit.
        :return: Unix-Timestamp
        """
        past_time = datetime.utcnow() - timedelta(hours=hours_ago)
        return int(past_time.replace(tzinfo=timezone.utc).timestamp())

    def get_price_at_time(self, symbol: str, currency: str, timestamp: int) -> float:
        """
        Ruft den Preis einer Kryptowährung zu einem bestimmten Zeitpunkt ab.
        :param symbol: Symbol der Kryptowährung (z. B. 'BTC').
        :param currency: Zielwährung (z. B. 'EUR').
        :param timestamp: Unix-Timestamp.
        :return: Preis (float).
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
        raise ValueError(f"Keine Daten für {symbol}-{currency} verfügbar.")

    @staticmethod
    def calculate_price_change(old_price: float, new_price: float) -> float:
        """
        Berechnet die prozentuale Preisänderung.
        :param old_price: Alter Preis.
        :param new_price: Neuer Preis.
        :return: Prozentuale Änderung (float).
        """
        return ((new_price - old_price) / old_price) * 100

    def analyze_prices(self, currency_pairs: list[str], hours_ago: int = 24) -> list[tuple]:
        """
        Analysiert die Preisänderung für eine Liste von Währungspaaren und gibt die Ergebnisse im gewünschten Format aus.
        :param currency_pairs: Liste von Währungspaaren (z. B. ['BTC-EUR', 'ETH-EUR']).
        :param hours_ago: Anzahl der Stunden in der Vergangenheit.
        :return: Liste von Tupeln: [(('pair', past_price), ('pair', current_price), ('pair', price_change_percent)), ...]
        """
        past_timestamp = self.get_unix_timestamp_for_past_hours(hours_ago)
        results = []

        for pair in currency_pairs:
            try:
                symbol, currency = pair.split("-")
                symbol = symbol.strip().upper()
                currency = currency.strip().upper()

                # Preise abrufen
                past_price = self.get_price_at_time(symbol, currency, past_timestamp)
                current_price = self.get_price_at_time(symbol, currency, int(datetime.now(timezone.utc).timestamp()))
                price_change = self.calculate_price_change(past_price, current_price)

                # Ergebnis speichern im gewünschten Format
                results.append((
                    (pair, past_price),
                    (pair, current_price),
                    (pair, price_change)
                ))
            except ValueError as e:
                print(f"Fehler für {pair}: {e}")
            except Exception as e:
                print(f"Unerwarteter Fehler für {pair}: {e}")
        return results



# Hauptprogramm
if __name__ == "__main__":
    # API-Schlüssel-Verwaltung
    file_dir = "/home/wolff/keys"
    file_name = "coinbase_key.txt"
    key_manager = APIKeyManager(file_dir, file_name)

    # API-Schlüssel laden
    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()

    # Initialisierung der Coinbase-Klasse
    analyzer_coinbase = CryptoPriceAnalyzerCoinbase(api_key, api_secret)            #  CryptoPriceAnalyzerCoinbase muss man aufrufen um tokens zu erhalten die bei coinbase handelbar sind

    # Unterstützte Märkte abrufen
    supported_markets = analyzer_coinbase.currencies
    print("Unterstützte Märkte:", supported_markets)

    # Benutzerdefinierte Auswahl von Währungspaaren
    currency_pairs = input(
        "Geben Sie die zu analysierenden Währungspaare ein (z. B. 'BTC-EUR,ETH-EUR') oder drücken Sie Enter für alle: "
    )
    if not currency_pairs.strip():
        currency_pairs = supported_markets  # Alle unterstützen Märkte analysieren
    else:
        currency_pairs = [pair.strip().upper() for pair in currency_pairs.split(",")]

    # Eingabe der Stunden in der Vergangenheit
    hours_ago = int(input("Vergangene Stunden eingeben: "))

    # CryptoCompare-Analyse
    analyzer = CryptoPriceAnalyzerCryptoCompare(api_key)
    results = analyzer.analyze_prices(currency_pairs, hours_ago)

    # Ergebnisse ausgeben
    print("\nAnalyse-Ergebnisse:")
    for result in results:
        print(f"Währungspaar: {result['pair']}")
        print(f"  - Preis vor {hours_ago} Stunden: {result['past_price']:.2f}")
        print(f"  - Aktueller Preis: {result['current_price']:.2f}")
        print(f"  - Preisänderung: {result['price_change_percent']:.2f}%\n")

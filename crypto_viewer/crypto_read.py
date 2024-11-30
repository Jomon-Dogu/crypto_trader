from crypto_viewer.key_manager import APIKeyManager
import ccxt
import requests
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

class CryptoPriceAnalyzerCoinbase:
    def __init__(self, api_key: str, api_secret: str):
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currencies = self.get_supported_markets()[0]

    def get_supported_markets(self) -> Tuple[List[str], List[str]]:
        url = "https://api.exchange.coinbase.com/products"
        response = requests.get(url).json()
        eur_markets = [market['id'] for market in response if market['quote_currency'] == 'EUR']

        supported, unsupported = [], []
        for pair in eur_markets:
            try:
                self.client.fetch_ticker(pair)
                supported.append(pair)
            except ccxt.errors.BadSymbol:
                unsupported.append(pair)
            except Exception as e:
                print(f"Fehler für {pair}: {e}")
                unsupported.append(pair)

        return supported, unsupported

    def fetch_price(self, currency: str, hours_ago: Optional[int] = None) -> Optional[float]:
        """
        Hilfsmethode zum Abrufen eines Preises.
        :param currency: Währungspaar, für das der Preis abgerufen werden soll.
        :param hours_ago: Wenn angegeben, wird der Preis zum angegebenen Zeitpunkt abgerufen.
        :return: Preis (float) oder None bei einem Fehler.
        """
        try:
            if hours_ago is None:
                # Aktueller Preis
                ticker = self.client.fetch_ticker(currency)
                return ticker['last']
            else:
                # Historischer Preis
                target_time = datetime.utcnow() - timedelta(hours=hours_ago)
                since = int(target_time.timestamp() * 1000)
                ohlcv = self.client.fetch_ohlcv(currency, timeframe='1h', since=since, limit=5)

                if ohlcv:
                    for candle in ohlcv:
                        candle_time = datetime.utcfromtimestamp(candle[0] / 1000)
                        if candle_time >= target_time:
                            return candle[4]  # Schlusspreis der gefundenen Kerze
        except Exception as e:
            print(f"Fehler beim Abrufen des Preises für {currency}: {e}")
        return None

    def calculate_price_change(self, current_price: float, past_price: Optional[float]) -> Optional[float]:
        """
        Hilfsmethode zur Berechnung der prozentualen Preisänderung.
        :param current_price: Aktueller Preis.
        :param past_price: Preis in der Vergangenheit.
        :return: Preisänderung in Prozent oder None bei ungültigem Wert.
        """
        if past_price and past_price != 0:
            return ((current_price - past_price) / past_price) * 100
        return None

    def analyze_specific_currencies(self, currencies: List[str], hours_ago: int = 24) -> List[Optional[Tuple[Tuple[str, float], Tuple[str, float], Tuple[str, Optional[float]]]]]:
        """
        Analysiert die Preisänderung für eine Liste spezifischer Währungen.
        :param currencies: Eine Liste von zu analysierenden Währungen.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit für die Analyse.
        :return: Liste mit Ergebnissen im Format [(currency, past_price), (currency, current_price), (currency, price_change)].
        """
        results = []
        for currency in currencies:
            if currency not in self.currencies:
                print(f"Währung {currency} wird nicht unterstützt.")
                results.append(None)
                continue

            current_price = self.fetch_price(currency)
            past_price = self.fetch_price(currency, hours_ago)

            if current_price is not None and past_price is not None:
                price_change = self.calculate_price_change(current_price, past_price)
                results.append(((currency, past_price), (currency, current_price), (currency, price_change)))
            else:
                print(f"Fehler bei der Analyse von {currency}.")
                results.append(None)
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
    analyzer_coinbase = CryptoPriceAnalyzerCoinbase(api_key, api_secret)

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

    # Preisanalyse
    results = analyzer_coinbase.analyze_specific_currencies(currency_pairs, hours_ago)

    # Ergebnisse ausgeben
    print("\nAnalyse-Ergebnisse:")
    for result in results:
        if result:
            past_price = result[0][1]
            current_price = result[1][1]
            price_change = result[2][1]

            print(f"Währungspaar: {result[0][0]}")
            print(f"  - Preis vor {hours_ago} Stunden: {past_price:.2f}")
            print(f"  - Aktueller Preis: {current_price:.2f}")
            print(f"  - Preisänderung: {price_change:.2f}%\n")
        else:
            print(f"Ergebnisse für ein Währungspaar konnten nicht abgerufen werden.\n")

from key_manager import APIKeyManager
import ccxt
import requests
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

class CryptoPriceAnalyzerCoinbase:
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialisiert den CryptoPriceAnalyzerCoinbase mit Coinbase-API-Schlüssel und holt unterstützte Märkte.
        :param api_key: API-Schlüssel für Coinbase.
        :param api_secret: Geheimnis für Coinbase.
        """
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currencies = self.get_supported_markets()[0]  # Initialisiere mit unterstützten Märkten

    def get_supported_markets(self) -> Tuple[List[str], List[str]]:
        """
        Ruft unterstützte EUR-Märkte von Coinbase ab und testet, ob sie unterstützt werden.
        :return: Eine Liste von unterstützten und nicht unterstützten Märkten.
        """
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

    def get_current_prices(self) -> List[Tuple[str, float]]:
        """
        Ruft die aktuellen Preise für alle unterstützten Währungen ab.
        :return: Eine Liste von Währungspaaren und deren aktuellen Preisen.
        """
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
        """
        Ruft die Preise für eine bestimmte Anzahl Stunden in der Vergangenheit ab.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit.
        :param max_attempts: Maximale Anzahl von Versuchen bei fehlgeschlagenen Anfragen.
        :return: Eine Liste von Währungspaaren und deren Preisen in der Vergangenheit.
        """
        past_prices = []
        target_time = datetime.utcnow() - timedelta(hours=hours_ago)
        since = int(target_time.timestamp() * 1000)

        for currency in self.currencies:
            attempt, past_price = 0, None
            while attempt < max_attempts and past_price is None:
                try:
                    # Abruf von OHLCV-Daten
                    ohlcv = self.client.fetch_ohlcv(currency, timeframe='1h', since=since, limit=5)
                    if ohlcv:
                        # Suche nach der nächsten Kerze zum gewünschten Zeitpunkt
                        for candle in ohlcv:
                            candle_time = datetime.utcfromtimestamp(candle[0] / 1000)
                            if candle_time >= target_time:
                                past_price = candle[4]  # Schlusspreis der gefundenen Kerze
                                break
                        if past_price is None:
                            print(f"Keine passende Kerze für {currency} gefunden. Versuche es erneut.")
                            attempt += 1
                        else:
                            past_prices.append((currency, past_price))
                    else:
                        print(f"Keine OHLCV-Daten für {currency}")
                        past_prices.append((currency, None))
                        break
                except ccxt.errors.BadSymbol:
                    past_prices.append((currency, None))
                    break
                except Exception as e:
                    print(f"Fehler beim Abrufen von {currency}: {e}")
                    attempt += 1

            if past_price is None:
                print(f"{currency}: Historische Daten konnten nicht abgerufen werden.")
                past_prices.append((currency, None))

        return past_prices

    def calculate_price_change(self, current_prices: List[Tuple[str, float]], past_prices: List[Tuple[str, Optional[float]]]) -> List[Tuple[str, float]]:
        """
        Berechnet die prozentuale Preisänderung.
        :param current_prices: Liste der aktuellen Preise.
        :param past_prices: Liste der Preise in der Vergangenheit.
        :return: Eine Liste von Währungspaaren und deren prozentualer Preisänderung.
        """
        changes = []
        past_dict = dict(past_prices)

        for currency, current_price in current_prices:
            past_price = past_dict.get(currency)
            if past_price is not None and past_price != 0:
                change = ((current_price - past_price) / past_price) * 100
   #             print(f"{currency}: Aktuell = {current_price}, Vergangenheit = {past_price}, Änderung = {change:.2f}%")
                changes.append((currency, change))
            else:
                print(f"{currency}: Preis in der Vergangenheit ist ungültig (past_price={past_price})")
        return changes

    def analyze_prices(self, hours_ago: int) -> List[Tuple[Tuple[str, float], Tuple[str, float], Tuple[str, float]]]:
        """
        Führt die Preisanalyse durch und gibt die Werte zurück.
        :param hours_ago: Anzahl der Stunden in der Vergangenheit.
        :return: Liste von Tupeln mit dem Format:
                 [(currency, past_price), (currency, current_price), (currency, price_change)]
        """
        current_prices = self.get_current_prices()
        past_prices = self.get_past_prices(hours_ago)
        changes = self.calculate_price_change(current_prices, past_prices)

        past_dict = dict(past_prices)
        change_dict = dict(changes)

        result = []
        for currency, current_price in current_prices:
            past_price = past_dict.get(currency, None)
            price_change = change_dict.get(currency, None)
            result.append(((currency, past_price), (currency, current_price), (currency, price_change)))

        return result


# Hauptprogramm
if __name__ == "__main__":
    # API-Schlüssel
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # APIKeyManager-Instanz erstellen
    key_manager = APIKeyManager(file_dir, file_name)

    # Lade die API-Schlüssel
    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()
    # Initialisiere die Analyseklasse
    analyzer = CryptoPriceAnalyzerCoinbase(api_key, api_secret)

    # Analyse durchführen
    hours_ago = int(input("vergangene Stunden eingeben: "))  # Keine Aufforderung, nur Eingabe der Stundenanzahl
    analysis_results = analyzer.analyze_prices(hours_ago)
 #   print(analysis_results)
    # Ergebnisse ausgeben
    print("\nErgebnisse:")
    print(analysis_results[0][0][0])
   
   
   
   # for past, current, change in analysis_results:
    #    print(f"{past[0]}: Vergangenheit = {past[1]}, Aktuell = {current[1]}, Änderung = {change[1]:.2f}%")

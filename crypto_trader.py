import ccxt
from typing import List, Dict
from crypto_evaluator import CryptoEvaluator
from key_manager import APIKeyManager
from crypto_read import CryptoRead
import time

class CryptoTrader:
    def __init__(self, api_key: str, api_secret: str, currency_pairs: List[str],crypto_reader:):
        """
        Initialisiert den API-Client und legt die Liste der Währungspaare fest.

        :param api_key: API-Schlüssel für die Authentifizierung bei der Coinbase-API
        :param api_secret: API-Secret für die Authentifizierung bei der Coinbase-API
        :param currency_pairs: Liste der zu handelnden Währungspaare, z. B. ['BTC-EUR', 'ETH-EUR']
        """
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currency_of_interest = currency_pairs  # Liste von Währungspaaren für den Handel
        self.crypto_reader = crypto_reader
        self.currency_of_interest = []  # Liste für interessante Währungspaare



    def set_currency_of_interest(self, currencies):
        """Setzt die Währungen von Interesse."""
        self.currency_of_interest = currencies

    def get_currency_of_interest(self):
        # Rückgabe der interessanten Währungen
            return self.currency_of_interest
    
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        Ruft die aktuellen Preise für alle festgelegten Währungspaare ab.

        :return: Dictionary mit Währungspaaren und ihren aktuellen Preisen.
        """
        prices = {}
        for pair in self.currency_of_interest:
            try:
                ticker = self.client.fetch_ticker(pair)
                prices[pair] = ticker['last']
                print(f"Aktueller Preis für {pair}: {prices[pair]}")
            except ccxt.BaseError as e:
                print(f"Fehler beim Abrufen des Preises für {pair}: {e}")
        
        return prices

    def buy_token_in_eur(self, pair: str, eur_amount: float):
        """
        Berechnet die Menge des Tokens basierend auf dem aktuellen EUR-Betrag und kauft den Token.

        :param pair: Währungspaar, das gekauft werden soll, z. B. 'BTC-EUR'
        :param eur_amount: Betrag in EUR, der für den Kauf verwendet werden soll
        """
        print(pair,"ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
        try:
            # Abrufen des aktuellen Preises
            current_price = self.client.fetch_ticker(pair)['last']
            # Berechnen der Kaufmenge in Basiswährung (z. B. BTC)
            amount_to_buy = eur_amount / current_price
            print(f"Berechnete Menge für {pair} bei {eur_amount} EUR: {amount_to_buy}")

            # Kaufauftrag erstellen
   #         order = self.client.create_market_buy_order(pair, amount_to_buy) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print(f"Kaufauftrag für {amount_to_buy} {pair.split('-')[0]} erfolgreich. Details: NOT JET")  #  {order}")
        except ccxt.BaseError as e:
            print(f"Fehler beim Kauf von {pair}: {e}")

    def trade_all_tokens_in_eur(self, eur_amount_per_token: float):
        """
        Kauft alle in der Liste festgelegten Währungspaare mit einem festgelegten EUR-Betrag.

        :param eur_amount_per_token: Betrag in EUR, der für den Kauf jedes Tokens verwendet werden soll
        """
        for pair in self.currency_of_interest:
            print(f"Kauf für {eur_amount_per_token} EUR in {pair}")
            self.buy_token_in_eur(pair, eur_amount_per_token)

def main():
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # Erstelle eine Instanz von APIKeyManager und lade die API-Schlüssel
    key_manager = APIKeyManager(file_dir, file_name)
    key_manager.load_keys()

    # API-Schlüssel abrufen
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()
    
    # Initialisiere CryptoRead für die Datenerfassung
    crypto_reader = CryptoRead(api_key, api_secret)
    
    # Rufe alle verfügbaren EUR-Märkte ab und speichere die Währungen von Interesse
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]

    # Erstelle eine Instanz von CryptoEvaluator und füge die Märkte von Interesse hinzu
    evaluator = CryptoEvaluator(crypto_reader)  # Der crypto_reader wird hier korrekt übergeben
    evaluator.set_currency_of_interest(all_coins_of_interest_useable)

    # Starte die kontinuierliche Datenerfassung in einem separaten Thread
    data_thread = evaluator.start_data_collection('change', cycles=10, hours_ago=6)

    # Warten auf Datenerfassung (Wartezeit kann je nach Bedarf angepasst werden)
    time.sleep(5)  # Wartezeit bis erste Daten verfügbar sind
    
    # Ausgabe der gesammelten Daten in regelmäßigen Abständen
    for _ in range(5):
        # Abrufen und Anzeigen der neuesten Ergebnisse
        latest_results = evaluator.get_latest_results()
        
        # Prüfen, ob `latest_results` Daten enthält
        if latest_results:
            print("Aktuelle Ergebnisse:", latest_results)
        else:
            print("Noch keine Ergebnisse verfügbar, warte auf Daten...")
        
        time.sleep(10)  # Zeit bis zur nächsten Abfrage
    
    # Warten auf Beendigung des Datenerfassung-Threads, falls notwendig
    data_thread.join()

    # Analysiere die gesammelten Daten und gebe Währungspaare von Interesse zurück
    currency_pairs = evaluator.get_currency_of_interest()
    print("Währungen von Interesse:", currency_pairs)

    # Initialisiere die CryptoTrader-Klasse für den Handel
    trader = CryptoTrader(api_key, api_secret, currency_pairs)
    
    # Preise der interessanten Währungspaare abrufen und anzeigen
    current_prices = trader.get_current_prices(currency_pairs)
    print("Aktuelle Preise:", current_prices)
    
    # Beispielkauf für alle interessanten Währungspaare mit festgelegtem Betrag in EUR pro Token
    eur_amount_per_token = 50  # Betrag in EUR, der für jedes Währungspaar verwendet werden soll
    trader.trade_all_tokens_in_eur(currency_pairs, eur_amount_per_token)


if __name__ == "__main__":
    main()
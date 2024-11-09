from crypto_read import CryptoRead
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import threading
import time
from key_manager import APIKeyManager
import math

class CryptoEvaluator:
    def __init__(self, crypto_reader: CryptoRead, parameter):
        self.crypto_reader = crypto_reader
        self.latest_data = None
        self.currency_of_interest = []
        self.entscheidung = []
        self.parameter = parameter
        self.crypto_reader.register_observer(self)

    def update(self, data: Dict[str, float]):
        self.latest_data = data
        self.perform_trading_logic()

    def perform_trading_logic(self):
        if self.latest_data is None:
            return
        
        currency_of_interest = []
        for currency, value in self.latest_data.items():
            if value > self.parameter:
                currency_of_interest.append(currency)

        self.currency_of_interest = currency_of_interest

    def get_currency_of_interest(self) -> List[str]:
        return self.currency_of_interest

    def start_data_collection(self, data_type: str, cycles: int, hours_ago: Optional[int] = None, interval: int = 10):
        data_thread = threading.Thread(
            target=self.print_prices_in_loop,
            args=(data_type, cycles, hours_ago, interval),
            daemon=True
        )
        data_thread.start()
        return data_thread

    def get_latest_results(self) -> List[Dict[str, float]]:
        return self.crypto_reader.results

    def get_price_change_percentage(self, hours_ago: int) -> List[Tuple[str, Optional[float]]]:
        current_prices = {currency: price for currency, price in self.crypto_reader.get_current_prices()}
        past_prices = self.crypto_reader.get_past_prices(hours_ago)
        
        price_changes = []
        for currency, past_price in past_prices:
            current_price = current_prices.get(currency)
            if past_price is not None and current_price is not None:
                change_percentage = ((current_price - past_price) / past_price) * 100
                price_changes.append((currency, change_percentage))
            else:
                print(f"Keine ausreichenden Daten für {currency}")
                price_changes.append((currency, None))
        
        return price_changes

    def print_prices_in_loop(self, data_type: str, cycles: int, hours_ago: Optional[int] = None, interval: int = 10):
        try:
            for _ in range(cycles):
                if data_type == 'current':
                    prices = self.crypto_reader.get_current_prices()
                    data = {currency: price for currency, price in prices}

                elif data_type == 'past':
                    if hours_ago is None:
                        print("Bitte geben Sie für 'past' Daten eine Stundenanzahl an.")
                        return
                    prices = self.crypto_reader.get_past_prices(hours_ago)
                    data = {currency: price for currency, price in prices}

                elif data_type == 'change':
                    if hours_ago is None:
                        print("Bitte geben Sie für 'change' Daten eine Stundenanzahl an.")
                        return
                    changes = self.get_price_change_percentage(hours_ago)
                    data = {currency: change for currency, change in changes if change is not None}

                else:
                    print("Ungültiger Datentyp. Wählen Sie 'current', 'past' oder 'change'.")
                    return

                self.crypto_reader.results.append(data)
                self.crypto_reader.notify_observers(data)
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nDatenerfassung wurde beendet.")


def main():
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # APIKeyManager-Instanz erstellen
    key_manager = APIKeyManager(file_dir, file_name)

    # Lade die API-Schlüssel
    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()
    
    # Trader-Instanz initialisieren
    crypto_reader = CryptoRead(api_key, api_secret)
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]

    # Initialisiere CryptoRead und CryptoEvaluator
    reader = CryptoRead(api_key, api_secret, all_coins_of_interest_useable)
    evaluator = CryptoEvaluator(reader,5)  # Trader wird automatisch als Beobachter registriert




    interval = 60*5       #10       # Intervall für die Datenerfassung
    monitor_interval = 60*5  #10    # Intervall für die Überwachungsschleife in main()
    XXX = 60                     # Zyklen für die Datenerfassung

    # Bestimme die Mindestanzahl an Iterationen für YYY, um die Synchronität zu gewährleisten
    YYY = math.ceil((XXX * interval) / monitor_interval)  # *3


    # Starte die kontinuierliche Datenerfassung in einem separaten Thread
    data_thread = evaluator.start_data_collection('change', XXX , 24, interval)  # mache ich das value von perform_trading_logic kleiner, muss ich hier das intervall von 1 auf 5 setzen.

    # Gebe einige Sekunden Zeit für den Datenabruf
    time.sleep(5)  

    for iteration in range(YYY):
        latest_results = evaluator.get_latest_results()
        
        # Ausgabe der aktuellen Ergebnisse
        if latest_results:
            print("Aktuelle Ergebnisse:", latest_results)
            print("#########################################################################################")
        else:
         print("Noch keine Ergebnisse verfügbar, warte auf Daten...")

        # Ausgabe der interessanten Währungen
   #     print("Währungen von Interesse (Hauptschleife):", evaluator.get_currency_of_interest())
        if len(evaluator.get_currency_of_interest()) > 0:
            evaluator.entscheidung = 'Kaufen'
            print(evaluator.get_currency_of_interest()," -------> ", evaluator.entscheidung)
        
        # Wartezeit, bevor die neuesten Ergebnisse erneut abgerufen werden
        time.sleep(10)  

    # Falls Sie sicherstellen möchten, dass die Datenerfassung abgeschlossen ist
    data_thread.join()  # Wartet, bis der Datenerfassungs-Thread beendet ist



if __name__ == "__main__":
    main()

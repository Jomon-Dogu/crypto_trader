from crypto_read import CryptoRead
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from key_manager import APIKeyManager
import threading
import time


class CryptoEvaluator:
    def __init__(self, crypto_reader: CryptoRead):
        """
        Initialisiert den Trader und registriert ihn als Beobachter für CryptoRead.
        """
        self.crypto_reader = crypto_reader
        self.latest_data = None
        self.currency_of_interest = []
        self.entscheidung = []

        # Registrierung des Traders als Beobachter
        self.crypto_reader.register_observer(self)

    def update(self, data: Dict[str, float]):
        """
        Empfängt die neuesten Daten von CryptoRead und speichert sie.
        
        :param data: Neueste Preis- oder Änderungsdaten, übermittelt von CryptoRead
        """
   #     print("Update-Methode aufgerufen mit Daten:", data)
        self.latest_data = data
        self.perform_trading_logic()

    def perform_trading_logic(self):
        """
        Führt die Trading-Logik basierend auf den neuesten Daten aus.
        """
        if self.latest_data is None:
            return  # Keine Daten vorhanden, keine Währungen zu überprüfen
        
        currency_of_interest = []  # Lokale Liste zur Speicherung der Währungen, die die Bedingungen erfüllen
        for currency, value in self.latest_data.items():
            if value > 0.1:  # Bedingung für interessante Währungen (Beispiel)##############################################bedingung
   #             print(f"{currency} hat sich WIRKLICH um mehr als 1% geändert.")
                currency_of_interest.append(currency)
   #         else:
   #             print(f"{currency} hat sich NICHT um mehr als 1% geändert.")

        # Speichern der interessanten Währungen in der Instanzvariablen
        self.currency_of_interest = currency_of_interest
   #     print("Aktualisierte Währungen von Interesse:", self.currency_of_interest)

    def get_currency_of_interest(self) -> List[str]:
        """
        Rückgabe der interessanten Währungen.
        """
        return self.currency_of_interest
    
    def start_data_collection(self, data_type: str, cycles: int, hours_ago: Optional[int] = None, interval: int = 10):
        """
        Startet die Datenerfassung im Hintergrund in einem separaten Thread.

        :param data_type: Art der Daten, die angezeigt werden sollen ('current', 'past' oder 'change')
        :param cycles: Anzahl der Zyklen
        :param hours_ago: Anzahl der Stunden zurück für 'past' und 'change' Daten.
        :param interval: Zeitspanne zwischen den Preisabfragen in Sekunden (Standard: 10 Sekunden)
        """
        self.hours_ago = hours_ago
        data_thread = threading.Thread(
            target=self.crypto_reader.print_prices_in_loop,
            args=(data_type, cycles, hours_ago, interval),
            daemon=True  # Der Thread wird automatisch beendet, wenn das Hauptprogramm endet
        )
        data_thread.start()
        return data_thread
    
    def get_latest_results(self) -> List[Dict[str, float]]:
        """
        Gibt die aktuellen Ergebnisse zurück, die durch die Hintergrunddatenerfassung gesammelt wurden.

        :return: Liste von Preisänderungen oder Preisen für alle Währungspaare
        """
        return self.crypto_reader.results  # Zugriff auf die print_prices_in_loop gesammelten Daten

    
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
    evaluator = CryptoEvaluator(reader)  # Trader wird automatisch als Beobachter registriert



    import math

    interval = 10               # Intervall für die Datenerfassung
    monitor_interval = 10       # Intervall für die Überwachungsschleife in main()
    XXX = 60                      # Zyklen für die Datenerfassung

    # Bestimme die Mindestanzahl an Iterationen für YYY, um die Synchronität zu gewährleisten
    YYY = math.ceil((XXX * interval) / monitor_interval*3)


    # Starte die kontinuierliche Datenerfassung in einem separaten Thread
    data_thread = evaluator.start_data_collection('change', XXX , 6, interval)  # mache ich das value von perform_trading_logic kleiner, muss ich hier das intervall von 1 auf 5 setzen.

    # Gebe einige Sekunden Zeit für den Datenabruf
    time.sleep(5)  

    for iteration in range(YYY):
  #      latest_results = evaluator.get_latest_results()
        
        # Ausgabe der aktuellen Ergebnisse
  #      if latest_results:
  #          print("Aktuelle Ergebnisse:", latest_results)
   #     else:
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

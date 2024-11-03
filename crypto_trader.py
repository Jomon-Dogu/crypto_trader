from crypto_read import CryptoRead
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import requests
from key_manager import APIKeyManager
import threading
import time


class CryptoTrader:
    def __init__(self, crypto_reader: CryptoRead):
        """
        Initialisiert den Trader und registriert ihn als Beobachter für CryptoRead.
        """
        self.crypto_reader = crypto_reader
        self.latest_data = None

        # Registrierung des Traders als Beobachter
        self.crypto_reader.register_observer(self)
        self.results = []  # Speichert die Ergebnisse, die von collect_prices_continuous gesammelt werden
    def update(self, data: Dict[str, float]):
        """
        Empfängt die neuesten Daten von CryptoRead und speichert sie.
        
        :param data: Neueste Preis- oder Änderungsdaten, übermittelt von CryptoRead
        """
        self.latest_data = data
        self.perform_trading_logic()

    def perform_trading_logic(self):
        """
        Führt die Trading-Logik basierend auf den neuesten Daten aus.
        Hier kann z. B. die Entscheidung getroffen werden, ob eine Währung gekauft/verkauft wird.
        """
  #      print("Neue Daten erhalten:", self.latest_data)
        # Beispiel: Einfache Trading-Logik (nur Ausgabe)
        for currency, value in self.latest_data.items():
            if value > 60 :
                print(f"{currency} ist größer als 60%")
            else:
                print("keine Währung ist größer 60%")
      #      print(f"Überprüfung von {currency} mit Wert: {value}")
            # Hier könnte komplexere Logik folgen, z.B. Schwellenwerte für Kauf-/Verkaufsentscheidungen

    def start_data_collection(self, data_type: str = 'current', interval: int = 10, hours_ago: Optional[int] = None):
        """
        Startet die Datenerfassung im Hintergrund in einem separaten Thread.

        :param data_type: Art der Daten, die angezeigt werden sollen ('current', 'past' oder 'change')
        :param interval: Zeitspanne zwischen den Preisabfragen in Sekunden (Standard: 10 Sekunden)
        :param hours_ago: Anzahl der Stunden zurück für 'past' und 'change' Daten.
        """
        data_thread = threading.Thread(
            target=self.crypto_reader.print_prices_in_loop,
            args=(data_type, interval, hours_ago),
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
    # Ausgabe der verfügbaren EUR-Märkte
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]

    # Initialisiere CryptoRead und CryptoTrader
    reader = CryptoRead(api_key, api_secret, ['BTC-EUR', 'ETH-EUR'])
    trader = CryptoTrader(reader)  # Trader wird automatisch als Beobachter registriert

    # Starte die kontinuierliche Datenerfassung in einem separaten Thread
    data_thread = trader.start_data_collection('change', 10, 6)

    for _ in range(5):
        # Abrufen und Anzeigen der neuesten Ergebnisse in regelmäßigen Abständen
        latest_results = trader.get_latest_results()
        print("Aktuelle Ergebnisse:", latest_results)
        time.sleep(10)  # Wartezeit, bevor die neuesten Ergebnisse erneut abgerufen werden


if __name__ == "__main__":
    main()

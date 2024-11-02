import ccxt
import time
from typing import Optional
from key_manager import APIKeyManager

class CryptoRead:
    def __init__(self, api_key: str, api_secret: str, currency: str = 'BTC-EUR'):
        """
        Initialisiert den API-Client und legt Standardwerte fest.

        :param api_key: API-Schlüssel für die Authentifizierung
        :param api_secret: API-Secret für die Authentifizierung
        :param currency: Währungspaar (z. B. 'BTC-EUR')
        """
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currency = currency




    def get_current_price(self) -> float:
        """
        Ruft den aktuellen Preis der festgelegten Währung ab.

        :return: Aktueller Preis der Währung als float
        """
        ticker = self.client.fetch_ticker(self.currency)
        current_price = ticker['last']
        print(f"Aktueller Preis für {self.currency}: {current_price}")
        return current_price

    def print_price_in_loop(self, interval: int = 10):
        """
        Gibt den aktuellen Preis in einer Endlosschleife aus.

        :param interval: Zeitspanne zwischen den Preisabfragen in Sekunden (Standard: 10 Sekunden)
        """
        try:
            while True:
                self.get_current_price()  # Aktuellen Preis abrufen
                time.sleep(interval)  # Warten für die angegebene Zeitspanne
        except KeyboardInterrupt:
            print("\nPreisanzeige wurde beendet.")  # Meldung bei Abbruch der Schleife




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
    
    # Trader-Instanz initialisieren
    crypto_name = ['BTC-EUR', 'ETH-EUR']

    reader = [CryptoRead(api_key, api_secret, currency=i) for i in crypto_name]
    [print(reader[o].get_current_price()) for o in range(len(reader))]


    # Preis in einer Endlosschleife ausgeben
  #  reader.print_price_in_loop(interval=10)  # 10 Sekunden zwischen den Preisabfragen

if __name__ == "__main__":
    main()
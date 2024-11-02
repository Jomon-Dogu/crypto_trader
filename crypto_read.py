import ccxt
import time
from typing import Optional
from key_manager import APIKeyManager
import requests

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

        self.get_eur_markets()

    def get_supported_markets(self):
        """
        Überprüft, welche Währungspaare in `self.currency_pairs` tatsächlich von Coinbase unterstützt werden.

        :return: Tuple mit zwei Listen: (unterstützte Paare, nicht unterstützte Paare)
        """
        supported = []
        unsupported = []
        
        for pair in self.eur_markets:
            try:
                # Versuch, das Ticker-Info für das Paar abzurufen
                self.client.fetch_ticker(pair)
                supported.append(pair)  # Kein Fehler, Paar wird unterstützt
            except ccxt.errors.BadSymbol:
                unsupported.append(pair)  # Fehler zeigt an, dass das Paar nicht unterstützt wird
            except Exception as e:
                # Allgemeiner Fehler, der abgefangen und protokolliert wird, falls erforderlich
                print(f"Fehler für {pair}: {e}")
                unsupported.append(pair)
        
        return supported, unsupported
    

    def get_eur_markets(self):
        """
        Ruft alle handelbaren Märkte in EUR von der Coinbase-API ab und speichert die Symbole im Attribut 'eur_markets'.
        """
        url = "https://api.exchange.coinbase.com/products"
        response = requests.get(url).json()

        

        # Filter für EUR-Märkte und nur Symbole (id) speichern
        self.eur_markets = [market['id'] for market in response if market['quote_currency'] == 'EUR']

    def get_current_price(self) -> float:
        """
        Ruft den aktuellen Preis der festgelegten Währung ab.

        :return: Aktueller Preis der Währung als float
        """
        ticker = self.client.fetch_ticker(self.currency)
        #print(ticker)
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
    
 
    crypto_reader = CryptoRead(api_key, api_secret)
    # Ausgabe der verfügbaren EUR-Märkte
    all_coins_of_interest = crypto_reader.eur_markets
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]
 #   print(all_coins_of_interest_useable)

    # Preis in einer Endlosschleife ausgeben
  #  reader.print_price_in_loop(interval=10)  # 10 Sekunden zwischen den Preisabfragen

     # Trader-Instanz initialisieren
   # all_coins_of_interest = ['XYO-EUR', 'ETH-EUR']
   # print(all_coins_of_interest)

    reader = [CryptoRead(api_key, api_secret, currency=i) for i in all_coins_of_interest_useable]
    

            
    [print(reader[o].get_current_price()) for o in range(len(reader))]


if __name__ == "__main__":
    main()
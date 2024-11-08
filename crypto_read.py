import ccxt
import time
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import requests
from key_manager import APIKeyManager


class CryptoRead:
    def __init__(self, api_key: str, api_secret: str, currencies: List[str] = ['BTC-EUR']):
        """
        Initialisiert den API-Client und legt Standardwerte fest.

        :param api_key: API-Schlüssel für die Authentifizierung
        :param api_secret: API-Secret für die Authentifizierung
        :param currencies: Liste von Währungspaaren (z. B. ['BTC-EUR', 'ETH-EUR'])
        """
        self.client = ccxt.coinbase({
            'apiKey': api_key,
            'secret': api_secret,
        })
        self.currencies = currencies  # Liste von Währungspaaren
        self.eur_markets = []
        self.results=[]
        self.observers = []  # Liste aller registrierten Beobachter (Trader)

    def register_observer(self, observer):
        """Registriert einen Beobachter, der bei neuen Daten benachrichtigt wird."""
        self.observers.append(observer)

    def notify_observers(self, data):
        """Benachrichtigt alle registrierten Beobachter mit neuen Daten."""
        for observer in self.observers:
            observer.update(data)



    def get_supported_markets(self):
            """
            Ruft alle handelbaren Märkte in EUR von der Coinbase-API ab und überprüft, welche 
            Währungspaare in EUR tatsächlich von Coinbase unterstützt werden.

            :return: Tuple mit zwei Listen: (unterstützte Paare, nicht unterstützte Paare)
            """
            # Schritt 1: Abrufen aller Märkte in EUR von der Coinbase-API
            url = "https://api.exchange.coinbase.com/products"
            response = requests.get(url).json()
            
            # Filtern der Märkte, um nur EUR-Märkte zu behalten
            self.eur_markets = [market['id'] for market in response if market['quote_currency'] == 'EUR']

            # Schritt 2: Überprüfen der EUR-Märkte auf Unterstützung
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


    def get_current_prices(self) -> List[Tuple[str, float]]:
        """
        Ruft die aktuellen Preise aller festgelegten Währungspaare ab.

        :return: Liste von Tuples mit Währungspaaren und ihren aktuellen Preisen.
        """
        prices = []
        for currency in self.currencies:
            try:
                ticker = self.client.fetch_ticker(currency)
                current_price = ticker['last']
     #           print(f"Aktueller Preis für {currency}: {current_price}")
                prices.append((currency, current_price))
            except ccxt.errors.BadSymbol:
                print(f"Symbol nicht unterstützt: {currency}")
            except Exception as e:
                print(f"Fehler beim Abrufen des Preises für {currency}: {e}")
        return prices

    def print_prices_in_loop(self, data_type: str, cycles: int, hours_ago: Optional[int] = None, interval: int = 10):
        """
        Speichert die Preise der festgelegten Währungen in einer Liste und gibt sie nach Abschluss zurück.

        :param data_type: Art der Daten, die angezeigt werden sollen ('current', 'past' oder 'change')
        :param interval: Zeitspanne zwischen den Preisabfragen in Sekunden (Standard: 10 Sekunden)
        :param hours_ago: Anzahl der Stunden zurück für 'past' und 'change' Daten.
        :param cycles: Anzahl der Iterationen, bevor die Schleife endet (Standard: 1).
        :return: Liste der erfassten Preisdaten je nach Datentyp.
        """
        try:
            u=0
            for _ in range(cycles):
                if data_type == 'current':
                    prices = self.get_current_prices()
                    data = {currency: price for currency, price in prices}
                    self.results.append({currency: price for currency, price in prices})

                elif data_type == 'past':
                    if hours_ago is None:
                        print("Bitte geben Sie für 'past' Daten eine Stundenanzahl an.")
                        return
                    prices = self.get_past_prices(hours_ago)
                    data = {currency: price for currency, price in prices}
                    self.results.append({currency: price for currency, price in prices})

                elif data_type == 'change':
                    if hours_ago is None:
                        print("Bitte geben Sie für 'change' Daten eine Stundenanzahl an.")
                        return
                    changes = self.get_price_change_percentage(hours_ago)
                    data = {currency: change for currency, change in changes if change is not None}
                    self.results.append({currency: change for currency, change in changes if change is not None})

                else:
                    print("Ungültiger Datentyp. Wählen Sie 'current', 'past' oder 'change'.")
                    return
                
                self.results.append(data)
                self.notify_observers(data)
                
                u+=1
                print("ende",u)
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nDatenerfassung wurde beendet.")
        
        return self.results


    def get_past_prices(self, hours_ago: int, max_attempts: int = 3) -> List[Tuple[str, Optional[float]]]:
        """
        Ruft die Preise für eine Liste von Währungen für eine bestimmte Anzahl von Stunden zurück ab.
        Führt mehrere Versuche durch, um sicherzustellen, dass die Daten abgerufen werden.

        :param hours_ago: Anzahl der Stunden, die in der Vergangenheit liegen
        :param max_attempts: Maximale Anzahl an Versuchen für die Datenabfrage
        :return: Liste von Tuples mit Währungspaaren und ihren Preisen vor `hours_ago` Stunden.
        """
        past_prices = []
        since = int((datetime.utcnow() - timedelta(hours=hours_ago)).timestamp() * 1000)

        for currency in self.currencies:
            attempt = 0
            past_price = None
            while attempt < max_attempts and past_price is None:
                try:
                    ohlcv = self.client.fetch_ohlcv(currency, timeframe='1h', since=since, limit=5)  # Abfrage mehrerer Kerzen
                    if ohlcv:
                        past_price = ohlcv[-1][4]  # Schlusskurs der letzten verfügbaren Kerze
                        past_prices.append((currency, past_price))
                    else:
                        print(f"Keine Daten für {currency} verfügbar, Versuch {attempt + 1}/{max_attempts}.")
                        attempt += 1
                except ccxt.errors.BadSymbol:
                    print(f"Symbol nicht unterstützt: {currency}")
                    past_prices.append((currency, None))
                    break
                except Exception as e:
                    print(f"Fehler beim Abrufen des Preises für {currency}: {e}")
                    attempt += 1

            if past_price is None:
                print(f"Keine ausreichenden historischen Daten für {currency}")
                past_prices.append((currency, None))

        return past_prices
    
    def get_price_change_percentage(self, hours_ago: int) -> List[Tuple[str, Optional[float]]]:
        """
        Berechnet die prozentuale Preisänderung für alle Währungen über einen bestimmten Zeitraum.

        :param hours_ago: Anzahl der Stunden zurück, um den Vergleichspreis zu ermitteln
        :return: Liste von Tuples mit Währungspaaren und der prozentualen Preisänderung.
        """
        current_prices = {currency: price for currency, price in self.get_current_prices()}
        past_prices = self.get_past_prices(hours_ago)
        
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
    all_coins_of_interest_useable = crypto_reader.get_supported_markets()[0]
 #   print(all_coins_of_interest_useable)

    # Preis in einer Endlosschleife ausgeben
  #  reader.print_price_in_loop(interval=10)  # 10 Sekunden zwischen den Preisabfragen

     # Trader-Instanz initialisieren
  #  all_coins_of_interest_useable = ['BTC-EUR', 'ETH-EUR']
   # print(all_coins_of_interest)
    reader = CryptoRead(api_key, api_secret, all_coins_of_interest_useable)
    print(reader.currencies)
  #  current_price = reader.get_current_prices()
  #  past_price = reader.get_past_prices(6)
 #   get_change_percentage = reader.get_price_change_percentage(6)
    get_change_percentage_loop = reader.print_prices_in_loop('change',6,6)
  #  print(current_price)
    print("##########################################")
  #  print(past_price)
    print("##########################################")
   # print(get_change_percentage)
    print("##########################################")
    print(reader.results)


if __name__ == "__main__":
    main()
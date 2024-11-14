import requests
import json
import os
import time
from crypto_read import CryptoRead
from key_manager import APIKeyManager
from datetime import datetime

def load_crypto_dict():
    """Lädt alle Kryptowährungen und ihre IDs von CoinGecko oder aus einer lokalen Datei."""
    cache_file = "crypto_ids.json"
    
    # Wenn die Datei existiert, laden wir die Daten daraus
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    
    # Ansonsten machen wir einen API-Aufruf, um die Daten zu laden
    url = "https://api.coingecko.com/api/v3/coins/list"
    try:
        response = requests.get(url)
        response.raise_for_status()
        coins = response.json()
        crypto_dict = {coin['symbol'].upper(): coin['id'] for coin in coins}
        
        # Speichern in einer lokalen Datei für zukünftige Zugriffe
        with open(cache_file, "w") as f:
            json.dump(crypto_dict, f)
        
        return crypto_dict
    except requests.RequestException as e:
        print(f"Fehler beim Laden der Kryptowährungsliste: {e}")
        return None

def get_multiple_crypto_data(crypto_ids):
    """Ruft die Preisdaten für mehrere Kryptowährungen ab, basierend auf ihren CoinGecko-IDs."""
    # IDs in eine durch Komma getrennte Liste umwandeln
    ids = ','.join(crypto_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,eur"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
        return None

def display_multiple_crypto_data(symbols, data, crypto_dict):
    """Zeigt die Preisinformationen für mehrere Kryptowährungen an."""
    for symbol in symbols:
        crypto_id = crypto_dict.get(symbol)
        if crypto_id and crypto_id in data:
            eur_price = data[crypto_id].get("eur", "n.a.")
            print(f"{symbol}: EUR {eur_price}")
        else:
            print(f"Preis für {symbol} konnte nicht abgerufen werden.")

def get_historical_data_crypto_compare(crypto_symbol, currency="EUR", limit=1):
    url = f"https://min-api.cryptocompare.com/data/histoday"
    
    date_string = int(time.time())
    print(date_string)
    date = datetime.utcfromtimestamp(date_string).strftime('%Y-%m-%d %H:%M:%S')
    print(date)

    # Umwandlung des Datumsstrings in ein datetime-Objekt
   # date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    # Umwandlung des datetime-Objekts in einen Unix-Timestamp
   # timestamp = int(date_object.timestamp())

 #   print(timestamp)  # Ausgabe: 1731369600    timestamp = 1731369600
    params = {
        "fsym": crypto_symbol,
        "tsym": currency,
        "limit": limit,
        "toTs": date_string  # Aktuelle Zeit als Endpunkt
    }
    headers = {
        'Authorization': 'Apikey YOUR_API_KEY'  # Falls du einen API-Schlüssel hast
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Fehler beim Abrufen der historischen Daten: {e}")
        return None

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



    # Alle Kryptowährungen laden und in einem Dictionary speichern
    crypto_dict = load_crypto_dict()
    if not crypto_dict:
        print("Konnte keine Kryptowährungsliste laden. Programm beendet.")
        return
  
    
    crypto_symbols = [coin.split('-')[0] for coin in all_coins_of_interest_useable]
    
    # Liste der gewünschten Kryptowährungen als Symbole
    symbols = crypto_symbols  # ["BTC", "ETH", "DOGE", "SOL", "ADA", "XRP", "LTC", "SHIP"]
    
    
    # IDs der gewünschten Kryptowährungen für eine einzige Anfrage sammeln
    crypto_ids = [crypto_dict[symbol] for symbol in symbols if symbol in crypto_dict]
    if not crypto_ids:
        print("Keine gültigen IDs für die angegebenen Symbole gefunden.")
        return
    
    # Parameter für die Schleife
    n = 1  # Anzahl der Durchläufe
    t = 10  # Pause zwischen den Durchläufen in Sekunden
    
    for i in range(n):
        print(f"\nDurchlauf {i+1}/{n}:")
        
        # Preise für alle gewünschten Kryptowährungen in einer Anfrage abrufen
        data = get_multiple_crypto_data(crypto_ids)
        if data:
            display_multiple_crypto_data(symbols, data, crypto_dict)
        
        # Wartezeit, bevor der nächste Durchlauf startet
        if i < n - 1:  # Nur warten, wenn es noch Durchläufe gibt
            print(f"Warte {t} Sekunden bis zum nächsten Durchlauf...")
            time.sleep(t)  # Warte für t Sekunden


    historical_data = get_historical_data_crypto_compare("BTC")

    rewrite_date = historical_data
    print(rewrite_date)




if __name__ == "__main__":
    main()


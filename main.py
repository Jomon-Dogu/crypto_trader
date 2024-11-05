from crypto_evaluator import CryptoTrader
from key_manager import APIKeyManager
from crypto_read import CryptoRead


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
    reader = CryptoRead(api_key, api_secret, 'BTC-EUR')
    trader = CryptoTrader(reader)  # Trader wird automatisch als Beobachter registriert

    # Preis in einer Endlosschleife ausgeben
    data_thread = trader.start_data_collection('change', 10, 6)

if __name__ == "__main__":
    main()

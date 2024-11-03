from crypto_trader import CryptoTrader
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
    trader = CryptoRead(api_key, api_secret, currency='BTC-EUR')
    # Preis in einer Endlosschleife ausgeben
    trader.print_price_in_loop(interval=10)  # 10 Sekunden zwischen den Preisabfragen

if __name__ == "__main__":
    main()

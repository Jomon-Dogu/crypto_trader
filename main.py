from crypto_trader import CryptoTrader

def main():
    # API-Schlüssel und Informationen
    api_key = 'DEIN_API_KEY'
    api_secret = 'DEIN_API_SECRET'
    
    # Trader-Instanz initialisieren
    trader = CryptoTrader(api_key, api_secret, currency='BTC-EUR')
    
    # Preis in einer Endlosschleife ausgeben
    trader.reader.print_price_in_loop(interval=10)  # 10 Sekunden zwischen den Preisabfragen

if __name__ == "__main__":
    main()

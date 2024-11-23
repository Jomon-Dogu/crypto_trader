from key_manager import APIKeyManager
from crypto_read import CryptoPriceAnalyzerCoinbase
from crypto_read_alternativ import CryptoPriceAnalyzerCryptoCompare
import time



class CryptoEvaluate:
    
    def __init__(self,data):
        self.data = data

    def threshold_change(self, value_1):
        """
        Filtert Währungspaare basierend auf einem Schwellenwert für die Preisänderung.
        :param value_1: Schwellenwert für die Preisänderung (in Prozent)
        :return: Liste der Paare, die den Schwellenwert überschreiten/unterschreiten
        """
        self.value_1 = value_1
        collected_results = []

        for entry in self.data:
            pair = entry[0][0]  # Währungspaar
            price_change = entry[2][1]  # Preisänderung

            if self.value_1 > 0 and price_change > self.value_1:
                collected_results.append((pair, price_change))
            elif self.value_1 < 0 and price_change < self.value_1:
                collected_results.append((pair, price_change))
            elif self.value_1 == 0 and price_change == self.value_1:
                collected_results.append((pair, price_change))

        return collected_results




if __name__ == "__main__":
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    key_manager = APIKeyManager(file_dir, file_name)

    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()

    threshold_value = 50  # in Prozent
    hours_ago = int(input("Vergangene Stunden eingeben: "))


    startpoint = 1
    endpoint = 10
    sleep_value = 60*2

    


    analyzer_coinbase = CryptoPriceAnalyzerCoinbase(api_key, api_secret)
    supported_markets = analyzer_coinbase.currencies

    # Benutzer gibt die Währungspaare ein, bevor die Schleife startet
    currency_pairs = input(
        f"\nGeben Sie die zu analysierenden Währungspaare aus dieser Liste ein(z. B. BTC-EUR,ETH-EUR):\n\n{supported_markets}\n\noder drücken Sie Enter für alle: "
    )
    if not currency_pairs.strip():
        currency_pairs = supported_markets  # Alle unterstützten Märkte analysieren
    else:
        currency_pairs = [pair.strip().upper() for pair in currency_pairs.split(",")]





    while startpoint < endpoint:
        print("Durchlauf: ",startpoint)
        startpoint += 1





        # Preisanalyse
        results_33 = analyzer_coinbase.analyze_specific_currencies(currency_pairs, hours_ago)
        print("")
        print("")
        print("######################## erst CryptoCoinbase: ##################################")

        # Ergebnisse ausgeben
        print("\nAnalyse-Ergebnisse:")
        for result in results_33:
            if result:
                past_price = result[0][1]
                current_price = result[1][1]
                price_change = result[2][1]

                print(f"Währungspaar: {result[0][0]}")
                print(f"  - Preis vor {hours_ago} Stunden: {past_price:.2f}")
                print(f"  - Aktueller Preis: {current_price:.2f}")
                print(f"  - Preisänderung: {price_change:.2f}%\n")
            else:
                print(f"Ergebnisse für ein Währungspaar konnten nicht abgerufen werden.\n")


        # Übergeben Sie die Ergebnisse an CryptoEvaluate
        evaluator = CryptoEvaluate(results_33)

        # Filtern Sie Währungspaare basierend auf dem Schwellenwert
        threshold_results = evaluator.threshold_change(threshold_value)
        print(f"Währungspaare mit Preisänderung über dem Schwellenwert {threshold_value}: ", threshold_results)



        print("######################## jetzt CryptoCompaire: ##################################")

        analyzer = CryptoPriceAnalyzerCryptoCompare(api_key)
        results = analyzer.analyze_prices(currency_pairs, hours_ago)
        results_2 = analyzer_coinbase.analyze_specific_currencies(currency_pairs, hours_ago)

        # Ergebnisse ausgeben
        print("\nAnalyse-Ergebnisse:")
        for result in results:
            if result:
                past_price = result[0][1]
                current_price = result[1][1]
                price_change = result[2][1]

                print(f"Währungspaar: {result[0][0]}")
                print(f"  - Preis vor {hours_ago} Stunden: {past_price:.2f}")
                print(f"  - Aktueller Preis: {current_price:.2f}")
                print(f"  - Preisänderung: {price_change:.2f}%\n")



        # Übergeben Sie die Ergebnisse an CryptoEvaluate
        evaluator = CryptoEvaluate(results)

        # Filtern Sie Währungspaare basierend auf dem Schwellenwert
        threshold_results = evaluator.threshold_change(threshold_value)
        print(f"Währungspaare mit Preisänderung über dem Schwellenwert {threshold_value}: ", threshold_results)


        # Übergeben Sie die Ergebnisse an CryptoEvaluate
     #   evaluator = CryptoEvaluate(results)

        # Filtern Sie Währungspaare basierend auf dem Schwellenwert
    #    threshold_results = evaluator.threshold_change(threshold_value)
     #   print("Währungspaare mit Preisänderung über dem Schwellenwert: ", threshold_results)


        time.sleep(sleep_value)

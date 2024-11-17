from key_manager import APIKeyManager
from crypto_read import CryptoPriceAnalyzerCoinbase
from crypto_read_alternativ import CryptoPriceAnalyzerCryptoCompare



class CryptoEvaluate:
    
    def __init__(self,data,value_1:int):
        self.data = data
        self.value_1 = value_1

    def threshold_change(self):
        collected_results=[]
        for i in range(len(self.data[:])):
            if self.data[i][2][1] > 1:
                collected_results.append(self.data[i][2])
                
        return collected_results




if __name__ == "__main__":
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    key_manager = APIKeyManager(file_dir, file_name)

    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()

    hours_ago = int(input("vergangene Stunden eingeben: "))  # Keine Aufforderung, nur Eingabe der Stundenanzahl
    threshold_value = 1  # in percent

    analyzer_coinbase= CryptoPriceAnalyzerCoinbase(api_key, api_secret)
    analyzer_coinbase_results = analyzer_coinbase.analyze_prices(hours_ago)
    print("##########################################################")
  #  print(analyzer_coinbase_results)
    print("##########################################################")
    threshold_change = CryptoEvaluate(analyzer_coinbase_results,threshold_value).threshold_change()
    print("analyzer_coinbase_results ", threshold_change)






    analyzer_coinbase = CryptoPriceAnalyzerCoinbase(api_key, api_secret)
    CURRENCY_PAIRS = analyzer_coinbase.currencies  # Die Liste von Währungspaaren aus Coinbase
    analyzer_crypto_compare = CryptoPriceAnalyzerCryptoCompare(api_key, CURRENCY_PAIRS)
    analyzer_crypto_compare_results = analyzer_crypto_compare.analyze_prices(hours_ago)
    print("##########################################################")
  #  print(analyzer_crypto_compare_results)
    print("##########################################################")
    threshold_change = CryptoEvaluate(analyzer_crypto_compare_results,threshold_value).threshold_change()
    print("analyzer_crypto_compare_results ", threshold_change)

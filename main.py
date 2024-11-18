from key_manager import APIKeyManager
from crypto_read import CryptoPriceAnalyzerCoinbase
from crypto_read_alternativ import CryptoPriceAnalyzerCryptoCompare
import time



class CryptoEvaluate:
    
    def __init__(self,data):
        self.data = data

    def threshold_change(self,value_1):
        self.value_1 = value_1
        collected_results=[]
        for i in range(len(self.data[:])):
            if self.value_1 > 0:
                if self.data[i][2][1] > self.value_1:
                    collected_results.append(self.data[i][2])
            elif self.value_1 < 0:
                if self.data[i][2][1] < self.value_1:
                    collected_results.append(self.data[i][2])
            elif self.value_1 == 0:
                if self.data[i][2][1] == self.value_1:
                    collected_results.append(self.data[i][2])
                
        return collected_results

    def str_of_interest(self,str_1):
        self.str_1 = str_1
        print(self.data[:])

        for i in range(len(self.data[:])):
            if self.data[i][0][0] == self.str_1 :
                print("hallo ", self.data[i][0][0])
            else:
                print("kein Eintrag")





if __name__ == "__main__":
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    key_manager = APIKeyManager(file_dir, file_name)

    key_manager.load_keys()
    api_key = key_manager.get_api_key()
    api_secret = key_manager.get_api_secret()

    hours_ago = int(input("vergangene Stunden eingeben: "))  # Keine Aufforderung, nur Eingabe der Stundenanzahl
    threshold_value = 10  # in percent

    startpoint = 1
    endpoint = 10
    sleep_value = 10
    str_choise = 'SHIB-EUR'
    while startpoint < endpoint:
        print(startpoint)
        startpoint = startpoint + 1


        analyzer_coinbase= CryptoPriceAnalyzerCoinbase(api_key, api_secret)
        analyzer_coinbase_results = analyzer_coinbase.analyze_prices(hours_ago)
     #   print("##########################################################")
    #  print(analyzer_coinbase_results)
    #    print("##########################################################")
 #       threshold_change = CryptoEvaluate(analyzer_coinbase_results).threshold_change(threshold_value)
 #       print("analyzer_coinbase_results ", threshold_change)


        CURRENCY_PAIRS = analyzer_coinbase.currencies  # Die Liste von Währungspaaren aus Coinbase
        analyzer_crypto_compare = CryptoPriceAnalyzerCryptoCompare(api_key, CURRENCY_PAIRS)
        analyzer_crypto_compare_results = analyzer_crypto_compare.analyze_prices(hours_ago)
    #    print("##########################################################")
    #  print(analyzer_crypto_compare_results)
     #   print("##########################################################")
#        threshold_change = CryptoEvaluate(analyzer_crypto_compare_results).threshold_change(threshold_value)
 #       print("analyzer_crypto_compare_results ", threshold_change)

        str_of_interest = CryptoEvaluate(analyzer_crypto_compare_results).str_of_interest(str_choise)
        print("hallo_2 ", str_of_interest)

        time.sleep(sleep_value)


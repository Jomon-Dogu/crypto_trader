import cbpro
import time

from typing import Any, Optional


class CryptoTrader:
    def __init__(self, api_key: str, api_secret: str, passphrase: str, currency: str = 'BTC-EUR'):
        """
        Initialisiert den API-Client und legt Standardwerte fest.

        :param api_key: API-Schlüssel für die Authentifizierung
        :param api_secret: API-Secret für die Authentifizierung
        :param passphrase: API-Passphrase für die Authentifizierung
        :param currency: Währungspaar (z. B. 'BTC-EUR')
        """
        self.client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)
        self.currency = currency

    def get_current_price(self) -> float:
        """
        Ruft den aktuellen Preis der festgelegten Währung ab.

        :return: Aktueller Preis der Währung als float
        """
        ticker = self.client.get_product_ticker(product_id=self.currency)
        current_price = float(ticker['price'])
        print(f"Aktueller Preis für {self.currency}: {current_price}")
        return current_price

    def place_order_if_price_below(self, target_price: float, trade_volume: str, order_type: str = 'buy') -> Optional[
        dict]:
        """
        Platziert eine Order, wenn der aktuelle Preis unter dem Zielpreis liegt.

        :param target_price: Preis, bei dem gekauft werden soll
        :param trade_volume: Handelsvolumen (z. B. '10.00' in EUR)
        :param order_type: Art der Order ('buy' oder 'sell')
        :return: Orderdetails als Dictionary, falls platziert, sonst None
        """
        current_price = self.get_current_price()
        if current_price < target_price:
            order = self.client.place_market_order(
                product_id=self.currency,
                side=order_type,
                funds=trade_volume
            )
            print("Order platziert:", order)
            return order
        else:
            print(f"Preis ist zu hoch, keine Order platziert. Aktueller Preis: {current_price}")
            return None

    def monitor_price_and_trade(self, initial_price: float, price_drop_threshold: float, trade_volume: str,
                                order_type: str = 'buy'):
        """
        Überwacht den Preis in einer Endlosschleife und platziert eine Order bei einem bestimmten Preisrückgang.

        :param initial_price: Ausgangspreis zur Berechnung des Preisrückgangs
        :param price_drop_threshold: Schwelle für Preisrückgang in Prozent (z. B. 0.05 für 5%)
        :param trade_volume: Handelsvolumen
        :param order_type: Art der Order ('buy' oder 'sell')
        """
        previous_price = initial_price
        while True:
            current_price = self.get_current_price()
            price_change = (previous_price - current_price) / previous_price

            if price_change >= price_drop_threshold:
                order = self.client.place_market_order(
                    product_id=self.currency,
                    side=order_type,
                    funds=trade_volume
                )
                print("Order platziert nach Preisrückgang:", order)
                previous_price = current_price  # Update des Referenzpreises nach Kauf
            else:
                print(f"Keine Order platziert. Preisänderung um {price_change * 100:.2f}%")

            # Wartezeit vor der nächsten Überprüfung
            time.sleep(60)


def main():
    # API-Schlüssel und Informationen
    api_key = 'DEIN_API_KEY'
    api_secret = 'DEIN_API_SECRET'
    passphrase = 'DEINE_PASSPHRASE'

    # Trader-Instanz initialisieren
    trader = CryptoTrader(api_key, api_secret, passphrase, currency='BTC-EUR')

    # Beispielverwendung der Methoden
    target_price = 30000  # Zielpreis für Kauf
    trade_volume = '10.00'  # Handelsvolumen in EUR
    initial_price = 32000  # Ausgangspreis
    price_drop_threshold = 0.05  # 5% Preisrückgang

    # Platzieren einer einmaligen Order bei einem bestimmten Zielpreis
    trader.place_order_if_price_below(target_price, trade_volume, order_type='buy')

    # Endlosschleife zur Überwachung und automatischen Bestellung bei Preisrückgang
    trader.monitor_price_and_trade(initial_price, price_drop_threshold, trade_volume, order_type='buy')



if __name__ == "__main__":
    main()

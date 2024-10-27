import cbpro
import time
from typing import List, Any


def current_price(client: cbpro.AuthenticatedClient, currency: str = 'BTC-EUR') -> int:
    """
    Aktuellen BTC-Preis abrufen

    :param client:
    :param currency:
    :return: Aktuellen BTC-Preis
    """
    ticker = client.get_product_ticker(product_id=currency)
    current_price = float(ticker['price'])
    print(f"Aktueller BTC Preis wird in ${currency} angegeben!")
    return current_price


def order_by_pricelimit(target_price: int, current_prices: int, client: Any, order: str, trade_volume: str,
                        currency: str = 'BTC-EUR') -> dict:
    """
    order_by_pricelimit

    :param target_price:
    :param current_prices:
    :param client:
    :param currency:
    :param order: buy or sell
    :param trade_volume: 10.00
    :return: string if order is placed or not
    """
    if current_prices < target_price:
        # Platzieren einer Kauforder
        order = client.place_market_order(
            product_id=currency,  # 'BTC-EUR'
            side=order,  # 'buy'
            funds=trade_volume  # '10.00'
        )
        result = "Kauforder platziert:", order
    else:
        result = f"BTC-Preis ist zu hoch, Kauforder nicht platziert. Aktueller Preis: ${current_price}"

    return result


####################################


def while_quiry(previous_price: int, price_drop_threshold: int, client: cbpro.AuthenticatedClient, order: str,
                trade_volume: str,
                currency: str = 'BTC-EUR') -> dict:
    """
    Infinite loop for continuous price verification: The while True loop makes it possible to check the market price
    periodically and place a buy order only when the condition is met.

    :param previous_price:
    :param price_drop_threshold:
    :param client:
    :param order:
    :param trade_volume:
    :param currency:
    :return: string if order is placed or not
    """
    # Vorheriger Preis als Referenzwert (hier nur ein Beispielwert)
    previous_price = 32000  # Beispielwert für vorherigen Preis
    price_drop_threshold = 0.05  # Schwelle für Preisrückgang, z.B. 5%

    # Endlosschleife, die den Marktpreis regelmäßig überprüft
    while True:
        # Aktuellen BTC-Preis abrufen
        ticker = client.get_product_ticker(product_id='BTC-USD')
        current_price = float(ticker['price'])
        print(f"Aktueller BTC Preis: ${current_price}")

        # Berechnung des Preisunterschieds
        price_change = (previous_price - current_price) / previous_price

        # Bedingte Kaufentscheidung basierend auf Preisrückgang
        if price_change >= price_drop_threshold:
            # Platzieren einer Kauforder
            order = client.place_market_order(
                product_id=currency,  # 'BTC-EUR'
                side=order,  # 'buy'
                funds=trade_volume  # '10.00'
            )
            result = "Kauforder platziert nach Preisrückgang:", order

            # Aktualisiere den previous_price nach dem Kauf
            previous_price = current_price
        else:
            result = f"Keine Kauforder platziert. Preisänderung um {price_change * 100:.2f}%"

        # Wartezeit vor der nächsten Abfrage (z.B. alle 60 Sekunden)
        time.sleep(60)

        return result


def main():
    # API-Schlüssel und Informationen
    api_key = 'DEIN_API_KEY'
    api_secret = 'DEIN_API_SECRET'
    passphrase = 'DEINE_PASSPHRASE'

    # API-Client für Coinbase Pro initialisieren
    client = cbpro.AuthenticatedClient(api_key, api_secret, passphrase)


if __name__ == "__main__":
    main()


# Se considera que hay cantidad suficiente en el activo spot
# Bug: solo se procesa la tasa tomadora y colocadora si hay BIDS y OFFERS. Si hay uno solo, no

from rate_watch_list import *
import csv
import pyRofex
import rofex
import configparser

# Variables globales
global watch_list


# setup_watch_list()
# ------------------
# Lee la lista de futuros a monitorear del archivo watch_list.csv
# Crea un diccionario, en el cual:
#   la clave es el simbolo del futuro (e.g. GGAL/AGO21)
#   el valor es par de activos financieros con los cuales se puede tomar o colocar tasa
def setup_watch_list():
    global watch_list

    with open('watch_list.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            underlying_asset_symbol = row['underlying_asset_symbol']
            if underlying_asset_symbol == 'DLR':
                underlying_asset_type = ASSET_TYPE_CURRENCY
            else:
                underlying_asset_type = ASSET_TYPE_STOCK
            underlying_asset = FinancialAsset(
                                                symbol=underlying_asset_symbol,  # e.g. GGAL.BA
                                                asset_type=underlying_asset_type  # e.g. 1: divisa 2: accion
                                            )
            future_symbol = row['future_symbol']
            future_maturity_date = row['future_maturity_date']
            future_asset = FinancialAsset(symbol=future_symbol,  # e.g. GGAL/AGO21
                                          asset_type=ASSET_TYPE_FUTURE,
                                          maturity_date=future_maturity_date  # 31-08-2021
                                          )
            watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)

        # Imprimir la lista de instrumentos a los cuales suscribirse para pedir market data
        instruments = watch_list.get_watch_symbols()
        print("Futures watch list")
        print("------------------")
        for instrument in instruments:
            print(instrument)
        print("------------------")


# First we define the handlers that will process the messages and exceptions.
def market_data_handler(message):
    global watch_list
    future_symbol = message['instrumentId']['symbol']
    try:
        future_bid_price = message['marketData']['BI'][0]['price']
        future_bid_size = message['marketData']['BI'][0]['size']
        future_ask_price = message['marketData']['OF'][0]['price']
        future_ask_size = message['marketData']['OF'][0]['size']
        watch_list.search_rate_arbitrage(future_symbol=future_symbol,
                                         future_bid_price=future_bid_price,
                                         future_bid_size=future_bid_size,
                                         future_ask_price=future_ask_price,
                                         future_ask_size=future_ask_size
                                         )
    except IndexError:
        pass


def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))


def error_handler(message):
    print("Error Message Received: {0}".format(message))


def exception_handler(e):
    print("Exception Occurred: {e}", e)


def setup_websocket_connection():
    # Initiate Websocket Connection
    pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                      order_report_handler=order_report_handler,
                                      error_handler=error_handler,
                                      exception_handler=exception_handler)


# subscribe_market_data()
# -----------------------
def subscribe_market_data():
    global watch_list
    tickers = watch_list.get_watch_symbols()

    # Pedir precios de bid y ask de los futuros de la watch_list
    entries = [pyRofex.MarketDataEntry.BIDS,
               pyRofex.MarketDataEntry.OFFERS
               ]

    # Suscribirse para pedir informacion de market data
    pyRofex.market_data_subscription(tickers=tickers, entries=entries)


# Crea una RateWatchList
# Setea el costo de transaccion
def create_watch_list():
    global watch_list
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.has_section('COST') and config.has_option('COST', 'transaction_cost'):
        transaction_cost = float(config['COST']['transaction_cost'])
    else:
        print("Falta [COST].transaction_cost en config.ini")
        transaction_cost = 0.0

    print(f"Costo de transaccion: {transaction_cost:.2%}")
    watch_list = RateWatchList(transaction_cost)


if __name__ == "__main__":
    global watch_list
    rofex.initialize()  # Loguearse a ROFEX
    create_watch_list()  # Leer parametros de costos de archivo de configuracion config.ini
    setup_watch_list()  # Cargar la lista de futuros a monitorear
    setup_websocket_connection()  # Indicar las funciones que manejan los eventos websocket
    subscribe_market_data()  # Suscribirse a bids y offers de los futuros de la watch_list

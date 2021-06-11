# Package rofex

import configparser
import pyRofex
import csv
import yahoo_finance
import cotizacion_dolar
from etc import *


# Variables globales de conexion
global watch_list


# First we define the handlers that will process the messages and exceptions.
def market_data_handler(message):
    symbol = message['instrumentId']['symbol']
    try:
        bid_price = message['marketData']['BI'][0]['price']
        ask_price = message['marketData']['OF'][0]['price']
        underlying_asset = watch_list[symbol]['underlying_asset']
        maturity_date = watch_list[symbol]['maturity_date']
        if maturity_date == "":
            maturity_date = get_maturity_date(symbol)
        if underlying_asset == "DLR":
            spot_price = cotizacion_dolar.dolar_oficial_promedio()
        else:
            spot_price = yahoo_finance.spot_price(underlying_asset)
        days_to_maturity = remaining_days(maturity_date)
        bid_rate, ask_rate = print_implicit_rates(symbol, spot_price, bid_price, ask_price, days_to_maturity)
        if (bid_rate < ask_rate):
            print("oportunidad!")
    except IndexError:
        pass

def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))


def error_handler(message):
    print("Error Message Received: {0}".format(message))


def exception_handler(e):
    print("Exception Occurred: {e}", e)


# setup()
def setup_connection():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not config.has_section('ROFEX'):
        print("Falta [ROFEX] en config.ini")
    elif not config.has_option('ROFEX', 'user'):
        print("Falta [ROFEX].user en config.ini")
    elif not config.has_option('ROFEX', 'password'):
        print("Falta [ROFEX].password en config.ini")
    elif not config.has_option('ROFEX', 'account'):
        print("Falta [ROFEX].account en config.ini")
    else:
        user = config['ROFEX']['user']
        password = config['ROFEX']['password']
        account = config['ROFEX']['account']
        pyRofex.initialize(user=user,
                           password=password,
                           account=account,
                           environment=pyRofex.Environment.REMARKET)

    # Initiate Websocket Connection
    pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                      order_report_handler=order_report_handler,
                                      error_handler=error_handler,
                                      exception_handler=exception_handler)


def setup_watch_list():

    global watch_list
    watch_list = dict()

    with open('watch_list.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            watch_pair = dict()
            watch_pair['future'] = row['future']
            watch_pair['underlying_asset'] = row['underlying_asset']
            watch_pair['maturity_date'] = row['maturity_date']
            watch_list[row['future']] = watch_pair

    # Lista de instrumentos a los cuales suscribirse para pedir market data
    instruments = list(watch_list.keys())

    # Pedir precios de bid y ask
    entries = [pyRofex.MarketDataEntry.BIDS,
               pyRofex.MarketDataEntry.OFFERS
               ]

    # Suscribirse para pedir informacion de market data
    pyRofex.market_data_subscription(tickers=instruments, entries=entries)

# Devuelve una lista de todos los instrumentos que cotizan en ROFEX
def get_symbol_list():
    get_all_instruments = pyRofex.get_all_instruments()
    symbol_list = []
    for instrument in get_all_instruments['instruments']:
        symbol = instrument['instrumentId']['symbol']
        symbol = symbol.split()[0]  # Toma todos los caracteres hasta el primer espacio
        symbol_list.append(symbol)
    symbol_list = list(dict.fromkeys(symbol_list))  # Elimina duplicados
    return symbol_list


def get_bid_ask_price(ticker):
    get_market_data = pyRofex.get_market_data(ticker=ticker,
                                              entries=[pyRofex.MarketDataEntry.BIDS, pyRofex.MarketDataEntry.OFFERS])
    try:
        if get_market_data['status'] != 'OK':
            return 0, "Error. Verifique que exista el ticker " + ticker
        else:
            bid_price = get_market_data['marketData']['BI'][0]['price']
            ask_price = get_market_data['marketData']['OF'][0]['price']
            return bid_price, ask_price

    except IndexError:
        print("No hay precios de mercado para el ticker " + ticker)
        return 0, 0


if __name__ == "__main__":

    # setup()
    #
    # # Test: Muestra el precio de todos los simbolos que tienen cotizacion
    # symbol_list = get_symbol_list()
    # for symbol in symbol_list:
    #     price, status = get_last_price(symbol)
    #     if price > 0:
    #         print(symbol, price)
    #     else:
    #         print(status)
    #
    # print(get_last_price("GGAL/AGO21"))
    # print(get_bid_price("GGAL/AGO21"))
    # print(get_offer_price("GGAL/AGO21"))

    # message = {'type': 'Md', 'timestamp': 1623433587427, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/AGO21'},
    # 'marketData': {'BI': [{'price': 101.4, 'size': 100}], 'OF': [{'price': 101.52, 'size': 100}]}}

    setup_connection()
    setup_watch_list()
    print("fin")
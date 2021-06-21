
# Se considera que hay cantidad suficiente en el activo spot
# Bug: solo se procesa la tasa tomadora y colocadora si hay BIDS y OFFERS. Si hay uno solo, no

from asset import *
import csv
import pyRofex, rofex
import configparser
import etc


# Variables globales
global watch_list  # Futuros a monitorear
global long_rate, short_rate  # Tasas tomadoras y colocadoras
global long_rate_quantity, short_rate_quantity  # Volumen ofrecido en tasas tomadoras y colocadoras
global transaction_cost  # Costo de transaccion por comprar o vender un accion o futuro

# setup_watch_list()
# ------------------
# Lee la lista de futuros a monitorear del archivo watch_list.csv
# Crea un diccionario, en el cual:
#   la clave es el simbolo del futuro (e.g. GGAL/AGO21)
#   el valor es par de activos financieros con los cuales se puede tomar o colocar tasa
def setup_watch_list():
    global watch_list, short_rate, long_rate, short_rate_quantity, long_rate_quantity
    watch_list = dict()
    short_rate = dict()
    long_rate = dict()
    short_rate_quantity = dict()
    long_rate_quantity = dict()

    with open('watch_list.csv') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            watch_pair = dict()
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
            watch_pair['future_asset'] = future_asset
            watch_pair['underlying_asset'] = underlying_asset
            watch_list[future_symbol] = watch_pair

        # Imprimir la lista de instrumentos a los cuales suscribirse para pedir market data
        instruments = list(watch_list.keys())
        print("Futures watch list")
        print("------------------")
        for instrument in instruments:
            print(instrument)
        print("------------------")

def check_rates():
    global short_rate, long_rate
    best_short_rate = min(short_rate.values())
    best_long_rate = max(long_rate.values())
    # Busca el futuro que tiene la mejor tasa
    best_short_future = [future for future in short_rate if short_rate[future] == best_short_rate][0]
    best_long_future = [future for future in long_rate if long_rate[future] == best_long_rate][0]
    best_short_quantity = short_rate_quantity[best_short_future]
    best_long_quantity = long_rate_quantity[best_long_future]
    print(f"Mejor tasa colocadora: {best_long_rate:.2%} ({best_long_future}, {best_long_quantity} unidades) "
          f"Mejor tasa tomadora: {best_short_rate:.2%} ({best_short_future}, {best_short_quantity} unidades) ")




# First we define the handlers that will process the messages and exceptions.
def market_data_handler(message):

    global transacion_cost, watch_list
    symbol = message['instrumentId']['symbol']
    try:
        future_bid_price = message['marketData']['BI'][0]['price']
        future_bid_size = message['marketData']['BI'][0]['size']
        future_ask_price = message['marketData']['OF'][0]['price']
        future_ask_size = message['marketData']['OF'][0]['size']
        underlying_asset = watch_list[symbol]['underlying_asset']
        spot_ask_price = underlying_asset.ask_price()
        spot_bid_price = underlying_asset.bid_price()
        future_asset = watch_list[symbol]['future_asset']
        days_to_maturity = future_asset.days_to_maturity
        nominal_short_rate, nominal_long_rate = etc.implicit_rates(
            asset=symbol, spot_ask_price=spot_ask_price, spot_bid_price=spot_bid_price,
            future_bid_price=future_bid_price, future_ask_price=future_ask_price,
            days_to_maturity=days_to_maturity, transaction_cost=transaction_cost)

        short_rate[symbol] = nominal_short_rate
        long_rate[symbol] = nominal_long_rate
        short_rate_quantity[symbol] = future_ask_size
        long_rate_quantity[symbol] = future_bid_size
        check_rates()
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
    instruments = list(watch_list.keys())

    # Pedir precios de bid y ask de los futuros de la watch_list
    entries = [pyRofex.MarketDataEntry.BIDS,
               pyRofex.MarketDataEntry.OFFERS
               ]

    # Suscribirse para pedir informacion de market data
    pyRofex.market_data_subscription(tickers=instruments, entries=entries)

def setup_parameters():
    global transaction_cost
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.has_section('COST') and config.has_option('COST', 'transaction_cost'):
        transaction_cost = float(config['COST']['transaction_cost'])
    else:
        print("Falta [COST].transaction_cost en config.ini")
        transaction_cost = 0.0

    print(f"Costo de transaccion: {transaction_cost:.2%}")

if __name__ == "__main__":
    rofex.initialize()  # Loguearse a ROFEX
    setup_parameters()  # Leer parametros de costos de archivo de configuracion config.ini
    setup_watch_list()  # Cargar la lista de futuros a monitorear
    setup_websocket_connection()  # Indicar las funciones que manejan los eventos websocket
    subscribe_market_data()  # Suscribirse a bids y offers de los futuros de la watch_list



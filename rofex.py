import pyRofex
import configparser

global pyrofex_setup_done
pyrofex_setup_done = False

def initialize():
    global pyrofex_setup_done
    if pyrofex_setup_done == True:
        return
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
        print("Connected to ROFEX!")
        pyrofex_setup_done = True

def init_websocket_connection(market_data_handler, order_report_handler, error_handler, exception_handler):
    initialize()
    # Initiate Websocket Connection
    pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                      order_report_handler=order_report_handler,
                                      error_handler=error_handler,
                                      exception_handler=exception_handler)

# Devuelve una lista de todos los instrumentos que cotizan en ROFEX
def get_symbol_list():
    initialize()
    get_all_instruments = pyRofex.get_all_instruments()
    symbol_list = []
    for instrument in get_all_instruments['instruments']:
        symbol = instrument['instrumentId']['symbol']
        symbol = symbol.split()[0]  # Toma todos los caracteres hasta el primer espacio
        symbol_list.append(symbol)
    symbol_list = list(dict.fromkeys(symbol_list))  # Elimina duplicados
    return symbol_list

def get_bid_price(ticker):
    initialize()
    get_market_data = pyRofex.get_market_data(ticker=ticker,
                                              entries=[pyRofex.MarketDataEntry.BIDS])
    try:
        if get_market_data['status'] != 'OK':
            return 0, "Error. Verifique que exista el ticker " + ticker
        else:
            bid_price = get_market_data['marketData']['BI'][0]['price']
            return bid_price

    except IndexError:
        print("No hay precios de mercado para el ticker " + ticker)
        return 0

def get_ask_price(ticker):
    initialize()
    get_market_data = pyRofex.get_market_data(ticker=ticker,
                                              entries=[pyRofex.MarketDataEntry.OFFERS])
    try:
        if get_market_data['status'] != 'OK':
            return 0, "Error. Verifique que exista el ticker " + ticker
        else:
            ask_price = get_market_data['marketData']['OF'][0]['price']
            return ask_price

    except IndexError:
        print("No hay precios de mercado para el ticker " + ticker)
        return 0


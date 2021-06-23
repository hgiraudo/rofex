# rofex.py
# --------
# Funciones wrapper para invocar a pyRofex (conexion a MatbaRofex)


import pyRofex
import configparser

# Antes de invocar a cualquier funcion, es preciso conectarse a ROFEX con user, pass y account
# pyrofex_setup_done es True si la conexion ya fue establecida
pyrofex_setup_done = False


# initialize()
# ------------
# Se conecta a ROFEX, salvo que ya se haya establecido la conexión
# Lee los datos de conexión (user, pass, account) del archivo config.ini
def initialize():
    global pyrofex_setup_done
    if pyrofex_setup_done:
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
        print("Conectado a ROFEX!")
        pyrofex_setup_done = True


# init_websocket_connection()
# ---------------------------
# Se conecta a ROFEX e inicializa una conexión WebSocket
def init_websocket_connection(market_data_handler, order_report_handler, error_handler, exception_handler):
    initialize()
    pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                      order_report_handler=order_report_handler,
                                      error_handler=error_handler,
                                      exception_handler=exception_handler)


# get_symbol_list()
# -----------------
# Devuelve una lista de todos los instrumentos que cotizan en ROFEX
#
# Ejemplo de uso:
#     symbol_list = get_symbol_list()
#     for symbol in symbol_list:
#         print(symbol)
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


# get_bid_price(ticker)
# ---------------------
# Devuelve el mayor precio de subasta actual de un activo que cotiza en ROFEX y un string con el resultado de ejecucion
#
# Ejemplo de uso:
#     bid_price, bid_price_status = get_bid_price(symbol)
#     if bid_price:
#         print(f"{symbol} bid price: ${bid_price}")
def get_bid_price(ticker):
    initialize()
    get_market_data = pyRofex.get_market_data(ticker=ticker,
                                              entries=[pyRofex.MarketDataEntry.BIDS])
    try:
        if get_market_data['status'] != 'OK':
            return 0, "Error. Verifique que exista el ticker " + ticker
        else:
            bid_price = get_market_data['marketData']['BI'][0]['price']
            return bid_price, "OK!"

    except IndexError:
        return 0, "No hay precios de mercado para el ticker " + ticker


# get_ask_price(ticker)
# ---------------------
# Devuelve el menor precio de compra actual de un activo que cotiza en ROFEX y un string con el resultado de ejecucion
#
# Ejemplo de uso:
#     ask_price, ask_price_status = get_ask_price(symbol)
#     if ask_price:
#         print(f"{symbol} ask price: ${ask_price}")
def get_ask_price(ticker):
    initialize()
    get_market_data = pyRofex.get_market_data(ticker=ticker,
                                              entries=[pyRofex.MarketDataEntry.OFFERS])
    try:
        if get_market_data['status'] != 'OK':
            return 0, "Error. Verifique que exista el ticker " + ticker
        else:
            ask_price = get_market_data['marketData']['OF'][0]['price']
            return ask_price, "OK!"

    except IndexError:
        return 0, "No hay precios de mercado para el ticker " + ticker


# buy(ticker, quantity, price)
# ----------------------------
# Compra <quantity> unidades del instrumento <ticker> al precio <price>
# Funcion no implementada aun. Solo imprime el pedido
def buy(ticker, quantity, price):
    print(f"Orden de compra: {quantity:.0f} unidades de {ticker} a ${price:.2f}")


# sell(ticker, quantity, price)
# ----------------------------
# Vende <quantity> unidades del instrumento <ticker> al precio <price>
# Funcion no implementada aun. Solo imprime el pedido
def sell(ticker, quantity, price):
    print(f"Orden de venta: {quantity:.0f} unidades {ticker} a ${price:.2f}")


# Test rofex.py
if __name__ == "__main__":

    symbol_list = get_symbol_list()
    for symbol in symbol_list:
        bid_price, bid_price_status = get_bid_price(symbol)
        if bid_price:
            print(f"{symbol} bid price: ${bid_price}")

        # Conectado a ROFEX!
        # RFX20/JUN21 bid price: $90075
        # DLR/ENE22 bid price: $114.1
        # RFX20/AGO21 bid price: $95850
        # DLR/OCT21A bid price: $106.2
        # YPFD/JUN21 bid price: $883.0
        # DLR/JUL21A bid price: $98.34
        # WTI/JUL21 bid price: $73.5
        # ORO/SEP21 bid price: $1785.0
        # DLR/AGO21A bid price: $100.96
        # YPFD/AGO21 bid price: $925.0
        # DLR/SEP21A bid price: $103.55
        # DLR/SEP21 bid price: $103.6
        # DLR/FEB22 bid price: $118.0
        # DLR/JUN21A bid price: $96.07
        # DLR/NOV21 bid price: $109.2
        # PAMP/AGO21 bid price: $116.65
        # DLR/MAR22 bid price: $121.0
        # DLR/AGO21 bid price: $100.92
        # WTI/NOV21 bid price: $69.91
        # GGAL/AGO21 bid price: $173.8
        # DLR/DIC21A bid price: $112.8
        # DLR/JUN21 bid price: $96.07
        # DLR/ABR22 bid price: $128.0
        # GGAL/JUN21 bid price: $167.85
        # DLR/OCT21 bid price: $106.25
        # ORO/JUL21 bid price: $1795.0
        # WTI/SEP21 bid price: $71.64
        # PAMP/JUN21 bid price: $112.8
        # DLR/NOV21A bid price: $109.1
        # DLR/DIC21 bid price: $112.8
        # DLR/MAY22 bid price: $132.0
        # DLR/JUL21 bid price: $98.34
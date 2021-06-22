# yahoo_finance.py
# ----------------
# Este módulo contiene funciones para tomar cotizaciones de Yahoo Finance


import yfinance

# get_ask_price (ticker)
# get_bid_price (ticker)
# -------------------
# Devuelve el precio de subasta/oferta  de un instrumento financiero
# Los datos se toman de Yahoo Finance
# Si no se encuentra precio, se imprime un mensaje de error y devuelve 0
#
# Ejemplo de uso
# --------------
# ticker = "GGAL"
# ask_price = get_ask_price (ticker=ticker)
# if ask_price:
#   print(f"{ticker} cotiza a {spot:.2f}")  # GGAL.BA  cotiza a 168.95
#
# ask_price = get_ask_price (ticker="XXX")  # Error. No hay ask price para el ticker XXX
# if ask_price:
#   print(f"{ticker} cotiza a {spot:.2f}")

def get_ask_price (ticker):
    info = yfinance.Ticker(ticker).info
    if not 'ask' in info:
        print("Error. No hay ask price para el ticker " + ticker)
        return 0
    else:
        ask_price = float(info['ask'])
        return ask_price

def get_bid_price (ticker):
    info = yfinance.Ticker(ticker).info
    if not 'bid' in info:
        print("Error. No hay bid price para el ticker " + ticker)
        return 0
    else:
        bid_price = float(info['bid'])
        return bid_price

if __name__ == "__main__":

    ticker = "GGAL.BA"
    ask_price = get_ask_price(ticker=ticker)
    bid_price = get_bid_price(ticker=ticker)
    print(f"{ticker} ask price ${ask_price:.2f}") # GGAL.BA ask price $ 163.40
    print(f"{ticker} bid price ${bid_price:.2f}") # GGAL.BA bid price $ 161.50




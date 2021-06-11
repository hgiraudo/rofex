import yfinance

# spot_price (ticker)
# -------------------
# Devuelve el precio actual de un instrumento financiero
# Los datos se toman de Yahoo Finances
# Si no se encuentra precio, se imprime un mensaje de error y devuelve 0
#
# Ejemplo de uso
# --------------
# spot = spot_price ("GGAL")
# if spot:
#   print(f"{ticker} cotiza a {spot:.2f}")  # GGAL.BA  cotiza a 168.95
#
# spot = spot_price ("XXX")  # Error. No hay spot price para el ticker XXX
# if spot:
#   print(f"{ticker} cotiza a {spot:.2f}")


def spot_price (ticker):
    info = yfinance.Ticker(ticker).info
    if not 'previousClose' in info:
        print("Error. No hay spot price para el ticker " + ticker)
        return 0
    else:
        spot_price = info['previousClose']
        spot_price = round(float(spot_price), 4)
        return spot_price

if __name__ == "__main__":

    ticker = "GGAL.BA"
    spot = spot_price(ticker)
    if spot:
        print(f"{ticker} cotiza a {spot:.2f}")

    ticker = "XXX"
    spot = spot_price(ticker)
    if spot:
        print(f"{ticker} cotiza a {spot:.2f}")



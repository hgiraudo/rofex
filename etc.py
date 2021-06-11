import datetime
import yahoo_finance
import cotizacion_dolar

# yearly_rates (interest, days)
# -----------------------------
# Calcula la tasa nominal anual y la tasa efectiva anual
# Recibe un interes y una cantidad de dias en el cual se obtiene ese interes
# Devuelve un objeto de tipo tupla
#
# Ejemplo de uso:
# ---------------
# i = 0.0349
# dias = 82
# tna, tea = yearly_rates(i, dias)
# print(f"Tasa {i:.2%} dias {dias} TNA {tna:.2%} TEA {tea:.2%}") # Tasa 3.49% dias 82 TNA 15.53% TEA 16.50%

def yearly_rates (interest, days):
    nominal_rate = interest * 365 / days
    effective_rate = (interest + 1) ** (365 / days) - 1
    return nominal_rate, effective_rate

# remaining_days (maturity_date)
# ---------------------------
# Calcula la cantidad de días entre la fecha actual y una fecha futura
# Recibe la fecha futura en un string con formato dd-mm-yyyy o un objeto datetime.date
#
# Ejemplo de uso:
# ---------------
# fecha_string = "31-08-2021"
# dias = remaining_days(fecha_string)
# print(f"Faltan {dias} dias para el {fecha_string}")  # Faltan 81 dias para el 31-08-2021
#
# fecha_date = datetime.date(2021, 8, 31)
# dias = remaining_days(fecha_date)
# print(f"Faltan {dias} dias para el {fecha_date}")  # Faltan 81 dias para el 2021-08-31

def remaining_days (maturity_date):
    today = datetime.date.today()
    if isinstance(maturity_date, str):
        maturity_date = datetime.datetime.strptime(maturity_date, "%d-%m-%Y").date()
    remaining_days = (maturity_date - today).days
    return remaining_days

# get_maturity_date
# -----------------
# Determina la fecha de fin de un futuro a partir del nombre del ticker
# El ticker suele tener la forma xyz/MMMYY donde xyz es el subyacente, MMM es el mes e YY es el año
# Devuelve un objeto de tipo datetime.date
#
# Ejemplo de uso
# --------------
# print(get_maturity_date("DLR/OCT21"))  # 2021-10-31
# print(type(get_maturity_date("DLR/OCT21")))  # <class 'datetime.date'>

def get_maturity_date (ticker):
    month_string = ticker.split("/")[1][:3]  # ej: OCT
    month_list = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
    month = month_list.index(month_string) + 1
    year = int(ticker.split("/")[1][3:]) + 2000
    # Para determinar el ultimo dia del mes se busca el primer día del mes siguiente y se resta 1
    maturity_date = datetime.date(year, month + 1, 1)
    maturity_date = maturity_date + datetime.timedelta(days=-1)
    return maturity_date

# print_implicit_rates(asset, spot_price, bid_price, ask_price, days_to_maturity)
# -------------------------------------------------------------------------------
# Calcula e imprime las tasas implicitas de un activo (accion, divisa, etc)
#
# Ejemplos de uso:
# ----------------
# print_implicit_rates("GGAL/AGO21", 170.6, 171.15, 173.4, 81)
#   GGAL/AGO21 Tasa colocadora: TNA 1.45% TEA 1.46%
#   GGAL/AGO21 Tasa tomadora: TNA 7.40% TEA 7.61%

def print_implicit_rates(asset, spot_price, bid_price, ask_price, days_to_maturity):
    bid_rate, ask_rate = 0, 0
    if bid_price and spot_price:
        bid_rate, tea = yearly_rates(bid_price / spot_price - 1, days_to_maturity)
        print(f"{asset} Tasa colocadora: TNA {bid_rate:.2%} TEA {tea:.2%}")
    if ask_rate and spot_price:
        tasa_tomadora, tea = yearly_rates(ask_price / spot_price - 1, days_to_maturity)
        print(f"{asset} Tasa tomadora: TNA {ask_rate:.2%} TEA {tea:.2%}")
    return bid_rate, ask_rate

# def implicit_rates_ticker (spot_ticker, future_ticker, maturity_date=""):
#     if maturity_date == "":
#         maturity_date = get_maturity_date(future_ticker)
#     spot_price = yahoo_finance.spot_price(spot_ticker)
#     bid_price, ask_price = rofex.get_bid_ask_price(future_ticker)
#     days_to_maturity = remaining_days(maturity_date)
#     print_implicit_rates(future_ticker, spot_price, bid_price, ask_price, days_to_maturity)
#
# def implicit_rates_usd (future_ticker, maturity_date=""):
#     if maturity_date == "":
#         maturity_date = get_maturity_date(future_ticker)
#     spot_price = cotizacion_dolar.dolar_oficial_promedio()
#     bid_price, ask_price = rofex.get_bid_ask_price(future_ticker)
#     days_to_maturity = remaining_days(maturity_date)
#     print_implicit_rates(future_ticker, spot_price, bid_price, ask_price, days_to_maturity)

# rofex.setup()
# implicit_rates_usd("DLR/AGO21", "31-08-2021")
# implicit_rates_usd("DLR/SEP21")
# implicit_rates_usd("DLR/OCT21")
# implicit_rates_ticker("GGAL.BA", "GGAL/AGO21")
# implicit_rates_ticker("GGAL.BA", "GGAL/AGO21")
# implicit_rates_ticker("PAMP.BA", "PAMP/AGO21")
# implicit_rates_ticker("YPFD.BA", "YPFD/AGO21")
#





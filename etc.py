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



# print_implicit_rates(asset, spot_price, bid_price, ask_price, days_to_maturity, transacion_cost)
# -------------------------------------------------------------------------------
# Calcula e imprime las tasas implicitas de un activo (accion, divisa, etc)
#
# Ejemplos de uso:
# ----------------
# print_implicit_rates(asset="GGAL/AGO21", spot_price=170, bid_price=172,
#                      ask_price=173, days_to_maturity=81, transaction_cost=0.001)
#   GGAL/AGO21 Tasa tomadora: TNA 8.87% TEA 9.18%
#   GGAL/AGO21 Tasa colocadora: TNA 4.39% TEA 4.47%

def implicit_rates(asset, spot_bid_price, spot_ask_price, future_bid_price, future_ask_price,
                   days_to_maturity, transaction_cost):
    nominal_short_rate, nominal_long_rate = 0, 0

    # Short position: short-sell the security and buy the future
    if future_ask_price and spot_bid_price:
        amount_lent = spot_bid_price * (1 - transaction_cost)
        amount_returned = future_ask_price * (1 + transaction_cost)
        interest = amount_returned / amount_lent - 1
        nominal_short_rate, effective_short_rate = yearly_rates(interest, days_to_maturity)
        print(f"{asset} Spot bid: ${spot_bid_price} Future ask: ${future_ask_price} Tasa tomadora: TNA {nominal_short_rate:.2%} TEA {effective_short_rate:.2%}")

    # Long position: buy the security and sell the future
    if future_bid_price and spot_ask_price:
        investment = spot_ask_price * (1 + transaction_cost)
        investment_return = future_bid_price * (1 - transaction_cost)
        interest = investment_return / investment - 1
        nominal_long_rate, effective_long_rate  = yearly_rates(interest, days_to_maturity)
        print(f"{asset} Spot ask: ${spot_ask_price} Future bid: ${future_bid_price} Tasa colocadora: TNA {nominal_long_rate:.2%} TEA {effective_long_rate:.2%}")
    return nominal_short_rate, nominal_long_rate

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





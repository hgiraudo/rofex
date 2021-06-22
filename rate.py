# rate.py
# -------
# Este módulo contiene funciones para calcular tasas implicitas y tasas anualizadas
#
# yearly_rates(interest, days)
# calcula la tasa anualizada
#
# implicit_rates(asset, spot_bid_price, spot_ask_price, future_bid_price,
#                   future_ask_price, days_to_maturity, transaction_cost)
# calcula e imprime las tasas implicitas


# yearly_rates(interest, days)
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
# implicit_rates(asset="GGAL/AGO21", spot_bid_price=170, spot_ask_price=171,
#               future_bid_price=174, future_ask_price=175, days_to_maturity=81, transaction_cost=0.001)
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

# Test: rate.py

if __name__ == "__main__":

    # Test: yearly_rates(interest, days)
    i = 0.0349
    dias = 82
    tna, tea = yearly_rates(i, dias)
    print(f"Tasa {i:.2%} dias {dias} TNA {tna:.2%} TEA {tea:.2%}") # Tasa 3.49% dias 82 TNA 15.53% TEA 16.50%
    print()

    # Test: implicit_rates(asset, spot_price, bid_price, ask_price, days_to_maturity, transaction_cost)
    short_rate, long_rate = implicit_rates(asset="PAMP/AGO21", spot_bid_price=105, spot_ask_price=113,
                  future_bid_price=115.4, future_ask_price=119.55, days_to_maturity=71, transaction_cost=0.000)

    # PAMP/AGO21 Spot bid: $105 Future ask: $119.55 Tasa tomadora: TNA 71.24% TEA 94.87%
    # PAMP/AGO21 Spot ask: $113 Future bid: $115.4 Tasa colocadora: TNA 10.92% TEA 11.41%

    print(f"{short_rate:.2%} {long_rate:.2%}")
    # 71.24% 10.92%

    # Test: implicit_rates(asset, spot_price, bid_price, ask_price, days_to_maturity, transaction_cost)
    short_rate, long_rate = implicit_rates(asset="GGAL/AGO21", spot_bid_price=161.5, spot_ask_price=163.4,
                  future_bid_price=115.4, future_ask_price=119.55, days_to_maturity=71, transaction_cost=0.000)

    # PAMP/AGO21 Spot bid: $105 Future ask: $119.55 Tasa tomadora: TNA 71.24% TEA 94.87%
    # PAMP/AGO21 Spot ask: $113 Future bid: $115.4 Tasa colocadora: TNA 10.92% TEA 11.41%




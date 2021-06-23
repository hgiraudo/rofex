# rate_watch_list.py
# ------------------
# Este modulo define la clase RateWatchList
# RateWatchList es una coleccion de pares FinancialAsset que permiten tomar o colocar tasa
#


from asset import *
import rate

class RateWatchList:

    # Constructor
    # -----------
    # transaction_cost es el porcentaje de comision que hay que pagar para comprar o vender un activo
    def __init__(self, transaction_cost):
        # Crear estructuras de datos vacías
        self.watch_list = dict()  # simbolos a monitorear. Ej: GGAL/AGO21, PAMP/AGO21, DLR/SEP21
        self.short_rate = dict()  # tasas tomadoras. Ej: GGAL/AGO21: 11.28%, PAMP/AGO21: 12.35%
        self.long_rate = dict()  # tasas colocadoras. Ej: GGAL/AGO21: 18.32%, PAMP/AGO21: 19.40%
        self.short_rate_quantity = dict()  # unidades de tasas tomadoras. Ej:  GGAL/AGO21: 10, PAMP/AGO21: 20
        self.long_rate_quantity = dict()  # unidades de tasas colocadoras. Ej:  GGAL/AGO21: 15, PAMP/AGO21: 5
        self.market_bid_price = dict ()  # precios de mercado. Ej: GGAL/AGO21: $168.1, GGAL.BA: $161.5
        self.market_ask_price = dict()  # precios de mercado. Ej: GGAL/AGO21: $168.95, GGAL.BA: $163.4
        self.transaction_cost = transaction_cost

    # add_watch_pair(future_asset, underlying_asset)
    # ----------------------------------------------
    # Agrega un par de activos financieros con los cuales se puede tomar o colocar tasa
    # Ej: add_watch_pair(future_asset=PAMP/AGO21, underlying_asset=PAMP.BA)
    # Los parametros future_asset y underlying_asset deben ser objetos de tipo FinancialAsset
    def add_watch_pair(self, future_asset, underlying_asset):
        watch_pair = dict()
        watch_pair['future_asset'] = future_asset
        watch_pair['underlying_asset'] = underlying_asset
        symbol = future_asset.symbol
        self.watch_list[symbol] = watch_pair
        days_to_maturity = future_asset.days_to_maturity
        # Para cada fecha de expiracion del futuro hay un diccionario distinto
        # e.g. DLR/AGO21, GGAL/AGO21 y PAMP/AGO21 van a un diccionario
        # DLR/SEP21, GGAL/SEP21 y PAMP/SEP21 van a otro
        self.short_rate[days_to_maturity] = dict()
        self.short_rate_quantity[days_to_maturity] = dict()
        self.long_rate[days_to_maturity] = dict()
        self.long_rate_quantity[days_to_maturity] = dict()

    # get_watch_symbols()
    # -------------------
    # Devuelve la lista de futuros a monitorear
    # Se usa para suscribirse a market data de esta lista de futuros
    def get_watch_symbols(self):
        watch_symbols = self.watch_list.keys()
        return watch_symbols

    # get_underlying_asset()
    # -----------------
    # Dado el ticker de un futuro, devuelve el activo subyacente
    def get_underlying_asset(self, future_symbol):
        underlying_asset = self.watch_list[future_symbol]['underlying_asset']
        return underlying_asset

    # search_rate_arbitrage(future_symbol, future_bid_price, future_bid_size,
    #                               future_ask_price, future_ask_size)
    #
    # Calcula las tasas tomadoras y colocadoras
    # Chequea si hay alguna oportunidad de arbitraje de tasas
    # Recibe un evento de market data (e.g. GGAL/AGO21 bid=$170 x 20 unidades, ask=$172 x 10 unidades)
    # La funcion busca los precios spot para el activo subyacente
    def search_rate_arbitrage(self, future_symbol, future_bid_price, future_bid_size,
                              future_ask_price, future_ask_size):

        # Calcula las tasas implícitas para el evento de market data recibido
        underlying_asset = self.get_underlying_asset(future_symbol)
        underlying_asset_symbol = underlying_asset.symbol
        spot_ask_price = underlying_asset.ask_price()
        spot_bid_price = underlying_asset.bid_price()
        future_asset = self.watch_list[future_symbol]['future_asset']
        days_to_maturity = future_asset.days_to_maturity
        nominal_short_rate, nominal_long_rate = rate.implicit_rates(
            asset=future_symbol, spot_ask_price=spot_ask_price, spot_bid_price=spot_bid_price,
            future_bid_price=future_bid_price, future_ask_price=future_ask_price,
            days_to_maturity=days_to_maturity, transaction_cost=self.transaction_cost)

        # Actualiza las listas de tasas y cantidades
        self.short_rate[days_to_maturity][future_symbol] = nominal_short_rate
        self.short_rate_quantity[days_to_maturity][future_symbol] = future_ask_size
        self.long_rate[days_to_maturity][future_symbol] = nominal_long_rate
        self.long_rate_quantity[days_to_maturity][future_symbol] = future_bid_size

        # Actualiza precios de mercado
        self.market_bid_price[future_symbol] = future_bid_price
        self.market_ask_price[future_symbol] = future_ask_price
        self.market_bid_price[underlying_asset_symbol] = spot_bid_price
        self.market_ask_price[underlying_asset_symbol] = spot_ask_price

        # Toma las listas de futuros que tienen la misma madurez que el actual
        # Esto es para evitar hacer arbitraje de tasas con dos futuros de distinta madurez (e.g. DLR/AGO21 y PAMP/SEP21)
        current_short_rate = self.short_rate[days_to_maturity]
        current_long_rate = self.long_rate[days_to_maturity]
        current_short_rate_quantity = self.short_rate_quantity[days_to_maturity]
        current_long_rate_quantity = self.long_rate_quantity[days_to_maturity]

        # Busca la mejor tasa tomadora (la minima) y mejor tasa colocadora (la maxima)
        best_short_rate = min(current_short_rate.values())  # e.g. 18%
        best_long_rate = max(current_long_rate.values())  # e.g. 24%

        # Identifica el simbolo correspondiente a la mejor tasa tomadora y colocadora
        best_short_future = [future for future in current_short_rate
                             if current_short_rate[future] == best_short_rate][0]  # e.g. GGAL/AGO21 es la que tiene 18%
        best_long_future = [future for future in current_long_rate
                            if current_long_rate[future] == best_long_rate][0]  # e.g. PAMP/AGO21 esla que tiene 24%

        # Busca las cantidades y precios subastados de los futuros con mejores tasas
        best_short_quantity = current_short_rate_quantity[best_short_future]
        best_short_investment = self.market_ask_price[best_short_future] * best_short_quantity
        best_long_quantity = current_long_rate_quantity[best_long_future]
        best_long_investment = self.market_bid_price[best_long_future] * best_long_quantity

        # Imprime los datos de las mejores tasas colocadora y tomadora
        print(f"Mejor tasa colocadora a {days_to_maturity} dias: {best_long_rate:.2%} ({best_long_future}, "
              f"{best_long_quantity} unidades, ${best_long_investment:.2f}) ")
        print(f"Mejor tasa tomadora a {days_to_maturity} dias: {best_short_rate:.2%} ({best_short_future}, "
              f"{best_short_quantity} unidades, ${best_short_investment:.2f}) ")
        print()

        if nominal_long_rate > best_short_rate or nominal_short_rate < best_long_rate:
            # Hay una oportunidad de arbitraje de tasas

            # Tasa colocadora: comprar el subyacente y vender el futuro
            long_rate_sell_asset = best_long_future
            long_rate_buy_asset = self.get_underlying_asset(best_long_future).symbol
            long_rate_sell_price = self.market_bid_price[long_rate_sell_asset]
            long_rate_buy_price = self.market_ask_price[long_rate_buy_asset]
            long_rate_max_amount = best_long_investment

            # Tasa tomadora: comprar el futuro del evento y vender en corto el subyacente
            short_rate_buy_asset = best_short_future
            short_rate_sell_asset = self.get_underlying_asset(best_short_future).symbol
            short_rate_buy_price = self.market_ask_price[short_rate_buy_asset]
            short_rate_sell_price = self.market_bid_price[short_rate_sell_asset]
            short_rate_max_amount = best_short_investment

            # Monto a invertir: minimo entre el que se puede colocar y el que se puede tomar
            max_investment_amount = min(long_rate_max_amount, short_rate_max_amount)

            # Cantidad de contratos a operar en cada tasa
            # Solo se pueden operar numeros enteros.
            long_rate_quantity = max_investment_amount // long_rate_buy_price
            short_rate_quantity = max_investment_amount // short_rate_sell_price

            # Si el monto maximo es muy pequeño, la cantidad puede ser cero.
            # Probar si la operacion es rentable con una unidad
            if long_rate_quantity == 0:
                long_rate_quantity = 1
            if short_rate_quantity == 0:
                short_rate_quantity == 1

            # Inversion, retorno y ganancia de la operacion
            # Los montos positivos son ingresos de efectivo, los negativos son egresos
            # Las variables _investment son los flujos al día de hoy (T + 0)
            # Las variables _return son los flujos al vencimiento del futuro (T + days_to_maturity)
            long_rate_investment = long_rate_buy_price * long_rate_quantity * (1 + self.transaction_cost) * (-1)
            short_rate_investment = short_rate_sell_price * short_rate_quantity * (1 - self.transaction_cost)
            long_rate_return = long_rate_sell_price * long_rate_quantity * (1 - self.transaction_cost)
            short_rate_return = short_rate_buy_price * short_rate_quantity * (1 + self.transaction_cost) * (-1)
            total_investment = long_rate_investment + short_rate_investment
            total_return = long_rate_return + short_rate_return
            total_profit = total_investment + total_return

            # Mostrar en pantalla datos de la operacion
            print("Tasa colocadora")
            print(f"Comprar {long_rate_buy_asset}: {long_rate_quantity:.0f} x ${long_rate_buy_price:.2f} "
                  f"= ${long_rate_investment:.2f} (incl. costos)")
            print(f"Vender {long_rate_sell_asset}: {long_rate_quantity:.0f} x ${long_rate_sell_price:.2f} "
                  f"= ${long_rate_return:.2f} (incl. costos)")
            print("Tasa tomadora")
            print(f"Vender {short_rate_sell_asset}: {short_rate_quantity:.0f} x ${short_rate_sell_price:.2f} "
                  f"= ${short_rate_investment:.2f} (incl. costos)")
            print(f"Comprar {short_rate_buy_asset}: {short_rate_quantity:.0f} x ${short_rate_buy_price:.2f} "
                  f"= ${short_rate_return:.2f} (incl. costos)")
            today_string = datetime.date.today().strftime("%d-%b-%Y")  # Convierte las fechas a formato dd-mmm-yyyy
            maturity_date_string = future_asset.maturity_date.strftime("%d-%b-%Y")
            print(f"Flujos netos: ${total_investment:.2f} ({today_string}) "
                  f"${total_return:.2f} ({maturity_date_string})")
            print(f"Ganancia neta: ${total_profit:.2f} ({days_to_maturity} dias)")
            print()

            # Controlar que la operacion sea rentable. Si se ejecuta esta parte del código, debería serlo.
            # Pero dado que solo pueden operarse cantidades enteras de contratos, si el margen es chico y la diferencia
            # en montos a invertir en tasa colocadora y tomadora es grande, la operacion podría no ser rentable
            # Mejora: buscar una cantidad entera distinta que haga la operacion rentable
            if total_profit < 0:
                print("Error. La operacion no es rentable. Cancelar operacion.")
                return

            # Eliminar los activos usados para no generar una nueva orden sobre estos mismos instrumentos
            self.short_rate[days_to_maturity].pop(best_short_future)
            self.long_rate[days_to_maturity].pop(best_long_future)
            self.short_rate_quantity[days_to_maturity].pop(best_short_future)
            self.long_rate_quantity[days_to_maturity].pop(best_long_future)
            self.market_bid_price.pop(short_rate_sell_asset)
            self.market_bid_price.pop(long_rate_sell_asset)
            self.market_ask_price.pop(short_rate_buy_asset)
            self.market_ask_price.pop(long_rate_buy_asset)

            # Tasa colocadora: vender el futuro
            rofex.sell(ticker=long_rate_sell_asset, quantity=long_rate_quantity, price=long_rate_sell_price)

            # Tasa colocadora: comprar el subyacente
            byma.buy(ticker=long_rate_buy_asset, quantity=long_rate_quantity, price=long_rate_buy_price)

            # Tasa tomadora: comprar el futuro
            rofex.buy(ticker=short_rate_buy_asset, quantity=short_rate_quantity, price=short_rate_buy_price)

            # Tasa tomadora: vender en corto el subyacente
            byma.sell(ticker=short_rate_sell_asset, quantity=short_rate_quantity, price=short_rate_sell_price)



# Test rate_watch_list.py
# -----------------------
if __name__ == "__main__":

    rate_watch_list = RateWatchList(transaction_cost=0.000)

    # Agregar 4 pares de activos a monitorear
    future_asset = FinancialAsset(symbol="GGAL/AGO21", asset_type=ASSET_TYPE_FUTURE)
    underlying_asset = FinancialAsset(symbol="GGAL.BA", asset_type=ASSET_TYPE_STOCK)
    rate_watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)
    future_asset = FinancialAsset(symbol="PAMP/AGO21", asset_type=ASSET_TYPE_FUTURE)
    underlying_asset = FinancialAsset(symbol="PAMP.BA", asset_type=ASSET_TYPE_STOCK)
    rate_watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)
    future_asset = FinancialAsset(symbol="YPFD/AGO21", asset_type=ASSET_TYPE_FUTURE)
    underlying_asset = FinancialAsset(symbol="YPFD.BA", asset_type=ASSET_TYPE_STOCK)
    rate_watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)
    future_asset = FinancialAsset(symbol="DLR/AGO21", asset_type=ASSET_TYPE_FUTURE)
    underlying_asset = FinancialAsset(symbol="DLR", asset_type=ASSET_TYPE_CURRENCY)
    rate_watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)
    future_asset = FinancialAsset(symbol="DLR/SEP21", asset_type=ASSET_TYPE_FUTURE)
    underlying_asset = FinancialAsset(symbol="DLR", asset_type=ASSET_TYPE_CURRENCY)
    rate_watch_list.add_watch_pair(future_asset=future_asset, underlying_asset=underlying_asset)

    print("Lista de futuros a monitorear:")
    for future in rate_watch_list.get_watch_symbols():
        print(future)
    # Lista de futuros a monitorear
    # 'GGAL/AGO21'
    # 'PAMP/AGO21'
    # 'YPFD/AGO21'
    # 'DLR/AGO21'
    # 'DLR/SEP21'

    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='PAMP/AGO21', future_bid_price=115.4, future_bid_size=10,
                                          future_ask_price=119.55, future_ask_size=15)

    # PAMP/AGO21 Spot ask: $109.9 Future bid: $115.4 Tasa colocadora: TNA 26.10% TEA 29.00%
    # PAMP/AGO21 Spot bid: $109.8 Future ask: $119.55 Tasa tomadora: TNA 46.30% TEA 55.83%
    # Mejor tasa colocadora a 70 dias: 26.10% (PAMP/AGO21, 10 unidades, $1154.00)
    # Mejor tasa tomadora a 70 dias: 46.30% (PAMP/AGO21, 15 unidades, $1793.25)


    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='DLR/AGO21', future_bid_price=101.1, future_bid_size=100,
                                          future_ask_price=101.22, future_ask_size=400)

    # DLR/AGO21 Spot ask: $100.8 Future bid: $101.1 Tasa colocadora: TNA 1.55% TEA 1.56%
    # DLR/AGO21 Spot bid: $94.8 Future ask: $101.22 Tasa tomadora: TNA 35.31% TEA 40.73%
    # Mejor tasa colocadora a 70 dias: 26.10% (PAMP/AGO21, 10 unidades, $1154.00)
    # Mejor tasa tomadora a 70 dias: 35.31% (DLR/AGO21, 400 unidades, $40488.00)


    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='YPFD/AGO21', future_bid_price=921, future_bid_size=7,
                                          future_ask_price=931, future_ask_size=4)

    # YPFD/AGO21 Spot ask: $850.0 Future bid: $921 Tasa colocadora: TNA 43.55% TEA 51.94%
    # YPFD/AGO21 Spot bid: $847.55 Future ask: $931 Tasa tomadora: TNA 51.34% TEA 63.18%
    # Mejor tasa colocadora a 70 dias: 43.55% (YPFD/AGO21, 7 unidades, $6447.00)
    # Mejor tasa tomadora a 70 dias: 35.31% (DLR/AGO21, 400 unidades, $40488.00)
    #
    # Colocar tasa
    # Comprar YPFD.BA: 7 x $850.00 = $-5950.00 (incl. costos)
    # Vender YPFD/AGO21: 7 x $921.00 = $6447.00 (incl. costos)
    # Tomar tasa
    # Vender DLR: 68 x $94.80 = $6446.40 (incl. costos)
    # Comprar DLR/AGO21: 68 x $101.22 = $-6882.96 (incl. costos)
    # Flujos netos: $496.40 (2021-06-22) $-435.96 (2021-08-31)
    # Ganancia neta: $60.44 (70 dias)


    print()
    # Este futuro tiene una fecha de vencimiento distinta
    rate_watch_list.search_rate_arbitrage(future_symbol='DLR/SEP21', future_bid_price=103.6, future_bid_size=200,
                                          future_ask_price=103.8, future_ask_size=250)

    # DLR/SEP21 Spot ask: $100.8 Future bid: $103.6 Tasa colocadora: TNA 10.14% TEA 10.52%
    # DLR/SEP21 Spot bid: $94.8 Future ask: $103.8 Tasa tomadora: TNA 34.65% TEA 39.24%
    # Mejor tasa colocadora a 100 dias: 10.14% (DLR/SEP21, 200 unidades, $20720.00)
    # Mejor tasa tomadora a 100 dias: 34.65% (DLR/SEP21, 250 unidades, $25950.00)


    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='GGAL/AGO21', future_bid_price=168.1, future_bid_size=18,
                                          future_ask_price=168.95, future_ask_size=14)

    # GGAL/AGO21 Spot ask: $160.4 Future bid: $168.1 Tasa colocadora: TNA 25.03% TEA 27.70%
    # GGAL/AGO21 Spot bid: $160.3 Future ask: $168.95 Tasa tomadora: TNA 28.14% TEA 31.53%
    # Mejor tasa colocadora a 70 dias: 26.10% (PAMP/AGO21, 10 unidades, $1154.00)
    # Mejor tasa tomadora a 70 dias: 28.14% (GGAL/AGO21, 14 unidades, $2365.30)

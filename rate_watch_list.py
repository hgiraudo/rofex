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

        # Actualiza las listas de tasas, cantidades y precios de mercado
        self.short_rate[days_to_maturity][future_symbol] = nominal_short_rate
        self.short_rate_quantity[days_to_maturity][future_symbol] = future_ask_size
        self.long_rate[days_to_maturity][future_symbol] = nominal_long_rate
        self.long_rate_quantity[days_to_maturity][future_symbol] = future_bid_size
        self.market_bid_price[future_symbol] = future_bid_price
        self.market_ask_price[future_symbol] = future_ask_price
        self.market_bid_price[underlying_asset_symbol] = spot_bid_price
        self.market_ask_price[underlying_asset_symbol] = spot_ask_price

        # Toma las listas de futuros que tienen la misma madurez que el actual
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

        # Busca las cantidades y precios subastados
        best_short_quantity = current_short_rate_quantity[best_short_future]
        best_short_investment = self.market_ask_price[best_short_future] * best_short_quantity
        best_long_quantity = current_long_rate_quantity[best_long_future]
        best_long_investment = self.market_bid_price[best_long_future] * best_long_quantity

        print(f"Mejor tasa colocadora a {days_to_maturity} dias: {best_long_rate:.2%} ({best_long_future}, "
              f"{best_long_quantity} unidades, ${best_long_investment}) ")
        print(f"Mejor tasa tomadora a {days_to_maturity} dias: {best_short_rate:.2%} ({best_short_future}, "
              f"{best_short_quantity} unidades, ${best_short_investment}) ")

        if nominal_long_rate > best_short_rate:
            print("Oportunidad tipo I")

        if nominal_short_rate < best_long_rate:

            # Tasa colocadora: tomar datos del mejor par de activos
            sell_future = best_long_future
            sell_future_max_quantity = best_long_quantity
            sell_future_price = self.market_bid_price[sell_future]
            buy_underlying_asset = self.get_underlying_asset(best_long_future).symbol
            buy_underlying_asset_price = self.market_ask_price[buy_underlying_asset]
            print("Colocar tasa", buy_underlying_asset, buy_underlying_asset_price, sell_future, sell_future_price)

            # Tasa tomadora: comprar el futuro del evento y vender en corto el subyacente
            sell_underlying_asset = underlying_asset.symbol
            sell_underlying_asset_price = spot_bid_price
            buy_future = future_symbol
            buy_future_price = future_ask_price
            buy_future_max_quantity = future_ask_size
            print("Tomar tasa", buy_future, buy_future_price, sell_underlying_asset, sell_underlying_asset_price)

            # El monto a invertir está limitado por el bid_size
            short_max_investment = buy_underlying_asset_price * sell_future_max_quantity
            long_max_investment = buy_future_max_quantity * sell_underlying_asset_price
            print("Tasa colocadora", buy_underlying_asset_price, sell_future_max_quantity, short_max_investment)
            print("Tasa tomadora", sell_underlying_asset_price, buy_future_max_quantity, long_max_investment)




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
    print(list(rate_watch_list.get_watch_symbols()))
    # ['GGAL/AGO21', 'PAMP/AGO21', 'YPFD/AGO21', 'DLR/AGO21', 'DLR/SEP21']

    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='PAMP/AGO21', future_bid_price=115.4, future_bid_size=10,
                                          future_ask_price=119.55, future_ask_size=15)

    # PAMP/AGO21 Spot bid: $105.0 Future ask: $119.55 Tasa tomadora: TNA 71.24% TEA 94.87%
    # PAMP/AGO21 Spot ask: $113.0 Future bid: $115.4 Tasa colocadora: TNA 10.92% TEA 11.41%
    # Mejor tasa colocadora a 71 dias: 10.92% (PAMP/AGO21, 10 unidades, $1154.0)
    # Mejor tasa tomadora a 71 dias: 71.24% (PAMP/AGO21, 15 unidades, $1793.25)

    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='DLR/AGO21', future_bid_price=101.1, future_bid_size=100,
                                          future_ask_price=101.22, future_ask_size=400)

    # DLR/AGO21 Spot bid: $94.71 Future ask: $101.22 Tasa tomadora: TNA 35.34% TEA 40.74%
    # DLR/AGO21 Spot ask: $100.71 Future bid: $101.1 Tasa colocadora: TNA 1.99% TEA 2.01%
    # Mejor tasa colocadora a 71 dias: 10.92% (PAMP/AGO21, 10 unidades, $1154.0)
    # Mejor tasa tomadora a 71 dias: 35.34% (DLR/AGO21, 400 unidades, $40488.0)

    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='YPFD/AGO21', future_bid_price=901.0, future_bid_size=7,
                                          future_ask_price=921, future_ask_size=4)

    # YPFD/AGO21 Spot bid: $820.0 Future ask: $921.0 Tasa tomadora: TNA 63.32% TEA 81.69%
    # YPFD/AGO21 Spot ask: $860.0 Future bid: $901.0 Tasa colocadora: TNA 24.51% TEA 27.05%
    # Mejor tasa colocadora a 71 dias: 24.51% (YPFD/AGO21, 7 unidades, $6307.0)
    # Mejor tasa tomadora a 71 dias: 35.34% (DLR/AGO21, 400 unidades, $40488.0)

    print()
    # Este futuro tiene una fecha de vencimiento distinta
    rate_watch_list.search_rate_arbitrage(future_symbol='DLR/SEP21', future_bid_price=103.6, future_bid_size=200,
                                          future_ask_price=103.8, future_ask_size=250)

    # DLR/SEP21 Spot bid: $94.71 Future ask: $103.8 Tasa tomadora: TNA 34.68% TEA 39.26%
    # DLR/SEP21 Spot ask: $100.71 Future bid: $103.6 Tasa colocadora: TNA 10.37% TEA 10.77%
    # Mejor tasa colocadora a 101 dias: 10.37% (DLR/SEP21, 200 unidades, $20720.0)
    # Mejor tasa tomadora a 101 dias: 34.68% (DLR/SEP21, 250 unidades, $25950.0)

    print()
    rate_watch_list.search_rate_arbitrage(future_symbol='GGAL/AGO21', future_bid_price=168.1, future_bid_size=18,
                                          future_ask_price=168.95, future_ask_size=14)

    # GGAL/AGO21 Spot bid: $161.5 Future ask: $168.95 Tasa tomadora: TNA 23.71% TEA 26.09%
    # GGAL/AGO21 Spot ask: $163.4 Future bid: $168.1 Tasa colocadora: TNA 14.79% TEA 15.69%
    # Mejor tasa colocadora a 71 dias: 24.51% (YPFD/AGO21, 7 unidades, $6307.0)
    # Mejor tasa tomadora a 71 dias: 23.71% (GGAL/AGO21, 14 unidades, $2365.3)

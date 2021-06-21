from asset import *
import etc

class RateWatchList:

    def __init__(self, transaction_cost):
        self.watch_list = dict()
        self.short_rate = dict()
        self.long_rate = dict()
        self.short_rate_quantity = dict()
        self.long_rate_quantity = dict()
        self.transaction_cost = transaction_cost

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

    def get_watch_symbols(self):
        watch_symbols = self.watch_list.keys()
        return watch_symbols

    # Chequea si hay alguna oportunidad de arbitraje de tasas
    # Recibe un evento de market data (e.g. GGAL/AGO21 bid=$170 x 20 unidades, ask=$172 x 10 unidades)
    def search_rate_arbitrage(self, future_symbol, future_bid_price, future_bid_size,
                              future_ask_price, future_ask_size):

        # Calcula las tasas implícitas para el evento de market data recibido
        underlying_asset = self.watch_list[future_symbol]['underlying_asset']
        spot_ask_price = underlying_asset.ask_price()
        spot_bid_price = underlying_asset.bid_price()
        future_asset = self.watch_list[future_symbol]['future_asset']
        days_to_maturity = future_asset.days_to_maturity
        nominal_short_rate, nominal_long_rate = etc.implicit_rates(
            asset=future_symbol, spot_ask_price=spot_ask_price, spot_bid_price=spot_bid_price,
            future_bid_price=future_bid_price, future_ask_price=future_ask_price,
            days_to_maturity=days_to_maturity, transaction_cost=self.transaction_cost)

        # Actualiza las listas de tasas y cantidades
        self.short_rate[days_to_maturity][future_symbol] = nominal_short_rate
        self.short_rate_quantity[days_to_maturity][future_symbol] = future_ask_size
        self.long_rate[days_to_maturity][future_symbol] = nominal_long_rate
        self.long_rate_quantity[days_to_maturity][future_symbol] = future_bid_size

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

        # Busca las cantidades subastadas
        best_short_quantity = current_short_rate_quantity[best_short_future]
        best_long_quantity = current_long_rate_quantity[best_long_future]

        print(f"Mejor tasa colocadora: {best_long_rate:.2%} ({best_long_future}, {best_long_quantity} unidades) "
              f"Mejor tasa tomadora: {best_short_rate:.2%} ({best_short_future}, {best_short_quantity} unidades) ")

        if nominal_long_rate > best_short_rate:
            print("Oportunidad tipo I")

        if nominal_short_rate < best_long_rate:
            print("Oportunidad tipo II")
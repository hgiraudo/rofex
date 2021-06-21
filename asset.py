
import cotizacion_dolar
import datetime
import rofex
import yahoo_finance

ASSET_TYPE_CURRENCY = 1  # e.g. DLR
ASSET_TYPE_STOCK = 2  # e.g. GGAL.BA, YPFD.BA, PAMP.BA
ASSET_TYPE_FUTURE = 3  # e.g. DLR/AGO21, DLR/SEP21, GGAL/AGO21

class FinancialAsset:

    # get_maturity_date
    # -----------------
    # Determina la fecha de fin de un futuro a partir del nombre del ticker
    # El ticker suele tener la forma xyz/MMMYY donde xyz es el subyacente, MMM es el mes e YY es el año
    # Devuelve un objeto de tipo datetime.date
    #
    # Ejemplo de uso
    # --------------
    # print(FinancialAsset.get_maturity_date("DLR/OCT21"))  # 2021-10-31
    # print(type(FinancialAsset.get_maturity_date("DLR/OCT21")))  # <class 'datetime.date'>

    def get_maturity_date(ticker):
        month_string = ticker.split("/")[1][:3]  # ej: OCT
        month_list = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
        month = month_list.index(month_string) + 1
        year = int(ticker.split("/")[1][3:]) + 2000
        # Para determinar el ultimo dia del mes se busca el primer día del mes siguiente y se resta 1
        maturity_date = datetime.date(year, month + 1, 1)
        maturity_date = maturity_date + datetime.timedelta(days=-1)
        return maturity_date

    # remaining_days (maturity_date)
    # ---------------------------
    # Calcula la cantidad de días entre la fecha actual y una fecha futura
    # Recibe la fecha futura en un string con formato dd-mm-yyyy o un objeto datetime.date
    #
    # Ejemplo de uso:
    # ---------------
    # fecha_string = "31-08-2021"
    # dias = FinancialAsset.remaining_days(fecha_string)
    # print(f"Faltan {dias} dias para el {fecha_string}")  # Faltan 81 dias para el 31-08-2021
    #
    # fecha_date = datetime.date(2021, 8, 31)
    # dias = FinancialAsset.remaining_days(fecha_date)
    # print(f"Faltan {dias} dias para el {fecha_date}")  # Faltan 81 dias para el 2021-08-31

    def remaining_days(maturity_date):
        today = datetime.date.today()
        if isinstance(maturity_date, str):
            maturity_date = datetime.datetime.strptime(maturity_date, "%d-%m-%Y").date()
        remaining_days = (maturity_date - today).days
        if remaining_days == 0:
            remaining_days = 1  # Si el futuro vence hoy, tomar 1 dia para evitar la division por 0
        return remaining_days

    def __init__(self, symbol, asset_type, maturity_date=None):
        self.symbol = symbol
        self.asset_type = asset_type
        if asset_type == ASSET_TYPE_FUTURE:
            if maturity_date is None:
                maturity_date = FinancialAsset.get_maturity_date(symbol)
            self.maturity_date = maturity_date
            self.days_to_maturity = FinancialAsset.remaining_days(maturity_date)
        else:
            self.days_to_maturity = 0

    def ask_price(self):
        if self.asset_type == ASSET_TYPE_CURRENCY:
            if self.symbol == "DLR":
                return cotizacion_dolar.dolar_oficial_venta()
            else:
                return 0
        elif self.asset_type == ASSET_TYPE_FUTURE:
            return rofex.get_ask_price(self.symbol)
        elif self.asset_type == ASSET_TYPE_STOCK:
            return yahoo_finance.get_ask_price(self.symbol)

    def bid_price(self):
        if self.asset_type == ASSET_TYPE_CURRENCY:
            if self.symbol == "DLR":
                return cotizacion_dolar.dolar_oficial_compra()
            else:
                return 0
        elif self.asset_type == ASSET_TYPE_FUTURE:
            return rofex.get_bid_price(self.symbol)
        elif self.asset_type == ASSET_TYPE_STOCK:
            return yahoo_finance.get_bid_price(self.symbol)

    def __str__(self):
        extra_info = ""
        if self.asset_type == ASSET_TYPE_CURRENCY:
            asset_type_string = "Currency"
        elif self.asset_type == ASSET_TYPE_STOCK:
            asset_type_string = "Stock"
        elif self.asset_type == ASSET_TYPE_FUTURE:
            asset_type_string = "Future"
            extra_info = f" Maturity date:{self.maturity_date}"
        else:
            asset_type_string = "Unknown"
        return f"<class 'FinancialAsset'> Symbol:{self.symbol} Type:{asset_type_string}{extra_info}"

if __name__ == "__main__":

    dolar = FinancialAsset(symbol="DLR", asset_type=ASSET_TYPE_CURRENCY)
    print(f"{dolar} Ask price:${dolar.ask_price()} Bid price:${dolar.bid_price()}")

    ggalago21 = FinancialAsset(symbol="GGAL/AGO21", asset_type=ASSET_TYPE_FUTURE)
    print(f"{ggalago21} Ask price:${ggalago21.ask_price()} Bid price:${ggalago21.bid_price()}")

    ggal = FinancialAsset(symbol="GGAL.BA", asset_type=ASSET_TYPE_STOCK)
    print(f"{ggal} Ask price:${ggal.ask_price()} Bid price:${ggal.bid_price()}")

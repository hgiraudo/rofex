# cotizacion_dolar.py
# -------------------
# Este modulo contiene funciones que devuelven la cotizacion actual del dolar
# Tipos de cotizacion disponibles: oficial, bolsa, blue, turista, contado con liquidacion y soja
# Los datos se obtienen de www.dolarsi.com
# Todas las funciones devuelven un valor de tipo float
#
# Ejemplos de uso
# ---------------
# print(dolar_oficial_promedio())  # 97.37
# compra, venta = dolar(TIPO_COTIZACION_BLUE)
# print(compra, venta)  # 152.0 157.0

import requests

# Constantes
# Se usan para espeicificar el tipo de cotizacion de dolar
# El texto de cada constante coincide con el del JSON que devuelve el web service
TIPO_COTIZACION_OFICIAL = 'Dolar Oficial'
TIPO_COTIZACION_BOLSA = 'Dolar Bolsa'
TIPO_COTIZACION_BLUE = 'Dolar Blue'
TIPO_COTIZACION_TURISTA = 'Dolar turista'
TIPO_COTIZACION_CCL = 'Dolar Contado con Liqui'
TIPO_COTIZACION_SOJA = 'Dolar Soja'

DOLAR_URL_API = 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'

# dolar(tipo_cotizacion)
# ----------------------
# Devuelve el valor de commpra y venta de un tipo de dolar
# El parametro indica si se trata de dolar blue, oficial, bolsa
#
# Ejemplo de uso:
# compra, venta = dolar(TIPO_COTIZACION_BLUE)
# print(compra, venta)  # 152.0 157.0

def dolar(tipo_cotizacion) :

    json = requests.get(DOLAR_URL_API).json()

    # json tiene una lista de diccionarios
    # Cada diccionario contiene la cotizacion de un tipo de dolar distinto: Oficial, Blue, CCL, Soja
    for dict_outer in json:

        # El valor almacenado en cada diccionario es a su vez otro diccionario
        for dict_inner in dict_outer.values():

          if dict_inner['nombre'] == tipo_cotizacion:
                compra = dict_inner['compra']
                venta = dict_inner['venta']
                # La API devuelve un string con separador decimal coma (Ej: 165,25).
                # Cambiar el separador decimal por un punto para poder convertir a float.
                compra = float(compra.replace(',', '.'))
                venta = float(venta.replace(',', '.'))
                return compra, venta

# dolar_oficial_promedio()
# ----------------------
# Devuelve el promedio entre el valor de compra y venta del dolar oficial

def dolar_oficial_promedio ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return (compra + venta) / 2

def dolar_oficial_venta ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return venta

def dolar_oficial_compra ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return compra


# dolar_oficial()
# ----------------------
# Devuelve el valor de compra y venta del dolar oficial

def dolar_oficial ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return compra, venta

# dolar_oficial_venta()
# ----------------------
# Devuelve el valor de venta actual del dolar oficial

def dolar_oficial_venta ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return venta

# dolar_oficial_compra()
# ----------------------
# Devuelve el valor de compra actual del dolar oficial

def dolar_oficial_compra ():
    compra, venta = dolar(TIPO_COTIZACION_OFICIAL)
    return compra


if __name__ == "__main__":
    cotizacion = dolar_oficial_promedio()
    print(cotizacion)  # e.g. 97.37
    print(type(cotizacion))  # <class 'float'>
    compra, venta = dolar_oficial()
    print(compra, venta)  # 94.71 100.71
    compra, venta = dolar(TIPO_COTIZACION_BLUE)
    print(compra, venta)  # 159.0 164.0

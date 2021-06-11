
import pyRofex
import time
import json

# Set the the parameter for the REMARKET environment
pyRofex.initialize(user="hgiraudo2113",
                   password="ncwywX7(",
                   account="REM2113",
                   environment=pyRofex.Environment.REMARKET)

# First we define the handlers that will process the messages and exceptions.
def market_data_handler(message):
    print("Market Data Message Received: {0}".format(message))
def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))
def error_handler(message):
    print("Error Message Received: {0}".format(message))
def exception_handler(e):
    print("Exception Occurred: {e}", e)
    # print("Exception Occurred: {0}".format(e.message))

# Initiate Websocket Connection
pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                  order_report_handler=order_report_handler,
                                  error_handler=error_handler,
                                  exception_handler=exception_handler)


# Subscribes to receive order report messages (default account will be used) **
pyRofex.order_report_subscription()

while True:
    print("waiting ...")
    time.sleep(300)








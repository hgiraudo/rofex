import pyRofex

# Set the the parameter for the REMARKET environment
pyRofex.initialize(user="hgiraudo2113",
                   password="ncwywX7(",
                   account="REM2113",
                   environment=pyRofex.Environment.REMARKET)

# Makes a request to the Rest API and get the last price
# Use the MarketDataEntry enum to specify the data
get_market_data = pyRofex.get_market_data(ticker="DLR/JUL21",
                        entries=[pyRofex.MarketDataEntry.BIDS, pyRofex.MarketDataEntry.OFFERS])
print(get_market_data)

get_market_data = pyRofex.get_market_data(ticker="DLR/AGO21")
print(get_market_data)

get_market_data = pyRofex.get_market_data(ticker="USD CAJA CAJA",
                       entries=[pyRofex.MarketDataEntry.LAST])
print(get_market_data)

# Gets available instruments list
get_all_instruments = pyRofex.get_all_instruments()
print(get_all_instruments)



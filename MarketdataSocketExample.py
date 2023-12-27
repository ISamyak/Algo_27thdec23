from datetime import datetime

from Connect import XTSConnect
from MarketDataSocketClient import MDSocket_io
import threading
import time
import json

# MarketData API Credentials
API_KEY = "27cb3075e6f28484597669"
API_SECRET = "Vfrx866#y0"
clientID = "D0253276"
source = "WEBAPI"

# Initialise
xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.interactive_login()
# print(response)
# Login for authorization token
# response = xt.marketdata_login()
# print(response)

# Store the token and userid
set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID']
# print("Login: ", response)

# Connecting to Marketdata socket
soc = MDSocket_io(set_marketDataToken, set_muserID)

# Instruments for subscribing
Instruments = [
                {'exchangeSegment': 1, 'exchangeInstrumentID': 26000},
               ]

# Callback for connection
def on_connect():
    """Connect from the socket."""
    # print('Market Data Socket connected successfully!')

    # # Subscribe to instruments
    # print('Sending subscription request for Instruments - \n' + str(Instruments))
    response = xt.send_subscription(Instruments, 1501)

    print("Subscription response: ", response)# print('Sent Subscription request!')
    
    time.sleep(10)
    print(response['result']['listQuotes'][0])

# Callback on receiving message
def on_message(data):
    print('I received a message!')

# Callback for message code 1501 FULL
def on_message1501_json_full(data):
    print('I received a 1501 Touchline message!' + data)

# Callback for message code 1502 FULL
def on_message1502_json_full(data):
    print('I received a 1502 Market depth message!' + data)

# Callback for message code 1505 FULL
def on_message1505_json_full(data):
    print('I received a 1505 Candle data message!' + data)

# Callback for message code 1507 FULL
def on_message1507_json_full(data):
    print('I received a 1507 MarketStatus data message!' + data)

# Callback for message code 1510 FULL
def on_message1510_json_full(data):
    print('I received a 1510 Open interest message!' + data)

# Callback for message code 1512 FULL
def on_message1512_json_full(data):
    print('I received a 1512 Level1,LTP message!' + data)

# Callback for message code 1105 FULL
def on_message1105_json_full(data):
    print('I received a 1105, Instrument Property Change Event message!' + data)


# Callback for message code 1501 PARTIAL
def on_message1501_json_partial(data):
    # print('I received a 1501, Touchline Event message!' + data)
    response = xt.send_subscription(Instruments, 1501)

    print("Subscription response: ", response)
    # print('Sent Subscription request!')
    
    time.sleep(10)
    data_dict = json.loads(response['result']['listQuotes'][0])
    average_traded_price = data_dict.get('AverageTradedPrice')
    print(average_traded_price)

# Callback for message code 1502 PARTIAL
def on_message1502_json_partial(data):
    print('I received a 1502 Market depth message!' + data)

# Callback for message code 1505 PARTIAL
def on_message1505_json_partial(data):
    print('I received a 1505 Candle data message!' + data)

# Callback for message code 1510 PARTIAL
def on_message1510_json_partial(data):
    print('I received a 1510 Open interest message!' + data)

# Callback for message code 1512 PARTIAL
def on_message1512_json_partial(data):
    print('I received a 1512, LTP Event message!' + data)



# Callback for message code 1105 PARTIAL
def on_message1105_json_partial(data):
    print('I received a 1105, Instrument Property Change Event message!' + data)

# Callback for disconnection
def on_disconnect():
    print('Market Data Socket disconnected!')


# Callback for error
def on_error(data):
    """Error from the socket."""
    print('Market Data Error', data)


# Assign the callbacks.
soc.on_connect = on_connect
soc.on_message = on_message
soc.on_message1502_json_full = on_message1502_json_full
soc.on_message1505_json_full = on_message1505_json_full
soc.on_message1507_json_full = on_message1507_json_full
soc.on_message1510_json_full = on_message1510_json_full
soc.on_message1501_json_full = on_message1501_json_full
soc.on_message1512_json_full = on_message1512_json_full
soc.on_message1105_json_full = on_message1105_json_full
soc.on_message1502_json_partial = on_message1502_json_partial
soc.on_message1505_json_partial = on_message1505_json_partial
soc.on_message1510_json_partial = on_message1510_json_partial
soc.on_message1501_json_partial = on_message1501_json_partial
soc.on_message1512_json_partial = on_message1512_json_partial
soc.on_message1105_json_partial = on_message1105_json_partial
soc.on_disconnect = on_disconnect
soc.on_error = on_error


# Event listener
el = soc.get_emitter()
el.on('connect', on_connect)
el.on('1501-json-full', on_message1501_json_full)
el.on('1502-json-full', on_message1502_json_full)
el.on('1507-json-full', on_message1507_json_full)
el.on('1512-json-full', on_message1512_json_full)
el.on('1105-json-full', on_message1105_json_full)
el.on('on_message1501_json_partial',on_message1501_json_partial)
# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
soc.on_message1501_json_partial('ap')


# def color_picture(callback):
#     print("Picture colored!")
#     # Pretend this is some task taking time
#     # Simulating the callback asynchronously after 5 seconds
#     threading.Timer(5, callback).start()

# # This is your sticker function
# def add_stickers():
#     print("Stickers added!")
#     # Infinite loop
#     while True:
#         print("hELLO")
#         time.sleep(5)

# # This is where the magic happens
# color_picture(add_stickers)

# # Any code here won't run because the infinite loop above blocks the execution
# print("This won't get printed!")
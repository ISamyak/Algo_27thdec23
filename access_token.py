# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 16:49:08 2022

@author: dell
"""

import pandas as pd
from Connect import XTSConnect
from InteractiveSocketClient import OrderSocket_io

API_KEY = "7dd103a44fac400d11d742"
API_SECRET = "Lwjy828$NJ"
source = "WEBAPI"
User_id = 'DM343'
#'userID': 'DM343'
# Initialise
xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.interactive_login()
set_interactiveToken = response['result']['token']
set_iuserID = response['result']['userID']
print("Login: ", response)


order_book = xt.get_order_book(User_id) 


##GET MARKET DATA ##############################################################################################
################################################################################################################
###RETRIEVE MARKET DATA ############################################


xt_market_api = "bc2d07c50722c74280d942"
xt_market_secret = "Obgw320@cl"
source = "WEBAPI"
xt_marketdata = XTSConnect(xt_market_api, xt_market_secret, source)
response_mar = xt.marketdata_login()
instruments = [{'exchangeSegment': 2, 'exchangeInstrumentID': 2885},{'exchangeSegment': 1, 'exchangeInstrumentID': 22}]
response_quote = xt.get_quote(
		Instruments=instruments,
		xtsMessageCode=1502,
		publishFormat='JSON')
#xt.comm = {'instruments'}

response_md = xt.get_ohlc(
    exchangeSegment=xt.EXCHANGE_NSECM,
    exchangeInstrumentID=22,
    startTime='Dec 16 2019 090000',
    endTime='Dec 18 2019 150000',
    compressionValue=1)


response_stock = xt.get_equity_symbol(
    exchangeSegment=1,
    series='EQ',
    symbol='Acc')
print('Equity Symbol:', str(response))
response_stock[0]


{'type': 'success',
 'code': 's-rds-0',
 'description': 'ok',
 'result': [{'ExchangeSegment': 1,
   'ExchangeInstrumentID': 22,
   'InstrumentType': 8,
   'Name': 'ACC',
   'DisplayName': 'ACC',
   'Description': 'ACC LIMITED-EQ',
   'Series': 'EQ',
   'NameWithSeries': 'ACC-EQ',
   'InstrumentID': 1100100000022,
   'PriceBand': {'High': 2902.35,
    'Low': 2374.65,
    'HighString': '2902.35',
    'LowString': '2374.65',
    'CreditRating': '2374.65-2902.35',
    'HighExecBandString': '0.00',
    'LowExecBandString': '0.00',
    'HighExecBand': 0,
    'LowExecBand': 0,
    'TERRange': '0.00-0.00'},
   'FreezeQty': 37745,
   'TickSize': 0.05,
   'LotSize': 1}]}
def on_connect():
    
    print('its connected')


    

response_order_placement = xt.place_order(
    exchangeSegment=xt.EXCHANGE_NSECM,
    exchangeInstrumentID=2885, 
    productType=xt.PRODUCT_MIS,
    orderType=xt.ORDER_TYPE_MARKET,
    orderSide=xt.TRANSACTION_TYPE_BUY,
    timeInForce=xt.VALIDITY_DAY,
    disclosedQuantity=0,
    orderQuantity=10,
    limitPrice=0,
    stopPrice=0,
    orderUniqueIdentifier="454845")



"""Cancel Orders Request"""
    response = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='454845')

































    

        

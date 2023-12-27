# from Connect import XTSConnect
# import json
# import time
# import math
# from datetime import datetime, timedelta

# """Investor client credentials"""
# API_KEY = "1206051bd8cc6678f59533"
# API_SECRET = "Wsjl454$9k"
# clientID = "D0253246"
# #userID = "D0253246"
# XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
# source = "WEBAPI"

# xt = XTSConnect(API_KEY, API_SECRET, source)
# print(XTSConnect(API_KEY, API_SECRET, source))
# response = xt.interactive_login()

# instruments = [
#     {'exchangeSegment':1, 'exchangeInstrumentID':26000,},
#     ]   

# instruments_OI = []

# # print("\n Current time: ",datetime.now())  
# Specify_the_Market_Open_TIME_HHMM = '0914'
# Specify_the_Open_TIME_HHMM = '1000'
# curr_dt = time.strftime("%Y%m%d", time.localtime())
# set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM
# set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
# # print("\n Order placement TIME configured as : ",set_order_placement_time_first)
# curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

# """ To get Spot Price of Nifty"""
# response = xt.get_quote(
#     Instruments=instruments,
#     xtsMessageCode=1512,
#     publishFormat='JSON')
# #print('Quote :', response['result']['listQuotes'][0])
# json_string = response['result']['listQuotes'][0]
# data = json.loads(json_string)
# Nifty_SP=data['LastTradedPrice']
# print('Spot Price:',data['LastTradedPrice'])

# OI_Data = [[None] * 7 for _ in range(15)]
# i=0
# j=0

# t=0
# while(curr_tm_chk >= set_previous_oi and t==0):
#     """ To get Instrument id of Near By price"""
#     Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%50)
#     #print("Strike" + "  "+ "Call"+"  "+"  "+"OI_C"+"   "+"Put" +"  "+ " OI_P")
#     while Nifty_SP+350> Nifty_Strike:
#         #print(Nifty_Strike,end="  ")
#         OI_Data[i][j]=Nifty_Strike
#         j=j+1
#         response = xt.get_option_symbol(
#             exchangeSegment=2,
#             series='OPTIDX',
#             symbol='NIFTY',
#             expiryDate='02Mar2023',
#             optionType='CE',
#             strikePrice=Nifty_Strike)
#         #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
#         OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
#         j=j+1

#         instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
#         temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
#         instruments_OI.append(temp)

#         response = xt.get_quote(
#             Instruments=instrument,
#             xtsMessageCode=1510,
#             publishFormat='JSON')
#         #print(response)
#         json_string = response['result']['listQuotes'][0]
#         data=json.loads(json_string)
#         OpenInterest=data["OpenInterest"]
#         #print(OpenInterest,end="  ")
#         OI_Data[i][j]=OpenInterest/50
#         j=j+1

#         response = xt.get_option_symbol(
#             exchangeSegment=2,
#             series='OPTIDX',
#             symbol='NIFTY',
#             expiryDate='02Mar2023',
#             optionType='PE',
#             strikePrice=Nifty_Strike)
#         #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
#         OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
#         j=j+1
#         instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
#         temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
#         instruments_OI.append(temp)
#         response = xt.get_quote(
#             Instruments=instrument,
#             xtsMessageCode=1510,
#             publishFormat='JSON')
#         json_string = response['result']['listQuotes'][0]
#         data=json.loads(json_string)
#         OpenInterest=data["OpenInterest"]
#         #print(OpenInterest,end="  ")
#         OI_Data[i][j]=OpenInterest/50

        
#         j=0
#         i=i+1  
#         #print()
#         Nifty_Strike=Nifty_Strike+50
#         t=1


# col_values_CE=[]
# col_values_PE=[]

# #Ready Instrument Near Spot Price 
# t=0
# while(curr_tm_chk >= set_previous_oi and t==0):
#     response = xt.get_quote(
#         Instruments=instruments,
#         xtsMessageCode=1512,
#         publishFormat='JSON')
# #print('Quote :', response['result']['listQuotes'][0])
#     json_string = response['result']['listQuotes'][0]
#     data = json.loads(json_string)
#     Nifty_SP=data['LastTradedPrice']
#     print('Spot Price:',data['LastTradedPrice'])

#     response = xt.get_quote(
#             Instruments=instruments_OI,
#             xtsMessageCode=1510,
#             publishFormat='JSON')
#     #print(response)
#     for i in range(30):
#         json_string = response['result']['listQuotes'][i]
#         data=json.loads(json_string)
#         OpenInterest=data["OpenInterest"]
#         if i%2==0:
#             Change=abs((OpenInterest/50)-OI_Data[int(i/2)][j+2])
#             col_values_CE.append(Change)
#             OI_Data[int(i/2)][j+5]=Change
#         else:
#             Change=abs((OpenInterest/50)-OI_Data[int(i/2)][j+4])
#             col_values_PE.append(Change)
#             OI_Data[int(i/2)][j+6]=Change
#     print("Strike" + "  "+ "Call"+"  "+"  "+"OI_C"+"   "+"Put" +"  "+ " OI_P" +" " + "Change in C_OI" +"   "+ "Change in P_OI")
#     for rows in OI_Data:
#         print(rows)            






   
#     # print(max(col_values_CE))
#     # print(max(col_values_PE))

# import numpy as np

# # Create a sample 2D array
# A = np.array([[100, 200, 50, 400, 300],
#               [50, 150, 300, 200, 100],
#               [500, 100, 300, 300, 50]])

# # Get the 4th column of the array
# col_4 = A[:, 3]

# # Get the indices of the two maximum values in the column
# max_indices = np.argpartition(col_4, -2)[-2:]

# # Get the maximum values and their corresponding rows
# max_values = col_4[max_indices]
# max_rows = A[max_indices, :]

# print(max_rows)

a=[[100, 200, 50, 400, 300],
[50, 150, 300, 200, 100],
[500, 100, 300, 300, 50]]


for rows in a[-2:]: 
    rows[4]=0

print(a)    

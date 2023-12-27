import numpy as np
from Connect import XTSConnect
import json
import time
import math
from datetime import datetime, timedelta
import pandas as pd
from pandas.tseries.offsets import BDay
import os
import json
from MarketDataSocketClient import MDSocket_io

"""Investor client credentials"""
API_KEY = "27cb3075e6f28484597669"
API_SECRET = "Vfrx866#y0"
clientID = "D0253276"
#userID = "D0253246"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.interactive_login()

day=''
last_day='Dec 27 2023'
"""---- 0 For Midcp Nifty , 1 For Fin ninfty , 2 for Bank Nifty , 3 For Nifty, 4 for Sensex ---"""
index=2
"""for index 4 no cutting tick made , index error + 2nd sp se cutting """
prefix=["MIDCPNIFTY01Jan2024","FINNIFTY26Dec2023","BANKNIFTY28Dec2023","NIFTY28Dec2023","SENSEX29Dec2023"]
exchangeInstrumentID_Number=[26121,26034,26001,26000,26065]
exchangeSegment_Number=[xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_BSECM]

set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID']

soc = MDSocket_io(set_marketDataToken, set_muserID)


def on_message1501_json_partial(data1,data2,Instruments,Atp_ltp_table,SIDE):
    i=0
    rate=0
    rate1=0
    rate_atm=0
    
    response = xt.send_subscription(Instruments, 1501)
    # print("Subscription response: ", response)   
    add_index=0
    add_index1=0
    index_atm=0
    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time =output_date+ " 090000"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    if index==0:
        add_index=125
        add_index1=250
        if float(a1[4])%25<15:
            index_atm=float(a1[4]) - float(a1[4])%25
        else:
            index_atm= float(a1[4]) + (25- float(a1[4])%25)
    elif index==1 or index==3:
        add_index=250
        add_index1=500
        if float(a1[4])%50<30:
            index_atm=float(a1[4]) - float(a1[4])%50
        else:
            index_atm= float(a1[4]) + (50- float(a1[4])%50)
    elif index==2:
        add_index=500
        add_index1=1000
        if float(a1[4])%100<50:
            index_atm=float(a1[4]) - float(a1[4])%100
        else:
            index_atm= float(a1[4]) + (100- float(a1[4])%100)
    elif index==4:
        add_index=500
        add_index1=1000
        if float(a1[4])%100<50:
            index_atm=float(a1[4]) - float(a1[4])%100
        else:
            index_atm= float(a1[4]) + (100- float(a1[4])%100)                                

    quote_strings = response['result']['listQuotes']
    time.sleep(10)
    for quote_str in quote_strings:
        quote_dict = json.loads(quote_str)
        last_traded_price = quote_dict[data2]
        average_traded_price = quote_dict[data1]

        if average_traded_price==0 or average_traded_price==' ':
            average_traded_price=last_traded_price

        if last_traded_price>average_traded_price:
            Atp_ltp_table[i][1]=Atp_ltp_table[i][1]+1
            Atp_ltp_table[i][2]= (((last_traded_price)/average_traded_price)-1)*100
        else:
            Atp_ltp_table[i][1]=0
            if last_traded_price==0 or last_traded_price==' ':
                average_traded_price=1
            Atp_ltp_table[i][2]= (((last_traded_price)/average_traded_price)-1)*100

        if last_traded_price>Atp_ltp_table[i][3]:
            Atp_ltp_table[i][4]=Atp_ltp_table[i][4]+1
        else:
            Atp_ltp_table[i][4]=0    

        if SIDE=='CE' and Atp_ltp_table[i][0]==(index_atm+add_index):
            rate=last_traded_price
        elif SIDE=='PE' and Atp_ltp_table[i][0]==(index_atm - add_index):
            rate=last_traded_price

        if SIDE=='CE' and Atp_ltp_table[i][0]==(index_atm):
            rate_atm=last_traded_price
        elif SIDE=='PE' and Atp_ltp_table[i][0]==(index_atm):
            rate_atm=last_traded_price    

        if SIDE=='CE' and Atp_ltp_table[i][0]==(index_atm+add_index1):
            rate1=last_traded_price
        elif SIDE=='PE' and Atp_ltp_table[i][0]==(index_atm - add_index1):
            rate1=last_traded_price     


        i=i+1
   
    if SIDE=='CE':
        start_index_near = next((i for i, row in enumerate(Atp_ltp_table) if row[0] == index_atm), None)
        subset = [row[2] for row in Atp_ltp_table[start_index_near+1:start_index_near + 9]]
        indexed_data = list(enumerate(subset))

        sorted_data = sorted(indexed_data, key=lambda x: x[1])
        most_negative = sorted_data[:2]
        if most_negative[0][0]<4 and most_negative[1][0]<4:
            print("Near by Jada tuti hui hai")
        else:
            print("Duur ali jada tuti hai - TAKE PROTECTION OF CALL ")            
        # for index_no, value in most_negative:
        #     print(f"Index: {index_no}, Value: {value}")
    # print(Atp_ltp_table)    
    if SIDE=='PE':

        start_index_near = next((i for i, row in enumerate(Atp_ltp_table) if row[0] == index_atm), None)

        subset = [row[2] for row in Atp_ltp_table[start_index_near-8:start_index_near + 0]]
        indexed_data = list(enumerate(subset))

        sorted_data = sorted(indexed_data, key=lambda x: x[1])
        
        most_negative = sorted_data[:2]
        if most_negative[0][0]>4 and most_negative[1][0]>4:
            print("Near by Jada tuti hui hai")
        else:
            print("Duur wali jada tuti hai - TAKE PROTECTION OF PUT ")    
        
        # for index_no, value in most_negative:
        #     print(f"Index: {index_no}, Value: {value}")    
    return Atp_ltp_table,rate,rate1,rate_atm        

soc.on_message1501_json_partial = on_message1501_json_partial
el = soc.get_emitter()

el.on('on_message1501_json_partial',on_message1501_json_partial)

def change_date_format(date):
    original_format = '%Y%m%d'
    date_object = datetime.strptime(date, original_format)
    output_format = '%b %d %Y'
    return date_object.strftime(output_format)  

def getting_ohlc(opening_time,closing_time):
    response = xt.get_ohlc(
        exchangeSegment=exchangeSegment_Number[index],
        exchangeInstrumentID=exchangeInstrumentID_Number[index],
        startTime=opening_time,
        endTime=closing_time,
        compressionValue=450000)
    a=response['result']['dataReponse'].split('|')
    if a==['']:
        print("1st Wrong data")
        response = xt.get_ohlc(
        exchangeSegment=exchangeSegment_Number[index],
        exchangeInstrumentID=exchangeInstrumentID_Number[index],
        startTime=opening_time,
        endTime=closing_time,
        compressionValue=450000)
        a=response['result']['dataReponse'].split('|')
        if a==['']:
            print("Wrong Data Imp")
            return a
        else:
            return a    
    else:
        return a


def instrument_for_ce_pe_table(Atp_ltp_table_ce,Atp_ltp_table_pe):
    i=0
    """Check before 9:15 and only once"""
    output_opening_time = output_date+ " 090000"
    output_closing_time = output_date+ " 091600"

    last_opening_time = last_day+ " 090000"
    last_closing_time = last_day+ " 153000"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    if a1==['']:
        print("Something in data is wrong - Can't be Ignore")

    Nifty_SP=float(a1[4])
    instrument_for_ce =[]
    instrument_for_pe=[]
    """range to be -350 to +350"""
    if index==3:
        Nifty_Strike=Nifty_SP - 700 - (Nifty_SP%50)
        while Nifty_SP+700 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)


            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_ce[i][3]=float(a[4])

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            if Nifty_Strike==10025:
                print(response['result'][0]['ExchangeInstrumentID'])
            instrument_for_pe.append(temp)
            
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_pe[i][3]=float(a[4])
            i=i+1
            Nifty_Strike=Nifty_Strike+50

        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe    

    elif index==2:
        Nifty_Strike=Nifty_SP - 1400 - (Nifty_SP%100)
        while Nifty_SP+1400 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=float(a[4])
            else:    
                Atp_ltp_table_ce[i][3]=float(a[4])

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_pe[i][3]=float(a[4])

            Nifty_Strike=Nifty_Strike+100
            i=i+1
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe     
    elif index==1:
        Nifty_Strike=Nifty_SP - 700 - (Nifty_SP%50)
        while Nifty_SP+700 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_ce[i][3]=float(a[4])
            
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_pe[i][3]=float(a[4])
            i=i+1
            Nifty_Strike=Nifty_Strike+50
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 
    elif index==0:
        Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%25)
        while Nifty_SP+350 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='CE',
                strikePrice=Nifty_Strike)
    
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_ce[i][3]=float(a[4])

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_pe[i][3]=float(a[4])
            i=i+1
            Nifty_Strike=Nifty_Strike+25
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 
    elif index==4:
        Nifty_Strike=Nifty_SP - 1400 - (Nifty_SP%100)
        
        while Nifty_SP+1400 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            
            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_BSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)

            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_ce[i][3]=float(a[4])

            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_BSEFO,
                exchangeInstrumentID=temp['exchangeInstrumentID'],
                startTime=last_opening_time,
                endTime=last_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                Atp_ltp_table_ce[i][3]=0
            else:    
                Atp_ltp_table_pe[i][3]=float(a[4])
            i=i+1
            Nifty_Strike=Nifty_Strike+100 
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 

def atp_ltp_table_form(instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe):
    Atp_ltp_table_ce,rate1,rate_x,rate_atm_ce=soc.on_message1501_json_partial('AverageTradedPrice','LastTradedPrice',instrument_setup_ce,Atp_ltp_table_ce,'CE')
    Atp_ltp_table_pe,rate2,rate_y,rate_atm_pe=soc.on_message1501_json_partial('AverageTradedPrice','LastTradedPrice',instrument_setup_pe,Atp_ltp_table_pe,'PE')
    
    if rate1*1.35<rate2:
        print("5 SP Away PE Side Mehngi hai Call Side take protection required : Rate CE : "+ str(rate1) + " Rate PE : " + str(rate2))
    elif rate2*1.35<rate1:
        print("5 SP Away CE Side Mehngi hai Put Side take protection required : Rate CE : "+ str(rate1) + " Rate PE : " + str(rate2))
    else:
        print("5 SP Away No Protection as per rate difference: Rate CE : "+ str(rate1) + " Rate PE : " + str(rate2))

    if rate_x*1.35<rate_y:
        print("10 SP Away PE Side Mehngi hai Call Side take protection required : Rate CE : "+ str(rate_x) + " Rate PE : " + str(rate_y))
    elif rate_y*1.35<rate_x:
        print("10 SP Away CE Side Mehngi hai Put Side take protection required : Rate CE : "+ str(rate_x) + " Rate PE : " + str(rate_y))
    else:
        print("10 SP Away No Protection as per rate difference: Rate CE : "+ str(rate_x) + " Rate PE : " + str(rate_y))    

    print("Rate of Pair Value is - "+ str(rate_atm_ce+rate_atm_pe))    

    return Atp_ltp_table_ce,Atp_ltp_table_pe

def delta_left():

    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time =output_date+ " 090000"
    a1=getting_ohlc(output_opening_time,output_closing_time)

    if index==0:
        if float(a1[4])%25<15:
            index_atm=float(a1[4]) - float(a1[4])%25
        else:
            index_atm= float(a1[4]) + (25- float(a1[4])%25)
    elif index==1 or index==3:
        if float(a1[4])%50<30:
            index_atm=float(a1[4]) - float(a1[4])%50
        else:
            index_atm= float(a1[4]) + (50- float(a1[4])%50)
    elif index==2:
        if float(a1[4])%100<50:
            index_atm=float(a1[4]) - float(a1[4])%100
        else:
            index_atm= float(a1[4]) + (100- float(a1[4])%100)
    elif index==4:
        if float(a1[4])%100<50:
            index_atm=float(a1[4]) - float(a1[4])%100
        else:
            index_atm= float(a1[4]) + (100- float(a1[4])%100) 

#ID,oRDER,SIDE, QUANT, LIMIT -hIGH , STOP - EXACT , 
# response=xt.place_order(
#     exchangeSegment="NSEFO",
#     exchangeInstrumentID=63993,
#     productType="NRML",
#     orderType="MARKET",
#     orderSide="BUY",
#     timeInForce="DAY",
#     disclosedQuantity=0,
#     orderQuantity=330,
#     limitPrice=10, 
#     stopPrice=7,
#     orderUniqueIdentifier="Test",
#     clientID="D0253276")
# print(response)

# response=xt.get_trade(clientID="D0253276")

# k=len(response['result'])

# for j in range(k):
#     print(response['result'][j]['AppOrderID'],end="  ")
#     print(response['result'][j]['OrderSide'],end="  ")
#     print(response['result'][j]['TradingSymbol'],end="  ")
#     print(response['result'][j]['OrderQuantity'],end=" ")
#     print(response['result'][j]['OrderAverageTradedPrice'],end=" ")
#     print(response['result'][j]['OrderStatus'],end="  ")
#     if response['result'][j]['OrderStatus']== 'Rejected':
#         print(response['result'][j]['CancelRejectReason'],end="  ")

#     print()


# response=xt.modify_order(
#     appOrderID=1209924498,
#     modifiedProductType="NRML",
#     modifiedOrderType="STOPLIMIT",
#     modifiedOrderQuantity=800,
#     modifiedDisclosedQuantity=0,
#     modifiedLimitPrice=15, 
#     modifiedStopPrice=12,
#     modifiedTimeInForce="DAY",
#     orderUniqueIdentifier="Test",
#     clientID="D0253276"
#     )
# print(response)



response=xt.get_position_daywise(clientID="D0253276")
k=len(response['result']['positionList'])
print("Trading Symbol                   ID       Buy_P   Sell_P      Open_Buy       Open_Sell    Buy_Amo     Sell_Amo    Net_Amo"  )
for j in range(k):
    print(response['result']['positionList'][j]['TradingSymbol'],end="  ")
    print(response['result']['positionList'][j]['ExchangeInstrumentId'],end="       ")
    print(str(round(float(response['result']['positionList'][j]['BuyAveragePrice']),2)),end="        ")
    print(str(round(float(response['result']['positionList'][j]['SellAveragePrice']),2)),end="       ")
    print(response['result']['positionList'][j]['OpenBuyQuantity'],end="        ")
    print(response['result']['positionList'][j]['OpenSellQuantity'],end="       ")
    print(response['result']['positionList'][j]['BuyAmount'],end="      ")
    print(response['result']['positionList'][j]['SellAmount'],end="     ")
    print(response['result']['positionList'][j]['NetAmount'],end="      ")
    print()

'''response=xt.get_position_netwise(clientID="D0253276")
print(response)'''

# response=xt.cancel_order(
#     appOrderID=1209924672,
#     orderUniqueIdentifier="Test",
#     clientID="D0253276"
#     )
# print(response)

# response=xt.cancelall_order(
#     exchangeSegment="BSEFO",
#     exchangeInstrumentID=861958)
# print(response)

response=xt.get_order_book(clientID="D0253276")

k=len(response['result'])

for j in range(k):
    print(response['result'][j]['AppOrderID'],end="  ")
    print(response['result'][j]['OrderSide'],end="  ")
    print(response['result'][j]['TradingSymbol'],end="  ")
    print(response['result'][j]['OrderQuantity'],end=" ")
    print(response['result'][j]['OrderStatus'],end="  ")
    print(response['result'][j]['OrderPrice'],end="  ")
    print(response['result'][j]['OrderStopPrice'],end="  ")
    if response['result'][j]['OrderStatus']== 'Rejected':
        print(response['result'][j]['CancelRejectReason'],end="  ")
    print()

'''response = xt.squareoff_position(
    exchangeSegment="NSEFO",
    exchangeInstrumentID=46077,
    productType="NRML",
    squareOffMode="DayWise",
    positionSquareOffQuantityType="ExactQty",
    squareOffQtyValue=75,
    blockOrderSending=0,
    cancelOrders=0,
    ClientId="D0253276"
    )
print(response)'''



"""wait till 9:15 till market open"""
Specify_the_Market_Open_TIME_HHMM = '0900' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = '0916'  #First 45 Min to get the Max OI Change
curr_dt = time.strftime("%Y%m%d", time.localtime())
set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
while(curr_tm_chk <= set_current_oi ):
    curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

"""Setting OI Data till 9:15 , Strike Price , Previous day OI IN Call and Put , 9:15 Clock OI of Call and Put"""
instruments_OI = []
output_date=change_date_format(curr_dt)
print(output_date)

"""ATP/LTP Table to check the prior nature of market"""
Atp_ltp_table_ce = [[0] * 5 for _ in range(29)]
Atp_ltp_table_pe = [[0] * 5 for _ in range(29)]

instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe =  instrument_for_ce_pe_table(Atp_ltp_table_ce,Atp_ltp_table_pe) 


# response = xt.get_option_symbol(
#     exchangeSegment=2,
#     series='OPTIDX',
#     symbol='BANKNIFTY',
#     expiryDate=prefix[index][9:],
#     optionType='CE',
#     strikePrice=47000)
# print(response['result'][0]['ExchangeInstrumentID'])

"""Wait till 10:00 for stability of market"""
Specify_the_Open_TIME_HHMM = '1930'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
    curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())


    Atp_ltp_table_ce,Atp_ltp_table_pe =  atp_ltp_table_form(instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe)
    i=0
    for row in Atp_ltp_table_ce:
        if i==15:
           print("----------------------Back---------------------------") 
        print(row)
        i=i+1
    print("---------------------------------------------------")
    i=0    
    for row in Atp_ltp_table_pe:
        if i==15:
           print("----------------------Front---------------------------") 
        print(row)
        i=i+1    
    print("---------------------------------------------------")  








                






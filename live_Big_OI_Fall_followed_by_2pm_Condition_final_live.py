from Connect import XTSConnect
from MarketDataSocketClient import MDSocket_io

import json
import time
import math
import json
from datetime import datetime, timedelta
import pandas as pd
from pandas.tseries.offsets import BDay
import os
import numpy as np
import csv
import smtplib
import copy
"""Investor client credentials"""
API_KEY = "1206051bd8cc6678f59533"
API_SECRET = "Wsjl454$9k"
clientID = "D0253246"
#userID = "D0253276"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()
day=''
"""---- 0 For Midcp Nifty , 1 For Fin ninfty , 2 for Bank Nifty , 3 For Nifty, 4 for Sensex ---"""
index=2
"""for index 4 no cutting tick made , index error + 2nd sp se cutting """
prefix=["MIDCPNIFTY01Jan2024","FINNIFTY26Dec2023","BANKNIFTY28Dec2023","NIFTY28Dec2023","SENSEX29Dec2023"]
exchangeInstrumentID_Number=[26121,26034,26001,26000,26065]
exchangeSegment_Number=[xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_NSECM,xt.EXCHANGE_BSECM]

m=2
set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID']

soc = MDSocket_io(set_marketDataToken, set_muserID)


def on_message1501_json_partial(data1,data2,Instruments,Atp_ltp_table):
    i=0
    response = xt.send_subscription(Instruments, 1501)
    # print("Subscription response: ", response)   
    time.sleep(10)
    quote_strings = response['result']['listQuotes']
    for quote_str in quote_strings:
        quote_dict = json.loads(quote_str)
        last_traded_price = quote_dict[data2]
        average_traded_price = quote_dict[data1]
        if last_traded_price>average_traded_price:
            Atp_ltp_table[i][1]=Atp_ltp_table[i][1]+1
            Atp_ltp_table[i][2]= (last_traded_price/average_traded_price)*100
        else:
            Atp_ltp_table[i][1]=0
            Atp_ltp_table[i][2]= (last_traded_price/average_traded_price)*100
        i=i+1    
    return Atp_ltp_table        

soc.on_message1501_json_partial = on_message1501_json_partial
el = soc.get_emitter()

el.on('on_message1501_json_partial',on_message1501_json_partial)

# soc.on_message1501_json_partial('AverageTradedPrice')

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

def previous_day_OI_set_Instrument_set(output_date):
    t=0
    i=0
    j=0
    """Check before 9:15 and only once"""
    output_opening_time = output_date+ " 090000"
    output_closing_time = output_date+ " 091600"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    if a1==['']:
        print("Something in data is wrong - Can't be Ignore")

    Nifty_SP=float(a1[4])
    """range to be -350 to +350"""
    if index==3:
        Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%50)
        while Nifty_SP+400 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:
                OI_Data[i][j]=int(a[6])
            j=j+1

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1
            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])         
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+50

    elif index==2:
        Nifty_Strike=Nifty_SP - 700 - (Nifty_SP%100)
        while Nifty_SP+800 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            # print(response)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:
                OI_Data[i][j]=int(a[6])
            j=j+1

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1
            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:
                OI_Data[i][j]=int(a[6])         
            j=0
            i=i+1  

            Nifty_Strike=Nifty_Strike+100
    elif index==1:
        Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%50)
        while Nifty_SP+400 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            # print(response)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])
            j=j+1

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1
            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])          
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+50
    elif index==0:
        Nifty_Strike=Nifty_SP - 175 - (Nifty_SP%25)
        while Nifty_SP+200 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            # print(response)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)

            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:        
                OI_Data[i][j]=int(a[6])
            j=j+1

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1
            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+25
    elif index==4:
        Nifty_Strike=Nifty_SP - 700 - (Nifty_SP%100)
        
        while Nifty_SP+800 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 12, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_BSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])
            j=j+1

            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1
            instrument = [{'exchangeSegment': 12, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_BSEFO,
                exchangeInstrumentID=instrument[0]['exchangeInstrumentID'],
                startTime=output_opening_time,
                endTime=output_closing_time,
                compressionValue=450000)
            a=response['result']['dataReponse'].split('|')
            if a==['']:
                OI_Data[i][j]=0
            else:    
                OI_Data[i][j]=int(a[6])
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+100        
        

def to_check_data_update(OI,instruments_OI):
    
    response=xt.get_quote(
        Instruments=instruments_OI,
        xtsMessageCode=1510,
        publishFormat='JSON'
        )

    json_string = response['result']['listQuotes'][14]
    json_string1 = response['result']['listQuotes'][15]
    data=json.loads(json_string)
    data1=json.loads(json_string1)
    OpenInterest=data["OpenInterest"]
    OpenInterest1=data1["OpenInterest"]


    if OpenInterest!=OI[7][13]:
        if OpenInterest1!=OI[7][14]:
            print("Data Update")
            return True
        else:
            return False
    else:
        return False    

def update_OI_Data(OI,instruments_OI):
	count=16
	response = xt.get_quote(
			Instruments=instruments_OI,
			xtsMessageCode=1510,
			publishFormat='JSON')
	for i in range((count*2)):
		json_string = response['result']['listQuotes'][i]
		j=0
		data=json.loads(json_string)
		OpenInterest=data["OpenInterest"]
		# print(OpenInterest)
		if i%2==0:
			Change=((OpenInterest)-OI[int(i/2)][j+2])
			OI[int(i/2)][j+11]=OI[int(i/2)][j+9]
			OI[int(i/2)][j+9]=OI[int(i/2)][j+7]
			OI[int(i/2)][j+7]=OI[int(i/2)][j+5]
			OI[int(i/2)][j+5]=Change
			OI[int(i/2)][j+13]=(OpenInterest)
		else:
			Change=((OpenInterest)-OI[int(i/2)][j+4])
			OI[int(i/2)][j+12]=OI[int(i/2)][j+10]
			OI[int(i/2)][j+10]=OI[int(i/2)][j+8]
			OI[int(i/2)][j+8]=OI[int(i/2)][j+6]
			OI[int(i/2)][j+6]=Change	
			OI[int(i/2)][j+14]=(OpenInterest)
		i=i+1   
	return OI	
						
def setting_data_for_Change_info(OI_Data,output_date):
    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time = output_date+ " 090000"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    start_sp=0
    if index==1 or index==3:
        if float(a1[4])%100<25:
            start_sp=float(a1[4])-float(a1[4])%100
        elif float(a1[4])%100>75:
            start_sp=float(a1[4]) + (100 - float(a1[4])%100)
        else:
            if float(a1[4])%100<50:
                start_sp=float(a1[4]) + (50- float(a1[4])%50)
            else:
                start_sp=float(a1[4])-float(a1[4])%50
    elif index==2:
        if float(a1[4])%100<50:
            start_sp=float(a1[4]) - float(a1[4])%100
        else:
            start_sp= float(a1[4]) + (100 - float(a1[4])%100)
    elif index==0:
        if float(a1[4])%25<17:
            start_sp= float(a1[4]) - float(a1[4])%25
        else:
            start_sp =  float(a1[4]) + (25- float(a1[4])%25)
    elif index==4:
        if float(a1[4])%100<50:
            start_sp=float(a1[4]) - float(a1[4])%100
        else:
            start_sp= float(a1[4]) + (100 - float(a1[4])%100)

            
    if index==1 and index==3:
        start_sp=start_sp-100

        for i, row in enumerate(OI_Data):
            if row[0] == start_sp:
                index_of_found_row = i
                break
        new_array = OI_Data[index_of_found_row:index_of_found_row + 5]
        for row in new_array:
            print(row)
        return new_array    

    elif index==2:
        start_sp=start_sp-200

        for i, row in enumerate(OI_Data):
            if row[0] == start_sp:
                index_of_found_row = i
                break
        new_array = OI_Data[index_of_found_row:index_of_found_row + 5]
        for row in new_array:
            print(row)
        return new_array 

    elif index==0:
        start_sp=start_sp-50

        for i, row in enumerate(OI_Data):
            if row[0] == start_sp:
                index_of_found_row = i
                break
        new_array= OI_Data[index_of_found_row:index_of_found_row + 5]
        for row in new_array:
            print(row)
        return new_array
    elif index==4:
        start_sp=start_sp-200

        for i, row in enumerate(OI_Data):
            if row[0] == start_sp:
                index_of_found_row = i
                break
        new_array = OI_Data[index_of_found_row:index_of_found_row + 5]
        for row in new_array:
            print(row)
        return new_array
             
def setting_inner_OI_Data(OI_Data_inner,new_array):
    i=0
    for row in new_array:
        OI_Data_inner[i][0]=row[0]
        OI_Data_inner[i][1]=row[7]+row[2]
        OI_Data_inner[i][2]=row[8]+row[4]
        i=i+1
    return OI_Data_inner    

def big_subtraction_tick(a,b,c,d,e,f,g,h):
    if index==1 or index==3:
        if e-f< -500000 or g-h < -500000:
            return True
        else:
            return False
    elif index==2 or index==0:
        if e-f< -400000 or g-h < -400000:
            return True
        else:
            return False
    elif index==4:
        if e-f<-100000 or g-h<-100000:
            return True
        else:
            return False
    else:
        return False  



def check_for_trade_points(OI_Data_inner,OI_Data,side,trade_distance_ce,trade_distance_pe):
    
    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time = output_date+ " 090000"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    point=0
    OI_add=0
    if index==1 or index==3:
        point=50
        OI_add=1000000
    elif index==0:
        point=25
        OI_add=900000
    elif index==2:
        point=100
        OI_add=700000
    elif index==4:
        point=140
        OI_add=150000
    else:
        point=35
        OI_add=1000000
           
    if side=='PE':        
        for j in range(16):
            if float(a1[4])-point <= OI_Data_inner[j][0] <= float(a1[4])+point:
                if OI_Data[j][13]-OI_Data_inner[j][1]>=OI_add:
                    print("10 lakh added on Strike price - "+ str(OI_Data_inner[j][0]))
                    a = OI_Data[j][6]-OI_Data[j][8]
                    if j==0:
                        b=0
                    else:    
                        b= OI_Data[j-1][6]-OI_Data[j-1][8]
                    if (a <0  and b<=0):
                        print("Subtraction in Both atm or itm Strike price")
                        if j==0:
                            if OI_Data_inner[j][2]-OI_Data[j][14]>0 and  OI_Data_inner[j+1][2]-OI_Data[j+1][14]>0:
                                print("We can initiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))

                            else:
                                print("Addition in ITM and OTM on opposite side don't trade")       
                        else:
                            if (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j+1][14]-OI_Data_inner[j+1][2]) and (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j][14]-OI_Data_inner[j][2]):
                                if (OI_Data[j][13]-OI_Data_inner[j][1])*0.20 >= ( OI_Data[j-1][14]-OI_Data_inner[j-1][2]):
                                    print("less than 20 %  addition in next SP - we can initiate Trade")
                                    print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                else:
                                    if (OI_Data[j-2][14] - OI_Data_inner[j-2][2] > OI_Data[j-1][14] - OI_Data_inner[j-1][2]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    elif a>0 and abs(a)<abs(b) and b<0:
                        print("Bigger -ve tick in ITM put")
                        if j==0:
                            if OI_Data_inner[0][2]-OI_Data[j][14]>0 and  OI_Data_inner[1][2]-OI_Data[j+1][14]>0:
                                print("We can intiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                            else:
                                print("Addition in ITM and OTM on opposite side dont trade")       
                        else:
                            if (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j+1][14]-OI_Data_inner[j+1][2]) and (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j][14]-OI_Data_inner[j][2]):
                                if (OI_Data[j][13]-OI_Data_inner[j][1])*0.20 >= ( OI_Data[j-1][14]-OI_Data_inner[j-1][2]):
                                    print("less than 20 % addition in next SP - we can intiate Trade")
                                    print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                else:
                                    if (OI_Data[j-2][14] - OI_Data_inner[j-2][2] > OI_Data[j-1][14] - OI_Data_inner[j-1][2]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    elif b>0 and abs(b)<abs(a) and a<0:
                        print("Bigger -ve tick in ATM put")
                        if j==0:
                            if OI_Data_inner[0][2]-OI_Data[j][14]>0 and  OI_Data_inner[1][2]-OI_Data[j+1][14]>0:
                                print("We can intiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                            else:
                                print("Addition in ITM and OTM on opposite side dont trade")       
                        else:
                            if (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j+1][14]-OI_Data_inner[j+1][2]) and (OI_Data[j][13] -OI_Data_inner[j][1])*0.10 >= (OI_Data[j][14]-OI_Data_inner[j][2]):
                                if (OI_Data[j][13]-OI_Data_inner[j][1])*0.20 >= ( OI_Data[j-1][14]-OI_Data_inner[j-1][2]):
                                    print("less than 20 % addition in next SP - we can intiate Trade")
                                    print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                else:
                                    if (OI_Data[j-2][14] - OI_Data_inner[j-2][2] > OI_Data[j-1][14] - OI_Data_inner[j-1][2]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_ce) + " points away " + " i.e. " + str( OI_Data_inner[j][0] + trade_distance_ce ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    else:
                        print("No -ve tick in opposite side")
                else:
                    print("Wait")
       
    elif side=='CE':        
        for j in range(16):
            if float(a1[4])-point <= OI_Data_inner[j][0] <= float(a1[4])+point:
                if OI_Data[j][14]-OI_Data_inner[j][2]>=OI_add:
                    print("10 lakh added on Strike price - "+ str(OI_Data_inner[j][0]))
                    a = OI_Data[j][5]-OI_Data[j][7]
                    if j==0:
                        b=0
                    else:    
                        b= OI_Data[j+1][5]-OI_Data[j+1][7]
                    if (a <0  and b<=0):
                        print("Subtraction in Both atm or itm Strike price")
                        if j==9:
                            if OI_Data_inner[j][1]-OI_Data[j][13]>0 and  OI_Data_inner[j-1][1]-OI_Data[j-1][13]>0:
                                print("We can initiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                            else:
                                print("Addition in ITM and OTM on opposite side don't trade")       
                        else:
                            if (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j-1][13]-OI_Data_inner[j-1][1]) and (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j][13]-OI_Data_inner[j][1]):
                                if (OI_Data[j][14]-OI_Data_inner[j][2])*0.20 >= ( OI_Data[j+1][13]-OI_Data_inner[j+1][1]):
                                    print("less than 20 %  addition in next SP - we can initiate Trade")
                                    print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                else:
                                    if (OI_Data[j+2][13] - OI_Data_inner[j+2][1] > OI_Data[j+1][13] - OI_Data_inner[j+1][1]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    elif a>0 and abs(a)<abs(b) and b<0:
                        print("Bigger -ve tick in ITM put")
                        if j==9:
                            if OI_Data_inner[j][1]-OI_Data[j][13]>0 and  OI_Data_inner[j-1][1]-OI_Data[j-1][13]>0:
                                print("We can initiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                            else:
                                print("Addition in ITM and OTM on opposite side don't trade")       
                        else:
                            if (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j-1][13]-OI_Data_inner[j-1][1]) and (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j][13]-OI_Data_inner[j][1]):
                                if (OI_Data[j][14]-OI_Data_inner[j][2])*0.20 >= ( OI_Data[j+1][13]-OI_Data_inner[j+1][1]):
                                    print("less than 20 %  addition in next SP - we can initiate Trade")
                                    print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                else:
                                    if (OI_Data[j+2][13] - OI_Data_inner[j+2][1] > OI_Data[j+1][13] - OI_Data_inner[j+1][1]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    elif b>0 and abs(b)<abs(a) and a<0:
                        print("Bigger -ve tick in ATM put")
                        if j==9:
                            if OI_Data_inner[j][1]-OI_Data[j][13]>0 and  OI_Data_inner[j-1][1]-OI_Data[j-1][13]>0:
                                print("We can initiate trade as 1 index cut")
                                print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                            else:
                                print("Addition in ITM and OTM on opposite side don't trade")       
                        else:
                            if (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j-1][13]-OI_Data_inner[j-1][1]) and (OI_Data[j][14] -OI_Data_inner[j][2])*0.10 >= (OI_Data[j][13]-OI_Data_inner[j][1]):
                                if (OI_Data[j][14]-OI_Data_inner[j][2])*0.20 >= ( OI_Data[j+1][13]-OI_Data_inner[j+1][1]):
                                    print("less than 20 %  addition in next SP - we can initiate Trade")
                                    print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                else:
                                    if (OI_Data[j+2][13] - OI_Data_inner[j+2][1] > OI_Data[j+1][13] - OI_Data_inner[j+1][1]):
                                        print("More addition at 100 SP away- we can initiate trade ")
                                        print("Sell " + str(trade_distance_pe) + " points away " + " i.e. " + str( OI_Data_inner[j][0] - trade_distance_pe ))
                                    else:
                                        print("Not all condition completed at this point")          
                            else:
                                print("Added on ITM Side in opposite - No Trade")
                    else:
                        print("No -ve tick in opposite side")
                else:
                    print("Wait")
                            

def momentum_for_trade(side):
    t1 = time.strftime("%H%M%S",time.localtime())
    current_time = datetime.now()
    new_time = current_time - timedelta(minutes=33)
    time_str = new_time.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str
    output_closing_time=output_date+" "+t1
    a=getting_ohlc(output_opening_time,output_closing_time)
    movement=0

    if index==3:
        movement=math.ceil(0.20*float(a[4])/100)
    elif index==0:
        movement=20
        movement= math.ceil(0.25*float(a[4])/100)
    elif index==2:
        movement=math.ceil(0.15*float(a[4])/100)
    elif index==4:
        movement=math.ceil(0.15*float(a[4])/100)
    elif index==1:
        movement=math.ceil(0.22*float(a[4])/100)       
    else:
        movement=50
                
    if float(a[2]) - float(a[3]) > movement :
        print("Movement required -" + str(movement))
        print("Movement of price - " +  str( float(a[2]) - float(a[3]) ) )
    else:
        print("Movement required -" + str(movement))
        print("No movement less movement in last 30 minutes"+ str( float(a[2]) - float(a[3]) ) )

    t1 = time.strftime("%H%M%S",time.localtime())    
    new_time_3min = current_time - timedelta(minutes=3)
    time_str_3min = new_time_3min.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str_3min
    output_closing_time=output_date+" "+t1
    a=getting_ohlc(output_opening_time,output_closing_time)
    last_min_high=float(a[2])
    last_min_low=float(a[3])
    
    new_time_33min = current_time - timedelta(minutes=33)
    time_str_33min = new_time_33min.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str_33min
    output_closing_time=output_date+" "+time_str_3min
    a=getting_ohlc(output_opening_time,output_closing_time)
    last_30min_high=float(a[2])
    last_30min_low=float(a[3])

    if side=='PE':
        if last_30min_high > last_min_high:
            print("-------------If not 1st Trade ---------  last 30 min high is not Crossed(Put) -------------------- ")
        else:
            print("------Last 30 min High Crossed(Put) ----------------------") 
    if side=='CE':        
        if last_30min_low < last_min_low:
            print("-------------If not 1st Trade ---------  last 30 min low is not Crossed(Call) -------------------- ")
        else:
            print("------Last 30 min Low Crossed(Call) ----------------------")     

    new_time_6min = current_time - timedelta(minutes=6)
    time_str_6min = new_time_6min.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str_6min    
    output_closing_time=output_date+" "+time_str_3min
    a=getting_ohlc(output_opening_time,output_closing_time)
    last_candle_high= float(a[2])
    last_candle_close=float(a[4])
    last_candle_low=float(a[3])


    new_time_9min = current_time - timedelta(minutes=9)
    time_str_9min = new_time_9min.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str_9min    
    output_closing_time=output_date+" "+time_str_6min
    a=getting_ohlc(output_opening_time,output_closing_time)
    last_2_candle_high= float(a[2])
    last_2_candle_close=float(a[4])
    last_2_candle_low=float(a[3])

    new_time_12min = current_time - timedelta(minutes=12)
    time_str_12min = new_time_12min.strftime("%H%M%S")
    output_opening_time=output_date+" "+time_str_12min    
    output_closing_time=output_date+" "+time_str_9min
    a=getting_ohlc(output_opening_time,output_closing_time)
    last_3_candle_high= float(a[2])
    last_3_candle_close=float(a[4])
    last_3_candle_low=float(a[3])

    if side=='PE':
        if last_3_candle_close>=last_2_candle_close:
            if last_candle_close>=last_3_candle_close:
                print("2nd Candle Close is Close from previous 2")
            else:
                print("----------2nd Candle Clsoe is not Clsoe from previous 2--------------")    
        else:
            if last_3_candle_close >= last_2_candle_close:
                print("2nd Candle Close is Close from previous 2")
            else:
                print("----------2nd Candle Close is not Close from previous 2--------------")

        if last_3_candle_high>=last_2_candle_high:
            if last_candle_high>=last_3_candle_high:
                print("2nd Candle High is High from previous 2")
            else:
                print("----------2nd Candle High is not High from previous 2--------------")    
        else:
            if last_candle_high >= last_2_candle_high:
                print("2nd Candle High is High from previous 2")
            else:
                print("----------2nd Candle High is not High from previous 2--------------")

    if side=='CE':
        if last_3_candle_close<=last_2_candle_close:
            if last_candle_close<=last_3_candle_close:
                print("2nd Candle Close is low from previous 2")
            else:
                print("----------2nd Candle Close is not low from previous 2--------------")    
        else:
            if last_3_candle_close <= last_2_candle_close:
                print("2nd Candle Close is low from previous 2")
            else:
                print("----------2nd Candle Close is not low from previous 2--------------")

        if last_3_candle_low<=last_2_candle_low:
            if last_candle_low<=last_3_candle_low:
                print("2nd Candle low is low from previous 2")
            else:
                print("----------2nd Candle low is not low from previous 2--------------")    
        else:
            if last_candle_low <= last_2_candle_low:
                print("2nd Candle low is low from previous 2")
            else:
                print("----------2nd Candle low is not low from previous 2--------------")                         
                       

def premium_discount(OI_Data,max_discount,min_discount):
    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time =output_date+ " 090000"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    delta=float(a1[4])
    sp=0
    if index==0:
        if float(a1[4])%25<15:
            sp=float(a1[4]) - float(a1[4])%25
            delta=delta-sp
        else:
            sp= float(a1[4]) + (25- float(a1[4])%25)
            delta=sp -delta
    elif index==1 or index==3:
        if float(a1[4])%50<30:
            sp=float(a1[4]) - float(a1[4])%50
            delta=delta-sp
        else:
            sp= float(a1[4]) + (50- float(a1[4])%50)
            delta=sp -delta
    elif index==2:
        if float(a1[4])%100<50:
            sp=float(a1[4]) - float(a1[4])%100
            delta=delta-sp
        else:
            sp= float(a1[4]) + (100- float(a1[4])%100)
            delta=sp -delta
    elif index==4:
        if float(a1[4])%100<50:
            sp=float(a1[4]) - float(a1[4])%100
            delta=delta-sp
        else:
            sp= float(a1[4]) + (100- float(a1[4])%100) 
            delta=sp -delta

    index_of_found_row=None
    for i, row in enumerate(OI_Data):
        if row[0] == sp:
            index_of_found_row = i
            break
    synthetic_price=sp

    if index!=4:
        response = xt.get_ohlc(
            exchangeSegment=xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=OI_Data[index_of_found_row][1],
            startTime=output_opening_time,
            endTime=output_closing_time,
            compressionValue=450000)
        a=response['result']['dataReponse'].split('|')
        if a==['']:
            print("No data")
            return max_discount,min_discount
        else:    
            synthetic_price=synthetic_price+float(a[4])
            delta=float(a[4])-delta
        
        response = xt.get_ohlc(
            exchangeSegment=xt.EXCHANGE_NSEFO,
            exchangeInstrumentID=OI_Data[index_of_found_row][3],
            startTime=output_opening_time,
            endTime=output_closing_time,
            compressionValue=450000)
        a=response['result']['dataReponse'].split('|')
    elif index==4:
        response = xt.get_ohlc(
            exchangeSegment=xt.EXCHANGE_BSEFO,
            exchangeInstrumentID=OI_Data[index_of_found_row][1],
            startTime=output_opening_time,
            endTime=output_closing_time,
            compressionValue=450000)
        a=response['result']['dataReponse'].split('|')
        if a==['']:
            print("No data")
            return max_discount,min_discount
        else:    
            synthetic_price=synthetic_price+float(a[4])
            delta=float(a[4])-delta

        response = xt.get_ohlc(
            exchangeSegment=xt.EXCHANGE_BSEFO,
            exchangeInstrumentID=OI_Data[index_of_found_row][3],
            startTime=output_opening_time,
            endTime=output_closing_time,
            compressionValue=450000)
        a=response['result']['dataReponse'].split('|')
 
    if a==['']:
        print("No Data")
    else:    
        synthetic_price=synthetic_price-float(a[4])
        delta=delta+float(a[4])
        print("Delta Value is - "+ str(delta))
        if synthetic_price > float(a1[4]):
            print("Premium  " + str(synthetic_price - float(a1[4])  ),end=" ")
        else:
            print("Discount "+ str(synthetic_price - float(a1[4])  ),end=" ")

        if max_discount < synthetic_price - float(a1[4]):
            max_discount= synthetic_price - float(a1[4])
            print("-----Max Discount : "+ str(max_discount), end="  ----- ")

        if min_discount > synthetic_price - float(a1[4]):
            min_discount = synthetic_price - float(a1[4])
            print("----- Min Discount : " + str(min_discount), end=" ----- ")

            
    return max_discount,min_discount    

def third_stop_loss(OI_Data,max_discount,min_discount):
    print("")
    max_discount1,min_discount1=premium_discount(OI_Data,max_discount,min_discount)
    if max_discount1 > max_discount*2 and max_discount1>0:
        if max_discount1>10:
            print("MAX Discount get doubled")
            
            t1 = time.strftime("%H%M%S",time.localtime())
            current_time = datetime.now()
            new_time = current_time - timedelta(minutes=30)
            time_str = new_time.strftime("%H%M%S")
            output_opening_time=output_date+" "+time_str
            output_closing_time=output_date+" "+t1
            a=getting_ohlc(output_opening_time,output_closing_time)
            if float(a[2]) - float(a[3]) > 30 :
                print("Movement of price - " +  str( float(a[2]) - float(a[3]) ) )
                if float(a[2])-20 <= float(a[4]) <= float(a[2])+20:
                    print("Price trading near 30 mins high")

    if min_discount1 < min_discount*2 and min_discount1<0:
        if min_discount1< -10:
            print("Min Discount get Doubled")
            t1 = time.strftime("%H%M%S",time.localtime())
            current_time = datetime.now()
            new_time = current_time - timedelta(minutes=30)
            time_str = new_time.strftime("%H%M%S")
            output_opening_time=output_date+" "+time_str
            output_closing_time=output_date+" "+t1
            a=getting_ohlc(output_opening_time,output_closing_time)
            if float(a[2]) - float(a[3]) > 30 :
                print("Movement of price - " +  str( float(a[2]) - float(a[3]) ))
                if float(a[3])-20 <= float(a[4]) <= float(a[3])+20:
                    print("Price trading near 30 mins low")


    if max_discount1>max_discount:
        max_discount=max_discount1

    if min_discount1<min_discount:
        min_discount=min_discount1

    return max_discount,min_discount                  


def instrument_for_ce_pe_table(Atp_ltp_table_ce,Atp_ltp_table_pe):
    i=0
    """Check before 9:15 and only once"""
    output_opening_time = output_date+ " 090000"
    output_closing_time = output_date+ " 091600"
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
            i=i+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)
            Nifty_Strike=Nifty_Strike+50

        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe    

    elif index==2:
        Nifty_Strike=Nifty_SP - 1400 - (Nifty_SP%100)
        while Nifty_SP+1400 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            i=i+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate=prefix[index][9:],
                optionType='PE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)

            Nifty_Strike=Nifty_Strike+100
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe     
    elif index==1:
        Nifty_Strike=Nifty_SP - 700 - (Nifty_SP%50)
        while Nifty_SP+700 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            i=i+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)
            
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='FINNIFTY',
                expiryDate=prefix[index][8:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)
            Nifty_Strike=Nifty_Strike+50
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 
    elif index==0:
        Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%25)
        while Nifty_SP+350 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            i=i+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='CE',
                strikePrice=Nifty_Strike)
    
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='MIDCPNIFTY',
                expiryDate=prefix[index][10:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp) 
            Nifty_Strike=Nifty_Strike+25
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 
    elif index==4:
        Nifty_Strike=Nifty_SP - 1400 - (Nifty_SP%100)
        
        while Nifty_SP+1400 >= Nifty_Strike:
            Atp_ltp_table_ce[i][0]=Nifty_Strike
            Atp_ltp_table_pe[i][0]=Nifty_Strike
            i=i+1
            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            
            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_ce.append(temp)

            response = xt.get_option_symbol(
                exchangeSegment=12,
                series='IO',
                symbol='BSX',
                expiryDate=prefix[index][6:],
                optionType='PE',
                strikePrice=Nifty_Strike)

            temp = {'exchangeSegment':12,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instrument_for_pe.append(temp)
            Nifty_Strike=Nifty_Strike+100 
        return instrument_for_ce,instrument_for_pe,Atp_ltp_table_ce,Atp_ltp_table_pe 

def atp_ltp_table_form(instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe):
    Atp_ltp_table_ce=soc.on_message1501_json_partial('AverageTradedPrice','LastTradedPrice',instrument_setup_ce,Atp_ltp_table_ce)
    Atp_ltp_table_pe=soc.on_message1501_json_partial('AverageTradedPrice','LastTradedPrice',instrument_setup_pe,Atp_ltp_table_pe)
    return Atp_ltp_table_ce,Atp_ltp_table_pe

                          
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
OI_Data = [[0] * 15 for _ in range(16)]
previous_day_OI_set_Instrument_set(output_date) 
print(OI_Data)

"""ATP/LTP Table to check the prior nature of market"""
# Atp_ltp_table_ce = [[0] * 3 for _ in range(20)]
# Atp_ltp_table_pe = [[0] * 3 for _ in range(20)]

# instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe =  instrument_for_ce_pe_table(Atp_ltp_table_ce,Atp_ltp_table_pe) 

"""Wait till 10:00 for stability of market"""
Specify_the_Open_TIME_HHMM = '0951'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
    curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
    # Atp_ltp_table_ce,Atp_ltp_table_pe =  atp_ltp_table_form(instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe)
    # for row in Atp_ltp_table_ce:
    #     print(row)
    # print("---------------------------------------------------")    
    # for row in Atp_ltp_table_pe:
    #     print(row)    
    # print("---------------------------------------------------")  
        
OI_Data = update_OI_Data(OI_Data,instruments_OI)

Specify_the_Open_TIME_HHMM = '1530'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
flag_side_ce=''
flag_side_pe=''
flag_time_ce=''
flag_time_pe=''
trade_side=''
first_ce=False
first_pe=False

Specify_record_tick_time='1000'
set_current_oi1=curr_dt+Specify_record_tick_time
Specify_record_tick_time='1530' 
set_current_oi2=curr_dt+Specify_record_tick_time

flag_at_10=True
ce_cumulative_best=0
ce_change_best=0
pe_cumulative_best=0
pe_chnage_best=0

ce_trade_itm_rank=0
pe_trade_itm_rank=0

tezi=0
mandi=0
max_discount=-500
min_discount=+500
greed_fear_check=True
"""both/ CE /PE """
open_trade_for_side="Both"

trending_side_ce=None
trending_side_pe=None

trade_distance_ce=0
trade_distance_pe=0
if index==0:
    trade_distance_ce=75
    trade_distance_pe=75
elif index==1 or index==3:
    trade_distance_ce=150
    trade_distance_pe=150
elif index==2:
    trade_distance_ce=400
    trade_distance_pe=400
elif index==4:
    trade_distance_ce=500
    trade_distance_pe=500    

while(curr_tm_chk <= set_current_oi ):

    update_data_flag = to_check_data_update(OI_Data,instruments_OI)
    curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
    if update_data_flag:   
        OI_Data = update_OI_Data(OI_Data,instruments_OI)
        print(curr_tm_chk)

        if (curr_tm_chk >= set_current_oi1):

            if greed_fear_check:
                output_opening_time=output_date+" 091500"
                output_closing_time=output_date+" 100000"
                a=getting_ohlc(output_opening_time,output_closing_time)
                if index==1 or index==3:
                    movement=90
                elif index==0:
                    movement=45
                elif index==2:
                    movement=200
                elif index==4:
                    movement=300    
                else:
                    movement=75

                if float(a[2]) - float(a[3]) > movement :
                    print("Greed as per Point Movement - " +  str( float(a[2]) - float(a[3]) ) )
                else:
                    print("No Greed as per Point Movement"+ str( float(a[2]) - float(a[3]) ) )

                greed_fear_check=False        


            max_index=0
            max_oi=-100000000000000
            max_oi_chng=-1000000000000
            max_index_chng=0

            max_index1=0
            max_oi1=-100000000000000 
            max_oi_chng1=-1000000000000
            max_index_chng1=0 
            i=0
            for row in OI_Data:
                if max_oi < row[13]:
                    max_oi=row[13]
                    max_index=i

                if max_oi_chng< row[5]:
                    max_oi_chng=row[5]
                    max_index_chng=i 


                if max_oi_chng1< row[6]:
                    max_oi_chng1=row[6]
                    max_index_chng1=i   

                if max_oi1<row[14]:
                    max_oi1=row[14]
                    max_index1=i
                i=i+1
            if flag_at_10:
                ce_cumulative_best=max_index
                pe_cumulative_best=max_index1
                ce_change_best=max_index_chng
                pe_chnage_best=max_index_chng1
                flag_at_10=False
                
            
            if flag_side_ce=='':
                flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7],OI_Data[max_index1][6], OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8])
                if flag:
                    print(" Subtracted more than 5 lakh in 1 OI Tick of PE")
                    flag_side_ce='CE'
                    flag_time_ce=datetime.now() + timedelta(minutes=15)
                    first_ce=True
                
                flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9],OI_Data[max_index1][6], OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10])
                if flag:
                    print("Subtracted more than 5 lakh in 2 OI Tick of PE") 
                    flag_side_ce='CE'
                    flag_time_ce=datetime.now() + timedelta(minutes=15)
                    first_ce=True

                flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11],OI_Data[max_index1][6], OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12])
                if flag:
                    print("Subtracted more than 5 lakh in 3 OI Tick of PE")
                    flag_side_ce='CE'
                    flag_time_ce=datetime.now() + timedelta(minutes=15)
                    first_ce=True

            if flag_side_pe=='':
                flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8],OI_Data[max_index][5], OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7])
                if flag:
                    print("Subtracted more than 5 lakh in 1 OI Tick of CE")
                    flag_side_pe='PE'
                    flag_time_pe=datetime.now() + timedelta(minutes=15)
                    first_pe=True

                flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10],OI_Data[max_index][5], OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9])
                if flag :
                    print("Subtracted more than 5 lakh in 2 OI Tick of CE")
                    flag_side_pe='PE'
                    flag_time_pe=datetime.now() + timedelta(minutes=15)
                    first_pe=True

                flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12],OI_Data[max_index][5], OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11])
                if flag :
                    print("Subtracted more than 5 lakh in 3 OI Tick of CE")
                    flag_side_pe='PE'
                    flag_time_pe=datetime.now() + timedelta(minutes=15)
                    first_pe=True    

            if flag_side_ce!='' and (curr_tm_chk <= set_current_oi2):
                if first_ce:
                    OI_Data_inner_ce = [[0] * 3 for _ in range(16)]       
                    # new_array = setting_data_for_Change_info(OI_Data,output_date)
                    OI_Data_inner_ce = setting_inner_OI_Data(OI_Data_inner_ce,OI_Data)
                    first_ce=False 

                momentum_for_trade('CE')    
                check_for_trade_points(OI_Data_inner_ce,OI_Data,'PE',trade_distance_ce,trade_distance_pe)  
            
            if flag_side_ce!='' and (flag_time_ce < datetime.now()):
                flag_side_ce=''

            if flag_side_pe!='' and (curr_tm_chk <= set_current_oi2):
                if first_pe:
                    OI_Data_inner_pe = [[0] * 3 for _ in range(16)]       
                    # new_array = setting_data_for_Change_info(OI_Data,output_date)
                    OI_Data_inner_pe = setting_inner_OI_Data(OI_Data_inner_pe,OI_Data)
                    first_pe=False

                momentum_for_trade('PE')     
                check_for_trade_points(OI_Data_inner_pe,OI_Data,'CE',trade_distance_ce,trade_distance_pe)


             
            if flag_side_pe!='' and (flag_time_pe < datetime.now()):
                flag_side_pe=''    

            if pe_cumulative_best==max_index1:
                print("Cumulative best of PE is not Changed - " + str(OI_Data[max_index1][0]))
            else:
                if pe_cumulative_best < max_index1:
                    if OI_Data[max_index1][14] > OI_Data[pe_cumulative_best][14]*1.1:
                        print("Cumulative move forward indicating tezi"+ str(OI_Data[max_index1][0]) )
                        pe_cumulative_best=max_index1
                else:
                    if OI_Data[max_index1][14] > OI_Data[pe_cumulative_best][14]*1.1:
                        print("Cumulative move backward indicating mandi"+ str(OI_Data[max_index1][0]) )
                        pe_cumulative_best=max_index1

            if pe_chnage_best == max_index_chng1:
                print("Change best of PE is not Changed - " + str(OI_Data[max_index_chng1][0]))
            else:
                if pe_chnage_best < max_index_chng1:
                    if OI_Data[max_index_chng1][6] > OI_Data[pe_chnage_best][6]*1.1:
                        print("Change move forward indicating tezi "+ str(OI_Data[max_index_chng1][0]) )
                        pe_chnage_best=max_index_chng1
                else:
                    if OI_Data[max_index_chng1][6] > OI_Data[pe_chnage_best][6]*1.1:
                        print("Change move backward indicating mandi"+ str(OI_Data[max_index_chng1][0]) )
                        pe_chnage_best=max_index_chng1

            if ce_cumulative_best==max_index:
                print("Cumulative best of CE is not Changed - " + str(OI_Data[max_index][0]))
            else:
                if ce_cumulative_best < max_index:
                    if OI_Data[max_index][13] > OI_Data[ce_cumulative_best][13]*1.1:
                        print("Cumulative move forward  indicating tezi"+ str(OI_Data[max_index][0]) )
                        ce_cumulative_best=max_index
                else:
                    if OI_Data[max_index][13] > OI_Data[ce_cumulative_best][13]*1.1:
                        print("Cumulative move backward indicating mandi"+ str(OI_Data[max_index][0]) )
                        ce_cumulative_best=max_index

            if ce_change_best == max_index_chng:
                print("Change best of CE is not Changed - " + str(OI_Data[max_index_chng][0]))
            else:
                if ce_change_best < max_index_chng:
                    if OI_Data[max_index_chng][5] > OI_Data[ce_change_best][5]*1.1:
                        print("Change move forward indicating tezi"+ str(OI_Data[max_index_chng][0]) )
                        ce_change_best=max_index_chng
                else:
                    if OI_Data[max_index_chng][5] > OI_Data[ce_change_best][5]*1.1:
                        print("Change move backward indicating mandi "+ str(OI_Data[max_index_chng][0]) )
                        ce_change_best=max_index_chng 

    max_discount,min_discount = premium_discount(OI_Data,max_discount,min_discount)
    max_discount,min_discount = third_stop_loss(OI_Data,max_discount,min_discount)
    time.sleep(10)            
    # Atp_ltp_table_ce,Atp_ltp_table_pe =  atp_ltp_table_form(instrument_setup_ce,instrument_setup_pe,Atp_ltp_table_ce,Atp_ltp_table_pe)
    # print("---------------------------------------------------") 
    # for row in Atp_ltp_table_ce:
    #     print(row)
    # print("---------------------------------------------------")    
    # for row in Atp_ltp_table_pe:
    #     print(row)    
    # print("---------------------------------------------------")


"""Stop loss check 
2 Opposite side best 
Cut ke aage jaa rhaa 2 baje ke baad if 2 trade
2 sp duur after 2 if volatile or premium.discount basis
Best chnage se aage nhi jaana hai"""


    


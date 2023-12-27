from Connect import XTSConnect
import json
import time
import math
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
clientID = "D0253276"
#userID = "D0253276"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()
day=''
"""---- 0 For Mid cap Nifty , 1 For Finninfty , 2 for Bank Nifty , 3 For Nifty ---"""
index=1

prefix=["MIDCPNIFTY25Sep2023","FINNIFTY03Oct2023","BANKNIFTY20Sep2023","NIFTY21Sep2023"]
exchangeInstrumentID_Number=[26121,26034,26001,26000]

m=1

def change_date_format(date):
	original_format = '%Y%m%d'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)  

def getting_ohlc(opening_time,closing_time):
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID= exchangeInstrumentID_Number[index],
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=450000)
	# print(response)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
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
    output_closing_time = output_date + " 091600"
    a1=getting_ohlc(output_opening_time,output_closing_time)
    if a1==['']:
        print("Something in data is wrong - Can't be Ignore")

    Nifty_SP=float(a1[4])
    """range to be -350 to +350"""
    if index==3:
        Nifty_Strike=Nifty_SP - 200 - (Nifty_SP%50)
        while Nifty_SP+250 >= Nifty_Strike:
            OI_Data[i][j]=Nifty_Strike
            j=j+1
            response = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='NIFTY',
                expiryDate=prefix[index][5:],
                optionType='CE',
                strikePrice=Nifty_Strike)
            # print(response)
            #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
            OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
            j=j+1

            instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
            temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
            instruments_OI.append(temp)
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            # print(response)
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest          
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+50


    elif index==2:
        Nifty_Strike=Nifty_SP - 400 - (Nifty_SP%100)
        while Nifty_SP+500 >= Nifty_Strike:
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            # print(response)
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest          
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+100
    elif index==1:
        Nifty_Strike=Nifty_SP - 200 - (Nifty_SP%50)
        while Nifty_SP+250 >= Nifty_Strike:
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            # print(response)
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest          
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+50
    elif index==0:
        Nifty_Strike=Nifty_SP - 100 - (Nifty_SP%25)
        while Nifty_SP+125 >= Nifty_Strike:
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            # print(response)
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest
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
            response = xt.get_quote(
                Instruments=instrument,
                xtsMessageCode=1510,
                publishFormat='JSON')
            json_string = response['result']['listQuotes'][0]
            data=json.loads(json_string)
            OpenInterest=data["OpenInterest"]
            #print(OpenInterest,end="  ")
            OI_Data[i][j]=OpenInterest          
            j=0
            i=i+1  
            #print()
            Nifty_Strike=Nifty_Strike+25

	        

def update_OI_Data(OI,instruments_OI):
	count=10
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
	else:
		return False

def Select_Inner_Sp_And_Set_To_Zero(output_date,OI_Data_inner):
	current_time = datetime.now()
	time_str2= current_time.strftime("%H%M%S")
	open_time= current_time - timedelta(minutes=5)
	time_str3= open_time.strftime("%H%M%S")
	output_opening_time = output_date +" "+time_str3 
	output_closing_time=output_date+" "+time_str2
	a= getting_ohlc(output_opening_time,output_closing_time)
	if index==1 or index==3:
		if float(a[4])%50<=25:
			x=float(a[4]) - float(a[4])%50 -100
			for i in range(5):
				OI_Data_inner[i][0]=x
				x=x+50
		elif float(a[4])%50>25:
			x= float(a[4]) + (50 - float(a[4])%50) - 100
			for i in range(5):
					OI_Data_inner[i][0]=x
					x=x+50
	elif index==0:
		if float(a[4])%25<15:
			x=float(a[4]) - float(a[4])%25 - 50
			for i in range(5):
				OI_Data_inner[i][0]=x
				x=x+25
		elif float(a[4])%25>=15:
			x= float(a[4]) - (25-float(a[4])%25) - 50
			for i in range(5):
				OI_Data_inner[i][0]=x
				x=x+25
	elif index==2:
		if float(a[4])%100<=50:
			x= float(a[4])- float(a[4])%100-200
			for i in range(5):
				OI_Data_inner[i][0]=x
				x=x+100
		elif float(a[4])%100>50:
			x= float(a[4]) - (100- float(a[4])%100) - 200
			for i in range(5):
				OI_Data_inner[i][0]=x
				x=x+100
	return OI_Data_inner			

def update_OI_Data_inner(OI_Data_inner,OI_Data):

	

	return OI_Data_inner


"""wait till 9:15 till market open"""
Specify_the_Market_Open_TIME_HHMM = '0900' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = '0915'  #First 45 Min to get the Max OI Change
curr_dt = time.strftime("%Y%m%d", time.localtime())
set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

"""Setting OI Data till 9:15 , Strike Price , Previous day OI IN Call and Put , 9:15 Clock OI of Call and Put"""
instruments_OI = []
output_date=change_date_format(curr_dt)
OI_Data = [[0] * 15 for _ in range(10)]
OI_Data_inner = [[0] * 9 for _ in range(5)]
previous_day_OI_set_Instrument_set(output_date)	

"""Wait till 10:00 for stablity of market"""
Specify_the_Open_TIME_HHMM = '1000'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

OI_Data = update_OI_Data(OI_Data,instruments_OI)


Specify_the_Open_TIME_HHMM = '1500'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
flag_side=''
flag_time=''
trade_side=''
first=False

Specify_record_tick_time='1009'
set_current_oi1=curr_dt+Specify_record_tick_time
Specify_record_tick_time='1400'	
set_current_oi2=curr_dt+Specify_record_tick_time

""" ----------Table info ----------------
Strike Price 	Instrumnet Call	 OI_CALL_at_9:15  Instrument_Put  OI_Put_9:15  Change_call_morn change_put_morn  7_last 8_last 9_last2 10_last2 11_last3 12_last3 Total_call Total_Put"""

while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
	OI_Data = update_OI_Data(OI_Data,instruments_OI)
	
	if (curr_tm_chk >= set_current_oi1):
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
		if flag_side=='' and (curr_tm_chk <= set_current_oi2):	
			flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7],OI_Data[max_index1][6], OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8])
			if flag:
				print(" Subtracted more than 5 lakh in 1 OI Tick of PE")
				flag_side='CE'
				flag_time=curr_tm_chk
				first=True

			flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8],OI_Data[max_index][5], OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7])
			if flag:
				print("Subtracted more than 5 lakh in 1 OI Tick of CE")
				flag_side='PE'
				flag_time=curr_tm_chk
				first=True

			flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9],OI_Data[max_index1][6], OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10])
			if flag:
				print("Subtracted more than 5 lakh in 2 OI Tick of PE") 
				flag_side='CE'
				flag_time=curr_tm_chk
				first=True

			flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10],OI_Data[max_index][5], OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9])
			if flag:
				print("Subtracted more than 5 lakh in 2 OI Tick of CE")
				flag_side='PE'
				flag_time=curr_tm_chk
				first=True

			flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11],OI_Data[max_index1][6], OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12])
			if flag:
				print("Subtracted more than 5 lakh in 3 OI Tick of PE ")
				flag_side='CE'
				flag_time=curr_tm_chk
				first=True

			flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12],OI_Data[max_index][5], OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11])
			if flag:
				print("Subtracted more than 5 lakh in 3 OI Tick of CE")
				flag_side='PE'
				flag_time=curr_tm_chk
				first=True

		if flag_side!='' and (curr_tm_chk <= set_current_oi2):
			if first:
				OI_Data_inner = [[0] * 9 for _ in range(5)]
				OI_Data_inner=Select_Inner_Sp_And_Set_To_Zero(output_date,OI_Data_inner)
				OI_Data_inner = update_OI_Data_inner(OI_Data_inner,OI_Data)
				first=False	

	time.sleep(180)			

	


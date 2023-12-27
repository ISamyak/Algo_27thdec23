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
clientID = "D0253246"
#userID = "D0253276"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()
day=''
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
prefix="NIFTY20Jul2023"
m=1
#26034 - Fin Nifty
def change_date_format(date):
	original_format = '%Y%m%d'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[3])) - (int(float(a[3])%100)) - 250
	while int(float(a[2]))+250 >= SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+50
	return sp

def getting_ohlc_nifty(opening_time,closing_time):
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=450000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
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

def getting_ohlc_nifty_using_compression(opening_time,closing_time,compress_Value):
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=compress_Value)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		return a
	else:
		return a		

def update_atp_ltp(output_date,Strike_Price_Set,output_opening_time,output_closing_time,Table,first):
	
	i=0
	for Nifty_Strike in Strike_Price_Set:
		response = xt.get_option_symbol(
			exchangeSegment=2,
            series='OPTIDX',
            symbol='NIFTY',
            expiryDate=prefix[5:],
            optionType='CE',
            strikePrice=Nifty_Strike)
		Table[i][0]=str(Nifty_Strike)+'CE'
		instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
		temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
		instruments_OI.append(temp)
		response1 = xt.get_ohlc(
        	exchangeSegment="NSEFO",
	    	exchangeInstrumentID=response['result'][0]['ExchangeInstrumentID'],
	    	startTime=output_opening_time,
	    	endTime=output_closing_time,
	    	compressionValue=450000)
		a=response1['result']['dataReponse'].split('|')
		if a==['']:
			print("Ignore")
		else:
			Table[i][6]=Table[i][6]+float(a[5])
			Table[i][7]=float(a[4])
			Table[i][8]=Table[i][8]+float(a[5])*float(a[4])
			b=Table[i][8]/Table[i][6]
			d=(float(a[4])/b-1)*100
			Table[i][1]=d
			if first:
				Table[i][2]=d
				Table[i][3]=output_closing_time
			else:
				if Table[i][2] > d:
					Table[i][2]=d
					Table[i][3]=output_closing_time

			Table[i][4]=Table[i][2]-10
		i=i+1
		response = xt.get_option_symbol(
			exchangeSegment=2,
            series='OPTIDX',
            symbol='NIFTY',
            expiryDate=prefix[5:],
            optionType='PE',
            strikePrice=Nifty_Strike)
		Table[i][0]=str(Nifty_Strike)+'PE'
		instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
		temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
		instruments_OI.append(temp)
		response1 = xt.get_ohlc(
			exchangeSegment="NSEFO",
	    	exchangeInstrumentID=response['result'][0]['ExchangeInstrumentID'],
	    	startTime=output_opening_time,
	    	endTime=output_closing_time,
	    	compressionValue=450000)
		a=response1['result']['dataReponse'].split('|')
		if a==['']:
			print("Ignore")
		else:	
			Table[i][6]=Table[i][6]+float(a[5])
			Table[i][7]=float(a[4])
			Table[i][8]=Table[i][8]+float(a[5])*float(a[4])
			b=Table[i][8]/Table[i][6]
			d=(float(a[4])/b-1)*100
			Table[i][1]=d
			if first:
				Table[i][2]=d
				Table[i][3]=output_closing_time
			else:
				if Table[i][2] > d:
					Table[i][2]=d
					Table[i][3]=output_closing_time
			Table[i][4]=Table[i][2]-10
			Table[i][5]=Table[i-1][1]+Table[i][1]
			Table[i-1][5]=Table[i-1][1]+Table[i][1]
		i=i+1

	return Table    

# def update_atp_ltp(output_date, Strike_Price_Set, output_opening_time, output_closing_time, Table, first):
#     # Create a list of instruments for call and put options
#     instruments = [xt.get_option_symbol(exchangeSegment=2, series='OPTIDX', symbol='NIFTY', expiryDate=prefix[5:], optionType=ot, strikePrice=sp) for sp in Strike_Price_Set for ot in ['CE', 'PE']]
#     # Create a list of factors for calculating the percentage change
#     factors = [1, -1] * len(Strike_Price_Set)
#     i = 0
#     for instrument, factor in zip(instruments, factors):
#         # Get the exchange instrument ID
#         eid = instrument['result'][0]['ExchangeInstrumentID']
#         # Get the ohlc data
#         ohlc = xt.get_ohlc(exchangeSegment="NSEFO", exchangeInstrumentID=eid, startTime=output_opening_time, endTime=output_closing_time, compressionValue=450000)
#         data = ohlc['result']['dataReponse'].split('|')
#         if data == ['']:
#             print("Ignore")
#         else:
#             # Update the table values
#             Table[i][0] = str(Strike_Price_Set[i // 2]) + ('CE' if i % 2 == 0 else 'PE')
#             Table[i][6] += float(data[5])
#             Table[i][7] = float(data[4])
#             Table[i][8] += float(data[5]) * float(data[4])
#             b = Table[i][8] / Table[i][6]
#             d = (float(data[4]) / b - 1) * 100
#             Table[i][1] = d
#             if first:
#                 Table[i][2] = d
#                 Table[i][3] = output_closing_time
#             else:
#                 if Table[i][2] > d:
#                     Table[i][2] = d
#                     Table[i][3] = output_closing_time
#             Table[i][4] = Table[i][2] - 10
#             if i % 2 == 1:
#                 # Calculate the sum of percentage changes for call and put options
#                 Table[i][5] = Table[i - 1][1] + Table[i][1]
#                 Table[i - 1][5] = Table[i - 1][1] + Table[i][1]
#         i += 1

#     return Table



instruments_OI = []
"""wait till 9:15 till market open"""
Specify_the_Market_Open_TIME_HHMM = '0900' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = '0915'  #First 45 Min to get the Max OI Change
curr_dt = time.strftime("%Y%m%d", time.localtime())

set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM #date maually
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())		

output_date=change_date_format(curr_dt)	
print(output_date)
Specify_the_Open_TIME_HHMM = '1458'#time change
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM

output_opening_time = output_date+ " 090000"
output_closing_time = output_date + " 100000"
a=getting_ohlc_nifty(output_opening_time,output_closing_time)
Strike_Price_Set=strike_price_for_data(a)
print(Strike_Price_Set)

time_str = '09:15:00'
time_obj = datetime.strptime(time_str, '%H:%M:%S')

Table = [[0] * 9 for _ in range(len(Strike_Price_Set)*2)]
first=True


while(curr_tm_chk <= set_current_oi ): #arrow time
	a=time_obj.strftime('%H%M%S')
	output_opening_time=output_date+" "+a
	time_obj += timedelta(minutes=15)
	a=time_obj.strftime('%H%M%S')
	output_closing_time=output_date+" "+a
	print(output_opening_time)
	Table=update_atp_ltp(output_date,Strike_Price_Set,output_opening_time,output_closing_time,Table,first)
	first=False
	print(" Ticker			LTP/ATP@time				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE		LTQ			LTP			LTS  ")	
	for rows in Table:
		print(rows)
	print("-------------------------------------------------------------------------------")	





	
	




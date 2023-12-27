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


def getting_ohlc(opening_time,closing_time):
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



"""wait till 9:15 till market open"""
last_day='Dec 22 2023'
Specify_the_Market_Open_TIME_HHMM = ' 091500' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = ' 153000'  #First 45 Min to get the Max OI Change
output_opening_time = last_day + Specify_the_Market_Open_TIME_HHMM
output_closing_time = last_day + Specify_the_Open_TIME_HHMM
# n=3


opening_time = datetime.strptime(output_opening_time, '%b %d %Y %H%M%S')
closing_time = datetime.strptime(output_closing_time, '%b %d %Y %H%M%S')


# for Lower low lower High
# Open at top close at bottom 
lower_low=[915]
lower_low_value=[]
higher_high=[915]
higher_high_value=[]

interval = timedelta(minutes=3)
n=918
while opening_time < closing_time:

    output_opening_time=opening_time.strftime('%b %d %Y %H%M%S')
    output_closing_time=(opening_time + interval).strftime('%b %d %Y %H%M%S')
    a1=getting_ohlc(output_opening_time,output_closing_time)
    print(a1)

    if float(a1[4])<float(a1[1]):
    	if  lower_low[-1]==915:
    		lower_low[-1]=(n)
    		lower_low_value.append(float(a1[1]))
    		lower_low_value.append(float(a1[4]))
    		print("-------------------lower low ----------------------")
    		print(lower_low)
    		print(lower_low_value)
    	if lower_low[-1]==n-3 and len(lower_low)%2==1:
    		lower_low[-1]=n
    		lower_low_value[-1]=float(a1[4])
    		print("-------------------lower low ----------------------")
    		print(lower_low) 
    		print(lower_low_value)

    				

    	if len(lower_low)%2==0:
    		if lower_low_value[1]>float(a1[4]):
	    		lower_low.append(n)
	    		lower_low_value.append(a1[4])
	    		print("-------------------lower low ----------------------")
	    		print(lower_low)
	    		print(lower_low_value)


    	if higher_high[-1]!=915 and len(lower_low)%2==0 :
    		if higher_high_value[0]<float(a1[4]):
	    		higher_high.append(n)
	    		higher_high_value.append(float(a1[4]))
	    		print("-------------------Higher High ----------------------")
	    		print(higher_high)
    			print(higher_high_value)
    			continue
	    	else:
	    		higher_high=[915]
	    		higher_high_value=[]
	    		print("-------------------Higher High ----------------------")
	    		print(higher_high)
    			print(higher_high_value)
    			continue

    	if higher_high[-1]!=915 and len(higher_high)%2==1:
	    	if higher_high_value[len(higher_high_value)-2]<float(a1[4]):
	    		higher_high[-1]=n
	    		higher_high_value[-1]=float(a1[4])
	    		print("-------------------Higher High ----------------------")
	    		print(higher_high)
    			print(higher_high_value)
    			continue
	    	else:
	    		higher_high=[915]
	    		higher_high_value=[]
	    		print("-------------------Higher High ----------------------")
	    		print(higher_high)
    			print(higher_high_value)
    			continue				

    			
    if float(a1[4])>float(a1[1]):
    	if  higher_high[-1]==915:
    		higher_high[-1]=(n)
    		higher_high_value.append(float(a1[1]))
    		higher_high_value.append(float(a1[4]))
    		print("-------------------Higher High ----------------------")
    		print(higher_high)
    		print(higher_high_value)

    	if higher_high[-1]==n-3  and len(higher_high)%2==1:
    		higher_high[-1]=n
    		higher_high_value[-1]=float(a1[4])
    		print("-------------------Higher High ----------------------")
    		print(higher_high) 
    		print(higher_high_value)
		

    	if len(higher_high)%2==0:
    		if higher_high_value[1]<float(a1[4]):
	    		higher_high.append(n)
	    		higher_high_value.append(float(a1[4]))
	    		print("-------------------Higher High ----------------------")
	    		print(higher_high)
	    		print(higher_high_value)

    	if lower_low[-1]!=915 and len(lower_low)%2==1:
    		if lower_low_value[len(lower_low_value)-2]>float(a1[4]):
	    		lower_low.append(n)
	    		lower_low_value.append(float(a1[4]))
	    		print("-------------------lower low ----------------------")
	    		print(lower_low)
    			print(lower_low_value)
    			continue
	    	else:
	    		lower_low=[915]
	    		lower_low_value=[]
	    		print("-------------------lower low ----------------------")
	    		print(lower_low)
    			print(lower_low_value)
    			continue

    	if lower_low[-1]!=915 and len(lower_low)%2==0:
    		if lower_low_value[len(lower_low_value)-2]>float(a1[4]):
    			lower_low[-1]=n
	    		lower_low_value[-1]=float(a1[4])
	    		print("-------------------lower low ----------------------")
	    		print(lower_low)
    			print(lower_low_value)
    			continue
	    	else:
	    		lower_low=[915]
	    		lower_low_value=[]
	    		print("-------------------lower low ----------------------")
	    		print(lower_low)
    			print(lower_low_value)			
    			continue

    opening_time += interval
    n=n+3

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
"""---- 0 For Midcp Nifty , 1 For Fin ninfty , 2 for Bank Nifty , 3 For Nifty ---"""
index=0

prefix=["MIDCPNIFTY16Oct2023","FINNIFTY17Oct2023","BANKNIFTY11Oct2023","NIFTY12Oct2023"]
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
    	exchangeInstrumentID=exchangeInstrumentID_Number[index],
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=450000)
	print(response)
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
    output_closing_time = output_date + " 091530"
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
						
def setting_data_for_Change_info(OI_Data,output_date):
    current_time = datetime.now()
    time_str2= current_time.strftime("%H%M%S")
    output_closing_time=output_date+" " +time_str2
    output_opening_time = output_date+ " 090000"
    a1=getting_ohlc(opening_time2,output_closing_time)
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

def setting_inner_OI_Data(OI_Data_inner,new_array):
    i=0
    for row in new_array:
        OI_Data_inner[i][0]=row[0]
        OI_Data_inner[i][1]=row[7]
        OI_Data_inner[i][2]=row[8]
        OI_Data_inner[i][3]=row[7]
        OI_Data_inner[i][4]=row[8]
        i=i+1
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
previous_day_OI_set_Instrument_set(output_date)	

"""Wait till 10:00 for stablity of market"""
Specify_the_Open_TIME_HHMM = '1000'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

OI_Data = update_OI_Data(OI_Data,instruments_OI)


Specify_the_Open_TIME_HHMM = '1500'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
flag_side_ce=''
flag_side_pe=''
flag_time=''
trade_side=''
first_ce=False
first_pe=False

Specify_record_tick_time='1009'
set_current_oi1=curr_dt+Specify_record_tick_time
Specify_record_tick_time='1400'	
set_current_oi2=curr_dt+Specify_record_tick_time

while(curr_tm_chk <= set_current_oi ):

	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
	OI_Data = update_OI_Data(OI_Data,instruments_OI)
	print(curr_tm_chk)

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

        if flag_side_ce=='':
            flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7],OI_Data[max_index1][6], OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8])
    	    if flag:
    			print(" Subtracted more than 5 lakh in 1 OI Tick of PE")
    			flag_side_ce='CE'
    			flag_time=curr_tm_chk
    			first_ce=True
            
            flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9],OI_Data[max_index1][6], OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10])
            if flag:
                print("Subtracted more than 5 lakh in 2 OI Tick of PE") 
                flag_side_ce='CE'
                flag_time=curr_tm_chk
                first_ce=True

            flag=big_subtraction_tick(OI_Data[max_index][5],OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11],OI_Data[max_index1][6], OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12])
            if flag:
                print("Subtracted more than 5 lakh in 3 OI Tick of PE")
                flag_side_ce='CE'
                flag_time=curr_tm_chk
                first_ce=True
        
        if flag_side_pe=='':
            flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][8],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][8],OI_Data[max_index][5], OI_Data[max_index][7],OI_Data[max_index_chng][5],OI_Data[max_index_chng][7])
            if flag:
                print("Subtracted more than 5 lakh in 1 OI Tick of CE")
                flag_side_pe='PE'
                flag_time=curr_tm_chk
                first_pe=True

            flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][10],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][10],OI_Data[max_index][5], OI_Data[max_index][9],OI_Data[max_index_chng][5],OI_Data[max_index_chng][9])
            if flag :
                print("Subtracted more than 5 lakh in 2 OI Tick of CE")
                flag_side_pe='PE'
                flag_time=curr_tm_chk
                first_pe=True

            flag=big_subtraction_tick(OI_Data[max_index1][6],OI_Data[max_index1][12],OI_Data[max_index_chng1][6],OI_Data[max_index_chng1][12],OI_Data[max_index][5], OI_Data[max_index][11],OI_Data[max_index_chng][5],OI_Data[max_index_chng][11])
            if flag :
                print("Subtracted more than 5 lakh in 3 OI Tick of CE")
                flag_side_pe='PE'
                flag_time=curr_tm_chk
                first_pe=True    


		if flag_side_ce!='' and (curr_tm_chk <= set_current_oi2):
			if first_ce:
                OI_Data_inner_ce = [[0] * 9 for _ in range(5)]       
                new_array = setting_data_for_Change_info(OI_Data,output_date)
                OI_Data_inner_ce = setting_inner_OI_Data(OI_Data_inner_ce,new_array)
                first_ce=False 

            OI_Data_inner_ce = update_inner_OI_Data(OI_Data,OI_Data_inner_ce)    


			for rows in OI_Data_inner_ce:
				print(rows)
					

        if flag_side_pe!='' and (curr_tm_chk <= set_current_oi2):
            if first_pe:
                OI_Data_inner_pe = [[0] * 9 for _ in range(5)]       
                new_array = setting_data_for_Change_info(OI_Data,output_date)
                OI_Data_inner_pe = setting_inner_OI_Data(OI_Data_inner_pe,new_array)
                first_pe=False 
            
            for rows in OI_Data_inner_pe:
                print(rows)
                        

	time.sleep(180)			

	


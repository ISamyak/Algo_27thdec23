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
prefix="NIFTY18May2023"
m=1

def change_date_format(date):
	original_format = '%Y%m%d'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

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
		return a
	else:
		return a

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[3])) - (int(float(a[3])%100)) - 500
	while int(float(a[2]))+500 > SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+100
	return sp

def getting_ohlc_strike(instrument_id,opening_time,closing_time):
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSEFO,
    	exchangeInstrumentID=instrument_id,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=450000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("2nd Wrong data")
		return a
	else:
		return a

def ratio_125_check(r,r1,r2):
	cumulative=False
	ratio= abs(r1)/abs(r2)
	if ratio>=r:
		cumulative=True
	else:
		cumulative=False
	return cumulative,ratio	

def setting_strike_price(setting_sp_closeTime,selected_strike_price,OI_Data):
	setting_sp_startTime = output_date+ " 091500"
	a=getting_ohlc_nifty(setting_sp_startTime,setting_sp_closeTime)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		strike=int(float(a[4]) - float(a[4])%100)
		A=np.array(OI_Data)
		row_info=(np.where(A[:,0]==strike)[0][0].tolist())
		a1=getting_ohlc_strike(OI_Data[row_info][1],setting_sp_startTime,setting_sp_closeTime)
		a2=getting_ohlc_strike(OI_Data[row_info][3],setting_sp_startTime,setting_sp_closeTime)
		p1=float(a1[4])
		p2=float(a2[4])
		p = int((p1+p2+50)/100) + 1	
		if p<=2:
			p=3
		
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		for_CE_STRIKE = float(a[3]) + abs(100- (float(a[3])%100))
		selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = float(a[2]) - abs((float(a[2])%100))
		selected_check_pe.append(for_PE_STRIKE)
		i=0
		for i in range(p-1):
			for_CE_STRIKE=for_CE_STRIKE+100 
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE-100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check,p

def gap_up_down_check(date,a):

	output_format = '%b %d %Y'
	original_datetime = datetime.strptime(date,output_format)
	previous_datetime = original_datetime - timedelta(days=1)
	if previous_datetime.weekday() >= 5:
			previous_datetime = previous_datetime - timedelta(days=previous_datetime.weekday() - 4)
	previous_date = previous_datetime.date()
	previous_date_str = (previous_date.strftime(output_format))
	time1=previous_date_str + " 143000"
	time2=previous_date_str + " 153000"

	a1=getting_ohlc_nifty(str(time1),str(time2))
	# a1=getting_nifty_data_from_excel(previous_date_str,62,74)
	last_day_high=float(a1[2])
	last_day_low=float(a1[3])
	if (last_day_high + (1.5*(last_day_high)/100)) < float(a[2]):
		print("Big Gap Up")
	elif(last_day_low - (1.5*(last_day_low)/100) ) > float(a[3]):
		print("Big Gap Down")

	
	if (last_day_high + 50) < float(a[2]):
		print("Gap Up")
		return "UP"
	elif(last_day_low - 50) > float(a[3]):
		print("Gap Down")
		return "DOWN"
	else:
		return ''	

def shifting_strike_price(setting_sp_closeTime,selected_strike_price,p):
	setting_sp_startTime = output_date+ " 091500"
	a=getting_ohlc_nifty(setting_sp_startTime,setting_sp_closeTime)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		for_CE_STRIKE = float(a[3]) + abs(100- (float(a[3])%100))
		selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = float(a[2]) - abs((float(a[2])%100))
		selected_check_pe.append(for_PE_STRIKE)
		i=0
		for i in range(p-1):
			for_CE_STRIKE=for_CE_STRIKE+100 
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE-100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check
	

def previous_day_OI_set_Instrument_set(output_date):
    t=0
    i=0
    j=0
    """Check before 9:15 and only once"""
    output_opening_time = output_date+ " 090000"
    output_closing_time = output_date + " 091530"
    a1=getting_ohlc_nifty(output_opening_time,output_closing_time)
    Nifty_SP=float(a1[4])
    """range to be -350 to +350"""
    Nifty_Strike=Nifty_SP - 500 - (Nifty_SP%100)
    while Nifty_SP+500> Nifty_Strike:
        OI_Data[i][j]=Nifty_Strike
        j=j+1
        response = xt.get_option_symbol(
            exchangeSegment=2,
            series='OPTIDX',
            symbol='NIFTY',
            expiryDate=prefix[5:],
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
            expiryDate=prefix[5:],
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


def set_data_for_max_oi(OI_Data,selected_check):
	
	A=np.array(OI_Data)
	row_info=[]

	for i in selected_check:
		row_info.append(np.where(A[:,0]==i)[0][0].tolist())

	oi_info_ce=[]
	oi_info_pe=[]
	for i in range(int(len(selected_check)/2)):
		oi_info_ce.append(OI_Data[row_info[i]][9])
		oi_info_pe.append(OI_Data[row_info[i+ int(len(selected_check)/2)]][10])
	max_value_ce=max(oi_info_ce)
	max_index_ce=oi_info_ce.index(max_value_ce)

	max_value_pe=max(oi_info_pe)
	max_index_pe=oi_info_pe.index(max_value_pe)
	
	max_oi_call = OI_Data[ row_info[0] + max_index_ce*2 ][9]
	last_day_call_oi = OI_Data[ row_info[0] + max_index_ce*2 ][2]
	indx_ce=[ row_info[0] + max_index_ce*2 ]

	max_oi_put=OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2 ][10]
	last_day_put_oi= OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2][4]
	indx_pe=[  row_info[int(len(selected_check)/2)] - max_index_pe*2 ]
	
	return max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe


"""Market Timing Setup"""
# print("\n Current time: ",datetime.now())  
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
OI_Data = [[0] * 11 for _ in range(11)]
previous_day_OI_set_Instrument_set(output_date)
# print(OI_Data)
# print(instruments_OI)

Specify_the_Open_TIME_HHMM = '0930'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

"""Strike price set for the day to store SP and Data"""
output_opening_time = output_date+ " 090000"
output_closing_time = output_date + " 093000"
a=getting_ohlc_nifty(output_opening_time,output_closing_time)
Strike_Price_Set=strike_price_for_data(a)
# print(Strike_Price_Set)

"""Setting Consider Strike Price"""
output_closing_time = output_date + " 093000"
selected_strike_price,p = setting_strike_price(output_closing_time,[],OI_Data)
print(output_date)
print(selected_strike_price)

"""setting one more imp sp in case of gap up and down"""
extra_sp_ce=0
extra_sp_pe=0
output_closing_time = output_date + " 092000"
a1=getting_ohlc_nifty(output_opening_time,output_closing_time)
gap=gap_up_down_check(output_date,a1)
if gap=="UP":
	extra_sp_ce=selected_strike_price[0]-100
	print(extra_sp_ce)
elif gap=="DOWN":
	extra_sp_pe=selected_strike_price[int(len(selected_strike_price)/2)]+100
	print(extra_sp_pe)

Specify_the_Open_TIME_HHMM = '1455'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
first=True
first1=True
crossover_by_pe=False
crossover_by_ce=False
count=0
count1=0
cross_by_pe_high=0
cross_by_ce_low=20000
time_of_crossover_ce=''
time_of_crossover_pe=''
set_oi_put=0
set_oi_call=0
trade=False
Cumulative_for_PE=False
Cumulative_for_CE=False
B=np.array(OI_Data)
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
	response = xt.get_quote(
			Instruments=instruments_OI,
			xtsMessageCode=1510,
			publishFormat='JSON')
	for i in range(len(Strike_Price_Set)*2 - 2):
		json_string = response['result']['listQuotes'][i]
		j=0
		data=json.loads(json_string)
		OpenInterest=data["OpenInterest"]
		# print(OpenInterest)
		if i%2==0:
			Change=((OpenInterest)-OI_Data[int(i/2)][j+2])
			OI_Data[int(i/2)][j+7]=OI_Data[int(i/2)][j+5]
			OI_Data[int(i/2)][j+5]=Change
			OI_Data[int(i/2)][j+9]=(OpenInterest)
		else:
			Change=((OpenInterest)-OI_Data[int(i/2)][j+4])
			OI_Data[int(i/2)][j+8]=OI_Data[int(i/2)][j+6]
			OI_Data[int(i/2)][j+6]=Change	
			OI_Data[int(i/2)][j+10]=(OpenInterest)
		i=i+1

	"""Setting Data of Selected strike price for data collection"""
	max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe= set_data_for_max_oi(OI_Data,selected_strike_price)
	
	"""Setiing crossover condition """			
	if last_day_call_oi > last_day_put_oi:
		if max_oi_put > max_oi_call:					
			if first:
				print("crossover_by_pe")
				crossover_by_pe=True
				crossover_by_ce=False
				count=0
				t1 = time.strftime("%H%M%S",time.localtime())
				output_closing_time = output_date +" " +t1
				a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
				if float(a1[4]) > cross_by_pe_high:
					time_of_crossover_pe=t1
					cross_by_pe_high=float(a1[4])
				set_oi_call=0
				first=False	
				first1=True			
		elif crossover_by_pe:
			print("Again Crossover by call")
			t1 = time.strftime("%H%M%S",time.localtime())
			output_closing_time = output_date +" " +t1
			a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
			if float(a1[4]) < cross_by_ce_low:
				time_of_crossover_ce=t1
				cross_by_ce_low=float(a1[4])
			set_oi_put=0
			count1=0
			crossover_by_ce=True
			crossover_by_pe=False
			first=True				
	else:
		if max_oi_call > max_oi_put:
			if first1:
				print("crossover_by_ce")
				crossover_by_ce=True
				crossover_by_pe=False
				set_oi_put=0
				count1=0
				t1 = time.strftime("%H%M%S",time.localtime())
				output_closing_time = output_date +" " +t1
				a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
				if float(a1[4]) < cross_by_ce_low:
					time_of_crossover_ce=t1
					cross_by_ce_low=float(a1[4])
				first1=False
				first=True
		elif crossover_by_ce:
			print("Again Crossover by Put")
			crossover_by_pe=True
			crossover_by_ce=False
			count=0
			t1 = time.strftime("%H%M%S",time.localtime())
			output_closing_time = output_date +" " +t1
			a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
			if float(a1[4]) > cross_by_pe_high:
				time_of_crossover_pe=t1
				cross_by_pe_high=float(a1[4])		
			set_oi_call=0
			first1=True

	"""pcr and cpr ratio 125%"""
	if crossover_by_pe and trade==False:
		Cumulative_for_PE,ratio = ratio_125_check(1.2,max_oi_put,max_oi_call)
		if Cumulative_for_PE:
			print("PCR Ratio")
	if crossover_by_ce and trade==False:
		Cumulative_for_CE,ratio = ratio_125_check(1.2,max_oi_call,max_oi_put)
		if Cumulative_for_CE:
			print("CPR Ratio")

	"""Reduction and Trade Point Setup"""
	if ( crossover_by_ce and extra_sp_pe==0):
		t1 = time.strftime("%H%M%S",time.localtime())
		if time_of_crossover_ce==t1:
			set_oi_put=OI_Data[indx_pe[0]][10]
			print(set_oi_put)
		else:
			set_oi_put=max(set_oi_put,OI_Data[indx_pe[0]][10])
			if (set_oi_put * 0.95) > OI_Data[indx_pe[0]][10]:
				print("Put Reduces")
				if count==0 and time_of_crossover_ce!=t1:
					output_opening_time = output_date +" " +time_of_crossover_ce 
					output_closing_time = output_date +" " +t1
					a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
					if a1==['']:
						print("Ignore once")
					else:	
						trade_point=float(a1[3])
						print(trade_point - 10)
						count=count+1
	elif (crossover_by_ce  and extra_sp_pe!=0):
		t1 = time.strftime("%H%M%S",time.localtime())
		row_info=np.where(B[:,0]==extra_sp_pe)[0].tolist()
		if time_of_crossover_ce==t1:
			set_oi_put=OI_Data[row_info[0]][10]
			print(set_oi_put)
		else:
			set_oi_put=max(set_oi_put,OI_Data[row_info[0]][10])
			if (set_oi_put * 0.95) > OI_Data[row_info[0]][10]:
				print("Put Reduces")
				if count==0 and time_of_crossover_ce!=t1:
					output_opening_time = output_date +" " +time_of_crossover_ce 
					output_closing_time = output_date +" " +t1
					a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
					if a1==['']:
						print("Ignore once")
					else:	
						trade_point=float(a1[3])
						print(trade_point - 10)
						count=count+1
															
	if ( crossover_by_pe  and extra_sp_ce==0):
		t1 = time.strftime("%H%M%S",time.localtime())
		if time_of_crossover_pe==t1:
			set_oi_call=OI_Data[indx_ce[0]][9]
			print(set_oi_call)
		else:
			set_oi_call=max(set_oi_call,OI_Data[indx_ce[0]][9])
			if (set_oi_call * 0.95) > OI_Data[indx_ce[0]][9]:
				print("Call Reduces")
				if count1==0 and time_of_crossover_pe!=t1:
					output_opening_time = output_date +" " +time_of_crossover_pe 
					output_closing_time = output_date +" " +t1
					a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
					if a1==['']:
						print("Ignore Once")
					else:	
						trade_point=float(a1[2])
						print(trade_point + 10)
						count1=count1+1
	elif(crossover_by_pe and extra_sp_ce !=0):
		t1 = time.strftime("%H%M%S",time.localtime())
		row_info=np.where(B[:,0]==extra_sp_ce)[0].tolist()
		if time_of_crossover_pe==t1:
			set_oi_call=OI_Data[row_info[0]][9]
			print(set_oi_call)
		else:
			set_oi_call=max(set_oi_call,OI_Data[row_info[0]][9])
			if (set_oi_call * 0.95) > OI_Data[row_info[0]][9]:
				print("Call Reduces")
				if count1==0 and time_of_crossover_pe!=t1:
					output_opening_time = output_date +" " +time_of_crossover_pe 
					output_closing_time = output_date +" " +t1
					a1=getting_ohlc_nifty(output_opening_time, output_closing_time)
					if a1==['']:
						print("Ignore Once")
					else:	
						trade_point=float(a1[2])
						print(trade_point + 10)
						count1=count1+1
	
	if (Cumulative_for_PE and crossover_by_pe and ratio<=1.30) and count1==1 and trade==False:
		print("Take a Trade if Price Point goes above " + str(trade_point+10))

	if (Cumulative_for_CE and crossover_by_ce and ratio<=1.30) and count==1 and trade==False:
		print("Take a Trade if Price Point goes below " + str(trade_point-10))	

	"""Shifting Of Selected Strike Price"""
	t1 = time.strftime("%H%M%S",time.localtime())
	output_closing_time = output_date +" " +t1
	selected_check1=shifting_strike_price(output_closing_time,selected_strike_price,p)
	if selected_check1!=selected_strike_price:
		selected_strike_price=selected_check1
		print(selected_check1)
	# for rows in OI_Data:
	# 	print(rows)
	print("Test")
	time.sleep(60)
	# print(curr_tm_chk)

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
response = xt.interactive_login()

day=''
header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/3_7/ex-date/Oct-Nov/Bank'
nifty_path = './Nirmal_Fincap/Nifty/2022/'
n_path = nifty_path + 'data.csv'

prefix=" "
m=1
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'
max_drawdown=0

def date_from_file_name(i):
	return i[10:20]

def day_from_date(date):
	date_obj = datetime.strptime(date,'%d-%m-%Y')
	return date_obj.strftime('%A')

def change_date_format(date):
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

def getting_ohlc_nifty(opening_time,closing_time):
	
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26121,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		return a
	else:
		return a


def setting_prefix_suffix_for_excel_data_inner(sp):
	filter_based_on_sp=[]
	for i in sp[0:5]:
		temp=prefix+str(i)+"CE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1)
	for i in sp[5:]:
		temp=prefix+str(i)+"PE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1) 	
	return filter_based_on_sp

def setting_prefix_suffix_for_excel_data(sp):
	filter_based_on_sp=[]
	for i in sp[0:9]:
		temp=prefix+str(i)+"CE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1)
	for i in sp[9:]:
		temp=prefix+str(i)+"PE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1) 	
	return filter_based_on_sp

def select_itm_atm_otm_strike_price(output_date,selected_strike_price,m,n):

	output_opening_time = output_date+ " 090000"
	output_closing_time = output_date + " 100000"
	# a=getting_nifty_data_from_excel(output_date,m,n)
	# print(a)		
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	
	if a==['']:
		print("we cannot ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  float(a[4])%100 <=25:
			for_CE_STRIKE=int(float(a[4]) - float(a[4])%100)+200
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE=int(float(a[4]) - float(a[4])%100)-200
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		elif float(a[4])%100 >= 75:
			for_CE_STRIKE=int(float(a[4]) + (100 - float(a[4])%100))+200
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE = int(float(a[4]) + (100 - float(a[4])%100))-200
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		else:

			for_CE_STRIKE=int(float(a[4]) - float(a[4])%100) + 250
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE = int(float(a[4]) - float(a[4])%100) - 150
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		selected_check_ce = selected_check_ce[::-1]		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check

def trade_initiate(date,tick,time):

	df = pd.read_csv(path)
	strike=setting_prefix_suffix_for_excel_data(tick)
	def extract_info(sp1,time):
		filtered_data = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
				
		filtered_data  = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == '15:29:59')]
		extracted_data2 = filtered_data.to_dict('records')
		
		row1=[date,sp1,str(time),'15:29:59','Sell',extracted_data[0]['Close'],extracted_data2[0]['Close'],'']

		sl=extracted_data[0]['Close']*2

		print(row1,sl)
		return row1,sl
		
	sp1=tick
	row1,sl=extract_info(sp1,time)
			
	return row1,sl

def sl_check(time,trade_data,max_drawdown):
	t=0
	df = pd.read_csv(path)
	while t<m:
		time_obj = datetime.strptime(time, "%H:%M:%S")
		time_obj += timedelta(minutes=1)
		time_str = time_obj.strftime("%H:%M:%S")

		# filtered_data  = df.loc[(df['Ticker']== trade_data[-2][1] ) & (df['Time'] == time_str)]
		# extracted = filtered_data.to_dict('records')
		# close1=extracted[0]['High']

		filtered_data  = df.loc[(df['Ticker']== trade_data[-1][1] ) & (df['Time'] == time_str)]
		extracted = filtered_data.to_dict('records')
		close2=extracted[0]['High']
		
		max_drawdown = max(max_drawdown,close2)

		# print(close1-close2-sl)
		# if (close1-close2) >= (sl*1.8):
		# 	print("--------------------StopLoss Hit---------------------------------"+ str(number))
		t=t+1
	return max_drawdown

def setting_oi_change_data_inner(length,filter_based_on_sp,selected_check,OI_Data,time):
	df = pd.read_csv(path)	
	for i in range(int(length/2)):
		"""Enter Strike price"""
		OI_Data[i][0]=selected_check[(i)]
		
		"""Enter Call OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][1]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
				print("4th Wrong Data")
		"""Enter Put OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+5] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][2]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i+5][12:17]) in selected_check else False):
				print("5th Wrong Data")		
		
	return OI_Data	


def setting_oi_change_data(length,filter_based_on_sp,selected_check,OI_Data):
	df = pd.read_csv(path)	
	for i in range(int(length/2)):
		"""Enter Strike price"""
		OI_Data[i][0]=selected_check[(i)]
		
		"""Enter Call OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == '9:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if extracted_data==[]:
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == '09:15:59')]
			extracted_data = filtered_data.to_dict('records')

		if(extracted_data != []):
			OI_Data[i][1]=extracted_data[0]['Open Interest']
		else:
			# if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
			print("4th Wrong Data")
		"""Enter Put OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+9] ) & (df['Time'] == '9:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if extracted_data==[]:
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == '09:15:59')]
			extracted_data = filtered_data.to_dict('records')

		if(extracted_data != []):
			OI_Data[i][2]=extracted_data[0]['Open Interest']
		else:
			# if (True if float(filter_based_on_sp[i+5][12:17]) in selected_check else False):
			print("5th Wrong Data")		
		
	return OI_Data		

def update_oi_data_inner(length,filter_based_on_sp,selected_check,OI_Data,time):
	df = pd.read_csv(path)
	for i in range(int(length/2)):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][5]=OI_Data[i][3]
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1]
			OI_Data[i][7]=extracted_data[0]['Open Interest']
		else:
			# if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
			print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+5] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][6]=OI_Data[i][4]
			OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
			OI_Data[i][8] = extracted_data[0]['Open Interest']
		else:
			# if (True if float(filter_based_on_sp[i+5][12:17]) in selected_check else False):
			print("9th Wrong Data")				    
	return OI_Data

def update_oi_data(length,filter_based_on_sp,selected_check,OI_Data,time):
	df = pd.read_csv(path)
	for i in range(int(length/2)):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][19]=OI_Data[i][17] #8tick
			OI_Data[i][17]=OI_Data[i][15] #7tick
			OI_Data[i][15]=OI_Data[i][13] #6tick
			OI_Data[i][13]=OI_Data[i][11] #5tick
			OI_Data[i][11]=OI_Data[i][9] #4tick
			OI_Data[i][9]=OI_Data[i][7]	#3tick
			OI_Data[i][7]=OI_Data[i][5] # 2tick
			OI_Data[i][5]=OI_Data[i][3] # 1tick
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1] #0 tick current
			OI_Data[i][21]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+9] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][20]=OI_Data[i][18]
			OI_Data[i][18]=OI_Data[i][16]
			OI_Data[i][16]=OI_Data[i][14]
			OI_Data[i][14]=OI_Data[i][12]
			OI_Data[i][12]=OI_Data[i][10]
			OI_Data[i][10]=OI_Data[i][8]
			OI_Data[i][8]=OI_Data[i][6]
			OI_Data[i][6]=OI_Data[i][4]
			OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
			OI_Data[i][22] = extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i+9][12:17]) in selected_check else False):
				print("9th Wrong Data")				    
	return OI_Data

def check_greater_than_10lakh_addition(matrix,side):
	i=0
	max_index=0
	max_oi=-100000000000000 
	
	for row in matrix:
		if max_oi < row[3] and side=='CE':
			max_oi=row[3]
			max_index=i 
			i=i+1
		else:
			i=i+1

		if max_oi < row[4] and side=='PE':
			max_oi=row[4]
			max_index=i 
			i=i+1
		else:
			i =i+1			

	if max_oi>1000000:
		return max_index
	else:
		return 'No'	

def oi_subtraction_flag(OI_Data,index):
	if index%2==0:
		if OI_Data[int((index-2)/2)][3]>0:
			a=int(index/2)
			x=OI_Data[a][4]-OI_Data[a][6]
			y=OI_Data[a-1][4]-OI_Data[a-1][6]
			if (x<0 and y<0):
				return True
			elif x<0 and (abs(x) > abs(y)):
				return True 
			elif y<0 and (abs(y) > abs(x)):
				return True
			else:
				print("No Subraction in OI in this tick")
				return False
	else:
		if OI_Data[int((index+2)/2)][4]>0:
			a=int(index/2)
			x=OI_Data[a][3]-OI_Data[a][5]
			y=OI_Data[a+1][3]-OI_Data[a+1][5]
			if (x<0 and y<0):
				return True
			elif x<0 and (abs(x) > abs(y)):
				return True 
			elif y<0 and (abs(y) > abs(x)):
				return True
			else:
				print("No Subraction in OI in this tick")
				return False

def to_get_shift_value(matrix):
	max_value_at_ce=0
	max_value_at_pe=0
	j=0
	indx_ce=''
	indx_pe=''
	for row in matrix:
		if max_value_at_ce<row[3]:
			max_value_at_ce=row[3]
			indx_ce=j+1

		if max_value_at_pe<row[4]:
			max_value_at_pe=row[4]
			indx_pe=j+1
		j=j+1		
	return indx_ce,indx_pe

def check_for_addition_subtraction(a,b,c,d,e,f,g,h,time_obj):
	# if a-b>600000 or c-d >600000:
		# print("Added more than 6 lakh  "+ str(a-b) +"  " +str(c-d))

	# time_obj1= time_obj - timedelta(minutes=33)
	# time_stra= time_obj1.time().strftime("%H%M%S")
	# opening = output_date +" "+time_stra
	# time_strb= time_obj.time().strftime("%H%M%S")
	# closing = output_date +" "+time_strb
	# a=getting_ohlc_nifty(opening,closing)


	if e-f< -500000 or g-h < -500000:
		# if float(a[2]) - float(a[3]) >= 32 :
		return True
		# else:
		# 	print("Price point not travel specific distance in last 30 mins")
		# 	return True		
	else:
		return False

def price_of_atm_strike_price(selected_itm_Sp,time):
	df = pd.read_csv(path)
	
	filtered_data = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == str(time))]
	extracted_data = filtered_data.to_dict('records')

	filtered_data  = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == '15:29:59' )]
	extracted_data2 = filtered_data.to_dict('records')

	price=[selected_itm_Sp,extracted_data[0]['Close'],extracted_data2[0]['Close']] 
			
		
	return price

def select_itm_atm_otm_strike_price_inner(output_date,selected_strike_price,time_obj,n):
	time_str = time_obj.strftime("%H%M%S")
	output_opening_time = output_date+ " 090000"
	output_closing_time = output_date + " "+str(time_str)
		
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	# a=getting_nifty_data_from_excel(output_date,0,n)
	# a=getting_nifty_data_from_excel(date,m,n)
	if a==['']:
		print("we cannot ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  float(a[4])%100 <=25:
			for_CE_STRIKE=int(float(a[4]) - float(a[4])%100)+100
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE=int(float(a[4]) - float(a[4])%100)-100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		elif float(a[4])%100 >= 75:
			for_CE_STRIKE=int(float(a[4]) + (100 - float(a[4])%100))+100
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE = int(float(a[4]) + (100 - float(a[4])%100))-100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		else:

			for_CE_STRIKE=int(float(a[4]) - float(a[4])%100) + 150
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)

			for_PE_STRIKE = int(float(a[4]) - float(a[4])%100) - 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
		selected_check_ce = selected_check_ce[::-1]		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check													

def premium_discount(time_obj):
	df = pd.read_csv(path)

	time_str3= time_obj.time().strftime("%H%M%S")
	output_closing_time = output_date +" "+time_str3
	output_opening_time = output_date+ " 090000"
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	if a==['']:
		return 0
	# print(a)
	sp=0
	if True:
		sp= int(float(a[4]) - float(a[4])%25)
	pass_index=prefix+str(sp)+"CE.NFO"
	pass_index1=prefix+str(sp)+"PE.NFO"


	filtered_data = df.loc[(df['Ticker']== pass_index ) & (df['Time'] == str(time_obj.time()))]
	extracted_data = filtered_data.to_dict('records')
	# print(extracted_data)
	filtered_data  = df.loc[(df['Ticker']== pass_index1 ) & (df['Time'] == str(time_obj.time()) )]
	extracted_data2 = filtered_data.to_dict('records')
	# print(extracted_data2)
	synthetic = sp + extracted_data[0]['Close'] - extracted_data2[0]['Close']

	if synthetic > float(a[4]):
		print(synthetic - float(a[4]))
		return synthetic - float(a[4])
	elif float(a[4]) >= synthetic:
		print(synthetic - float(a[4]))
		return synthetic - float(a[4])	

	  		

with open(filepath, 'w', newline='') as file:
	writer=csv.writer(file)
	writer.writerow(header)
	for i in files:
		path=folder_path+'/'+i
		"""----------------- ---------------Setting Date Format--------------------------------------------------"""
		date=date_from_file_name(i)
		print(date)

		day=day_from_date(date)
		print(day)
		day, month, year = date.split('-')
		month_mapping = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR','05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG','09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}
		month_abbr = month_mapping.get(month)
		formatted_date = f"{day}{month_abbr}{year[-2:]}"
		print(formatted_date)
		prefix= "MIDCPNIFTY" + formatted_date
		"""Setting the date Format to extract data for that Particular Date"""
		output_date=change_date_format(date)

		output_opening_time = output_date+ " 090000"
		output_closing_time = output_date + " 100000"
		selected_itm_Sp = select_itm_atm_otm_strike_price(output_date,[],0,46)
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(selected_itm_Sp)
		length=int(len(selected_itm_Sp))

		OI_Data = [[0] * 23 for _ in range(int(length/2))]
		OI_Data_inner = [[0] * 9 for _ in range(int(length/2))]
		selected_itm_Sp_inner=[]
		filter_based_on_sp_inner=[]
		OI_Data = setting_oi_change_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data)	

		time_str = '10:00:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		flag_side=''
		flag_time=''
		first=False
		trade=False
		trade_side=''
		trade_side1=''
		n=46
		important_sp=[]
		traded_sp_index=''
		
		entry_price=0
		trade_data=[]
		flag_divergence=False

		ce_side_best_change=0
		pe_side_best_change=0
		ce_side_best_change_index=''
		pe_side_best_change_index=''
		shift_side_c=''
		shift_side_p=''
		trending_flag=''
		first1=True	
		flag_time=time_obj

		premium_count=0
		discount_count=0

		while time_obj.time() < datetime.strptime('15:15:59', '%H:%M:%S').time():
			# OI_Data=update_oi_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data,time_obj.time())
			print(time_obj.time())

			value=premium_discount(time_obj)


			if value>5:
				premium_count=premium_count+1
				discount_count=0
				if premium_count==5:
					print("--------Premium--------------")
			elif value <-5:
				discount_count=discount_count+1
				premium_count=0
				if discount_count==5:
					print("--------------Discount------------------")
						

			time_obj += timedelta(minutes=m)
			n=n+1	
		print("---------------------------------------------------------------------------------------------------------------")


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

day=''
header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2022/9/expiry3'
nifty_path = './'
n_path = nifty_path + 'nifty_cash_5min.csv'
vix_path= nifty_path + 'vix.csv'

prefix="NIFTY15SEP22"
m=1
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'
max_drawdown=0

def date_from_file_name(i):
	return i[10:20]

def day_from_date(date):
	date_obj = datetime.strptime(date,'%d-%m-%Y')
	return date_obj.strftime('%A')

def add_a_minute(closing_time):
	format = "%b %d %Y %H%M%S"
	dt = datetime.strptime(closing_time, format)
	dt += timedelta(minutes=1)
	updated_datetime_str = dt.strftime(format)
	return updated_datetime_str

def getting_ohlc_nifty(opening_time,closing_time):
	closing_time=add_a_minute(closing_time)
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		return a
	else:
		return a

def getting_nifty_data_from_excel(date,m,n):
	a1=[]
	df1 = pd.read_csv(n_path)
	filtered_data = df1.loc[(df1['Date']== date)][m:n]
	a1.append(filtered_data['Open'].iloc[0])
	a1.append(filtered_data['High'].max())
	a1.append(filtered_data['Low'].min())
	a1.append(filtered_data['Close'].iloc[-1])
	return a1

def change_date_format(date):
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[2])) - (int(float(a[2])%100)) - 500
	while int(float(a[1]))+500 > SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+100
	return sp	

def setting_prefix_suffix_for_excel_data(sp):
	filter_based_on_sp=[]
	for i in sp:
		temp=prefix+str(i)+"CE.NFO"
		temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		filter_based_on_sp.append(temp1)
	return filter_based_on_sp	


def select_itm_strike_price(setting_sp_closeTime,selected_strike_price,m,n):
	a=getting_nifty_data_from_excel(date,m,n)
	print(a)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  a[3]%100 <= 80:
			for_CE_STRIKE=int(a[3] - a[3]%100) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 100
			selected_check_pe.append(for_PE_STRIKE)
		elif a[3]%100 > 80:
			for_CE_STRIKE=int(a[3] + (100-a[3]%100)) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] + (100-a[3]%100))+100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check		

def shift_itm_strike_price(setting_sp_closeTime,selected_strike_price,m,n):
	a=getting_nifty_data_from_excel(date,m,n)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  a[3]%100 <= 80:
			for_CE_STRIKE=int(a[3] - a[3]%100) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 100
			selected_check_pe.append(for_PE_STRIKE)
		elif a[3]%100 > 80:
			for_CE_STRIKE=int(a[3] + (100-a[3]%100)) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] + (100-a[3]%100))+100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check

def setting_strike_price(setting_sp_closeTime,selected_strike_price,m,n):
	# setting_sp_startTime = output_date+ " 091500"
	# a=getting_ohlc_nifty(setting_sp_startTime,setting_sp_closeTime)
	a=getting_nifty_data_from_excel(date,m,n)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		strike=int(a[3] - a[3]%50)
		temp=prefix+str(strike)+"CE.NFO"
		temp1=prefix+str(strike)+"PE.NFO"
		df = pd.read_csv(path)
		filtered_data = df.loc[(df['Ticker']== temp) & (df['Time'] == '09:29:59')]
		extracted_data = filtered_data.to_dict('records')
		p1=extracted_data[0]['Close']
		filtered_data = df.loc[(df['Ticker']== temp1) & (df['Time'] == '09:29:59')]
		extracted_data = filtered_data.to_dict('records')
		p2=extracted_data[0]['Close']
		# print(p1 + p2)
		p = int((p1+p2+50)/100) + 1	
		if p<=2:
			p=3
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		for_CE_STRIKE = float(a[2]) + abs(100- (float(a[2])%100))
		selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = float(a[1]) - abs((float(a[1])%100))
		selected_check_pe.append(for_PE_STRIKE)
		i=0
		for i in range(p-1):
			for_CE_STRIKE=for_CE_STRIKE+100 
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE-100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check,p

def shifting_strike_price(setting_sp_closeTime,selected_strike_price,m,n,p):
	# setting_sp_startTime = output_date+ " 091500"
	# a=getting_ohlc_nifty(setting_sp_startTime,setting_sp_closeTime)
	a=getting_nifty_data_from_excel(date,m,n)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		strike=int(a[3] - a[3]%50)
		temp=prefix+str(strike)+"CE.NFO"
		temp1=prefix+str(strike)+"PE.NFO"

		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		for_CE_STRIKE = float(a[2]) + abs(100- (float(a[2])%100))
		selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = float(a[1]) - abs((float(a[1])%100))
		selected_check_pe.append(for_PE_STRIKE)
		i=0
		for i in range(p-1):
			for_CE_STRIKE=for_CE_STRIKE+100 
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE-100
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check				


def setting_oi_change_data(length,filter_based_on_sp,selected_check,OI_Data,OI_Data_15min,OI_Data_20min,OI_Data_30min):
	df = pd.read_csv(path)	
	for i in range(length):
		"""Enter Strike price"""
		OI_Data[i][0]=Strike_Price_Set[(i)]
		OI_Data_15min[i][0]=Strike_Price_Set[(i)]
		OI_Data_20min[i][0]=Strike_Price_Set[(i)]
		OI_Data_30min[i][0]=Strike_Price_Set[(i)]
		
		"""Enter Call OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][1]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][1]=extracted_data[0]['Open Interest']
			OI_Data_20min[i][1]=extracted_data[0]['Open Interest']
			OI_Data_30min[i][1]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("4th Wrong Data")
		"""Enter Put OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][2]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][2]=extracted_data[0]['Open Interest']
			OI_Data_20min[i][2]=extracted_data[0]['Open Interest']
			OI_Data_30min[i][2]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("5th Wrong Data")		
		
		"""Enter Change OI Data in CE at 10:00"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:59:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1] 
			OI_Data[i][7]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_15min[i][1] 
			OI_Data_15min[i][7]=extracted_data[0]['Open Interest']
			OI_Data_20min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_20min[i][1] 
			OI_Data_20min[i][7]=extracted_data[0]['Open Interest']
			OI_Data_30min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_30min[i][1] 
			OI_Data_30min[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("6th Wrong Data")
		"""Enter Change OI Data in PE at 09:30"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:59:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][4] = extracted_data[0]['Open Interest'] -OI_Data[i][2] 
			OI_Data[i][8]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][4] = extracted_data[0]['Open Interest'] -OI_Data_15min[i][2] 
			OI_Data_15min[i][8]=extracted_data[0]['Open Interest']	
			OI_Data_20min[i][4] = extracted_data[0]['Open Interest'] -OI_Data_20min[i][2] 
			OI_Data_20min[i][8]=extracted_data[0]['Open Interest']
			OI_Data_30min[i][4] = extracted_data[0]['Open Interest'] -OI_Data_30min[i][2] 
			OI_Data_30min[i][8]=extracted_data[0]['Open Interest']		
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("7th Wrong Data")

	return OI_Data,OI_Data_15min,OI_Data_20min,OI_Data_30min			


def update_oi_data(length,filter_based_on_sp,selected_check,OI_Data,time):
	df = pd.read_csv(path)
	for i in range(length):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][5]=OI_Data[i][3]
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1]
			OI_Data[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][6]=OI_Data[i][4]
			OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
			OI_Data[i][8] = extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("9th Wrong Data")	    
	return OI_Data

def update_oi_data_15(length,filter_based_on_sp,selected_check,OI_Data_15min,time):
	df = pd.read_csv(path)
	for i in range(length):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_15min[i][5]=OI_Data_15min[i][3]
			OI_Data_15min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_15min[i][1]
			OI_Data_15min[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_15min[i][6]=OI_Data_15min[i][4]
			OI_Data_15min[i][4] =  extracted_data[0]['Open Interest'] - OI_Data_15min[i][2]
			OI_Data_15min[i][8] = extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("9th Wrong Data")	    
	return OI_Data_15min

def update_oi_data_20(length,filter_based_on_sp,selected_check,OI_Data_20min,time):
	df = pd.read_csv(path)
	for i in range(length):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_20min[i][5]=OI_Data_20min[i][3]
			OI_Data_20min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_20min[i][1]
			OI_Data_20min[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_20min[i][6]=OI_Data_20min[i][4]
			OI_Data_20min[i][4] =  extracted_data[0]['Open Interest'] - OI_Data_20min[i][2]
			OI_Data_20min[i][8] = extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("9th Wrong Data")	    
	return OI_Data_20min

def update_oi_data_30(length,filter_based_on_sp,selected_check,OI_Data_30min,time):
	df = pd.read_csv(path)
	for i in range(length):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_30min[i][5]=OI_Data_30min[i][3]
			OI_Data_30min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_30min[i][1]
			OI_Data_30min[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data_30min[i][6]=OI_Data_30min[i][4]
			OI_Data_30min[i][4] =  extracted_data[0]['Open Interest'] - OI_Data_30min[i][2]
			OI_Data_30min[i][8] = extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("9th Wrong Data")	    
	return OI_Data_30min

def extra_sp_data_save(OI_Data,extra_sp,option_type):
	A=np.array(OI_Data)
	row_info1=np.where(A[:,0]==extra_sp)[0].tolist()
	if option_type=='CE':
		return OI_Data[row_info1[0]][7],OI_Data[row_info1[0]][1]
	if option_type=='PE':
		return OI_Data[row_info1[0]][8],OI_Data[row_info1[0]][2],


def set_data_for_max_oi(OI_Data,selected_check,india_vix):
	
	A=np.array(OI_Data)
	row_info=[]

	for i in selected_check:
		row_info.append(np.where(A[:,0]==i)[0][0].tolist())

	oi_info_ce=[]
	oi_info_pe=[]
	for i in range(int(len(selected_check)/2)):
		oi_info_ce.append(OI_Data[row_info[i]][7])
		oi_info_pe.append(OI_Data[row_info[i+ int(len(selected_check)/2)]][8])
	max_value_ce=max(oi_info_ce)
	max_index_ce=oi_info_ce.index(max_value_ce)

	max_value_pe=max(oi_info_pe)
	max_index_pe=oi_info_pe.index(max_value_pe)
	
	max_oi_call = OI_Data[ row_info[0] + max_index_ce*2 ][7]
	last_day_call_oi = OI_Data[ row_info[0] + max_index_ce*2 ][1]
	indx_ce=[ row_info[0] + max_index_ce*2 ]

	max_oi_put=OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2 ][8]
	last_day_put_oi= OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2][2]
	indx_pe=[  row_info[int(len(selected_check)/2)] - max_index_pe*2 ]
	
	return max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe
			

def set_data_for_max_change_in_oi(OI_Data,selected_check):
	A=np.array(OI_Data)
	
	row_info=[]

	for i in selected_check:
		row_info.append(np.where(A[:,0]==i)[0][0].tolist())

	oi_info_ce=[]
	oi_info_pe=[]
	for i in range(int(len(selected_check)/2)):
		oi_info_ce.append(abs(OI_Data[row_info[i]][3]))
		oi_info_pe.append(abs(OI_Data[row_info[i+ int(len(selected_check)/2)]][4]))

	max_value_ce=max(oi_info_ce)
	max_index_ce=oi_info_ce.index(max_value_ce)

	max_value_pe=max(oi_info_pe)
	max_index_pe=oi_info_pe.index(max_value_pe)

	max_oi_call_chng = OI_Data[ row_info[0] + max_index_ce*2 ][7]
	last_day_call_oi_chng = OI_Data[ row_info[0] + max_index_ce*2 ][1]
	indx_ce_chng=[ row_info[0] + max_index_ce*2 ]

	max_oi_put_chng=OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2 ][8]
	last_day_put_oi_chng= OI_Data[ row_info[int(len(selected_check)/2)] - max_index_pe*2][2]
	indx_pe_chng=[  row_info[int(len(selected_check)/2)] - max_index_pe*2 ]
		
	return max_oi_call_chng,last_day_call_oi_chng,indx_ce_chng,max_oi_put_chng,last_day_put_oi_chng,indx_pe_chng


# def check_itm_exist_in_top_OIs(OI_Data,Strike_Price_Set,selected_itm_Sp):
# 	A=np.array(OI_Data)
# 	oi_info_ce=[]
# 	oi_info_pe=[]
# 	for i in range(int(len(Strike_Price_Set))):
# 		oi_info_ce.append((OI_Data[i][3]))
# 		oi_info_pe.append((OI_Data[i][4]))	

# 	arr = np.array(oi_info_ce)
# 	arr1 = np.array(oi_info_pe)

# 	arr_sorted = np.sort(arr)[::-1]
# 	arr_sorted1 = np.sort(arr1)[::-1]	

# 	top3_max_ce = arr_sorted[:3]
# 	top3_max_pe = arr_sorted1[:3]

# 	top3_indices_ce = [np.where(arr == max_val)[0] for max_val in top3_max_ce]
# 	top3_indices_pe = [np.where(arr1 == max_val)[0] for max_val in top3_max_pe]
# 	call=False
# 	put=False
# 	for i in range(3):
# 		if selected_itm_Sp[0]==OI_Data[top3_indices_ce[i][0]][0]:
# 			call=True
# 		if 	selected_itm_Sp[1]==OI_Data[top3_indices_pe[i][0]][0]:
# 			put=True
# 	return call,put 		

def pcr_ratio(OI_Data,Strike_Price_Set):
	A=np.array(OI_Data)
	oi_total_ce=0
	oi_total_pe=0
	for i in range(int(len(Strike_Price_Set))):
		oi_total_ce=oi_total_ce+OI_Data[i][7]
		oi_total_pe=oi_total_pe+OI_Data[i][8]
		# print(oi_total_pe)

	return oi_total_pe/oi_total_ce

def ratio_125_check(r,r1,r2,indx,indx_chng,s1,s2):
	cumulative=False
	ratio= abs(r1)/abs(r2)
	global max_pcr_cpr_ratio
	if ratio>=r:
		cumulative=True
		max_pcr_cpr_ratio = max(max_pcr_cpr_ratio,ratio)
	else:
		cumulative=False
	return cumulative,ratio									

def nifty_data_after_format_change(time1,time2):
	time_int = int(str(time1.time()).replace(':', ''))
	formatted_num = '{:06d}'.format(time_int)
	output_opening_time=output_date + " "+str(formatted_num)

	time_int = int(str(time2.time()).replace(':', ''))
	formatted_num = '{:06d}'.format(time_int)
	output_closing_time=output_date + " "+str(formatted_num)
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	return a

def trade_initiate(date,a,side,time):
	df = pd.read_csv(path)

	def extract_info(sp1,sp2,time,b):
		filtered_data = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		
		filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == str(time))]
		extracted_data1 = filtered_data.to_dict('records')
		
		filtered_data  = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == '15:19:59')]
		extracted_data2 = filtered_data.to_dict('records')
		
		filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == '15:19:59')]
		extracted_data3 = filtered_data.to_dict('records')
		
		row1=[date,sp1,str(time),'15:19:59','Sell',extracted_data[0]['Close'],extracted_data2[0]['Close'],'']
		row2=[date,sp2,str(time),'15:19:59','Buy',extracted_data1[0]['Close'],extracted_data3[0]['Close'],'']
		sl=extracted_data[0]['Close'] - extracted_data1[0]['Close']


		if sl>6.5:
			b=b+50
			if side=='PE.NFO':
				selling_sp=float(a[3]) - (float(a[3])%50) - float(b)
				buying_sp=selling_sp - 100
			else:
				selling_sp= float(a[3])  + (50 - float(a[3])%50) + float(b)
				buying_sp=selling_sp+100
		elif sl<3.5:
			b=b-50
			if side=='PE.NFO':
				selling_sp=float(a[3]) - (float(a[3])%50) - float(b)
				buying_sp=selling_sp - 100
			else:
				selling_sp= float(a[3])  + (50 - float(a[3])%50) + float(b)
				buying_sp=selling_sp+100
		else:
			print(row1,row2,sl)
			return row1,row2,sl

		sp1=prefix+str(int(selling_sp))+side
		sp2=prefix+str(int(buying_sp))+side
		row1,row2,sl=extract_info(sp1,sp2,time,b)
		return row1,row2,sl
		

	if side=='PE.NFO':
		selling_sp = float(a[3]) - (float(a[3])%50) -200
		buying_sp=selling_sp - 100
	else:
		selling_sp= float(a[3])  + (50 - float(a[3])%50) + 200
		buying_sp=selling_sp+100	
	sp1=prefix+str(int(selling_sp))+side
	sp2=prefix+str(int(buying_sp))+side
	row1,row2,sl=extract_info(sp1,sp2,time,200)
			
	return row1,row2,sl
				

def sl_check(time,trade_data,sl):
	t=0
	df = pd.read_csv(path)
	while t<m:
		time_obj = datetime.strptime(time, "%H:%M:%S")
		time_obj += timedelta(minutes=1)
		time_str = time_obj.strftime("%H:%M:%S")

		filtered_data  = df.loc[(df['Ticker']== trade_data[-2][1] ) & (df['Time'] == time_str)]
		extracted = filtered_data.to_dict('records')
		close1=extracted[0]['High']

		filtered_data  = df.loc[(df['Ticker']== trade_data[-1][1] ) & (df['Time'] == time_str)]
		extracted = filtered_data.to_dict('records')
		close2=extracted[0]['High']
		global max_drawdown
		max_drawdown = max(max_drawdown,close1-close2-sl)
		print(close1-close2-sl)
		if (close1-close2) >= (sl*1.8):
			print("--------------------StopLoss Hit---------------------------------")
		t=t+1


def gap_up_down_check(date,a):
	output_format = '%d-%m-%Y'
	original_datetime = datetime.strptime(date,output_format)
	previous_datetime = original_datetime - timedelta(days=1)
	if previous_datetime.weekday() >= 5:
			previous_datetime = previous_datetime - timedelta(days=previous_datetime.weekday() - 4)
	previous_date = previous_datetime.date()
	previous_date_str = (previous_date.strftime(output_format))
	time1=previous_date_str + " 143000"
	time2=previous_date_str + " 153000"

	# a1=getting_ohlc_nifty(str(time1),str(time2))
	a1=getting_nifty_data_from_excel(previous_date_str,62,74)
	last_day_high=float(a1[1])
	last_day_low=float(a1[2])
	if (last_day_high + (1.5*(last_day_high)/100)) < float(a[1]):
		print("Big Gap Up")
	elif(last_day_low - (1.5*(last_day_low)/100) ) > float(a[2]):
		print("Big Gap Down")

	
	if (last_day_high + 50) < float(a[1]):
		print("Gap Up")
		return "UP"
	elif(last_day_low - 50) > float(a[2]):
		print("Gap Down")
		return "DOWN"
	else:
		return ''	


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

		"""Setting the date Format to extract data for that Particular Date"""
		output_date=change_date_format(date)
		
		"""Get the Nifty Range of the Day for Setting Strike Price and Data filteration for the day"""	
		output_opening_time = output_date+ " 090000"
		output_closing_time = output_date + " 153000"
		
		# a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		a1=getting_nifty_data_from_excel(date,0,74)
		
		"""Setting Strike price for day range from -300 to + 300"""
		Strike_Price_Set=strike_price_for_data(a1)

		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(Strike_Price_Set)	

		"""Setting Strike Price For Day"""
		output_closing_time = output_date + " 100000"
		selected_itm_Sp = select_itm_strike_price(output_closing_time,[],0,10)
		print(selected_itm_Sp)

		"""Setting OI Data till 9:30 , Strike Price , Previous day OI IN Call and Put , 9:30 Clock OI of Call and Put"""
		length=int(len(Strike_Price_Set))
		OI_Data = [[0] * 9 for _ in range(length)]
		OI_Data_15min=[[0] * 9 for _ in range(length)]
		OI_Data_20min=[[0] * 9 for _ in range(length)]
		OI_Data_30min=[[0] * 9 for _ in range(length)]
		OI_Data,OI_Data_15min,OI_Data_20min,OI_Data_30min = setting_oi_change_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data,OI_Data_15min,OI_Data_20min,OI_Data_30min)
		""" SP, OI at 9:15_c , OI at 9:15 Put , OI at 9:15 Call, Oi at Time chnage , Oi at time Put chnage, last Oi , last Oi put , Cumulative , Cumulative put""" 
		time_str = '10:00:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		i=1
		j=1
		k=1
		A=np.array(OI_Data_15min)
		B=np.array(OI_Data_20min)
		C=np.array(OI_Data_30min)
		count15_C=0
		count20_C=0
		count30_C=0
		count15_P=0
		count20_P=0
		count30_P=0
		n=10
		price_15_C=0
		price_15_C2=0
		price_15_P=0
		price_15_P2=0
		price_20_C=0
		price_20_C2=0
		price_20_P=0
		price_20_P2=0
		price_30_C=0
		price_30_C2=0
		price_30_P=0
		price_30_P2=0
		minute_check=0
		trade=False
		trade_Side=''
		trade_point=0
		trade_open=''
		trade_data=[]
		# top3_call_15=False
		# top3_put_15=False
		# top3_call_20=False
		# top3_put_20=False
		# top3_call_30=False
		# top3_put_30=False

		while time_obj.time() < datetime.strptime('14:55:59', '%H:%M:%S').time():
			print(time_obj.strftime('%H:%M:%S'))

			"""Data Update on 1min basis"""
			OI_Data=update_oi_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data,time_obj.time())	
			ratio = pcr_ratio(OI_Data,Strike_Price_Set)
			# print(ratio)
			if i==15:
				OI_Data_15min=update_oi_data_15(length,filter_based_on_sp,selected_itm_Sp,OI_Data_15min,time_obj.time())
				row=np.where(A==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_15min[row[0]][5]-OI_Data_15min[row[0]][3] < 0 and trade==False):
					print("Added in ITM Call 15")
					count15_C=count15_C+1
					# call,put=check_itm_exist_in_top_OIs(OI_Data,Strike_Price_Set,selected_itm_Sp)
					# if call:
					# 	top3_call_15=True

					if count15_C==1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_15_C=float(a1[3])
						price_15_C=n
					elif count15_C>=3:
						a1=getting_nifty_data_from_excel(date,price_15_C,n)
						# print(a1)
						# print(price_15_C)
						# print(a1[3])
						if float(a1[3])*1.001 < float(price_15_C) and ratio>0.85:
						# if ratio>0.85:
							price_15_C2=float(a1[2])
							trade=True
							trade_Side='CE'
							print("Trade  Call below " + str(price_15_C2))
				else:
					print("No addition")
					count15_C=0
				
				
				row1=np.where(A==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_15min[row1[0]][6]-OI_Data_15min[row1[0]][4] < 0 and trade==False ):
					print("Added in ITM Put 15")
					count15_P=count15_P+1
					
					if count15_P==1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_15_P=float(a1[3])
						price_15_P=n
					elif count15_P>=3:
						a1=getting_nifty_data_from_excel(date,price_15_P,n)
						# print(price_15_P)
						# print(a1[3])
						if float(a1[3])*0.999 > price_15_P and ratio<1.15:
						# if ratio<1.15:
							price_15_P2=float(a1[1])
							trade=True
							trade_Side='PE'
							print("Trade Put above " + str(price_15_P2))
				else:
					print("No addition")
					count15_P=0	
				
				i=1
			else:
				i=i+1

			if j==20:
				OI_Data_20min=update_oi_data_20(length,filter_based_on_sp,selected_itm_Sp,OI_Data_20min,time_obj.time())
				row=np.where(B==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_20min[row[0]][5]-OI_Data_20min[row[0]][3] < 0 and trade==False):
					print("Added in ITM Call 20")
					count20_C=count20_C+1
	
					if count20_C==1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_20_C=float(a1[3])
						price_20_C=n
					elif count20_C>=3:
						a1=getting_nifty_data_from_excel(date,price_20_C,n)
						# print(price_20_C)
						# print(a1[3])
						if float(a1[3])*1.001 < price_20_C and ratio >0.85:
						# if ratio>0.85:
							price_20_C2=float(a1[2])
							trade=True
							trade_Side='CE'
							print("Trade  Call below " + str(price_20_C2))
				else:
					count20_C=0
					print("No addition")
				
				row1=np.where(B==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_20min[row1[0]][6]-OI_Data_20min[row1[0]][4] < 0 and trade==False):
					print("Added in ITM Put 20")
					count20_P=count20_P+1
					
					if count20_P==1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_20_P=float(a1[3])
						price_20_P=n
					elif count20_P>=3:
						a1=getting_nifty_data_from_excel(date,price_20_P,n)
						# print(price_20_P)
						# print(a1[3])
						if float(a1[3])*0.999 > price_20_P and ratio<1.15 :
						# if ratio<1.15:
							price_20_P2=float(a1[1])
							trade=True
							trade_Side='PE'
							print("Trade Put Above " + str(price_20_P2))
				else:
					count20_P=0
					print("No addition")
				j=1
			else:
				j=j+1

			if k==30:
				OI_Data_30min=update_oi_data_30(length,filter_based_on_sp,selected_itm_Sp,OI_Data_30min,time_obj.time())
				row=np.where(C==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_30min[row[0]][5]-OI_Data_30min[row[0]][3] < 0 and trade==False):
					print("Added in ITM Call 30")
					count30_C=count30_C+1

					if count30_C==1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_30_C=float(a1[3])
						price_30_C=n
					elif count30_C>=3:
						a1=getting_nifty_data_from_excel(date,price_30_C,n)
						# print(price_30_C)
						# print(a1[3])
						if float(a1[3])*1.001 < price_30_C and ratio > 0.85:
						# if ratio>0.85:
							price_30_C2=float(a1[2])
							trade=True
							trade_Side='CE'
							print("Trade  Call below " + str(price_30_C2))
				else:
					print("No addition")
					count30_C=0

				row1=np.where(C==selected_itm_Sp[0])[0].tolist()
				if( OI_Data_30min[row1[0]][6]-OI_Data_30min[row1[0]][4] < 0 and trade==False):
					print("Added in ITM Put 30")
					count30_P=count30_P+1

					if count30_P>=1:
						a1=getting_nifty_data_from_excel(date,n,n+1)
						# price_30_P=float(a1[3])
						price_30_P=n
					elif count30_P==3:
						a1=getting_nifty_data_from_excel(date,price_30_P,n)
						# print(price_30_P)
						# print(a1[3])
						if float(a1[3])*0.999 > price_30_P and ratio < 1.15:
						# if ratio<1.15:
							price_30_P2=float(a1[1])
							trade=True
							trade_Side='PE'
							print("Trade  Put Above " + str(price_30_P2))
				else:
					print("No addition")
					count30_P=0

				k=1
			else:
				k=k+1


			if trade and trade_Side=='PE' and trade_open=='':
				print("PE Bech Do")
				a1=getting_nifty_data_from_excel(date,n,n+1)
				if (a1[3] > price_15_P2 and price_15_P2!=0) or (a1[3] > price_20_P2 and price_20_P2!=0) or (a1[3] > price_30_P2 and price_30_P2!=0):
					row1,row2,sl=trade_initiate(output_date,a1,'PE.NFO',time_obj.time())
					trade=True
					trade_open='PUT'
					trade_data.append(row1)
					trade_data.append(row2)
					print("Difference : " + str(sl))	

			if trade and trade_Side=='CE' and trade_open=='':
				print("CE Bech Do")
				a1=getting_nifty_data_from_excel(date,n,n+1)
				if (a1[3] < price_15_C2 and price_15_C2!=0) or (a1[3] < price_20_C2 and price_20_C2!=0) or (a1[3] < price_30_C2 and price_30_C2!=0):
					row1,row2,sl=trade_initiate(output_date,a1,'CE.NFO',time_obj.time())
					trade=True
					trade_open='CALL'
					trade_data.append(row1)
					trade_data.append(row2)
					print("Difference : " + str(sl))


			"""Stop Loss Check """
			if trade and trade_open!='':
				sl_check(str(time_obj.time()),trade_data,sl)

			if minute_check==4:
				n=n+1
				minute_check=0
			else:
				minute_check=minute_check+1		
			
			time_obj += timedelta(minutes=m)

			"""Shifting Of Selected Strike Price"""
			time_int = int(str(time_obj.time()).replace(':', ''))
			formatted_num = '{:06d}'.format(time_int)
			output_closing_time=output_date + " "+str(formatted_num)
			selected_check1=shift_itm_strike_price(output_closing_time,selected_itm_Sp,0,n)
			if selected_check1[0]!=selected_itm_Sp[0]:
				selected_itm_Sp[0]=selected_check1[0]
				count30_C=0
				count20_C=0
				count15_C=0
				print(selected_check1)
			if selected_check1[1]!=selected_itm_Sp[1]:
				selected_itm_Sp[1]=selected_check1[1]
				count30_P=0
				count20_P=0
				count15_P=0
				print(selected_check1)	



		for rows in trade_data:
			writer.writerow(rows)
		print(max_drawdown)
		max_drawdown=0		



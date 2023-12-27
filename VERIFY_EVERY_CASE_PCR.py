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
# response = xt.interactive_login()

day=''
header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2022/7/expiry4/A'
nifty_path = './'
n_path = nifty_path + 'nifty_cash_5min.csv'
vix_path= nifty_path + 'vix.csv'

prefix="NIFTY28JUL22"
m=1
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'
max_drawdown=0
max_pcr_cpr_ratio=0

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
	SP=int(float(a[2])) - (int(float(a[2])%50)) - 500
	while int(float(a[1]))+500 > SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+50
	return sp	

def setting_prefix_suffix_for_excel_data(sp):
	filter_based_on_sp=[]
	for i in sp:
		temp=prefix+str(i)+"CE.NFO"
		temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		filter_based_on_sp.append(temp1)
	return filter_based_on_sp	

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


def setting_oi_change_data(length,filter_based_on_sp,selected_check,OI_Data,OI_Data_15min):
	df = pd.read_csv(path)	
	for i in range(length):
		"""Enter Strike price"""
		OI_Data[i][0]=Strike_Price_Set[(i)]
		OI_Data_15min[i][0]=Strike_Price_Set[(i)]
		"""Enter Call OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][1]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][1]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("4th Wrong Data")
		"""Enter Put OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][2]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][2]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("5th Wrong Data")		
		
		"""Enter Change OI Data in CE at 9:30"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:29:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1] 
			OI_Data[i][7]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][3] = extracted_data[0]['Open Interest'] - OI_Data_15min[i][1] 
			OI_Data_15min[i][7]=extracted_data[0]['Open Interest']
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("6th Wrong Data")
		"""Enter Change OI Data in PE at 09:30"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:29:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][4] = extracted_data[0]['Open Interest'] -OI_Data[i][2] 
			OI_Data[i][8]=extracted_data[0]['Open Interest']
			OI_Data_15min[i][4] = extracted_data[0]['Open Interest'] -OI_Data_15min[i][2] 
			OI_Data_15min[i][8]=extracted_data[0]['Open Interest']	
		else:
			if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
				print("7th Wrong Data")
	return OI_Data,OI_Data_15min			


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


def ratio_125_check(r,r1,r2,indx,indx_chng,s1,s2):
	cumulative=False
	ratio= abs(r1)/abs(r2)
	global max_pcr_cpr_ratio
	if ratio>=r:
		cumulative=True
		max_pcr_cpr_ratio = max(max_pcr_cpr_ratio,ratio)
	else:
		cumulative=False
		# if indx == indx_chng:
		# 	cumulative=False
		# else:
		# 	if s1/s2 >=r:
		# 		cumulative=True
		# 		print("By Change")
		# 	else:
		# 		cumulative=False
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

	# if sl>11:
	# 	if side=='PE.NFO':
	# 		selling_sp=float(a[3]) - (float(a[3])%50) -450
	# 		buying_sp=selling_sp - 100
	# 	else:
	# 		selling_sp= float(a[3])  + (50 - float(a[3])%50) + 450
	# 		buying_sp=selling_sp+100
	# elif sl<5:
	# 	if side=='PE.NFO':
	# 		selling_sp=float(a[3]) - (float(a[3])%50) -300
	# 		buying_sp=selling_sp - 100
	# 	else:
	# 		selling_sp= float(a[3])  + (50 - float(a[3])%50) + 300
	# 		buying_sp=selling_sp+100
	# sp1=prefix+str(int(selling_sp))+side
	# sp2=prefix+str(int(buying_sp))+side
	# row1,row2,sl=extract_info(sp1,sp2,time)				
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
		max_drawdown=max(max_drawdown,((close1-close2)-sl))
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

		india_vix=0
		"""vix check"""
		df1 = pd.read_csv(vix_path)
		output_format = '%d-%m-%Y'
		output_format1= '%d/%m/%Y'
		original_datetime = datetime.strptime(date,output_format)
		previous_datetime = original_datetime - timedelta(days=1)
		if previous_datetime.weekday() >= 5:
				previous_datetime = previous_datetime - timedelta(days=previous_datetime.weekday() - 4)
		previous_date = previous_datetime.date()
		previous_date_str = (previous_date.strftime(output_format))
		previous_date_str1 = (previous_date.strftime(output_format1))
		# previous_date_str1 = previous_date_str1.lstrip("0")
		day, month, year = previous_date_str1.split('/')
		day = day.lstrip('0')
		month = month.lstrip('0')
		previous_date_str2 = f"{day}/{month}/{year}"
		
		filtered_data = df1.loc[(df1['Date']== previous_date_str)][0:1]

		if len(filtered_data)==0:
			print(previous_date_str1)
			filtered_data = df1.loc[(df1['Date']== previous_date_str1)][0:1]
			if len(filtered_data)==0:
				filtered_data = df1.loc[(df1['Date']== previous_date_str2)][0:1]
				india_vix=filtered_data['India VIX C'].iloc[0]
				print(india_vix)
			else:
				india_vix=filtered_data['India VIX C'].iloc[0]
				print(india_vix)
		else:
			india_vix=filtered_data['India VIX C'].iloc[0]
			print(india_vix)

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
		output_closing_time = output_date + " 093000"
		selected_strike_price,p = setting_strike_price(output_closing_time,[],0,3)
		print(selected_strike_price)

		"""setting one more imp sp in case of gap up and down"""
		extra_sp_ce=0
		extra_sp_pe=0
		output_closing_time = output_date + " 092000"
		# a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		a1=getting_nifty_data_from_excel(date,0,1)
		gap=gap_up_down_check(date,a1)
		if gap=="UP":
			extra_sp_ce=selected_strike_price[0]-100
			print(extra_sp_ce)
		elif gap=="DOWN":
			extra_sp_pe=selected_strike_price[int(len(selected_strike_price)/2)]+100
			print(extra_sp_pe)	

		"""Setting OI Data till 9:30 , Strike Price , Previous day OI IN Call and Put , 9:30 Clock OI of Call and Put"""
		length=int(len(Strike_Price_Set))
		OI_Data = [[0] * 9 for _ in range(length)]
		OI_Data_15min=[[0] * 9 for _ in range(length)]
		OI_Data,OI_Data_15min = setting_oi_change_data(length,filter_based_on_sp,selected_strike_price,OI_Data,OI_Data_15min)	
		# for rows in OI_Data:
		# 		print(rows)
		# print("--------------------------------------------------------------------------------")
		B=np.array(OI_Data)
		first=True
		first1=True
		first2=True
		first3=True	
		trade=False
		crossover_by_pe=False
		crossover_by_ce=False
		crossover_by_pe_extra=False
		crossover_by_ce_extra=False
		time_str = '09:30:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		time_of_crossover_ce=''
		time_of_crossover_pe=''
		time_of_crossover_ce_extra=''
		time_of_crossover_pe_extra=''
		Cumulative_for_PE=False
		Cumulative_for_CE=False
		count=0
		count1=0
		trade=False
		trade_data=[]
		sl=0
		trade_side=''
		reversal_count=0
		reversal_count1_time=''
		reversal_point_initiated=False
		reversal_point_initiated_time=''
		square_off=False
		retrade=''
		set_oi_put=0
		set_oi_call=0
		set_oi_put_extra=0
		set_oi_call_extra=0
		n=3
		crossover_n_ce=0
		crossover_n_pe=0
		crossover_n_ce_extra=0
		crossover_n_pe_extra=0
		minute_check=0
		cross_by_pe_high=0
		cross_by_ce_low=20000
		cross_by_pe_high_extra=0
		cross_by_ce_low_extra=20000
		indx_ce_extra=0
		indx_pe_extra=0

		while time_obj.time() < datetime.strptime('14:55:59', '%H:%M:%S').time():
			print(time_obj.strftime('%H:%M:%S'))

			"""Data Update on 1min basis"""
			OI_Data=update_oi_data(length,filter_based_on_sp,selected_strike_price,OI_Data,time_obj.time())

			"""Setting Data of Selected strike price for data collection"""
			max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe= set_data_for_max_oi(OI_Data,selected_strike_price,india_vix)
			
			"""Setting data based on Change in OI """
			max_oi_call_chng,last_day_call_oi_chng,indx_ce_chng,max_oi_put_chng,last_day_put_oi_chng,indx_pe_chng= set_data_for_max_change_in_oi(OI_Data,selected_strike_price)

			
			# if indx_ce_extra==0:
			# 	indx_ce_extra=indx_ce
			# elif indx_ce_extra[0]-2 == indx_ce[0]:
			# 	print(indx_ce)
			# 	indx_ce_extra=indx_ce
			# 	time_of_crossover_ce=time_of_crossover_ce_extra
			# 	crossover_n_ce=crossover_n_ce_extra
			# 	set_oi_put=set_oi_put_extra
			# 	print(set_oi_put)
				
			# if indx_pe_extra==0:
			# 	indx_pe_extra=indx_pe
			# elif indx_pe_extra[0]+2 == indx_pe[0]:
			# 	indx_pe_extra=indx_pe
			# 	time_of_crossover_pe=time_of_crossover_pe_extra
			# 	crossover_n_pe=crossover_n_pe_extra	
			# 	set_oi_call=set_oi_call_extra
			# 	print(set_oi_call)
			

			"""Setiing crossover condition """			
			if last_day_call_oi > last_day_put_oi:
				if max_oi_put > max_oi_call:					
					if first:
						print("crossover_by_pe")
						crossover_by_pe=True
						crossover_by_ce=False
						count=0
						a1=getting_nifty_data_from_excel(date,crossover_n_pe,n+1)
						if a1[3] > cross_by_pe_high:
							time_of_crossover_pe=time_obj
							crossover_n_pe=n
						set_oi_call=0
						first=False	
						first1=True			
				elif crossover_by_pe:
					print("Again Crossover by call")
					a1=getting_nifty_data_from_excel(date,crossover_n_ce,n+1)
					if a1[3] < cross_by_ce_low:
						time_of_crossover_ce=time_obj
						crossover_n_ce=n
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
						a1=getting_nifty_data_from_excel(date,crossover_n_ce,n+1)
						if a1[3] < cross_by_ce_low:
							time_of_crossover_ce=time_obj
							crossover_n_ce=n
						first1=False
						first=True
				elif crossover_by_ce:
					print("Again Crossover by Put")
					crossover_by_pe=True
					crossover_by_ce=False
					count=0
					a1=getting_nifty_data_from_excel(date,crossover_n_pe,n+1)
					if a1[3] > cross_by_pe_high:
						time_of_crossover_pe=time_obj
						crossover_n_pe=n
					set_oi_call=0
					first1=True

			"""pcr and cpr ratio 125%"""
			if crossover_by_pe and trade==False:
				Cumulative_for_PE,ratio = ratio_125_check(1.2,max_oi_put,max_oi_call,indx_ce,indx_ce_chng,max_oi_put_chng,max_oi_call_chng)
				# print(ratio)
				if Cumulative_for_PE:
					print("PCR Ratio")
			if crossover_by_ce and trade==False:
				Cumulative_for_CE,ratio = ratio_125_check(1.2,max_oi_call,max_oi_put,indx_pe,indx_pe_chng,max_oi_call_chng,max_oi_put_chng)
				# print(ratio)
				if Cumulative_for_CE:
					print("CPR Ratio")	
			
			"""Reduction and Trade Point Setup"""
			if ( crossover_by_ce and extra_sp_pe==0):
				if time_of_crossover_ce==time_obj:
					set_oi_put=OI_Data[indx_pe[0]][8]
					print(set_oi_put)
				else:
					set_oi_put=max(set_oi_put,OI_Data[indx_pe[0]][8])
					if (set_oi_put * 0.95) > OI_Data[indx_pe[0]][8]:
						print("Put Reduces")
						if count==0 and crossover_n_ce!=n:
							# a=nifty_data_after_format_change(time_of_crossover,time_obj)
							a1=getting_nifty_data_from_excel(date,crossover_n_ce,n)
							if a1==['']:
								print("Ignore once")
							else:	
								trade_point=float(a1[2])
								print(trade_point - 10)
								count=count+1
			elif (crossover_by_ce  and extra_sp_pe!=0):
				row_info=np.where(B[:,0]==extra_sp_pe)[0].tolist()
				if time_of_crossover_ce==time_obj:
					set_oi_put=OI_Data[row_info[0]][8]
					print(set_oi_put)
				else:
					set_oi_put=max(set_oi_put,OI_Data[row_info[0]][8])
					if (set_oi_put * 0.95) > OI_Data[row_info[0]][8]:
						print("Put Reduces")
						if count==0 and crossover_n_ce!=n:
							# a=nifty_data_after_format_change(time_of_crossover,time_obj)
							a1=getting_nifty_data_from_excel(date,crossover_n_ce,n)
							if a1==['']:
								print("Ignore once")
							else:	
								trade_point=float(a1[2])
								print(trade_point - 10)
								count=count+1
												
			if ( crossover_by_pe  and extra_sp_ce==0):
				if time_of_crossover_pe==time_obj:
					set_oi_call=OI_Data[indx_ce[0]][7]
					print(set_oi_call)
				else:
					set_oi_call=max(set_oi_call,OI_Data[indx_ce[0]][7])
					if (set_oi_call * 0.95) > OI_Data[indx_ce[0]][7]:
						print("Call Reduces")
						if count1==0 and crossover_n_pe!=n:
							# a=nifty_data_after_format_change(time_of_crossover,time_obj)
							a1=getting_nifty_data_from_excel(date,crossover_n_pe,n)
							if a1==['']:
								print("Ignore Once")
							else:	
								trade_point=float(a1[1])
								print(trade_point + 10)
								count1=count1+1
			elif(crossover_by_pe and extra_sp_ce !=0):
				row_info=np.where(B[:,0]==extra_sp_ce)[0].tolist()
				if time_of_crossover_pe==time_obj:
					set_oi_call=OI_Data[row_info[0]][7]
					print(set_oi_call)
				else:
					set_oi_call=max(set_oi_call,OI_Data[row_info[0]][7])
					if (set_oi_call * 0.95) > OI_Data[row_info[0]][7]:
						print("Call Reduces")
						if count1==0 and crossover_n_pe!=n:

							# a=nifty_data_after_format_change(time_of_crossover,time_obj)
							a1=getting_nifty_data_from_excel(date,crossover_n_pe,n)
							if a1==['']:
								print("Ignore Once")
							else:	
								trade_point=float(a1[1])
								print(trade_point + 10)
								count1=count1+1
									
			
			"""Trade Initiation"""

			if (Cumulative_for_PE and crossover_by_pe and ratio<=1.30) and count1==1 and trade==False:
				if time_obj < (time_of_crossover_pe +  timedelta(minutes=90)):
					print("Take a Trade if Price Point goes above " + str(trade_point+10))
					# time_int2=time_obj + timedelta(minutes=2)
					# a=nifty_data_after_format_change(time_of_crossover,time_int2)
					a1=getting_nifty_data_from_excel(date,crossover_n_pe,n)
					if a1==['']:
						print("Ignore Once")
					else:	
						if (trade_point + 10) < float(a1[3]):
							print("PE Bech Do")
							row1,row2,sl=trade_initiate(output_date,a1,'PE.NFO',time_obj.time())
							trade=True
							trade_side='PUT'
							trade_data.append(row1)
							trade_data.append(row2)
							print("Difference : " + str(sl))

				else:
					print("Trade Got Delayed")

			if (Cumulative_for_CE and crossover_by_ce and ratio<=1.30) and count==1 and trade==False:
				if time_obj < ( time_of_crossover_ce +  timedelta(minutes=90)):
					print("Take a Trade if Price Point goes below " + str(trade_point-10))
					# time_int2=time_obj + timedelta(minutes=2)
					# a=nifty_data_after_format_change(time_of_crossover,time_int2)
					a1=getting_nifty_data_from_excel(date,crossover_n_ce,n)
					if a1==['']:
						print("Ignore once in a while")
					else:	
						if (trade_point - 10) > float(a1[3]):
							print("CE Bech Do")
							row1,row2,sl=trade_initiate(output_date,a1,'CE.NFO',time_obj.time())
							trade=True
							trade_side='CALL'
							trade_data.append(row1)
							trade_data.append(row2)
							print("Difference : " + str(sl))
				else:
					print("Trade Got Delayed")

			"""Stop Loss Check """
			if trade:
				sl_check(str(time_obj.time()),trade_data,sl)

			if trade and square_off==False:
				if trade_side=='PUT':
					reversal_point_initiated,ratio=ratio_125_check(1.8,max_oi_put,max_oi_call,indx_ce,indx_ce_chng,1,1)
					if (reversal_point_initiated and ratio>1.8) and square_off==False:
						time_int2=time_obj - timedelta(minutes=5)
						# a=nifty_data_after_format_change(time_int2,time_obj)
						a1=getting_nifty_data_from_excel(date,n,n+1)
						print("Square of position below :" + str((float(a1[2]))-10))
						trade_point=float(a1[2])
						reversal_point_initiated_time=time_obj
						square_off=True

				elif trade_side=='CALL':
					reversal_point_initiated,ratio=ratio_125_check(1.8,max_oi_call,max_oi_put,indx_pe,indx_pe_chng,1,1)
					if (reversal_point_initiated and ratio>1.8) and square_off==False:
						time_int2=time_obj - timedelta(minutes=5)
						# a=nifty_data_after_format_change(time_int2,time_obj)
						a1=getting_nifty_data_from_excel(date,n,n+1)
						print("Square off Position above :" + str((float(a1[1]))+10))
						trade_point=float(a1[1])
						reversal_point_initiated_time=time_obj
						square_off=True	
			
			if square_off:
				if trade_side=='PUT':
					df = pd.read_csv(path)
					if time_obj < (reversal_point_initiated_time + timedelta(minutes=30)):
						time_int2=time_obj - timedelta(minutes=2)
						# a=nifty_data_after_format_change(time_int2,time_obj)
						a1=getting_nifty_data_from_excel(date,n,n+1)
						print("Square Off Trade if Price Point goes below " + str(trade_point-10))
						if a1==['']:
							print("Ignore Once")
						else:	
							if trade_point-10 > float(a1[2]):
								for rows in trade_data[-2:]:
									print(rows)
									rows[3]=str(time_obj.time())
									filtered_data  = df.loc[(df['Ticker']== rows[1] ) & (df['Time'] == str(time_obj.time()))]
									extracted = filtered_data.to_dict('records')
									rows[6]=extracted[0]['Close']
									print(rows)
								reversal_point_initiated=''
								square_off=False
								trade_side=''

					else:
						print("Resetup reversal")
						reversal_point_initiated_time=''
						square_off=False
				elif trade_side=='CALL':
					df = pd.read_csv(path)
					if time_obj < (reversal_point_initiated_time + timedelta(minutes=30)):
						time_int2=time_obj - timedelta(minutes=2)
						# a=nifty_data_after_format_change(time_int2,time_obj)
						a1=getting_nifty_data_from_excel(date,n,n+1)
						print("Square Off Trade if Price Point goes below " + str(trade_point+10))
						if a1==['']:
							print("Ignore Once")
						else:	
							if trade_point+10 < float(a1[1]):
								for rows in trade_data[-2:]:
									print(rows)
									rows[3]=str(time_obj.time())
									filtered_data  = df.loc[(df['Ticker']== rows[1] ) & (df['Time'] == str(time_obj.time()))]
									extracted = filtered_data.to_dict('records')
									rows[6]=extracted[0]['Close']
									print(rows)
								reversal_point_initiated=''
								square_off=False
								trade_side=''

					else:
						print("Resetup reversal")
						reversal_point_initiated_time=''
						square_off=False
						

			if minute_check==4:
				n=n+1
				minute_check=0
			else:
				minute_check=minute_check+1

			"""Shifting Of Selected Strike Price"""
			time_int = int(str(time_obj.time()).replace(':', ''))
			formatted_num = '{:06d}'.format(time_int)
			output_closing_time=output_date + " "+str(formatted_num)
			selected_check1=shifting_strike_price(output_closing_time,selected_strike_price,0,n,p)
			if selected_check1!=selected_strike_price:
				selected_strike_price=selected_check1
				print(selected_check1)

			time_obj += timedelta(minutes=m)

			# if crossover_by_pe:
			# 	if crossover_n_pe!=n:
			# 		a1=getting_nifty_data_from_excel(date,crossover_n_pe,n)
			# 		if a1[2] > cross_by_pe_high:	
			# 			cross_by_pe_high=a1[2]
					
			# 		extra_sp=(OI_Data[indx_pe[0]][0]+100)
			# 		if india_vix>21.5:
			# 			if(True if float((OI_Data[indx_pe[0]][0]+100)) in selected_strike_price[5:11] else False):
			# 				# print("Yes Higher Sp Available")
			# 				extra_sp_oi,extra_Sp_last_day_oi =  extra_sp_data_save(OI_Data,extra_sp,"PE")
			# 				"""Setiing crossover condition for another  """			
			# 				if last_day_call_oi > extra_Sp_last_day_oi:
			# 					if extra_sp_oi > max_oi_call:					
			# 						if first2:
			# 							print("crossover_by_pe_extra")
			# 							crossover_by_pe_extra=True
			# 							crossover_by_ce_extra=False
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 							if a1[3] > cross_by_pe_high_extra:
			# 								time_of_crossover_pe_extra=time_obj
			# 								crossover_n_pe_extra=n
			# 							set_oi_call_extra=OI_Data[indx_ce[0]][7]
			# 							first2=False	
			# 							first3=True			
			# 					elif crossover_by_pe_extra:
			# 						print("Again Crossover by call_extra")
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 						if a1[3] < cross_by_ce_low_extra:
			# 							time_of_crossover_ce_extra=time_obj
			# 							crossover_n_ce_extra=n
			# 						set_oi_put_extra=0
			# 						crossover_by_ce_extra=True
			# 						crossover_by_pe_extra=False
			# 						first2=True				
			# 				else:
			# 					if max_oi_call > extra_sp_oi:
			# 						if first1:
			# 							print("crossover_by_ce_extra")
			# 							crossover_by_ce_extra=True
			# 							crossover_by_pe_extra=False
			# 							set_oi_put_extra=0
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 							if a1[3] < cross_by_ce_low_extra:
			# 								time_of_crossover_ce_extra=time_obj
			# 								crossover_n_ce_extra=n
			# 							first3=False
			# 							first2=True
			# 					elif crossover_by_ce_extra:
			# 						print("Again Crossover by Put_ extra")
			# 						crossover_by_pe_extra=True
			# 						crossover_by_ce_extra=False
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 						if a1[3] > cross_by_pe_high_extra:
			# 							time_of_crossover_pe_extra=time_obj
			# 							crossover_n_pe_extra=n
			# 						set_oi_call_extra=OI_Data[indx_ce[0]][7]
			# 						first3=True
			# 		else:
			# 			if(True if float((OI_Data[indx_pe[0]][0]+100)) in selected_strike_price[3:6] else False):
			# 				# print("Yes Higher Sp Available")
			# 				extra_sp_oi,extra_Sp_last_day_oi =  extra_sp_data_save(OI_Data,extra_sp,"PE")
			# 				"""Setiing crossover condition for another  """			
			# 				if last_day_call_oi > extra_Sp_last_day_oi:
			# 					if extra_sp_oi > max_oi_call:					
			# 						if first2:
			# 							print("crossover_by_pe_extra")
			# 							crossover_by_pe_extra=True
			# 							crossover_by_ce_extra=False
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 							if a1[3] > cross_by_pe_high_extra:
			# 								time_of_crossover_pe_extra=time_obj
			# 								crossover_n_pe_extra=n
			# 							set_oi_call_extra=OI_Data[indx_ce[0]][7]
			# 							first2=False	
			# 							first3=True			
			# 					elif crossover_by_pe_extra:
			# 						print("Again Crossover by call_extra")
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 						if a1[3] < cross_by_ce_low_extra:
			# 							time_of_crossover_ce_extra=time_obj
			# 							crossover_n_ce_extra=n
			# 						set_oi_put_extra=0
			# 						crossover_by_ce_extra=True
			# 						crossover_by_pe_extra=False
			# 						first2=True				
			# 				else:
			# 					if max_oi_call > extra_sp_oi:
			# 						if first1:
			# 							print("crossover_by_ce_extra")
			# 							crossover_by_ce_extra=True
			# 							crossover_by_pe_extra=False
			# 							set_oi_put_extra=0
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 							if a1[3] < cross_by_ce_low_extra:
			# 								time_of_crossover_ce_extra=time_obj
			# 								crossover_n_ce_extra=n
			# 							first3=False
			# 							first2=True
			# 					elif crossover_by_ce_extra:
			# 						print("Again Crossover by Put_ extra")
			# 						crossover_by_pe_extra=True
			# 						crossover_by_ce_extra=False
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 						if a1[3] > cross_by_pe_high_extra:
			# 							time_of_crossover_pe_extra=time_obj
			# 							crossover_n_pe_extra=n
			# 						set_oi_call_extra=OI_Data[indx_ce[0]][7]
			# 						first3=True				


						
			# if crossover_by_ce:
			# 	if crossover_n_ce!=n:
			# 		a1=getting_nifty_data_from_excel(date,crossover_n_ce,n)
			# 		if a1[3]  < cross_by_ce_low:
			# 			cross_by_ce_low=a1[3]
			# 		extra_sp=(OI_Data[indx_ce[0]][0]-100)
			# 		if india_vix>21.5:
			# 			if(True if float((OI_Data[indx_ce[0]][0]-100)) in selected_strike_price[0:5] else False):
			# 				# print("Yes Lower Sp Available")	
			# 				extra_sp_oi,extra_Sp_last_day_oi = extra_sp_data_save(OI_Data,extra_sp,"CE")
			# 				"""Setiing crossover condition """			
			# 				if extra_Sp_last_day_oi > last_day_put_oi:
			# 					if max_oi_put > extra_sp_oi:					
			# 						if first2:
			# 							print("crossover_by_pe_extra")
			# 							crossover_by_pe_extra=True
			# 							crossover_by_ce_extra=False
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 							if a1[3] > cross_by_pe_high_extra:
			# 								time_of_crossover_pe_extra=time_obj
			# 								crossover_n_pe_extra=n
			# 							set_oi_call_extra=0
			# 							first2=False	
			# 							first3=True			
			# 					elif crossover_by_pe_extra:
			# 						print("Again Crossover by call _ extra")
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 						if a1[3] < cross_by_ce_low_extra:
			# 							time_of_crossover_ce_extra=time_obj
			# 							crossover_n_ce_extra=n
			# 						set_oi_put_extra=OI_Data[indx_pe[0]][8]
			# 						crossover_by_ce_extra=True
			# 						crossover_by_pe_extra=False
			# 						first2=True				
			# 				else:
			# 					if extra_sp_oi > max_oi_put:
			# 						if first3:
			# 							print("crossover_by_ce_extra")
			# 							crossover_by_ce_extra=True
			# 							crossover_by_pe_extra=False
			# 							set_oi_put_extra=OI_Data[indx_pe[0]][8]
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 							if a1[3] < cross_by_ce_low_extra:
			# 								time_of_crossover_ce_extra=time_obj
			# 								crossover_n_ce_extra=n
			# 							first3=False
			# 							first2=True
			# 					elif crossover_by_ce_extra:
			# 						print("Again Crossover by Put extra")
			# 						crossover_by_pe_extra=True
			# 						crossover_by_ce_extra=False
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 						if a1[3] > cross_by_pe_high_extra:
			# 							time_of_crossover_pe_extra=time_obj
			# 							crossover_n_pe_extra=n
			# 						set_oi_call_extra=0
			# 						first3=True
			# 		else:
			# 			if(True if float((OI_Data[indx_ce[0]][0]-100)) in selected_strike_price[0:3] else False):
			# 				# print("Yes Lower Sp Available")	
			# 				extra_sp_oi,extra_Sp_last_day_oi = extra_sp_data_save(OI_Data,extra_sp,"CE")
			# 				"""Setiing crossover condition """			
			# 				if extra_Sp_last_day_oi > last_day_put_oi:
			# 					if max_oi_put > extra_sp_oi:					
			# 						if first2:
			# 							print("crossover_by_pe_extra")
			# 							crossover_by_pe_extra=True
			# 							crossover_by_ce_extra=False
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 							if a1[3] > cross_by_pe_high_extra:
			# 								time_of_crossover_pe_extra=time_obj
			# 								crossover_n_pe_extra=n
			# 							set_oi_call_extra=0
			# 							first2=False	
			# 							first3=True			
			# 					elif crossover_by_pe_extra:
			# 						print("Again Crossover by call _ extra")
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 						if a1[3] < cross_by_ce_low_extra:
			# 							time_of_crossover_ce_extra=time_obj
			# 							crossover_n_ce_extra=n
			# 						set_oi_put_extra=OI_Data[indx_pe[0]][8]
			# 						crossover_by_ce_extra=True
			# 						crossover_by_pe_extra=False
			# 						first2=True				
			# 				else:
			# 					if extra_sp_oi > max_oi_put:
			# 						if first3:
			# 							print("crossover_by_ce_extra")
			# 							crossover_by_ce_extra=True
			# 							crossover_by_pe_extra=False
			# 							set_oi_put_extra=OI_Data[indx_pe[0]][8]
			# 							a1=getting_nifty_data_from_excel(date,crossover_n_ce_extra,n+1)
			# 							if a1[3] < cross_by_ce_low_extra:
			# 								time_of_crossover_ce_extra=time_obj
			# 								crossover_n_ce_extra=n
			# 							first3=False
			# 							first2=True
			# 					elif crossover_by_ce_extra:
			# 						print("Again Crossover by Put extra")
			# 						crossover_by_pe_extra=True
			# 						crossover_by_ce_extra=False
			# 						a1=getting_nifty_data_from_excel(date,crossover_n_pe_extra,n+1)
			# 						if a1[3] > cross_by_pe_high_extra:
			# 							time_of_crossover_pe_extra=time_obj
			# 							crossover_n_pe_extra=n
			# 						set_oi_call_extra=0
			# 						first3=True				


		for rows in trade_data:
			writer.writerow(rows)
		print(max_drawdown)
		print(max_pcr_cpr_ratio)
		max_drawdown=0
		max_pcr_cpr_ratio=0
		



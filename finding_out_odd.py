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
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/3_7/ex-date/A/A1'
nifty_path = './Nirmal_Fincap/Nifty/2022/'
n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

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
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
		a=response['result']['dataReponse'].split('|')
		if a==['']:
			return a
		else:
			return a	
	else:
		return a


def getting_nifty_data_from_excel(date,m,n,ret=False):
	a1=[]
	df1 = pd.read_csv(n_path)

	original_format = '%b %d %Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%Y%m%d'
	date=date_object.strftime(output_format)
	filtered_data = df1.loc[(df1['Date']== int(date))][m:n]
	F=np.array(filtered_data)
	a1.append(date)
	a1.append(filtered_data['Open'].iloc[0])
	a1.append(filtered_data['High'].max())
	candle_info_high=np.where(F[:,4]==a1[1])[0].tolist()
	a1.append(filtered_data['Low'].min())
	candle_info_low=np.where(F[:,5]==a1[2])[0].tolist()
	a1.append(filtered_data['Close'].iloc[-1])
	# print(candle_info_high[0])
	# print(candle_info_low[0])
	if ret:
		return a1,(n-m)-candle_info_high[0],(n-m)-candle_info_low[0]
	else:	
		return a1


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
	# a=getting_nifty_data_from_excel(date,m,n)
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
			if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
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
			if (True if float(filter_based_on_sp[i+5][12:17]) in selected_check else False):
				print("5th Wrong Data")		
		
	return OI_Data	

def update_oi_data(length,filter_based_on_sp,selected_check,OI_Data,time):
	df = pd.read_csv(path)
	for i in range(int(length/2)):
		"""Enter Change OI Data in CE"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if extracted_data==[]:
			t=str(time)
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i] ) & (df['Time'] == str(t[1:]))]
			extracted_data = filtered_data.to_dict('records')

		if(extracted_data != []):
			# OI_Data[i][19]=OI_Data[i][17] #8tick
			# OI_Data[i][17]=OI_Data[i][15] #7tick
			# OI_Data[i][15]=OI_Data[i][13] #6tick
			# OI_Data[i][13]=OI_Data[i][11] #5tick
			# OI_Data[i][11]=OI_Data[i][9] #4tick
			# OI_Data[i][9]=OI_Data[i][7]	#3tick
			# OI_Data[i][7]=OI_Data[i][5] # 2tick
			OI_Data[i][5]=OI_Data[i][3] # 1tick
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1] #0 tick current
			OI_Data[i][21]=extracted_data[0]['Open Interest']
			OI_Data[i][19]=max(OI_Data[i][19],OI_Data[i][21])
		else:
			if (True if float(filter_based_on_sp[i][12:17]) in selected_check else False):
				print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+9] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if extracted_data==[]:
			t=str(time)
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i+9] ) & (df['Time'] == t[1:] )]
			extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			# OI_Data[i][20]=OI_Data[i][18]
			# OI_Data[i][18]=OI_Data[i][16]
			# OI_Data[i][16]=OI_Data[i][14]
			# OI_Data[i][14]=OI_Data[i][12]
			# OI_Data[i][12]=OI_Data[i][10]
			# OI_Data[i][10]=OI_Data[i][8]
			# OI_Data[i][8]=OI_Data[i][6]
			OI_Data[i][6]=OI_Data[i][4]
			OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
			OI_Data[i][22] = extracted_data[0]['Open Interest']
			OI_Data[i][20]=max(OI_Data[i][20],OI_Data[i][22])
		else:
			if (True if float(filter_based_on_sp[i+9][12:17]) in selected_check else False):
				print("9th Wrong Data")				    
	return OI_Data

def best_Cumulative_Change(matrix):
	i=0
	max_index_call=0
	max_index_chng_call=0
	max_index_put=1
	max_index_chng_put=1

	max_oi_call=-100000000000000 
	max_oi_chng_call=-100000000000000
	max_oi_put=-100000000000000 
	max_oi_chng_put=-100000000000000
	
	for row in matrix:
		if max_oi_chng_call < row[3]:
			max_oi_chng_call=row[3]
			max_index_chng_call=i 
			
		if max_oi_call<row[21]:
			max_oi_call=row[21]
			max_index_call=i
			i=i+1
		else:
			i=i+1

		if max_oi_chng_put < row[4]:
			max_oi_chng_put=row[4]
			max_index_chng_put=i 
			
		if max_oi_put<row[22]:
			max_oi_put=row[22]
			max_index_put=i
			i=i+1
		else:
			i=i+1		
					

	
	return max_index_call,max_index_chng_call,max_index_put,max_index_chng_put

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
		prefix= "NIFTY" + formatted_date
		"""Setting the date Format to extract data for that Particular Date"""
		output_date=change_date_format(date)


		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
			

		"""Setting Strike Price For Day for 2:45 self"""
		output_opening_time = output_date+ " 090000"
		output_closing_time = output_date + " 093000"
		selected_itm_Sp = select_itm_atm_otm_strike_price(output_date,[],0,46)
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(selected_itm_Sp)

		length=int(len(selected_itm_Sp))

		OI_Data = [[0] * 23 for _ in range(int(length/2))]
		OI_Data_inner = [[0] * 9 for _ in range(int(length/2))]
		selected_itm_Sp_inner=[]
		filter_based_on_sp_inner=[]
		OI_Data = setting_oi_change_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data)	
		# print(OI_Data)

		time_str = '09:30:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')	

		output_closing_time = output_date + " 091800"
		a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		nifty_record=float(a[4])
		max_nifty = float(a[2])
		min_nifty = float(a[3])


		print("Nifty Record- " + str(nifty_record))

		while time_obj.time() < datetime.strptime('15:00:59', '%H:%M:%S').time():
			OI_Data=update_oi_data(length,filter_based_on_sp,selected_itm_Sp,OI_Data,time_obj.time())
			
			print(time_obj.time())
			time_obj1=time_obj - timedelta(minutes=2)
			time_str2= time_obj1.time().strftime("%H%M%S")
			output_opening_time = output_date+" "+time_str2  
			time_str3= time_obj.time().strftime("%H%M%S")
			output_closing_time = output_date +" "+time_str3
			a=getting_ohlc_nifty(output_opening_time,output_closing_time)

			max_nifty= max(max_nifty,float(a[2]))
			min_nifty= min(min_nifty,float(a[3]))
				


			call_cumulative,call_change,put_cumulative,put_chnage=best_Cumulative_Change(OI_Data)

			

			if float(a[2]) - min_nifty >=40:
				print("50 points Up move")
				print(max_nifty)

				if OI_Data[int(call_cumulative/2)][0] - float(a[4]) <= 20:
					if OI_Data[int(call_cumulative/2)][19]*0.9 < OI_Data[int(call_cumulative/2)][21]:
						print("----------------Odd CE---------------------")
						print("Cumulative Best Call - "+ str(OI_Data[int(call_cumulative/2)][0]))


				if OI_Data[int(call_change/2)][0] - float(a[4]) <=20:
					if OI_Data[int(call_change/2)][19]*0.9 < OI_Data[int(call_change/2)][21]:
						print("----------------Odd CE---------------------")
						print("Change Best Call - "+ str(OI_Data[int(call_change/2)][0]))
		



			elif max_nifty - float(a[3]) >=40:
				print("50 point Down move")
				print(min_nifty)

				if OI_Data[int(put_cumulative/2)][0] - float(a[4]) >= -20:
					if OI_Data[int(put_cumulative/2)][20]*0.9 < OI_Data[int(put_cumulative/2)][22]:
						print("----------------Odd PE---------------------")
						print("Cumulative Best Put - "+ str(OI_Data[int(put_cumulative/2)][0]))


				if  OI_Data[int(put_chnage/2)][0] - float(a[4]) >= -20:
					if OI_Data[int(put_chnage/2)][20]*0.9 < OI_Data[int(put_chnage/2)][22]:
						print("----------------Odd PE---------------------")
						print("Change Best Put- "+ str(OI_Data[int(put_chnage/2)][0]))

				
			print(max_nifty)
			print(min_nifty)
			time_obj += timedelta(minutes=m)

			
				


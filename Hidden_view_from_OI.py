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
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/3_7/ex-date'
nifty_path = './Nirmal_Fincap/Nifty/2022/'
n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

prefix=" "
m=1
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'


# def date_from_file_name(i):
# 	return i[17:25]

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


def getting_filtered_data_from_excel(date,m,n):
	df1 = pd.read_csv(n_path)
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%Y%m%d'
	date=date_object.strftime(output_format)
	filtered_data = df1.loc[(df1['Date']== int(date))][m:n]
	filtered_data=filtered_data.iloc[::3]
	return filtered_data


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
		return a
	else:
		return a


def getting_nifty_data_from_excel(date,m,n,ret=False):
	a1=[]
	df1 = pd.read_csv(n_path)
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%Y%m%d'
	date=date_object.strftime(output_format)
	filtered_data = df1.loc[(df1['Date']== int(date))][m:n]
	F=np.array(filtered_data)
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
	for i in sp:
		temp=prefix+str(i)+"CE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1)
	for i in sp:
		temp=prefix+str(i)+"PE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1) 	
	return filter_based_on_sp

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[3])) - (int(float(a[3])%100)) - 300
	while int(float(a[2]))+300 > SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+50
	return sp


def setting_oi_change_data(length,filter_based_on_sp,OI_Data):
	df = pd.read_csv(path)	
	for i in range(length):
		"""Enter Strike price"""
		OI_Data[i][0]=Strike_Price_Set[(i)]
		
		"""Enter Call OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][1]=extracted_data[0]['Open Interest']
		else:
			print("4th Wrong Data")
		"""Enter Put OI Data"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:15:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][2]=extracted_data[0]['Open Interest']

		else:
			print("5th Wrong Data")		
		
		"""Enter Change OI Data in CE at 10:00"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:59:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1] 
			OI_Data[i][7]=extracted_data[0]['Open Interest']
		else:
			print("6th Wrong Data")

		"""Enter Change OI Data in PE at 09:30"""
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:59:59')]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][4] = extracted_data[0]['Open Interest'] -OI_Data[i][2] 
			OI_Data[i][8]=extracted_data[0]['Open Interest']	
		else:
			print("7th Wrong Data")
	return OI_Data			


def update_oi_data(length,filter_based_on_sp,OI_Data,time):
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
			print("8th Wrong Data")	
		"""Enter Change OI Data in PE """
		filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == str(time))]
		extracted_data = filtered_data.to_dict('records')
		if(extracted_data != []):
			OI_Data[i][6]=OI_Data[i][4]
			OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
			OI_Data[i][8] = extracted_data[0]['Open Interest']
		else:
			print("9th Wrong Data")				    
	return OI_Data	

def getting_small_table_near_spot_price(OI_Data,cl_price):
	start = cl_price - (cl_price%50) -100
	strike_price=[]
	for i in range(6):
		strike_price.append(start)
		start=start+50
	

	selected_data = [row for row in OI_Data if row[0] in strike_price]

	return selected_data

def selection_of_best_suitable_call_sp(A,closing_price):
	cumulative_sp=''
	change_oi_sp=''

	max_oi=0
	max_oi_indx=0
	max_oi_chng=0
	max_oi_indx_chng=0

	for row_idx, row in enumerate(A):

		if row[7]>max_oi:
			max_oi=row[7]
			max_oi_indx=row_idx

		if row[3]>max_oi_chng:	
			max_oi_chng=row[3]
			max_oi_indx_chng=row_idx
	cumulative_sp=A[max_oi_indx][0]
	change_oi_sp=A[max_oi_indx_chng][0]		

	if closing_price- cumulative_sp < closing_price - change_oi_sp:
		return max_oi_indx
	else:
		return max_oi_indx_chng

def selection_of_best_suitable_put_sp(A,closing_price):
	cumulative_sp=''

	max_oi=0
	max_oi_indx=0

	for row_idx, row in enumerate(A):

		if row[7]>max_oi:
			max_oi=row[7]
			max_oi_indx=row_idx

	cumulative_sp=A[max_oi_indx][0]
	return max_oi_indx

			
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

		
		"""Get the Nifty Range of the Day for Setting Strike Price and Data filteration for the day"""	
		output_opening_time = output_date+ " 090000"
		output_closing_time = output_date + " 153000"
		
		a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		
		Strike_Price_Set=strike_price_for_data(a)
		
		
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(Strike_Price_Set)
		length=int(len(Strike_Price_Set))
		OI_Data = [[0] * 9 for _ in range(length)]

		OI_Data= setting_oi_change_data(length,filter_based_on_sp,OI_Data)
		
		"""Setting Strike Price For Day"""
		time_str = '10:00:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		A=np.array(OI_Data)

		
		output_closing_time = output_date + " 100000"	
		a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		

		A=getting_small_table_near_spot_price(OI_Data,float(a[4]))
		print(A)
		sum_of_call=0
		sum_of_put=0
		Z=np.array(OI_Data)
		while time_obj.time() < datetime.strptime('14:55:59', '%H:%M:%S').time():
			print(time_obj.strftime('%H:%M:%S'))
			OI_Data=update_oi_data(length,filter_based_on_sp,OI_Data,time_obj.time())
			
			t1 = str(time_obj.strftime('%H%M%S'))
			output_closing_time = output_date +" "+t1	
			a=getting_ohlc_nifty(output_opening_time,output_closing_time)
			print(a)
			if a!=['']:
				A=getting_small_table_near_spot_price(OI_Data,float(a[4]))
			

			indx_no_ce=selection_of_best_suitable_call_sp(A,float(a[4]))
		
			sum_of_call=A[indx_no_ce][7]+A[indx_no_ce-1][7]
			print(sum_of_call)
			indx_no_pe=selection_of_best_suitable_put_sp(A,float(a[4]))
			
			row1=np.where(Z==A[indx_no_pe][0])[0].tolist()
			sum_of_put= OI_Data[row1[0]+1][8]+OI_Data[row1[0]][8]
			if sum_of_call - sum_of_put < 6000000:
				sum_of_put=OI_Data[row1[0]+1][8]+OI_Data[row1[0]][8]
				indx_pe_selected=OI_Data[row1[0]][0]
				print(sum_of_put)
				print(indx_pe_selected)
			else:	
				x=OI_Data[row1[0]-1][8]+OI_Data[row1[0]][8]
				if sum_of_call - x < 6000000:
					sum_of_put=x
					indx_pe_selected=OI_Data[row1[0]-1][0]
					print(sum_of_put)
					print(indx_pe_selected)
				else:	
					y=OI_Data[row1[0]-1][8]+OI_Data[row1[0]-2][8]
					if sum_of_call - y < 6000000:
						sum_of_put=y
						indx_pe_selected=OI_Data[row1[0]-2][0]
						print(sum_of_put)
						print(indx_pe_selected)
					else:
						sum_of_put=y
						indx_pe_selected=OI_Data[row1[0]-2][0]
						print(sum_of_put)
						print(indx_pe_selected)
						# z=OI_Data[row1[0]-2][8]+OI_Data[row1[0]-3][8]
						# if sum_of_call - z < 6000000:
						# 	sum_of_put=z
						# 	indx_pe_selected=OI_Data[row1[0]-3][0]
						# 	print(sum_of_put)
						# 	print(indx_pe_selected)
						# else:
							# w=OI_Data[row1[0]-4][8]+OI_Data[row1[0]-3][8]
							# if sum_of_call - w < 6000000:
							# 	sum_of_put=w
							# 	indx_pe_selected=OI_Data[row1[0]-4][0]
							# 	print(sum_of_put)
							# 	print(indx_pe_selected)
							# else:
							# 	sum_of_put=w
							# 	indx_pe_selected=OI_Data[row1[0]-4][0]
							# 	print(sum_of_put)
							# 	print(indx_pe_selected)
									
							

								

			time_obj += timedelta(minutes=m)	
		

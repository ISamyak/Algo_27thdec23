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
#tajol96062@kxgif.com

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
    	exchangeInstrumentID=26001,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		print("1st Wrong data")
		return a
	else:
		return a

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
		sp= int(float(a[4]) - float(a[4])%100)
	pass_index=prefix+str(sp)+"CE.NFO"
	pass_index1=prefix+str(sp)+"PE.NFO"


	filtered_data = df.loc[(df['Ticker']== pass_index ) & (df['Time'] == str(time_obj.time()))]
	extracted_data = filtered_data.to_dict('records')
	# print(extracted_data)
	filtered_data  = df.loc[(df['Ticker']== pass_index1 ) & (df['Time'] == str(time_obj.time()) )]
	extracted_data2 = filtered_data.to_dict('records')
	# print(extracted_data2)
	if extracted_data==[] or extracted_data2==[]:
		return 0
	synthetic = sp + extracted_data[0]['Close'] - extracted_data2[0]['Close']

	if synthetic > float(a[4]):
		print(synthetic - float(a[4]))
		return synthetic - float(a[4])
	elif float(a[4]) >= synthetic:
		print(synthetic - float(a[4]))
		return synthetic - float(a[4])	

def getting_data_for_sp_calculate_atp_ltp(date,prefix,table,table1,table_ce,table_pe):
	
	
	output_closing_time = output_date +" 091600"
	output_opening_time = output_date+ " 090000"
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	if a==['']:
		print("False data - Please check")
		return 0
	else:
		# atm=int(float(a[4])-float(a[4])%50)	
		# ce_sp=[atm+300,atm+350,atm+400,atm+450,atm+500,atm+550,atm+600,atm+650,atm+700]
		# ce_sp = [f"{prefix}{value}{'CE.NFO'}" for value in ce_sp]
		# pe_sp=[atm-300,atm-350,atm-400,atm-450,atm-500,atm-550,atm-600,atm-650,atm-700]
		# pe_sp = [f"{prefix}{value}{'PE.NFO'}" for value in pe_sp]

		atm=int(float(a[4])-float(a[4])%100)	
		ce_sp=[atm+400,atm+500,atm+600,atm+700,atm+800,atm+900,atm+1000,atm+1100,atm+1200]
		ce_sp = [f"{prefix}{value}{'CE.NFO'}" for value in ce_sp]
		pe_sp=[atm-400,atm-500,atm-600,atm-700,atm-800,atm-900,atm-1000,atm-1100,atm-1200]
		pe_sp = [f"{prefix}{value}{'PE.NFO'}" for value in pe_sp]

		ce_sp_near=[atm,atm+100,atm+200,atm+300,atm+400]
		ce_sp_near = [f"{prefix}{value}{'CE.NFO'}" for value in ce_sp_near]
		pe_sp_near=[atm,atm-100,atm-200,atm-300,atm-400]
		pe_sp_near = [f"{prefix}{value}{'PE.NFO'}" for value in pe_sp_near]
	# print(ce_sp)
	# print(pe_sp)

	df = pd.read_csv(path)

	l=0
	for j in range(len(ce_sp)):
		start_time = pd.to_datetime('9:15:59').time()

		end_time = pd.to_datetime('11:15:59').time()
		df['Time'] = pd.to_datetime(df['Time'])

		filtered_data = df.loc[(df['Ticker'] == ce_sp[j]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]

		extracted_data = filtered_data.to_dict('records')
		
		a=0
		a1=0

		table[j][0]=ce_sp[j]
		count=0
		max_time_continue=0
		start_time=''
		ultra_count=0
		for i in range(len(extracted_data)):
			if(extracted_data != [] or extracted_data[i]['Volume'] !=0):
				if i==0:
					c=extracted_data[i]['Volume']
					a=extracted_data[i]['Volume']*extracted_data[i]['Close']
					b=a/c
					d=extracted_data[i]['Close']/b-1
				else:
					c=extracted_data[i]['Volume']+c
					a=a+extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d=(extracted_data[i]['Close']/b-1)*100
					if d>5:
						count=count+1
						ultra_count=ultra_count+1
						if max_time_continue<count:
							max_time_continue=count
							start_time=extracted_data[i]['Time']
					else:
						count=0	
			else:		
				print("8th Wrong Data")
		table[j][1]=max_time_continue
		# table[j][2]=start_time
		if max_time_continue>0:
			start_time=str(start_time)
			timestamp = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue)
			table[j][2]=str(new_timestamp)
		else:
			table[j][2]=start_time
		table[j][3]=ultra_count		
		
	for j in range(len(pe_sp)):
		start_time = pd.to_datetime('9:15:59').time()

		end_time = pd.to_datetime('11:15:59').time()
		df['Time'] = pd.to_datetime(df['Time'])

		filtered_data = df.loc[(df['Ticker'] == pe_sp[j]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]
		
		extracted_data = filtered_data.to_dict('records')
		
		a=0
		a1=0

		table1[j][0]=pe_sp[j]
		count=0
		max_time_continue=0
		start_time=''
		ultra_count=0
		for i in range(len(extracted_data)):
			
			if(extracted_data != [] and extracted_data[i]['Volume'] !=0):
				if i==0:
					c=extracted_data[i]['Volume']
					a=extracted_data[i]['Volume']*extracted_data[i]['Close']
					b=a/c
					d=extracted_data[i]['Close']/b-1
				else:
					c=extracted_data[i]['Volume']+c
					a=a+extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d=(extracted_data[i]['Close']/b-1)*100
					if d>5:
						count=count+1
						ultra_count=ultra_count+1
						if max_time_continue<count:
							max_time_continue=count
							start_time=extracted_data[i]['Time']
					else:
						count=0	
			else:		
				print("8th Wrong Data")
		table1[j][1]=max_time_continue
		# table1[j][2]=start_time
		if max_time_continue>0:
			start_time=str(start_time)
			timestamp = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue)
			table1[j][2]=str(new_timestamp)
		else:
			table1[j][2]=start_time
		table1[j][3]=ultra_count		


	for j in range(len(ce_sp_near)):
		start_time = pd.to_datetime('9:15:59').time()

		end_time = pd.to_datetime('11:15:59').time()
		df['Time'] = pd.to_datetime(df['Time'])

		filtered_data = df.loc[(df['Ticker'] == ce_sp_near[j]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]
		
		extracted_data = filtered_data.to_dict('records')
		
		a=0
		a1=0

		table_ce[j][0]=ce_sp_near[j]
		count=0
		count_alter=0
		max_time_continue=0
		max_time_continue_alter=0
		start_time=''
		start_time_alter=''
		for i in range(len(extracted_data)):
			
			if(extracted_data != [] and extracted_data[i]['Volume'] !=0):
				if i==0:
					c=extracted_data[i]['Volume']
					a=extracted_data[i]['Volume']*extracted_data[i]['Close']
					b=a/c
					d=extracted_data[i]['Close']/b-1
				else:
					c=extracted_data[i]['Volume']+c
					a=a+extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d=(extracted_data[i]['Close']/b-1)*100
					if d>5:
						count=count+1
						count_alter=0
						if max_time_continue<count:
							max_time_continue=count
							start_time=extracted_data[i]['Time']
					else:
						if d<15:
							count_alter=count_alter+1
							if max_time_continue_alter<count_alter:
								max_time_continue_alter=count_alter
								start_time_alter=extracted_data[i]['Time']
						count=0	
			else:		
				print("8th Wrong Data")
		table_ce[j][1]=max_time_continue
		# table_ce[j][2]=start_time
		if max_time_continue>0:
			start_time=str(start_time)
			timestamp = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue)
			table_ce[j][2]=str(new_timestamp)
		else:
			table_ce[j][2]=start_time
		table_ce[j][3]=max_time_continue_alter
		# table_ce[j][4]=start_time_alter
		if max_time_continue_alter>0:
			start_time_alter=str(start_time_alter)
			timestamp = datetime.strptime(start_time_alter,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue_alter)
			table_ce[j][4]=str(new_timestamp)
		else:
			table_ce[j][4]=start_time_alter	

	for j in range(len(pe_sp_near)):
		start_time = pd.to_datetime('9:15:59').time()

		end_time = pd.to_datetime('11:15:59').time()
		df['Time'] = pd.to_datetime(df['Time'])

		filtered_data = df.loc[(df['Ticker'] == pe_sp_near[j]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]
		
		extracted_data = filtered_data.to_dict('records')
		
		a=0
		a1=0

		table_pe[j][0]=pe_sp_near[j]
		count=0
		count_alter=0
		max_time_continue=0
		max_time_continue_alter=0
		start_time=''
		start_time_alter=''
		for i in range(len(extracted_data)):
			
			if(extracted_data != [] and extracted_data[i]['Volume'] !=0):
				if i==0:
					c=extracted_data[i]['Volume']
					a=extracted_data[i]['Volume']*extracted_data[i]['Close']
					b=a/c
					d=extracted_data[i]['Close']/b-1
				else:
					c=extracted_data[i]['Volume']+c
					a=a+extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d=(extracted_data[i]['Close']/b-1)*100
					if d>5:
						count=count+1
						count_alter=0
						if max_time_continue<count:
							max_time_continue=count
							start_time=extracted_data[i]['Time']
					else:
						if d<15:
							count_alter=count_alter+1
							if max_time_continue_alter<count_alter:
								max_time_continue_alter=count_alter
								start_time_alter=extracted_data[i]['Time']
						count=0	
			else:		
				print("8th Wrong Data")
		table_pe[j][1]=max_time_continue
		# table_pe[j][2]=start_time
		if max_time_continue>0:
			start_time=str(start_time)
			timestamp = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue)
			table_pe[j][2]=str(new_timestamp)
		else:
			table_pe[j][2]=start_time
		table_pe[j][3]=max_time_continue_alter
		# table_pe[j][4]=start_time_alter
		if max_time_continue_alter>0:
			start_time_alter=str(start_time_alter)
			timestamp = datetime.strptime(start_time_alter,'%Y-%m-%d %H:%M:%S')
			new_timestamp = timestamp - timedelta(minutes=max_time_continue_alter)
			table_pe[j][4]=str(new_timestamp)
		else:
			table_pe[j][4]=start_time_alter				
		
	return table,table1,table_ce,table_pe



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
		prefix= "BANKNIFTY" + formatted_date
		"""Setting the date Format to extract data for that Particular Date"""
		output_date=change_date_format(date)

		table = [[0] * 4 for _ in range(9)]
		table1 = [[0] * 4 for _ in range(9)]
		table_ce = [[0] * 5 for _ in range(6)]
		table_pe = [[0] * 5 for _ in range(6)]

		time_str = '09:15:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		max_premium=0
		max_discount=0
		count_premium=0
		count_discount=0
		n=0

		premium_count_5=0
		discount_count_5=0


		table,table1,table_ce,table_pe=getting_data_for_sp_calculate_atp_ltp(output_date,prefix,table,table1,table_ce,table_pe)

		for rows in table:
			print(rows)
		print("---------------------------------------------------------------------------------------------------------------")
		for rows in table1:
			print(rows)	
		print("---------------------------------------------------------------------------------------------------------------")
		for rows in table_ce:
			print(rows)
		print("---------------------------------------------------------------------------------------------------------------")
		for rows in table_pe:
			print(rows)		
		print("---------------------------------------------------------------------------------------------------------------")

		while time_obj.time() < datetime.strptime('11:15:59', '%H:%M:%S').time():

			print(time_obj.time())
			value=premium_discount(time_obj)

			if value>0:
				count_premium=count_premium+1
				count_discount=0
				if count_premium>max_premium:
					max_premium=count_premium

			elif value<0:
				count_discount=count_discount+1
				count_premium=0
				if count_discount>max_discount:
					max_discount=count_discount

			if value>8:
				premium_count_5=premium_count_5+1
				discount_count_5=0
				if premium_count_5==5:
					print("--------Premium--------------")
					premium_count_5=0
			elif value <-8:
				discount_count_5=discount_count_5+1
				premium_count_5=0
				if discount_count_5==5:
					print("--------------Discount------------------")		
					discount_count_5=0



			time_obj += timedelta(minutes=m)
			n=n+1

		print(max_premium)
		print(max_discount)	
		print("---------------------------------------------------------------------------------------------------------------")

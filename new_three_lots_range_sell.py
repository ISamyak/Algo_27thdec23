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
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/3_7/ex-date-fn/A/B'
nifty_path = './Nirmal_Fincap/Nifty/2022/'
n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

prefix=" "
m=1
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'


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


def setting_prefix_suffix_for_excel_data(sp):
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

def select_atm_strike_price(output_date,output_closing_time,selected_strike_price):

	output_opening_time = output_date+ " 090000"
		
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	print(a)
	if a==['']:
		print("we cannot ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  float(a[4])%100 <=25:
			for_STRIKE=int(float(a[4]) - float(a[4])%100)
			selected_check_ce.append(for_STRIKE)
			selected_check_pe.append(for_STRIKE)

		elif float(a[4])%100 >= 75:
			for_STRIKE=int(float(a[4]) + (100 - float(a[4])%100))
			selected_check_ce.append(for_STRIKE)
			selected_check_pe.append(for_STRIKE)

		else:
			for_STRIKE=int(float(a[4]) - float(a[4])%100) + 50
			selected_check_ce.append(for_STRIKE)
			selected_check_pe.append(for_STRIKE)
	
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

def sl_check(time,trade_data,sl,number):
	t=0
	df = pd.read_csv(path)
	while t<m:
		time_obj = datetime.strptime(time, "%H:%M:%S")
		time_obj += timedelta(minutes=1)
		time_str = time_obj.strftime("%H:%M:%S")

		filtered_data  = df.loc[(df['Ticker']== trade_data[-1][1] ) & (df['Time'] == time_str)]
		extracted = filtered_data.to_dict('records')
		close1=extracted[0]['High']

		# filtered_data  = df.loc[(df['Ticker']== trade_data[-1][1] ) & (df['Time'] == time_str)]
		# extracted = filtered_data.to_dict('records')
		# close2=extracted[0]['High']
		global max_drawdown
		max_drawdown = max(max_drawdown,close1)
		# print(close1)
		if (close1) >= (sl):
			print("--------------------StopLoss Hit---------------------------------"+ str(number))
		t=t+1


		
def price_of_atm_strike_price(selected_itm_Sp,time):
	df = pd.read_csv(path)
	
	filtered_data = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == str(time))]
	extracted_data = filtered_data.to_dict('records')
	if extracted_data==[]:
		time = time_obj.time().strftime("%H:%M:%S")
		filtered_data = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == str(time))]

	filtered_data  = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == '15:29:59' )]
	extracted_data2 = filtered_data.to_dict('records')
	print(selected_itm_Sp)
	print(extracted_data)
	print(extracted_data2)
	price=[selected_itm_Sp,extracted_data[0]['Close'],extracted_data2[0]['Close']] 
			
		
	return price

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
		# a1=getting_nifty_data_from_excel(date,0,378)
		
		"""Setting Strike price for day range from -300 to + 300"""
		Strike_Price_Set=strike_price_for_data(a)

		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
			

		"""Setting Strike Price For Day for 2:45 self"""
		trade_data=[]
		output_closing_time = output_date + " 100059"
		selected_atm_Sp = select_atm_strike_price(output_date,output_closing_time,[])
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(selected_atm_Sp)
		print(" Sell  Pair " +  str(selected_atm_Sp[0]))

		time_str = '10:00:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')

		pass_index=prefix+str(selected_atm_Sp[0])+"PE.NFO"

		price=price_of_atm_strike_price(pass_index,time_obj.time())
		print(price)
		row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
		trade_data.append(row1)

		pass_index=prefix+str(selected_atm_Sp[0])+"CE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		print(price)
		row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
		trade_data.append(row1)


		trade=False
		max_drawdown=0
		strike_price_sell=selected_atm_Sp[0]

		while time_obj.time() < datetime.strptime('15:00:59', '%H:%M:%S').time():
			
			time_obj1 = time_obj.replace(second=0)
			time_str3= time_obj1.time().strftime("%H%M%S")
			output_opening_time= output_date + " "+time_str3
			time_obj += timedelta(minutes=m)
			time_obj1 = time_obj.replace(second=0)
			time_str3= time_obj1.time().strftime("%H%M%S")
			output_closing_time = output_date +" "+time_str3
			a=getting_ohlc_nifty(output_opening_time,output_closing_time)
			if a==['']:
				continue
			# print(a)
			if float(a[2]) >= strike_price_sell+50:
				strike_price_sell=strike_price_sell+50
				print("Sell Higher " + str(strike_price_sell))

				pass_index=prefix+str(strike_price_sell)+"PE.NFO"
				price=price_of_atm_strike_price(pass_index,time_obj.time())
				print(price)
				row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
				trade_data.append(row1)

				pass_index=prefix+str(strike_price_sell)+"CE.NFO"
				price=price_of_atm_strike_price(pass_index,time_obj.time())
				print(price)
				row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
				trade_data.append(row1)

			elif float(a[3]) <= strike_price_sell-50:
				strike_price_sell=strike_price_sell-50
				print("Sell Lower " + str(strike_price_sell))

				pass_index=prefix+str(strike_price_sell)+"PE.NFO"
				price=price_of_atm_strike_price(pass_index,time_obj.time())
				print(price)
				row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
				trade_data.append(row1)

				pass_index=prefix+str(strike_price_sell)+"CE.NFO"
				price=price_of_atm_strike_price(pass_index,time_obj.time())
				print(price)
				row1=[output_date,price[0],time_obj.time(),'15:29:59','Sell',price[1],price[2],'']
				trade_data.append(row1)

		for rows in trade_data:
			writer.writerow(rows)
				

			
			



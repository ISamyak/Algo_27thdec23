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
API_KEY = "27cb3075e6f28484597669"
API_SECRET = "Vfrx866#y0"
clientID = "D0253276"
#userID = "D0253276"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"


xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.interactive_login()

day=''
header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/3_7/ex-date-fn/Oct_nov/'
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
    	exchangeInstrumentID=26034,
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

def select_pair_strike_price(output_date,selected_strike_price,m,n):

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

		if float(a[4])%100<50:
			for_STRIKE=int(float(a[4]) - float(a[4])%100)-50
			selected_check.append(for_STRIKE)
			for_STRIKE=for_STRIKE+50
			selected_check.append(for_STRIKE)
			for_STRIKE=for_STRIKE+50
			selected_check.append(for_STRIKE)
		elif float(a[4])%100>=50:
			for_STRIKE=int(float(a[4]) - float(a[4])%50)-50
			selected_check.append(for_STRIKE)
			for_STRIKE=for_STRIKE+50
			selected_check.append(for_STRIKE)
			for_STRIKE=for_STRIKE+50
			selected_check.append(for_STRIKE)

			

		return selected_check	

def price_of_atm_strike_price(selected_itm_Sp,time):
	df = pd.read_csv(path)
	
	filtered_data = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == str(time))]
	extracted_data = filtered_data.to_dict('records')
	if extracted_data==[]:
		time = time_obj.time().strftime("%H:%M:%S")
		filtered_data = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == str(time))]

	# filtered_data  = df.loc[(df['Ticker']== selected_itm_Sp ) & (df['Time'] == '15:29:59' )]
	# extracted_data2 = filtered_data.to_dict('records')
	price=[selected_itm_Sp,extracted_data[0]['Close']] 
			
		
	return price

def getting_data_for_nearest_itm_atp_ltp(sp_itm,time_obj):
	
	df = pd.read_csv(path)
	start_time = pd.to_datetime('09:15:00').time()
	end_time = time_obj.time()
	df['Time'] = pd.to_datetime(df['Time'])
	filtered_data = df.loc[(df['Ticker'] == sp_itm) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]	
	# filtered_data = df.loc[(df['Ticker']== i[:23])][20688:21408]
	extracted_data = filtered_data.to_dict('records')
	a=0
	d=0	
	for j in range(len(extracted_data)):
		if(extracted_data != []):
			if j==0:
				c=extracted_data[j]['Volume']
				a=extracted_data[j]['Volume']*extracted_data[j]['Close']
				b=a/c
				d=extracted_data[j]['Close']/b-1
			else:
				c=extracted_data[j]['Volume']+c
				a=a+extracted_data[j]['Volume']*extracted_data[j]['Close']	
				b=a/c
				d=(extracted_data[j]['Close']/b-1)*100		
		else:
			print("8th Wrong Data")
	return c,a,d

def update_data_for_nearest_itm_atp_ltp(sp_itm,time_obj,volume,trade_value):
	
	df = pd.read_csv(path)
	start_time = pd.to_datetime('09:15:00').time()
	end_time = time_obj.time()
	df['Time'] = pd.to_datetime(df['Time'])
	filtered_data = df.loc[(df['Ticker'] == sp_itm) & (df['Time'].dt.time == end_time)]	
	# filtered_data = df.loc[(df['Ticker']== i[:23])][20688:21408]
	extracted_data = filtered_data.to_dict('records')

	if(extracted_data != []):
		c=extracted_data[0]['Volume']+volume
		a=trade_value+extracted_data[0]['Volume']*extracted_data[0]['Close']	
		b=a/c
		d=(extracted_data[0]['Close']/b-1)*100		
	else:
		print("8th Wrong Data")
	return c,a,d		

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
		prefix= "FINNIFTY" + formatted_date
		"""Setting the date Format to extract data for that Particular Date"""
		output_date=change_date_format(date)

		output_opening_time = output_date+ " 090000"
		output_closing_time = output_date + " 100000"
		selected_Sp = select_pair_strike_price(output_date,[],0,46)
		# filter_based_on_sp=setting_prefix_suffix_for_excel_data(selected_Sp)

		time_str = '10:00:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		n=46

		q1=1.0
		q2=1.0
		q3=1.0
		ratio_val_call=0
		ratio_val_put=0
		sp_itm_ce=prefix+str(selected_Sp[0])+"CE.NFO"
		sp_itm_pe=prefix+str(selected_Sp[2])+"PE.NFO"



		volume_ce,trade_value_ce,ltp_atp_ratio_ce=getting_data_for_nearest_itm_atp_ltp(sp_itm_ce,time_obj)
		volume_pe,trade_value_pe,ltp_atp_ratio_pe=getting_data_for_nearest_itm_atp_ltp(sp_itm_pe,time_obj)

		# print(ltp_atp_ratio_ce)
		# print(ltp_atp_ratio_pe)

		pass_index=prefix+str(selected_Sp[0])+"PE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		p1=price[1]
		# ratio_val_put=q1*price[1]

		pass_index=prefix+str(selected_Sp[1])+"PE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		p2=price[1]
		# ratio_val_put=ratio_val_put+q2*price[1]

		pass_index=prefix+str(selected_Sp[2])+"PE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		p3=price[1]
		# ratio_val_put=ratio_val_put+q3*price[1]

		pass_index=prefix+str(selected_Sp[0])+"CE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		c1=price[1]
		# ratio_val_call=q1*price[1]

		pass_index=prefix+str(selected_Sp[1])+"CE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		c2=price[1]
		# ratio_val_call=ratio_val_call+q2*price[1]

		pass_index=prefix+str(selected_Sp[2])+"CE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		c3=price[1]

		pass_index=prefix+str(selected_Sp[0]-50)+"CE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		pro1=price[1]

		pass_index=prefix+str(selected_Sp[2]+50)+"PE.NFO"
		price=price_of_atm_strike_price(pass_index,time_obj.time())
		pro2=price[1]


		# print("Total Sell value:"+ str(p1+p2+p3+c1+c2+c3))

		time_str = '10:01:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')

		max_loss = (450 - (p1+p2+p3+c1+c2+c3)) - ((250 - (pro1 + pro2))*3)
		max_profit = ((p1+p2+p3+c1+c2+c3)-100) - (((pro1 + pro2)-200)*3)

		print("Max profit can be - " + str(max_profit))
		print("Max loss can be - "+ str(max_loss))

		print("20% of Max loss"+ str(max_loss*0.2))

		while time_obj.time() < datetime.strptime('15:00:59', '%H:%M:%S').time():

			print(time_obj.time())

			pass_index=prefix+str(selected_Sp[0])+"PE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			p4=price[1]
			# # ratio_val_put=q1*price[1]

			pass_index=prefix+str(selected_Sp[1])+"PE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			p5=price[1]
			# # ratio_val_put=ratio_val_put+q2*price[1]

			pass_index=prefix+str(selected_Sp[2])+"PE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			p6=price[1]
			# # ratio_val_put=ratio_val_put+q3*price[1]

			pass_index=prefix+str(selected_Sp[0])+"CE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			c4=price[1]
			# # ratio_val_call=q1*price[1]

			pass_index=prefix+str(selected_Sp[1])+"CE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			c5=price[1]
			# # ratio_val_call=ratio_val_call+q2*price[1]

			pass_index=prefix+str(selected_Sp[2])+"CE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			c6=price[1]

			pass_index=prefix+str(selected_Sp[0]-50)+"CE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			pro3=price[1]

			pass_index=prefix+str(selected_Sp[2]+50)+"PE.NFO"
			price=price_of_atm_strike_price(pass_index,time_obj.time())
			pro4=price[1]


			diff1=p1-p4
			diff2=p2-p5
			diff3=p3-p6

			diff4=c1-c4
			diff5=c2-c5
			diff6=c3-c6

			diff7= (pro4-pro2)*3
			diff8=(pro3-pro1)*3

			current_condition= diff1+diff2+diff3+diff4+diff5+diff6+diff7+diff8

			print(current_condition)

			if (max_loss*(0-0.2))>current_condition:
				print("-----------------20 % loss hit------------------------")


			# ratio_val_call=ratio_val_call+q3*price[1]

			# for_put = ratio_val_put/(ratio_val_call+ ratio_val_put)
			# for_call = ratio_val_call/(ratio_val_call+ ratio_val_put)

			# print(time_obj.time(),end=" put ratio: ")
			# print(for_put ,end=" call ratio : " )
			# print(for_call)

			# if (for_put) < 0.37:
			# 	print("Market tezi Adjust")
			# 	qx =((-0.57*(q1*p1 + q2*p2)) + (0.43*(q1*c1 + q2*c2))) / (0.57*p3 - 0.43*c3)
			# 	print("Add qunatity in q3 - "+ str (qx-q3))
			# 	q3=qx	
			# elif for_call < 0.37:
			# 	print("Market Mandi Adjust")
			# 	qx =((-0.57*(q2*c2 + q3*c3)) + (0.43*(q2*p2 + q3*p3))) / (0.57*c1 - 0.43*p1)
			# 	print("Add qunatity in q1 - "+ str (qx-q1))
			# 	q1=qx
			# else:
			# 	print("Continue")

			volume_ce,trade_value_ce,ltp_atp_ratio_ce=update_data_for_nearest_itm_atp_ltp(sp_itm_ce,time_obj,volume_ce,trade_value_ce)
			volume_pe,trade_value_pe,ltp_atp_ratio_pe=update_data_for_nearest_itm_atp_ltp(sp_itm_pe,time_obj,volume_pe,trade_value_pe)

			# print(ltp_atp_ratio_ce)
			# print(ltp_atp_ratio_pe)

			if ltp_atp_ratio_ce>100:
				# pass_index=prefix+str(selected_Sp[0])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p1=price[1]
				# # ratio_val_put=q1*price[1]

				# pass_index=prefix+str(selected_Sp[1])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p2=price[1]
				# # ratio_val_put=ratio_val_put+q2*price[1]

				# pass_index=prefix+str(selected_Sp[2])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p3=price[1]
				# # ratio_val_put=ratio_val_put+q3*price[1]

				# pass_index=prefix+str(selected_Sp[0])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c1=price[1]
				# # ratio_val_call=q1*price[1]

				# pass_index=prefix+str(selected_Sp[1])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c2=price[1]
				# # ratio_val_call=ratio_val_call+q2*price[1]

				# pass_index=prefix+str(selected_Sp[2])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c3=price[1]

				print("------------------Atp ltp hit ------------------")
				

			if ltp_atp_ratio_pe>100:
				# pass_index=prefix+str(selected_Sp[0])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p1=price[1]
				# # ratio_val_put=q1*price[1]

				# pass_index=prefix+str(selected_Sp[1])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p2=price[1]
				# # ratio_val_put=ratio_val_put+q2*price[1]

				# pass_index=prefix+str(selected_Sp[2])+"PE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# p3=price[1]
				# # ratio_val_put=ratio_val_put+q3*price[1]

				# pass_index=prefix+str(selected_Sp[0])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c1=price[1]
				# # ratio_val_call=q1*price[1]

				# pass_index=prefix+str(selected_Sp[1])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c2=price[1]
				# # ratio_val_call=ratio_val_call+q2*price[1]

				# pass_index=prefix+str(selected_Sp[2])+"CE.NFO"
				# price=price_of_atm_strike_price(pass_index,time_obj.time())
				# c3=price[1]

				print("------------------Atp ltp hit ------------------")
				

			time_obj += timedelta(minutes=m)
			n=n+1	






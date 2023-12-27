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
import collections

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
folder_path ='./Nirmal_Fincap/1min_data/CE'
folder_path1='./Nirmal_Fincap/1min_data/PE'
path='./Nirmal_Fincap/1min_data/merged/merged_data.csv'
# nifty_path = './Nirmal_Fincap/Nifty/2022/'
# n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

prefix="NIFTY06JUL23"
candle=1
max_drawdown=0
files = os.listdir(folder_path)
files1= os.listdir(folder_path1)
# filepath=folder_path+'/Trade.csv'


#function
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
		response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=4500000)
		a=response['result']['dataReponse'].split('|')
		if a==['']:
			print("Wrong Data Imp")
			return a
		else:
			return a	
	else:
		return a


def setting_prefix_suffix_for_excel_data(sp):
	filter_based_on_sp=[]
	for i in sp[0:3]:
		temp=prefix+str(i)+"CE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1)
	for i in sp[3:]:
		temp=prefix+str(i)+"PE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1) 	
	return filter_based_on_sp

def select_itm_strike_price(a):

	selected_check=[]
	selected_check_ce=[]
	selected_check_pe=[]
	
	if  a%100 <=25:
		for_CE_STRIKE=int(a - a%100)
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE=int(a - a%100) - 50
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE = for_CE_STRIKE - 50
		selected_check_ce.append(for_CE_STRIKE)
		# for_CE_STRIKE = for_CE_STRIKE - 50
		# selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE=int(a - a%100)
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = int(a - a%100) + 50
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = for_PE_STRIKE + 50
		selected_check_pe.append(for_PE_STRIKE)
		# for_PE_STRIKE = for_PE_STRIKE + 50
		# selected_check_pe.append(for_PE_STRIKE)

	elif a%100 >= 75:
		for_CE_STRIKE=int(a + (100 - a%100))
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE=int(a + (100-a%100)) - 50
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE= for_CE_STRIKE-50
		# selected_check_ce.append(for_CE_STRIKE)
		# for_CE_STRIKE= for_CE_STRIKE-50
		selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = int(a + (100 - a%100))
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = int(a + (100-a%100))+50
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = for_PE_STRIKE + 50
		selected_check_pe.append(for_PE_STRIKE)
		# for_PE_STRIKE = for_PE_STRIKE + 50
		# selected_check_pe.append(for_PE_STRIKE)
	else:

		for_CE_STRIKE=int(a - a%100) + 50
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE=int(a - a%100)
		selected_check_ce.append(for_CE_STRIKE)
		for_CE_STRIKE= for_CE_STRIKE-50
		selected_check_ce.append(for_CE_STRIKE)
		# for_CE_STRIKE= for_CE_STRIKE-50
		# selected_check_ce.append(for_CE_STRIKE)
		for_PE_STRIKE = int(a - a%100) + 50
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = int(a - a%100) + 100
		selected_check_pe.append(for_PE_STRIKE)
		for_PE_STRIKE = for_PE_STRIKE + 50
		selected_check_pe.append(for_PE_STRIKE)
		# for_PE_STRIKE = for_PE_STRIKE + 50
		# selected_check_pe.append(for_PE_STRIKE)
	
	selected_check_ce = selected_check_ce[::-1]		
	selected_check = selected_check_ce + selected_check_pe
	return selected_check				

def getting_data_for_nearest_itm_atp_ltp(date,ITM_Table):
	k=0
	for i in files:
		path=folder_path+'/'+i
		df = pd.read_csv(path)
		start_time = pd.to_datetime('14:58:00').time()
		end_time = pd.to_datetime('15:09:59').time()
		df['Time'] = pd.to_datetime(df['Time'])
		filtered_data = df.loc[(df['Ticker'] == i[:23]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]	
		# filtered_data = df.loc[(df['Ticker']== i[:23])][20688:21408]
		extracted_data = filtered_data.to_dict('records')
		a=0	
		for j in range(len(extracted_data)):
			if(extracted_data != []):
				if j==0:
					c=extracted_data[j]['LTQ']
					a=extracted_data[j]['LTQ']*extracted_data[j]['LTP']
					b=a/c
					d=extracted_data[j]['LTP']/b-1
				else:
					c=extracted_data[j]['LTQ']+c
					a=a+extracted_data[j]['LTQ']*extracted_data[j]['LTP']	
					b=a/c
					d=(extracted_data[j]['LTP']/b-1)*100		
			else:
				print("8th Wrong Data")
			ITM_Table[k][0]=i[:23]
			ITM_Table[k][1]=extracted_data[j]['Time']
			ITM_Table[k][2]=d
			k=k+1
	return ITM_Table			

def getting_data_for_nearest_itm_atp_ltp_PE(date,ITM_Table):
	k=0
	for i in files1:
		path=folder_path1+'/'+i
		df = pd.read_csv(path)

		start_time = pd.to_datetime('14:58:00').time()
		end_time = pd.to_datetime('15:09:59').time()
		df['Time'] = pd.to_datetime(df['Time'])
		filtered_data = df.loc[(df['Ticker'] == i[:23]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]
		# filtered_data = df.loc[(df['Ticker']== i[:23])][20688:21408]
		extracted_data = filtered_data.to_dict('records')
		a=0	
		for j in range(len(extracted_data)):
			if(extracted_data != []):
				if j==0:
					c=extracted_data[j]['LTQ']
					a=extracted_data[j]['LTQ']*extracted_data[j]['LTP']
					b=a/c
					d=extracted_data[j]['LTP']/b-1
				else:
					c=extracted_data[j]['LTQ']+c
					a=a+extracted_data[j]['LTQ']*extracted_data[j]['LTP']	
					b=a/c
					d=(extracted_data[j]['LTP']/b-1)*100		
			else:
				print("8th Wrong Data")

			ITM_Table[k][0]=i[:23]
			ITM_Table[k][1]=extracted_data[j]['Time']
			ITM_Table[k][2]=d
			k=k+1
	return ITM_Table	


def ltp_atp_correction(mini):
	if mini >= 0:
		return -15
	elif mini < 0 and mini > -10:
		return mini - 14
	elif mini <=-10 and mini > -20:
		return mini - 12
	elif mini <=-20 and mini > -30:
		return mini - 10
	elif mini <=-30 and mini > -35:
		return mini - 7
	elif mini <=-35 and mini > -40:
		return mini - 6
	elif mini <=-40 and mini > -45:
		return mini - 5
	elif mini <=-45 and mini > -50:
		return mini - 4
	elif mini <=-50 and mini > -60:
		return mini - 3
	elif mini <=-60 and mini > -99.9:
		return mini - 2
	else:
		return mini							



def getting_data_for_sp_calculate_atp_ltp(date,Table,sp,LTP_ATP_Table,ITM_Table_CE_info,ITM_Table_PE_info,sum_counter):
	df = pd.read_csv(path)
	counter_for_sum=[[0] * 7 for _ in range(30000)]
	l=0
	for j in range(len(sp)):
		print(j)
		start_time = pd.to_datetime('09:15:01').time()

		end_time = pd.to_datetime('15:00:00').time()
		df['Time'] = pd.to_datetime(df['Time'])

		filtered_data = df.loc[(df['Ticker'] == sp[j]) & (df['Time'].dt.time >= start_time) & (df['Time'].dt.time <= end_time)]
		
		extracted_data = filtered_data.to_dict('records')
		
		a=0
		a1=0
		Table[j][0]=sp[j]

		mini=400
		mini_time=''
		mini_index_value=0
		alpha=0
		alpha_time=''
		mini1=400
		mini_time1=''
		mini_index_value1=0
		for i in range(len(extracted_data)):
			
			if(extracted_data != [] and extracted_data[i]['LTQ'] !=0):
				if i==0:
					c=extracted_data[i]['LTQ']
					a=extracted_data[i]['LTQ']*extracted_data[i]['LTP']
					b=a/c
					d=extracted_data[i]['LTP']/b-1
				else:
					c=extracted_data[i]['LTQ']+c
					a=a+extracted_data[i]['LTQ']*extracted_data[i]['LTP']	
					b=a/c
					d=(extracted_data[i]['LTP']/b-1)*100
					if mini > d:
						# a1=getting_nifty_data_from_excel(date,0,i)
						mini_index_value=0
						mini_time=extracted_data[i]['Time']
						mini=min(mini,d)
			else:		
				print("8th Wrong Data")
		

			LTP_ATP_Table[j][0]=extracted_data[i]['Ticker']
			LTP_ATP_Table[j][1]=extracted_data[i]['Time']
			LTP_ATP_Table[j][2]=extracted_data[i]['LTP']
			LTP_ATP_Table[j][3]=extracted_data[i]['LTQ']
			LTP_ATP_Table[j][4]=c
			LTP_ATP_Table[j][5]=a
			LTP_ATP_Table[j][6]=b
			LTP_ATP_Table[j][7]=d


			Table[j][1]=d
			Table[j][2]=mini
			Table[j][3]=mini_time
 
			Table[j][4]= ltp_atp_correction(mini)
			
			Table[j][6]=mini_index_value

			"""For Oppposite side"""
			if "CE" in sp[j]:
				modified_string = sp[j].replace("CE", "PE")
			else:
				modified_string= sp[j].replace("PE", "CE")

			timestamp = pd.Timestamp(extracted_data[i]['Time'])
			time_only = timestamp.strftime('%H:%M:%S')

			time_only = pd.to_datetime(time_only).time()

			filtered_data1 = df.loc[(df['Ticker'] == modified_string) & (df['Time'].dt.time == time_only)]
			extracted_data1 = filtered_data1.to_dict('records')
			
			
			if extracted_data1==[]:
				# print("Check what to do")
				xyz=1
			else:	
				
				for k in range(len(extracted_data1)):
					if(extracted_data1 != [] and extracted_data1[k]['LTQ'] !=0):
						if i==0:
							c1=extracted_data1[k]['LTQ']
							a1=extracted_data1[k]['LTQ']*extracted_data1[k]['LTP']
							b1=a1/c1
							d1=extracted_data1[k]['LTP']/b1-1
						else:
							c1=extracted_data1[k]['LTQ']+c1
							a1=a1+extracted_data1[k]['LTQ']*extracted_data1[k]['LTP']	
							b1=a1/c1
							d1=(extracted_data1[k]['LTP']/b1-1)*100

							if mini1 > d1:
								# a1=getting_nifty_data_from_excel(date,0,i)
								mini_index_value1=0

							mini1=min(mini1,d1)
					else:
						print("8th Wrong Data")

					LTP_ATP_Table[j][8]=extracted_data1[k]['Ticker']
					LTP_ATP_Table[j][9]=extracted_data1[k]['Time']
					LTP_ATP_Table[j][10]=extracted_data1[k]['LTP']
					LTP_ATP_Table[j][11]=extracted_data1[k]['LTQ']
					LTP_ATP_Table[j][12]=c1
					LTP_ATP_Table[j][13]=a1
					LTP_ATP_Table[j][14]=b1
					LTP_ATP_Table[j][15]=d1

					Table[j][5]=d+d1
				
				if l==0:
					counter_for_sum[i][l]=extracted_data1[k]['Time']
				
				counter_for_sum[i][l+1]=d+d1

		l=l+1
		print(counter_for_sum)
	# print(counter_for_sum)
	min_indexes = []

	for row in counter_for_sum:
	    min_value = min(row[1:])  # Find the minimum value in the current row
	    min_index = row.index(min_value)  # Find the index of the minimum value
	    min_indexes.append(min_index)

	counts = collections.Counter(min_indexes)
	numbers_to_count = [1, 2, 3, 4, 5,6]
	print(numbers_to_count)
	print(numbers_to_count[-120:])
	sum_counter = [counts[number] for number in numbers_to_count[-120:] ]
	print(sum_counter)
	
	return Table,LTP_ATP_Table,sum_counter


def update_data_atp_ltp(date,Table,sp,LTP_ATP_Table,time,Trade,counter,price_counter):
	df = pd.read_csv(path)
	for j in range(len(sp)):
		filtered_data = df.loc[(df['Ticker']== sp[j] )  & (df['Time'] == str(time)) ]
		extracted_data = filtered_data.to_dict('records')
		for i in range(len(extracted_data)):
			if(extracted_data != []):
				c=LTP_ATP_Table[j][4]+extracted_data[0]['LTQ']
				a= LTP_ATP_Table[j][5] + extracted_data[0]['LTQ']*extracted_data[0]['LTP']	
				b=a/c
				d=(extracted_data[0]['LTP']/b-1)*100
			else:
				print("8th Wrong Data")
				continue
			LTP_ATP_Table[j][0]=extracted_data[0]['Ticker']
			LTP_ATP_Table[j][1]=extracted_data[0]['Time']
			LTP_ATP_Table[j][2]=extracted_data[0]['LTP']
			LTP_ATP_Table[j][3]=extracted_data[0]['LTQ']
			LTP_ATP_Table[j][4]=c
			LTP_ATP_Table[j][5]=a	
			LTP_ATP_Table[j][6]=b	
			LTP_ATP_Table[j][7]=d

			if "CE" in sp[j]:
				modified_string = sp[j].replace("CE", "PE")
			else:
				modified_string= sp[j].replace("PE", "CE")
			
			filtered_data1 = df.loc[(df['Ticker']== modified_string ) & (df['Time'] == str(time))  ]
			extracted_data1 = filtered_data1.to_dict('records')

			for k in range(len(extracted_data1)):
				if(extracted_data1 != []):
					c1=extracted_data1[0]['LTQ']+LTP_ATP_Table[j][12]
					a1=  LTP_ATP_Table[j][13] +extracted_data1[0]['LTQ']*extracted_data1[0]['LTP']	
					b1=a1/c1
					d1=(extracted_data1[0]['LTP']/b1-1)*100
				else:
					print("8th Wrong Data")
			if extracted_data1 == []:
				xyz=0			 
			else:	
				LTP_ATP_Table[j][8]=modified_string
				LTP_ATP_Table[j][9]=str(time)
				LTP_ATP_Table[j][10]=extracted_data1[0]['LTP']
				LTP_ATP_Table[j][11]=extracted_data1[0]['LTQ']
				LTP_ATP_Table[j][12]=c1
				LTP_ATP_Table[j][13]=a1
				LTP_ATP_Table[j][14]=b1
				LTP_ATP_Table[j][15]=d1

				
				Table[j][1]=d

				Table[j][5]=d+d1
		if Table[j][1] < Table[j][4]:
			counter[j]=counter[j]+1

		if LTP_ATP_Table[j][2]*3 <= LTP_ATP_Table[j][10]:
			price_counter[j]=price_counter[j]+1

	return Table,LTP_ATP_Table,counter,price_counter


curr_dt="20230706"

output_date=change_date_format(curr_dt)
output_opening_time = output_date+ " 140000"
output_closing_time = output_date + " 145800"
a1=getting_ohlc_nifty(output_opening_time,output_closing_time)
print(a1)
selected_itm_Sp = select_itm_strike_price(float(a1[4]))
print(selected_itm_Sp)

Table = [[0] * 9 for _ in range(len(selected_itm_Sp))]
LTP_ATP_Table=[[0] * 16 for _ in range(len(selected_itm_Sp))]
simple_filter_sp=setting_prefix_suffix_for_excel_data(selected_itm_Sp)
ITM_Table_CE_info=[[0] * 3 for _ in range(72000*5)]
ITM_Table_PE_info=[[0] * 3 for _ in range(72000*5)]

ITM_Table_CE_info=getting_data_for_nearest_itm_atp_ltp(output_date,ITM_Table_CE_info)
# print(ITM_Table_CE_info)
ITM_Table_PE_info=getting_data_for_nearest_itm_atp_ltp_PE(output_date,ITM_Table_PE_info)
# print(ITM_Table_PE_info)

sum_counter=[0,0,0,0,0,0]
Table,LTP_ATP_Table,sum_counter=getting_data_for_sp_calculate_atp_ltp(output_date,Table,simple_filter_sp,LTP_ATP_Table,ITM_Table_CE_info,ITM_Table_PE_info,sum_counter)
print(" Ticker					   LTP/ATP@3:00				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE	Index Index@Trade	  Sum_Count_Max  ")	
for rows in Table:
	print(rows)
print("-------------------------------------------------------------------------------")	
for rows in LTP_ATP_Table:
	print(rows)
print("-------------------------------------------------------------------------------")


time_str = '15:00:00'
time_obj = datetime.strptime(time_str, '%H:%M:%S')
Trade=''
Trade1=''
counter=[0,0,0,0,0,0]
price_counter=[0,0,0,0,0,0]
min_indexes = []
while time_obj.time() < datetime.strptime('15:29:59', '%H:%M:%S').time():
	print(time_obj.time())
	time_obj += timedelta(seconds=candle)

	Table,LTP_ATP_Table,counter,price_counter=update_data_atp_ltp(output_date,Table,simple_filter_sp,LTP_ATP_Table,time_obj.time(),Trade,counter,price_counter)
	print(counter)
	print(price_counter)

	if any(value >= 5 for value in price_counter) and Trade == '':
		indices = [index for index, value in enumerate(counter) if value >= 5]
		if indices == []:
			print("Not fulfilled")
		else:
			print(indices)
			sum_array = [row[5] for row in Table]
			min_value = min(sum_array)
			min_index = sum_array.index(min_value)
			
			max_value = max(sum_counter)
			max_value_index=sum_counter.index(max_value)

			z=selected_itm_Sp[min_index]
			y=selected_itm_Sp[max_value_index]
			
			if max_value_index > min_index:
				print("Take a call trade")
				if y-z >=100:
					print("Intiate Trade")
					Trade=True
				else:
					print("Take 1-1.5 rs above")
			elif max_value_index < min_index:
				print("Take a put Trade only if counter ce pe")
				if z-y >=100:
					print("Intiate trade")
				else:
					print("Take 1-1.5 rs Above")
			else:
				print("No Shifting yet")

			 
				 

	# if Trade=='':
	# 	sum_array = [row[5] for row in Table]
	# 	# print(sum_array)
	# 	min_value = min(sum_array)  # Find the minimum value in the current row
	# 	min_index = sum_array.index(min_value)  # Find the index of the minimum value
	# 	min_indexes.append(min_index)

	# else:		    
	# 	counts = collections.Counter(min_indexes)
	# 	numbers_to_count = [0,1, 2, 3, 4, 5]
	# 	sum_counter1 = [counts[number] for number in numbers_to_count]
	# 	print(sum_counter1)

	# 	max_value = max(sum_counter)
	# 	max_value_index=sum_counter.index(max_value)

	# 	shift_value=max(sum_counter1)
	# 	shift_value_index=sum_counter1.index(shift_value)

	# 	if max_value_index > shift_value_index:
	# 		print("Take a call trade")
	# 		if max_value_index - shift_value_index >=2:
	# 			print("Intiate Trade")
	# 		else:
	# 			print("Take 1-1.5 rs above")
	# 	elif max_value_index < shift_value_index:
	# 		print("Take a put Trade only if counter ce pe")
	# 		if max_value_index - shift_value_index >=2:
	# 			print("Intiate trade")
	# 		else:
	# 			print("Take 1-1.5 rs Above")
	# 	else:
	# 		print("No Shifting yet")			


	for rows in Table:
		print(rows)
	print("-------------------------------------------------------------------------------")
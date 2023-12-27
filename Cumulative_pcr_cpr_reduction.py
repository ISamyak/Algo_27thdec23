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
header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2022/11/expiry4'
prefix="NIFTY24NOV22"
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

def change_date_format(date):
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[3])) - (int(float(a[3])%50)) - 300
	while int(float(a[2]))+300 > SP:
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

def setting_strike_price(setting_sp_closeTime,selected_strike_price):
	setting_sp_startTime = output_date+ " 091500"
	a=getting_ohlc_nifty(setting_sp_startTime,setting_sp_closeTime)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:	
		for_CE_STRIKE = float(a[3]) + abs(100- (float(a[3])%100))
		for_PE_STRIKE = float(a[2]) - abs((float(a[2])%100))
		# print("-----------------------------------------------")
		# print("Selected Strike price")
		selected_check=[]
		# print("CE Strike " +"  "+"PE Strike")
		# print(str(for_CE_STRIKE) + "  " +str(for_PE_STRIKE))
		selected_check.append(for_CE_STRIKE)
		selected_check.append(for_CE_STRIKE+100)
		selected_check.append(for_CE_STRIKE+200)
		# selected_check.append(for_CE_STRIKE+150)
		selected_check.append(for_PE_STRIKE)
		selected_check.append(for_PE_STRIKE-100)
		selected_check.append(for_PE_STRIKE-200)
		# selected_check.append(for_CE_STRIKE-150)
		# print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
		# print(str(for_CE_STRIKE + 200) + "  " +str(for_PE_STRIKE - 200))
		# print(str(for_CE_STRIKE + 150) + "  " +str(for_PE_STRIKE - 150))
		# print("-----------------------------------------------")
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

def set_data_for_max_oi(OI_Data,selected_check):
	A=np.array(OI_Data)
	row_info1=np.where(A==selected_check[0])[0].tolist()
	row_info2=np.where(A==selected_check[1])[0].tolist()
	row_info3=np.where(A==selected_check[2])[0].tolist()
	row_info4=np.where(A==selected_check[3])[0].tolist()
	row_info5=np.where(A==selected_check[4])[0].tolist()
	row_info6=np.where(A==selected_check[5])[0].tolist()

	if abs(OI_Data[row_info1[0]][7]) > abs(OI_Data[row_info2[0]][7]):
		if abs(OI_Data[row_info1[0]][7]) > abs(OI_Data[row_info3[0]][7]):
			max_oi_call=OI_Data[row_info1[0]][7]
			last_day_call_oi=OI_Data[row_info1[0]][1]
			indx_ce=row_info1
		else:
			max_oi_call=OI_Data[row_info3[0]][7]
			last_day_call_oi=OI_Data[row_info3[0]][1]
			indx_ce=row_info3
	else:
		if abs(OI_Data[row_info2[0]][7]) > abs(OI_Data[row_info3[0]][7]):
			max_oi_call=OI_Data[row_info2[0]][7]
			last_day_call_oi=OI_Data[row_info2[0]][1]
			indx_ce=row_info2
		else:
			max_oi_call=OI_Data[row_info3[0]][7]
			last_day_call_oi=OI_Data[row_info3[0]][1]
			indx_ce=row_info3

	if abs(OI_Data[row_info4[0]][8]) > abs(OI_Data[row_info5[0]][8]):
		if abs(OI_Data[row_info4[0]][8]) > abs(OI_Data[row_info6[0]][8]):
			max_oi_put=OI_Data[row_info4[0]][8]
			last_day_put_oi=OI_Data[row_info4[0]][2]
			indx_pe=row_info4
		else:
			max_oi_put=OI_Data[row_info6[0]][8]
			last_day_put_oi=OI_Data[row_info6[0]][2]
			indx_pe=row_info6
	else:
		if abs(OI_Data[row_info5[0]][8]) > abs(OI_Data[row_info6[0]][8]):
			max_oi_put=OI_Data[row_info5[0]][8]
			last_day_put_oi=OI_Data[row_info5[0]][2]
			indx_pe=row_info5
		else:
			max_oi_put=OI_Data[row_info6[0]][8]
			last_day_put_oi=OI_Data[row_info6[0]][2]
			indx_pe=row_info6
	return max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe

def set_data_for_max_change_in_oi(OI_Data,selected_check):
	A=np.array(OI_Data)
	row_info1=np.where(A==selected_check[0])[0].tolist()
	row_info2=np.where(A==selected_check[1])[0].tolist()
	row_info3=np.where(A==selected_check[2])[0].tolist()
	row_info4=np.where(A==selected_check[3])[0].tolist()
	row_info5=np.where(A==selected_check[4])[0].tolist()
	row_info6=np.where(A==selected_check[5])[0].tolist()

	if abs(OI_Data[row_info1[0]][3]) > abs(OI_Data[row_info2[0]][3]):
		if abs(OI_Data[row_info1[0]][3]) > abs(OI_Data[row_info3[0]][3]):
			max_oi_call_chng=OI_Data[row_info1[0]][7]
			last_day_call_oi_chng=OI_Data[row_info1[0]][1]
			indx_ce_chng=row_info1
		else:
			max_oi_call_chng=OI_Data[row_info3[0]][7]
			last_day_call_oi_chng=OI_Data[row_info3[0]][1]
			indx_ce_chng=row_info3
	else:
		if abs(OI_Data[row_info2[0]][3]) > abs(OI_Data[row_info3[0]][3]):
			max_oi_call_chng=OI_Data[row_info2[0]][7]
			last_day_call_oi_chng=OI_Data[row_info2[0]][1]
			indx_ce_chng=row_info2
		else:
			max_oi_call_chng=OI_Data[row_info3[0]][7]
			last_day_call_oi_chng=OI_Data[row_info3[0]][1]
			indx_ce_chng=row_info3

	if abs(OI_Data[row_info4[0]][4]) > abs(OI_Data[row_info5[0]][4]):
		if abs(OI_Data[row_info4[0]][4]) > abs(OI_Data[row_info6[0]][4]):
			max_oi_put_chng=OI_Data[row_info4[0]][8]
			last_day_put_oi_chng=OI_Data[row_info4[0]][2]
			indx_pe_chng=row_info4
		else:
			max_oi_put_chng=OI_Data[row_info6[0]][8]
			last_day_put_oi_chng=OI_Data[row_info6[0]][2]
			indx_pe_chng=row_info6
	else:
		if abs(OI_Data[row_info5[0]][4]) > abs(OI_Data[row_info6[0]][4]):
			max_oi_put_chng=OI_Data[row_info5[0]][8]
			last_day_put_oi_chng=OI_Data[row_info5[0]][2]
			indx_pe_chng=row_info5
		else:
			max_oi_put_chng=OI_Data[row_info6[0]][8]
			last_day_put_oi_chng=OI_Data[row_info6[0]][2]
			indx_pe_chng=row_info6
	return max_oi_call_chng,last_day_call_oi_chng,indx_ce_chng,max_oi_put_chng,last_day_put_oi_chng,indx_pe_chng

def ratio_125_check(r,r1,r2,indx,indx_chng,s1,s2):
	cumulative=False
	ratio= abs(r1)/abs(r2)
	global max_pcr_cpr_ratio
	if ratio>=r:
		cumulative=True
		max_pcr_cpr_ratio = max(max_pcr_cpr_ratio,ratio)
	else:
		if indx == indx_chng:
			cumulative=False
		else:
			if s1/s2 >=r:
				cumulative=True
				print("By Change")
			else:
				cumulative=False
	return cumulative									

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

	def extract_info(sp1,sp2,time):
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
		return row1,row2,sl

	if side=='PE.NFO':
		selling_sp = float(a[4]) - (float(a[4])%50) -200
		buying_sp=selling_sp - 100
	else:
		selling_sp= float(a[4])  + (50 - float(a[4])%50) + 200
		buying_sp=selling_sp+100	
	sp1=prefix+str(int(selling_sp))+side
	sp2=prefix+str(int(buying_sp))+side
	row1,row2,sl=extract_info(sp1,sp2,time)

	if sl>10.5:
		if side=='PE.NFO':
			selling_sp=float(a[4]) - (float(a[4])%50) -250
			buying_sp=selling_sp - 100
		else:
			selling_sp= float(a[4])  + (50 - float(a[4])%50) + 250
			buying_sp=selling_sp+100
	elif sl<5:
		if side=='PE.NFO':
			selling_sp=float(a[4]) - (float(a[4])%50) -150
			buying_sp=selling_sp - 100
		else:
			selling_sp= float(a[4])  + (50 - float(a[4])%50) + 150
			buying_sp=selling_sp+100
	sp1=prefix+str(int(selling_sp))+side
	sp2=prefix+str(int(buying_sp))+side
	row1,row2,sl=extract_info(sp1,sp2,time)			
				
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
		if (close1-close2) >= (sl*2):
			print("--------------------StopLoss Hit---------------------------------")
		t=t+1

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
		a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		
		"""Setting Strike price for day range from -300 to + 300"""
		Strike_Price_Set=strike_price_for_data(a)
			
		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(Strike_Price_Set)

		"""Setting Strike Price For Day"""
		output_closing_time = output_date + " 093000"
		selected_strike_price = setting_strike_price(output_closing_time,[])
		print(selected_strike_price)

		"""Setting OI Data till 9:30 , Strike Price , Previous day OI IN Call and Put , 9:30 Clock OI of Call and Put"""
		length=int(len(Strike_Price_Set))
		OI_Data = [[0] * 9 for _ in range(length)]
		OI_Data_15min=[[0] * 9 for _ in range(length)]
		OI_Data,OI_Data_15min = setting_oi_change_data(length,filter_based_on_sp,selected_strike_price,OI_Data,OI_Data_15min)	
		# for rows in OI_Data:
		# 		print(rows)
		# print("--------------------------------------------------------------------------------")
		B=np.array(OI_Data_15min)
		first=True	
		trade=False
		crossover_by_pe=False
		crossover_by_ce=False
		time_str = '09:30:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		time_of_crossover=''
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

		while time_obj.time() < datetime.strptime('14:55:59', '%H:%M:%S').time():
			print(time_obj.strftime('%H:%M:%S'))

			"""Data Update on 1min basis"""
			OI_Data=update_oi_data(length,filter_based_on_sp,selected_strike_price,OI_Data,time_obj.time())

			"""Setting Data of Selected strike price for data collection"""
			max_oi_call,last_day_call_oi,indx_ce,max_oi_put,last_day_put_oi,indx_pe= set_data_for_max_oi(OI_Data,selected_strike_price)

			"""Setting data based on Change in OI """
			max_oi_call_chng,last_day_call_oi_chng,indx_ce_chng,max_oi_put_chng,last_day_put_oi_chng,indx_pe_chng= set_data_for_max_change_in_oi(OI_Data,selected_strike_price)

			"""Setiing crossover condition """			
			if last_day_call_oi > last_day_put_oi:
				if max_oi_put > max_oi_call:
					print("crossover_by_pe")
					crossover_by_pe=True					
					if first:
						time_of_crossover=time_obj
						first=False				
				elif crossover_by_pe:
					print("Again Crossover by call")
					time_of_crossover=time_obj
					crossover_by_ce=True
					crossover_by_pe=False				
			else:
				if max_oi_call > max_oi_put:
					print("crossover_by_ce")
					crossover_by_ce=True
					if first:
						time_of_crossover=time_obj
						first=False
				elif crossover_by_ce:
					print("Again Crossover by Put")
					crossover_by_pe=True
					crossover_by_ce=False
					time_of_crossover=time_obj

			"""pcr and cpr ratio 125%"""
			if crossover_by_pe and trade==False:
				max_change_ce=abs(max_oi_call_chng - last_day_call_oi_chng)
				max_change_pe=abs(max_oi_put_chng - last_day_put_oi_chng)
				Cumulative_for_PE = ratio_125_check(1.2,max_oi_put,max_oi_call,indx_ce,indx_ce_chng,max_oi_put_chng,max_oi_call_chng)
				if Cumulative_for_PE:
					print("PCR Ratio")
			if crossover_by_ce and trade==False:
				max_change_ce=abs(max_oi_call_chng - last_day_call_oi_chng)
				max_change_pe=abs(max_oi_put_chng - last_day_put_oi_chng)
				Cumulative_for_CE = ratio_125_check(1.2,max_oi_call,max_oi_put,indx_pe,indx_pe_chng,max_oi_call_chng,max_oi_put_chng)
				if Cumulative_for_CE:
					print("CPR Ratio")	
			
			"""Reduction and Trade Point Setup"""
			if (Cumulative_for_CE and crossover_by_ce):
				if (OI_Data[indx_pe[0]][6]-OI_Data[indx_pe[0]][4] > 0):
					print("Put Reduces")
					if count==0:
						if time_of_crossover==time_obj:	
							time_int2=time_of_crossover - timedelta(minutes=5)
							a=nifty_data_after_format_change(time_int2,time_obj)
							trade_point=float(a[3])
							print(trade_point - 10)
							count=count+1
						else:
							a=nifty_data_after_format_change(time_of_crossover,time_obj)
							trade_point=float(a[3])
							print(trade_point - 10)
							count=count+1						
			
			if (Cumulative_for_PE and crossover_by_pe):
				if(OI_Data[indx_ce[0]][5]-OI_Data[indx_ce[0]][3] > 0):
					print("Call Reduces")
					if count1==0:
						if time_of_crossover.time()==time_obj.time():
							time_int2=time_of_crossover - timedelta(minutes=5)
							a=nifty_data_after_format_change(time_int2,time_obj)
							trade_point=float(a[2])
							print(trade_point + 10)
							count1=count1+1
						else:
							a=nifty_data_after_format_change(time_of_crossover,time_obj)
							trade_point=float(a[2])
							print(trade_point + 10)
							count1=count1+1						

			"""Trade Initiation"""
			if (Cumulative_for_PE and crossover_by_pe) and count1==1 and trade==False:
				if time_obj < (time_of_crossover +  timedelta(minutes=90)):
					print("Take a Trade if Price Point goes above " + str(trade_point+10))
					time_int2=time_obj + timedelta(minutes=2)
					a=nifty_data_after_format_change(time_of_crossover,time_int2)
					if a==['']:
						print("Ignore Once")
					else:	
						if (trade_point + 10) < float(a[4]):
							print("PE Bech Do")
							row1,row2,sl=trade_initiate(output_date,a,'PE.NFO',time_obj.time())
							trade=True
							trade_side='PUT'
							trade_data.append(row1)
							trade_data.append(row2)
							print("Difference : " + str(sl))

				else:
					print("Trade Got Delayed")

			if (Cumulative_for_CE and crossover_by_ce) and count==1 and trade==False:
				if time_obj < ( time_of_crossover +  timedelta(minutes=90)):
					print("Take a Trade if Price Point goes below " + str(trade_point-10))
					time_int2=time_obj + timedelta(minutes=2)
					a=nifty_data_after_format_change(time_of_crossover,time_int2)
					if a==['']:
						print("Ignore once in a while")
					else:	
						if (trade_point - 10) > float(a[4]):
							print("CE Bech Do")
							row1,row2,sl=trade_initiate(output_date,a,'CE.NFO',time_obj.time())
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
					reversal_point_initiated=ratio_125_check(1.8,max_oi_put,max_oi_call,indx_ce,indx_ce_chng,1,1)
					if (reversal_point_initiated) and square_off==False:
						time_int2=time_obj - timedelta(minutes=5)
						a=nifty_data_after_format_change(time_int2,time_obj)
						print("Square of position below :" + str((float(a[4]))-10))
						trade_point=float(a[4])
						reversal_point_initiated_time=time_obj
						square_off=True

				elif trade_side=='CALL':
					reversal_point_initiated=ratio_125_check(1.8,max_oi_call,max_oi_put,indx_pe,indx_pe_chng,1,1)
					if (reversal_point_initiated) and square_off==False:
						time_int2=time_obj - timedelta(minutes=5)
						a=nifty_data_after_format_change(time_int2,time_obj)
						print("Square off Position above :" + str((float(a[4]))+10))
						trade_point=float(a[4])
						reversal_point_initiated_time=time_obj
						square_off=True	
			
			if square_off:
				if trade_side=='PUT':
					df = pd.read_csv(path)
					if time_obj < (reversal_point_initiated_time + timedelta(minutes=30)):
						time_int2=time_obj - timedelta(minutes=2)
						a=nifty_data_after_format_change(time_int2,time_obj)
						print("Square Off Trade if Price Point goes below " + str(trade_point-10))
						if a==['']:
							print("Ignore Once")
						else:	
							if trade_point-10 > float(a[3]):
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
						a=nifty_data_after_format_change(time_int2,time_obj)
						print("Square Off Trade if Price Point goes below " + str(trade_point+10))
						if a==['']:
							print("Ignore Once")
						else:	
							if trade_point+10 < float(a[2]):
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
						

			"""Shifting Of Selected Strike Price"""
			time_int = int(str(time_obj.time()).replace(':', ''))
			formatted_num = '{:06d}'.format(time_int)
			output_closing_time=output_date + " "+str(formatted_num)
			selected_check1=setting_strike_price(output_closing_time,selected_strike_price)
			if selected_check1!=selected_strike_price:
				selected_strike_price=selected_check1
				print(selected_check1)

			time_obj += timedelta(minutes=m)

		for rows in trade_data:
			writer.writerow(rows)
		print(max_drawdown)
		print(max_pcr_cpr_ratio)
		max_drawdown=0
		max_pcr_cpr_ratio=0
		



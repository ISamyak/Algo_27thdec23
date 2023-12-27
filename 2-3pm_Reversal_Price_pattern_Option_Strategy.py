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
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2021/ex-date/1_4/A'
nifty_path = './Nirmal_Fincap/Nifty/2021/2021/'
n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

prefix=" "
candle=1
max_drawdown=0
files = os.listdir(folder_path)
filepath=folder_path+'/Trade.csv'


# def date_from_file_name(i):
# 	return i[17:25]

def date_from_file_name(i):
	return i[10:20]

def day_from_date(date):
	date_obj = datetime.strptime(date,'%d-%m-%Y')
	return date_obj.strftime('%A')

# def day_from_date(date):
# 	date_obj = datetime.strptime(date,'%d%m%Y')
# 	return date_obj.strftime('%A')

def getting_filtered_data_from_excel(date,m,n):
	df1 = pd.read_csv(n_path)
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%Y%m%d'
	date=date_object.strftime(output_format)
	filtered_data = df1.loc[(df1['Date']== int(date))][m:n]
	filtered_data=filtered_data.iloc[::3]
	return filtered_data


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

# def getting_nifty_data_from_excel(date,m,n,ret=False):
# 	a1=[]
# 	df1 = pd.read_csv(n_path)
# 	original_format = '%d%m%Y'
# 	date_object = datetime.strptime(date, original_format)
# 	output_format = '%d/%m/%Y'
# 	date=date_object.strftime(output_format)
# 	d=date.split('/')
# 	dat=int(str(int(d[0]))+str(((d[1])))+str(int(d[2])))
# 	filtered_data = df1.loc[(df1['Date']==int(dat))][m:n]
# 	F=np.array(filtered_data)
# 	a1.append(filtered_data['Open'].iloc[0])
# 	a1.append(filtered_data['High'].max())
# 	candle_info_high=np.where(F[:,2]==a1[1])[0].tolist()

# 	a1.append(filtered_data['Low'].min())
# 	candle_info_low=np.where(F[:,3]==a1[2])[0].tolist()
# 	a1.append(filtered_data['Close'].iloc[-1])
# 	# print(candle_info_high[0])
# 	# print(candle_info_low[0])

# 	if ret:
# 		return a1,(n-m)-candle_info_high[0],(n-m)-candle_info_low[0]
# 	else:	
# 		return a1


def change_date_format(date):
	original_format = '%d-%m-%Y'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

# def change_date_format(date):
# 	original_format = '%d%m%Y'
# 	date_object = datetime.strptime(date, original_format)
# 	output_format = '%b %d %Y'
# 	return date_object.strftime(output_format)


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
	for i in sp[0:4]:
		temp=prefix+str(i)+"CE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1)
	for i in sp[4:]:
		temp=prefix+str(i)+"PE.NFO"
		# temp1=prefix+str(i)+"PE.NFO"
		filter_based_on_sp.append(temp)
		# filter_based_on_sp.append(temp1) 	
	return filter_based_on_sp	

def select_itm_strike_price(setting_sp_closeTime,selected_strike_price,m,n):
	a=getting_nifty_data_from_excel(date,m,n)
	# print(a)
	if a==['']:
		print("we can ignore")
		return selected_strike_price
	else:
		selected_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		
		if  a[3]%100 <=25:
			for_CE_STRIKE=int(a[3] - a[3]%100)
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=int(a[3] - a[3]%100) - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE=int(a[3] - a[3]%100)
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)

		elif a[3]%100 >= 75:
			for_CE_STRIKE=int(a[3] + (100 - a[3]%100))
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=int(a[3] + (100-a[3]%100)) - 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] + (100 - a[3]%100))
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] + (100-a[3]%100))+50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
		else:

			for_CE_STRIKE=int(a[3] - a[3]%100) + 50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE=int(a[3] - a[3]%100)
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-50
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
		
		selected_check_ce = selected_check_ce[::-1]		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check		

def getting_data_for_nearest_itm_atp_ltp(date,ITM_Table,sp):
	df = pd.read_csv(path)
	k=0
	for i in sp:
		filtered_data = df.loc[(df['Ticker']== i )]
		extracted_data = filtered_data.to_dict('records')
		a=0	
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

			ITM_Table[k][0]=i
			ITM_Table[k][1]=extracted_data[j]['Time']
			ITM_Table[k][2]=d
			k=k+1

	return ITM_Table			

def getting_data_for_sp_calculate_atp_ltp(date,Table,sp,LTP_ATP_Table,ITM_Table_CE_info,ITM_Table_PE_info):
	df = pd.read_csv(path)
	for j in range(len(sp)):
		filtered_data = df.loc[(df['Ticker']== sp[j] )]
		extracted_data = filtered_data.to_dict('records')
		a=0
		Table[j][0]=sp[j]

		mini=400
		mini_time=''
		mini_index_value=0
		alpha=0
		alpha_time=''
		for i in range(len(extracted_data[0:271])):
			if(extracted_data != []):
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
					if mini > d and i>151:
						a1=getting_nifty_data_from_excel(date,0,i)
						mini_index_value=a1[3]
						mini_time=extracted_data[i]['Time']
						mini=min(mini,d)
			else:		
				print("8th Wrong Data")

			# if "CE" in sp[j] and i>151 :
			# 	extracted_data1 = [row for row in ITM_Table_PE_info if (row[1] == extracted_data[i]['Time'] and row[0] == sp[j] )]
			# 	if extracted_data1!=[]:
			# 		z = d - extracted_data1[0][2]
			# 		if z>50 or z<-50:
			# 			if alpha_time=='':
			# 				alpha=z
			# 				alpha_time=extracted_data[i]['Time']
			
			# if "PE" in sp[j] and i>151:
			# 	extracted_data1 = [row for row in ITM_Table_CE_info if (row[1] == extracted_data[i]['Time'] and row[0] == sp[j] ) ]	
			# 	if extracted_data1!=[]:		
			# 		z = d - extracted_data1[0][2]
			# 		if z>50 or z<-50:
			# 			if alpha_time=='':
			# 				alpha=z
			# 				alpha_time=extracted_data[i]['Time']		

			LTP_ATP_Table[j][0]=extracted_data[i]['Ticker']
			LTP_ATP_Table[j][1]=extracted_data[i]['Time']
			LTP_ATP_Table[j][2]=extracted_data[i]['Close']
			LTP_ATP_Table[j][3]=extracted_data[i]['Volume']
			LTP_ATP_Table[j][4]=c
			LTP_ATP_Table[j][5]=a
			LTP_ATP_Table[j][6]=b
			LTP_ATP_Table[j][7]=d


			Table[j][1]=d
			Table[j][2]=mini
			Table[j][3]=mini_time
			if mini > -20:
				Table[j][4]=mini-10
			else:
				Table[j][4]=mini-5
			Table[j][6]=mini_index_value
			# Table[j][8]=alpha
			# Table[j][9]=alpha_time

		"""For Oppposite side"""
		if "CE" in sp[j]:
			modified_string = sp[j].replace("CE", "PE")
		else:
			modified_string= sp[j].replace("PE", "CE")
		filtered_data = df.loc[(df['Ticker']== modified_string )]
		extracted_data = filtered_data.to_dict('records')
		a=0
		# Table[j][7]=modified_string

		mini=200
		mini_time=''
		mini_index_value=0
		for i in range(len(extracted_data[0:271])):
			if(extracted_data != []):
				if i==0:
					c=extracted_data[i]['Volume']
					a=extracted_data[i]['Volume']*extracted_data[i]['Close']
					b=a/c
					d1=extracted_data[i]['Close']/b-1
				else:
					c=extracted_data[i]['Volume']+c
					a=a+extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d1=(extracted_data[i]['Close']/b-1)*100
					if mini > d1:
						a1=getting_nifty_data_from_excel(date,0,i)
						mini_index_value=a1[3]

					mini=min(mini,d1)
			else:
				print("8th Wrong Data")

			LTP_ATP_Table[j][8]=extracted_data[i]['Ticker']
			LTP_ATP_Table[j][9]=extracted_data[i]['Time']
			LTP_ATP_Table[j][10]=extracted_data[i]['Close']
			LTP_ATP_Table[j][11]=extracted_data[i]['Volume']
			LTP_ATP_Table[j][12]=c
			LTP_ATP_Table[j][13]=a
			LTP_ATP_Table[j][14]=b
			LTP_ATP_Table[j][15]=d1

			Table[j][5]=d+d1		

	return Table,LTP_ATP_Table

def update_data_atp_ltp(date,Table,sp,LTP_ATP_Table,time,Trade):
	df = pd.read_csv(path)
	for j in range(len(sp)):
		filtered_data = df.loc[(df['Ticker']== sp[j] )  & (df['Time'] == str(time)) ]
		extracted_data = filtered_data.to_dict('records')
		for i in range(len(extracted_data)):
			if(extracted_data != []):
				c=LTP_ATP_Table[j][4]+extracted_data[i]['Volume']
				a= LTP_ATP_Table[j][5] + extracted_data[i]['Volume']*extracted_data[i]['Close']	
				b=a/c
				d=(extracted_data[i]['Close']/b-1)*100
			else:
				if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
					print("8th Wrong Data")

			LTP_ATP_Table[j][0]=extracted_data[i]['Ticker']
			LTP_ATP_Table[j][1]=extracted_data[i]['Time']
			LTP_ATP_Table[j][2]=extracted_data[i]['Close']
			LTP_ATP_Table[j][3]=extracted_data[i]['Volume']
			LTP_ATP_Table[j][4]=c
			LTP_ATP_Table[j][5]=a	
			LTP_ATP_Table[j][6]=b	
			LTP_ATP_Table[j][7]=d

			if "CE" in sp[j]:
				modified_string = sp[j].replace("CE", "PE")
			else:
				modified_string= sp[j].replace("PE", "CE")
			
			filtered_data = df.loc[(df['Ticker']== modified_string ) & (df['Time'] == str(time))  ]
			extracted_data = filtered_data.to_dict('records')

			for i in range(len(extracted_data)):
				if(extracted_data != []):
					c=extracted_data[i]['Volume']+LTP_ATP_Table[j][12]
					a=  LTP_ATP_Table[j][13] +extracted_data[i]['Volume']*extracted_data[i]['Close']	
					b=a/c
					d1=(extracted_data[i]['Close']/b-1)*100
				else:
					if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
						print("8th Wrong Data")
			if extracted_data == []:
				xyz=0			 
			else:	
				LTP_ATP_Table[j][8]=modified_string
				LTP_ATP_Table[j][9]=str(time)
				LTP_ATP_Table[j][10]=extracted_data[i]['Close']
				LTP_ATP_Table[j][11]=extracted_data[i]['Volume']
				LTP_ATP_Table[j][12]=c
				LTP_ATP_Table[j][13]=a
				LTP_ATP_Table[j][14]=b
				LTP_ATP_Table[j][15]=d1

				
				Table[j][1]=d

				Table[j][5]=d+d1

	return Table,LTP_ATP_Table		

def trade_initiate(date,tick,time):
	df = pd.read_csv(path)

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
		
		# a=getting_ohlc_nifty(output_opening_time,output_closing_time)
		a1=getting_nifty_data_from_excel(date,0,378)
		
		"""Setting Strike price for day range from -300 to + 300"""
		Strike_Price_Set=strike_price_for_data(a1)

		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
		filter_based_on_sp=setting_prefix_suffix_for_excel_data(Strike_Price_Set)	

		"""Setting Strike Price For Day"""
		output_closing_time = output_date + " 134500"
		selected_itm_Sp = select_itm_strike_price(output_closing_time,[],0,286)
		print(selected_itm_Sp)
		Table = [[0] * 8 for _ in range(len(selected_itm_Sp))]
		LTP_ATP_Table=[[0] * 16 for _ in range(len(selected_itm_Sp))]
		simple_filter_sp=setting_prefix_suffix_for_excel_data(selected_itm_Sp)
		ITM_Table_CE_info=[[0] * 3 for _ in range(378*3)]
		ITM_Table_PE_info=[[0] * 3 for _ in range(378*3)]

		ITM_Table_CE_info=getting_data_for_nearest_itm_atp_ltp(date,ITM_Table_CE_info,simple_filter_sp[0:3])
		ITM_Table_PE_info=getting_data_for_nearest_itm_atp_ltp(date,ITM_Table_PE_info,simple_filter_sp[5:])		
		Table,LTP_ATP_Table=getting_data_for_sp_calculate_atp_ltp(date,Table,simple_filter_sp,LTP_ATP_Table,ITM_Table_CE_info,ITM_Table_PE_info)
		print(" Ticker					   LTP/ATP@1:45				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE	Index Index@Trade  ")	
		for rows in Table:
			print(rows)
		print("-------------------------------------------------------------------------------")

		time_str = '13:45:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		n=272
		Trade=''
		Trade1=''
		trade_data=[]
		sl=0
		point1=False
		point2=False
		point3=False

		point11=False
		point21=False
		point31=False

		min_atp_ltp=200
		min_atp_ltp1=200
		new_Trade=False
		new_Trade1=False

		tick=0
		tick0=0
		tick1=0
		tick2=0
		min_atp_ltp_new=200
		min_atp_ltp_new1=200

		if Table[2][1]>=100 and Table[2][1] <=200:
			k=100
			m=50
			l=80
		elif Table[2][1]>=200:
			k=200
			m=80
			l=120
		else:
			k=50
			m=25
			l=40

		if Table[5][1]>=100 and Table[5][1]<=200:
			k1=100
			m1=50
			l1=80
		elif Table[5][1]>=200:
			k1=200
			m1=80
			l1=120
		else:
			k1=50
			m1=25
			l1=40		

		while time_obj.time() < datetime.strptime('15:29:59', '%H:%M:%S').time():
			print(time_obj.time())
			time_obj1 = time_obj
			Get_point=False
			Get_point1=False
			
			if(Table[1][1] > 0 or Table[2][1]>0) and (Trade==''):
				print("I am here")

				# if Table[2][1]>5 and (Table[2][1] - Table[5][1] >= k):
				# 	print("Point 1 itm is Here")
				# 	print(time_obj1.time())
				# 	point1=True	
				# 	while Get_point==False and time_obj1.time() > datetime.strptime('09:16:59', '%H:%M:%S').time():
						
				# 		extracted_data1 = [row for row in ITM_Table_CE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[2][0]) ]
				# 		min_atp_ltp=min(min_atp_ltp,extracted_data1[0][2])
				# 		extracted_data2 = [row for row in ITM_Table_PE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[5][0]) ]
				# 		if extracted_data1==[] or extracted_data2==[]:
				# 			time_obj1 -= timedelta(minutes=candle)	
				# 			continue
				# 		if extracted_data1[0][2] - extracted_data2[0][2] <=m and point2==False:
				# 			print("Point 2 itm is here")
				# 			point2=True
				# 			print(time_obj1.time())
				# 		if point2 and (extracted_data1[0][2] - extracted_data2[0][2] >=l) and point3==False:
				# 			print("Point 3 itm is here")
				# 			point3=True
				# 			print(time_obj1.time())
				# 			print(min_atp_ltp)
				# 			if min_atp_ltp<-20:
				# 				min_atp_ltp=min_atp_ltp-10
				# 			else:
				# 				min_atp_ltp=min_atp_ltp-5		
				# 			Trade='CE'
				# 			Get_point=True
						
				# 		time_obj1 -= timedelta(minutes=candle)
				time_obj1=time_obj
				if Table[1][1]>5 and (Table[1][1] - Table[5][1] >= k):
					print("Point 11 itm is Here")
					print(time_obj1.time())
					point11=True
					while Get_point1==False and time_obj1.time() > datetime.strptime('09:16:59', '%H:%M:%S').time():

						extracted_data1 = [row for row in ITM_Table_CE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[1][0]) ]
						if extracted_data1==[]:
							time_obj1 -= timedelta(minutes=candle)	
							continue
						min_atp_ltp1=min(min_atp_ltp1,extracted_data1[0][2])
						extracted_data2 = [row for row in ITM_Table_PE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[5][0]) ]
						if extracted_data1==[] or extracted_data2==[]:
							time_obj1 -= timedelta(minutes=candle)	
							continue
						if extracted_data1[0][2] - extracted_data2[0][2] <=m and point21==False:
							print("Point 21 itm is here")
							point21=True
							print(time_obj1.time())
						if point21 and extracted_data1[0][2] - extracted_data2[0][2] >=l and point31==False:
							print("Point 31 itm is here")
							point31=True
							print(time_obj1.time())
							print(min_atp_ltp1)
							if min_atp_ltp1<-20:
								min_atp_ltp1=min_atp_ltp1-10
							else:
								min_atp_ltp1=min_atp_ltp1-5		
							Trade1='CE'
							Get_point1=True
						
						time_obj1 -= timedelta(minutes=candle)		

					if point31==False:
						point11=False
						point21=False
		
			if(Table[5][1] > 0 or Table[6][1]>0) and (Trade==''):
				print("I am here")
				# if Table[5][1]>5 and (Table[5][1] - Table[2][1] >= k1):
				# 	print("Point 1 itm pe is Here")
				# 	print(time_obj1.time())
				# 	point1=True
				# 	while Get_point== False and time_obj1.time() > datetime.strptime('09:16:59', '%H:%M:%S').time():
				# 		extracted_data1 = [row for row in ITM_Table_PE_info if (row[0]==Table[5][0] and row[1]==str(time_obj1.time())) ]
						
				# 		min_atp_ltp=min(min_atp_ltp,extracted_data1[0][2])
				# 		extracted_data2 = [row for row in ITM_Table_CE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[2][0]) ]
						
				# 		if extracted_data1==[] or extracted_data2==[]:
				# 			time_obj1 -= timedelta(minutes=candle)	
				# 			continue
				# 		if extracted_data1[0][2] - extracted_data2[0][2] <=m1 and point2==False:
				# 			print("Point 2 itm pe is here")
				# 			point2=True
				# 			print(time_obj1.time())
				# 		if point2 and extracted_data1[0][2] - extracted_data2[0][2] >=l1 and point3==False:
				# 			print("Point 3 itm pe is here")
				# 			point3=True
				# 			print(time_obj1.time())
				# 			print(min_atp_ltp)
				# 			if min_atp_ltp<-20:
				# 				min_atp_ltp=min_atp_ltp-10
				# 			else:
				# 				min_atp_ltp=min_atp_ltp-5
				# 			Trade='PE'
				# 			Get_point=True

				# 		time_obj1 -= timedelta(minutes=candle)	

				time_obj1=time_obj
				if Table[6][1]>5 and (Table[6][1] - Table[2][1] >= k1):
					print("Point 1 pe is Here")
					print(time_obj1.time())
					point1=True
					while Get_point1== False and time_obj1.time() > datetime.strptime('09:16:59', '%H:%M:%S').time():
						extracted_data1 = [row for row in ITM_Table_PE_info if (row[0]==Table[6][0] and row[1]==str(time_obj1.time())) ]
						if extracted_data1==[]:
							time_obj1 -= timedelta(minutes=candle)	
							continue
						min_atp_ltp=min(min_atp_ltp,extracted_data1[0][2])
						extracted_data2 = [row for row in ITM_Table_CE_info if (row[1] == str(time_obj1.time()) and row[0]==Table[2][0]) ]
						if extracted_data1==[] or extracted_data2==[]:
							time_obj1 -= timedelta(minutes=candle)	
							continue
						if extracted_data1[0][2] - extracted_data2[0][2] <=m1 and point2==False:
							print("Point 21 pe is here")
							point2=True
							print(time_obj1.time())
						if point2 and extracted_data1[0][2] - extracted_data2[0][2] >=l1 and point3==False:
							print("Point 31 pe is here")
							point3=True
							print(time_obj1.time())
							print(min_atp_ltp)
							if min_atp_ltp<-20:
								min_atp_ltp=min_atp_ltp-10
							else:
								min_atp_ltp=min_atp_ltp-5
							Trade1='PE'
							Get_point1=True

						time_obj1 -= timedelta(minutes=candle)

					if point3==False:
						point1=False
						point2=False			

			
			
			# if Trade=='CE' and trade_data==[]:
			# 	if (min_atp_ltp) > LTP_ATP_Table[2][7]:

			# 		column_5 = [row[5] for row in Table]
			# 		print(column_5)
			# 		value=sorted(column_5[1:7])[:1]
					
			# 		# if Table[2][5]==value[0]:
			# 		if Table[2][5] < Table[5][5]:
			# 			print("Trade Call")
			# 			print(time_obj.time())
			# 			print(Table[2][0])
			# 			print(LTP_ATP_Table[2][0])
			# 			print(n)
			# 			row,sl=trade_initiate(date,Table[2][0],time_obj.time())
			# 			trade_data.append(row)
			# 			a1=getting_nifty_data_from_excel(date,0,n)
			# 			Table[2][7]=a1[3]
			# 			Table[1][7]=a1[3]
			# 			Trade='CE'

			if Trade1=='CE' and trade_data==[]:
				if (min_atp_ltp1) > LTP_ATP_Table[1][7]:

					column_5 = [row[5] for row in Table]
					print(column_5)
					value=sorted(column_5[1:7])[:1]
					# if Table[1][5]==value[0]:
					if Table[1][5] < Table[6][5]:
						print("Trade Call")
						print(time_obj.time())
						print(Table[1][0])
						print(LTP_ATP_Table[1][7])
						print(n)
						row,sl=trade_initiate(date,Table[1][0],time_obj.time())
						trade_data.append(row)
						a1=getting_nifty_data_from_excel(date,0,n)
						Table[2][7]=a1[3]
						Table[1][7]=a1[3]
						Trade1='CE'			

			# if Trade=='PE' and trade_data==[]:
			# 	if (min_atp_ltp) > LTP_ATP_Table[5][7]:
	
			# 		column_5 = [row[5] for row in Table]
			# 		print(column_5)
			# 		value=sorted(column_5[1:7])[:1]
			# 		# if Table[5][5]==value[0]:
			# 		if Table[5][5] < Table[2][5]:
			# 			print("Trade Put")
			# 			print(time_obj.time())
			# 			print(Table[5][0])
			# 			print(LTP_ATP_Table[5][0])
			# 			print(n)
			# 			row,sl=trade_initiate(date,Table[5][0],time_obj.time())
			# 			trade_data.append(row)
			# 			a1=getting_nifty_data_from_excel(date,0,n)
			# 			Table[5][7]=a1[3]
			# 			Table[6][7]=a1[3]
			# 			Trade='PE'

			if Trade1=='PE' and trade_data==[]:
				if (min_atp_ltp) > LTP_ATP_Table[6][7]:
	
					column_5 = [row[5] for row in Table]
					print(column_5)
					value=sorted(column_5[1:7])[:1]
					# if Table[6][5]==value[0]:
					if Table[6][5] < Table[1][5]:
						print("Trade Put")
						print(time_obj.time())
						print(Table[6][0])
						print(LTP_ATP_Table[6][0])
						print(n)
						row,sl=trade_initiate(date,Table[6][0],time_obj.time())
						trade_data.append(row)
						a1=getting_nifty_data_from_excel(date,0,n)
						Table[5][7]=a1[3]
						Table[6][7]=a1[3]
						Trade1='PE'			
			
			if trade_data != []:
				sl_check(str(time_obj.time()),trade_data,sl,1)

			if Trade=='':
				point1=False
				point2=False
				point3=False
	

			time_obj += timedelta(minutes=candle)
			n=n+1
			# if time_obj.time() > datetime.strptime('14:01:59', '%H:%M:%S').time():
			# 	selected_itm_Sp1 = select_itm_strike_price(output_closing_time,[],0,n)

			# 	if selected_itm_Sp1 != selected_itm_Sp:
			# 		if (Table[1][1]>0 or Table[2][1]>0) and selected_itm_Sp[0]<selected_itm_Sp1[0]:
			# 			print("We cannot Ignore")
			# 		else:
			# 			pass

			"""-------------------------------------------------------------"""
			if time_obj.time() > datetime.strptime('13:46:59', '%H:%M:%S').time():
			# 	if Table[2][1]>5 and (Table[2][1] - Table[5][1] >= k) and tick==0:
			# 		if tick==0:
			# 			tick=tick+1
			# 			print("Point 3 in new call")
			# 			print(time_obj.time())

				

			# 	if tick==1 and (Table[2][1] - Table[5][1] <= m):
			# 		tick=tick+1
			# 		print("Point 2 in new call ")
			# 		print(time_obj.time())

			# 	if tick==2:
			# 		min_atp_ltp_new=min(min_atp_ltp_new,Table[2][1])	

			# 	if tick==2 and (Table[2][1] - Table[5][1] >= l):
			# 		tick=tick+1
			# 		print("Point 1 in new call")
			# 		print(time_obj.time())
			# 		tick=0
			# 		if trade_data==[]:
			# 			Trade='CE'
			# 			min_atp_ltp=min_atp_ltp_new
						

				"""-------------------------------------------------------------"""
				if Table[1][1]>5 and (Table[1][1] - Table[5][1] >= k) and tick0==0:
					if tick0==0:
						tick0=tick0+1
						print("Point 3 in new far call")
						print(time_obj.time())

				

				if tick0==1 and (Table[1][1] - Table[5][1] <= m):
					tick0=tick0+1
					print("Point 2 in new far call ")
					print(time_obj.time())

				if tick0==2:
					min_atp_ltp_new=min(min_atp_ltp_new,Table[1][1])	

				if tick0==2 and (Table[1][1] - Table[5][1] >= l):
					tick0=tick0+1
					print("Point 1 in new far call")
					print(time_obj.time())
					tick0=0
					if trade_data==[]:
						Trade1='CE'
						min_atp_ltp1=min_atp_ltp_new
						print(min_atp_ltp1)		

				
					

				"""-------------------------------------------------------------"""
				# if Table[5][1]>5 and (Table[5][1] - Table[2][1] >= k1) and tick1==0:
				# 	if tick1==0:
				# 		tick1=tick1+1
				# 		print("Point 3 in new pe")
				# 		print(time_obj.time())	

				# if tick1==1 and (Table[5][1] - Table[2][1] <= m1):
				# 	tick1=tick1+1
				# 	print("Point 2 in new pe ")
				# 	print(time_obj.time())

				# if tick1==2:
				# 	min_atp_ltp_new=min(min_atp_ltp_new,Table[5][1])		

				# if tick1==2 and (Table[5][1] - Table[2][1] >= l1):
				# 	tick1=tick1+1
				# 	print("Point 1 in new pe ")
				# 	print(time_obj.time())
				# 	tick1=0
				# 	if trade_data==[]:
				# 		Trade='PE'
				# 		min_atp_ltp=min_atp_ltp_new	


				"""-------------------------------------------------------------"""
				if Table[6][1]>5 and (Table[6][1] - Table[2][1] >= k1) and tick2==0:
					if tick2==0:
						tick2=tick2+1
						print("Point 3 in new far pe")
						print(time_obj.time())
						
				if tick2==1 and (Table[6][1] - Table[2][1] <= m1):
					tick2=tick2+1
					print("Point 2 in new far pe")
					print(time_obj.time())
				
				if tick2==2:
					min_atp_ltp_new1=min(min_atp_ltp_new1,Table[6][1])	

				if tick2==2 and (Table[6][1] - Table[2][1] >= l1):
					tick2=tick2+1
					print("Point 1 in new far pe")
					print(time_obj.time())
					tick2=0
					if trade_data==[]:
						Trade1='PE'
						min_atp_ltp=min_atp_ltp_new1
						print(min_atp_ltp)

			Table,LTP_ATP_Table=update_data_atp_ltp(date,Table,simple_filter_sp,LTP_ATP_Table,time_obj.time(),Trade)
			for rows in Table:
				print(rows)
			print("-------------------------------------------------------------------------------")						
			

		for rows in trade_data:
			writer.writerow(rows)

		print(" Ticker					   LTP/ATP@2				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE		Index 		Index@Trade  ")
		for rows in Table:
			print(rows)
		print(max_drawdown)
		print(min_atp_ltp)
		print(min_atp_ltp1)	
		max_drawdown=0
		print("-------------------------------------------------------------------------------")
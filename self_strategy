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
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2022/5/ex-date/'
nifty_path = './Nirmal_Fincap/Nifty/2022/'
n_path = nifty_path + 'data.csv'
# vix_path= nifty_path + 'vix.csv'

prefix=" "
m=1
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
			for_PE_STRIKE=int(a[3] - a[3]%100)
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 50
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
			for_PE_STRIKE = int(a[3] + (100 - a[3]%100))
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] + (100-a[3]%100))+50
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
			for_PE_STRIKE = int(a[3] - a[3]%100) + 50
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = int(a[3] - a[3]%100) + 100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 50
			selected_check_pe.append(for_PE_STRIKE)
		selected_check_ce = selected_check_ce[::-1]		
		selected_check = selected_check_ce + selected_check_pe
		return selected_check		

def getting_data_for_nearest_itm_atp_ltp(date,ITM_Table,sp):
	df = pd.read_csv(path)
	filtered_data = df.loc[(df['Ticker']== sp )]
	extracted_data = filtered_data.to_dict('records')
	a=0
	for i in range(len(extracted_data[0:286])):
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
		else:
			if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
				print("8th Wrong Data")

		ITM_Table[i][0]=sp
		ITM_Table[i][1]=extracted_data[i]['Time']
		ITM_Table[i][2]=d

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
		for i in range(len(extracted_data[0:286])):
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
					if mini > d and i>166:
						a1=getting_nifty_data_from_excel(date,0,i)
						mini_index_value=a1[3]
						mini_time=extracted_data[i]['Time']
						mini=min(mini,d)
			else:
				if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
					print("8th Wrong Data")

			if "CE" in sp[j] and i>166 :
				extracted_data1 = [row for row in ITM_Table_PE_info if row[1] == extracted_data[i]['Time']]
				if extracted_data1!=[]:
					z = d - extracted_data1[0][2]
					if z>50 or z<-50:
						if alpha_time=='':
							alpha=z
							alpha_time=extracted_data[i]['Time']
			
			if "PE" in sp[j] and i>166:
				extracted_data1 = [row for row in ITM_Table_CE_info if row[1] == extracted_data[i]['Time']]	
				if extracted_data1!=[]:		
					z = d - extracted_data1[0][2]
					if z>50 or z<-50:
						if alpha_time=='':
							alpha=z
							alpha_time=extracted_data[i]['Time']		

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
			Table[j][8]=alpha
			Table[j][9]=alpha_time

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
		for i in range(len(extracted_data[0:286])):
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
				if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
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



def update_data_atp_ltp(date,Table,sp,LTP_ATP_Table,time):
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
		output_closing_time = output_date + " 140000"
		selected_itm_Sp = select_itm_strike_price(output_closing_time,[],0,286)
		print(selected_itm_Sp)
		Table = [[0] * 10 for _ in range(len(selected_itm_Sp))]
		LTP_ATP_Table=[[0] * 16 for _ in range(len(selected_itm_Sp))]
		simple_filter_sp=setting_prefix_suffix_for_excel_data(selected_itm_Sp)
		ITM_Table_CE_info=[[0] * 3 for _ in range(286)]
		ITM_Table_PE_info=[[0] * 3 for _ in range(286)]

		ITM_Table_CE_info=getting_data_for_nearest_itm_atp_ltp(date,ITM_Table_CE_info,simple_filter_sp[1])
		ITM_Table_PE_info=getting_data_for_nearest_itm_atp_ltp(date,ITM_Table_PE_info,simple_filter_sp[4])		

		Table,LTP_ATP_Table=getting_data_for_sp_calculate_atp_ltp(date,Table,simple_filter_sp,LTP_ATP_Table,ITM_Table_CE_info,ITM_Table_PE_info)
		print(" Ticker					   LTP/ATP@2				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE	Index Index@Trade  Difference_50per		Time_of_Diff")	
		for rows in Table:
			print(rows)
		print("-------------------------------------------------------------------------------")

		time_str = '14:01:59'
		time_obj = datetime.strptime(time_str, '%H:%M:%S')
		n=287
		Trade=''
		Trade_Index=''
		flag=-1
		trade_data=[]
		sl=0
		while time_obj.time() < datetime.strptime('15:29:59', '%H:%M:%S').time():

			Table,LTP_ATP_Table=update_data_atp_ltp(date,Table,simple_filter_sp,LTP_ATP_Table,time_obj.time())
			
			if (Table[1][1]>0 or Table[0][1]>0) and Trade=='' :
				if Table[0][4] > LTP_ATP_Table[0][7] or Table[1][4] > LTP_ATP_Table[1][7]:
					if Table[1][4] > LTP_ATP_Table[1][7] and (Table[1][8]>50 or Table[1][8]<-50):
						Trade_Index=Table[1][0] 
						flag=1
					elif Table[0][4] > LTP_ATP_Table[0][7] and (Table[0][8]>50 or Table[0][8]<-50) :
						Trade_Index=Table[0][0]
						flag=0
						
					column_4 = [row[5] for row in Table]
					print(column_4)
					value=sorted(column_4)[:1]
					if Table[flag][5]==value[0]:
						print("Trade Call")
						print(time_obj.time())
						print(Trade_Index)
						print(n)
						row,sl=trade_initiate(date,Trade_Index,time_obj.time())
						trade_data.append(row)
						a1=getting_nifty_data_from_excel(date,0,n)
						Table[0][7]=a1[3]
						Table[1][7]=a1[3]
						Trade='CE'

			if (Table[4][1] > 0 or Table[5][1]>0) and Trade=='':
				if Table[4][4] > LTP_ATP_Table[4][7] or Table[5][4] > LTP_ATP_Table[5][7]:
					if Table[5][4] > LTP_ATP_Table[5][7] and (Table[5][8]>50 or Table[5][8]<-50) :
						Trade_Index=Table[5][0] 
						flag=5	
					elif Table[4][4] > LTP_ATP_Table[4][7] and (Table[4][8]>50 or Table[4][8]<-50) :
						Trade_Index=Table[4][0]
						flag=4
					

					column_4 = [row[5] for row in Table]
					print(column_4)
					value=sorted(column_4)[:1]
					if Table[flag][5]==value[0]:
						print("Trade Put")
						print(time_obj.time())
						print(Trade_Index)
						print(n)
						row,sl=trade_initiate(date,Trade_Index,time_obj.time())
						trade_data.append(row)
						a1=getting_nifty_data_from_excel(date,0,n)
						Table[4][7]=a1[3]
						Table[5][7]=a1[3]
						Trade='PE'
			
			if Trade != '':
				sl_check(str(time_obj.time()),trade_data,sl,1)

			time_obj += timedelta(minutes=m)
			n=n+1

		for rows in trade_data:
			writer.writerow(rows)

		print(" Ticker					   LTP/ATP@2				Min LTP/ATP 		Min_Time 		Add -10/-5 		Sum_CE_PE		Index 		Index@Trade  Difference_50per		Time_of_Diff")	
		for rows in Table:
			print(rows)
		
		print(max_drawdown)	
		max_drawdown=0
		print("-------------------------------------------------------------------------------")
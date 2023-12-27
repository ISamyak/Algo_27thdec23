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
#userID = "D0253246"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()
day=''


header = ['Date', 'Strike Price', 'Entry time', 'Closing Time' ,'Buy/Sell','Entry Price' , 'Closing Price' , 'Profit per lot']

# specify the path to the folder - GET LIST 
"""----------------- ---------------Setting Location--------------------------------------------------"""
folder_path = './Nirmal_Fincap/NIFTY_ADJ_OPT_2023/Jan/expiry2'
files = os.listdir(folder_path)

filepath=folder_path+'/Trade.csv'
# print the list of files
# print(files)

with open(filepath, 'w', newline='') as file:
	writer=csv.writer(file)
	writer.writerow(header)
	"""Back Testing Start from Here"""
	for i in files:
		path=folder_path+'/'+i
		"""----------------- ---------------Setting Date Format--------------------------------------------------"""
		date=i[10:20]
		print(date)
		date_obj = datetime.strptime(date,'%d-%m-%Y')
		day = date_obj.strftime('%A')
		print(day)
		"""Setting the date Format to extract data for that Particular Date"""
		original_format = '%d-%m-%Y'
		date_object = datetime.strptime(date, original_format)
		output_format = '%b %d %Y'
		output_string = date_object.strftime(output_format)
		output_opening_time = output_string+ " 090000"
		output_closing_time = output_string + " 153000"
		
		"""Get the Nifty Range of the Day for Setting Strike Price and Data filteration for the day"""
		response = xt.get_ohlc(
	    	exchangeSegment=xt.EXCHANGE_NSECM,
	    	exchangeInstrumentID=26000,
	    	startTime=output_opening_time,
	    	endTime=output_closing_time,
	    	compressionValue=450000)
		a=response['result']['dataReponse'].split('|')
		if a==['']:
			print("1st Wrong data")
		# print(a)
		# print("High:"+a[2] + "Low:" + a[3],end=" ")
		"""+300 AND -300 From day high and low data"""
		Strike_Price_Set=[]
		SP=int(float(a[3])) - (int(float(a[3])%50)) - 300
		while int(float(a[2]))+300 > SP:
			Strike_Price_Set.append(SP)
			# PRINT(SP,end=" ")
			SP=SP+50
		# print(Strike_Price_Set)

		"""Start Reading File and Filteration Process"""
		trade=False
		trade_data=[]
		df = pd.read_csv(path)
		# print(df)
		filter_based_on_sp=[]
		"""----------------- ---------------Setting Prefix and Suffix--------------------------------------------------"""
		prefix="NIFTY12JAN23"
		for i in Strike_Price_Set:
			temp=prefix+str(i)+"CE.NFO"
			temp1=prefix+str(i)+"PE.NFO"
			filter_based_on_sp.append(temp)
			filter_based_on_sp.append(temp1)
		# print(filter_based_on_sp)

		print("--------------------------------------------------------------------------------------------------------------------------")
		"""Setting Strike Price For Day"""
		setting_sp_startTime=output_string+" 091500"
		setting_sp_closeTime=output_string+" 093000"
		response = xt.get_ohlc(
	    	exchangeSegment=xt.EXCHANGE_NSECM,
	    	exchangeInstrumentID=26000,
	    	startTime=setting_sp_startTime,
	    	endTime=setting_sp_closeTime,
	    	compressionValue=450000)
		a=response['result']['dataReponse'].split('|')
		# print(a)
		if a==['']:
			print("2nd Wrong data")

		today = output_string
		original_datetime = datetime.strptime(today,output_format)
		previous_datetime = original_datetime - timedelta(days=1)
		if previous_datetime.weekday() >= 5:
			previous_datetime = previous_datetime - timedelta(days=previous_datetime.weekday() - 4)
		previous_date = previous_datetime.date()
		previous_date_str = previous_date.strftime(output_format)
		response = xt.get_ohlc(
		exchangeSegment=xt.EXCHANGE_NSECM,
		exchangeInstrumentID=26000,
		startTime=previous_date_str + " 090000",
		endTime=previous_date_str + " 160000",
		compressionValue=450000)
		a1=response['result']['dataReponse'].split('|')
		if a1==['']:
			print("3rd Wrong data")
		last_day_close=float(a1[4])
		# print(previous_date_str+ " : "+ str(last_day_close))
		if last_day_close > float(a[2]):
			# print("Gap Down")
			if (last_day_close - float(a[2]) >150):
				last_day_close=last_day_close-100
			elif (last_day_close - float(a[2]) > 100):
				last_day_close = last_day_close - 50	
				
			for_CE_STRIKE = float(a[3]) + abs((float(a[3])%50 - 50))
			for_PE_STRIKE = last_day_close - abs((last_day_close%50))
			print("-----------------------------------------------")
			print("Selected Strike price")
			selected_check=[]
			print("CE Strike " +"  "+"PE Strike")
			print(str(for_CE_STRIKE) + "  " +str(for_PE_STRIKE))
			selected_check.append(for_CE_STRIKE)
			selected_check.append(for_CE_STRIKE+50)
			selected_check.append(for_CE_STRIKE+100)
			# selected_check.append(for_CE_STRIKE+150)
			selected_check.append(for_PE_STRIKE)
			selected_check.append(for_PE_STRIKE-50)
			selected_check.append(for_PE_STRIKE-100)
			# selected_check.append(for_PE_STRIKE-150)
			print(str(for_CE_STRIKE + 50) + "  " +str(for_PE_STRIKE - 50))
			print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
			# print(str(for_CE_STRIKE + 150) + "  " +str(for_PE_STRIKE - 150))
			print("-----------------------------------------------")
		elif last_day_close < float(a[3]):
			# print("Gap Up")
			if (( float(a[3]) - last_day_close) >150):
				last_day_close=last_day_close+100
			elif (( float(a[3]) - last_day_close) > 100):
				last_day_close = last_day_close + 50
			for_CE_STRIKE = last_day_close + abs((last_day_close%50) - 50)
			for_PE_STRIKE = float(a[2]) - abs((float(a[2])%50))
			print("-----------------------------------------------")
			print("Selected Strike price")
			selected_check=[]
			print("CE Strike " +"  "+"PE Strike")
			print(str(for_CE_STRIKE) + "  " +str(for_PE_STRIKE))
			selected_check.append(for_CE_STRIKE)
			selected_check.append(for_CE_STRIKE+50)
			selected_check.append(for_CE_STRIKE+100)
			# selected_check.append(for_CE_STRIKE+150)
			selected_check.append(for_PE_STRIKE)
			selected_check.append(for_PE_STRIKE-50)
			selected_check.append(for_PE_STRIKE-100)
			# selected_check.append(for_PE_STRIKE-150)
			print(str(for_CE_STRIKE + 50) + "  " +str(for_PE_STRIKE - 50))
			print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
			# print(str(for_CE_STRIKE + 150) + "  " +str(for_PE_STRIKE - 150))
			print("-----------------------------------------------")
		else:
			for_CE_STRIKE = float(a[3]) + abs((float(a[3])%50 - 50))
			for_PE_STRIKE = float(a[2]) - abs((float(a[2])%50))
			print("-----------------------------------------------")
			print("Selected Strike price")
			selected_check=[]
			print("CE Strike " +"  "+"PE Strike")
			print(str(for_CE_STRIKE) + "  " +str(for_PE_STRIKE))
			selected_check.append(for_CE_STRIKE)
			selected_check.append(for_CE_STRIKE+50)
			selected_check.append(for_CE_STRIKE+100)
			# selected_check.append(for_CE_STRIKE+150)
			selected_check.append(for_PE_STRIKE)
			selected_check.append(for_PE_STRIKE-50)
			selected_check.append(for_PE_STRIKE-100)
			# selected_check.append(for_CE_STRIKE-150)
			print(str(for_CE_STRIKE + 50) + "  " +str(for_PE_STRIKE - 50))
			print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
			# print(str(for_CE_STRIKE + 150) + "  " +str(for_PE_STRIKE - 150))
			print("-----------------------------------------------")

		# print(selected_check)
		"""Setting OI Data till 9:25 , Strike Price , Previous day OI IN Call and Put , 9:25o Clock OI of Call and Put"""
		length=int(len(Strike_Price_Set))	
		OI_Data = [[0] * 9 for _ in range(length)]
		for i in range(length):
			"""Enter Strike price"""
			OI_Data[i][0]=Strike_Price_Set[(i)]

			"""Enter Call OI Data"""
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:15:59')]
			extracted_data = filtered_data.to_dict('records')
			if(extracted_data != []):
				OI_Data[i][1]=extracted_data[0]['Open Interest']
			else:
				if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
					print("4th Wrong Data")
			"""Enter Put OI Data"""
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:15:59')]
			extracted_data = filtered_data.to_dict('records')
			if(extracted_data != []):
				OI_Data[i][2]=extracted_data[0]['Open Interest']
			else:
				if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
					print("5th Wrong Data")		
			
			"""Enter Change OI Data in CE at 10:00"""
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == '09:29:59')]
			extracted_data = filtered_data.to_dict('records')
			if(extracted_data != []):
				OI_Data[i][3] =  OI_Data[i][1] - extracted_data[0]['Open Interest'] 
				# OI_Data[i][3]=extracted_data[0]['Open Interest']
			else:
				if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
					print("6th Wrong Data")
			"""Enter Change OI Data in PE at 10:00"""
			filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == '09:29:59')]
			extracted_data = filtered_data.to_dict('records')
			if(extracted_data != []):
				OI_Data[i][4] =  OI_Data[i][2] - extracted_data[0]['Open Interest'] 
				# OI_Data[i][4]=extracted_data[0]['Open Interest']	
			else:
				if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
					print("7th Wrong Data")
		
		A=np.array(OI_Data)			
		# for rows in OI_Data:
		# 	print(rows)
		Cumulative_for_PE=False
		Cumulative_for_CE = False
		time = ['09:44:59','09:59:59','10:14:59','10:29:59','10:44:59','10:59:59','11:14:59','11:29:59','11:44:59','11:59:59','12:14:59','12:29:59','12:44:59','12:59:59','13:14:59','13:29:59','13:44:59','13:59:59','14:14:59','14:29:59','14:44:59','14:59:59']
		time1= ['09:34:59', '09:39:59', '09:44:59', '09:49:59', '09:54:59', '09:59:59','10:00:59','10:04:59', '10:09:59', '10:14:59', '10:19:59', '10:24:59', '10:29:59', '10:34:59', '10:39:59', '10:44:59', '10:49:59', '10:54:59', '10:59:59', '11:04:59', '11:09:59', '11:14:59', '11:19:59', '11:24:59', '11:29:59', '11:34:59', '11:39:59', '11:44:59', '11:49:59', '11:54:59', '11:59:59', '12:04:59', '12:09:59', '12:14:59', '12:19:59', '12:24:59', '12:29:59', '12:34:59', '12:39:59', '12:44:59', '12:49:59', '12:54:59', '12:59:59', '13:04:59', '13:09:59', '13:14:59', '13:19:59', '13:24:59', '13:29:59', '13:34:59', '13:39:59', '13:44:59', '13:49:59', '13:54:59', '13:59:59', '14:04:59', '14:09:59', '14:14:59', '14:19:59', '14:24:59', '14:29:59', '14:34:59', '14:39:59', '14:44:59',]
		count = 0
		count1=0
		trade_point=0
		sl=0
		j=0
		trade_time=''
		last_trade=''
		while len(time)>j:
			print(time[j])
			for i in range(length):
				"""Enter Change OI Data in CE at 10:00"""
				filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2] ) & (df['Time'] == time[j])]
				extracted_data = filtered_data.to_dict('records')
				if(extracted_data != []):
					OI_Data[i][5]=OI_Data[i][3]
					OI_Data[i][3] = extracted_data[0]['Open Interest'] - OI_Data[i][1]
					OI_Data[i][7]=extracted_data[0]['Open Interest']
				else:
					if (True if float(filter_based_on_sp[i*2][12:17]) in selected_check else False):
						print("8th Wrong Data")	
				"""Enter Change OI Data in PE at 10:00"""
				filtered_data = df.loc[(df['Ticker']== filter_based_on_sp[i*2+1] ) & (df['Time'] == time[j])]
				extracted_data = filtered_data.to_dict('records')
				if(extracted_data != []):
					OI_Data[i][6]=OI_Data[i][4]
					OI_Data[i][4] =  extracted_data[0]['Open Interest'] - OI_Data[i][2]
					OI_Data[i][8] = extracted_data[0]['Open Interest']
				else:
					if (True if float(filter_based_on_sp[i*2+1][12:17]) in selected_check else False):
						print("9th Wrong Data")	  
			# print(time[j])
			for rows in OI_Data:
					print(rows)
			print("------------------------------------------------------------------------------------------------")		
			"""To get spot price"""		
			time_int = int(time[j].replace(':', ''))
			formatted_num = '{:06d}'.format(time_int-100)
			formatted_num1 = '{:06d}'.format(time_int)
			start=output_string + " "+str(formatted_num)
			end=output_string + " "+str(formatted_num1)
			response = xt.get_ohlc(
				exchangeSegment=xt.EXCHANGE_NSECM,
				exchangeInstrumentID=26000,
				startTime=output_opening_time,
				endTime=end,
				compressionValue=45000)
			a=response['result']['dataReponse'].split('|')
			# print(a)
			if a==['']:
				print("10th Wrong Data")
			"""Spot Price Cumulative Sum /  OI of +100 - 100 and Spot"""
			if (day=="Wednesday"  or day=="Tuesday" or day=="Monday"  or day=="Friday" or day=="Thursday"):
				if(float(a[4])%100>75):
					check_sp_hi_c=float(a[4]) + (100 - float(a[4])%100)
					# check_sp_hi_c1=check_sp_hi_c + 50
					# check_sp_hi_c2=check_sp_hi_c+100

					check_sp_hi_p=check_sp_hi_c
					# check_sp_hi_p1=check_sp_hi_p - 50
					# check_sp_hi_p2 = check_sp_hi_p - 100
				elif (float(a[4])%100<25):
					check_sp_hi_c = float(a[4]) - (float(a[4])%100)
					# check_sp_hi_c1 = check_sp_hi_c + 50
					# check_sp_hi_c2 = check_sp_hi_c+100

					check_sp_hi_p=check_sp_hi_c
					# check_sp_hi_p1=check_sp_hi_p- 50
					# check_sp_hi_p2 = check_sp_hi_p - 100
				else:
					check_sp_hi_c = float(a[4]) + (100 - float(a[4])%100)
					check_sp_hi_p = float(a[4]) - (float(a[4])%100)
					# if( (float(a[4])%50) > 25):
					# 	check_sp_hi_c= float(a[4]) + ( 50 -float(a[4])%50)
					# 	check_sp_hi_c1=check_sp_hi_c+50
					# 	check_sp_hi_c2=check_sp_hi_c+100
					# 	check_sp_hi_p=check_sp_hi_c
					# 	check_sp_hi_p1=check_sp_hi_p-50
					# 	check_sp_hi_p2=check_sp_hi_p-100
					# else:
					# 	check_sp_hi_c= float(a[4]) - (float(a[4])%50)
					# 	check_sp_hi_c1=check_sp_hi_c+50
					# 	check_sp_hi_c2=check_sp_hi_c+100
					# 	check_sp_hi_p=check_sp_hi_c
					# 	check_sp_hi_p1=check_sp_hi_p-50
					# 	check_sp_hi_p2=check_sp_hi_p-100
			
				row_info=np.where(A==check_sp_hi_p)[0].tolist()
				row_info2=np.where(A==check_sp_hi_c)[0].tolist()
				# row_info3=np.where(A==check_sp_hi_p1)[0].tolist()
				# row_info4=np.where(A==check_sp_hi_c1)[0].tolist()
				# row_info5=np.where(A==check_sp_hi_p2)[0].tolist()
				# row_info6=np.where(A==check_sp_hi_c2)[0].tolist()
				
				pe_sum_data=OI_Data[row_info[0]][2] + OI_Data[row_info[0]][4]
				ce_sum_data=OI_Data[row_info2[0]][1] + OI_Data[row_info2[0]][3]
				# pe_sum_data = max((OI_Data[row_info[0]][2] + OI_Data[row_info[0]][4]),(OI_Data[row_info3[0]][2] + OI_Data[row_info3[0]][4]),(OI_Data[row_info5[0]][2] + OI_Data[row_info5[0]][4]))
				# ce_sum_data = max((OI_Data[row_info2[0]][1] + OI_Data[row_info2[0]][3]),(OI_Data[row_info4[0]][1] + OI_Data[row_info4[0]][3]),(OI_Data[row_info6[0]][1] + OI_Data[row_info6[0]][3]))

				# print(pe_sum_data)
				# print(ce_sum_data)
				pcr=pe_sum_data/ce_sum_data
				cpr=ce_sum_data/pe_sum_data

				if pcr>=1.25:
					Cumulative_for_PE=True
					print("PCR Ratio Justified")
				else:
					Cumulative_for_PE=False	
				if cpr>=1.25:
					Cumulative_for_CE=True
					print("CPR Ratio Justified")
				else:
					Cumulative_for_CE=False	
				# if (pe_sum_data > ce_sum_data): 
				# 	Cumulative_for_PE = True
				# 	if((pe_sum_data*0.80) < ce_sum_data):
				# 		Cumulative_for_CE=True
				# 	else:
				# 		Cumulative_for_CE=False	
				# else:
				# 	Cumulative_for_CE = True
				# 	if((ce_sum_data*0.80) < pe_sum_data):
				# 		Cumulative_for_PE=True
				# 	else:
				# 		Cumulative_for_PE=False

			# elif(day==" "):
			# 	check_sp_hi_c = float(a[4]) + (100- float(a[4])%100)
			# 	check_sp_lo_c = check_sp_hi_c - 100
			# 	check_sp_hi_p= 0
			# 	check_sp_lo_p=0
			# 	if (float(a[4]) % 100 > 50):
			# 		check_sp_hi_p = float(a[4]) + (100- float(a[4])%100)
			# 		check_sp_lo_p = check_sp_hi_p - 100
			# 	else:
			# 		check_sp_hi_p = float(a[4]) - (float(a[4])%100)
			# 		check_sp_lo_p = check_sp_hi_p - 100
			# 	row_info=np.where(A==check_sp_hi_p)[0].tolist()
			# 	row_info1=np.where(A==check_sp_lo_p)[0].tolist()
			# 	row_info2=np.where(A==check_sp_hi_c)[0].tolist()
			# 	row_info3=np.where(A==check_sp_lo_c)[0].tolist()

			# 	pe_sum_data = OI_Data[row_info[0]][2] + OI_Data[row_info[0]][4]
			# 	pe_sum_data1 = OI_Data[row_info1[0]][2] + OI_Data[row_info1[0]][4]
			# 	ce_sum_data = OI_Data[row_info2[0]][1] + OI_Data[row_info2[0]][3]
			# 	ce_sum_data1 = OI_Data[row_info3[0]][1] + OI_Data[row_info3[0]][3]

			# 	if ((pe_sum_data > ce_sum_data or pe_sum_data > ce_sum_data1) or (pe_sum_data1 > ce_sum_data or pe_sum_data1 > ce_sum_data1) ):
			# 		Cumulative_for_PE = True
			# 	else:
			# 		Cumulative_for_PE = False

			# 	if ((pe_sum_data < ce_sum_data or pe_sum_data < ce_sum_data1) or (pe_sum_data1 < ce_sum_data or pe_sum_data1 < ce_sum_data1)):
			# 		Cumulative_for_CE = True
			# 	else:
			# 		Cumulative_for_CE = False			

			"""Shifting Of Selected Strike Price"""
			if(trade):
				selected_check=[]
				for_CE_STRIKE = float(a[3]) + abs((float(a[3])%50 - 50))
				for_PE_STRIKE = float(a[2]) - abs((float(a[2])%50))
				# print("-----------------------------------------------")
				# print("Selected Strike price")
				selected_check=[]
				# print("CE Strike " +"  "+"PE Strike")
				# print(str(for_CE_STRIKE) + "  " +str(for_PE_STRIKE))
				selected_check.append(for_CE_STRIKE)
				selected_check.append(for_CE_STRIKE+50)
				selected_check.append(for_CE_STRIKE+100)
				# selected_check.append(for_CE_STRIKE+150)
				selected_check.append(for_PE_STRIKE)
				selected_check.append(for_PE_STRIKE-50)
				selected_check.append(for_PE_STRIKE-100)
				# selected_check.append(for_PE_STRIKE-150)
				# print(str(for_CE_STRIKE + 50) + "  " +str(for_PE_STRIKE - 50))
				# print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
				# print("-----------------------------------------------")
			
			rows=np.where(A==selected_check[0])[0].tolist()
			rows1=np.where(A==selected_check[1])[0].tolist()
			rows2=np.where(A==selected_check[2])[0].tolist()
			rows3=np.where(A==selected_check[3])[0].tolist()
			rows5=np.where(A==selected_check[4])[0].tolist()

			Reduction_Count=0
			Reduction_Count = Reduction_Count+1 if OI_Data[rows[0]][5]-OI_Data[rows[0]][3] > 0 else Reduction_Count
			Reduction_Count = Reduction_Count+1 if OI_Data[rows1[0]][5]-OI_Data[rows1[0]][3] > 0 else Reduction_Count
			Reduction_Count = Reduction_Count+1 if OI_Data[rows2[0]][5]-OI_Data[rows2[0]][3] > 0 else Reduction_Count
			if( Reduction_Count==3 and ( OI_Data[rows3[0]][6] - OI_Data[rows3[0]][4] < 0 
					or OI_Data[rows5[0]][6] - OI_Data[rows5[0]][4] < 0) ) :
				print("Call Reduction in all 3 OI's" +" time: "+time[j] +"  count:" + str(count+1))

				if Cumulative_for_CE:
					count=count+1
					if count1>=1:
						count1=0
					time_int = int(time[j].replace(':', ''))
					time_int1 = int(time[j-1].replace(':', ''))
					formatted_num = '{:06d}'.format(time_int1)
					formatted_num1 = '{:06d}'.format(time_int)
					start=output_string + " "+str(formatted_num)
					end=output_string + " "+str(formatted_num1)
					response = xt.get_ohlc(
					exchangeSegment=xt.EXCHANGE_NSECM,
					exchangeInstrumentID=26000,
					startTime=start,
					endTime=end,
					compressionValue=450000)
					a=response['result']['dataReponse'].split('|')
					if a==['']:
						print("11th Wrong Data")
					if count==1:
						trade_point=float(a[2])
						# print(trade_point)
					elif count==2:
						trade_point=max(float(a[2]),trade_point)
						print(trade_point)
						trade=False
						trade_time=time[j]
						count1=0	
				else:
					print("Saved Due to Cumulative")
						
			elif( Reduction_Count==2 and ( OI_Data[rows3[0]][6] - OI_Data[rows3[0]][4] < 0 
					or OI_Data[rows5[0]][6] - OI_Data[rows5[0]][4] < 0) ) :
				print("Call Reduction in  2 OI's" +" time: "+time[j],end=' ')

				if Cumulative_for_CE:
					sort=sorted([OI_Data[rows[0]][5]-OI_Data[rows[0]][3], OI_Data[rows1[0]][5]-OI_Data[rows1[0]][3],OI_Data[rows2[0]][5]-OI_Data[rows2[0]][3]])
					if (min(sort[1],sort[2]) > abs(sort[0])):
						print("  count:" + str(count+1))
						count=count+1
						if count1>=1:
							count1=0
						# print("Take Interval of 5 min")

						j=time1.index(time[j])
						time=time1
						time_int = int(time[j].replace(':', ''))
						time_int1 = int(time[j-1].replace(':', ''))
						formatted_num = '{:06d}'.format(time_int1)
						formatted_num1 = '{:06d}'.format(time_int)
						start=output_string + " "+str(formatted_num)
						end=output_string + " "+str(formatted_num1)
						response = xt.get_ohlc(
						exchangeSegment=xt.EXCHANGE_NSECM,
						exchangeInstrumentID=26000,
						startTime=start,
						endTime=end,
						compressionValue=450000)
						a=response['result']['dataReponse'].split('|')
						if a==['']:
							print("12th Wrong Data")
						if count==1:
							trade_point=float(a[2])
							# print(trade_point)
						elif count==2:
							trade_point=max(float(a[2]),trade_point)
							print(trade_point)
							trade=False
							trade_time=time[j]
							count1=0
					else:
						print("Saved Due to 3rd less addition")
				else:
					print("Saved due to Cumulative")
						
					
			rows=np.where(A==selected_check[3])[0].tolist()
			rows1=np.where(A==selected_check[4])[0].tolist()
			rows2=np.where(A==selected_check[5])[0].tolist()
			rows3=np.where(A==selected_check[1])[0].tolist()
			rows5=np.where(A==selected_check[2])[0].tolist()

			Reduction_Count=0
			Reduction_Count = Reduction_Count+1 if OI_Data[rows[0]][6]-OI_Data[rows[0]][4] > 0 else Reduction_Count
			Reduction_Count = Reduction_Count+1 if OI_Data[rows1[0]][6]-OI_Data[rows1[0]][4] >0 else Reduction_Count
			Reduction_Count = Reduction_Count+1 if OI_Data[rows2[0]][6]-OI_Data[rows2[0]][4] > 0 else Reduction_Count
			if(Reduction_Count ==3 and ( OI_Data[rows3[0]][5] - OI_Data[rows3[0]][3] < 0 
				or OI_Data[rows5[0]][5] - OI_Data[rows5[0]][3] < 0 )) :
				print("Put Reduction in all 3 OI's" +  " time: "+ time[j]+"  count:" + str(count1+1))

				if Cumulative_for_PE:
					count1=count1+1
					if count>=1:
						count=0
					time_int = int(time[j].replace(':', ''))
					time_int1 = int(time[j-1].replace(':', ''))
					formatted_num = '{:06d}'.format(time_int1)
					formatted_num1 = '{:06d}'.format(time_int)
					start=output_string + " "+str(formatted_num)
					end=output_string + " "+str(formatted_num1)
					response = xt.get_ohlc(
					exchangeSegment=xt.EXCHANGE_NSECM,
					exchangeInstrumentID=26000,
					startTime=start,
					endTime=end,
					compressionValue=450000)
					a=response['result']['dataReponse'].split('|')
					if a==['']:
						print("13th Wrong Data")
					if count1==1:
						trade_point=float(a[3])
						# print(trade_point)
					elif count1==2:
						trade_point=min(float(a[3]),trade_point)
						print(trade_point)
						trade=False
						trade_time=time[j]
						count=0	
				else:
					print("Saved Due to Cumulative")		
			elif( Reduction_Count==2 and ( OI_Data[rows3[0]][5] - OI_Data[rows3[0]][3] < 0 
				or OI_Data[rows5[0]][5] - OI_Data[rows5[0]][3] < 0 )) :
				print("Put Reduction in 2 OI's" +  " time: "+ time[j],end=' ')
				if Cumulative_for_PE:
					sort=sorted([OI_Data[rows[0]][6]-OI_Data[rows[0]][4],OI_Data[rows1[0]][6]-OI_Data[rows1[0]][4],OI_Data[rows2[0]][6]-OI_Data[rows2[0]][4]])
					if(min(sort[1],sort[2])> abs(sort[0])):
						print("  count:" + str(count1+1))
						count1=count1+1
						if count>=1:
							count=0
						# print("TAKE INTERVAL FOR 5 MIN")
						j=time1.index(time[j])
						time=time1

						time_int = int(time[j].replace(':', ''))
						time_int1 = int(time[j-1].replace(':', ''))
						formatted_num = '{:06d}'.format(time_int1)
						formatted_num1 = '{:06d}'.format(time_int)
						start=output_string + " "+str(formatted_num)
						end=output_string + " "+str(formatted_num1)
						response = xt.get_ohlc(
						exchangeSegment=xt.EXCHANGE_NSECM,
						exchangeInstrumentID=26000,
						startTime=start,
						endTime=end,
						compressionValue=450000)
						a=response['result']['dataReponse'].split('|')
						if a==['']:
							print("14th Wrong Data")
						if count1==1:
							trade_point=float(a[3])
							# print(trade_point)
						elif count1==2:
							trade_point=min(float(a[3]),trade_point)
							print(trade_point)
							trade=False
							trade_time=time[j]
							count=0
					else:
						print("Saved Due to 3rd")
				else:
					print("Saved due to Cumulative")
						
			if((count>=2 or count1>=2) and trade==False):
				
				x= time.index(trade_time)
				y=time.index(time[j])

				if y-x>6:
					if count>=2:
						count=0
						print("Saved due to Time Pass from trading Signal")
					else:
						count1=0
						print(" Saved due to Time Pass from trading Signal")

				# trade=True
				if count>=2 and last_trade!='Put_Sell':
					print("Take a Trade if Price Point goes above " + str(trade_point+10))
					count=10
					time_int = int(time[j].replace(':', ''))
					time_int1 = int(time[j-1].replace(':', ''))
					formatted_num = '{:06d}'.format(time_int1)
					formatted_num1 = '{:06d}'.format(time_int)
					start=output_string + " "+str(formatted_num)
					end=output_string + " "+str(formatted_num1)
					response = xt.get_ohlc(
					exchangeSegment=xt.EXCHANGE_NSECM,
					exchangeInstrumentID=26000,
					startTime=start,
					endTime=end,
					compressionValue=450000)
					a=response['result']['dataReponse'].split('|')
					print(a[2])
					if(float(a[2])> trade_point+10):
						print("Take a Trade Put Bech Do")
						selling_sp = float(a[4]) + ( 50 - float(a[4])%50) -200
						buying_sp=selling_sp - 100
						sp1=prefix+str(int(selling_sp))+'PE.NFO'
						sp2=prefix+str(int(buying_sp))+'PE.NFO'
						filtered_data = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == time[j])]
						extracted_data = filtered_data.to_dict('records')
						# print(extracted_data[0]['Close'])
						filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == time[j])]
						extracted_data1 = filtered_data.to_dict('records')
						# print(extracted_data1[0]['Close'])
						filtered_data  = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == '15:19:59')]
						extracted_data2 = filtered_data.to_dict('records')
						# print(extracted_data2[0]['Close'])
						filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == '15:19:59')]
						extracted_data3 = filtered_data.to_dict('records')
						# print(extracted_data3[0]['Close'])
						row1=[output_string,sp1,time[j],'15:19:59','Sell',extracted_data[0]['Close'],extracted_data2[0]['Close'],'']
						row2=[output_string,sp2,time[j],'15:19:59','Buy',extracted_data1[0]['Close'],extracted_data3[0]['Close'],'']
						trade_data.append(row1)
						trade_data.append(row2)
						last_trade='Put_Sell'
						sl=extracted_data[0]['Close'] - extracted_data1[0]['Close']
						print("Difference : " + str(sl))
						for rows in OI_Data:
							print(rows)
						print("------------------------------------------------------------------------------------------------")		
						if (len(trade_data) > 2):
							for rows in trade_data[-4:-2]:
								print(rows)
								rows[3]=time[j]
								filtered_data  = df.loc[(df['Ticker']== rows[1] ) & (df['Time'] == time[j])]
								extracted = filtered_data.to_dict('records')
								rows[6]=extracted[0]['Close']
								print(rows)
						trade=True
					
				elif count1>=2 and last_trade!='Call_Sell':
					print("Take a Trade if Price Point goes below " + str(trade_point-10))
					count1=10
					time_int = int(time[j].replace(':', ''))
					time_int1 = int(time[j-1].replace(':', ''))
					formatted_num = '{:06d}'.format(time_int1)
					formatted_num1 = '{:06d}'.format(time_int)
					start=output_string + " "+str(formatted_num)
					end=output_string + " "+str(formatted_num1)
					response = xt.get_ohlc(
					exchangeSegment=xt.EXCHANGE_NSECM,
					exchangeInstrumentID=26000,
					startTime=start,
					endTime=end,
					compressionValue=450000)
					a=response['result']['dataReponse'].split('|')
					print(a[3])	
					if(float(a[3]) < (trade_point-10)):
						print("Take a Trade Call Bech Do")

						selling_sp= float(a[4])  - (float(a[4])%50) + 200
						buying_sp=selling_sp+100
						sp1=prefix+str(int(selling_sp))+'CE.NFO'
						sp2=prefix+str(int(buying_sp))+'CE.NFO'
						
						filtered_data = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == time[j])]
						extracted_data = filtered_data.to_dict('records')
						# print(extracted_data)
						filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == time[j])]
						extracted_data1 = filtered_data.to_dict('records')
						# print(extracted_data1[0]['Close'])
						filtered_data  = df.loc[(df['Ticker']== sp1 ) & (df['Time'] == '15:19:59')]
						extracted_data2 = filtered_data.to_dict('records')
						# print(extracted_data2[0]['Close'])
						filtered_data  = df.loc[(df['Ticker']== sp2 ) & (df['Time'] == '15:19:59')]
						extracted_data3 = filtered_data.to_dict('records')
						# print(extracted_data3[0]['Close'])
						row1=[output_string,sp1,time[j],'15:19:59','Sell',extracted_data[0]['Close'],extracted_data2[0]['Close'],'']
						row2=[output_string,sp2,time[j],'15:19:59','Buy',extracted_data1[0]['Close'],extracted_data3[0]['Close'],'']
						trade_data.append(row1)
						trade_data.append(row2)
						last_trade='Call_Sell'
						sl=extracted_data[0]['Close'] - extracted_data1[0]['Close']
						print("Difference : " + str(sl))
						for rows in OI_Data:
							print(rows)
						print("------------------------------------------------------------------------------------------------")		
						if (len(trade_data) > 2):
							for rows in trade_data[-4:-2]:
								print(rows)
								rows[3]=time[j]
								filtered_data  = df.loc[(df['Ticker']== rows[1] ) & (df['Time'] == time[j])]
								extracted = filtered_data.to_dict('records')
								rows[6]=extracted[0]['Close']
								print(rows)
						trade=True
			
			if trade:
				time_str = time[j]
				t=0
				while t<15:
					time_obj = datetime.strptime(time_str, "%H:%M:%S")
					time_obj += timedelta(minutes=1)
					time_str = time_obj.strftime("%H:%M:%S")

					filtered_data  = df.loc[(df['Ticker']== trade_data[-2][1] ) & (df['Time'] == time_str)]
					extracted = filtered_data.to_dict('records')
					close1=extracted[0]['High']
					# print(close1)
					filtered_data  = df.loc[(df['Ticker']== trade_data[-1][1] ) & (df['Time'] == time_str)]
					extracted = filtered_data.to_dict('records')
					close2=extracted[0]['High']
					# print(close2)
					# print(close1-close2)
					if (close1-close2) >= (sl*2):
						print("StopLoss Hit")
					t=t+1
			j=j+1

		for rows in trade_data:
			# print(rows)
			writer.writerow(rows)









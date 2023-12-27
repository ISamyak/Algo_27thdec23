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
import smtplib
import copy
"""Investor client credentials"""
API_KEY = "27cb3075e6f28484597669"
API_SECRET = "Vfrx866#y0"
clientID = "D0253276"
#userID = "D0253276"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()
day=''
"""------------------Chnage Folder path and EXPIRY DATE IN BELOW 2 LINES----------------------"""
prefix="NIFTY16Nov2023"
m=1



def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            email_body = f"Subject: {subject}\n\n{message}"
            server.sendmail(sender_email, recipient_email, email_body)
        
        print("Email sent successfully!")
    except Exception as e:
        print("An error occurred while sending the email:", str(e))

# def email():
#     sender_email = 'samyak1347@gmail.com' # Enter your Gmail email address
#     sender_password = 'drfvleaiehnzzmiw' # Enter your Gmail password
#     recipient_email = 'samyak1347@gmail.com' # Enter your friend's email address
#     subject = 'Test'
#     message = 'Sell CE'

#     send_email(sender_email, sender_password, recipient_email, subject, message)

def change_date_format(date):
	original_format = '%Y%m%d'
	date_object = datetime.strptime(date, original_format)
	output_format = '%b %d %Y'
	return date_object.strftime(output_format)

def strike_price_for_data(a):
	sp=[]
	SP=int(float(a[3])) - (int(float(a[3])%100)) - 400
	while int(float(a[2]))+500 >= SP:
		sp.append(SP)
		# PRINT(SP,end=" ")
		SP=SP+100
	return sp

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
    	compressionValue=450000)
		a=response['result']['dataReponse'].split('|')
		if a==['']:
			print("Wrong Data Imp")
			return a
		else:
			return a	
	else:
		return a

def previous_day_OI_set_Instrument_set(output_date):
    t=0
    i=0
    j=0
    """Check before 9:15 and only once"""
    output_opening_time = output_date+ " 090000"
    output_closing_time = output_date + " 091530"
    a1=getting_ohlc_nifty(output_opening_time,output_closing_time)
    if a1==['']:
    	a1=getting_ohlc_nifty(output_opening_time,output_closing_time)
    	if a1==['']:
    		print("Something in data is wrong - Can't be Ignore")

    Nifty_SP=float(a1[4])
    """range to be -350 to +350"""
    Nifty_Strike=Nifty_SP - 400 - (Nifty_SP%100)
    while Nifty_SP+500 >= Nifty_Strike:
        OI_Data[i][j]=Nifty_Strike
        j=j+1
        response = xt.get_option_symbol(
            exchangeSegment=2,
            series='OPTIDX',
            symbol='NIFTY',
            expiryDate=prefix[5:],
            optionType='CE',
            strikePrice=Nifty_Strike)
        # print(response)
        #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
        OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
        j=j+1

        instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
        temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
        instruments_OI.append(temp)
        response = xt.get_quote(
            Instruments=instrument,
            xtsMessageCode=1510,
            publishFormat='JSON')
        # print(response)
        json_string = response['result']['listQuotes'][0]
        data=json.loads(json_string)
        OpenInterest=data["OpenInterest"]
        #print(OpenInterest,end="  ")
        OI_Data[i][j]=OpenInterest
        j=j+1

        response = xt.get_option_symbol(
            exchangeSegment=2,
            series='OPTIDX',
            symbol='NIFTY',
            expiryDate=prefix[5:],
            optionType='PE',
            strikePrice=Nifty_Strike)
        #print(response['result'][0]['ExchangeInstrumentID'],end="  ")
        OI_Data[i][j]=response['result'][0]['ExchangeInstrumentID']
        j=j+1
        instrument = [{'exchangeSegment': 2, 'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],},]
        temp = {'exchangeSegment':2,'exchangeInstrumentID':response['result'][0]['ExchangeInstrumentID'],}
        instruments_OI.append(temp)
        response = xt.get_quote(
            Instruments=instrument,
            xtsMessageCode=1510,
            publishFormat='JSON')
        json_string = response['result']['listQuotes'][0]
        data=json.loads(json_string)
        OpenInterest=data["OpenInterest"]
        #print(OpenInterest,end="  ")
        OI_Data[i][j]=OpenInterest          
        j=0
        i=i+1  
        #print()
        Nifty_Strike=Nifty_Strike+100


def select_itm_strike_price(output_opening_time,output_closing_time):
	a=getting_ohlc_nifty(output_opening_time,output_closing_time)
	# print(a)
	if a==['']:
		print("Not getting value of Nifty")
	else:
		selected_check=[]
		reduction_check=[]
		selected_check_ce=[]
		selected_check_pe=[]
		close=float(a[4])
		if  close%100 <= 80:
			for_CE_STRIKE=int(close - close%100) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE = for_CE_STRIKE - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(close - close%100) + 100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 100
			selected_check_pe.append(for_PE_STRIKE)

		elif close%100 > 80:
			for_CE_STRIKE=int(close + (100-close%100)) - 100
			selected_check_ce.append(for_CE_STRIKE)
			for_CE_STRIKE= for_CE_STRIKE-100
			selected_check_ce.append(for_CE_STRIKE)
			for_PE_STRIKE = int(close + (100-close%100))+100
			selected_check_pe.append(for_PE_STRIKE)
			for_PE_STRIKE = for_PE_STRIKE + 100
			selected_check_pe.append(for_PE_STRIKE)
		
		if close%100>50:
			for_CE_STRIKE=int(close- close%100)+100
			reduction_check.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 100
			reduction_check.append(for_CE_STRIKE)
			for_PE_STRIKE=int(close-close%100)+100
			reduction_check.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE+100
			reduction_check.append(for_PE_STRIKE)
		elif close%100<=50:
			for_CE_STRIKE=int(close- close%100)
			reduction_check.append(for_CE_STRIKE)
			for_CE_STRIKE=for_CE_STRIKE - 100
			reduction_check.append(for_CE_STRIKE)
			for_PE_STRIKE=int(close-close%100)
			reduction_check.append(for_PE_STRIKE)
			for_PE_STRIKE=for_PE_STRIKE+100
			reduction_check.append(for_PE_STRIKE)


		selected_check = selected_check_ce + selected_check_pe
		return selected_check,reduction_check	

def update_OI_Data(OI,instruments_OI,Strike_Price_Set):
	response = xt.get_quote(
			Instruments=instruments_OI,
			xtsMessageCode=1510,
			publishFormat='JSON')
	# print(response)
	for i in range(len(Strike_Price_Set)*2 - 4):
		json_string = response['result']['listQuotes'][i]
		j=0
		data=json.loads(json_string)
		OpenInterest=data["OpenInterest"]
		# print(OpenInterest)
		if i%2==0:
			Change=((OpenInterest)-OI[int(i/2)][j+2])
			OI[int(i/2)][j+7]=OI[int(i/2)][j+5]
			OI[int(i/2)][j+5]=Change
			OI[int(i/2)][j+9]=(OpenInterest)
		else:
			Change=((OpenInterest)-OI[int(i/2)][j+4])
			OI[int(i/2)][j+8]=OI[int(i/2)][j+6]
			OI[int(i/2)][j+6]=Change	
			OI[int(i/2)][j+10]=(OpenInterest)
		i=i+1
	return OI	

def getting_ohlc_nifty_using_compression(opening_time,closing_time,compress_Value):
	response = xt.get_ohlc(
    	exchangeSegment=xt.EXCHANGE_NSECM,
    	exchangeInstrumentID=26000,
    	startTime=opening_time,
    	endTime=closing_time,
    	compressionValue=compress_Value)
	a=response['result']['dataReponse'].split('|')
	if a==['']:
		a=response['result']['dataReponse'].split('|')
		if a==['']:
			print("1st Wrong data")
			return a
		else:
			return a
			
	else:
		return a

def calculate_moving_averages(data, period):
    if len(data) < period:
        period=len(data)
    
    moving_averages = []
    for i in range(period, len(data) + 1):
        subset = data[i-period:i]
        average = sum(subset) / period
        moving_averages.append(average)
    
    return moving_averages[-1]

def moving_Average_5_13_26(opening_time,closing_time,compress_Value,Side):
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	if a==['']:
		print("Ignore 1st time)")
		return True
	else:	
		x=4
		count=0
		close=[]
		for i in range(len(a)):
			if i==x+count*7:
				close.append(float(a[i]))
				count=count+1
		ma_5 = calculate_moving_averages(close, 5)
		ma_13 = calculate_moving_averages(close, 13)
		ma_26 = calculate_moving_averages(close, 26)
		if Side=='C':
			if ma_26>ma_13 and ma_13>ma_5:
				return True
			else:
				return False	
		elif Side=='P':
			if ma_5>ma_13 and ma_13>ma_26:
				return True
			else:
				return False

def calculate_rolling_average(data, period):
    average = []
    for i in range(len(data)):
        if i < period:
            average.append(0)
        else:
            average.append(sum(data[i-period+1:i+1]) / period)
    return average

def RSI(output_date,price_time,period=14):
	period_time= price_time - timedelta(minutes=60)
	if period_time.time() < datetime.strptime("09:15", "%H:%M").time():
		period_time=output_date+" "+"091500"
		period=10
	else:
		time_str4=period_time.strftime("%H%M%S")
		period_time=output_date+" "+time_str4

	time_str5=price_time.strftime("%H%M%S")	
	output_closing_time=output_date+" "+time_str5
	a=getting_ohlc_nifty_using_compression(period_time,output_closing_time,180)
	if a==[]:
		a=getting_ohlc_nifty_using_compression(period_time,output_closing_time,180)
		if a==[]:
			a=getting_ohlc_nifty_using_compression(period_time,output_closing_time,180)
			if a==[]:
				print("Wrong data of nifty")
	x=4
	count=0
	close=[]
	for i in range(len(a)):
		if i==x+count*7:
			close.append(float(a[i]))
			count=count+1
		
	delta = [close[i] - close[i-1] for i in range(1, len(close))]
	gain = [d if d > 0 else 0 for d in delta]
	loss = [-d if d < 0 else 0 for d in delta]
	avg_gain = calculate_rolling_average(gain,period)
	avg_loss = calculate_rolling_average(loss,period)
	rs = [avg_gain[i] / avg_loss[i] if avg_loss[i] != 0 else 0 for i in range(len(avg_gain))]
	rsi = [100 - (100 / (1 + rs[i])) if rs[i] != 0 else 0 for i in range(len(rs))]
	return rsi[-1]


def to_check_first_buy_leg(output_date,compress_Value):
	t1 = time.strftime("%H%M%S",time.localtime())
	current_time = datetime.now()
	new_time = current_time - timedelta(minutes=30)
	time_str = new_time.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str
	output_closing_time=output_date+" "+t1
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=2
	count=0
	high=[]
	for i in range(len(a)):
		if i==x+count*7:
			high.append(float(a[i]))
			count=count+1

	highest=max(high)

	highest_index=high.index(highest)
	highest_time= current_time - timedelta(minutes=(10-highest_index)*3)
	Fifteen_min_back_time_from_Highest = highest_time - timedelta(minutes=21)
	time_str1 = Fifteen_min_back_time_from_Highest.strftime("%H%M%S")
	time_str2 = highest_time.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str1
	output_closing_time=output_date+" "+time_str2
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=3
	count=0
	low=[]
	for i in range(len(a)):
		if i==x+count*7:
			low.append(float(a[i]))
			count=count+1
	
	lowest=min(low)
	lowest_index=low.index(lowest)
	sixty_min_back_time_from_Highest= highest_time - timedelta(minutes=60)
	time_str3= sixty_min_back_time_from_Highest.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str3
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=3
	count=0
	low=[]
	for i in range(len(a)):
		if i==x+count*7:
			low.append(float(a[i]))
			count=count+1
	another_lowest=min(low)
	if float(another_lowest) < float(lowest):
		print("Buy leg Present")
		lowest_price_time= highest_time - timedelta(minutes= (5- lowest_index )*3) 
		rsi = RSI(output_date,lowest_price_time) 
		return True,float(lowest),rsi
	else:
		print("No Buy leg")
		return False,0,0
					
def to_check_first_Sell_leg(output_date,compress_Value):
	t1 = time.strftime("%H%M%S",time.localtime())
	current_time = datetime.now()
	new_time = current_time - timedelta(minutes=30)
	time_str = new_time.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str
	output_closing_time=output_date+" "+t1
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=3
	count=0
	Low=[]
	for i in range(len(a)):
		if i==x+count*7:
			Low.append(float(a[i]))
			count=count+1
	lowest=min(Low)
	lowest_index=Low.index(lowest)
	lowest_time= current_time - timedelta(minutes=(10-lowest_index)*3)
	Fifteen_min_back_time_from_Lowest = lowest_time - timedelta(minutes=21)
	time_str1 = Fifteen_min_back_time_from_Lowest.strftime("%H%M%S")
	time_str2 = lowest_time.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str1
	output_closing_time=output_date+" "+time_str2
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=2
	count=0
	high=[]
	for i in range(len(a)):
		if i==x+count*7:
			high.append(float(a[i]))
			count=count+1
	highest=max(high)
	highest_index=high.index(highest)
	sixty_min_back_time_from_Lowest= lowest_time - timedelta(minutes=60)
	time_str3= sixty_min_back_time_from_Lowest.strftime("%H%M%S")
	output_opening_time=output_date+" "+time_str3
	a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,compress_Value)
	x=2
	count=0
	high=[]
	for i in range(len(a)):
		if i==x+count*7:
			high.append(float(a[i]))
			count=count+1
	another_highest=max(high)
	if float(another_highest) > float(highest):
		print("Sell leg Present")
		highest_price_time= lowest_time - timedelta(minutes= (5- highest_index )*3) 
		rsi = RSI(output_date,highest_price_time) 
		return True,float(highest),rsi
	else:
		print("No Sell leg")
		return False,0,0


def tick_Count_With_other_Indicator(OI,Add_Count,Side,shifting,reduction_flag,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,leg_price,rsi_value):
	D=np.array(OI)
	if Side=='C':
		row=np.where(D==selected_itm_Sp[0])[0].tolist()
		row1=np.where(D==selected_itm_Sp[1])[0].tolist()
		row_red=np.where(D==reduction_check[2])[0].tolist()
		row_red1=np.where(D==reduction_check[3])[0].tolist()
		if((OI[row_red[0]][6]-OI[row_red[0]][8] < 0) or (OI[row_red1[0]][6] - OI[row_red1[0]][8] < 0 )):
				reduction_flag=True
		if Add_Count==2 and shifting:
			rowp=np.where(D==past_selected_itm_Sp[0])[0].tolist()	
			if( (OI[row[0]][5]-OI[row[0]][7] > 0 or OI[rowp[0]][5]-OI[rowp[0]][7]  > 0 or OI[row1[0]][5]-OI[row1[0]][7] > 0 ) and trade==False):
				print("Added in ITM or ATM or far ITM Call")
				Add_Count=Add_Count+1
				if Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1						
			else:
				print("No Addition")
				Add_Count=0
				reduction_flag=False
				buy_leg_flag=False
				leg_price=0
				rsi_value=0
		else:		
			if((OI[row[0]][5]-OI[row[0]][7] > 0)  and trade==False):	
				print("Added in ITM Call")
				Add_Count=Add_Count+1			
				if Add_Count==1:
					buy_leg_flag,leg_price,rsi_value=to_check_first_buy_leg(output_date,180)
				elif Add_Count==2:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1								
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 2nd Tick")
					else:
						print("MA False")
						Add_Count=1

					if reduction_flag:
						print("True")
					else:
						print("False")
						Add_Count=1	
					current_time = datetime.now()
					open_time= current_time - timedelta(minutes=6)
					time_str3= open_time.strftime("%H%M%S")
					output_opening_time = output_date +" "+time_str3 
					a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,180)
					count=0
					high=[]
					for i in range(len(a)):
						if i==2+count*7:
							high.append(float(a[i]))
							count=count+1
					Upper=max(high)
					print(Upper)
				elif Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1

			elif ((OI[row1[0]][5]-OI[row1[0]][7] > 0 ) and Add_Count>=2 and trade==False):
				print("Added in far ITM Call")
				Add_Count=Add_Count+1
				if Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1		
			else:
				print("No addition")
				Add_Count=0
				reduction_flag=False
				buy_leg_flag=False
				leg_price=0
				rsi_value=0

		return Add_Count,reduction_flag,leg_price,rsi_value

	if Side=='P':
		row=np.where(D==selected_itm_Sp[2])[0].tolist()
		row1=np.where(D==selected_itm_Sp[3])[0].tolist()
		row_red=np.where(D==reduction_check[0])[0].tolist()
		row_red1=np.where(D==reduction_check[1])[0].tolist()
		if((OI[row_red[0]][5]-OI[row_red[0]][7] < 0) or (OI[row_red1[0]][5] - OI[row_red1[0]][7] < 0 )):
				reduction_flag=True
		if Add_Count==2 and shifting:
			rowp=np.where(D==past_selected_itm_Sp[2])[0].tolist()
			if( (OI[row[0]][6]-OI[row[0]][8] > 0 or OI[rowp[0]][6]-OI[rowp[0]][8]  > 0 or OI[row1[0]][6]-OI[row1[0]][8] > 0 ) and trade==False):
				print("Added in ITM or ATM or far ITM Put")
				Add_Count=Add_Count+1
				if Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1				
			else:
				print("No Addition")
				Add_Count=0
				reduction_flag=False
				sell_leg_flag=False
				leg_price=0
				rsi_value=0
		else:
			if((OI[row[0]][6]-OI[row[0]][8] > 0)  and trade==False):	
				print("Added in ITM Put")
				Add_Count=Add_Count+1			
				if Add_Count==1:
					sell_leg_flag,leg_price,rsi_value=to_check_first_Sell_leg(output_date,180)
				elif Add_Count==2:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1								
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 2nd Tick")
					else:
						print("MA False")
						Add_Count=1

					if reduction_flag:
						print("True")
					else:
						print("False")
						Add_Count=1

					current_time = datetime.now()
					open_time= current_time - timedelta(minutes=6)
					time_str3= open_time.strftime("%H%M%S")
					output_opening_time = output_date +" "+time_str3 
					a=getting_ohlc_nifty_using_compression(output_opening_time,output_closing_time,180)
					count=0
					low=[]
					for i in range(len(a)):
						if i==2+count*7:
							low.append(float(a[i]))
							count=count+1
					Lower=min(low)
					print(Lower)		

				elif Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1

			elif ((OI[row1[0]][6]-OI[row1[0]][8] > 0 ) and Add_Count>=2 and trade==False):
				print("Added in far ITM Put")
				Add_Count=Add_Count+1
				if Add_Count>=3:
					t1 = time.strftime("%H%M%S",time.localtime())
					output_opening_time = output_date +" 090000" 
					output_closing_time=output_date+" " +t1
					if moving_Average_5_13_26(output_opening_time,output_closing_time,180,Side):
						print("MA True 3rd Tick")
					else:
						print("MA False")
						Add_Count=1				
			else:
				print("No Addition")
				Add_Count=0
				reduction_flag=False
				sell_leg_flag=False
				leg_price=0
				rsi_value=0

		return Add_Count,reduction_flag,leg_price,rsi_value

def rsi_flag(output_date,count,rsi_price,rsi_value,rsi_flag,Side):

	if count>=0 and count<=3 and rsi_price!=0:
		current_time = datetime.now()
		time_str2= current_time.strftime("%H%M%S")
		open_time= current_time - timedelta(minutes=6)
		time_str3= open_time.strftime("%H%M%S")
		output_opening_time = output_date +" "+time_str3 
		output_closing_time=output_date+" "+time_str2
		a= getting_ohlc_nifty(output_opening_time,output_closing_time)
		
		rsi=RSI(output_date,current_time)
		
		if float(a[3]) < rsi_price and rsi < rsi_value and Side=='C':
			rsi_flag=True
			return rsi_flag
		elif float(a[2]) > rsi_price and rsi > rsi_value and Side=='P':
			rsi_flag=True
			return rsi_flag	
		elif rsi_flag==False and count==3:
			print("Dont take Call Trade RSI and Trade Price not crossed")
			return rsi_flag 
		else:
			return rsi_flag			
	elif count==1 and rsi_price==0:
		rsi_flag=True
		return rsi_flag
	else:
		return rsi_flag		

def make_flag_and_Check_reverse(output_date,count,rsi_flag,opp_Side,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,frame,trade_point):
	if count>=3 and rsi_flag:
		print("Make flag and trade")

		current_time = datetime.now()
		time_str2= current_time.strftime("%H%M%S")
		open_time= current_time - timedelta(minutes=90)
		time_str3= open_time.strftime("%H%M%S")
		output_opening_time = output_date +" "+time_str3
		output_closing_time=output_date+" " +time_str2

		if moving_Average_5_13_26(output_opening_time,output_closing_time,180,'P'):
			print("MA(5 > 13 > 26)")
			time1=current_time-timedelta(minutes=15)
			time1_str=time1.strftime("%H%M%S")
			opening_time1=output_date+" "+time1_str
			a=getting_ohlc_nifty(opening_time1,output_closing_time)
			time2=current_time-timedelta(minutes=45)
			time2_str=time2.strftime("%H%M%S")
			opening_time2=output_date+" "+time1_str
			a1=getting_ohlc_nifty(opening_time2,output_closing_time)
			if float(a[2]) > float(a1[2]):
				print("Reverse True")
				count=0
				reduction_check=False
				rsi_value=0
				rsi_price=0
				rsi_flag=False
				flag_range=[]
				trade=False
				trade_Side=''
				trade_count=0
				return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,0
		
		if frame==3 and count>=3 and trade_point==0:
			two_candle_time=current_time-timedelta(minutes=6)
			time_str1=two_candle_time.strftime("%H%M%S")
			output_opening_time=output_date+" "+time_str1
			a=getting_ohlc_nifty(output_opening_time,output_closing_time)
			flag_range.append(float(a[3]))
			flag_range.append(float(a[2]))
			trade_count=0
			return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point
		else:	
			if count>=3:
				last_candle=current_time-timedelta(minutes=3)
				time_str1=last_candle.strftime("%H%M%S")
				output_opening_time=output_date+" "+time_str1
				a=getting_ohlc_nifty(output_opening_time,output_closing_time)
				if not((flag_range[1] <= float(a[2]) and float(a[3]) >= flag_range[1]) or (flag_range[0] >= float(a[2]) and flag_range[0] >= float(a[3]))):
					trade_count=trade_count+1
					if trade_count>=3 and trade_point==0:
						last_candle=current_time-timedelta(minutes=15)
						time_str1=last_candle.strftime("%H%M%S")
						output_opening_time=output_date+" "+time_str1
						a=getting_ohlc_nifty(output_opening_time,output_closing_time)
						if opp_Side=='P':
							trade_point=float(a[3])
							trade=True
							trade_Side='CE'
							print("Trade  Call below " + str(trade_point))
							sender_email = 'samyak1347@gmail.com'
							sender_password = 'drfvleaiehnzzmiw'
							recipient_email = 'anubhavgarg97@gmail.com'
							subject = 'ITM Addition Trade'
							message = "Trade  Call below " + str(trade_point)
							send_email(sender_email, sender_password, recipient_email, subject, message)
							return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point
						elif opp_Side=='C':
							trade_point=float(a[2])
							trade=True
							trade_Side='PE'
							print("Trade  Put Above " + str(trade_point))
							sender_email = 'samyak1347@gmail.com'
							sender_password = 'drfvleaiehnzzmiw'
							recipient_email = 'anubhavgarg97@gmail.com'
							subject = 'ITM Addition Trade'
							message = "Trade  Put Above " + str(trade_point)
							send_email(sender_email, sender_password, recipient_email, subject, message)
							return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point
					else:
						return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point		
				else:
					trade_count=0
					return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point
	else:
		return count,rsi_flag,reduction_check,rsi_price,rsi_value,flag_range,trade,trade_Side,trade_count,trade_point


def pcr_ratio(OI_Data,Strike_Price_Set):
	A=np.array(OI_Data)
	oi_total_ce=0
	oi_total_pe=0
	for i in range(int(len(Strike_Price_Set))-1):
		oi_total_ce=oi_total_ce+OI_Data[i][9]
		oi_total_pe=oi_total_pe+OI_Data[i][10]
		# print(oi_total_pe)
	return oi_total_pe/oi_total_ce	

"""wait till 9:15 till market open"""
Specify_the_Market_Open_TIME_HHMM = '0900' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = '0915'  #First 45 Min to get the Max OI Change
curr_dt = time.strftime("%Y%m%d", time.localtime())
set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

"""Setting OI Data till 9:15 , Strike Price , Previous day OI IN Call and Put , 9:15 Clock OI of Call and Put"""
instruments_OI = []
output_date=change_date_format(curr_dt)
OI_Data = [[0] * 11 for _ in range(11)]
OI_Data15 = [[0] * 11 for _ in range(11)]
OI_Data21 = [[0] * 11 for _ in range(11)]
OI_Data30 = [[0] * 11 for _ in range(11)]
previous_day_OI_set_Instrument_set(output_date)
OI_Data15=copy.deepcopy(OI_Data)
OI_Data21=copy.deepcopy(OI_Data)
OI_Data30=copy.deepcopy(OI_Data)
A=np.array(OI_Data15)
B=np.array(OI_Data21)
C=np.array(OI_Data30)

# print(OI_Data)
# print(instruments_OI)	

"""Wait till 10:00 for stablity of market"""
Specify_the_Open_TIME_HHMM = '1000'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

"""Strike price set for the day to store SP and Data"""
output_opening_time = output_date+ " 090000"
output_closing_time = output_date + " 100000"
selected_itm_Sp,reduction_check = select_itm_strike_price(output_opening_time,output_closing_time)
print(selected_itm_Sp)
# print(reduction_check)	

"""Strike price set for the day to store SP and Data"""
output_opening_time = output_date+ " 090000"
output_closing_time = output_date + " 100000"
a=getting_ohlc_nifty(output_opening_time,output_closing_time)
Strike_Price_Set=strike_price_for_data(a)

"""Updating OI Data at 10"""
OI_Data15 = update_OI_Data(OI_Data15,instruments_OI,Strike_Price_Set)
OI_Data21 = update_OI_Data(OI_Data21,instruments_OI,Strike_Price_Set)
OI_Data30 = update_OI_Data(OI_Data30,instruments_OI,Strike_Price_Set)

Specify_the_Open_TIME_HHMM = '1455'
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
frame15=0
frame21=0
frame30=0
count15_C=0
count21_C=0
count30_C=0
count15_P=0
count21_P=0
count30_P=0
shifting=False
trade=False
reduction_check_15C=False
reduction_check_15P=False
reduction_check_21C=False
reduction_check_21P=False
reduction_check_30C=False
reduction_check_30P=False
rsi_price_15C=0
rsi_value_15C=0
rsi_price_15P=0
rsi_value_15P=0
rsi_price_21C=0
rsi_value_21C=0
rsi_price_21P=0
rsi_value_21P=0
rsi_price_30C=0
rsi_value_30C=0
rsi_price_30P=0
rsi_value_30P=0
past_selected_itm_Sp=[]
rsi_flag_15C=False
rsi_flag_15P=False
rsi_flag_21C=False
rsi_flag_21P=False
rsi_flag_30C=False
rsi_flag_30P=False
flag_range_15C=[]
flag_range_15P=[]
flag_range_21C=[]
flag_range_21P=[]
flag_range_30C=[]
flag_range_30P=[]
trade_count_15C=0
trade_count_15P=0
trade_count_21C=0
trade_count_21P=0
trade_count_30C=0
trade_count_30P=0
trade_point_15C=0
trade_point_15P=0
trade_point_21C=0
trade_point_21P=0
trade_point_30C=0
trade_point_30P=0
trade=False
trade_Side=''


while(curr_tm_chk <= set_current_oi ):
	curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())
	OI_Data = update_OI_Data(OI_Data,instruments_OI,Strike_Price_Set)
	ratio = pcr_ratio(OI_Data,Strike_Price_Set)
	
	t1 = time.strftime("%H%M%S",time.localtime())
	
	if frame15==15:		
		OI_Data15 = update_OI_Data(OI_Data15,instruments_OI,Strike_Price_Set)
		print(curr_tm_chk)
		count15_C,reduction_check_15C,rsi_price_15C,rsi_value_15C=tick_Count_With_other_Indicator(OI_Data15,count15_C,'C',shifting,reduction_check_15C,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_15C,rsi_value_15C)
		count15_P,reduction_check_15P,rsi_price_15P,rsi_value_15P=tick_Count_With_other_Indicator(OI_Data15,count15_P,'P',shifting,reduction_check_15P,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_15P,rsi_value_15P)
		frame15=3							
	else:
		frame15=frame15+3

	if frame21==21:
		print(curr_tm_chk)
		OI_Data21 = update_OI_Data(OI_Data21,instruments_OI,Strike_Price_Set)
		count21_C,reduction_check_21C,rsi_price_21C,rsi_value_21C=tick_Count_With_other_Indicator(OI_Data21,count21_C,'C',shifting,reduction_check_21C,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_21C,rsi_value_21C)
		count21_P,reduction_check_21P,rsi_price_21P,rsi_value_21P=tick_Count_With_other_Indicator(OI_Data21,count21_P,'P',shifting,reduction_check_21P,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_21P,rsi_value_21P)
		frame21=3
	else:
		frame21=frame21+3

	if frame30==30:
		print(curr_tm_chk)
		OI_Data30 = update_OI_Data(OI_Data30,instruments_OI,Strike_Price_Set)
		count30_C,reduction_check_30C,rsi_price_30C,rsi_value_30C=tick_Count_With_other_Indicator(OI_Data30,count30_C,'C',shifting,reduction_check_30C,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_30C,rsi_value_30C)
		count30_P,reduction_check_30P,rsi_price_30P,rsi_value_30P=tick_Count_With_other_Indicator(OI_Data30,count30_P,'P',shifting,reduction_check_30P,selected_itm_Sp,past_selected_itm_Sp,reduction_check,trade,rsi_price_30P,rsi_value_30P)
		frame30=3	
	else:
		frame30=frame30+3

	rsi_flag_15C=rsi_flag(output_date,count15_C,rsi_price_15C,rsi_value_15C,rsi_flag_15C,'C')
	rsi_flag_21C=rsi_flag(output_date,count21_C,rsi_price_21C,rsi_value_21C,rsi_flag_21C,'C')
	rsi_flag_30C=rsi_flag(output_date,count30_C,rsi_price_30C,rsi_value_30C,rsi_flag_30C,'C')
	rsi_flag_15P=rsi_flag(output_date,count15_P,rsi_price_15P,rsi_value_15P,rsi_flag_15P,'P')
	rsi_flag_21P=rsi_flag(output_date,count21_P,rsi_price_21P,rsi_value_21P,rsi_flag_21P,'P')
	rsi_flag_30P=rsi_flag(output_date,count30_P,rsi_price_30P,rsi_value_30P,rsi_flag_30P,'P')

	if count15_C>=3 or count21_C>=3 or count30_C>=3 or count15_P>=3 or count21_P>=3 or count30_P>=3 :
		column_9 = [row[9] for row in OI_Data]
		column_10 = [row[10] for row in OI_Data]

		column_5 = [row[5] for row in OI_Data]
		column_6 = [row[6] for row in OI_Data]

		max_values_9 = sorted(column_9, reverse=True)[:2]
		max_values_10 = sorted(column_10, reverse=True)[:2]
		max_value= max_values_9 + max_values_10

		max_values_5 = sorted(column_5, reverse=True)[:2]
		max_values_6 = sorted(column_6, reverse=True)[:2]
		max_value_Chng= max_values_5 + max_values_6

		value=sorted(max_value,reverse=True)[:2]
		value1=sorted(max_value_Chng,reverse=True)[:2]

		if value[0] in max_values_9 or value[1] in max_values_9 or value1[0] in max_values_5 or value1[1] in max_values_5 :
			Callable=True
		else:
			Callable=False
			print("Top 2 in Put only")
			if count15_C>=3:
				count15_C=2
			if count21_C>=3:
				count21_C=2
			if count30_C>=3:
				count30_C=2		

		if value[0] in max_values_10 or value[1] in max_values_10 or value1[0] in max_values_6 or value1[1] in max_values_6 :
			Putable=True
		else:
			Putable=False	
			print("Top 2 in Call only")
			if count15_P>=3:
				count15_P=2
			if count21_P>=3:
				count21_P=2
			if count30_P>=3:
				count30_P=2
	
	if ratio>=0.80:
		count15_C,rsi_flag_15C,reduction_check_15C,rsi_price_15C,rsi_value_15C,flag_range_15C,trade,trade_Side,trade_count_15C,trade_point_15C=make_flag_and_Check_reverse(output_date,count15_C,rsi_flag_15C,'P',reduction_check_15C,rsi_price_15C,rsi_value_15C,flag_range_15C,trade,trade_Side,trade_count_15C,frame15,trade_point_15C)
		count21_C,rsi_flag_21C,reduction_check_21C,rsi_price_21C,rsi_value_21C,flag_range_21C,trade,trade_Side,trade_count_21C,trade_point_21C=make_flag_and_Check_reverse(output_date,count21_C,rsi_flag_21C,'P',reduction_check_21C,rsi_price_21C,rsi_value_21C,flag_range_21C,trade,trade_Side,trade_count_21C,frame21,trade_point_21C)
		count30_C,rsi_flag_30C,reduction_check_30C,rsi_price_30C,rsi_value_30C,flag_range_30C,trade,trade_Side,trade_count_30C,trade_point_30C=make_flag_and_Check_reverse(output_date,count30_C,rsi_flag_30C,'P',reduction_check_30C,rsi_price_30C,rsi_value_30C,flag_range_30C,trade,trade_Side,trade_count_30C,frame30,trade_point_30C)
	else:
		print(ratio)

	if ratio<=1.20:
		count15_P,rsi_flag_15P,reduction_check_15P,rsi_price_15P,rsi_value_15P,flag_range_15P,trade,trade_Side,trade_count_15P,trade_point_15P=make_flag_and_Check_reverse(output_date,count15_P,rsi_flag_15P,'C',reduction_check_15P,rsi_price_15P,rsi_value_15P,flag_range_15P,trade,trade_Side,trade_count_15P,frame15,trade_point_15P)
		count21_P,rsi_flag_21P,reduction_check_21P,rsi_price_21P,rsi_value_21P,flag_range_21P,trade,trade_Side,trade_count_21P,trade_point_21P=make_flag_and_Check_reverse(output_date,count21_P,rsi_flag_21P,'C',reduction_check_21P,rsi_price_21P,rsi_value_21P,flag_range_21P,trade,trade_Side,trade_count_21P,frame21,trade_point_21P)
		count30_P,rsi_flag_30P,reduction_check_30P,rsi_price_30P,rsi_value_30P,flag_range_30P,trade,trade_Side,trade_count_30P,trade_point_30P=make_flag_and_Check_reverse(output_date,count30_P,rsi_flag_30P,'C',reduction_check_30P,rsi_price_30P,rsi_value_30P,flag_range_30P,trade,trade_Side,trade_count_30P,frame30,trade_point_30P)
	else:
		print(ratio)

		

	
	time.sleep(180)	








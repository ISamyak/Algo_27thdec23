"""Importing necessary Library"""
from Connect import XTSConnect
import json
import time
import math
from datetime import datetime, timedelta
import pandas as pd
from pandas.tseries.offsets import BDay
import numpy as np

"""Investor client credentials"""
API_KEY = "1206051bd8cc6678f59533"
API_SECRET = "Wsjl454$9k"
clientID = "D0253246"
#userID = "D0253246"
XTS_API_BASE_URL = "http://xts.nirmalbang.com:3000"
source = "WEBAPI"

"""UserLogin"""
xt = XTSConnect(API_KEY, API_SECRET, source)
#print(XTSConnect(API_KEY, API_SECRET, source))
response = xt.interactive_login()



"""Nifty Instrument + Blank instrument for StrikeData"""
instruments = [
    {'exchangeSegment':1, 'exchangeInstrumentID':26000,},
    ]   
instruments_OI = []


"""Market Timing Setup"""
# print("\n Current time: ",datetime.now())  
Specify_the_Market_Open_TIME_HHMM = '0900' #to get Old date OI of Strike
Specify_the_Open_TIME_HHMM = '1000'  #First 45 Min to get the Max OI Change
curr_dt = time.strftime("%Y%m%d", time.localtime())
set_previous_oi = curr_dt + Specify_the_Market_Open_TIME_HHMM
set_current_oi = curr_dt + Specify_the_Open_TIME_HHMM
curr_tm_chk = time.strftime("%Y%m%d%H%M", time.localtime())

""" To get Spot Price of Nifty"""
def Spot_Price_Nifty():
	response = xt.get_quote(
	    Instruments=instruments,
	    xtsMessageCode=1512,
	    publishFormat='JSON')
	#print('Quote :', response['result']['listQuotes'][0])
	json_string = response['result']['listQuotes'][0]
	data = json.loads(json_string)
	Nifty_SP=data['LastTradedPrice']
	return data['LastTradedPrice']
	
Nifty_SP = Spot_Price_Nifty()
print('Spot Price:',Nifty_SP)

"""Array to Hold Data for Future use"""
OI_Data = [[0] * 9 for _ in range(15)]


def previous_day_OI_set_Instrument_set():
	t=0
	i=0
	j=0
	"""Check before 9:15 and only once"""
	while(curr_tm_chk >= set_previous_oi and t==0):
		"""range to be -350 to +350"""
		Nifty_Strike=Nifty_SP - 350 - (Nifty_SP%50)
		while Nifty_SP+350> Nifty_Strike:
		    OI_Data[i][j]=Nifty_Strike
		    j=j+1
		    response = xt.get_option_symbol(
		        exchangeSegment=2,
		        series='OPTIDX',
		        symbol='NIFTY',
		        expiryDate='09Mar2023',
		        optionType='CE',
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
		    #print(response)
		    json_string = response['result']['listQuotes'][0]
		    data=json.loads(json_string)
		    OpenInterest=data["OpenInterest"]
		    #print(OpenInterest,end="  ")
		    OI_Data[i][j]=OpenInterest/50
		    j=j+1

		    response = xt.get_option_symbol(
		        exchangeSegment=2,
		        series='OPTIDX',
		        symbol='NIFTY',
		        expiryDate='09Mar2023',
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
		    OI_Data[i][j]=OpenInterest/50		    
		    j=0
		    i=i+1  
		    #print()
		    Nifty_Strike=Nifty_Strike+50
		    t=1

previous_day_OI_set_Instrument_set()
instruments_OI= [{'exchangeSegment': 2, 'exchangeInstrumentID': 47044}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47067}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47068}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47088}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47089}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47102}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47109}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47110}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47115}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47116}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47117}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47120}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47121}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47122}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47128}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47129}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47131}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47139}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47140}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47192}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47197}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47213}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47214}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47222}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47223}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47278}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47279}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47280}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47283}, {'exchangeSegment': 2, 'exchangeInstrumentID': 47295}]
#print(instruments_OI)

print("Strike" + "  "+ "  Call"+"  "+"  "+"OI_C"+"   "+"Put" +"  "+ "  OI_P" +" " + "C_C_OI" +"   "+ "C_P_OI"+"  "+ "R_C_C_OI"+"  "+"R_P_P_OI")
for rows in OI_Data:
		print(rows)
print("-----------------------------------------------")
col_values_CE=[]
col_values_PE=[]

#Ready Instrument Near Spot Price till 10:00 clock candle
t=0
while(curr_tm_chk <= set_current_oi and t==0):
	response = xt.get_quote(
    	Instruments=instruments,
    	xtsMessageCode=1512,
    	publishFormat='JSON')
	json_string = response['result']['listQuotes'][0]
	data = json.loads(json_string)
	Nifty_SP=data['LastTradedPrice']
	print('Spot Price:',data['LastTradedPrice'])

	response = xt.get_quote(
			Instruments=instruments_OI,
			xtsMessageCode=1510,
			publishFormat='JSON')
	#print(response)
	for i in range(30):
		j=0
		json_string = response['result']['listQuotes'][i]
		data=json.loads(json_string)
		OpenInterest=data["OpenInterest"]
		if i%2==0:
			Change=abs((OpenInterest/50)-OI_Data[int(i/2)][j+2])
			col_values_CE.append(Change)
			OI_Data[int(i/2)][j+5]=Change
		else:
			Change=abs((OpenInterest/50)-OI_Data[int(i/2)][j+4])
			col_values_PE.append(Change)
			OI_Data[int(i/2)][j+6]=Change
	time.sleep(100)			


print("Strike" + "  "+ "  Call"+"  "+"  "+"OI_C"+"   "+"Put" +"  "+ "  OI_P" +" " + "C_C_OI" +"   "+ "C_P_OI"+"  "+ "R_C_C_OI"+"  "+"R_P_P_OI")
for rows in OI_Data:
		print(rows)
print("-----------------------------------------------")
"""Decide Strike price based on ohlc"""
now = datetime.now()
formatted_date = now.strftime('%b %d %Y')
formatted_date1 = formatted_date + " 091500"
formatted_date2 =  formatted_date + " 100000"
response = xt.get_ohlc(
exchangeSegment=xt.EXCHANGE_NSECM,
exchangeInstrumentID=26000,
startTime=formatted_date1,
endTime=formatted_date2,
compressionValue=45000)
# print("OHLC: " + str(response))
a=response['result']['dataReponse'].split('|')
# print("High:"+a[2] + "Low:" + a[3])
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
selected_check.append(for_PE_STRIKE)
selected_check.append(for_PE_STRIKE-50)
selected_check.append(for_PE_STRIKE-100)
print(str(for_CE_STRIKE + 50) + "  " +str(for_PE_STRIKE - 50))
print(str(for_CE_STRIKE + 100) + "  " +str(for_PE_STRIKE - 100))
print("-----------------------------------------------")

"""To Get Comman Values of Strike Price for Cumulative Shift"""
A=np.array(OI_Data)
common_values = []
for val in set(selected_check):
    if selected_check.count(val) > 1:
        common_values.append(val)
print(common_values)


OI_Data=[[17050.0, 47034, 280.0, 47041, 13227.0, 1418.0, 44126.0, 1417.0, 44570.0],
[17100.0, 47044, 1661.0, 47067, 47884.0, -814.0, -2730.0, -815.0, -3213.0],
[17150.0, 47068, 705.0, 47088, 10893.0, 6456.0, 74824.0, 6628.0, 75006.0],
[17200.0, 47089, 8296.0, 47102, 40693.0, -5144.0, 5121.0, -5078.0, 3525.0],
[17250.0, 47109, 3312.0, 47110, 14859.0, 25680.0, 82236.0, 26327.0, 82132.0],
[17300.0, 47115, 39155.0, 47116, 63904.0, -23648.0, -11071.0, -23468.0, -9876.0],
[17350.0, 47117, 27640.0, 47120, 19559.0, 60559.0, 174657.0, 60543.0, 174638.0],
[17400.0, 47121, 130134.0, 47122, 60749.0, -91321.0, 22872.0, -89483.0, 22285.0],
[17450.0, 47128, 34332.0, 47129, 7473.0, 132930.0, 193904.0, 135768.0, 182104.0],
[17500.0, 47131, 97666.0, 47139, 28771.0, -44556.0, -1434.0, -43691.0, -2922.0],
[17550.0, 47140, 27161.0, 47192, 4383.0, 66672.0, 34776.0, 64096.0, 32774.0],
[17600.0, 47197, 68267.0, 47213, 10550.0, -16861.0, -1378.0, -15443.0, -1572.0],
[17650.0, 47214, 38387.0, 47222, 2063.0, 53982.0, 13037.0, 52487.0, 12968.0],
[17700.0, 47223, 53921.0, 47278, 5559.0, 13442.0, -2557.0, 13037.0, -2578.0],
[17750.0, 47279, 26479.0, 47280, 990.0, 76200.0, 6332.0, 75433.0, 6260.0]]

"""Now wait for to get 2 Reduction and Cumulative Shift to intiate trade"""
count=1
count1=0
cumlative_shift=True

while (count<2 and count1<2) or cumlative_shift :
	response = xt.get_quote(
    	Instruments=instruments,
    	xtsMessageCode=1512,
    	publishFormat='JSON')
	json_string = response['result']['listQuotes'][0]
	data = json.loads(json_string)
	Nifty_SP=data['LastTradedPrice']
	print('Spot Price:',data['LastTradedPrice'])

	response = xt.get_quote(
			Instruments=instruments_OI,
			xtsMessageCode=1510,
			publishFormat='JSON')
	#print(response)
	for i in range(30):
		j=0
		json_string = response['result']['listQuotes'][i]
		data=json.loads(json_string)
		OpenInterest=data["OpenInterest"]
		if i%2==0:
			Change=((OpenInterest/50)-OI_Data[int(i/2)][j+2])
			OI_Data[int(i/2)][j+7]=OI_Data[int(i/2)][j+5]
			OI_Data[int(i/2)][j+5]=Change
		else:
			Change=((OpenInterest/50)-OI_Data[int(i/2)][j+4])
			OI_Data[int(i/2)][j+8]=OI_Data[int(i/2)][j+6]
			OI_Data[int(i/2)][j+6]=Change	
	print("Strike" + "  "+ "  Call"+"  "+"  "+"OI_C"+"   "+"Put" +"  "+ "  OI_P" +" " + "C_C_OI" +"   "+ "C_P_OI" +"  "+ "R_C_C_OI"+"  "+"R_P_P_OI")
	for rows in OI_Data:
		print(rows)

	today = pd.Timestamp.today().normalize()
	prev_workday = (today - BDay(1)).normalize()
	prev_day= prev_workday.strftime('%b %d %Y')
	# print(prev_workday)
	response = xt.get_ohlc(
	exchangeSegment=xt.EXCHANGE_NSECM,
	exchangeInstrumentID=26000,
	startTime=prev_day + " 090000",
	endTime=prev_day + " 160000",
	compressionValue=450000)
	a=response['result']['dataReponse'].split('|')

	response = xt.get_quote(
	    Instruments=instruments,
	    xtsMessageCode=1512,
	    publishFormat='JSON')
	#print('Quote :', response['result']['listQuotes'][0])
	json_string = response['result']['listQuotes'][0]
	data = json.loads(json_string)
	Nifty_SP=data['LastTradedPrice']
	#print('Spot Price:',data['LastTradedPrice'])
	if (float(data['LastTradedPrice']) > float(a[4])):
		print("Teji")
		rows=np.where(A==selected_check[0])[0].tolist()
		rows1=np.where(A==selected_check[1])[0].tolist()
		rows2=np.where(A==selected_check[2])[0].tolist()
		rows3=np.where(A==selected_check[3])[0].tolist()
		print(str(OI_Data[rows[0]][7]) + " > " + str(OI_Data[rows[0]][5]))
		print(str(OI_Data[rows1[0]][7]) + " > " + str(OI_Data[rows1[0]][5]))
		print(str(OI_Data[rows2[0]][7]) + " > " + str(OI_Data[rows2[0]][5]))
		print(str(OI_Data[rows3[0]][8]) + " < " + str(OI_Data[rows3[0]][6]))
		print(OI_Data[rows[0]][7]-OI_Data[rows[0]][5] > 0)
		print(OI_Data[rows1[0]][7]-OI_Data[rows1[0]][5] > 0 )
		print(OI_Data[rows2[0]][7]-OI_Data[rows2[0]][5]>0)
		print(OI_Data[rows3[0]][8] - OI_Data[rows3[0]][6] < 0 )

		if(OI_Data[rows[0]][7]-OI_Data[rows[0]][5] > 0 
			and OI_Data[rows1[0]][7]-OI_Data[rows1[0]][5] > 0 
			and OI_Data[rows2[0]][7]-OI_Data[rows2[0]][5]>0
			and OI_Data[rows3[0]][8] - OI_Data[rows3[0]][6] < 0 
			):
			print("Call Reduction in all 3 OI's and Highest OI addition in Put")
			count=count+1
		"""Cumulative Shift   total of call = 2 + 5 < total of put 4 + 7"""
		for i in common_values:
			rows4=np.where(A==i)[0].tolist()
			print(str(OI_Data[rows4[0]][2])+" + "+str(OI_Data[rows4[0]][5])+ " < "+ str(OI_Data[rows4[0]][4]) +" + "+ str(OI_Data[rows4[0]][6]))
			print((OI_Data[rows4[0]][2] + OI_Data[rows4[0]][5]) < (OI_Data[rows4[0]][4] + OI_Data[rows4[0]][6]))
			if((OI_Data[rows4[0]][2] + OI_Data[rows4[0]][5]) < (OI_Data[rows4[0]][4] + OI_Data[rows4[0]][6])):
				cumlative_shift=False

		 			
	else:
		rows=np.where(A==selected_check[3])[0].tolist()
		rows1=np.where(A==selected_check[4])[0].tolist()
		rows2=np.where(A==selected_check[5])[0].tolist()
		rows3=np.where(A==selected_check[0])[0].tolist()
		# print(OI_Data[rows[0]][0])
		print("Mandi")	
		if(OI_Data[rows[0]][8]-OI_Data[rows[0]][6] > 0 
			and OI_Data[rows1[0]][8]-OI_Data[rows1[0]][6] > 0 
			and OI_Data[rows2[0]][8]-OI_Data[rows2[0]][6] >0 
			and OI_Data[rows3[0]][7] - OI_Data[rows3[0]][5] < 0 ):
			print("Put Reduction in all 3 OI's and Highest OI addition in Call")
			count1=count1+1
		"""Cumulative Shift  total of call = 2 + 5 > total of put 4 + 7"""			
		for i in common_values:
			rows4=np.where(A==i)[0].tolist()
			if((OI_Data[rows4[0]][2] + OI_Data[rows4[0]][5]) > (OI_Data[rows4[0]][4] + OI_Data[rows4[0]][6])):
				cumlative_shift=False	

	
	time.sleep(900)
print(curr_tm_chk)		
# print(max(col_values_CE))
# print(max(col_values_PE))




    

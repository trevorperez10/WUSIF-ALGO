import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup

# specify the url
import urllib.request


headers = {
    'x-rapidapi-host': "yh-finance.p.rapidapi.com",
    'x-rapidapi-key': "ea0fe23a72mshbfc9dfafe36fc9dp1870e7jsnbb7a2a7713ff"
    }
url = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"

debtToEquity = []
priceToBVRatio = []
priceToSalesRatio = []
returnOnEquity = []
price = []
stocks = []
stocksBT = []

debtToEquityHist = []
priceToBVRatioHist = []
priceToSalesRatioHist = []
returnOnEquityHist = []
priceHist = {}
num_Indicators = 4
#function that webscrapes list of stocks to test 
def webscrape():
	class AppURLopener(urllib.request.FancyURLopener):
		version = "Mozilla/5.0"
	opener = AppURLopener()
	response = opener.open('https://www.stockmonitor.com/nasdaq-stocks/')
	soup = BeautifulSoup(response, 'html.parser')
	stocks = []
	content = soup.find('table').findAll('a')
	for i in content:
		stocks.append(i.text.strip())
	return stocks

#function that finds values for indicators for each company
def stockInfo(x):
	headers = {
    'x-rapidapi-host': "yh-finance.p.rapidapi.com",
    'x-rapidapi-key': "ea0fe23a72mshbfc9dfafe36fc9dp1870e7jsnbb7a2a7713ff"
    }
	url = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"
	#call stock api
	querystring = {"symbol":x}
	session = Session()
	session.headers.update(headers)
	response = session.get(url, params=querystring)
	data = json.loads(response.text)
	#sort through data for financial values
	
	#debt to equity
	print(x)
	liab = data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][0]['totalLiab']['raw']
	equity = data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][0]['totalStockholderEquity']['raw']
	#price to bv 
	marketPricePerShare=data['price']['regularMarketPrice']['raw']
	totalassets = data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][0]['totalAssets']['raw']
	marketCap = data['price']['marketCap']['raw']
	sharesoutstanding = marketCap/marketPricePerShare
	bookvalue=totalassets-liab
	bvpershare=bookvalue/sharesoutstanding
	#price to sales
	#marketCap found above
	revenue = data['incomeStatementHistoryQuarterly']['incomeStatementHistory'][0]['totalRevenue']['raw']
	#return on equity
	netIncome= data[ 'incomeStatementHistoryQuarterly']['incomeStatementHistory'][0]['netIncome']['raw']
	#equity found above
	#additional

	#add indicators to arrays
	price.append(marketPricePerShare)
	debtToEquity.append(liab/equity)
	priceToBVRatio.append(marketPricePerShare/bvpershare)
	priceToSalesRatio.append(marketCap / revenue)
	returnOnEquity.append(netIncome/equity)

#function that finds values for indicators for each company

def HistPrices(x):
	print(x)
	#try:
	url = "https://alpha-vantage.p.rapidapi.com/query"
	querystring = {"symbol":x,"function":"TIME_SERIES_MONTHLY_ADJUSTED","datatype":"json"}
	headers = {
	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
	"X-RapidAPI-Key": "ea0fe23a72mshbfc9dfafe36fc9dp1870e7jsnbb7a2a7713ff"
	}

	response = requests.request("GET", url, headers=headers, params=querystring)
	data = json.loads(response.text)
	try:
		price = data["Monthly Adjusted Time Series"]["2017-12-29"]["4. close"]
		print('tried')
		priceHist[x] = price
	except:
		print ('failed')
		stocksBT.remove(x)


def backtest(x):
	#call stock api
	querystring = {"symbol":x}
	session = Session()
	session.headers.update(headers)
	response = session.get(url, params=querystring)
	data = json.loads(response.text)
	#sort through data for financial values
	
	#debt to equity
	try:
		liab = data['balanceSheetHistory']['balanceSheetStatements'][3]['totalLiab']['raw']
		equity = data['balanceSheetHistory']['balanceSheetStatements'][3]['totalStockholderEquity']['raw']
	#price to bv 

		equity=data['balanceSheetHistory']['balanceSheetStatements'][3]['totalStockholderEquity']['raw']
		commonStock = data['balanceSheetHistory']['balanceSheetStatements'][3]['commonStock']['raw']
		
	# print(commonStock)
		marketPricePerShare = float(priceHist[x])
		totalassets = data['balanceSheetHistory']['balanceSheetStatements'][3]['totalAssets']['raw']
		marketCap = equity * commonStock
		bookvalue=totalassets-liab
		bvpershare=bookvalue/equity
	#price to sales
	#marketCap found above
		revenue = data['incomeStatementHistory']['incomeStatementHistory'][3]['totalRevenue']['raw']
	#return on equity
		netIncome= data[ 'incomeStatementHistory']['incomeStatementHistory'][3]['netIncome']['raw']
	#equity found above
	#additional

	#add indicators to arrays
	#priceHist.append(marketPricePerShare)
		debtToEquityHist.append(liab/equity)
		priceToBVRatioHist.append(marketPricePerShare/bvpershare)
		priceToSalesRatioHist.append(marketCap / revenue)
		returnOnEquityHist.append(netIncome/equity)
	except KeyError:
		print("bt")
		print(x)
		stocksBT.remove(x)
		del priceHist[x]




#function that normalizes the data to balance different indicators 
def normalize(arr):
	mn = min(arr)
	mx = max(arr)
	normed = []
	for i in arr:
		standard = (i - mn)/(mx-mn)
		normed.append(standard)
	return normed

def score(stocks, ndte, nptbv, npts, nroe):
	scores = {}
	for i in range(len(stocks)):
		ticker = stocks[i]
		dteScore = abs(ndte[-1] - ndte[i])
		ptbvScore = abs(nptbv[-1] - nptbv[i])
		ptsScore = abs(npts[-1] - npts[i])
		roeScore = abs(nroe[-1] - nroe[i])
		scoreVal = dteScore + ptbvScore + ptsScore + roeScore
		scores[ticker] = (scoreVal)
	return scores





#main function
if __name__ == "__main__":

	stocks = webscrape()
	stocksBT = stocks
	print (stocksBT)
	#stocks = ["TSLA", "FB", "AAPL"]
	#stocks = ['ABT']
	for i in stocks:
		#stockInfo(i)
		HistPrices(i)
	print(stocksBT)
	print(priceHist)
	for i in stocksBT:
		backtest(i)

	#for i in stocks:
	#	stockInfo(i)
	#print('ABT')
	print(stocksBT)
	print(priceHist)
	#debtToEquity.append(.7)
	#priceToSalesRatio.append(1.5)
	#priceToBVRatio.append(.5)
	#returnOnEquity.append(.2)
	debtToEquityHist.append(.7)
	priceToSalesRatioHist.append(1.5)
	priceToBVRatioHist.append(.5)
	returnOnEquityHist.append(.2)
	
	#ndte = normalize(debtToEquity)
	#nptbv = normalize(priceToBVRatio)
	#npts = normalize(priceToSalesRatio)
	#nroe = normalize(returnOnEquity)
	print(debtToEquityHist)
	ndte = normalize(debtToEquityHist)
	nptbv = normalize(priceToBVRatioHist)
	npts = normalize(priceToSalesRatioHist)
	nroe = normalize(returnOnEquityHist)
	print(ndte)
	scores = score(stocksBT, ndte, nptbv, npts, nroe)
	sortedScores = sorted(scores.items(), key=lambda x: x[1])
	print (sortedScores)

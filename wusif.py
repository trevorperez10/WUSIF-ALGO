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
	revenue = data['incomeStatementHistory']['incomeStatementHistory'][0]['totalRevenue']['raw']
	#return on equity
	netIncome= data[ 'incomeStatementHistoryQuarterly']['incomeStatementHistory'][0]['netIncome']['raw']
	#equity found above
	#additional

	#add indicators to arrays
	debtToEquity.append(liab/equity)
	priceToBVRatio.append(marketPricePerShare/bvpershare)
	priceToSalesRatio.append(marketCap / revenue)
	returnOnEquity.append(netIncome/equity)

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
	stocks = stocks[0:-3]
	print (stocks)
	#stocks = ["TSLA", "FB", "AAPL"]
	#stocks = ['ABT']
	for i in stocks:
		stockInfo(i)
	#print('ABT')
	debtToEquity.append(.7)
	priceToSalesRatio.append(1.5)
	priceToBVRatio.append(.5)
	returnOnEquity.append(.2)
	ndte = normalize(debtToEquity)
	nptbv = normalize(priceToBVRatio)
	npts = normalize(priceToSalesRatio)
	nroe = normalize(returnOnEquity)
	scores = score(stocks, ndte, nptbv, npts, nroe)
	sortedScores = sorted(scores.items(), key=lambda x: x[1])
	print (sortedScores)
	#print(stocks)
	#stockInfo("TSLA")
	#stockInfo("FB")
	#print(debtToEquity)
	#print(normDTE)
	#np.insert(stock, stockInfo("FB"))
	#print ("debt to equity ratio: " + str(liab / equity)) #low debt to equity ratio = good, mulitply by -1 for score 
	##print ("price to earnings ratio: ")
	#print("price to BV ratio: " +str(marketPricePerShare/bvpershare))
	#print ("price to sales ratio: " + str(marketCap / revenue))#low price to sales ratio = good, multiple by -1 for score 
	#print("return on equity: " + str(netIncome/equity))
#645324000
#print(response.text)

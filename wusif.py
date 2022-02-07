from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


url = "https://yh-finance.p.rapidapi.com/stock/v2/get-financials"

querystring = {"symbol":"AMRN","region":"US"}

headers = {
    'x-rapidapi-host': "yh-finance.p.rapidapi.com",
    'x-rapidapi-key': "ea0fe23a72mshbfc9dfafe36fc9dp1870e7jsnbb7a2a7713ff"
    }

 
session = Session()
session.headers.update(headers)
response = session.get(url, params=querystring)
data = json.loads(response.text)
liab = data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][0]['totalLiab']['raw']
equity = data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][0]['totalStockholderEquity']['raw']
marketCap = data['price']['marketCap']['raw']
revenue = data['incomeStatementHistory']['incomeStatementHistory'][0]['totalRevenue']['raw']
print (revenue)
print (marketCap)
print (liab)
print (equity)
print ("debt to equity ratio: " + str(liab / equity)) #low debt to equity ratio = good, mulitply by -1 for score 
print ("price to sales ratio: " + str(marketCap / revenue))#low price to sales ratio = good, multiple by -1 for score 
#645324000
#print(response.text)

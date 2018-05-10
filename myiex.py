import requests
import matplotlib.pyplot as plt
def keystats(symbol):
    r = requests.get("https://api.iextrading.com/1.0/stock/{}/stats".format(symbol))
    return r.json()
def price(symbol):
    r = requests.get("https://api.iextrading.com/1.0/stock/{}/pirce".format(symbol))
    return r.text
def quote(symbol):

    r = requests.get("https://api.iextrading.com/1.0/stock/{}/quote".format(symbol))
    return r.json()
    
def oneday_price(symbol):
    r = requests.get("https://api.iextrading.com/1.0/stock/{}/chart/1d".format(symbol))
    return r.json()
def single_stock_overview(symbol):
    r = requests.get("https://api.iextrading.com/1.0/stock/{}/batch?types=quote,company,chart&range=1d".format(symbol))
    return r.json()
def multi_1year_data(symbols):
    sb = ''
    for i in symbols:
        sb = sb + i + ','
        r = requests.get(
            "https://api.iextrading.com/1.0/stock/market/batch?symbols={}&types=chart&range=2y".format(sb[:-1]))
    return r.json()

def batch_quote_and_oneday(symbols):
    sb = ''
    for i in symbols:
        sb = sb + i + ','
    r = requests.get("https://api.iextrading.com/1.0/stock/market/batch?symbols={}&types=quote,chart&range=1d".format(sb[:-1]))
    return r.json()

# symbol = ('fb','aapl','baba','googl')
# c = batch_quote_and_oneday(symbol)
# for i in c:
#     print(i)
"""
symbol = 'fb'
a = oneday_price(symbol)

def plot_timeseries(daily):
    time_series = [i['marketOpen'] for i in daily]
    plt.figure(figsize = (2,0.8),dpi = 100)
    plt.plot(time_series)

    plt.axis('off')
    #plt.tight_layout()
    #plt.show()
    plt.margins(0)
    plt.savefig('test2.png')
    return plt

myplt = plot_timeseries(a)
"""

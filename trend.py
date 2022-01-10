from contextlib import redirect_stderr
import warnings
warnings.filterwarnings('ignore')
# import libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import investpy as inv
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.signal import argrelextrema

def get_data(symbol,n=2):
    # download quotes
    df = inv.get_crypto_historical_data(crypto=symbol,
                                           from_date='01/01/2021',
                                           to_date='10/10/2022')
    #get_stock_historical_data(stock=symbol,
                                         #   country='United States',
                                          #  from_date='01/01/2015',
                                           # to_date='01/12/2022')
    # create difference pct from previous close
    df['change_pct'] = df['Close'].pct_change() *100
    df['change'] = df['Close'].diff()
    df['range'] = df.High - df.Low

    # drop na values (e.g. 1 change% will be na)
    df.dropna(inplace=True)

    # normalize volume, change & change %
    # df['zchange'] = stats.zscore(df.change)
    # df['zchange_pct'] = stats.zscore(df.change_pct)
    # df['zvol'] = stats.zscore(df.Volume)
    # df['zrange'] = stats.zscore(df.range)

    # Find local min and max
    df['xmax']=df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']
    df['xmin']=df.iloc[argrelextrema(df.Close.values, np.less, order=n)[0]]['Close']

    # trend indicator
    df['line']=(df['xmin'] + df['xmax'])/2
    df['line'].fillna(df['xmax'],inplace=True)
    df['line'].fillna(df['xmin'],inplace=True)
    df['line'].ffill(inplace=True)
    return df

def collect_all(quotes):
    quotes_data = defaultdict() 

    for quote in quotes:
        try:
            quotes_data[quote] = get_data(quote)
            
        except RuntimeError:
            print(quote,"could not be fetched!")
            
    return quotes_data


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def get_slope(dates,prices):
    dates = to_integer(dates)
    slope, intercept = np.polyfit(dates,prices,1)
    return slope
    
def getSlopeColor(slope_max,slope_min):
    if slope_max < 0 and slope_min < 0:
        color = "red"
    elif slope_max > 0 and slope_min > 0:
        color = "green"
    else:
        color="black"
    return color
#part1
# quotes_data = {}
quotes = ["XRP"]#["bitcoin","Ethereum","Binance Coin","XRP"]#inv.stocks.get_stocks_list(country="United States")[:4]
quotes_data = collect_all(quotes)
quotes = quotes_data.keys()
df = quotes_data['XRP'][-200:-50]
# df['line']=(df['xmin'] + df['xmax'])/2
# df['line'].fillna(df['xmax'],inplace=True)
# df['line'].fillna(df['xmin'],inplace=True)

# print(trend.columns)
trend = df['line'].dropna()
trend = trend[-5:]
print(df)
slope = get_slope(trend.index,trend)
local_maxs = df['xmax'].dropna()[-2:]
local_mins = df['xmin'].dropna()[-2:]
slope_max = get_slope(local_maxs.index,local_maxs)
slope_min = get_slope(local_mins.index,local_mins)



color = getSlopeColor(slope_max,slope_min)
print(slope)

plt.figure(figsize=(20,10))
plt.plot(df.index,df.Close)
# plt.scatter(trend.index,trend)
# plt.plot(trend.index,trend,c="purple")
plt.scatter(df.index,df.xmax,c='r')
plt.scatter(df.index,df.xmin,c='g')
plt.plot(local_maxs.index,local_maxs,c=color)
plt.plot(local_mins.index,local_mins,c=color)

plt.show()

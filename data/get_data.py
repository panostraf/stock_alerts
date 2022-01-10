import investpy as inv
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import numpy as np
import statistics
from scipy.stats import norm



def get_data(symbol):
    # df = inv.get_stock_historical_data(stock='AAPL',
    #                                     country='United States',
    #                                     from_date='01/01/2021',
    #                                     to_date='01/01/2023')
    df = inv.get_crypto_historical_data(crypto=symbol,
                                           from_date='01/01/2021',
                                           to_date='10/10/2023')
    df = df[-110:]
    return df

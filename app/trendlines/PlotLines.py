from itsdangerous import exc
from pandas.core.frame import DataFrame
from app.trendlines.trends import *
import plotly.express as px
import matplotlib.pyplot as plt
import datetime as dt
import plotly.graph_objects as go
import investpy as inv
from app.data.get_data import get_data




def main(symbol,n=3,
    minAngle=0.001,
    maxnLines=1):

    df = get_data(str(symbol))
    original_df = df
    
    # df = df.iloc[-int(df_range):]
    #print(float(df.Close[-1]))
    last = float(df.Close[-1])

    std = round(df.Close.std(),2)

    # Data transformation
    df = LocalMinMax.addLocalMinMax(df,n=n)
    df.reset_index(inplace=True)
    df.reset_index(inplace=True)
    # Get an index for each date in a new dataframe
    
    df.rename({"index":"datePoint"},inplace=True,axis=1)
    dates = df[['datePoint',"Date"]]
    dates['Date'] = dates['Date'].astype(str)
    df.drop("datePoint",axis=1,inplace=True)
    df.set_index("Date",inplace=True)




    linesXmin = Lines().getLinesFromMin(df,angle_threshold=minAngle,maxnlines = maxnLines)
    linesXmax = Lines().getLinesFromMax(df,angle_threshold=minAngle,maxnlines = maxnLines)
    print("MIN MAX")
    print(linesXmax)
    print("\n\n\n...........................")
    print(linesXmin)
    print("\n\n\n...........................")
    

    if (len(linesXmin) > 0) and (len(linesXmax) >0):
        trend_dates = pd.concat([linesXmax[['Date2','slope','intercept','days']],linesXmin[['Date2','slope','intercept','days']]])
    elif len(linesXmax) > 0 :
        trend_dates = linesXmax[['Date2','slope','intercept','days']]
    elif len(linesXmin) > 0 :
        trend_dates = linesXmin[['Date2','slope','intercept','days']]
    else:
        downtrends = {}
        downtrends['Date'] = ["2021-01-01"]
        downtrends['Close'] = [0]
        uptrends = {}
        uptrends['Date'] = ["2021-01-01"]
        uptrends['Close'] = [0]
        return last, std, "neutral", original_df,uptrends,downtrends
        
    
    
    downtrends = {}
    if len(linesXmax.index>0):
        
        linesXmax = linesXmax[['Date','Date2','xmax','xmax2']].to_dict('list')
        for i in range(len(linesXmax['Date'])):
            try:
                # x = [ for d in dates]
                point1 = [(dt.datetime.strptime(linesXmax['Date'][i],'%Y-%m-%d').date()), linesXmax['xmax'][i]]
                point2 = [(dt.datetime.strptime(linesXmax['Date2'][i],'%Y-%m-%d').date()), linesXmax['xmax2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                
                downtrends['Date'] = [d.strftime('%Y-%m-%d') for d in x_values]
                downtrends['Close'] = y_values
            except KeyError:
                pass
    else:
        downtrends['Date'] = ["2021-01-01"]
        downtrends['Close'] = [0]

    uptrends = {}
    if len(linesXmin.index>0):
        linesXmin = linesXmin[['Date','Date2','xmin','xmin2']].to_dict('list')
        for i in range(len(linesXmin['Date'])):
            # x = [ for d in dates]
            try:
                point1 = [(dt.datetime.strptime(linesXmin['Date'][i],'%Y-%m-%d').date()), linesXmin['xmin'][i]]
                point2 = [(dt.datetime.strptime(linesXmin['Date2'][i],'%Y-%m-%d').date()), linesXmin['xmin2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                uptrends['Date'] = [d.strftime('%Y-%m-%d') for d in x_values]
                uptrends['Close'] = y_values

            except KeyError:
                pass
    else:
        uptrends['Date'] = ["2021-01-01"]
        uptrends['Close'] = [0]
    
   

    last_trend_date = trend_dates['Date2'].max()
    last_trend = ""
    last_slope = float(trend_dates[trend_dates['Date2'] ==last_trend_date].sort_values(by='days',ascending=False).head(1)['slope'])
    print("LAST SLOPE",last_slope)


    try:
        last_slope = float(last_slope)
    except:
        last_slope = 0
    if float(last_slope) < 0.01:
        last_trend = "DownTrend"
    elif float(last_slope) > 0.01:
        last_trend = "Uptrend"
    else:
        last_trend = "Neutral"
    
    original_df['Date'] = original_df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
    print("\n\n\n")

    print('uptrends')
    print(uptrends)
    print("downtrends:")
    print(downtrends)

    print("\n\n\n")
    return last, std, last_trend, original_df,uptrends,downtrends
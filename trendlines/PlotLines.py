from pandas.core.frame import DataFrame
from trendlines.trends import *
import plotly.express as px
import matplotlib.pyplot as plt
import datetime as dt
import plotly.graph_objects as go
import investpy as inv
from data.get_data import get_data




def main(symbol,n=4,
    minAngle=0.005,
    maxnLines=2):

    df = get_data(str(symbol))
    original_df = df
    print(float(df.Close[-1]))
    last = float(df.Close[-1])



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
    # print(len(linesXmin))
    # print(len(linesXmax))

    # fig = px.line(df, x="Date", y="Close")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name="Close",line = dict(color='royalblue', width=4),
    line_shape='linear'))
    
    if len(linesXmax.index>0):
        linesXmax = linesXmax[['Date','Date2','xmax','xmax2']].to_dict('list')
        for i in range(len(linesXmax['Date'])):
            try:
                # x = [ for d in dates]
                point1 = [(dt.datetime.strptime(linesXmax['Date'][i],'%Y-%m-%d').date()), linesXmax['xmax'][i]]
                point2 = [(dt.datetime.strptime(linesXmax['Date2'][i],'%Y-%m-%d').date()), linesXmax['xmax2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                # plt.plot(x_values,y_values)
                # fig.add_trace(x=x_values,y=y_values)
                fig.add_trace(go.Scatter(x=x_values, 
                                        y=y_values, 
                                        name=f"Downtrend - {str(i+1)}",
                                        line_shape='linear'))
            except KeyError:
                pass

    if len(linesXmin.index>0):
        linesXmin = linesXmin[['Date','Date2','xmin','xmin2']].to_dict('list')
        for i in range(len(linesXmin['Date'])):
            # x = [ for d in dates]
            try:
                point1 = [(dt.datetime.strptime(linesXmin['Date'][i],'%Y-%m-%d').date()), linesXmin['xmin'][i]]
                point2 = [(dt.datetime.strptime(linesXmin['Date2'][i],'%Y-%m-%d').date()), linesXmin['xmin2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                fig.add_trace(go.Scatter(x=x_values, 
                                        y=y_values, 
                                        name=f"Uptrend - {str(i+1)}",
                                        line_shape='linear'))
            except KeyError:
                pass
    
    fig = addLocalMinMaxLine(pd.DataFrame(df),fig,n=n)

    fig.update_layout(
    autosize=True,
    
    # style={'width':'100%',
    # 'height':'100%'}
    # ,
    height=1080,
    width=1920,
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        # pad=4)
    )
    )
    fig.update_layout(autosize=True)
    fig.update_layout(showlegend=False)
    
    return fig, last




def addLocalMinMaxLine(df,fig,n):
    
    
    df,color,local_maxs,local_mins,slope = Lines().getMinMaxLine(df,n)
    print("...........111111111111111111")
    print(df)
    print("..............")
    print("///////////22222222222222222")
    print("||||||||||||||||")
    fig.add_trace(go.Scatter(x=df.Date, y=df.line, name=f"test", line = dict(color='royalblue', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=df.Date, y=df.xmax, name=f"tops", mode = 'markers',fillcolor="red"))
    fig.add_trace(go.Scatter(x=df.Date, y=df.xmin, name=f"bottoms",  mode = 'markers',fillcolor="green"))
    # fig.add_trace(go.Scatter(x=df.Date, y=df.max))
    # fig.add_trace(go.Scatter(x=df.Date, y=df.min))

    return fig

    # plt.figure(figsize=(20,10))
    # plt.plot(df.index,df.Close)
    # # plt.scatter(trend.index,trend)
    # # plt.plot(trend.index,trend,c="purple")
    # plt.scatter(df.index,df.xmax,c='r')
    # plt.scatter(df.index,df.xmin,c='g')
    # plt.plot(local_maxs.index,local_maxs,c=color)
    # plt.plot(local_mins.index,local_mins,c=color)


if __name__=="__main__":
    import investpy as inv
    symbol = "XRP"
    df = inv.get_crypto_historical_data(crypto=symbol,
                                           from_date='01/01/2021',
                                           to_date='01/01/2022')

    # df.to_csv("data2.csv")

    # API Data Pull
    # df = pd.read_csv("data2.csv")
    df = df[-120:]
    print(df)

    #SET PARAMETERS
    n=4
    minAngle=0.005
    maxnLines=2

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

    print(df)
    linesXmin = Lines().getLinesFromMin(df,angle_threshold=minAngle,maxnlines = maxnLines)
    linesXmax = Lines().getLinesFromMax(df,angle_threshold=minAngle,maxnlines = maxnLines)
    # print(linesXmin)
    # print(len(linesXmin))
    # print(linesXmin['Date'])
    
    
    print(len(linesXmin))
    print(len(linesXmax))
    # exit(-1)
    plt.plot(df.Date,df.Close)
    if len(linesXmin.index>0):
        linesXmin = linesXmin[['Date','Date2','xmin','xmin2']].to_dict('list')
        for i in range(len(linesXmin['Date'])):
            # x = [ for d in dates]
            try:
                point1 = [(dt.datetime.strptime(linesXmin['Date'][i],'%Y-%m-%d').date()), linesXmin['xmin'][i]]
                point2 = [(dt.datetime.strptime(linesXmin['Date2'][i],'%Y-%m-%d').date()), linesXmin['xmin2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                plt.plot(x_values,y_values)
            except KeyError:
                pass
    if len(linesXmax.index>0):
        linesXmax = linesXmax[['Date','Date2','xmax','xmax2']].to_dict('list')
        for i in range(len(linesXmax['Date'])):
            try:
                # x = [ for d in dates]
                point1 = [(dt.datetime.strptime(linesXmax['Date'][i],'%Y-%m-%d').date()), linesXmax['xmax'][i]]
                point2 = [(dt.datetime.strptime(linesXmax['Date2'][i],'%Y-%m-%d').date()), linesXmax['xmax2'][i]]
                x_values = [point1[0], point2[0]]
                y_values = [point1[1], point2[1]]
                plt.plot(x_values,y_values)
            except KeyError:
                pass
    plt.xticks(rotation=45)
    plt.show()
    exit(-1)
    point1 = [linesXmin['Date'], linesXmin['xmin']]
    point2 = [linesXmin['Date2'], linesXmin['xmin2']]

    point1DOWN = [linesXmax['Date'], linesXmax['xmax']]
    point2DOWN = [linesXmax['Date2'], linesXmax['xmax2']]

    xlabels=[]
    dates['Date'] = pd.to_datetime(dates['Date'], format='%Y%m%d', errors='ignore')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='ignore')
    for d in dates['Date'].tolist()[::5]:
        xlabels.append(d)

    plt.plot(df.Date,df.Close)
    # print(df.columns)
    for i in range(len(linesXmin['Date'])):
        # print(i)
        # print(type(point1[0][i]))
        # print(point1[0][i])
        x_values = [point1[0][i],point2[0][i]]
        y_values = [point1[1][i],point2[1][i]]
        
        plt.plot(x_values,y_values)

    # for i in range(len(linesXmax['Date'])):
    #     # print(i)
    #     x_values = [point1DOWN[0][i],point2DOWN[0][i]]
    #     y_values = [point1DOWN[1][i],point2DOWN[1][i]]
        
    #     plt.plot(x_values,y_values)
    # plt.xticks(xlabels,rotation=45)
    # plt.locator_params(axis="x", nbins=100)
    plt.show()
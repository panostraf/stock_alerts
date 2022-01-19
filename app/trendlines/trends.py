from scipy.signal import argrelextrema
import pandas as pd
import numpy as np
from sklearn.utils.extmath import cartesian
from datetime import datetime
import math
from scipy.spatial.distance import pdist, squareform
# from trend import get_slope


class LocalMinMax:
    def __init__(self,
                df, #data dates + OHLC,
                n=4):
        self.df = df

    @staticmethod
    def addLocalMinMax(df,n=4):
        df['xmax']=df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']
        df['xmin']=df.iloc[argrelextrema(df.Close.values, np.less, order=n)[0]]['Close']
        return df

    @staticmethod
    def LocalMax(df,n=4):
        df['xmax']=df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']
        return df

    @staticmethod
    def LocalMin(df,n=4):
        df['xmin']=df.iloc[argrelextrema(df.Close.values, np.less, order=n)[0]]['Close']
        return df


class Lines:
    def __init__(self):
        self.uptrends = {}
        self.downtrends = {}


    def getLinesFromMin(self,df,angle_threshold=0.005,maxnlines=5):
        df.reset_index(inplace=True)
        dates = df['Date']
        dates=dates.reset_index()
        # ##print(dates)

        # Keep only pairs with local minimum
        df = df[df.xmin.notnull()]
        

        temp_dates = df.Date
        # Create all date combinations
        temp_data = pd.DataFrame(cartesian((temp_dates, temp_dates)))
        temp_data.columns = ["Date","Date2"]
        
        temp_data = pd.merge(temp_data,df[["Date","xmin"]],how="left",on="Date")
        temp_data = pd.merge(temp_data,df[["Date","xmin"]],how="left",left_on="Date2",right_on="Date")
        temp_data.drop("Date_y",inplace=True,axis=1)
        temp_data.columns = ["Date","Date2","xmin","xmin2"]
        
        # Filter duplicated dates from cartesian
        temp_data = temp_data[(temp_data['Date']) != (temp_data['Date2'])]
        

        # Keep only upwards trend lines
        temp_data = temp_data[temp_data["xmin2"]>=temp_data['xmin']]


        # temp_data = temp_data[temp_data["Date"]<temp_data["Date2"]]
        temp_data.reset_index(inplace=True)
        temp_data.drop("index",axis=1,inplace=True)
        # df.reset_index(inplace=True)

        temp_data['minimum'] = 0

        # Find minimum close of the period
        # TODO make it using .apply()
        for i in range(len(temp_data)):
            d1 = temp_data.Date.astype("datetime64").loc[i]
            d2 = temp_data.Date2.astype("datetime64").loc[i]
            minimum = np.min(df['Close'][(df['Date'].astype("datetime64")>=d1) & (df['Date'].astype("datetime64")<=d2)])
            # ##print(minimum)
            # ##print(d1,d2,minimum)
            temp_data["minimum"].loc[i] = minimum

        temp_data.dropna(inplace=True)

        # Drop lines where min close of the period > starting point of the line
        temp_data = temp_data[(temp_data['minimum'])>=(temp_data['xmin'])]

        temp_data_group = temp_data.groupby("xmin2").count()['Date']
        # ##print(temp_data_group)
        # Count how strong each line is
        temp_data = temp_data.merge(temp_data_group,
                                    left_on="xmin2",
                                    right_on=temp_data_group.index,
                                    how='inner')
        # rename and reset columns
        temp_data.columns = ["Date","Date2","xmin","xmin2","minimum","importance"]
        temp_data=temp_data.sort_values(by='importance',ascending=False)

        # use n of days to define the longest trends
        temp_data['days'] = temp_data['Date2'].astype("datetime64") - temp_data['Date'].astype("datetime64")


        
        # Use date points instead of dates to calculate slopes
        temp_data2 = temp_data.merge(dates,left_on='Date',right_on="Date",how="inner")
        temp_data2.rename(columns={"index":"DateIndex"},inplace=True)
        temp_data2 = temp_data2.merge(dates,left_on='Date2',right_on="Date",how="inner")
        temp_data2.rename(columns={"index":"DateIndex2"},inplace=True)
        temp_data2.drop('Date_y',axis=1,inplace=True)
        temp_data2.rename(columns={'Date_x':'Date'},inplace=True)
        temp_data=temp_data2
        del temp_data2


        # Find slope for each line
        temp_data.Date = temp_data.Date.astype("str")
        temp_data.Date2 = temp_data.Date2.astype("str")

        if len(temp_data) == 0:
            return temp_data
        temp_slope_intercept= pd.DataFrame.from_records((temp_data.apply(lambda x: get_slope([x["DateIndex"],x["DateIndex2"]],[x['xmin'],x['xmin2']]),axis=1)),
                                columns=['slope','intercept'])
        
        temp_data = pd.concat([temp_data,temp_slope_intercept],axis=1)
        temp_data.reset_index(inplace=True)
        temp_data.drop("index",axis=1,inplace=True)

        
        temp_data.reset_index(inplace=True)
        
        # Compare all pairs of lines with the same starting point
        # If the angle is small keep the longest one
        angles = []
        linesToKeep = []
        for pointa in temp_data.Date.unique():
            foo = temp_data[temp_data['Date']==pointa]
            foo = foo.to_dict('records')
            angle_last = None
            
            last_record = None
            
            for record in foo:
                
                print(record)
                
                if last_record:
                    angle = math.atan((last_record['slope']-record['slope'])/(1+last_record['slope']*record['slope']))
                    print(angle)
                    angles.append(angle)
                    # if ((-1*angle_threshold)<= angle) and (angle<= angle_threshold):
                    # ##print(angle,angle_threshold)
                    if (abs(angle)) >= abs(angle_threshold):
                        if last_record['days']>record['days']:
                            linesToKeep.append(last_record)
                        else:
                            linesToKeep.append(record)
                    # last_record = record
                    # angles.append(angle)
                else:
                    last_record = record
                print()

        angles2 = []
        linesToKeep2 = []
        for pointb in temp_data.Date2.unique():
            foo = temp_data[temp_data['Date']==pointa]
            foo = foo.to_dict('records')
            angle_last = None
            
            last_record = None
            
            for record in foo:
                
                print(record)
                
                if last_record:
                    angle = math.atan((last_record['slope']-record['slope'])/(1+last_record['slope']*record['slope']))
                    angles.append(angle)

                    if (abs(angle)) >= abs(angle_threshold):
                        if last_record['days']>record['days']:
                            linesToKeep2.append(last_record)
                        else:
                            linesToKeep2.append(record)
                else:
                    last_record = record
                print()
                
        
        print(pd.DataFrame(linesToKeep2).drop_duplicates())
        
        new = pd.DataFrame(linesToKeep)
        new.drop_duplicates(inplace=True)
        

        new = pd.concat([pd.DataFrame(linesToKeep2).drop_duplicates(),new],axis=0).drop_duplicates()
        
        temp_data = new
        

        if len(new)<=0:
            return temp_data

        # Keep n lines based on importance
        try:
            temp_data = temp_data.sort_values(by=["importance","days"],ascending=False)[:maxnlines]
        except KeyError:
            temp_data.reset_index(inplace=True)
            pass

        # temp_data.sort_values(by="Date",ascending=True,inplace=True)
        temp_data['Date'] = pd.to_datetime(temp_data['Date'], format='%Y%m%d', errors='ignore')
        temp_data['Date2'] = pd.to_datetime(temp_data['Date2'], format='%Y%m%d', errors='ignore')

        return temp_data#.to_dict(orient='list')

    def getLinesFromMax(self,df,angle_threshold=0.005,maxnlines=5):

        df.reset_index(inplace=True)
        dates = df['Date']
        dates=dates.reset_index()

        # Keep only pairs with local maximum
        df = df[df.xmax.notnull()]
        

        temp_dates = df.Date
        # Create all date combinations
        temp_data = pd.DataFrame(cartesian((temp_dates, temp_dates)))
        temp_data.columns = ["Date","Date2"]
        
        temp_data = pd.merge(temp_data,df[["Date","xmax"]],how="left",on="Date")
        temp_data = pd.merge(temp_data,df[["Date","xmax"]],how="left",left_on="Date2",right_on="Date")
        temp_data.drop("Date_y",inplace=True,axis=1)
        temp_data.columns = ["Date","Date2","xmax","xmax2"]
        
        # Filter duplicated dates from cartesian
        temp_data = temp_data[(temp_data['Date']) != (temp_data['Date2'])]
        
    

        # Keep only Downward trend lines
        temp_data = temp_data[temp_data["xmax2"]<=temp_data['xmax']]


        # temp_data = temp_data[temp_data["Date"]<temp_data["Date2"]]
        temp_data.reset_index(inplace=True)
        temp_data.drop("index",axis=1,inplace=True)
        # df.reset_index(inplace=True)

        temp_data['maximum'] = 0

        # Find max close of the period
        for i in range(len(temp_data)):
            d1 = temp_data.Date.astype("datetime64").loc[i]
            d2 = temp_data.Date2.astype("datetime64").loc[i]
            maximum = np.max(df['Close'][(df['Date'].astype("datetime64")>=d1) & (df['Date'].astype("datetime64")<=d2)])
            # ##print(maximum)
            # ##print(d1,d2,maximum)
            temp_data["maximum"].loc[i] = maximum

        temp_data.dropna(inplace=True)

        # Drop lines where max close of the period > starting point of the line
        # TODO uncomment next line
        temp_data = temp_data[(temp_data['maximum'])<=(temp_data['xmax'])]

        temp_data_group = temp_data.groupby("xmax2").count()['Date']
        # Count how strong each line is
        temp_data = temp_data.merge(temp_data_group,
                                    left_on="xmax2",
                                    right_on=temp_data_group.index,
                                    how='inner')
        # rename and reset columns
        temp_data.columns = ["Date","Date2","xmax","xmax2","maximum","importance"]
        temp_data=temp_data.sort_values(by='importance',ascending=False)

        # use n of days to define the longest trends
        temp_data['days'] = temp_data['Date2'].astype("datetime64") - temp_data['Date'].astype("datetime64")
        
        # Use date points instead of dates to calculate slopes
        temp_data2 = temp_data.merge(dates,left_on='Date',right_on="Date",how="inner")
        temp_data2.rename(columns={"index":"DateIndex"},inplace=True)
        temp_data2 = temp_data2.merge(dates,left_on='Date2',right_on="Date",how="inner")
        temp_data2.rename(columns={"index":"DateIndex2"},inplace=True)
        temp_data2.drop('Date_y',axis=1,inplace=True)
        temp_data2.rename(columns={'Date_x':'Date'},inplace=True)
        temp_data=temp_data2
        del temp_data2


        
        # Find slope for each line
        temp_data.Date = temp_data.Date.astype("str")
        temp_data.Date2 = temp_data.Date2.astype("str")
        ##print(temp_data)
        if len(temp_data) == 0:
            return temp_data
        temp_slope_intercept= pd.DataFrame.from_records((temp_data.apply(lambda x: get_slope([x["DateIndex"],x["DateIndex2"]],[x['xmax'],x['xmax2']]),axis=1)),
                                columns=['slope','intercept'])
        
        temp_data = pd.concat([temp_data,temp_slope_intercept],axis=1)
        temp_data.reset_index(inplace=True)
        temp_data.drop("index",axis=1,inplace=True)

        
        temp_data.reset_index(inplace=True)

        # Compare all pairs of lines with the same starting point
        # If the angle is small keep the longest one
        angles = []
        linesToKeep = []
        for pointa in temp_data.Date.unique():
            foo = temp_data[temp_data['Date']==pointa]
            foo = foo.to_dict('records')
            angle_last = None
            
            last_record = None
            for record in foo:
                
                # ##print(record)
                if last_record:
                    angle = math.atan((last_record['slope']-record['slope'])/(1+last_record['slope']*record['slope']))
                    
                    angles.append(angle)
                    if (abs(angle)) >= abs(angle_threshold):
                        if last_record['days']>record['days']:
                            linesToKeep.append(last_record)
                        else:
                            linesToKeep.append(record)
                    # last_record = record
                    # angles.append(angle)
                else:
                    last_record = record
                
        angles2 = []
        linesToKeep2 = []
        for pointb in temp_data.Date2.unique():
            foo = temp_data[temp_data['Date']==pointa]
            foo = foo.to_dict('records')
            angle_last = None
            
            last_record = None
            
            for record in foo:
                
                print(record)
                
                if last_record:
                    angle = math.atan((last_record['slope']-record['slope'])/(1+last_record['slope']*record['slope']))
                    print(angle)
                    angles.append(angle)

                    if (abs(angle)) >= abs(angle_threshold):
                        if last_record['days']>record['days']:
                            linesToKeep2.append(last_record)
                        else:
                            linesToKeep2.append(record)
                else:
                    last_record = record
                print()

        print(pd.DataFrame(linesToKeep2).drop_duplicates())
        
        new = pd.DataFrame(linesToKeep)
        new.drop_duplicates(inplace=True)

        new = pd.concat([pd.DataFrame(linesToKeep2).drop_duplicates(),new],axis=0).drop_duplicates()

        temp_data = new

        if len(new)<=0:
            return temp_data

        # Keep n lines based on importance
        try:
            temp_data = temp_data.sort_values(by=["importance","days"],ascending=False)[:maxnlines]
        except KeyError:
            temp_data.reset_index(inplace=True)
            pass
        
        temp_data['Date'] = pd.to_datetime(temp_data['Date'], format='%Y%m%d', errors='ignore')
        temp_data['Date2'] = pd.to_datetime(temp_data['Date2'], format='%Y%m%d', errors='ignore')
        
        return temp_data

  






def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def get_slope(dates,prices):
    if (len(dates)==0) or (len(prices)==0):
        return 0
    try:
        slope, intercept = np.polyfit(dates,prices,1)
        return slope ,intercept
    except:
        return 0

def angle(s1, s2): 
    return math.degrees(math.atan((s2-s1)/(1+(s2*s1))))
    



    
def getSlopeColor(slope_max,slope_min):
    if slope_max < 0 and slope_min < 0:
        color = "red"
    elif slope_max > 0 and slope_min > 0:
        color = "green"
    else:
        color="black"
    return color
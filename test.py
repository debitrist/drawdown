import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

end1 = datetime.now()
end = datetime(end1.year, end1.month, end1.day - 5)
start = datetime(end.year - 30, end.month, end.day)

Stock = web.DataReader("SPY", 'yahoo', start, end)
Date = pd.Series(pd.to_datetime(pd.Series(Stock.index), format='%Y-%m-%d'), index=Stock.index)
Stock['Date'] = Stock.index.to_series()

def create_drawdowns(df, period, ddfilter=-10):
    RHName = 'RH_' + str(period)
    df_idx = df.index
    duration = pd.Series(index=df_idx)
    rollinghigh = pd.Series(df['Close'].rolling(period, min_periods=1).max())
    drawdown = pd.Series(df['Close'] / rollinghigh) - 1
    ddstart = []
    ddend = []
    ddstartpx = []
    ddendpx = []
    # Loop over the index range
    for t in df.index[1:]:
        i = df.index.get_loc(t)
        if drawdown[i] != 0 and drawdown[i-1] == 0:
            duration[i] = 1
            ddstart.append(df.index[i-1])
            ddstartpx.append(df['Close'].iloc[i-1])
        elif drawdown[i] == 0 and drawdown[i-1]<0:
            duration[i] = 0
            ddend.append(t)
            ddendpx.append(df['Close'].iloc[i])
        elif drawdown[i] == 0:
            duration[i] = 0
        else: duration[i-1]+1

    ##filling up NATs
    ddend.append(df.index[-1])
    ddendpx.append(df['Close'].iloc[-1])
    ##creating DD Table with metrics
    maxddpx = [df['Close'].loc[x:y].min() for x,y in zip(ddstart,ddend)]
    maxdd = [df[df['Close']==x].index.tolist()[0] for x in maxddpx]
    global DDTable
    DDTable = pd.concat([pd.Series(ddstart, name="Start"), pd.Series(maxdd, name="Max DD"), pd.Series(ddend, name="End"), pd.Series(ddstartpx, name="StartPx"),pd.Series(maxddpx,name="TroughPx"),pd.Series(ddendpx,name="EndPx")], axis=1)
    DDTable['DD%']=(DDTable['TroughPx']/DDTable['StartPx']-1)*100
    #filtering for ddfilter threshold
    DDTable = DDTable[DDTable['DD%']<ddfilter]
    print(DDTable)
    #Creating DDSummary dataframe for analytics just in case
    DDSummary = pd.DataFrame(index=df_idx)
    DDSummary['% DD'] = drawdown
    DDSummary['Duration'] = duration
    DDSummary['Close1'] = df['Close']
    DDSummary[RHName] = pd.Series(rollinghigh, index=df_idx)

create_drawdowns(Stock, 250)

def plotdd(df):
    fig = df['Close'].plot()
    for x,y,k in zip(DDTable['Start'],DDTable['Max DD'],DDTable['DD%']):
        if k < -20:
            plt.axvspan(x,y,facecolor='r',alpha=0.8)
        elif k < -15:
            plt.axvspan(x,y,facecolor='r',alpha=0.5)
        else: plt.axvspan(x,y,facecolor='r',alpha=0.2)
    fig.figure.savefig("graph.png")


plotdd(Stock)

import pandas as pd
import pandas_datareader.data as web
from datetime import datetime, timedelta

end1 = datetime.now()
end = datetime(end1.year, end1.month, end1.day - 5)
start = datetime(end.year - 5, end.month, end.day)

Stock = web.DataReader("SPY", 'yahoo', start, end)
Date = pd.Series(pd.to_datetime(pd.Series(Stock.index), format='%Y-%m-%d'), index=Stock.index)
Stock['Date'] = Stock.index.to_series()

def create_drawdowns(df, period):
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
    df1 = pd.concat([pd.Series(ddstart), pd.Series(ddend), pd.Series(ddstartpx),pd.Series(ddendpx)], ignore_index=True, axis=1)
    df1['MaxDDPrice'] = [df['Close'].loc[x:y].min() for x,y in zip(df1[0],df1[1])]
    print(df1)
    DDSummary = pd.DataFrame(index=df_idx)
    DDSummary['% DD'] = drawdown
    DDSummary['Duration'] = duration
    DDSummary['Close1'] = df['Close']
    DDSummary[RHName] = pd.Series(rollinghigh, index=df_idx)
    DDSummary.to_csv('out.csv')


create_drawdowns(Stock, 250)

print(Stock)

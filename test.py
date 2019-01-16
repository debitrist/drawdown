import pandas as pd
import pandas_datareader.data as web
from datetime import datetime, timedelta

end1 = datetime.now()
end = datetime(end1.year, end1.month, end1.day-5)
start = datetime(end.year-5, end.month, end.day)

Stock = web.DataReader("SPY", 'yahoo', start, end)
Date = pd.Series(pd.to_datetime(pd.Series(Stock.index), format = '%Y-%m-%d'),index=Stock.index)
Stock['Date'] = Stock.index.to_series()

def create_drawdowns(df, period):
    RHName = 'RH_' + str(period)
    df_idx = df.index
    duration = pd.Series(index = df_idx)
    rollinghigh = pd.Series(df['Close'].rolling(period, min_periods=1).max())
    drawdown = pd.Series(df['Close']/rollinghigh)-1
    # Loop over the index range
    for t in Stock.index[1:]:
        i = df.index.get_loc(t)
        duration[i]= 0 if drawdown[i] == 0 else duration[i-1] + 1
        
    DDSummary = pd.DataFrame(index = df_idx)
    DDSummary['% DD'] = drawdown
    DDSummary['Duration'] = duration
    DDSummary['Close1'] = df['Close']
    DDSummary[RHName] = pd.Series(rollinghigh, index = df_idx)
    DDSummary.to_csv('out.csv')
    return(DDSummary[DDSummary['% DD'] < -0.05])
    

create_drawdowns(Stock,250)

print(Stock)

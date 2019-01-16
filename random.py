import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

end = datetime.now()
start = datetime(end.year-5, end.month, end.day)
 
Stock = web.DataReader("SPY", 'yahoo', start, end)
def normalizeDataFrame(dataframe):
 dataframe.reset_index(inplace=True)
 return dataframe

normalizeDataFrame(Stock)

###ATR Calc

def ATR(df, period):
    atr = 'ATR_' + str(period)
    df['h-l'] = df['High'] - df['Low']
    df['h-yc'] = abs(df['High'] - df['Close'].shift())
    df['l-yc'] = abs(df['Low'] - df['Close'].shift())
    df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)
    df[atr] = df['TR'].rolling(period).mean()
    df[atr] = ( df[atr].shift()*(period-1) + df['TR'] ) /  period
    df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)   
    return df 

### Super Trend
def SuperTrend(df, period, multiplier):
    """
    Function to compute SuperTrend
    
    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])
        
    Returns :
        df : Pandas DataFrame with new columns added for 
            True Range (TR), ATR (ATR_$period)
            SuperTrend (ST_$period_$multiplier)
            SuperTrend Direction (STX_$period_$multiplier)
    """
    atr = 'ATR_' + str(period)
    st = 'ST_' + str(period) + '_' + str(multiplier)
    stx = 'STX_' + str(period) + '_' + str(multiplier)
    
    """
    SuperTrend Algorithm :
    
        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR
        
        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND)) 
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)
        
        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """
    
    # Compute basic upper and lower bands
    df['basic_ub'] = (df['High'] + df['Low']) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df['High'] + df['Low']) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or df['Close'].iat[i - 1] > df['final_ub'].iat[i - 1] else df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or df['Close'].iat[i - 1] < df['final_lb'].iat[i - 1] else df['final_lb'].iat[i - 1]
       
    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df['Close'].iat[i] <= df['final_ub'].iat[i] else \
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df['Close'].iat[i] >  df['final_ub'].iat[i] else \
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df['Close'].iat[i] >= df['final_lb'].iat[i] else \
                        df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df['Close'].iat[i] <  df['final_lb'].iat[i] else 0.00 
                 
    # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df['Close'] < df[st]), 'down',  'up'), np.NaN)

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)
    
    df.fillna(0, inplace=True)

    return df

###ADX Function
def ADX(df, n, n_ADX):  
    ##DMI Calcs
    i = 0  
    UpI = []  
    DoI = []  
    while i + 1 <= df.index[-1]:  
        UpMove = df.loc[i + 1, 'High'] - df.loc[i, 'High']  
        DoMove = df.loc[i, 'Low'] - df.loc[i + 1, 'Low']  
        if UpMove > DoMove and UpMove > 0:  
            UpD = UpMove  
        else: UpD = 0  
        UpI.append(UpD)  
        if DoMove > UpMove and DoMove > 0:  
            DoD = DoMove  
        else: DoD = 0  
        DoI.append(DoD)  
        i = i + 1  
    ##True Range Calcs
    i = 0  
    TR_l = [0]  
    while i < df.index[-1]:  
        TR = max(df.loc[i + 1, 'High']-df.loc[i + 1, 'Low'], abs(df.loc[i + 1, 'High']-df.loc[i, 'Close']), abs(df.loc[i + 1, 'Low']-df.loc[i, 'Close']))
        TR_l.append(TR)  
        i = i + 1  
    TR_s = pd.Series(TR_l)  
    ATR = pd.Series(TR_s.ewm(span = n, min_periods = n, adjust=False).mean())  
    UpI = pd.Series(UpI)  
    DoI = pd.Series(DoI)  
    PosDI = pd.Series(100*UpI.ewm(span = n, min_periods = n-1, adjust=False).mean() / ATR)  
    NegDI = pd.Series(100*DoI.ewm(span = n, min_periods = n-1, adjust=False).mean() / ATR)
    DX = pd.Series(100*(abs(PosDI - NegDI) / (PosDI + NegDI)))
    ADX = pd.Series(DX.ewm(span = n_ADX, min_periods = n_ADX -1, adjust=False).mean(), name = 'ADX_' + str(n) + '_' + str(n_ADX))  
    ##ADX Dataframe
    ADXFull = pd.DataFrame()
    ADXFull['DMIU'] = PosDI
    ADXFull['DMID'] = NegDI
    ADXFull['ADX'] = ADX
    ##Trend Strength based off ADX
    i = 0
    Trend = []
    for i in ADXFull.index:
        if ADXFull.loc[i,'DMIU'] > ADXFull.loc[i, 'DMID'] and ADXFull.loc[i, 'ADX'] > ADXFull.loc[i,'DMIU']:
            Trend.append("Strong UpT")
        elif ADXFull.loc[i,'DMID'] > ADXFull.loc[i, 'DMIU'] and ADXFull.loc[i, 'ADX'] > ADXFull.loc[i,'DMID']:
            Trend.append("Strong DownT")
        elif ADXFull.loc[i,'DMIU'] > ADXFull.loc[i, 'DMID']:
            Trend.append("Weak UpT")
        elif ADXFull.loc[i,'DMID'] > ADXFull.loc[i, 'DMIU']:
            Trend.append("Weak DownT")
        else: Trend.append("Unclear")
        i = i + 1
    ADXFull['Trend'] = pd.Series(Trend)
    df = df.join(ADXFull)  
    return df

### Moving Average Trend Channel
    SMAn = 200 ## INPUT
    Stock['MAHigh'] = pd.Series(Stock['High'].rolling(SMAn).mean())
    Stock['MALow'] = pd.Series(Stock['Low'].rolling(SMAn).mean())
    Stock['MAClose'] = pd.Series(Stock['Close'].rolling(SMAn).mean())
    i=1
    TrendRegime = [0]
    DailyTrendChannel = [0]
    while i <Stock.index[-1]:
        if Stock.loc[i, 'Close'] > Stock.loc[i-1, 'MAClose']:
            TrendRegime.append("Bull")
        else: TrendRegime.append("Bear")
        if TrendRegime[i] == "Bull":
            DailyTrendChannel.append(max(Stock.loc[i, 'MALow'], DailyTrendChannel[i-1]))
        else: DailyTrendChannel.append(min(Stock.loc[i, 'MAHigh'], DailyTrendChannel[i-1]))
        i = i + 1
Stock['TrendRegime'] = pd.Series(TrendRegime)    
Stock['DailyTrendChannel'] = pd.Series(DailyTrendChannel)

print(Stock)

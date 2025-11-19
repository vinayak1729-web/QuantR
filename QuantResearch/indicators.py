import yfinance as yf
def fetch_data(ticker,start_date,end_date):
    return yf.download(tickers=ticker,start=start_date,end=end_date,auto_adjust=False)

def Rsi(price,period=14):

    delta = price.diff()
    gain =(delta.where(delta>0,0)).rolling(window=period).mean()
    loss =(-delta.where(delta<0,0)).rolling(window=period).mean()    
    return (100-(100/(1+(gain/loss))))


def bb_bands(price,period=20,num_std=2):
    rolling_mean =price.rolling(window=period).mean()
    rolling_std =price.rolling(window=period).std()
    upper_band = rolling_mean+(rolling_std*num_std)
    lower_band = rolling_mean-(rolling_std*num_std)
    return upper_band,rolling_mean,lower_band


def macd(price,short_period=12,long_period=26,signal_period=9):
    shortLine = price.ewm(span=short_period,adjust=False).mean()
    longLine = price.ewm(span=long_period,adjust=False).mean()
    macd_line = shortLine-longLine
    signalLine = macd_line.ewm(span=signal_period,adjust=False).mean()
    histogram =macd_line-signalLine
    return macd_line , signalLine , histogram

def sma(price,period=9):
    return price.rolling(window =period).mean()

def ema(price,period=9):
    return price.ewm(span=period,adjust =False).mean()


def demma(price,period =9):
    ema = price.ewm(span=period,adjust =False).mean()
    Eema1 =ema.ewm(span=period,adjust = False).mean()
    Eema2=Eema1.ewm(span=period,adjust = False).mean()
    demma = 2*(ema) -(Eema1)
    return demma

def temma(price,period =9):
    ema = price.ewm(span=period,adjust =False).mean()
    Eema1 =ema.ewm(span=period,adjust = False).mean()
    Eema2=Eema1.ewm(span=period,adjust = False).mean()
    temma = 3*ema -(3*Eema1)+Eema2
    return temma

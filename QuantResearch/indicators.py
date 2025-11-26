import yfinance as yf
import pandas as pd

# Core indicator functions
def fetch_data(ticker, start_date, end_date):
    data = yf.download(tickers=ticker, start=start_date, end=end_date, auto_adjust=False)
    # Flatten multi-level columns if they exist
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def Rsi(price, period=14):
    delta = price.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return (100 - (100 / (1 + (gain / loss))))

def bb_bands(price, period=20, num_std=2):
    rolling_mean = price.rolling(window=period).mean()
    rolling_std = price.rolling(window=period).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

def macd(price, short_period=12, long_period=26, signal_period=9):
    shortLine = price.ewm(span=short_period, adjust=False).mean()
    longLine = price.ewm(span=long_period, adjust=False).mean()
    macd_line = shortLine - longLine
    signalLine = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signalLine
    return macd_line, signalLine, histogram

def atr(data, period=14):
    high = data['High']
    low = data['Low']
    close = data['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return (tr.rolling(window=period).mean())

def sma(price, period=9):
    return price.rolling(window=period).mean()

def ema(price, period=9):
    return price.ewm(span=period, adjust=False).mean()

def demma(price, period=9):
    ema_val = price.ewm(span=period, adjust=False).mean()
    Eema1 = ema_val.ewm(span=period, adjust=False).mean()
    demma_val = 2 * (ema_val) - (Eema1)
    return demma_val

def temma(price, period=9):
    ema_val = price.ewm(span=period, adjust=False).mean()
    Eema1 = ema_val.ewm(span=period, adjust=False).mean()
    Eema2 = Eema1.ewm(span=period, adjust=False).mean()
    temma_val = 3 * ema_val - (3 * Eema1) + Eema2
    return temma_val

def RVWAP(high, low, close, volume, period=20):
    tp = (high + low + close) / 3
    tpv = tp * volume
    rolling_tpv = tpv.rolling(window=period).sum()
    rolling_volume = volume.rolling(window=period).sum()
    return rolling_tpv / rolling_volume

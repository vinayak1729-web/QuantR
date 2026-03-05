
import yfinance as yf
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────
def fetch_data(ticker, start_date, end_date):
    data = yf.download(tickers=ticker, start=start_date, end=end_date, auto_adjust=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

# ─────────────────────────────────────────────
# ORIGINAL INDICATORS
# ─────────────────────────────────────────────
def Rsi(price, period=14):
    delta = price.diff()
    gain  = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / loss)))

def bb_bands(price, period=20, num_std=2):
    rolling_mean = price.rolling(window=period).mean()
    rolling_std  = price.rolling(window=period).std()
    upper_band   = rolling_mean + (rolling_std * num_std)
    lower_band   = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

def macd(price, short_period=12, long_period=26, signal_period=9):
    shortLine  = price.ewm(span=short_period, adjust=False).mean()
    longLine   = price.ewm(span=long_period,  adjust=False).mean()
    macd_line  = shortLine - longLine
    signalLine = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram  = macd_line - signalLine
    return macd_line, signalLine, histogram

def atr(data, period=14):
    high  = data['High']
    low   = data['Low']
    close = data['Close']
    
    # 1. Calculate True Range (TR) - You had this perfectly right!
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low  - close.shift())
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 2. Calculate Average True Range (ATR) using Wilder's Smoothing
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    
    return atr

def sma(price, period=9):
    return price.rolling(window=period).mean()

def ema(price, period=9):
    return price.ewm(span=period, adjust=False).mean()

def demma(price, period=9):
    ema_val = price.ewm(span=period, adjust=False).mean()
    Eema1   = ema_val.ewm(span=period, adjust=False).mean()
    return 2 * ema_val - Eema1

def temma(price, period=9):
    ema_val = price.ewm(span=period, adjust=False).mean()
    Eema1   = ema_val.ewm(span=period, adjust=False).mean()
    Eema2   = Eema1.ewm(span=period, adjust=False).mean()
    return 3 * ema_val - 3 * Eema1 + Eema2

def RVWAP(high, low, close, volume, period=20):
    tp  = (high + low + close) / 3
    tpv = tp * volume
    return tpv.rolling(window=period).sum() / volume.rolling(window=period).sum()

# ─────────────────────────────────────────────
# NEW INDICATORS
# ─────────────────────────────────────────────

def stochastic(data, k_period=14, d_period=3):
    """Stochastic Oscillator returns %K and %D."""
    low_min  = data['Low'].rolling(window=k_period).min()
    high_max = data['High'].rolling(window=k_period).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min + 1e-9)
    d = k.rolling(window=d_period).mean()
    return k, d

def williams_r(data, period=14):
    """Williams %R oscillator."""
    high_max = data['High'].rolling(window=period).max()
    low_min  = data['Low'].rolling(window=period).min()
    return -100 * (high_max - data['Close']) / (high_max - low_min + 1e-9)

def obv(data):
    """On-Balance Volume."""
    direction = np.where(data['Close'] > data['Close'].shift(1), 1,
                np.where(data['Close'] < data['Close'].shift(1), -1, 0))
    return pd.Series((direction * data['Volume']).cumsum(), index=data.index)

def parabolic_sar(data, af_start=0.02, af_step=0.02, af_max=0.2):
    """Parabolic SAR returns (sar_series, trend_series). trend: 1=up, -1=down."""
    high  = data['High'].values
    low   = data['Low'].values
    close = data['Close'].values
    n     = len(close)
    sar   = np.zeros(n)
    trend = np.ones(n, dtype=int)
    ep    = np.zeros(n)
    af    = np.zeros(n)
    sar[0] = low[0]; ep[0] = high[0]; af[0] = af_start
    for i in range(1, n):
        pt = trend[i-1]
        if pt == 1:
            sar[i] = sar[i-1] + af[i-1] * (ep[i-1] - sar[i-1])
            sar[i] = min(sar[i], low[i-1], low[max(0, i-2)])
            if low[i] < sar[i]:
                trend[i] = -1; sar[i] = ep[i-1]; ep[i] = low[i]; af[i] = af_start
            else:
                trend[i] = 1; ep[i] = max(ep[i-1], high[i])
                af[i] = min(af[i-1]+af_step, af_max) if ep[i] > ep[i-1] else af[i-1]
        else:
            sar[i] = sar[i-1] + af[i-1] * (ep[i-1] - sar[i-1])
            sar[i] = max(sar[i], high[i-1], high[max(0, i-2)])
            if high[i] > sar[i]:
                trend[i] = 1; sar[i] = ep[i-1]; ep[i] = high[i]; af[i] = af_start
            else:
                trend[i] = -1; ep[i] = min(ep[i-1], low[i])
                af[i] = min(af[i-1]+af_step, af_max) if ep[i] < ep[i-1] else af[i-1]
    return pd.Series(sar, index=data.index), pd.Series(trend, index=data.index)

def adx(data, period=14):
    """Average Directional Index returns (ADX, +DI, -DI)."""
    high  = data['High']
    low   = data['Low']
    close = data['Close']
    plus_dm  = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    plus_dm[plus_dm  <= minus_dm] = 0
    minus_dm[minus_dm <= plus_dm] = 0
    tr  = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    atr_val  = tr.ewm(span=period, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=period, adjust=False).mean()  / (atr_val + 1e-9)
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / (atr_val + 1e-9)
    dx       = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    adx_val  = dx.ewm(span=period, adjust=False).mean()
    return adx_val, plus_di, minus_di

def ichimoku(data, tenkan=9, kijun=26, senkou_b=52):
    """Ichimoku Cloud. Returns tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou_span."""
    def mid(s, p): return (s['High'].rolling(p).max() + s['Low'].rolling(p).min()) / 2
    tenkan_sen    = mid(data, tenkan)
    kijun_sen     = mid(data, kijun)
    senkou_a      = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_b_line = mid(data, senkou_b).shift(kijun)
    chikou_span   = data['Close'].shift(-kijun)
    return tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou_span

def pivot_points(data):
    """Classic pivot points from the last completed bar. Returns dict P,R1-R3,S1-S3."""
    h = float(data['High'].iloc[-1])
    l = float(data['Low'].iloc[-1])
    c = float(data['Close'].iloc[-1])
    p = (h + l + c) / 3
    return dict(P=p, R1=2*p-l, R2=p+(h-l), R3=h+2*(p-l),
                     S1=2*p-h, S2=p-(h-l), S3=l-2*(h-p))

def fibonacci_levels(data):
    """Fibonacci retracement levels over the full dataset."""
    hi = float(data['High'].max())
    lo = float(data['Low'].min())
    diff = hi - lo
    return {
        '0%':    hi,
        '23.6%': hi - 0.236 * diff,
        '38.2%': hi - 0.382 * diff,
        '50%':   hi - 0.500 * diff,
        '61.8%': hi - 0.618 * diff,
        '78.6%': hi - 0.786 * diff,
        '100%':  lo,
    }

def slope(series, period=14):
    """Linear-regression slope normalised as (slope/mean_price)*100 — % per bar."""
    vals = series.values.astype(float)
    out  = np.full(len(vals), np.nan)
    x    = np.arange(period, dtype=float)
    for i in range(period - 1, len(vals)):
        y = vals[i - period + 1: i + 1]
        if np.isnan(y).any():
            continue
        m, _ = np.polyfit(x, y, 1)
        mean  = np.mean(y) or 1
        out[i] = (m / mean) * 100
    return pd.Series(out, index=series.index)
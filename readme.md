# QuantResearch
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-QuantResearch-orange)](https://pypi.org/project/QuantResearch/)

A comprehensive Python library for quantitative financial analysis, technical indicator calculation, strategy backtesting, and advanced trading signal visualization. QuantResearch 2.5.2 provides easy-to-use functions for fetching market data from NSE, BSE, US, and Crypto markets, calculating a full suite of technical indicators, writing and running backtests via **QuantQL** (a built-in domain-specific language), and generating professional-grade charts with candlestick patterns — all available through both a Python API and a full GUI dashboard.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
  - [Data Fetching](#data-fetching)
  - [Technical Indicators](#technical-indicators)
  - [Visualization](#visualization)
- [QuantQL — Backtesting Language](#-quantql--backtesting-language)
  - [Language Syntax](#language-syntax)
  - [Supported Indicators](#supported-indicators-in-quantql)
  - [Condition Operators](#condition-operators)
  - [Strategy Examples](#strategy-examples)
  - [Running a Backtest](#running-a-backtest)
  - [Backtest Metrics](#backtest-metrics)
  - [Exporting Results](#exporting-results)
- [QuantResearch Dashboard](#-quantresearch-dashboard)
  - [Launching the Dashboard](#launching-the-dashboard)
  - [Dashboard Tabs](#dashboard-tabs)
  - [Quant Metrics Panel](#quant-metrics-panel)
- [Usage Examples](#-usage-examples)
- [Requirements](#-requirements)
- [Authors](#-authors)
- [License](#-license)
- [Support](#-support)
- [Disclaimer](#%EF%B8%8F-disclaimer)

## 🎯 Overview
QuantResearch 2.5.2 is designed for traders, financial analysts, and quantitative researchers who need reliable technical analysis tools with professional visualization capabilities and a powerful backtesting engine. It combines data fetching, indicator calculation, strategy backtesting via QuantQL, and candlestick charting into a single, intuitive package.

Whether you're backtesting trading strategies, analyzing market trends, or building automated trading systems, QuantResearch 2.5.2 provides all the essential tools you need — including a domain-specific language that lets you define buy/sell strategies in plain, readable syntax and simulate them against real historical data with full performance analytics, trade logs, equity curves, and export capabilities.

## ✨ Features
- 📊 **Data Fetching:** Download historical OHLCV data from Yahoo Finance for NSE, BSE, US, and Crypto markets
- 📈 **Technical Indicators:** RSI, MACD, Bollinger Bands, ATR, SMA, EMA, DEMA, TEMA, RVWAP, Stochastic, Williams %R, OBV, Parabolic SAR, ADX, Ichimoku Cloud, Pivot Points, Fibonacci Levels, Slope
- 🧪 **QuantQL Backtest Engine:** Write trading strategies in a readable domain-specific language and backtest against real historical data with full performance analytics
- 🎨 **Professional Visualization:** Beautiful dark-theme charts with both line and candlestick chart support
- 🕯️ **Candlestick Charts:** Full candlestick chart support for price action analysis
- 📉 **Multi-Chart Views:** Combined price and indicator charts in single views
- 🔔 **Signal Generation:** Automatic buy/sell crossover point detection
- 🖥️ **GUI Dashboard:** Full-featured Tkinter dashboard with 5 tabs — Historical, Live OHLC, Multi-Ticker, Watchlist, and Backtest
- 🇮🇳 **India + Global Support:** Auto-resolves NSE/BSE tickers (e.g. `RELIANCE` → `RELIANCE.NS`), Indian rupee/crore/lakh formatting, Nifty 50 watchlist defaults
- 📊 **Quant Metrics:** Sharpe, Sortino, Calmar, VaR, CVaR, Alpha, Beta, CAGR, Max Drawdown and more
- ⚡ **Simple API:** Intuitive functions that are easy to learn and use
- 🔧 **Customizable Parameters:** Adjust periods and thresholds for your strategy
- 📱 **Cross-Platform:** Works on Windows, macOS, and Linux

## 📦 Installation
Install QuantResearch using pip:
```bash
pip install QuantResearch
```
Or install from source:
```bash
git clone https://github.com/vinayak1729-web/QuantR.git
cd QuantR
pip install -e .
```

## 🚀 Quick Start
Here's a simple example to get started in 5 minutes:

```python
from QuantResearch import fetch_data, Rsi, plot_rsi

# Step 1: Fetch stock data
ticker = "AAPL"
data = fetch_data(ticker, start_date="2023-01-01", end_date="2024-01-01")

# Step 2: Calculate RSI
rsi = Rsi(data['Close'], period=14)

# Step 3: Visualize with candlestick chart
plot_rsi(data=data, rsi=rsi, period=14, ticker=ticker, kind='candle')
```

Launch the full GUI dashboard:
```python
from QuantResearch.dashboard import launch_dashboard
launch_dashboard()
```

Run a backtest using QuantQL:
```python
from QuantResearch.backtest_engine import run_backtest

result = run_backtest("""
BACKTEST "RSI + MACD Strategy"
MARKET NSE
TICKER RELIANCE
PERIOD 1Y

USE RSI(14)
USE MACD(12, 26, 9)

BUY  WHEN RSI > 30 AND MACD CROSSES_ABOVE SIGNAL
SELL WHEN RSI > 70 OR MACD CROSSES_BELOW SIGNAL

CAPITAL 100000
STOP_LOSS 5%
TAKE_PROFIT 15%
COMMISSION 0.1%
""")

for key, val in result.metrics.items():
    print(f"{key}: {val}")
```

## 📚 API Reference

### Data Fetching

#### `fetch_data(ticker, start_date, end_date)`
Downloads historical OHLCV (Open, High, Low, Close, Volume, Adjusted Close) data from Yahoo Finance. Supports NSE (`.NS`), BSE (`.BO`), US, and Crypto (e.g. `BTC-USD`) tickers.

Parameters:
- `ticker` (str): Stock ticker symbol (e.g. `"AAPL"`, `"RELIANCE.NS"`, `"BTC-USD"`)
- `start_date` (str): Start date in format `"YYYY-MM-DD"`
- `end_date` (str): End date in format `"YYYY-MM-DD"`

Returns:
- `pandas.DataFrame`: Contains columns: Open, High, Low, Close, Adj Close, Volume

Example:
```python
data = fetch_data("RELIANCE.NS", "2023-01-01", "2024-01-01")
print(data.head())
print(f"Shape: {data.shape}")
```

---

### Technical Indicators

#### `Rsi(price, period=14)`
Relative Strength Index — a momentum oscillator measuring the magnitude of recent price changes.

Parameters:
- `price` (pandas.Series): Price series (typically closing prices)
- `period` (int): Lookback period (default: 14)

Returns:
- `pandas.Series`: RSI values ranging from 0 to 100

Interpretation:
```
RSI > 70  → Overbought (potential sell signal)
RSI < 30  → Oversold  (potential buy signal)
30–70     → Neutral zone
```

Example:
```python
rsi = Rsi(data['Close'], period=14)
print(f"Current RSI: {rsi.iloc[-1]:.2f}")
```

---

#### `bb_bands(price, period=20, num_std=2)`
Bollinger Bands — volatility bands placed above and below a moving average.

Parameters:
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 20)
- `num_std` (int/float): Number of standard deviations (default: 2)

Returns:
- Tuple: `(upper_band, middle_band, lower_band)`

Example:
```python
upper, mid, lower = bb_bands(data['Close'], period=20, num_std=2)
plot_bollinger(data=data, adj_close=data['Close'], bb_upper=upper,
               bb_mid=mid, bb_lower=lower, ticker="AAPL", kind='candle')
```

---

#### `macd(price, short_period=12, long_period=26, signal_period=9)`
MACD — Moving Average Convergence Divergence trend indicator.

Parameters:
- `price` (pandas.Series): Price series
- `short_period` (int): Short EMA period (default: 12)
- `long_period` (int): Long EMA period (default: 26)
- `signal_period` (int): Signal line EMA period (default: 9)

Returns:
- Tuple: `(macd_line, signal_line, histogram)`

Example:
```python
macd_line, signal_line, hist = macd(data['Close'])
plot_macd(macd_line, signal_line, hist, ticker="AAPL", data=data, kind='candle')
```

---

#### `atr(data, period=14)`
Average True Range — volatility indicator measuring price movement range using Wilder's Smoothing.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `period` (int): Lookback period (default: 14)

Returns:
- `pandas.Series`: ATR values

Example:
```python
atr_values = atr(data, period=14)
print(f"Current ATR: {atr_values.iloc[-1]:.2f}")
```

---

#### `sma(price, period=9)`
Simple Moving Average — average price over a specified period.

Parameters:
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

Returns:
- `pandas.Series`: SMA values

---

#### `ema(price, period=9)`
Exponential Moving Average — weighted average giving more importance to recent prices.

Parameters:
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

Returns:
- `pandas.Series`: EMA values

---

#### `demma(price, period=9)`
Double Exponential Moving Average — smoother trend indicator with reduced lag.

Parameters:
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

Returns:
- `pandas.Series`: DEMA values

---

#### `temma(price, period=9)`
Triple Exponential Moving Average — smoothest trend indicator with minimal lag.

Parameters:
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

Returns:
- `pandas.Series`: TEMA values

---

#### `RVWAP(high, low, close, volume, period=20)`
Rolling Volume-Weighted Average Price — price benchmark reflecting volume and price.

Parameters:
- `high` (pandas.Series): High prices
- `low` (pandas.Series): Low prices
- `close` (pandas.Series): Close prices
- `volume` (pandas.Series): Trading volume
- `period` (int): Lookback period (default: 20)

Returns:
- `pandas.Series`: VWAP values

---

#### `stochastic(data, k_period=14, d_period=3)`
Stochastic Oscillator — momentum indicator comparing closing price to the high-low range over a lookback period.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `k_period` (int): %K lookback period (default: 14)
- `d_period` (int): %D smoothing period (default: 3)

Returns:
- Tuple: `(%K series, %D series)`

Interpretation:
```
%K > 80                   → Overbought
%K < 20                   → Oversold
%K CROSSES_ABOVE %D       → Bullish signal
%K CROSSES_BELOW %D       → Bearish signal
```

Example:
```python
k, d = stochastic(data, k_period=14, d_period=3)
print(f"Stoch %K: {k.iloc[-1]:.2f}  %D: {d.iloc[-1]:.2f}")
```

---

#### `williams_r(data, period=14)`
Williams %R oscillator — momentum indicator showing overbought/oversold conditions on an inverted 0 to -100 scale.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `period` (int): Lookback period (default: 14)

Returns:
- `pandas.Series`: Williams %R values from -100 to 0

Interpretation:
```
%R > -20  → Overbought
%R < -80  → Oversold
```

Example:
```python
wr = williams_r(data, period=14)
```

---

#### `obv(data)`
On-Balance Volume — cumulative volume-based momentum indicator. Adds volume on up-days and subtracts on down-days.

Parameters:
- `data` (pandas.DataFrame): OHLCV data (requires Close and Volume columns)

Returns:
- `pandas.Series`: Cumulative OBV values

Example:
```python
obv_series = obv(data)
```

---

#### `parabolic_sar(data, af_start=0.02, af_step=0.02, af_max=0.2)`
Parabolic SAR (Stop and Reverse) — trend-following indicator used to identify potential price reversals and trail stops.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `af_start` (float): Starting acceleration factor (default: 0.02)
- `af_step` (float): AF increment on each new extreme (default: 0.02)
- `af_max` (float): Maximum acceleration factor (default: 0.2)

Returns:
- Tuple: `(sar_series, trend_series)` where `trend` is `1` for uptrend, `-1` for downtrend

Example:
```python
sar, trend = parabolic_sar(data)
print(f"SAR: {sar.iloc[-1]:.2f}  Trend: {'UP' if trend.iloc[-1] == 1 else 'DOWN'}")
```

---

#### `adx(data, period=14)`
Average Directional Index — measures trend strength regardless of direction, along with +DI and -DI directional indicators.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `period` (int): Lookback period (default: 14)

Returns:
- Tuple: `(adx_series, plus_di_series, minus_di_series)`

Interpretation:
```
ADX > 25   → Strong trend
ADX < 20   → Weak / no trend
+DI > -DI  → Bullish trend direction
-DI > +DI  → Bearish trend direction
```

Example:
```python
adx_val, plus_di, minus_di = adx(data, period=14)
print(f"ADX: {adx_val.iloc[-1]:.2f}")
```

---

#### `ichimoku(data, tenkan=9, kijun=26, senkou_b=52)`
Ichimoku Cloud — a comprehensive multi-component indicator showing support/resistance, trend direction, and momentum.

Parameters:
- `data` (pandas.DataFrame): OHLC data
- `tenkan` (int): Tenkan-sen (Conversion Line) period (default: 9)
- `kijun` (int): Kijun-sen (Base Line) period (default: 26)
- `senkou_b` (int): Senkou Span B period (default: 52)

Returns:
- Tuple: `(tenkan_sen, kijun_sen, senkou_a, senkou_b_line, chikou_span)`

Example:
```python
tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku(data)
```

---

#### `pivot_points(data)`
Classic Pivot Points — calculates support and resistance levels from the last completed bar's High, Low, and Close.

Parameters:
- `data` (pandas.DataFrame): OHLC data

Returns:
- `dict` with keys: `P`, `R1`, `R2`, `R3`, `S1`, `S2`, `S3`

Example:
```python
pp = pivot_points(data)
print(f"Pivot: {pp['P']:.2f}  R1: {pp['R1']:.2f}  S1: {pp['S1']:.2f}")
```

---

#### `fibonacci_levels(data)`
Fibonacci Retracement Levels — calculates 7 standard retracement levels across the full dataset's high-low range.

Parameters:
- `data` (pandas.DataFrame): OHLC data (uses overall High max and Low min)

Returns:
- `dict` with keys: `'0%'`, `'23.6%'`, `'38.2%'`, `'50%'`, `'61.8%'`, `'78.6%'`, `'100%'`

Example:
```python
fib = fibonacci_levels(data)
for level, price in fib.items():
    print(f"Fib {level}: {price:.2f}")
```

---

#### `slope(series, period=14)`
Linear Regression Slope — calculates the normalized trend slope as `(slope / mean_price) * 100` (percentage per bar), useful for quantifying trend momentum.

Parameters:
- `series` (pandas.Series): Price series
- `period` (int): Lookback period for the regression window (default: 14)

Returns:
- `pandas.Series`: Normalized slope values

Example:
```python
slp = slope(data['Close'], period=14)
```

---

### Visualization

All visualization functions support two chart types via the `kind` parameter:
- `kind='line'` — Traditional line charts (default)
- `kind='candle'` — Candlestick charts with OHLC data

#### `plot_candlestick(data, ticker='Stock')`
Plot a standalone candlestick chart.

Parameters:
- `data` (pandas.DataFrame): OHLC data with Open, High, Low, Close columns
- `ticker` (str): Stock ticker for title (default: `'Stock'`)

Returns:
- None (displays chart)

Example:
```python
plot_candlestick(data, ticker="AAPL")
```

---

#### `plot_macd(macd_line, signal_line, histogram, ticker=None, data=None, kind='line')`
Displays MACD with optional candlestick price chart.

Parameters:
- `macd_line` (pandas.Series): MACD line values
- `signal_line` (pandas.Series): Signal line values
- `histogram` (pandas.Series): Histogram values
- `ticker` (str, optional): Stock ticker
- `data` (pandas.DataFrame, optional): OHLC data (required if `kind='candle'`)
- `kind` (str): `'line'` or `'candle'` (default: `'line'`)

Example:
```python
# Line chart (traditional)
plot_macd(macd_line, signal_line, hist, ticker="AAPL")

# Candlestick chart with price action
plot_macd(macd_line, signal_line, hist, ticker="AAPL", data=data, kind='candle')
```

---

#### `plot_bollinger(data=None, adj_close=None, bb_upper=None, bb_mid=None, bb_lower=None, ticker=None, kind='line')`
Visualizes Bollinger Bands with optional candlestick chart.

Parameters:
- `data` (pandas.DataFrame, optional): OHLC data (required if `kind='candle'`)
- `adj_close` (pandas.Series): Adjusted close prices (required if `kind='line'`)
- `bb_upper` (pandas.Series): Upper Bollinger Band
- `bb_mid` (pandas.Series): Middle Bollinger Band
- `bb_lower` (pandas.Series): Lower Bollinger Band
- `ticker` (str, optional): Stock ticker
- `kind` (str): `'line'` or `'candle'` (default: `'line'`)

Example:
```python
upper, mid, lower = bb_bands(data['Close'])

# Line chart
plot_bollinger(adj_close=data['Close'], bb_upper=upper, bb_mid=mid,
               bb_lower=lower, ticker="AAPL")

# Candlestick chart
plot_bollinger(data=data, adj_close=data['Close'], bb_upper=upper,
               bb_mid=mid, bb_lower=lower, ticker="AAPL", kind='candle')
```

---

#### `plot_rsi(data=None, rsi=None, period=14, lower=30, upper=70, ticker=None, kind='line')`
Displays RSI with optional price candlestick chart.

Parameters:
- `data` (pandas.DataFrame, optional): OHLC data (required if `kind='candle'`)
- `rsi` (pandas.Series): RSI values
- `period` (int): RSI period (default: 14)
- `lower` (int): Oversold threshold (default: 30)
- `upper` (int): Overbought threshold (default: 70)
- `ticker` (str, optional): Stock ticker
- `kind` (str): `'line'` or `'candle'` (default: `'line'`)

Example:
```python
rsi = Rsi(data['Close'], period=14)

# Line chart
plot_rsi(rsi=rsi, period=14, ticker="AAPL")

# Candlestick chart with price
plot_rsi(data=data, rsi=rsi, period=14, ticker="AAPL", kind='candle')
```

---

#### `plot_moving_averages(data=None, price=None, sma_val=None, ema_val=None, dema_val=None, tema_val=None, ticker=None, kind='line')`
Compares moving averages with optional candlestick chart.

Parameters:
- `data` (pandas.DataFrame, optional): OHLC data (required if `kind='candle'`)
- `price` (pandas.Series, optional): Price series (required if `kind='line'`)
- `sma_val` (pandas.Series, optional): SMA values
- `ema_val` (pandas.Series, optional): EMA values
- `dema_val` (pandas.Series, optional): DEMA values
- `tema_val` (pandas.Series, optional): TEMA values
- `ticker` (str, optional): Stock ticker
- `kind` (str): `'line'` or `'candle'` (default: `'line'`)

Example:
```python
sma_20 = sma(data['Close'], period=20)
ema_20  = ema(data['Close'], period=20)

# Candlestick chart with moving averages
plot_moving_averages(data=data, sma_val=sma_20, ema_val=ema_20,
                     ticker="AAPL", kind='candle')
```

---

## 🧪 QuantQL — Backtesting Language

QuantQL is a domain-specific language built into QuantResearch that lets you write trading strategies in plain, readable syntax and backtest them against real historical data. The engine handles everything: data fetching, indicator computation, trade simulation, stop-loss/take-profit, commission/slippage, equity curve tracking, and full performance metrics — all from a simple script.

### Language Syntax

```
BACKTEST "<Strategy Name>"
MARKET <NSE | BSE | US | CRYPTO | Auto>
TICKER <SYMBOL>
PERIOD <1Y | 6M | 3M | 30D | 2W | ...>

USE <INDICATOR>(<params>)
...

BUY  WHEN <condition>
SELL WHEN <condition>

CAPITAL <amount>
POSITION_SIZE <percent>%
STOP_LOSS <percent>%
TAKE_PROFIT <percent>%
COMMISSION <percent>%
SLIPPAGE <percent>%
```

**Keyword Reference:**

| Keyword | Description | Example |
|---|---|---|
| `BACKTEST` | Strategy name (string in quotes) | `BACKTEST "My Strategy"` |
| `MARKET` | Exchange/market selector | `MARKET NSE` |
| `TICKER` | Asset symbol | `TICKER RELIANCE` |
| `PERIOD` | Historical lookback period | `PERIOD 1Y` |
| `USE` | Declare an indicator with parameters | `USE RSI(14)` |
| `BUY WHEN` | Entry condition | `BUY WHEN RSI < 30` |
| `SELL WHEN` | Exit condition | `SELL WHEN RSI > 70` |
| `CAPITAL` | Starting capital (number) | `CAPITAL 100000` |
| `POSITION_SIZE` | Fraction of capital per trade | `POSITION_SIZE 50%` |
| `STOP_LOSS` | Stop-loss % below entry price | `STOP_LOSS 5%` |
| `TAKE_PROFIT` | Take-profit % above entry price | `TAKE_PROFIT 15%` |
| `COMMISSION` | Per-trade commission | `COMMISSION 0.1%` |
| `SLIPPAGE` | Per-trade slippage | `SLIPPAGE 0.05%` |

**Period Formats:**

| Format | Meaning |
|---|---|
| `1Y` | 1 year (365 days) |
| `6M` | 6 months (180 days) |
| `3M` | 3 months (90 days) |
| `2W` | 2 weeks (14 days) |
| `30D` | 30 days |

**Market Values:**

| Value | Description |
|---|---|
| `NSE` | Indian NSE — auto-appends `.NS` |
| `BSE` | Indian BSE — auto-appends `.BO` |
| `US` | US markets — no suffix |
| `CRYPTO` | Crypto — auto-appends `-USD` |
| `Auto` | Auto-detect from known NSE ticker set |

---

### Supported Indicators in QuantQL

Declare indicators with `USE`, then reference them by name in `BUY WHEN` / `SELL WHEN` conditions. Indicators that produce multiple outputs expose sub-names automatically:

| `USE` Declaration | Available Names in Conditions |
|---|---|
| `USE RSI(14)` | `RSI` |
| `USE MACD(12, 26, 9)` | `MACD`, `SIGNAL`, `HISTOGRAM` |
| `USE SMA(20)` | `SMA` |
| `USE EMA(20)` | `EMA` |
| `USE DEMA(20)` | `DEMA` |
| `USE TEMA(20)` | `TEMA` |
| `USE BB(20)` | `BB_UPPER`, `BB_MID`, `BB_LOWER` |
| `USE ATR(14)` | `ATR` |
| `USE STOCH(14, 3)` | `STOCH_K`, `STOCH_D` |
| `USE WILLIAMS(14)` | `WILLIAMS` |
| `USE ADX(14)` | `ADX`, `PLUS_DI`, `MINUS_DI` |
| `USE SLOPE(14)` | `SLOPE` |
| `USE SAR` | `SAR`, `SAR_TREND` |
| `USE OBV` | `OBV` |
| `USE VWAP(20)` | `VWAP` |

**Price primitives** (usable directly in conditions without `USE`):

`CLOSE`, `OPEN`, `HIGH`, `LOW`, `VOLUME`

---

### Condition Operators

| Operator | Description | Example |
|---|---|---|
| `>` | Greater than | `RSI > 70` |
| `<` | Less than | `RSI < 30` |
| `>=` | Greater than or equal | `ADX >= 25` |
| `<=` | Less than or equal | `CLOSE <= BB_LOWER` |
| `==` | Equal to | `SAR_TREND == 1` |
| `!=` | Not equal to | `SAR_TREND != -1` |
| `CROSSES_ABOVE` | Crossover upward (this bar vs last bar) | `MACD CROSSES_ABOVE SIGNAL` |
| `CROSSES_BELOW` | Crossover downward | `EMA CROSSES_BELOW SMA(50)` |
| `AND` | Both conditions true | `RSI > 30 AND ADX > 25` |
| `OR` | Either condition true | `RSI > 70 OR MACD CROSSES_BELOW SIGNAL` |
| `NOT` | Negate a condition | `NOT RSI > 70` |

Conditions can be grouped with parentheses:
```
BUY WHEN (RSI < 35 AND CLOSE < BB_LOWER) OR STOCH_K CROSSES_ABOVE STOCH_D
```

---

### Strategy Examples

**RSI + MACD Crossover (NSE)**
```
BACKTEST "RSI + MACD Crossover"
MARKET NSE
TICKER MARUTI
PERIOD 1Y

USE RSI(14)
USE MACD(12, 26, 9)

BUY  WHEN RSI > 30 AND MACD CROSSES_ABOVE SIGNAL
SELL WHEN RSI > 70 OR MACD CROSSES_BELOW SIGNAL

CAPITAL 100000
STOP_LOSS 5%
TAKE_PROFIT 15%
COMMISSION 0.1%
```

**Bollinger Bounce (NSE)**
```
BACKTEST "Bollinger Bounce"
MARKET NSE
TICKER RELIANCE
PERIOD 6M

USE BB(20)
USE RSI(14)

BUY  WHEN CLOSE < BB_LOWER AND RSI < 35
SELL WHEN CLOSE > BB_MID OR RSI > 65

CAPITAL 500000
STOP_LOSS 3%
TAKE_PROFIT 10%
COMMISSION 0.1%
```

**SMA Trend + ADX Filter (US)**
```
BACKTEST "SMA Trend Follow"
MARKET US
TICKER AAPL
PERIOD 2Y

USE SMA(50)
USE EMA(20)
USE ADX(14)

BUY  WHEN CLOSE > SMA(50) AND EMA > SMA(50) AND ADX > 25
SELL WHEN CLOSE < SMA(50)

CAPITAL 50000
STOP_LOSS 7%
TAKE_PROFIT 20%
COMMISSION 0.05%
```

**Stochastic Reversal (NSE)**
```
BACKTEST "Stochastic Reversal"
MARKET NSE
TICKER TCS
PERIOD 1Y

USE STOCH(14, 3)
USE ADX(14)

BUY  WHEN STOCH_K < 20 AND STOCH_K CROSSES_ABOVE STOCH_D AND ADX > 20
SELL WHEN STOCH_K > 80 OR STOCH_K CROSSES_BELOW STOCH_D

CAPITAL 200000
STOP_LOSS 4%
TAKE_PROFIT 12%
COMMISSION 0.1%
```

**Crypto Momentum (BTC)**
```
BACKTEST "BTC Momentum"
MARKET CRYPTO
TICKER BTC
PERIOD 6M

USE EMA(20)
USE SMA(50)
USE RSI(14)

BUY  WHEN EMA > SMA(50) AND RSI > 45
SELL WHEN EMA CROSSES_BELOW SMA(50) OR RSI > 80

CAPITAL 50000
STOP_LOSS 8%
TAKE_PROFIT 25%
COMMISSION 0.2%
```

---

### Running a Backtest

**Python API:**
```python
from QuantResearch.backtest_engine import compile_strategy, run_backtest, BacktestEngine

# Option 1 — run directly from script string
result = run_backtest(my_strategy_script)

# Option 2 — compile then run separately
strategy = compile_strategy(my_strategy_script)
engine   = BacktestEngine(strategy)
result   = engine.run()

# Access results
print(result.metrics)       # dict of performance metrics
print(result.trades)        # list of Trade objects
print(result.equity_curve)  # pandas.Series
print(result.indicators)    # dict of computed indicator Series
print(result.data)          # pandas.DataFrame of OHLCV data
```

**Standalone GUI:**
```python
from QuantResearch.backtest_engine import backtest_dashboard
backtest_dashboard()
```

---

### Backtest Metrics

After simulation, `result.metrics` contains the following performance statistics:

| Metric | Description |
|---|---|
| Total Trades | Number of completed trades |
| Winners | Number of profitable trades |
| Losers | Number of losing trades |
| Win Rate | Percentage of winning trades |
| Net P&L | Total profit/loss after commission |
| Total Return | Percentage return over the period |
| Gross Profit | Sum of all winning trade P&L |
| Gross Loss | Sum of all losing trade P&L |
| Profit Factor | Gross Profit / abs(Gross Loss) |
| Avg Win | Average profit per winning trade |
| Avg Loss | Average loss per losing trade |
| Max Consec Wins | Longest consecutive winning streak |
| Max Consec Losses | Longest consecutive losing streak |
| Avg Hold (days) | Average trade holding period in days |
| Total Commission | Total commission paid across all trades |
| Sharpe Ratio | Risk-adjusted return (rf = 6.5% annualised) |
| Max Drawdown | Largest peak-to-trough equity decline |
| Volatility | Annualised standard deviation of daily returns |
| Starting Capital | Initial capital |
| Final Equity | Portfolio value at end of simulation |

---

### Exporting Results

After running a backtest in the GUI Backtest tab:

- **Export CSV** — saves a full report: strategy parameters, all metrics, a complete trade log (entry/exit dates, prices, P&L, commission, exit reason, hold days), and the equity curve with daily return percentages.
- **Export PNG** — saves the backtest chart (price with trade markers, equity curve, sub-indicator panel) as a high-resolution PNG at 150 DPI.

---

## 🖥️ QuantResearch Dashboard

The QuantResearch Dashboard is a full-featured GUI built with Tkinter and Matplotlib. It supports India (NSE/BSE) and global (US/Crypto) markets with automatic ticker resolution, professional dark-theme charts, real-time live data, and a persistent watchlist.

### Launching the Dashboard
```python
from QuantResearch.dashboard import launch_dashboard
launch_dashboard()
```

---

### Dashboard Tabs

#### 📊 Tab 1 — Historical

The main analysis tab. Enter any ticker (NSE, BSE, US, or Crypto) and select a timeframe to fetch and chart historical OHLCV data with any combination of indicators overlaid.

**Market Selector:** Choose `Auto`, `NSE`, `BSE`, `US`, or `Crypto`. In `Auto` mode, known Indian NSE tickers are resolved automatically (e.g. typing `RELIANCE` fetches `RELIANCE.NS` with ₹ formatting).

**Timeframe Buttons:** `1M` `3M` `6M` `9M` `1Y` `3Y` `5Y` — each automatically adjusts all indicator periods via adaptive period settings.

**Overlays (toggled from the Control Panel):**
- Volume bars
- VWAP (Rolling Volume-Weighted Average Price)
- Volume Profile with configurable bin count (10–200) and optional custom date range
- Benchmark comparison (^NSEI, ^BSESN, ^NSEBANK, SPY, QQQ, BTC-USD, GLD, or custom)

**Moving Averages (toggled individually):** SMA, EMA, DEMA, TEMA, RVWAP

**Indicators (all with adjustable period spinboxes):**
RSI, MACD, ATR, Bollinger Bands, Stochastic, Williams %R, OBV, ADX, Parabolic SAR, Ichimoku Cloud, Pivot Points, Fibonacci Levels, Slope

**Fibonacci Custom Range** — optionally pin Fibonacci high/low to a specific date window using the built-in date pickers, rather than the full dataset.

**Export Buttons:**
- `💾 PNG` — save the current chart as an image
- `📄 CSV` — export OHLCV + indicator data
- `📈 Metrics` — toggle the Quant Metrics panel

---

#### 📡 Tab 2 — Live OHLC

Live market data streaming via Yahoo Finance WebSocket. Displays real-time OHLC candlestick charts with optional RSI, MACD, Bollinger Bands, Stochastic, Volume, SMA, and EMA overlays. Supports configurable resample intervals (e.g. `1min`, `5min`) and price alerts.

---

#### 🗂 Tab 3 — Multi-Ticker

Fetch and display multiple tickers side by side in a scrollable multi-chart view. Each sub-chart independently shows price with optional RSI, MACD, ATR, Stochastic, and ADX indicator panels.

---

#### ⭐ Tab 4 — Watchlist

A persistent watchlist stored in `~/.quant_watchlist.json`. Shows live price, % change, 52-week high/low, and exchange for each ticker.

Features:
- **↺ Refresh Prices** — re-fetch all watchlist prices in a background thread
- **🇮🇳 Add Nifty50 Defaults** — instantly add the top 10 Nifty 50 tickers (RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, WIPRO.NS, BAJFINANCE.NS, KOTAKBANK.NS, LT.NS)
- **→ Chart** — jump to the Historical tab with the selected ticker pre-loaded
- **✕** — remove a ticker from the watchlist

---

#### 🧪 Tab 5 — Backtest (QuantQL)

Write and run QuantQL strategy scripts directly inside the dashboard. Features:

- Built-in code editor with 5 ready-to-run example strategies
- Pre-plot of raw price chart before the simulation runs
- Visual trade book — buy entries (▲ green) and sell exits (▼ red) overlaid on the price chart
- Equity curve panel with green/red fill vs starting capital and live equity label
- Sub-indicator panel (RSI, MACD, Stochastic, ADX) below the main chart
- Full metrics table
- Trade log table with every trade's details (entry/exit dates, prices, P&L, commission, exit reason, hold days)
- CSV trade book export
- PNG chart export

---

### Quant Metrics Panel

Toggle with the `📈 Metrics` button in the Historical tab. Computes institutional-grade performance statistics on the loaded price series, with optional benchmarking against a selected index:

| Metric | Description |
|---|---|
| Total Return | Cumulative price return over the loaded period |
| CAGR | Compound Annual Growth Rate |
| Volatility | Annualised standard deviation (252-day basis) |
| Sharpe | Risk-adjusted return (rf = 6.5% Indian repo rate approximation) |
| Sortino | Downside risk-adjusted return |
| Max Drawdown | Largest peak-to-trough equity decline |
| Calmar | CAGR / abs(Max Drawdown) |
| VaR 95% | Value at Risk at 95% confidence level |
| CVaR 95% | Conditional VaR (Expected Shortfall) |
| Win Rate | Frequency of positive daily returns |
| Profit Factor | Avg daily gain / avg daily loss ratio |
| Beta | Systematic risk vs selected benchmark |
| Alpha (ann) | Annualised excess return vs benchmark |
| Correlation | Return correlation with benchmark |
| Bars | Total trading days in the dataset |

Values are color-coded: green = strong, gold = neutral, red = weak/concerning, cyan = informational.

---

## 💡 Usage Examples

### Example 1: Complete Technical Analysis with Candlesticks
```python
from QuantResearch import *

ticker = "AAPL"
data = fetch_data(ticker, "2023-06-01", "2024-06-01")

rsi = Rsi(data['Close'], period=14)
macd_line, signal_line, histogram = macd(data['Close'])
upper, mid, lower = bb_bands(data['Close'])

plot_candlestick(data, ticker=ticker)
plot_rsi(data=data, rsi=rsi, ticker=ticker, kind='candle')
plot_macd(macd_line, signal_line, histogram, ticker=ticker, data=data, kind='candle')
plot_bollinger(data=data, adj_close=data['Close'], bb_upper=upper,
               bb_mid=mid, bb_lower=lower, ticker=ticker, kind='candle')
```

### Example 2: Moving Average Strategy with Candlesticks
```python
from QuantResearch import fetch_data, sma, ema, plot_moving_averages

data = fetch_data("MSFT", "2023-01-01", "2024-01-01")

sma_20 = sma(data['Close'], period=20)
sma_50 = sma(data['Close'], period=50)
ema_12 = ema(data['Close'], period=12)

plot_moving_averages(data=data, sma_val=sma_20, ema_val=ema_12,
                     ticker="MSFT", kind='candle')

golden_cross = (sma_20 > sma_50) & (sma_20.shift(1) <= sma_50.shift(1))
print(f"Golden Cross signals: {golden_cross.sum()}")
```

### Example 3: RSI Strategy with Candlestick Analysis
```python
from QuantResearch import fetch_data, Rsi, plot_rsi

data = fetch_data("GOOGL", "2023-01-01", "2024-01-01")
rsi = Rsi(data['Close'], period=14)

oversold   = rsi < 30
overbought = rsi > 70

print(f"Oversold signals:  {oversold.sum()}")
print(f"Overbought signals: {overbought.sum()}")

plot_rsi(data=data, rsi=rsi, period=14, ticker="GOOGL", kind='candle')
```

### Example 4: MACD Crossover with Price Action
```python
from QuantResearch import fetch_data, macd, plot_macd

data = fetch_data("TSLA", "2024-01-01", "2024-11-01")
macd_line, signal_line, hist = macd(data['Close'])

bullish = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
bearish = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))

print(f"Bullish signals: {bullish.sum()}")
print(f"Bearish signals: {bearish.sum()}")

plot_macd(macd_line, signal_line, hist, ticker="TSLA", data=data, kind='candle')
```

### Example 5: Bollinger Bands Squeeze Detection
```python
from QuantResearch import fetch_data, bb_bands, plot_bollinger

data = fetch_data("NVDA", "2023-01-01", "2024-01-01")
upper, mid, lower = bb_bands(data['Close'], period=20, num_std=2)

band_width = (upper - lower) / mid
squeeze = band_width < band_width.quantile(0.25)
print(f"Squeeze periods detected: {squeeze.sum()}")

plot_bollinger(data=data, adj_close=data['Close'], bb_upper=upper,
               bb_mid=mid, bb_lower=lower, ticker="NVDA", kind='candle')
```

### Example 6: Advanced Indicators
```python
from QuantResearch.indicators import (fetch_data, stochastic, adx,
                                       parabolic_sar, pivot_points, fibonacci_levels)

data = fetch_data("TCS.NS", "2023-01-01", "2024-01-01")

k, d = stochastic(data, k_period=14, d_period=3)
print(f"Stoch %K: {k.iloc[-1]:.2f}  %D: {d.iloc[-1]:.2f}")

adx_val, plus_di, minus_di = adx(data, period=14)
print(f"ADX: {adx_val.iloc[-1]:.2f}  +DI: {plus_di.iloc[-1]:.2f}  -DI: {minus_di.iloc[-1]:.2f}")

sar, trend = parabolic_sar(data)
print(f"SAR: {sar.iloc[-1]:.2f}  Trend: {'UP' if trend.iloc[-1] == 1 else 'DOWN'}")

pp = pivot_points(data)
print(f"Pivot: {pp['P']:.2f}  R1: {pp['R1']:.2f}  S1: {pp['S1']:.2f}")

fib = fibonacci_levels(data)
for lvl, price in fib.items():
    print(f"  {lvl}: {price:.2f}")
```

### Example 7: Full Backtest via QuantQL
```python
from QuantResearch.backtest_engine import run_backtest

result = run_backtest("""
BACKTEST "ADX + Stochastic Strategy"
MARKET NSE
TICKER HDFCBANK
PERIOD 1Y

USE STOCH(14, 3)
USE ADX(14)

BUY  WHEN STOCH_K < 20 AND STOCH_K CROSSES_ABOVE STOCH_D AND ADX > 25
SELL WHEN STOCH_K > 80 OR STOCH_K CROSSES_BELOW STOCH_D

CAPITAL 200000
POSITION_SIZE 80%
STOP_LOSS 4%
TAKE_PROFIT 12%
COMMISSION 0.1%
""")

for k, v in result.metrics.items():
    print(f"{k:<25} {v}")
```

---

## 📋 Requirements

| Package | Version | Purpose |
|---|---|---|
| Python | >= 3.7 | Runtime environment |
| pandas | >= 1.3.0 | Data manipulation |
| yfinance | >= 0.2.0 | Financial data retrieval |
| matplotlib | >= 3.4.0 | Visualization |
| numpy | >= 1.19.0 | Numerical computations |
| tkinter | (stdlib) | GUI dashboard |
| tkcalendar | >= 1.6.0 | Date pickers in dashboard |

## 👥 Authors

QuantResearch is developed and maintained by:

**Vinayak Shinde**
- Email: vinayak.r.shinde.1729@gmail.com
- GitHub: [@vinayak1729-web](https://github.com/vinayak1729-web)
- Role: Lead Developer

**Vishal Mishra**
- Email: vishal214.mishra@gmail.com
- GitHub: [@vishalmishra369](https://github.com/vishalmishra369)
- Role: Co-Developer

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🤝 Support
For issues, questions, or feature requests:

- **GitHub Issues:** [Report a bug](https://github.com/vinayak1729-web/QuantR/issues)
- **Documentation:** [View on GitHub](https://github.com/vinayak1729-web/QuantR)
- **Email Support:** Contact the authors

## ⚠️ Disclaimer
**Important:** QuantResearch is provided for educational and research purposes only. It is not intended as financial advice.

- Always consult with a financial advisor before making investment decisions
- Past performance does not guarantee future results
- Technical indicators are tools; they should not be used as sole decision-making factors
- Use proper risk management in all trading activities
- Test strategies thoroughly before live trading
- Backtest results are simulated on historical data and do not account for all real-world trading conditions

## 📞 Contact
For more information, visit:

- **Repository:** https://github.com/vinayak1729-web/QuantR
- **PyPI Package:** https://pypi.org/project/QuantResearch/

*Made with ❤️ by Vinayak Shinde and Vishal Mishra*

# QuantResearch

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/QuantResearch.svg)](https://pypi.org/project/QuantResearch/)

A comprehensive Python library for quantitative financial analysis, technical indicator calculation, and trading signal visualization. QuantResearch provides easy-to-use functions for fetching market data, calculating technical indicators, and generating trading insights.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Data Fetching](#data-fetching)
  - [Technical Indicators](#technical-indicators)
  - [Visualization](#visualization)
- [Usage Examples](#usage-examples)
- [Requirements](#requirements)
- [Authors](#authors)
- [License](#license)
- [Support](#support)

## 🎯 Overview

QuantResearch is designed for traders, financial analysts, and quantitative researchers who need reliable technical analysis tools. It combines data fetching, indicator calculation, and professional visualization into a single, intuitive package.

Whether you're backtesting trading strategies, analyzing market trends, or building automated trading systems, QuantResearch provides the essential tools you need.

## ✨ Features

- **📊 Data Fetching**: Download historical OHLCV data from Yahoo Finance
- **📈 Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, SMA, EMA, DEMA, TEMA, RVWAP
- **🎨 Professional Visualization**: Beautiful charts for price action, indicators, and trading signals
- **🔔 Signal Generation**: Automatic buy/sell crossover point detection
- **⚡ Simple API**: Intuitive functions that are easy to learn and use
- **🔧 Customizable Parameters**: Adjust periods and thresholds for your strategy
- **📱 Cross-Platform**: Works on Windows, macOS, and Linux

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

# Step 3: Visualize
plot_rsi(rsi, period=14, ticker=ticker)
```

Run this and you'll see a beautiful RSI chart with overbought/oversold levels!

---

## 📚 API Reference

### Data Fetching

#### `fetch_data(ticker, start_date, end_date)`

Downloads historical OHLCV (Open, High, Low, Close, Volume, Adjusted Close) data for a given ticker from Yahoo Finance.

**Parameters:**
- `ticker` (str): Stock ticker symbol (e.g., "AAPL", "MSFT", "GOOGL")
- `start_date` (str): Start date in format "YYYY-MM-DD"
- `end_date` (str): End date in format "YYYY-MM-DD"

**Returns:**
- `pandas.DataFrame`: Contains columns: Open, High, Low, Close, Adj Close, Volume

**Example:**
```python
data = fetch_data("AAPL", "2023-01-01", "2024-01-01")
print(data.head())
print(f"Shape: {data.shape}")
```

**Output:**
```
            Open    High     Low   Close  Adj Close        Volume
Date                                                              
2023-01-03  130.03  130.90  129.64  130.03  129.47      57098400
2023-01-04  130.47  131.05  129.89  130.73  130.16      48480400
```

---

### Technical Indicators

#### `Rsi(price, period=14)`

**Relative Strength Index** - A momentum oscillator measuring the magnitude of recent price changes. Identifies overbought and oversold conditions.

**Parameters:**
- `price` (pandas.Series): Price series (typically closing prices)
- `period` (int): Lookback period for RSI calculation (default: 14)

**Returns:**
- `pandas.Series`: RSI values ranging from 0 to 100

**Interpretation:**
```
RSI > 70  → Overbought (potential sell signal)
RSI < 30  → Oversold (potential buy signal)
30-70     → Neutral zone
```

**Example:**
```python
rsi = Rsi(data['Close'], period=14)
print(f"Current RSI: {rsi.iloc[-1]:.2f}")

# Find overbought conditions
overbought = rsi[rsi > 70]
print(f"Overbought signals: {len(overbought)}")
```

---

#### `bb_bands(price, period=20, num_std=2)`

**Bollinger Bands** - Volatility bands placed above and below a moving average. Consist of three lines: upper band, middle band (SMA), and lower band.

**Parameters:**
- `price` (pandas.Series): Price series (typically closing prices)
- `period` (int): Lookback period for moving average (default: 20)
- `num_std` (int/float): Number of standard deviations (default: 2)

**Returns:**
- Tuple of three `pandas.Series`: (upper_band, middle_band, lower_band)

**Interpretation:**
```
Price near upper band  → Potentially overbought
Price near lower band  → Potentially oversold
Band width change      → Indicates volatility changes
```

**Example:**
```python
upper, mid, lower = bb_bands(data['Close'], period=20, num_std=2)
plot_bollinger(data['Adj Close'], upper, mid, lower, ticker="AAPL")

# Check for breakouts
breakout_up = data['Close'] > upper
breakout_down = data['Close'] < lower
```

---

#### `macd(price, short_period=12, long_period=26, signal_period=9)`

**MACD** (Moving Average Convergence Divergence) - A trend-following momentum indicator that shows the relationship between two moving averages.

**Parameters:**
- `price` (pandas.Series): Price series
- `short_period` (int): Short EMA period (default: 12)
- `long_period` (int): Long EMA period (default: 26)
- `signal_period` (int): Signal line EMA period (default: 9)

**Returns:**
- Tuple of three `pandas.Series`: (macd_line, signal_line, histogram)

**Interpretation:**
```
MACD crosses above signal  → Bullish signal (buy)
MACD crosses below signal  → Bearish signal (sell)
Histogram divergence       → Potential trend reversal
```

**Example:**
```python
macd_line, signal_line, hist = indicators.macd(data['Close'])
visualize.show_macd(macd_line, signal_line, hist, "AAPL")

# Detect crossovers
bullish_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
bearish_cross = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
```

---

#### `atr(data, period=14)`

**Average True Range** - A volatility indicator measuring the average price movement range over a period.

**Parameters:**
- `data` (pandas.DataFrame): OHLC data with 'High', 'Low', 'Close' columns
- `period` (int): Lookback period (default: 14)

**Returns:**
- `pandas.Series`: ATR values

**Interpretation:**
```
High ATR   → High volatility (wide price swings)
Low ATR    → Low volatility (narrow price range)
Rising ATR → Increasing volatility
```

**Use Cases:**
- Setting stop-loss and take-profit levels
- Position sizing in trading
- Identifying breakout opportunities

**Example:**
```python
atr_values = indicators.atr(data, period=14)

# Use ATR for stop-loss placement
stop_loss = data['Close'] - (atr_values * 2)
take_profit = data['Close'] + (atr_values * 3)

print(f"Current ATR: {atr_values.iloc[-1]:.2f}")
```

---

#### `sma(price, period=9)`

**Simple Moving Average** - The average price over a specified period, giving equal weight to all prices.

**Parameters:**
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

**Returns:**
- `pandas.Series`: SMA values

**Characteristics:**
- Slower to respond to price changes
- Good for identifying long-term trends
- Less responsive than EMA

**Example:**
```python
sma_9 = indicators.sma(data['Close'], period=9)
sma_20 = indicators.sma(data['Close'], period=20)
sma_50 = indicators.sma(data['Close'], period=50)

# Golden cross: Fast SMA crosses above slow SMA
golden_cross = (sma_9 > sma_20) & (sma_9.shift(1) <= sma_20.shift(1))
```

---

#### `ema(price, period=9)`

**Exponential Moving Average** - A moving average that gives more weight to recent prices, making it more responsive than SMA.

**Parameters:**
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

**Returns:**
- `pandas.Series`: EMA values

**Characteristics:**
- More responsive to recent price changes
- Better for short-term analysis
- Faster crossovers than SMA

**Example:**
```python
ema_12 = indicators.ema(data['Close'], period=12)
ema_26 = indicators.ema(data['Close'], period=26)

# EMA trend confirmation
uptrend = (ema_12 > ema_26) & (data['Close'] > ema_12)
```

---

#### `demma(price, period=9)`

**Double Exponential Moving Average** - A smoother trend indicator that reduces lag by applying EMA twice. More responsive than SMA with less lag than single EMA.

**Parameters:**
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

**Returns:**
- `pandas.Series`: DEMA values

**Formula:**
```
DEMA = 2 × EMA - EMA(EMA)
```

**Example:**
```python
dema_9 = indicators.demma(data['Close'], period=9)
visualize.plot_moving_averages(data['Close'], 
                               indicators.sma(data['Close']), 
                               indicators.ema(data['Close']), 
                               dema_9, 
                               indicators.temma(data['Close']))
```

---

#### `temma(price, period=9)`

**Triple Exponential Moving Average** - The smoothest trend indicator with minimal lag. Uses three levels of EMA smoothing.

**Parameters:**
- `price` (pandas.Series): Price series
- `period` (int): Lookback period (default: 9)

**Returns:**
- `pandas.Series`: TEMA values

**Formula:**
```
TEMA = 3 × EMA - 3 × EMA(EMA) + EMA(EMA(EMA))
```

**Example:**
```python
tema_9 = indicators.temma(data['Close'], period=9)

# TEMA is ideal for trend-following strategies
tema_trend = tema_9.diff() > 0  # Uptrend when TEMA increasing
```

---

#### `RVWAP(high, low, close, volume, period=20)`

**Volume-Weighted Average Price** - A trading benchmark that reflects both price and volume, giving more weight to price levels with higher volume.

**Parameters:**
- `high` (pandas.Series): High prices
- `low` (pandas.Series): Low prices
- `close` (pandas.Series): Close prices
- `volume` (pandas.Series): Trading volume
- `period` (int): Lookback period (default: 20)

**Returns:**
- `pandas.Series`: VWAP values

**Interpretation:**
```
Price above VWAP  → Bullish bias (institutional accumulation)
Price below VWAP  → Bearish bias (institutional distribution)
```

**Example:**
```python
vwap = indicators.RVWAP(data['High'], data['Low'], data['Close'], 
                        data['Volume'], period=20)

# VWAP reversal strategy
vwap_bounce = (data['Close'] > vwap) & (data['Close'].shift(1) <= vwap.shift(1))
```

---

### Visualization

#### `show_macd(macdline, signalLine, hist, ticker)`

Displays MACD line, signal line, and histogram with color-coded bars.

**Parameters:**
- `macdline` (pandas.Series): MACD line values
- `signalLine` (pandas.Series): Signal line values
- `hist` (pandas.Series): Histogram values
- `ticker` (str): Stock ticker for chart title

**Example:**
```python
macd_line, signal_line, histogram = indicators.macd(data['Close'])
visualize.show_macd(macd_line, signal_line, histogram, "AAPL")
```

---

#### `plot_bollinger(ajd_close, bb_upper, bb_mid, bb_lower, ticker=None)`

Visualizes Bollinger Bands with price action overlay.

**Parameters:**
- `ajd_close` (pandas.Series): Adjusted close prices
- `bb_upper` (pandas.Series): Upper Bollinger Band
- `bb_mid` (pandas.Series): Middle Bollinger Band (SMA)
- `bb_lower` (pandas.Series): Lower Bollinger Band
- `ticker` (str, optional): Stock ticker for title

**Example:**
```python
upper, mid, lower = indicators.bb_bands(data['Close'])
visualize.plot_bollinger(data['Adj Close'], upper, mid, lower, ticker="AAPL")
```

---

#### `plot_rsi(rsi, period=14, lower=30, upper=70, ticker=None)`

Displays RSI with overbought (70) and oversold (30) threshold lines.

**Parameters:**
- `rsi` (pandas.Series): RSI values
- `period` (int): RSI period for label (default: 14)
- `lower` (int): Oversold threshold (default: 30)
- `upper` (int): Overbought threshold (default: 70)
- `ticker` (str, optional): Stock ticker for title

**Example:**
```python
rsi = indicators.Rsi(data['Close'])
visualize.plot_rsi(rsi, period=14, lower=30, upper=70, ticker="AAPL")
```

---

#### `plot_moving_averages(price, sma_val, ema_val, dema_val, tema_val, title="Moving Averages Comparison")`

Compares four different moving averages on the same chart.

**Parameters:**
- `price` (pandas.Series): Price series
- `sma_val` (pandas.Series): Simple Moving Average
- `ema_val` (pandas.Series): Exponential Moving Average
- `dema_val` (pandas.Series): Double Exponential Moving Average
- `tema_val` (pandas.Series): Triple Exponential Moving Average
- `title` (str, optional): Chart title

**Example:**
```python
sma = indicators.sma(data['Close'], period=9)
ema = indicators.ema(data['Close'], period=9)
dema = indicators.demma(data['Close'], period=9)
tema = indicators.temma(data['Close'], period=9)

visualize.plot_moving_averages(data['Close'], sma, ema, dema, tema, 
                               title="AAPL Moving Averages Analysis")
```

---

#### `plot_crossovers(price, ma1, ma2, ma1_label='MA1', ma2_label='MA2')`

Visualizes moving average crossovers with automatic buy/sell signal detection. Green triangles indicate buy signals, red triangles indicate sell signals.

**Parameters:**
- `price` (pandas.Series): Price series
- `ma1` (pandas.Series): First moving average (typically fast)
- `ma2` (pandas.Series): Second moving average (typically slow)
- `ma1_label` (str): Label for first MA (default: 'MA1')
- `ma2_label` (str): Label for second MA (default: 'MA2')

**Returns:**
- Displays chart with green triangles (buy signals) and red triangles (sell signals)

**Example:**
```python
sma_fast = indicators.sma(data['Close'], period=9)
sma_slow = indicators.sma(data['Close'], period=21)

visualize.plot_crossovers(data['Close'], sma_fast, sma_slow, 
                         ma1_label='SMA 9', ma2_label='SMA 21')
```

---

## 💡 Usage Examples

### Example 1: Complete Technical Analysis Dashboard

```python
from QuantResearch import (fetch_data, Rsi, macd, bb_bands, atr, 
                           sma, plot_rsi, show_macd, plot_bollinger, plot_crossovers)

# Fetch data for analysis
ticker = "AAPL"
data = fetch_data(ticker, "2023-06-01", "2024-06-01")

# Calculate all indicators
rsi = Rsi(data['Close'], period=14)
macd_line, signal_line, histogram = macd(data['Close'])
upper, mid, lower = bb_bands(data['Close'])
atr_val = atr(data, period=14)
sma_9 = sma(data['Close'], period=9)
sma_21 = sma(data['Close'], period=21)

# Display all charts
plot_rsi(rsi, ticker=ticker)
show_macd(macd_line, signal_line, histogram, ticker)
plot_bollinger(data['Adj Close'], upper, mid, lower, ticker=ticker)
plot_crossovers(data['Close'], sma_9, sma_21, "SMA 9", "SMA 21")

print(f"Current RSI: {rsi.iloc[-1]:.2f}")
print(f"Current ATR: {atr_val.iloc[-1]:.2f}")
```

---

### Example 2: Moving Average Crossover Strategy

```python
from QuantResearch import fetch_data, ema, plot_crossovers

data = fetch_data("MSFT", "2023-01-01", "2024-01-01")

# Fast and slow moving averages
fast_ma = ema(data['Close'], period=9)
slow_ma = ema(data['Close'], period=21)

# Detect signals
buy_signal = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
sell_signal = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

print(f"Total Buy Signals: {buy_signal.sum()}")
print(f"Total Sell Signals: {sell_signal.sum()}")

# Visualize
plot_crossovers(data['Close'], fast_ma, slow_ma, "EMA 9", "EMA 21")
```

---

### Example 3: Volatility Analysis

```python
from QuantResearch import fetch_data, atr, bb_bands

data = fetch_data("TSLA", "2024-01-01", "2024-11-01")

# Calculate volatility metrics
atr_14 = atr(data, period=14)
bb_upper, bb_mid, bb_lower = bb_bands(data['Close'], period=20)

# Volatility analysis
band_width = (bb_upper - bb_lower) / bb_mid
print("Volatility Statistics:")
print(f"  ATR Mean: {atr_14.mean():.2f}")
print(f"  ATR Std Dev: {atr_14.std():.2f}")
print(f"  Band Width Mean: {band_width.mean():.2f}")

# High volatility days
high_vol_days = atr_14[atr_14 > atr_14.quantile(0.75)]
print(f"\nHigh Volatility Days: {len(high_vol_days)}")
```

---

### Example 4: RSI-Based Trading Signals

```python
from QuantResearch import fetch_data, Rsi, plot_rsi

data = fetch_data("GOOGL", "2023-01-01", "2024-01-01")

# Calculate RSI
rsi = Rsi(data['Close'], period=14)

# Generate signals
oversold = rsi < 30  # Potential buy
overbought = rsi > 70  # Potential sell
neutral = (rsi >= 30) & (rsi <= 70)

print(f"Oversold signals: {oversold.sum()}")
print(f"Overbought signals: {overbought.sum()}")

plot_rsi(rsi, period=14, lower=30, upper=70, ticker="GOOGL")
```

---

## 📋 Requirements

QuantResearch requires the following dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >= 3.7 | Runtime environment |
| pandas | >= 1.3.0 | Data manipulation |
| yfinance | >= 0.2.0 | Financial data retrieval |
| matplotlib | >= 3.4.0 | Visualization |

These will be installed automatically when you install QuantResearch via pip.

---

## 👥 Authors

**QuantResearch** is developed and maintained by:

- **Vinayak Shinde**
  - Email: vinayak.r.shinde.1729@gmail.com
  - GitHub: [@vinayak1729-web](https://github.com/vinayak1729-web)
  - Role: Lead Developer

- **Vishal Mishra**
  - Email: vishal214.mishra@gmail.com
  - GitHub: (https://github.com/vishalmishra369)
  - Role: Co-Developer

### Contributing

We welcome contributions! If you'd like to contribute to QuantResearch, please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🤝 Support

For issues, questions, or feature requests:

- **GitHub Issues**: [Report a bug](https://github.com/vinayak1729-web/QuantR/issues)
- **Documentation**: [View on GitHub](https://github.com/vinayak1729-web/QuantR#readme)
- **Email Support**: Contact the authors

---

## ⚠️ Disclaimer

**Important**: QuantResearch is provided for **educational and research purposes only**. It is **not intended as financial advice**. 

- Always consult with a financial advisor before making investment decisions
- Past performance does not guarantee future results
- Technical indicators are tools; they should not be used as sole decision-making factors
- Use proper risk management in all trading activities
- Test strategies thoroughly before live trading

---

## 📊 What's New

### Version 1.0.0 (Latest)
- ✅ Core technical indicators (RSI, MACD, Bollinger Bands, ATR, SMA, EMA, DEMA, TEMA, VWAP)
- ✅ Professional visualization functions
- ✅ Data fetching from Yahoo Finance
- ✅ Complete documentation and examples

---

## 🙏 Acknowledgments

- **Yahoo Finance** for providing historical market data
- **pandas** and **matplotlib** communities for excellent libraries
- All contributors and users who provide feedback

---

## 📞 Contact

For more information, visit:
- **Repository**: https://github.com/vinayak1729-web/QuantR
- **PyPI Package**: https://pypi.org/project/QuantResearch/

---

**Made with ❤️ by Vinayak Shinde and Vishal Mishra**

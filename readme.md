# QuantResearch 📈

**Technical indicators and visualization tools for quantitative research and algorithmic trading.**

[![PyPI version](https://badge.fury.io/py/QuantResearch.svg)](https://badge.fury.io/py/QuantResearch)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Installation

```bash
pip install QuantResearch
```

---

## 📊 Features

- **Fetch stock data** from Yahoo Finance
- **Technical Indicators**: RSI, MACD, Bollinger Bands, SMA, EMA, DEMA, TEMA
- **Beautiful Visualizations**: Ready-to-use plotting functions
- **Easy to Use**: Simple, intuitive API
- **Lightweight**: Minimal dependencies

---

## 🎯 Quick Start

```python
from QuantResearch import fetch_data, Rsi, plot_rsi

# Fetch stock data
data = fetch_data('AAPL', '2024-01-01', '2024-11-01')

# Calculate RSI
rsi = Rsi(data['Close'], period=14)

# Visualize
plot_rsi(rsi, ticker='AAPL')
```

---

## 📚 Complete Function Reference

### 1. Data Fetching

#### `fetch_data(ticker, start_date, end_date)`

Fetch historical stock data from Yahoo Finance.

**Parameters:**
- `ticker` (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'TSLA')
- `start_date` (str): Start date in 'YYYY-MM-DD' format
- `end_date` (str): End date in 'YYYY-MM-DD' format

**Returns:** pandas DataFrame with OHLCV data

**Example:**
```python
from QuantResearch import fetch_data

# Fetch Apple stock data
data = fetch_data('AAPL', '2023-01-01', '2024-01-01')
print(data.head())
```

---

### 2. Technical Indicators

#### `Rsi(price, period=14)`

Calculate Relative Strength Index (RSI).

**Parameters:**
- `price` (pandas Series): Price data (typically closing prices)
- `period` (int, default=14): Number of periods for RSI calculation

**Returns:** pandas Series with RSI values (0-100)

**Example:**
```python
from QuantResearch import fetch_data, Rsi

data = fetch_data('MSFT', '2024-01-01', '2024-11-01')
rsi = Rsi(data['Close'], period=14)

print(f"Current RSI: {rsi.iloc[-1]:.2f}")
```

**Interpretation:**
- RSI > 70: Overbought (potential sell signal)
- RSI < 30: Oversold (potential buy signal)

---

#### `bb_bands(price, period=20, num_std=2)`

Calculate Bollinger Bands.

**Parameters:**
- `price` (pandas Series): Price data
- `period` (int, default=20): Moving average period
- `num_std` (int, default=2): Number of standard deviations

**Returns:** Tuple of (upper_band, middle_band, lower_band)

**Example:**
```python
from QuantResearch import fetch_data, bb_bands

data = fetch_data('TSLA', '2024-01-01', '2024-11-01')
upper, middle, lower = bb_bands(data['Close'], period=20, num_std=2)

print(f"Upper Band: {upper.iloc[-1]:.2f}")
print(f"Middle Band: {middle.iloc[-1]:.2f}")
print(f"Lower Band: {lower.iloc[-1]:.2f}")
```

**Interpretation:**
- Price near upper band: Potentially overbought
- Price near lower band: Potentially oversold
- Band squeeze: Low volatility, potential breakout coming

---

#### `macd(price, short_period=12, long_period=26, signal_period=9)`

Calculate Moving Average Convergence Divergence (MACD).

**Parameters:**
- `price` (pandas Series): Price data
- `short_period` (int, default=12): Short EMA period
- `long_period` (int, default=26): Long EMA period
- `signal_period` (int, default=9): Signal line period

**Returns:** Tuple of (macd_line, signal_line, histogram)

**Example:**
```python
from QuantResearch import fetch_data, macd

data = fetch_data('GOOGL', '2024-01-01', '2024-11-01')
macd_line, signal_line, histogram = macd(data['Close'])

print(f"MACD: {macd_line.iloc[-1]:.2f}")
print(f"Signal: {signal_line.iloc[-1]:.2f}")
print(f"Histogram: {histogram.iloc[-1]:.2f}")
```

**Interpretation:**
- MACD crosses above signal: Bullish (buy signal)
- MACD crosses below signal: Bearish (sell signal)
- Positive histogram: Bullish momentum
- Negative histogram: Bearish momentum

---

#### `sma(price, period=9)`

Calculate Simple Moving Average.

**Parameters:**
- `price` (pandas Series): Price data
- `period` (int, default=9): Number of periods

**Returns:** pandas Series with SMA values

**Example:**
```python
from QuantResearch import fetch_data, sma

data = fetch_data('AAPL', '2024-01-01', '2024-11-01')
sma_20 = sma(data['Close'], period=20)
sma_50 = sma(data['Close'], period=50)

# Golden cross detection
if sma_20.iloc[-1] > sma_50.iloc[-1]:
    print("Golden Cross: Bullish signal!")
```

---

#### `ema(price, period=9)`

Calculate Exponential Moving Average.

**Parameters:**
- `price` (pandas Series): Price data
- `period` (int, default=9): Number of periods

**Returns:** pandas Series with EMA values

**Example:**
```python
from QuantResearch import fetch_data, ema

data = fetch_data('NVDA', '2024-01-01', '2024-11-01')
ema_12 = ema(data['Close'], period=12)
ema_26 = ema(data['Close'], period=26)

print(f"EMA(12): {ema_12.iloc[-1]:.2f}")
print(f"EMA(26): {ema_26.iloc[-1]:.2f}")
```

---

#### `demma(price, period=9)`

Calculate Double Exponential Moving Average (DEMA).

**Parameters:**
- `price` (pandas Series): Price data
- `period` (int, default=9): Number of periods

**Returns:** pandas Series with DEMA values

**Example:**
```python
from QuantResearch import fetch_data, demma

data = fetch_data('AMZN', '2024-01-01', '2024-11-01')
dema = demma(data['Close'], period=20)
print(f"DEMA: {dema.iloc[-1]:.2f}")
```

**Note:** DEMA reacts faster to price changes than regular EMA.

---

#### `temma(price, period=9)`

Calculate Triple Exponential Moving Average (TEMA).

**Parameters:**
- `price` (pandas Series): Price data
- `period` (int, default=9): Number of periods

**Returns:** pandas Series with TEMA values

**Example:**
```python
from QuantResearch import fetch_data, temma

data = fetch_data('META', '2024-01-01', '2024-11-01')
tema = temma(data['Close'], period=20)
print(f"TEMA: {tema.iloc[-1]:.2f}")
```

**Note:** TEMA is even more responsive than DEMA, with less lag.

---

### 3. Visualization Functions

#### `plot_rsi(rsi, period=14, lower=30, upper=70, ticker=None)`

Plot RSI with overbought/oversold levels.

**Parameters:**
- `rsi` (pandas Series): RSI values
- `period` (int, default=14): RSI period (for title)
- `lower` (int, default=30): Oversold threshold
- `upper` (int, default=70): Overbought threshold
- `ticker` (str, optional): Ticker symbol for title

**Example:**
```python
from QuantResearch import fetch_data, Rsi, plot_rsi

data = fetch_data('AAPL', '2024-01-01', '2024-11-01')
rsi = Rsi(data['Close'])
plot_rsi(rsi, ticker='AAPL', lower=30, upper=70)
```

---

#### `plot_bollinger(adj_close, bb_upper, bb_mid, bb_lower, ticker=None)`

Plot price with Bollinger Bands.

**Parameters:**
- `adj_close` (pandas Series): Adjusted close prices
- `bb_upper` (pandas Series): Upper Bollinger Band
- `bb_mid` (pandas Series): Middle band (moving average)
- `bb_lower` (pandas Series): Lower Bollinger Band
- `ticker` (str, optional): Ticker symbol for title

**Example:**
```python
from QuantResearch import fetch_data, bb_bands, plot_bollinger

data = fetch_data('TSLA', '2024-01-01', '2024-11-01')
upper, middle, lower = bb_bands(data['Close'], period=20)
plot_bollinger(data['Adj Close'], upper, middle, lower, ticker='TSLA')
```

---

#### `show_macd(macd_line, signal_line, histogram, ticker)`

Plot MACD, signal line, and histogram.

**Parameters:**
- `macd_line` (pandas Series): MACD line values
- `signal_line` (pandas Series): Signal line values
- `histogram` (pandas Series): MACD histogram
- `ticker` (str): Ticker symbol for title

**Example:**
```python
from QuantResearch import fetch_data, macd, show_macd

data = fetch_data('GOOGL', '2024-01-01', '2024-11-01')
macd_line, signal_line, hist = macd(data['Close'])
show_macd(macd_line, signal_line, hist, 'GOOGL')
```

---

## 🔥 Complete Examples

### Example 1: Multi-Indicator Analysis

```python
from QuantResearch import (
    fetch_data, Rsi, macd, bb_bands,
    plot_rsi, show_macd, plot_bollinger
)

# Fetch data
ticker = 'AAPL'
data = fetch_data(ticker, '2024-01-01', '2024-11-01')

# Calculate indicators
rsi = Rsi(data['Close'], period=14)
macd_line, signal_line, hist = macd(data['Close'])
upper, middle, lower = bb_bands(data['Close'], period=20)

# Visualize all indicators
plot_rsi(rsi, ticker=ticker)
show_macd(macd_line, signal_line, hist, ticker)
plot_bollinger(data['Adj Close'], upper, middle, lower, ticker=ticker)
```

---

### Example 2: Simple Trading Strategy

```python
from QuantResearch import fetch_data, Rsi, macd

# Fetch data
data = fetch_data('MSFT', '2024-01-01', '2024-11-01')

# Calculate indicators
rsi = Rsi(data['Close'])
macd_line, signal_line, _ = macd(data['Close'])

# Get latest values
current_rsi = rsi.iloc[-1]
current_macd = macd_line.iloc[-1]
current_signal = signal_line.iloc[-1]

# Simple strategy
if current_rsi < 30 and current_macd > current_signal:
    print("🟢 BUY SIGNAL: RSI oversold + MACD bullish crossover")
elif current_rsi > 70 and current_macd < current_signal:
    print("🔴 SELL SIGNAL: RSI overbought + MACD bearish crossover")
else:
    print("⚪ HOLD: No clear signal")
```

---

### Example 3: Multiple Stocks Comparison

```python
from QuantResearch import fetch_data, Rsi
import pandas as pd

tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
results = {}

for ticker in tickers:
    data = fetch_data(ticker, '2024-01-01', '2024-11-01')
    rsi = Rsi(data['Close'])
    results[ticker] = rsi.iloc[-1]

# Display results
print("\n📊 Current RSI Values:")
print("-" * 30)
for ticker, rsi_value in sorted(results.items(), key=lambda x: x[1]):
    status = "🔴 Overbought" if rsi_value > 70 else "🟢 Oversold" if rsi_value < 30 else "⚪ Neutral"
    print(f"{ticker:6s}: {rsi_value:6.2f} {status}")
```

---

### Example 4: Moving Average Strategy

```python
from QuantResearch import fetch_data, sma, ema
import matplotlib.pyplot as plt

# Fetch data
data = fetch_data('AAPL', '2024-01-01', '2024-11-01')

# Calculate multiple moving averages
sma_20 = sma(data['Close'], period=20)
sma_50 = sma(data['Close'], period=50)
ema_12 = ema(data['Close'], period=12)

# Plot
plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='Close Price', linewidth=2)
plt.plot(sma_20, label='SMA(20)', linestyle='--')
plt.plot(sma_50, label='SMA(50)', linestyle='--')
plt.plot(ema_12, label='EMA(12)', linestyle='-.')
plt.title('AAPL - Moving Averages')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
```

---

## 🎓 Understanding the Indicators

### RSI (Relative Strength Index)
- **Range**: 0-100
- **Overbought**: > 70
- **Oversold**: < 30
- **Best for**: Identifying reversal points

### MACD (Moving Average Convergence Divergence)
- **Bullish**: MACD crosses above signal line
- **Bearish**: MACD crosses below signal line
- **Best for**: Trend following and momentum

### Bollinger Bands
- **Upper Band**: Price resistance level
- **Lower Band**: Price support level
- **Best for**: Volatility and breakout trading

### Moving Averages (SMA, EMA, DEMA, TEMA)
- **SMA**: Simple average, smooth but slow
- **EMA**: Exponential, more responsive
- **DEMA**: Double exponential, even faster
- **TEMA**: Triple exponential, fastest response

---

## 📦 Dependencies

- `yfinance` >= 0.2.0
- `pandas` >= 1.3.0
- `matplotlib` >= 3.4.0

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Vinayak Shinde**
- Email: vinayak.r.shinde.1729@gmail.com
- GitHub: [@vinayak1729-web](https://github.com/vinayak1729-web)

---

## ⭐ Support

If you find this project helpful, please give it a star ⭐ on GitHub!

---

## 📊 Version History

- **0.0.1** (2024-11-19): Initial release
  - Basic technical indicators (RSI, MACD, Bollinger Bands)
  - Moving averages (SMA, EMA, DEMA, TEMA)
  - Visualization functions
  - Data fetching from Yahoo Finance

---

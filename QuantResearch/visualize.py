
import matplotlib.pyplot as plt

def show_macd(macdline, signalLine, hist, ticker):
    fig, ax = plt.subplots(figsize=(10,6))

    # MACD and signal lines
    macdline.plot(ax=ax, label='MACD', color='blue')
    signalLine.plot(ax=ax, label='Signal', color='orange')

    # Histogram (bar) with colors by sign
    colors = hist.apply(lambda x: 'green' if x >= 0 else 'red')
    ax.bar(hist.index, hist.values, color=colors, alpha=0.8)

    ax.set_title(f"MACD, Signal & Histogram for {ticker}")
    ax.legend()
    plt.show()


def plot_bollinger(ajd_close,bb_upper,bb_mid,bb_lower, ticker=None):
    plt.figure(figsize=(10,6))

    plt.plot(ajd_close, label='Adj Close')
    plt.plot(bb_upper, color='red', linestyle='--', label='BB-UPPER')
    plt.plot(bb_mid,   color='orange', label='rolling mean')
    plt.plot(bb_lower, color='red', linestyle='--', label='BB-LOWER')

    plt.xlabel('date')
    plt.ylabel('price')
    title = 'Bollinger Bands'
    if ticker is not None:
        title += f' for {ticker}'
    plt.title(title)

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_rsi(rsi, period=14, lower=30, upper=70, ticker=None):
    plt.figure(figsize=(10,4))
    plt.plot(rsi, label=f'RSI {period}', color='purple')

    # horizontal lines
    plt.axhline(y=upper, color='red', linestyle='--', linewidth=1)
    plt.axhline(y=lower, color='green', linestyle='--', linewidth=1)

    plt.ylim(0, 100)
    title = f'RSI ({period})'
    if ticker is not None:
        title += f' for {ticker}'
    plt.title(title)

    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def _add_candlesticks(ax, data, width=0.6):
    """
    Helper function to add candlesticks to an existing axis.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to plot on
    data : pandas.DataFrame
        DataFrame with OHLC columns: 'Open', 'High', 'Low', 'Close'
    width : float, default 0.6
        Width of candlestick bodies
        
    Returns:
    --------
    pandas.DatetimeIndex or pandas.Index
        The cleaned index after removing NaN values
        
    Raises:
    -------
    ValueError
        If required OHLC columns are missing
    """
    required_cols = ['Open', 'High', 'Low', 'Close']
    missing_cols = [col for col in required_cols if col not in data.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    data_clean = data[required_cols].dropna()
    
    if len(data_clean) == 0:
        raise ValueError("No valid data to plot after removing NaN values")
    
    open_prices = data_clean['Open'].values
    close_prices = data_clean['Close'].values
    high_prices = data_clean['High'].values
    low_prices = data_clean['Low'].values
    
    x = range(len(open_prices))
    
    for i in x:
        open_val = float(open_prices[i])
        close_val = float(close_prices[i])
        high_val = float(high_prices[i])
        low_val = float(low_prices[i])
        
        # Color: green for bullish, red for bearish
        color = 'green' if close_val >= open_val else 'red'
        
        # Draw the wick (high-low line)
        ax.plot([i, i], [low_val, high_val], 
                color='black', linewidth=1, zorder=1)
        
        # Draw the body (open-close rectangle)
        body_height = abs(close_val - open_val)
        body_bottom = min(open_val, close_val)
        
        ax.add_patch(
            plt.Rectangle(
                (i - width/2, body_bottom),
                width,
                body_height,
                facecolor=color,
                edgecolor='black',
                linewidth=0.5,
                alpha=0.7,
                zorder=2
            )
        )
    
    return data_clean.index


def _format_x_axis(ax, index, max_ticks=10):
    """
    Helper function to format x-axis labels.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes object to format
    index : pandas.Index
        The index to use for labels
    max_ticks : int, default 10
        Maximum number of x-axis ticks to display
    """
    x = range(len(index))
    
    if hasattr(index, 'strftime'):
        # Format date labels
        labels = [date.strftime('%Y-%m-%d') for date in index]
        step = max(1, len(x) // max_ticks)
        ax.set_xticks(x[::step])
        ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)], 
                          rotation=45, ha='right')
    else:
        # Use sequential labels
        step = max(1, len(x) // max_ticks)
        ax.set_xticks(x[::step])
        ax.set_xticklabels([f'Day {i+1}' for i in range(0, len(x), step)], 
                          rotation=45, ha='right')


def plot_candlestick(data, ticker='Stock'):
    """
    Plot a candlestick chart from OHLC data.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame with columns: 'Open', 'High', 'Low', 'Close'
        Index should be dates for proper date formatting
    ticker : str, default 'Stock'
        Ticker symbol for the chart title
        
    Returns:
    --------
    None
        Displays the plot
        
    Example:
    --------
    >>> plot_candlestick(data, ticker='GOOG')
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    try:
        clean_index = _add_candlesticks(ax, data)
        _format_x_axis(ax, clean_index)
        
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Price', fontsize=10)
        ax.set_title(f'{ticker} Candlestick Chart', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error plotting candlestick chart: {e}")
        plt.close(fig)


def plot_macd(macd_line, signal_line, histogram, ticker=None, 
              data=None, kind='line'):
    """
    Plot MACD (Moving Average Convergence Divergence) indicator.
    
    Parameters:
    -----------
    macd_line : pandas.Series
        MACD line values
    signal_line : pandas.Series
        Signal line values
    histogram : pandas.Series
        MACD histogram values
    ticker : str, optional
        Ticker symbol for the chart title
    data : pandas.DataFrame, optional
        DataFrame with OHLC data (required if kind='candle')
    kind : str, default 'line'
        Chart type: 'line' or 'candle'
        
    Returns:
    --------
    None
        Displays the plot
        
    Example:
    --------
    >>> plot_macd(data['macd'], data['signal'], data['hist'], ticker='GOOG')
    """
    if kind == 'candle' and data is not None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                        gridspec_kw={'height_ratios': [2, 1]})
        
        try:
            # Price chart with candlesticks
            clean_index = _add_candlesticks(ax1, data)
            _format_x_axis(ax1, clean_index)
            
            ax1.set_ylabel('Price', fontsize=10)
            title = 'Price Chart'
            if ticker:
                title += f' - {ticker}'
            ax1.set_title(title, fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # Align MACD data
            x = range(len(clean_index))
            macd_aligned = macd_line.reindex(clean_index)
            signal_aligned = signal_line.reindex(clean_index)
            hist_aligned = histogram.reindex(clean_index)
            
            # MACD chart
            ax2.plot(x, macd_aligned.values, label='MACD', color='blue', linewidth=1.5)
            ax2.plot(x, signal_aligned.values, label='Signal', color='orange', linewidth=1.5)
            
            # Histogram with colors
            colors = ['green' if val >= 0 else 'red' for val in hist_aligned.values]
            ax2.bar(x, hist_aligned.values, color=colors, alpha=0.8, width=0.8)
            
            _format_x_axis(ax2, clean_index)
            
        except Exception as e:
            print(f"Error plotting MACD with candlesticks: {e}")
            plt.close(fig)
            return
            
    else:
        fig, ax2 = plt.subplots(figsize=(12, 6))
        
        # MACD and signal lines
        macd_line.plot(ax=ax2, label='MACD', color='blue', linewidth=1.5)
        signal_line.plot(ax=ax2, label='Signal', color='orange', linewidth=1.5)
        
        # Histogram with colors
        colors = histogram.apply(lambda x: 'green' if x >= 0 else 'red')
        ax2.bar(histogram.index, histogram.values, color=colors, alpha=0.8, width=0.8)
        
        plt.xticks(rotation=45, ha='right')
    
    # Common formatting
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('MACD Value', fontsize=10)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    title = 'MACD, Signal & Histogram'
    if ticker:
        title += f' for {ticker}'
    if kind != 'candle':
        ax2.set_title(title, fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def plot_bollinger(data=None, adj_close=None, bb_upper=None, bb_mid=None, 
                   bb_lower=None, ticker=None, kind='line'):
    """
    Plot Bollinger Bands with optional candlestick chart.
    
    Parameters:
    -----------
    data : pandas.DataFrame, optional
        DataFrame with OHLC data (required if kind='candle')
    adj_close : pandas.Series
        Adjusted close prices
    bb_upper : pandas.Series
        Upper Bollinger Band
    bb_mid : pandas.Series
        Middle Bollinger Band (rolling mean)
    bb_lower : pandas.Series
        Lower Bollinger Band
    ticker : str, optional
        Ticker symbol for the chart title
    kind : str, default 'line'
        Chart type: 'line' or 'candle'
        
    Returns:
    --------
    None
        Displays the plot
        
    Example:
    --------
    >>> plot_bollinger(adj_close=data['Adj Close'], bb_upper=data['bb_upper'],
    ...                bb_mid=data['bb_mid'], bb_lower=data['bb_lower'], 
    ...                ticker='GOOG')
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    try:
        if kind == 'candle' and data is not None:
            clean_index = _add_candlesticks(ax, data)
            
            # Align BB data with candlestick indices
            x = range(len(clean_index))
            bb_upper_aligned = bb_upper.reindex(clean_index)
            bb_mid_aligned = bb_mid.reindex(clean_index)
            bb_lower_aligned = bb_lower.reindex(clean_index)
            
            ax.plot(x, bb_upper_aligned.values, color='red', linestyle='--', 
                    label='BB Upper', linewidth=1.5)
            ax.plot(x, bb_mid_aligned.values, color='orange', 
                    label='Rolling Mean', linewidth=1.5)
            ax.plot(x, bb_lower_aligned.values, color='red', linestyle='--', 
                    label='BB Lower', linewidth=1.5)
            
            # Fill between bands
            ax.fill_between(x, bb_upper_aligned.values, bb_lower_aligned.values, 
                           alpha=0.1, color='gray')
            
            _format_x_axis(ax, clean_index)
            
        else:
            ax.plot(adj_close, label='Adj Close', linewidth=2, color='blue')
            ax.plot(bb_upper, color='red', linestyle='--', label='BB Upper', linewidth=1.5)
            ax.plot(bb_mid, color='orange', label='Rolling Mean', linewidth=1.5)
            ax.plot(bb_lower, color='red', linestyle='--', label='BB Lower', linewidth=1.5)
            
            # Fill between bands
            ax.fill_between(bb_upper.index, bb_upper.values, bb_lower.values, 
                           alpha=0.1, color='gray')
            
            plt.xticks(rotation=45, ha='right')
        
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Price', fontsize=10)
        
        title = 'Bollinger Bands'
        if ticker:
            title += f' for {ticker}'
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error plotting Bollinger Bands: {e}")
        plt.close(fig)


def plot_rsi(data=None, rsi=None, period=14, lower=30, upper=70, 
             ticker=None, kind='line'):
    """
    Plot RSI (Relative Strength Index) with optional price chart.
    
    Parameters:
    -----------
    data : pandas.DataFrame, optional
        DataFrame with OHLC data (required if kind='candle')
    rsi : pandas.Series
        RSI values
    period : int, default 14
        RSI period
    lower : int, default 30
        Oversold threshold
    upper : int, default 70
        Overbought threshold
    ticker : str, optional
        Ticker symbol
    kind : str, default 'line'
        Chart type: 'line' or 'candle'
        
    Returns:
    --------
    None
        Displays the plot
        
    Example:
    --------
    >>> plot_rsi(rsi=data['rsi'], period=14, ticker='GOOG')
    """
    try:
        if kind == 'candle' and data is not None:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                            gridspec_kw={'height_ratios': [2, 1]})
            
            # Price chart with candlesticks
            clean_index = _add_candlesticks(ax1, data)
            _format_x_axis(ax1, clean_index)
            
            ax1.set_ylabel('Price', fontsize=10)
            title = 'Price Chart'
            if ticker:
                title += f' - {ticker}'
            ax1.set_title(title, fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # RSI chart
            x = range(len(clean_index))
            rsi_aligned = rsi.reindex(clean_index)
            ax2.plot(x, rsi_aligned.values, label=f'RSI {period}', 
                    color='purple', linewidth=2)
            
            _format_x_axis(ax2, clean_index)
            
        else:
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
        
        # RSI thresholds
        ax2.axhline(y=upper, color='red', linestyle='--', linewidth=1, 
                   label=f'Overbought ({upper})')
        ax2.axhline(y=lower, color='green', linestyle='--', linewidth=1, 
                   label=f'Oversold ({lower})')
        ax2.fill_between(range(len(rsi)), upper, 100, alpha=0.1, color='red')
        ax2.fill_between(range(len(rsi)), 0, lower, alpha=0.1, color='green')
        
        ax2.set_ylim(0, 100)
        ax2.set_xlabel('Date', fontsize=10)
        ax2.set_ylabel('RSI', fontsize=10)
        
        title = f'RSI ({period})'
        if ticker:
            title += f' for {ticker}'
        if kind != 'candle':
            ax2.set_title(title, fontsize=12, fontweight='bold')
        
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error plotting RSI: {e}")
        if 'fig' in locals():
            plt.close(fig)


def plot_moving_averages(data=None, price=None, sma_val=None, ema_val=None, 
                         dema_val=None, tema_val=None, ticker=None, kind='line'):
    """
    Plot moving averages comparison.
    
    Parameters:
    -----------
    data : pandas.DataFrame, optional
        DataFrame with OHLC data (required if kind='candle')
    price : pandas.Series, optional
        Price series (required if kind='line')
    sma_val : pandas.Series, optional
        SMA values
    ema_val : pandas.Series, optional
        EMA values
    dema_val : pandas.Series, optional
        DEMA values
    tema_val : pandas.Series, optional
        TEMA values
    ticker : str, optional
        Ticker symbol
    kind : str, default 'line'
        Chart type: 'line' or 'candle'
        
    Returns:
    --------
    None
        Displays the plot
        
    Example:
    --------
    >>> plot_moving_averages(price=data['Close'], sma_val=data['sma'],
    ...                      ema_val=data['ema'], ticker='GOOG')
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    try:
        if kind == 'candle' and data is not None:
            clean_index = _add_candlesticks(ax, data)
            x = range(len(clean_index))
            
            if sma_val is not None:
                ax.plot(x, sma_val.reindex(clean_index).values, label='SMA', 
                       linestyle='--', linewidth=2, color='blue')
            if ema_val is not None:
                ax.plot(x, ema_val.reindex(clean_index).values, label='EMA', 
                       linestyle='--', linewidth=2, color='orange')
            if dema_val is not None:
                ax.plot(x, dema_val.reindex(clean_index).values, label='DEMA', 
                       linestyle='-.', linewidth=2, color='green')
            if tema_val is not None:
                ax.plot(x, tema_val.reindex(clean_index).values, label='TEMA', 
                       linestyle='-.', linewidth=2, color='purple')
            
            _format_x_axis(ax, clean_index)
            
        else:
            if price is not None:
                ax.plot(price, label='Price', color='black', alpha=0.7, linewidth=2)
            if sma_val is not None:
                ax.plot(sma_val, label='SMA', linestyle='--', linewidth=2, color='blue')
            if ema_val is not None:
                ax.plot(ema_val, label='EMA', linestyle='--', linewidth=2, color='orange')
            if dema_val is not None:
                ax.plot(dema_val, label='DEMA', linestyle='-.', linewidth=2, color='green')
            if tema_val is not None:
                ax.plot(tema_val, label='TEMA', linestyle='-.', linewidth=2, color='purple')
            
            plt.xticks(rotation=45, ha='right')
        
        title = 'Moving Averages Comparison'
        if ticker:
            title += f' for {ticker}'
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Price', fontsize=10)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error plotting moving averages: {e}")
        plt.close(fig)


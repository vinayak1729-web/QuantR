from .indicators import (
    fetch_data,
    Rsi,
    bb_bands,
    macd,
    atr,
    sma,
    ema,
    demma,
    temma,
    RVWAP
)

from .visualize import (
    plot_candlestick,
    plot_macd,
    plot_bollinger,
    plot_rsi,
    plot_moving_averages
)

# Import dashboard functionality
try:
    from .dashboard import launch_dashboard
    __all__ = [
        # Data fetching
        'fetch_data',
        
        # Indicators
        'Rsi',
        'bb_bands',
        'macd',
        'atr',
        'sma',
        'ema',
        'demma',
        'temma',
        'RVWAP',
        
        # Visualization
        'plot_candlestick',
        'plot_macd',
        'plot_bollinger',
        'plot_rsi',
        'plot_moving_averages',
        
        # Dashboard
        'launch_dashboard'
    ]
except ImportError as e:
    # Dashboard dependencies (tkinter, tkcalendar) may not be installed
    print(f"Warning: Dashboard not available. Install with: pip install tkcalendar")
    __all__ = [
        # Data fetching
        'fetch_data',
        
        # Indicators
        'Rsi',
        'bb_bands',
        'macd',
        'atr',
        'sma',
        'ema',
        'demma',
        'temma',
        'RVWAP',
        
        # Visualization
        'plot_candlestick',
        'plot_macd',
        'plot_bollinger',
        'plot_rsi',
        'plot_moving_averages'
    ]

__version__ = '2.0.0'
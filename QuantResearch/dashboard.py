import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
from .indicators import Rsi ,RVWAP , macd , bb_bands , atr ,fetch_data ,sma , temma , demma , ema
# ============================================================================
# PERIOD SETTINGS FOR DIFFERENT TIME FRAMES
# ============================================================================
PERIOD_SETTINGS = {
    "1M":    {"rsi": 14,  "bb": 20,   "macd": (12, 26, 9),   "atr": 14,  "ma": 9,    "rvwap": 20},
    "3M":    {"rsi": 21,  "bb": 25,   "macd": (12, 26, 9),   "atr": 21,  "ma": 20,   "rvwap": 20},
    "6M":    {"rsi": 30,  "bb": 30,   "macd": (12, 26, 9),   "atr": 30,  "ma": 30,   "rvwap": 30},
    "9M":    {"rsi": 40,  "bb": 30,   "macd": (12, 26, 9),   "atr": 30,  "ma": 30,   "rvwap": 30},
    "1Y":    {"rsi": 40,  "bb": 30,   "macd": (12, 26, 9),   "atr": 40,  "ma": 50,   "rvwap": 30},
    "3Y":    {"rsi": 60,  "bb": 50,   "macd": (26, 52, 18),  "atr": 60,  "ma": 100,  "rvwap": 50},
    "5Y":    {"rsi": 70,  "bb": 50,   "macd": (26, 52, 18),  "atr": 70,  "ma": 200,  "rvwap": 70},
}



class QuantDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantResearch Dashboard")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size to 90% of screen
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#1e1e1e')

        # Data storage
        self.data = None
        self.current_ticker = None
        self.current_start = None
        self.current_end = None
        self.current_timeframe = "1M"  # Track selected timeframe
        self.period_config = PERIOD_SETTINGS["1M"]  # Store current period config

        # Indicator states
        self.ma_states = {
            'SMA': tk.BooleanVar(value=False),
            'EMA': tk.BooleanVar(value=False),
            'DEMA': tk.BooleanVar(value=False),
            'TEMA': tk.BooleanVar(value=False)
        }

        self.indicator_states = {
            'MACD': tk.BooleanVar(value=False),
            'ATR': tk.BooleanVar(value=False),
            'RSI': tk.BooleanVar(value=False),
            'Bollinger Bands': tk.BooleanVar(value=False)  # Add Bollinger Bands
        }

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure grid weights
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=4)  # 80% for charts
        main_container.grid_columnconfigure(1, weight=1)  # 20% for control panel

        # Left side - Charts area (75% width)
        left_container = tk.Frame(main_container, bg='#1e1e1e')
        left_container.grid(row=0, column=0, sticky='nsew', padx=(0, 5))

        # Time range selector at the top
        self.time_frame = tk.Frame(left_container, bg='#2d2d2d', height=50, relief=tk.RAISED, borderwidth=2)
        self.time_frame.pack(fill=tk.X, pady=(0, 5))
        self.time_frame.pack_propagate(False)
        self.setup_time_selector()

        # Chart display area
        self.chart_container = tk.Frame(left_container, bg='#2d2d2d', relief=tk.RAISED, borderwidth=2)
        self.chart_container.pack(fill=tk.BOTH, expand=True)

        self.welcome_label = tk.Label(
            self.chart_container,
            text="Welcome to QuantWindow",
            font=('Arial', 24, 'bold'),
            bg='#2d2d2d',
            fg="#eaff00"
        )
        self.welcome_label.pack(expand=True)

        # Right side - PERMANENT Control Panel (25% width)
        self.control_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.RAISED, borderwidth=2)
        self.control_frame.grid(row=0, column=1, sticky='nsew')
        self.setup_control_panel()

    def setup_time_selector(self):
        tk.Label(self.time_frame, text="Time Range:", font=('Arial', 9, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(side=tk.LEFT, padx=(10, 8))

        periods = [('5Y', 1825, '5Y'), ('3Y', 1095, '3Y'), ('1Y', 365, '1Y'), 
                  ('9M', 270, '9M'), ('6M', 180, '6M'), ('3M', 90, '3M'), ('1M', 30, '1M')]

        for label, days, timeframe_key in periods:
            btn = tk.Button(self.time_frame, text=label, width=5,
                           command=lambda d=days, tf=timeframe_key: self.change_time_range(d, tf),
                           bg='#3d3d3d', fg='#ffffff', font=('Arial', 8, 'bold'),
                           relief=tk.RAISED, borderwidth=2, cursor='hand2',
                           activebackground='#00ff88', activeforeground='#1e1e1e')
            btn.pack(side=tk.LEFT, padx=2)

    def setup_control_panel(self):
        # Main frame with fixed structure
        control_main = tk.Frame(self.control_frame, bg='#2d2d2d')
        control_main.pack(fill=tk.BOTH, expand=True)

        # Title (fixed at top)
        title_label = tk.Label(control_main, text="Control Panel", font=('Arial', 14, 'bold'),
                             bg='#2d2d2d', fg='#00ff88')
        title_label.pack(pady=(10, 15), anchor='n')

        # Scrollable content area
        canvas = tk.Canvas(control_main, bg='#2d2d2d', highlightthickness=0)
        scrollbar = tk.Scrollbar(control_main, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')

        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Ticker input
        ticker_frame = tk.Frame(scrollable_frame, bg='#2d2d2d')
        ticker_frame.pack(pady=8, padx=15, fill=tk.X)

        tk.Label(ticker_frame, text="Company Ticker:", font=('Arial', 9, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(anchor=tk.W)

        self.ticker_var = tk.StringVar()
        ticker_entry = tk.Entry(ticker_frame, textvariable=self.ticker_var, font=('Arial', 10),
                              bg='#3d3d3d', fg='#ffffff', insertbackground='#ffffff',
                              relief=tk.SOLID, borderwidth=1)
        ticker_entry.pack(fill=tk.X, pady=(5, 0), ipady=4)
        ticker_entry.bind('<Return>', lambda e: self.fetch_and_plot())

        # Date inputs
        date_frame = tk.Frame(scrollable_frame, bg='#2d2d2d')
        date_frame.pack(pady=8, padx=15, fill=tk.X)

        tk.Label(date_frame, text="Start Date:", font=('Arial', 9, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(anchor=tk.W)

        self.start_date = DateEntry(date_frame, width=23, background='#3d3d3d',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.pack(fill=tk.X, pady=(5, 8))
        self.start_date.set_date(datetime.now() - timedelta(days=30))

        tk.Label(date_frame, text="End Date:", font=('Arial', 9, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(anchor=tk.W)

        self.end_date = DateEntry(date_frame, width=23, background='#3d3d3d',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.pack(fill=tk.X, pady=(5, 0))

        # Fetch button
        fetch_btn = tk.Button(scrollable_frame, text="📊 Fetch Data", command=self.fetch_and_plot,
                             bg='#00ff88', fg='#1e1e1e', font=('Arial', 10, 'bold'),
                             relief=tk.RAISED, borderwidth=3, cursor='hand2',
                             activebackground='#00dd77')
        fetch_btn.pack(pady=12, padx=15, fill=tk.X, ipady=5)

        # Separator
        tk.Frame(scrollable_frame, height=2, bg='#00ff88').pack(fill=tk.X, padx=15, pady=10)

        # Moving Averages section
        ma_label = tk.Label(scrollable_frame, text="📈 Moving Averages", font=('Arial', 11, 'bold'),
                          bg='#2d2d2d', fg='#00ff88')
        ma_label.pack(pady=(8, 8))

        ma_frame = tk.Frame(scrollable_frame, bg='#2d2d2d')
        ma_frame.pack(pady=5, padx=15, fill=tk.X)

        for ma_name in ['SMA', 'EMA', 'DEMA', 'TEMA']:
            self.create_toggle_button(ma_frame, ma_name, self.ma_states[ma_name], is_ma=True)

        # Separator
        tk.Frame(scrollable_frame, height=2, bg='#00ff88').pack(fill=tk.X, padx=15, pady=10)

        # Technical Indicators section
        ind_label = tk.Label(scrollable_frame, text="📊 Technical Indicators", font=('Arial', 11, 'bold'),
                           bg='#2d2d2d', fg='#00ff88')
        ind_label.pack(pady=(8, 8))

        ind_frame = tk.Frame(scrollable_frame, bg='#2d2d2d')
        ind_frame.pack(pady=5, padx=15, fill=tk.X)

        for ind_name in ['RSI', 'MACD', 'ATR', 'Bollinger Bands']:
            self.create_toggle_button(ind_frame, ind_name, self.indicator_states[ind_name], is_ma=False)

        # Add some bottom padding
        tk.Frame(scrollable_frame, height=20, bg='#2d2d2d').pack()

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_toggle_button(self, parent, name, var, is_ma=True):
        frame = tk.Frame(parent, bg='#2d2d2d')
        frame.pack(pady=6, fill=tk.X)

        label = tk.Label(frame, text=name, font=('Arial', 9, 'bold'),
                        bg='#2d2d2d', fg='#ffffff', width=12, anchor=tk.W)
        label.pack(side=tk.LEFT, padx=(0, 8))

        btn = tk.Button(frame, text="OFF", width=8,
                       command=lambda: self.toggle_indicator(name, var, btn, is_ma),
                       bg='#ff4444', fg='white', font=('Arial', 8, 'bold'),
                       relief=tk.RAISED, borderwidth=2, cursor='hand2',
                       activebackground='#ff6666')
        btn.pack(side=tk.RIGHT)
        btn.var = var

    def toggle_indicator(self, name, var, btn, is_ma):
        var.set(not var.get())
        if var.get():
            btn.config(text="ON", bg='#00ff88', fg='#1e1e1e', activebackground='#00dd77')
        else:
            btn.config(text="OFF", bg='#ff4444', fg='white', activebackground='#ff6666')

        if self.data is not None:
            self.update_plot()

    def change_time_range(self, days, timeframe_key):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        self.start_date.set_date(start_date)
        self.end_date.set_date(end_date)
        
        # Update timeframe and period config
        self.current_timeframe = timeframe_key
        self.period_config = PERIOD_SETTINGS.get(timeframe_key, PERIOD_SETTINGS["1M"])
        
        if self.current_ticker:
            self.fetch_and_plot()

    def fetch_and_plot(self):
        ticker = self.ticker_var.get().strip().upper()
        if not ticker:
            messagebox.showwarning("Input Error", "Please enter a ticker symbol")
            return

        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end = self.end_date.get_date().strftime('%Y-%m-%d')

        try:
            print(f"Fetching data for {ticker} from {start} to {end}...")

            # Remove welcome screen on first action
            for widget in self.chart_container.winfo_children():
                widget.destroy()

            self.welcome_label = None

            loading_label = tk.Label(self.chart_container, text=f"Loading {ticker} data...",
                                   font=('Arial', 16, 'bold'), bg='#2d2d2d', fg='#00ff88')
            loading_label.pack(expand=True)

            self.root.update()

            # Fetch data
            self.data = fetch_data(ticker, start, end)

            if self.data is None or self.data.empty:
                messagebox.showerror("Data Error", f"No data found for {ticker}")
                loading_label.destroy()
                return

            self.current_ticker = ticker
            self.current_start = start
            self.current_end = end

            print(f"Data fetched successfully! Shape: {self.data.shape}")
            print(f"Columns: {self.data.columns.tolist()}")
            print(f"Date range: {self.data.index[0]} to {self.data.index[-1]}")
            print(f"Current Period Config: {self.period_config}")

            self.update_plot()

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching data: {str(e)}")
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()

    def update_plot(self):
        if self.data is None or self.data.empty:
            return

        # Clear existing charts
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Count active bottom indicators
        active_indicators = [name for name, var in self.indicator_states.items() 
                           if var.get() and name != 'Bollinger Bands']

        num_indicators = len(active_indicators)

        # Create figure with dynamic subplot layout
        if num_indicators == 0:
            fig = Figure(figsize=(12, 7), facecolor='#2d2d2d', dpi=100)
            gs = fig.add_gridspec(1, 1)
            axes = [fig.add_subplot(gs[0, 0])]

        elif num_indicators == 1:
            fig = Figure(figsize=(12, 7), facecolor='#2d2d2d', dpi=100)
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
            axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0])]

        elif num_indicators == 2:
            fig = Figure(figsize=(12, 7), facecolor='#2d2d2d', dpi=100)
            gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], hspace=0.3, wspace=0.3)
            axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]

        else:  # 3 or more indicators
            fig = Figure(figsize=(12, 7), facecolor='#2d2d2d', dpi=100)
            gs = fig.add_gridspec(2, 3, height_ratios=[3, 1], hspace=0.3, wspace=0.3)
            axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]),
                   fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[1, 2])]

        # Main price chart with candlesticks
        ax_main = axes[0]

        self.plot_candlesticks(ax_main)

        # Add Bollinger Bands to main chart if enabled
        if self.indicator_states['Bollinger Bands'].get():
            self.add_bollinger_bands(ax_main)

        # Add moving averages to main chart
        self.add_moving_averages(ax_main)

        ax_main.set_title(f'{self.current_ticker} - Price Chart | Period Config: {self.period_config}',
                        color='#ffffff', fontsize=12, fontweight='bold', pad=10)
        ax_main.set_ylabel('Price ($)', color='#ffffff', fontsize=9)
        ax_main.tick_params(colors='#ffffff', labelsize=7)
        ax_main.grid(True, alpha=0.2, color='#ffffff', linestyle='--')

        # Only show legend if there are items to display
        handles, labels = ax_main.get_legend_handles_labels()
        if handles:
            ax_main.legend(loc='upper left', facecolor='#2d2d2d',
                         edgecolor='#00ff88', labelcolor='#ffffff', fontsize=7)
        ax_main.set_facecolor('#1e1e1e')

        # Plot active indicators
        for idx, ind_name in enumerate(active_indicators):
            ax_ind = axes[idx + 1]
            ax_ind.set_facecolor('#1e1e1e')

            if ind_name == 'RSI':
                self.plot_rsi_indicator(ax_ind)
            elif ind_name == 'MACD':
                self.plot_macd_indicator(ax_ind)
            elif ind_name == 'ATR':
                self.plot_atr_indicator(ax_ind)

        fig.tight_layout(pad=1.5)

        # Embed figure
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_candlesticks(self, ax):
        """Plot candlestick chart"""
        data_clean = self.data[['Open', 'High', 'Low', 'Close']].dropna()

        if len(data_clean) == 0:
            return

        open_prices = data_clean['Open'].values
        close_prices = data_clean['Close'].values
        high_prices = data_clean['High'].values
        low_prices = data_clean['Low'].values

        x = range(len(open_prices))
        width = 0.6

        for i in x:
            color = "#00ff00" if close_prices[i] >= open_prices[i] else "#ff0000"

            # Draw wick
            ax.plot([i, i], [low_prices[i], high_prices[i]],
                   color='#ffffff', linewidth=0.8, alpha=0.8)

            # Draw body
            body_height = abs(close_prices[i] - open_prices[i])
            body_bottom = min(open_prices[i], close_prices[i])

            rect = plt.Rectangle((i - width/2, body_bottom), width, body_height,
                               facecolor=color, edgecolor='#ffffff',
                               linewidth=0.5, alpha=0.9)
            ax.add_patch(rect)

        # Format x-axis with dates
        step = max(1, len(data_clean) // 10)
        tick_positions = list(range(0, len(data_clean), step))
        tick_labels = [data_clean.index[i].strftime('%Y-%m-%d') for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    def add_bollinger_bands(self, ax):
        """Add Bollinger Bands to the price chart"""
        bb_period = self.period_config.get('bb', 20)
        bb_upper, bb_mid, bb_lower = bb_bands(self.data['Close'], period=bb_period)

        x = range(len(self.data))

        ax.plot(x, bb_upper.values, color='#FFD700', label=f'BB Upper ({bb_period})',
               linestyle='--', linewidth=1.5, alpha=0.7)
        ax.plot(x, bb_mid.values, color='#00FFFF', label=f'BB Middle ({bb_period})',
               linestyle='-.', linewidth=1, alpha=0.6)
        ax.plot(x, bb_lower.values, color='#FFD700', label=f'BB Lower ({bb_period})',
               linestyle='--', linewidth=1.5, alpha=0.7)

        # Fill between upper and lower bands
        ax.fill_between(x, bb_upper.values, bb_lower.values, alpha=0.1, color='#FFD700')

    def add_moving_averages(self, ax):
        """Add moving averages to the chart"""
        x = range(len(self.data))
        ma_period = self.period_config.get('ma', 9)

        if self.ma_states['SMA'].get():
            sma_val = sma(self.data['Close'], period=ma_period)
            ax.plot(x, sma_val.values, label=f'SMA({ma_period})',
                   color='#00aaff', linewidth=1.5, linestyle='--', alpha=0.8)

        if self.ma_states['EMA'].get():
            ema_val = ema(self.data['Close'], period=ma_period)
            ax.plot(x, ema_val.values, label=f'EMA({ma_period})',
                   color='#ff9500', linewidth=1.5, linestyle='--', alpha=0.8)

        if self.ma_states['DEMA'].get():
            dema_val = demma(self.data['Close'], period=ma_period)
            ax.plot(x, dema_val.values, label=f'DEMA({ma_period})',
                   color='#af52de', linewidth=1.5, linestyle='-.', alpha=0.8)

        if self.ma_states['TEMA'].get():
            tema_val = temma(self.data['Close'], period=ma_period)
            ax.plot(x, tema_val.values, label=f'TEMA({ma_period})',
                   color='#ffcc00', linewidth=1.5, linestyle='-.', alpha=0.8)

    def plot_rsi_indicator(self, ax):
        """Plot RSI indicator"""
        rsi_period = self.period_config.get('rsi', 14)
        rsi_val = Rsi(self.data['Close'], period=rsi_period)

        x = range(len(rsi_val))

        ax.plot(x, rsi_val.values, color='#af52de', linewidth=2)
        ax.axhline(y=70, color='#ff4444', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=30, color='#00ff88', linestyle='--', linewidth=1.5, alpha=0.7)

        ax.fill_between(x, 70, 100, alpha=0.1, color='#ff4444')
        ax.fill_between(x, 0, 30, alpha=0.1, color='#00ff88')

        ax.set_ylim(0, 100)
        ax.set_title(f'RSI ({rsi_period})', color='#ffffff', fontsize=10, fontweight='bold')
        ax.set_ylabel('RSI', color='#ffffff', fontsize=8)
        ax.tick_params(colors='#ffffff', labelsize=6)
        ax.grid(True, alpha=0.2, color='#ffffff', linestyle='--')

        # Format x-axis
        step = max(1, len(self.data) // 5)
        tick_positions = list(range(0, len(self.data), step))
        tick_labels = [self.data.index[i].strftime('%m-%d') for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    def plot_macd_indicator(self, ax):
        """Plot MACD indicator"""
        macd_config = self.period_config.get('macd', (12, 26, 9))
        short_period, long_period, signal_period = macd_config

        macd_line, signal_line, hist = macd(self.data['Close'], 
                                           short_period=short_period,
                                           long_period=long_period,
                                           signal_period=signal_period)

        x = range(len(macd_line))

        ax.plot(x, macd_line.values, label='MACD', color='#00aaff', linewidth=1.5)
        ax.plot(x, signal_line.values, label='Signal', color='#ff9500', linewidth=1.5)

        colors = ['#00ff88' if val >= 0 else '#ff4444' for val in hist.values]
        ax.bar(x, hist.values, color=colors, alpha=0.6, width=0.8)

        ax.axhline(y=0, color='#ffffff', linestyle='-', linewidth=0.8, alpha=0.5)

        ax.set_title(f'MACD ({short_period}/{long_period}/{signal_period})', 
                    color='#ffffff', fontsize=10, fontweight='bold')
        ax.set_ylabel('Value', color='#ffffff', fontsize=8)
        ax.tick_params(colors='#ffffff', labelsize=6)
        ax.grid(True, alpha=0.2, color='#ffffff', linestyle='--')
        ax.legend(loc='upper left', fontsize=6, facecolor='#2d2d2d',
                 edgecolor='#00ff88', labelcolor='#ffffff')

        # Format x-axis
        step = max(1, len(self.data) // 5)
        tick_positions = list(range(0, len(self.data), step))
        tick_labels = [self.data.index[i].strftime('%m-%d') for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    def plot_atr_indicator(self, ax):
        """Plot ATR indicator"""
        atr_period = self.period_config.get('atr', 14)
        atr_val = atr(self.data, period=atr_period)

        x = range(len(atr_val))

        ax.plot(x, atr_val.values, color='#ff9500', linewidth=2)
        ax.fill_between(x, 0, atr_val.values, alpha=0.2, color='#ff9500')

        ax.set_title(f'ATR ({atr_period})', color='#ffffff', fontsize=10, fontweight='bold')
        ax.set_ylabel('ATR', color='#ffffff', fontsize=8)
        ax.tick_params(colors='#ffffff', labelsize=6)
        ax.grid(True, alpha=0.2, color='#ffffff', linestyle='--')

        # Format x-axis
        step = max(1, len(self.data) // 5)
        tick_positions = list(range(0, len(self.data), step))
        tick_labels = [self.data.index[i].strftime('%m-%d') for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')

def launch_dashboard():
    """Main function to launch the QuantResearch Dashboard"""
    root = tk.Tk()
    app = QuantDashboard(root)
    root.mainloop()

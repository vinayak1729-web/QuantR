import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import threading
import platform
import json, os, math

from .indicators import (
    Rsi, RVWAP, macd, bb_bands, atr, fetch_data,
    sma, temma, demma, ema,
    stochastic, williams_r, obv, parabolic_sar,
    adx, ichimoku, pivot_points, fibonacci_levels, slope
)



# ═══════════════════════════════════════════════════════════════════
# MANGO PALETTE
# ═══════════════════════════════════════════════════════════════════
C = {
    'bg':         '#0a0e14',
    'bg2':        '#111820',
    'bg3':        '#182030',
    'border':     '#1e3048',
    'accent':     '#ffb347',
    'accent2':    '#ffd580',
    'green':      '#00e676',
    'red':        '#ff1744',
    'blue':       '#29b6f6',
    'purple':     '#ce93d8',
    'white':      '#e8edf3',
    'muted':      '#607080',
    'gold':       '#ffc107',
    'cyan':       '#00e5ff',
    'tab_sel':    '#ffb347',
    'tab_bg':     '#111820',
    'teal':       '#1de9b6',
    'orange':     '#ff6d00',
}

# ═══════════════════════════════════════════════════════════════════
# KNOWN INDIAN NSE TICKERS  (auto-appends .NS)
# ═══════════════════════════════════════════════════════════════════
NSE_TICKERS = {
    'RELIANCE','TCS','INFY','HDFCBANK','ICICIBANK','SBIN','WIPRO',
    'HINDUNILVR','BAJFINANCE','KOTAKBANK','LT','AXISBANK','ASIANPAINT',
    'MARUTI','SUNPHARMA','TATAMOTORS','TATASTEEL','TECHM','NESTLEIND',
    'POWERGRID','NTPC','ONGC','COALINDIA','GRASIM','BPCL','INDUSINDBK',
    'TITAN','BAJAJ-AUTO','HEROMOTOCO','DRREDDY','CIPLA','EICHERMOT',
    'BRITANNIA','DIVISLAB','UPL','ADANIPORTS','ADANIENT','JSWSTEEL',
    'HINDALCO','VEDL','HCLTECH','ULTRACEMCO','SHREECEM','TATACONSUM',
    'APOLLOHOSP','BAJAJFINSV','HAVELLS','PIDILITIND','SIEMENS','ABB',
    'MUTHOOTFIN','CHOLAFIN','BHARTIARTL','ZOMATO','PAYTM','NYKAA',
    'DMART','IRCTC','POLYCAB','TRENT','DIXON','LTIM','PERSISTENT',
    'COFORGE','MPHASIS','OFSS','KPIT','ZYDUSLIFE','MANKIND','TORNTPHARM',
    'LUPIN','AUROPHARMA','BIOCON','ALKEM','ABBOTINDIA','GLAXO',
    'HDFCLIFE','SBILIFE','ICICIGI','MAXHEALTH','FORTIS',
    'BANKBARODA','PNB','CANBK','UNIONBANK','FEDERALBNK','BANDHANBNK',
    'IDFCFIRSTB','AUBANK','RBLBANK','EQUITASBNK',
    'RECLTD','PFC','IRFC','HUDCO',
    'HAL','BEL','BHEL','RVNL','IRCON','NBCC',
    'SAIL','NMDC','MOIL','NATIONALUM',
    'ITC','GODREJCP','DABUR','EMAMILTD','COLPAL','MARICO',
    'VOLTAS','BLUESTARCO','WHIRLPOOL','CROMPTON','HAVELLS',
    'M&M','ASHOKLEY','TVSMOTOR','BAJAJ-AUTO','MOTHERSON','SONA BLW',
    'NIFTY50','NIFTYBANK','MIDCAP','SMALLCAP',
}

BSE_TICKERS = {
    'SENSEX','BSESN',
}

CRYPTO_SUFFIXES = {'-USD','-INR','-USDT','-BTC','-ETH'}

MARKET_BENCHMARKS = {
    'NSE':    '^NSEI',
    'BSE':    '^BSESN',
    'US':     'SPY',
    'Crypto': 'BTC-USD',
}

# ═══════════════════════════════════════════════════════════════════
# PERIOD SETTINGS
# ═══════════════════════════════════════════════════════════════════
PERIOD_SETTINGS = {
    "1M": {"rsi":14, "bb":20, "macd":(12,26,9), "atr":14, "ma":9,   "rvwap":20,
           "stoch":(14,3), "williams":14, "adx":14, "slope":14},
    "3M": {"rsi":21, "bb":25, "macd":(12,26,9), "atr":21, "ma":20,  "rvwap":20,
           "stoch":(14,3), "williams":14, "adx":14, "slope":20},
    "6M": {"rsi":30, "bb":30, "macd":(12,26,9), "atr":30, "ma":30,  "rvwap":30,
           "stoch":(21,5), "williams":21, "adx":21, "slope":30},
    "9M": {"rsi":40, "bb":30, "macd":(12,26,9), "atr":30, "ma":30,  "rvwap":30,
           "stoch":(21,5), "williams":21, "adx":21, "slope":30},
    "1Y": {"rsi":40, "bb":30, "macd":(12,26,9), "atr":40, "ma":50,  "rvwap":30,
           "stoch":(21,5), "williams":21, "adx":21, "slope":40},
    "3Y": {"rsi":60, "bb":50, "macd":(26,52,18),"atr":60, "ma":100, "rvwap":50,
           "stoch":(21,7), "williams":30, "adx":30, "slope":60},
    "5Y": {"rsi":70, "bb":50, "macd":(26,52,18),"atr":70, "ma":200, "rvwap":70,
           "stoch":(21,7), "williams":30, "adx":30, "slope":70},
}

DEFAULT_LIVE_TICKERS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS",
                         "AAPL","MSFT","BTC-USD","ETH-USD"]

WATCHLIST_FILE = os.path.join(os.path.expanduser("~"), ".quant_watchlist.json")

# ═══════════════════════════════════════════════════════════════════
# TICKER NORMALIZATION  ← THE CORE FIX FOR INDIAN TICKERS
# ═══════════════════════════════════════════════════════════════════
def normalize_ticker(raw: str, market: str = "Auto") -> tuple:
    """
    Returns (yf_ticker, currency_symbol, exchange_label, display_name)

    market: "Auto" | "NSE" | "BSE" | "US" | "Crypto"

    Rules:
      - Already has .NS  → NSE / ₹
      - Already has .BO  → BSE / ₹
      - Already has -USD / -INR → Crypto
      - market="NSE"     → append .NS  → ₹
      - market="BSE"     → append .BO  → ₹
      - market="US"      → no suffix   → $
      - market="Auto"    → check NSE_TICKERS set, else US
      - Indices (^NSEI, ^BSESN) → ₹
      - SPY, QQQ, etc.   → $
    """
    t = raw.strip().upper()
    display = t  # user-friendly name

    # ── Already-suffixed or index ──────────────────────────────
    if t.startswith('^'):
        if t in ('^NSEI', '^BSESN', '^NSEBANK', '^CNXIT'):
            return t, '₹', 'IDX', t
        return t, '$', 'IDX', t

    if t.endswith('.NS'):
        return t, '₹', 'NSE', t.replace('.NS', '')
    if t.endswith('.BO'):
        return t, '₹', 'BSE', t.replace('.BO', '')

    # ── Crypto ────────────────────────────────────────────────
    for sfx in CRYPTO_SUFFIXES:
        if t.endswith(sfx):
            ccy = '₹' if sfx == '-INR' else '$'
            return t, ccy, 'Crypto', t

    # ── Explicit market override ───────────────────────────────
    if market == 'NSE':
        return f"{t}.NS", '₹', 'NSE', t
    if market == 'BSE':
        return f"{t}.BO", '₹', 'BSE', t
    if market == 'US':
        return t, '$', 'US', t
    if market == 'Crypto':
        return f"{t}-USD", '$', 'Crypto', t

    # ── Auto-detect ────────────────────────────────────────────
    base = t.replace('-', '').replace('&', '')
    if t in NSE_TICKERS or base in NSE_TICKERS:
        return f"{t}.NS", '₹', 'NSE', t

    # Default → US market
    return t, '$', 'US', t


def fmt_price(price, currency: str = '$', decimals: int = 2) -> str:
    """Format price with correct currency symbol."""
    if price is None or (isinstance(price, float) and math.isnan(price)):
        return "—"
    sym = currency
    if abs(price) >= 1_000_000:
        return f"{sym}{price/1e6:.2f}M"
    if abs(price) >= 1_000:
        return f"{sym}{price:,.{decimals}f}"
    return f"{sym}{price:.{decimals}f}"


def fmt_vol(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    if v >= 1e7:
        return f"{v/1e7:.2f}Cr"   # Indian crore
    if v >= 1e5:
        return f"{v/1e5:.2f}L"    # Indian lakh
    if v >= 1e6:
        return f"{v/1e6:.2f}M"
    if v >= 1e3:
        return f"{v/1e3:.1f}K"
    return str(int(v))


# ═══════════════════════════════════════════════════════════════════
# QUANT METRICS
# ═══════════════════════════════════════════════════════════════════
def compute_quant_metrics(prices: pd.Series, benchmark_prices: pd.Series = None,
                           risk_free: float = 0.065) -> dict:
    """
    Compute quant-grade performance metrics.
    risk_free: annual rate (default 6.5% – Indian repo rate approximation)
    """
    ret = prices.pct_change().dropna()
    if len(ret) < 5:
        return {}

    # Annualisation factor (trading days ≈ 252)
    ann = 252
    rf_daily = (1 + risk_free) ** (1/ann) - 1

    total_ret   = (prices.iloc[-1] / prices.iloc[0]) - 1
    cagr        = (1 + total_ret) ** (ann / len(prices)) - 1 if len(prices) > 1 else 0
    vol         = ret.std() * np.sqrt(ann)
    sharpe      = (ret.mean() - rf_daily) / ret.std() * np.sqrt(ann) if ret.std() > 0 else 0

    # Sortino
    down_ret    = ret[ret < rf_daily]
    down_std    = down_ret.std() * np.sqrt(ann) if len(down_ret) > 0 else 1e-9
    sortino     = (ret.mean() - rf_daily) / (down_ret.std() if len(down_ret) > 0 else 1e-9) * np.sqrt(ann)

    # Max Drawdown
    cum         = (1 + ret).cumprod()
    roll_max    = cum.cummax()
    dd          = (cum - roll_max) / roll_max
    max_dd      = dd.min()
    calmar      = cagr / abs(max_dd) if max_dd != 0 else 0

    # VaR / CVaR (95%)
    var_95      = np.percentile(ret, 5)
    cvar_95     = ret[ret <= var_95].mean()

    # Win rate
    win_rate    = (ret > 0).mean()
    avg_win     = ret[ret > 0].mean() if (ret > 0).any() else 0
    avg_loss    = ret[ret < 0].mean() if (ret < 0).any() else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

    metrics = {
        'Total Return':   f"{total_ret*100:+.2f}%",
        'CAGR':           f"{cagr*100:.2f}%",
        'Volatility':     f"{vol*100:.2f}%",
        'Sharpe':         f"{sharpe:.2f}",
        'Sortino':        f"{sortino:.2f}",
        'Max Drawdown':   f"{max_dd*100:.2f}%",
        'Calmar':         f"{calmar:.2f}",
        'VaR 95%':        f"{var_95*100:.2f}%",
        'CVaR 95%':       f"{cvar_95*100:.2f}%",
        'Win Rate':       f"{win_rate*100:.1f}%",
        'Profit Factor':  f"{profit_factor:.2f}",
        'Bars':           str(len(prices)),
    }

    # Beta / Alpha vs benchmark
    if benchmark_prices is not None and len(benchmark_prices) > 5:
        bret = benchmark_prices.pct_change().dropna()
        # Align
        common = ret.index.intersection(bret.index)
        if len(common) > 5:
            r_a = ret.loc[common]
            r_b = bret.loc[common]
            cov  = np.cov(r_a, r_b)
            beta = cov[0,1] / cov[1,1] if cov[1,1] != 0 else 0
            alpha_daily = r_a.mean() - (rf_daily + beta * (r_b.mean() - rf_daily))
            alpha_ann   = alpha_daily * ann
            corr        = r_a.corr(r_b)
            metrics['Beta']        = f"{beta:.2f}"
            metrics['Alpha (ann)'] = f"{alpha_ann*100:+.2f}%"
            metrics['Correlation'] = f"{corr:.2f}"

    return metrics


# ═══════════════════════════════════════════════════════════════════
# SOUND HELPER
# ═══════════════════════════════════════════════════════════════════
def beep():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(880, 200)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════
# LIVE DATA STORE
# ═══════════════════════════════════════════════════════════════════
class LiveDataStore:
    def __init__(self):
        self._lock  = threading.Lock()
        self._ticks: dict = {}
        self._prev_prices: dict = {}

    def add_tick(self, ticker: str, timestamp_ms, price: float):
        ts = pd.to_datetime(int(timestamp_ms), unit='ms')
        with self._lock:
            prev = self._ticks.get(ticker, [{}])
            if prev:
                self._prev_prices[ticker] = float(prev[-1].get("price", price))
            if ticker not in self._ticks:
                self._ticks[ticker] = []
            self._ticks[ticker].append({"time": ts, "price": price})
            if len(self._ticks[ticker]) > 3000:
                self._ticks[ticker] = self._ticks[ticker][-3000:]

    def get_ohlc(self, ticker: str, resample: str = "1min") -> pd.DataFrame:
        with self._lock:
            ticks = list(self._ticks.get(ticker, []))
        if not ticks:
            return pd.DataFrame()
        df = pd.DataFrame(ticks).set_index("time")
        return df["price"].resample(resample).ohlc().dropna()

    def get_latest_price(self, ticker: str):
        with self._lock:
            ticks = self._ticks.get(ticker, [])
            return float(ticks[-1]["price"]) if ticks else None

    def get_prev_price(self, ticker: str):
        with self._lock:
            return self._prev_prices.get(ticker)

    def get_tick_log(self, ticker: str, n: int = 50):
        with self._lock:
            return list(self._ticks.get(ticker, []))[-n:]

    def tickers(self):
        with self._lock:
            return list(self._ticks.keys())


# ═══════════════════════════════════════════════════════════════════
# WEBSOCKET MANAGER
# ═══════════════════════════════════════════════════════════════════
class WebSocketManager:
    def __init__(self, store: LiveDataStore, tickers: list):
        self.store   = store
        self.tickers = tickers
        self._thread = None
        self._ws     = None
        self.status_var = None

    def _on_message(self, message: dict):
        ticker = message.get("id", "")
        price  = message.get("price")
        ts     = message.get("time")
        if ticker and price is not None and ts is not None:
            self.store.add_tick(ticker, ts, float(price))

    def _run(self):
        self._set_status("🔴  Connecting…")
        try:
            with yf.WebSocket() as ws:
                self._ws = ws
                ws.subscribe(self.tickers)
                self._set_status(f"🟢  Live — {len(self.tickers)} tickers")
                ws.listen(self._on_message)
        except Exception as exc:
            self._set_status(f"⚠️  {exc}")

    def _set_status(self, text: str):
        if self.status_var:
            try: self.status_var.set(text)
            except Exception: pass

    def start(self, tickers: list = None):
        if tickers:
            self.tickers = tickers
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def reconnect(self, tickers: list = None):
        if tickers:
            self.tickers = tickers
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()


# ═══════════════════════════════════════════════════════════════════
# STYLE HELPERS
# ═══════════════════════════════════════════════════════════════════
def style_ax(ax, title="", ylabel="", fontsize=9):
    ax.set_facecolor(C['bg'])
    ax.tick_params(colors=C['muted'], labelsize=6)
    ax.grid(True, alpha=0.10, color='#2a3f55', linestyle='--')
    for spine in ax.spines.values():
        spine.set_color(C['border'])
    if title:
        ax.set_title(title, color=C['white'], fontsize=fontsize, fontweight='bold', pad=5)
    if ylabel:
        ax.set_ylabel(ylabel, color=C['muted'], fontsize=7)


def set_x_date_ticks(ax, index, n=8, fmt='%Y-%m-%d'):
    step = max(1, len(index) // n)
    ticks = list(range(0, len(index), step))
    ax.set_xticks(ticks)
    if hasattr(index[0], 'strftime'):
        ax.set_xticklabels([index[i].strftime(fmt) for i in ticks],
                           rotation=45, ha='right', color=C['muted'], fontsize=6)
    else:
        ax.set_xticklabels(ticks, rotation=45, ha='right', color=C['muted'], fontsize=6)


def draw_candles(ax, data_df, width=0.6):
    d = data_df[['Open','High','Low','Close']].dropna()
    for i, row in enumerate(d.itertuples()):
        bull  = row.Close >= row.Open
        color = C['green'] if bull else C['red']
        ax.plot([i, i], [row.Low, row.High], color=C['muted'], linewidth=0.7, alpha=0.8)
        body_h = abs(row.Close - row.Open) or (row.High - row.Low) * 0.01
        ax.add_patch(plt.Rectangle(
            (i - width/2, min(row.Open, row.Close)), width, body_h,
            facecolor=color, edgecolor='none', alpha=0.92))
    ax.set_xlim(-0.5, len(d) - 0.5)

    # ── Tight Y-axis: only show actual price range with 3% padding ──
    lo = d['Low'].min()
    hi = d['High'].max()
    pad = (hi - lo) * 0.03
    ax.set_ylim(lo - pad, hi + pad * 3)   # extra top room for legend

    return d.index


def compute_volume_profile(data_df, n_bins=40):
    """
    Returns (price_levels, volumes) for a horizontal Volume Profile.
    Bins the entire data range into n_bins price buckets and sums volume per bucket.
    """
    lo  = data_df['Low'].min()
    hi  = data_df['High'].max()
    bins = np.linspace(lo, hi, n_bins + 1)
    mid  = (bins[:-1] + bins[1:]) / 2
    vols = np.zeros(n_bins)

    for row in data_df.itertuples():
        # Distribute bar's volume proportionally across the bins it spans
        bar_lo, bar_hi = row.Low, row.High
        bar_range = bar_hi - bar_lo or 1e-9
        for j in range(n_bins):
            overlap = min(bins[j+1], bar_hi) - max(bins[j], bar_lo)
            if overlap > 0:
                vols[j] += row.Volume * overlap / bar_range

    return mid, vols


def draw_volume_profile(ax, data_df, fib_start_idx=None, fib_end_idx=None,
                        n_bins=40, poc_color='#ffc107', vah_color='#00e676', val_color='#ff1744'):
    """
    Draw a horizontal Volume-at-Price histogram on the RIGHT side of ax.
    Highlights POC (Point of Control), VAH/VAL (70% value area).
    If fib_start_idx/fib_end_idx provided, restrict to that slice.
    """
    d = data_df.copy()
    if fib_start_idx is not None and fib_end_idx is not None:
        d = d.iloc[fib_start_idx:fib_end_idx+1]
    if d.empty or 'Volume' not in d.columns:
        return

    mid, vols = compute_volume_profile(d, n_bins=n_bins)
    if vols.sum() == 0:
        return

    # Normalise to 15% of chart x-width
    x_max = ax.get_xlim()[1]
    norm_vols = vols / vols.max() * (x_max * 0.15)

    poc_idx = int(np.argmax(vols))

    # Value Area: 70% of total volume around POC
    total = vols.sum()
    sorted_idx = np.argsort(vols)[::-1]
    cumvol = 0.0
    va_set = set()
    for si in sorted_idx:
        cumvol += vols[si]
        va_set.add(si)
        if cumvol >= total * 0.70:
            break
    va_indices = sorted(va_set)
    vah_price  = mid[max(va_indices)] if va_indices else mid[poc_idx]
    val_price  = mid[min(va_indices)] if va_indices else mid[poc_idx]

    # Draw horizontal bars from the right edge
    bar_h = (mid[1] - mid[0]) * 0.85 if len(mid) > 1 else 1
    for j in range(n_bins):
        x0 = x_max - norm_vols[j]
        color = poc_color if j == poc_idx else (
            '#1a3a2a' if j in va_set else '#1a1f2b')
        ax.barh(mid[j], norm_vols[j], height=bar_h, left=x0,
                color=color, alpha=0.75, zorder=2)

    # POC line
    ax.axhline(mid[poc_idx], color=poc_color, lw=1.2, linestyle='-', alpha=0.9, zorder=3,
               label=f'POC {mid[poc_idx]:,.0f}')
    # VAH / VAL
    ax.axhline(vah_price, color=vah_color, lw=0.9, linestyle='--', alpha=0.8, zorder=3,
               label=f'VAH {vah_price:,.0f}')
    ax.axhline(val_price, color=val_color, lw=0.9, linestyle='--', alpha=0.8, zorder=3,
               label=f'VAL {val_price:,.0f}')

    # Labels at right edge
    ax.text(x_max * 0.985, mid[poc_idx], f'POC', color=poc_color,
            fontsize=6, va='center', ha='right', fontfamily='Consolas', zorder=4)
    ax.text(x_max * 0.985, vah_price,  f'VAH', color=vah_color,
            fontsize=6, va='center', ha='right', fontfamily='Consolas', zorder=4)
    ax.text(x_max * 0.985, val_price,  f'VAL', color=val_color,
            fontsize=6, va='center', ha='right', fontfamily='Consolas', zorder=4)


# ═══════════════════════════════════════════════════════════════════
# PERIOD SPINBOX WIDGET
# ═══════════════════════════════════════════════════════════════════
class PeriodSpinbox(tk.Frame):
    def __init__(self, parent, label, default, mn=2, mx=500, width=5, **kw):
        super().__init__(parent, bg=C['bg3'], **kw)
        tk.Label(self, text=label, font=('Consolas', 8),
                 bg=C['bg3'], fg=C['muted']).pack(side=tk.LEFT, padx=(0,2))
        self.var = tk.IntVar(value=default)
        tk.Spinbox(self, from_=mn, to=mx, textvariable=self.var,
                   width=width, font=('Consolas', 8),
                   bg=C['bg2'], fg=C['accent'], insertbackground=C['accent'],
                   buttonbackground=C['bg3'], relief=tk.FLAT,
                   disabledforeground=C['muted']).pack(side=tk.LEFT)

    def get(self):
        return self.var.get()


# ═══════════════════════════════════════════════════════════════════
# METRICS CARD WIDGET
# ═══════════════════════════════════════════════════════════════════
class MetricsCard(tk.Frame):
    """Compact quant-metrics display panel."""
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C['bg2'], **kw)
        self._labels = {}
        self._build()

    def _build(self):
        tk.Label(self, text="QUANT METRICS", font=('Consolas',9,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(anchor='w', padx=8, pady=(6,2))
        tk.Frame(self, height=1, bg=C['border']).pack(fill=tk.X, padx=6, pady=2)

        self._grid = tk.Frame(self, bg=C['bg2'])
        self._grid.pack(fill=tk.X, padx=6, pady=4)

    def update(self, metrics: dict):
        for w in self._grid.winfo_children():
            w.destroy()
        self._labels = {}

        COLOR_MAP = {
            'Total Return': lambda v: C['green'] if '+' in v else C['red'],
            'CAGR':         lambda v: C['green'] if float(v.rstrip('%')) > 0 else C['red'],
            'Sharpe':       lambda v: C['green'] if float(v) >= 1 else (C['gold'] if float(v) >= 0 else C['red']),
            'Sortino':      lambda v: C['green'] if float(v) >= 1.5 else (C['gold'] if float(v) >= 0.5 else C['red']),
            'Max Drawdown': lambda v: C['red'] if float(v.rstrip('%')) < -20 else C['gold'],
            'Alpha (ann)':  lambda v: C['green'] if '+' in v else C['red'],
            'Beta':         lambda v: C['cyan'],
            'Correlation':  lambda v: C['cyan'],
            'Win Rate':     lambda v: C['green'] if float(v.rstrip('%')) >= 50 else C['red'],
        }

        ROW_ORDER = ['Total Return','CAGR','Volatility','Sharpe','Sortino',
                     'Max Drawdown','Calmar','VaR 95%','CVaR 95%',
                     'Win Rate','Profit Factor','Beta','Alpha (ann)','Correlation','Bars']

        keys = [k for k in ROW_ORDER if k in metrics] + \
               [k for k in metrics if k not in ROW_ORDER]

        for i, key in enumerate(keys):
            val = metrics[key]
            r   = i // 2
            c0  = (i % 2) * 2
            col_fn = COLOR_MAP.get(key)
            try:
                val_color = col_fn(val) if col_fn else C['white']
            except Exception:
                val_color = C['white']

            tk.Label(self._grid, text=key, font=('Consolas',7),
                     bg=C['bg2'], fg=C['muted'], anchor='w'
                     ).grid(row=r, column=c0,   sticky='w', padx=(4,2), pady=1)
            tk.Label(self._grid, text=val, font=('Consolas',7,'bold'),
                     bg=C['bg2'], fg=val_color, anchor='e'
                     ).grid(row=r, column=c0+1, sticky='e', padx=(0,8), pady=1)

    def clear(self):
        for w in self._grid.winfo_children():
            w.destroy()


# ═══════════════════════════════════════════════════════════════════
# MAIN DASHBOARD CLASS
# ═══════════════════════════════════════════════════════════════════
class QuantDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantResearch Dashboard  ·  India + Global")
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        ww, wh = int(sw*0.93), int(sh*0.90)
        root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        root.configure(bg=C['bg'])
        
        # ── Historical state ──────────────────────────────────
        self.data              = None
        self.benchmark_data    = None
        self.current_ticker    = None
        self.current_yf_ticker = None
        self.current_currency  = '$'
        self.current_exchange  = 'US'
        self.current_start     = None
        self.current_end       = None
        self.current_timeframe = "1M"
        self.period_config     = PERIOD_SETTINGS["1M"]
        self._crosshair_cid    = None

        # indicator states
        self.ma_states = {n: tk.BooleanVar(value=False)
                          for n in ['SMA','EMA','DEMA','TEMA','RVWAP']}
        self.indicator_states = {n: tk.BooleanVar(value=False)
                                 for n in ['MACD','ATR','RSI','Bollinger Bands',
                                           'Stochastic','Williams %R','OBV',
                                           'ADX','Parabolic SAR','Ichimoku',
                                           'Pivot Points','Fibonacci','Slope']}
        self.extra_overlay_states = {
            'Volume':         tk.BooleanVar(value=True),
            'VWAP':           tk.BooleanVar(value=False),
            'Benchmark':      tk.BooleanVar(value=False),
            'Volume Profile': tk.BooleanVar(value=False),
        }

        # Fibonacci custom range  (None = use full dataset)
        self.fib_start_var    = None   # DateEntry created in control panel
        self.fib_end_var      = None
        self.fib_use_range    = tk.BooleanVar(value=False)   # toggle custom range
        self.vp_use_range     = tk.BooleanVar(value=False)   # VP custom range
        self.custom_periods: dict[str, PeriodSpinbox] = {}

        # ── Market selector ───────────────────────────────────
        self.market_var = tk.StringVar(value="Auto")

        # ── Benchmark ─────────────────────────────────────────
        self.benchmark_var = tk.StringVar(value="^NSEI")

        # ── Live state ────────────────────────────────────────
        self.live_store  = LiveDataStore()
        self.ws_manager  = WebSocketManager(self.live_store, list(DEFAULT_LIVE_TICKERS))
        self.live_ani    = None
        self.live_canvas_widget = None
        self.live_fig    = None

        self.live_tickers_var      = tk.StringVar(value=", ".join(DEFAULT_LIVE_TICKERS))
        self.ws_status_var         = tk.StringVar(value="⚫  Disconnected")
        self.ws_manager.status_var = self.ws_status_var
        self.live_selected_ticker  = tk.StringVar(value=DEFAULT_LIVE_TICKERS[0])
        self.live_resample_var     = tk.StringVar(value="1min")

        self.live_indicator_states = {n: tk.BooleanVar(value=False)
                                      for n in ['RSI','MACD','Bollinger Bands',
                                                'Stochastic','Volume']}
        self.live_ma_states = {n: tk.BooleanVar(value=False) for n in ['SMA','EMA']}
        self.alert_thresholds: dict[str, tuple] = {}

        # ── Watchlist ─────────────────────────────────────────
        self.watchlist: list[str] = self._load_watchlist()

        self._setup_ui()

    # ─── Watchlist persistence ──────────────────────────────────
    def _load_watchlist(self):
        try:
            with open(WATCHLIST_FILE) as f:
                return json.load(f)
        except Exception:
            return []

    def _save_watchlist(self):
        try:
            with open(WATCHLIST_FILE, 'w') as f:
                json.dump(self.watchlist, f)
        except Exception:
            pass

    # ─── Root UI setup ──────────────────────────────────────────
    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook',     background=C['bg'],  borderwidth=0)
        style.configure('TNotebook.Tab', background=C['bg2'], foreground=C['muted'],
                        padding=[14,6], font=('Consolas',9,'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', C['accent'])],
                  foreground=[('selected', C['bg'])])
        style.configure('TCombobox', fieldbackground=C['bg3'], background=C['bg3'],
                        foreground=C['white'], selectbackground=C['accent'])

        # ── Status bar ─────────────────────────────────────────
        sb = tk.Frame(self.root, bg=C['bg2'], height=24)
        sb.pack(side=tk.BOTTOM, fill=tk.X)
        self.statusbar_var = tk.StringVar(value="Ready  —  Enter a ticker (e.g. RELIANCE → auto-resolves to RELIANCE.NS)")
        tk.Label(sb, textvariable=self.statusbar_var, font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted'], anchor='w').pack(side=tk.LEFT, padx=8)
        tk.Label(sb, text="QuantResearch  v3.0  |  NSE/BSE/US/Crypto", font=('Consolas',8),
                 bg=C['bg2'], fg=C['border']).pack(side=tk.RIGHT, padx=8)

        # ── Notebook ───────────────────────────────────────────
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.hist_tab  = tk.Frame(self.nb, bg=C['bg'])
        self.live_tab  = tk.Frame(self.nb, bg=C['bg'])
        self.multi_tab = tk.Frame(self.nb, bg=C['bg'])
        self.watch_tab = tk.Frame(self.nb, bg=C['bg'])

        self.nb.add(self.hist_tab,  text='📊  Historical')
        self.nb.add(self.live_tab,  text='📡  Live OHLC')
        self.nb.add(self.multi_tab, text='🗂   Multi-Ticker')
        self.nb.add(self.watch_tab, text='⭐  Watchlist')

        self._build_historical_tab()
        self._build_live_tab()
        self._build_multi_tab()
        self._build_watchlist_tab()

    def _set_status(self, msg):
        self.statusbar_var.set(msg)

    # ═══════════════════════════════════════════════════════════
    # TAB 1  ─  HISTORICAL
    # ═══════════════════════════════════════════════════════════
    def _build_historical_tab(self):
        c = tk.Frame(self.hist_tab, bg=C['bg'])
        c.pack(fill=tk.BOTH, expand=True)
        c.grid_rowconfigure(0, weight=1)
        c.grid_columnconfigure(0, weight=5)
        c.grid_columnconfigure(1, weight=1)

        # ── Left ─────────────────────────────────────────────
        left = tk.Frame(c, bg=C['bg'])
        left.grid(row=0, column=0, sticky='nsew', padx=(4,3), pady=4)

        tf_bar = tk.Frame(left, bg=C['bg2'], height=44)
        tf_bar.pack(fill=tk.X, pady=(0,3))
        tf_bar.pack_propagate(False)
        self._build_timeframe_bar(tf_bar)

        self.chart_container = tk.Frame(left, bg=C['bg2'])
        self.chart_container.pack(fill=tk.BOTH, expand=True)
        self._show_welcome(self.chart_container)

        # ── Right ─────────────────────────────────────────────
        right = tk.Frame(c, bg=C['bg2'])
        right.grid(row=0, column=1, sticky='nsew', padx=(0,4), pady=4)
        self._build_control_panel(right)

    def _build_timeframe_bar(self, parent):
        tk.Label(parent, text="RANGE:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(10,6))
        for lbl, days, tf in [('5Y',1825,'5Y'),('3Y',1095,'3Y'),('1Y',365,'1Y'),
                               ('9M',270,'9M'),('6M',180,'6M'),('3M',90,'3M'),('1M',30,'1M')]:
            tk.Button(parent, text=lbl, width=4,
                      command=lambda d=days, t=tf: self.change_time_range(d, t),
                      bg=C['bg3'], fg=C['white'], font=('Consolas',8,'bold'),
                      relief=tk.FLAT, cursor='hand2',
                      activebackground=C['accent'], activeforeground=C['bg']
                      ).pack(side=tk.LEFT, padx=2, pady=8)

        tk.Frame(parent, width=2, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        tk.Button(parent, text="💾 PNG", command=self._save_chart_png,
                  bg=C['bg3'], fg=C['cyan'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=3, pady=8)
        tk.Button(parent, text="📄 CSV", command=self._export_csv,
                  bg=C['bg3'], fg=C['cyan'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=3, pady=8)
        tk.Button(parent, text="📈 Metrics", command=self._toggle_metrics_panel,
                  bg=C['bg3'], fg=C['gold'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=3, pady=8)

    def _show_welcome(self, parent):
        tk.Label(parent,
                 text="QuantResearch Dashboard\n\n"
                      "🇮🇳  Indian NSE/BSE tickers supported\n"
                      "e.g.  RELIANCE  ·  TCS  ·  INFY  ·  NIFTY50\n\n"
                      "🌐  Global: AAPL  ·  BTC-USD  ·  ^NSEI\n\n"
                      "Select Market → Enter Ticker → Fetch Data",
                 font=('Consolas',13,'bold'), bg=C['bg2'], fg=C['accent'],
                 justify='center').pack(expand=True)

    # ── CONTROL PANEL ─────────────────────────────────────────
    def _build_control_panel(self, parent):
        tk.Label(parent, text="CONTROL PANEL", font=('Consolas',10,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(pady=(10,4))

        cv = tk.Canvas(parent, bg=C['bg2'], highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=cv.yview,
                          bg=C['bg3'], troughcolor=C['bg2'])
        sf = tk.Frame(cv, bg=C['bg2'])
        sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cw = cv.create_window((0,0), window=sf, anchor="nw")
        cv.bind("<Configure>", lambda e: cv.itemconfig(cw, width=e.width))
        cv.configure(yscrollcommand=sb.set)
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── Market selector ───────────────────────────────────
        self._cp_section(sf, "MARKET")
        mf = tk.Frame(sf, bg=C['bg2']); mf.pack(pady=4, padx=12, fill=tk.X)
        for mkt in ['Auto','NSE','BSE','US','Crypto']:
            b = tk.Radiobutton(mf, text=mkt, variable=self.market_var, value=mkt,
                               font=('Consolas',8,'bold'), bg=C['bg2'], fg=C['muted'],
                               selectcolor=C['bg3'], activebackground=C['bg2'],
                               activeforeground=C['accent'],
                               indicatoron=False, relief=tk.FLAT, bd=0,
                               cursor='hand2', width=6,
                               command=self._on_market_change)
            b.pack(side=tk.LEFT, padx=2)
        # bind selection highlight
        self.market_var.trace_add('write', lambda *_: self._refresh_market_btns(mf))
        self._market_btns = mf

        # ── Ticker entry ──────────────────────────────────────
        self._cp_section(sf, "TICKER")
        tf = tk.Frame(sf, bg=C['bg2']); tf.pack(pady=4, padx=12, fill=tk.X)
        self.ticker_var = tk.StringVar()
        ent = tk.Entry(tf, textvariable=self.ticker_var, font=('Consolas',12,'bold'),
                       bg=C['bg3'], fg=C['accent'], insertbackground=C['accent'],
                       relief=tk.FLAT, bd=4)
        ent.pack(fill=tk.X, ipady=6)
        ent.bind('<Return>', lambda _: self.fetch_and_plot())

        # Resolved ticker display
        self.resolved_label_var = tk.StringVar(value="")
        tk.Label(sf, textvariable=self.resolved_label_var, font=('Consolas',7),
                 bg=C['bg2'], fg=C['teal']).pack(anchor='w', padx=14)

        # ── Dates ─────────────────────────────────────────────
        self._cp_section(sf, "DATE RANGE")
        df = tk.Frame(sf, bg=C['bg2']); df.pack(pady=4, padx=12, fill=tk.X)
        tk.Label(df, text="Start", font=('Consolas',8), bg=C['bg2'], fg=C['muted']).pack(anchor='w')
        self.start_date = DateEntry(df, width=22, background=C['bg3'], foreground=C['white'],
                                    borderwidth=1, date_pattern='yyyy-mm-dd',
                                    font=('Consolas',9))
        self.start_date.pack(fill=tk.X, pady=(2,6))
        self.start_date.set_date(datetime.now()-timedelta(days=30))
        tk.Label(df, text="End", font=('Consolas',8), bg=C['bg2'], fg=C['muted']).pack(anchor='w')
        self.end_date = DateEntry(df, width=22, background=C['bg3'], foreground=C['white'],
                                  borderwidth=1, date_pattern='yyyy-mm-dd',
                                  font=('Consolas',9))
        self.end_date.pack(fill=tk.X, pady=(2,0))

        # ── Benchmark ─────────────────────────────────────────
        self._cp_section(sf, "BENCHMARK")
        bf = tk.Frame(sf, bg=C['bg2']); bf.pack(pady=4, padx=12, fill=tk.X)
        tk.Label(bf, text="vs", font=('Consolas',8), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        bmk_cb = ttk.Combobox(bf, textvariable=self.benchmark_var,
                               values=['^NSEI','^BSESN','^NSEBANK','SPY','QQQ',
                                       'BTC-USD','GLD','CUSTOM'],
                               width=12, font=('Consolas',8))
        bmk_cb.pack(side=tk.LEFT, padx=6)
        self._make_toggle(bf, 'Show', self.extra_overlay_states['Benchmark'],
                          callback=self._safe_update)

        tk.Button(sf, text="▶  FETCH DATA", command=self.fetch_and_plot,
                  bg=C['accent'], fg=C['bg'], font=('Consolas',11,'bold'),
                  relief=tk.FLAT, cursor='hand2',
                  activebackground=C['accent2'], activeforeground=C['bg']
                  ).pack(pady=10, padx=12, fill=tk.X, ipady=7)

        tk.Button(sf, text="⭐  Add to Watchlist", command=self._add_to_watchlist,
                  bg=C['bg3'], fg=C['gold'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(padx=12, fill=tk.X, ipady=3)

        self._cp_sep(sf)

        # ── Overlays ──────────────────────────────────────────
        self._cp_section(sf, "OVERLAYS")
        ovf = tk.Frame(sf, bg=C['bg2']); ovf.pack(pady=4, padx=12, fill=tk.X)
        for n in ['Volume','VWAP']:
            self._make_toggle(ovf, n, self.extra_overlay_states[n], callback=self._safe_update)

        # Volume Profile toggle + range sub-panel
        vp_row = tk.Frame(ovf, bg=C['bg2']); vp_row.pack(fill=tk.X, pady=2)
        vp_btn = tk.Button(vp_row, text='Volume Profile', width=14, anchor='w',
                           font=('Consolas',8), relief=tk.FLAT, cursor='hand2',
                           bg=C['bg3'], fg=C['muted'])
        def _tog_vp(v=self.extra_overlay_states['Volume Profile'], b=vp_btn):
            v.set(not v.get())
            b.config(bg=C['accent'], fg=C['bg']) if v.get() else b.config(bg=C['bg3'], fg=C['muted'])
            self._safe_update()
        vp_btn.config(command=_tog_vp)
        vp_btn.pack(side=tk.LEFT)

        # VP range sub-panel (shown inline)
        vp_rng_frame = tk.Frame(sf, bg=C['bg2']); vp_rng_frame.pack(fill=tk.X, padx=20, pady=(0,4))
        tk.Label(vp_rng_frame, text="VP Bins:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.vp_bins_sp = PeriodSpinbox(vp_rng_frame, "", 40, mn=10, mx=200, width=4)
        self.vp_bins_sp.pack(side=tk.LEFT, padx=2)
        tk.Label(vp_rng_frame, text="  Custom Range:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(6,2))
        vp_range_chk = tk.Checkbutton(vp_rng_frame, variable=self.vp_use_range,
                                       bg=C['bg2'], fg=C['accent'], selectcolor=C['bg3'],
                                       activebackground=C['bg2'], command=self._safe_update)
        vp_range_chk.pack(side=tk.LEFT)

        # VP date range pickers (start/end)
        vp_dates = tk.Frame(sf, bg=C['bg2']); vp_dates.pack(fill=tk.X, padx=20, pady=(0,4))
        tk.Label(vp_dates, text="VP From:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.vp_start_date = DateEntry(vp_dates, width=11, background=C['bg3'], foreground=C['white'],
                                        borderwidth=1, date_pattern='yyyy-mm-dd', font=('Consolas',8))
        self.vp_start_date.pack(side=tk.LEFT, padx=4)
        self.vp_start_date.set_date(datetime.now()-timedelta(days=30))
        tk.Label(vp_dates, text="→", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.vp_end_date = DateEntry(vp_dates, width=11, background=C['bg3'], foreground=C['white'],
                                      borderwidth=1, date_pattern='yyyy-mm-dd', font=('Consolas',8))
        self.vp_end_date.pack(side=tk.LEFT, padx=4)
        tk.Button(vp_dates, text="Apply", command=self._safe_update,
                  bg=C['bg3'], fg=C['teal'], font=('Consolas',7,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=2)

        self._cp_sep(sf)

        # ── Moving Averages ────────────────────────────────────
        self._cp_section(sf, "MOVING AVERAGES")
        maf = tk.Frame(sf, bg=C['bg2']); maf.pack(pady=4, padx=12, fill=tk.X)
        for n, v in self.ma_states.items():
            self._make_toggle(maf, n, v, callback=self._safe_update)

        self._cp_sep(sf)

        # ── Indicators ────────────────────────────────────────
        self._cp_section(sf, "INDICATORS  (period ↑↓)")
        indf = tk.Frame(sf, bg=C['bg2']); indf.pack(pady=4, padx=12, fill=tk.X)

        ind_defaults = {
            'RSI': 14, 'MACD': 12, 'ATR': 14,
            'Bollinger Bands': 20, 'Stochastic': 14,
            'Williams %R': 14, 'OBV': None, 'ADX': 14,
            'Parabolic SAR': None, 'Ichimoku': None,
            'Pivot Points': None, 'Fibonacci': None, 'Slope': 14,
        }
        for name, var in self.indicator_states.items():
            row = tk.Frame(indf, bg=C['bg2']); row.pack(fill=tk.X, pady=3)
            btn = tk.Button(row, text=name, width=14, anchor='w',
                            font=('Consolas',8), relief=tk.FLAT, cursor='hand2',
                            bg=C['bg3'], fg=C['muted'],
                            activebackground=C['accent'], activeforeground=C['bg'])
            btn.config(command=lambda v=var, b=btn: self._toggle_ind_btn(v, b))
            btn.pack(side=tk.LEFT)
            default_p = ind_defaults.get(name)
            if default_p is not None:
                sp = PeriodSpinbox(row, "P:", default_p, width=4)
                sp.pack(side=tk.RIGHT)
                self.custom_periods[name] = sp
            else:
                tk.Label(row, text="", bg=C['bg2'], width=8).pack(side=tk.RIGHT)

        # ── Fibonacci Range Sub-panel ─────────────────────────
        fib_sub = tk.Frame(indf, bg=C['bg2']); fib_sub.pack(fill=tk.X, pady=(0,4))
        tk.Label(fib_sub, text="  Fib Range:", font=('Consolas',7,'bold'),
                 bg=C['bg2'], fg=C['gold']).pack(side=tk.LEFT)
        fib_chk = tk.Checkbutton(fib_sub, text="Custom", variable=self.fib_use_range,
                                  font=('Consolas',7), bg=C['bg2'], fg=C['gold'],
                                  selectcolor=C['bg3'], activebackground=C['bg2'],
                                  command=self._safe_update)
        fib_chk.pack(side=tk.LEFT, padx=4)

        fib_dates = tk.Frame(indf, bg=C['bg2']); fib_dates.pack(fill=tk.X, pady=(0,4))

        tk.Label(fib_dates, text="  From:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.fib_start_var = DateEntry(fib_dates, width=11, background=C['bg3'],
                                        foreground=C['white'], borderwidth=1,
                                        date_pattern='yyyy-mm-dd', font=('Consolas',8))
        self.fib_start_var.pack(side=tk.LEFT, padx=3)
        self.fib_start_var.set_date(datetime.now()-timedelta(days=30))

        fib_dates2 = tk.Frame(indf, bg=C['bg2']); fib_dates2.pack(fill=tk.X, pady=(0,6))
        tk.Label(fib_dates2, text="  To:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(0,9))
        self.fib_end_var = DateEntry(fib_dates2, width=11, background=C['bg3'],
                                      foreground=C['white'], borderwidth=1,
                                      date_pattern='yyyy-mm-dd', font=('Consolas',8))
        self.fib_end_var.pack(side=tk.LEFT, padx=3)

        # "Use swing high/low of range" selector
        fib_mode_frame = tk.Frame(indf, bg=C['bg2']); fib_mode_frame.pack(fill=tk.X, pady=(0,6))
        tk.Label(fib_mode_frame, text="  Mode:", font=('Consolas',7), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.fib_mode_var = tk.StringVar(value="High→Low")
        for mode in ["High→Low","Low→High"]:
            tk.Radiobutton(fib_mode_frame, text=mode, variable=self.fib_mode_var, value=mode,
                           font=('Consolas',7), bg=C['bg2'], fg=C['muted'],
                           selectcolor=C['bg3'], activebackground=C['bg2'],
                           indicatoron=True, relief=tk.FLAT,
                           command=self._safe_update).pack(side=tk.LEFT, padx=3)
        tk.Button(fib_dates2, text="Apply", command=self._safe_update,
                  bg=C['bg3'], fg=C['gold'], font=('Consolas',7,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=4)

        self._cp_sep(sf)

        # ── Quant Metrics Panel ───────────────────────────────
        self.metrics_card = MetricsCard(sf)
        self.metrics_card.pack(fill=tk.X, padx=8, pady=4)

        tk.Frame(sf, height=16, bg=C['bg2']).pack()

        cv.pack(side="left",  fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _on_market_change(self):
        mkt = self.market_var.get()
        # Update benchmark default
        bmk = MARKET_BENCHMARKS.get(mkt, '^NSEI')
        if mkt != 'Auto':
            self.benchmark_var.set(bmk)
        # Refresh resolved label if ticker already entered
        raw = self.ticker_var.get().strip()
        if raw:
            yf_t, ccy, exch, disp = normalize_ticker(raw, mkt)
            self.resolved_label_var.set(f"→ {yf_t}  [{exch}]  {ccy}")

    def _refresh_market_btns(self, frame):
        mkt = self.market_var.get()
        for w in frame.winfo_children():
            if isinstance(w, tk.Radiobutton):
                if w.cget('text') == mkt:
                    w.config(fg=C['accent'])
                else:
                    w.config(fg=C['muted'])

    def _toggle_metrics_panel(self):
        if self.metrics_card.winfo_ismapped():
            self.metrics_card.pack_forget()
        else:
            self.metrics_card.pack(fill=tk.X, padx=8, pady=4)

    def _cp_section(self, parent, title):
        f = tk.Frame(parent, bg=C['bg2']); f.pack(fill=tk.X, padx=8, pady=(10,2))
        tk.Label(f, text=title, font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(anchor='w')

    def _cp_sep(self, parent):
        tk.Frame(parent, height=1, bg=C['border']).pack(fill=tk.X, padx=8, pady=6)

    def _make_toggle(self, parent, name, var, callback=None):
        f = tk.Frame(parent, bg=C['bg2']); f.pack(fill=tk.X, pady=2)
        btn = tk.Button(f, text=name, width=14, anchor='w',
                        font=('Consolas',8), relief=tk.FLAT, cursor='hand2',
                        bg=C['bg3'], fg=C['muted'])
        def _tog(v=var, b=btn):
            v.set(not v.get())
            b.config(bg=C['accent'], fg=C['bg']) if v.get() else b.config(bg=C['bg3'], fg=C['muted'])
            if callback: callback()
        btn.config(command=_tog)
        btn.pack(side=tk.LEFT)
        return btn

    def _toggle_ind_btn(self, var, btn):
        var.set(not var.get())
        btn.config(bg=C['accent'], fg=C['bg']) if var.get() else btn.config(bg=C['bg3'], fg=C['muted'])
        self._safe_update()

    def _safe_update(self):
        if self.data is not None:
            self.update_plot()

    def _get_period(self, name, fallback_key=None):
        if name in self.custom_periods:
            return self.custom_periods[name].get()
        if fallback_key and fallback_key in self.period_config:
            return self.period_config[fallback_key]
        return 14

    # ── FETCH & PLOT ──────────────────────────────────────────
    def change_time_range(self, days, tf_key):
        end_d = datetime.now()
        self.start_date.set_date(end_d - timedelta(days=days))
        self.end_date.set_date(end_d)
        self.current_timeframe = tf_key
        self.period_config = PERIOD_SETTINGS.get(tf_key, PERIOD_SETTINGS["1M"])
        if self.current_ticker:
            self.fetch_and_plot()

    def fetch_and_plot(self):
        raw = self.ticker_var.get().strip()
        if not raw:
            messagebox.showwarning("Input", "Enter a ticker symbol"); return

        market = self.market_var.get()
        yf_ticker, currency, exchange, display_name = normalize_ticker(raw, market)

        # Update resolved label
        self.resolved_label_var.set(f"→ {yf_ticker}  [{exchange}]  {currency}")

        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end   = self.end_date.get_date().strftime('%Y-%m-%d')

        try:
            for w in self.chart_container.winfo_children(): w.destroy()
            tk.Label(self.chart_container,
                     text=f"Loading {yf_ticker}…",
                     font=('Consolas',15,'bold'), bg=C['bg2'], fg=C['accent']).pack(expand=True)
            self.root.update()

            self.data = fetch_data(yf_ticker, start, end)
            if self.data is None or self.data.empty:
                # Try alternative exchange suffix if Auto
                if market == 'Auto' and '.' not in yf_ticker and not yf_ticker.startswith('^'):
                    alt = f"{raw.upper()}.BO"
                    self.data = fetch_data(alt, start, end)
                    if self.data is not None and not self.data.empty:
                        yf_ticker = alt; exchange = 'BSE'; currency = '₹'
                        self.resolved_label_var.set(f"→ {yf_ticker}  [{exchange}]  {currency}  (BSE fallback)")
                    else:
                        messagebox.showerror("No Data",
                            f"No data for '{raw}'.\n\n"
                            f"Tried: {yf_ticker}, {alt}\n\n"
                            f"Tips:\n"
                            f"• NSE tickers need .NS  (e.g. RELIANCE.NS)\n"
                            f"• BSE tickers need .BO  (e.g. RELIANCE.BO)\n"
                            f"• Or select Market = NSE/BSE before fetching\n"
                            f"• Indices: ^NSEI (Nifty), ^BSESN (Sensex)")
                        return
                else:
                    messagebox.showerror("No Data",
                        f"No data for '{yf_ticker}'.\n\n"
                        f"Tips:\n"
                        f"• NSE: RELIANCE.NS  or select Market=NSE\n"
                        f"• BSE: RELIANCE.BO  or select Market=BSE\n"
                        f"• Indices: ^NSEI, ^BSESN\n"
                        f"• Crypto: BTC-USD, ETH-USD")
                    return

            self.current_ticker    = display_name
            self.current_yf_ticker = yf_ticker
            self.current_currency  = currency
            self.current_exchange  = exchange
            self.current_start     = start
            self.current_end       = end

            # Fetch benchmark if enabled
            self.benchmark_data = None
            if self.extra_overlay_states['Benchmark'].get():
                bmk_ticker = self.benchmark_var.get().strip()
                if bmk_ticker and bmk_ticker.upper() != 'CUSTOM':
                    try:
                        self.benchmark_data = fetch_data(bmk_ticker, start, end)
                    except Exception:
                        pass

            # Quant metrics
            metrics = compute_quant_metrics(
                self.data['Close'],
                self.benchmark_data['Close'] if self.benchmark_data is not None else None
            )
            self.metrics_card.update(metrics)

            self._set_status(
                f"✓ {yf_ticker}  [{exchange}]  {currency}  |  "
                f"{len(self.data)} bars  |  {start} → {end}")
            self.update_plot()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            import traceback; traceback.print_exc()

    # ── MASTER PLOT BUILDER ───────────────────────────────────
    def update_plot(self):
        if self.data is None or self.data.empty:
            return
        for w in self.chart_container.winfo_children():
            w.destroy()

        ccy = self.current_currency

        sub_panel_inds = ['MACD','ATR','RSI','Stochastic','Williams %R','OBV','ADX','Slope']
        active_sub = [n for n in sub_panel_inds if self.indicator_states[n].get()]
        n = len(active_sub)
        show_vol = self.extra_overlay_states['Volume'].get()

        n_rows  = 1 + (1 if show_vol else 0) + n
        ratios  = [5] + ([1] if show_vol else []) + [1.5]*n
        fig     = Figure(figsize=(13,8), facecolor=C['bg'], dpi=100)
        gs      = fig.add_gridspec(n_rows, 1, height_ratios=ratios, hspace=0.08)

        row_idx = 0
        ax_main = fig.add_subplot(gs[row_idx]); row_idx += 1
        style_ax(ax_main)

        d_idx = draw_candles(ax_main, self.data)
        x_idx = np.arange(len(d_idx))

        # ── Benchmark overlay ─────────────────────────────────
        if (self.extra_overlay_states['Benchmark'].get() and
                self.benchmark_data is not None and not self.benchmark_data.empty):
            bmk = self.benchmark_data['Close'].reindex(self.data.index, method='ffill')
            # Normalise to same starting price
            scale = self.data['Close'].iloc[0] / bmk.iloc[0]
            bmk_scaled = bmk * scale
            ax_main.plot(x_idx, bmk_scaled.values,
                         color=C['muted'], lw=1, linestyle=':', alpha=0.6,
                         label=f'Benchmark ({self.benchmark_var.get()})')

        # ── Bollinger Bands ───────────────────────────────────
        if self.indicator_states['Bollinger Bands'].get():
            p = self._get_period('Bollinger Bands', 'bb')
            bu, bm, bl = bb_bands(self.data['Close'], period=p)
            ax_main.plot(x_idx, bu.values, color=C['gold'],  linestyle='--', lw=1,   alpha=0.8, label=f'BB↑({p})')
            ax_main.plot(x_idx, bm.values, color=C['cyan'],  linestyle='-.', lw=0.8, alpha=0.7, label='BB mid')
            ax_main.plot(x_idx, bl.values, color=C['gold'],  linestyle='--', lw=1,   alpha=0.8, label=f'BB↓({p})')
            ax_main.fill_between(x_idx, bu.values, bl.values, alpha=0.06, color=C['gold'])

        if self.indicator_states['Ichimoku'].get():
            t, k, sa, sb_l, ch = ichimoku(self.data)
            ax_main.plot(x_idx, t.values,    color='#ff6b6b', lw=1,   label='Tenkan')
            ax_main.plot(x_idx, k.values,    color='#4ecdc4', lw=1,   label='Kijun')
            ax_main.plot(x_idx, sa.values,   color='#a8e6cf', lw=0.8, alpha=0.7, label='Senkou A')
            ax_main.plot(x_idx, sb_l.values, color='#ff8b94', lw=0.8, alpha=0.7, label='Senkou B')
            ax_main.fill_between(x_idx, sa.values, sb_l.values,
                                  where=sa.values >= sb_l.values, alpha=0.12, color='#a8e6cf')
            ax_main.fill_between(x_idx, sa.values, sb_l.values,
                                  where=sa.values <  sb_l.values, alpha=0.12, color='#ff8b94')

        if self.indicator_states['Parabolic SAR'].get():
            sar_s, trend_s = parabolic_sar(self.data)
            ax_main.scatter(x_idx[trend_s.values == 1],  sar_s.values[trend_s.values == 1],
                            color=C['green'], s=8, marker='.', alpha=0.9, label='SAR↑', zorder=5)
            ax_main.scatter(x_idx[trend_s.values == -1], sar_s.values[trend_s.values == -1],
                            color=C['red'],   s=8, marker='.', alpha=0.9, label='SAR↓', zorder=5)

        if self.indicator_states['Fibonacci'].get():
            # Determine slice for Fib calculation
            fib_data = self.data
            fib_start_xi = 0
            fib_end_xi   = len(self.data) - 1

            if self.fib_use_range.get() and self.fib_start_var is not None:
                fs = pd.Timestamp(self.fib_start_var.get_date())
                fe = pd.Timestamp(self.fib_end_var.get_date())
                mask = (self.data.index >= fs) & (self.data.index <= fe)
                if mask.any():
                    fib_data    = self.data.loc[mask]
                    fib_start_xi = np.where(mask)[0][0]
                    fib_end_xi   = np.where(mask)[0][-1]

            # Find swing high and low in the selected range
            mode     = getattr(self, 'fib_mode_var', None)
            mode_val = mode.get() if mode else "High→Low"
            swing_h  = float(fib_data['High'].max())
            swing_l  = float(fib_data['Low'].min())

            # Fibonacci ratios
            fib_ratios = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0,
                          1.272, 1.618]
            fib_labels = ['0%','23.6%','38.2%','50%','61.8%','78.6%','100%',
                          '127.2%','161.8%']
            fib_colors = ['#ff6b6b','#ffb347','#ffd700','#98fb98',
                          '#00e5ff','#ce93d8','#4ecdc4','#ff6b6b','#ffb347']

            if mode_val == "High→Low":
                price_start, price_end = swing_h, swing_l
            else:
                price_start, price_end = swing_l, swing_h

            diff = price_end - price_start

            # Draw shaded zone between 38.2% and 61.8% (Golden Zone)
            gz_lo = price_start + diff * 0.382
            gz_hi = price_start + diff * 0.618
            ax_main.axhspan(min(gz_lo,gz_hi), max(gz_lo,gz_hi),
                            alpha=0.07, color='#ffd700', zorder=0,
                            label='Golden Zone 38.2–61.8%')

            for ratio, lbl, fc in zip(fib_ratios, fib_labels, fib_colors):
                lvl = price_start + diff * ratio
                ax_main.axhline(lvl, color=fc, linestyle=':', lw=0.9, alpha=0.75)

                # Label at RIGHT edge showing price and ratio
                ax_main.text(len(self.data) - 0.5, lvl,
                             f'  {lbl}  {fmt_price(lvl, ccy)}',
                             color=fc, fontsize=5.5, va='center',
                             fontfamily='Consolas',
                             bbox=dict(facecolor=C['bg'], alpha=0.5, pad=0.5,
                                       edgecolor='none'))

            # Mark the swing points on chart
            h_xi = int(fib_data['High'].values.argmax()) + fib_start_xi
            l_xi = int(fib_data['Low'].values.argmin())  + fib_start_xi
            ax_main.annotate(f'⬆ {fmt_price(swing_h,ccy)}',
                             xy=(h_xi, swing_h), fontsize=6, color='#ffd700',
                             fontfamily='Consolas',
                             xytext=(h_xi, swing_h + (swing_h-swing_l)*0.02),
                             arrowprops=dict(arrowstyle='->', color='#ffd700', lw=0.8))
            ax_main.annotate(f'⬇ {fmt_price(swing_l,ccy)}',
                             xy=(l_xi, swing_l), fontsize=6, color='#ff6b6b',
                             fontfamily='Consolas',
                             xytext=(l_xi, swing_l - (swing_h-swing_l)*0.02),
                             arrowprops=dict(arrowstyle='->', color='#ff6b6b', lw=0.8))

            # Highlight the selected fib range with a vertical band
            if self.fib_use_range.get():
                ax_main.axvspan(fib_start_xi, fib_end_xi,
                                alpha=0.05, color='#ffd700', zorder=0)

        if self.indicator_states['Pivot Points'].get():
            pp = pivot_points(self.data)
            for lbl, lvl in pp.items():
                fc = C['green'] if lbl.startswith('R') else (C['red'] if lbl.startswith('S') else C['gold'])
                ax_main.axhline(lvl, color=fc, linestyle='--', lw=0.7, alpha=0.6)
                ax_main.text(0, lvl, f' {lbl}:{fmt_price(lvl,ccy)}', color=fc, fontsize=5, va='center')

        if self.extra_overlay_states['VWAP'].get() and 'Volume' in self.data.columns:
            p  = self.period_config.get('rvwap', 20)
            vw = RVWAP(self.data['High'], self.data['Low'],
                       self.data['Close'], self.data['Volume'], period=p)
            ax_main.plot(x_idx, vw.values, color='#ff6b81', lw=1.2,
                         linestyle='-.', alpha=0.85, label=f'RVWAP({p})')

        # ── Moving Averages ───────────────────────────────────
        mp = self._get_period('SMA', 'ma')
        ma_colors = {'SMA':'#29b6f6','EMA':'#ffb347','DEMA':'#ce93d8',
                     'TEMA':'#ffd580','RVWAP':'#ff6b81'}
        for n_ma, v_ma in self.ma_states.items():
            if not v_ma.get(): continue
            if n_ma == 'SMA':
                ax_main.plot(x_idx, sma(self.data['Close'], mp).values,
                             color=ma_colors['SMA'], lw=1.4, linestyle='--', alpha=0.85, label=f'SMA({mp})')
            elif n_ma == 'EMA':
                ax_main.plot(x_idx, ema(self.data['Close'], mp).values,
                             color=ma_colors['EMA'], lw=1.4, linestyle='--', alpha=0.85, label=f'EMA({mp})')
            elif n_ma == 'DEMA':
                ax_main.plot(x_idx, demma(self.data['Close'], mp).values,
                             color=ma_colors['DEMA'], lw=1.4, linestyle='-.', alpha=0.85, label=f'DEMA({mp})')
            elif n_ma == 'TEMA':
                ax_main.plot(x_idx, temma(self.data['Close'], mp).values,
                             color=ma_colors['TEMA'], lw=1.4, linestyle='-.', alpha=0.85, label=f'TEMA({mp})')
            elif n_ma == 'RVWAP' and 'Volume' in self.data.columns:
                p_rv = self.period_config.get('rvwap', 20)
                rv = RVWAP(self.data['High'], self.data['Low'],
                           self.data['Close'], self.data['Volume'], period=p_rv)
                ax_main.plot(x_idx, rv.values, color=ma_colors['RVWAP'], lw=1.4,
                             linestyle='-.', alpha=0.85, label=f'RVWAP({p_rv})')

        # ── Y-axis: currency formatting ────────────────────────
        sym = ccy
        ax_main.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{sym}{x:,.0f}" if abs(x) >= 1000 else f"{sym}{x:.2f}"))

        # ── Volume Profile overlay ─────────────────────────────
        if self.extra_overlay_states['Volume Profile'].get() and 'Volume' in self.data.columns:
            n_bins = self.vp_bins_sp.get() if hasattr(self, 'vp_bins_sp') else 40
            vp_start_xi, vp_end_xi = None, None

            if self.vp_use_range.get() and hasattr(self, 'vp_start_date'):
                vs = pd.Timestamp(self.vp_start_date.get_date())
                ve = pd.Timestamp(self.vp_end_date.get_date())
                mask = (self.data.index >= vs) & (self.data.index <= ve)
                if mask.any():
                    vp_start_xi = int(np.where(mask)[0][0])
                    vp_end_xi   = int(np.where(mask)[0][-1])
                    # Highlight VP range
                    ax_main.axvspan(vp_start_xi, vp_end_xi,
                                    alpha=0.04, color=C['teal'], zorder=0)

            draw_volume_profile(ax_main, self.data,
                                fib_start_idx=vp_start_xi, fib_end_idx=vp_end_xi,
                                n_bins=n_bins)

        # Re-lock tight Y after all overlays (overlays may push y to 0)
        lo = self.data['Low'].min()
        hi = self.data['High'].max()
        pad = (hi - lo) * 0.03
        ax_main.set_ylim(lo - pad, hi + pad * 3)

        ax_main.set_title(
            f'{self.current_ticker}  ·  [{self.current_exchange}]  ·  '
            f'{self.current_start} → {self.current_end}  ·  {self.current_timeframe}',
            color=C['white'], fontsize=11, fontweight='bold', pad=8)
        ax_main.set_ylabel(f'Price ({ccy})', color=C['muted'], fontsize=8)
        set_x_date_ticks(ax_main, d_idx)
        handles, labels = ax_main.get_legend_handles_labels()
        if handles:
            ax_main.legend(loc='upper left', facecolor=C['bg3'], edgecolor=C['border'],
                           labelcolor=C['white'], fontsize=6, framealpha=0.7)

        # ── Volume subplot ────────────────────────────────────
        if show_vol and 'Volume' in self.data.columns:
            ax_vol = fig.add_subplot(gs[row_idx]); row_idx += 1
            style_ax(ax_vol, ylabel='Vol')
            vol      = self.data['Volume'].values
            colors_v = [C['green'] if self.data['Close'].iloc[i] >= self.data['Open'].iloc[i]
                        else C['red'] for i in range(len(self.data))]
            ax_vol.bar(x_idx, vol, color=colors_v, alpha=0.7, width=0.8)
            ax_vol.set_xlim(-0.5, len(self.data)-0.5)
            ax_vol.tick_params(labelbottom=False)
            # Indian-aware formatting
            if self.current_exchange in ('NSE','BSE'):
                ax_vol.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x,_: f'{x/1e7:.1f}Cr' if x>=1e7 else
                                                       f'{x/1e5:.1f}L'  if x>=1e5 else
                                                       f'{x/1e3:.0f}K'))
            else:
                ax_vol.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x,_: f'{x/1e6:.1f}M' if x>=1e6 else f'{x/1e3:.0f}K'))

        # ── Sub-panel indicators ──────────────────────────────
        for ind_name in active_sub:
            ax_i = fig.add_subplot(gs[row_idx]); row_idx += 1
            style_ax(ax_i)
            ax_i.set_xlim(-0.5, len(self.data)-0.5)

            if ind_name == 'RSI':
                p = self._get_period('RSI', 'rsi')
                v = Rsi(self.data['Close'], period=p)
                ax_i.plot(x_idx, v.values, color=C['purple'], lw=1.5)
                ax_i.axhline(70, color=C['red'],   linestyle='--', lw=1, alpha=0.7)
                ax_i.axhline(30, color=C['green'],  linestyle='--', lw=1, alpha=0.7)
                ax_i.fill_between(x_idx, 70, 100, alpha=0.08, color=C['red'])
                ax_i.fill_between(x_idx, 0,  30,  alpha=0.08, color=C['green'])
                ax_i.set_ylim(0, 100)
                ax_i.set_ylabel(f'RSI({p})', color=C['purple'], fontsize=7)

            elif ind_name == 'MACD':
                s, l, sp = self.period_config.get('macd', (12,26,9))
                mc, sig, hist = macd(self.data['Close'], s, l, sp)
                ax_i.plot(x_idx, mc.values,  color=C['blue'],   lw=1.2, label='MACD')
                ax_i.plot(x_idx, sig.values, color=C['accent'],  lw=1.2, label='Signal')
                colors_h = [C['green'] if v >= 0 else C['red'] for v in hist.values]
                ax_i.bar(x_idx, hist.values, color=colors_h, alpha=0.6, width=0.8)
                ax_i.axhline(0, color=C['muted'], lw=0.6, alpha=0.4)
                ax_i.set_ylabel('MACD', color=C['blue'], fontsize=7)
                ax_i.legend(loc='upper left', fontsize=5, facecolor=C['bg3'],
                            edgecolor=C['border'], labelcolor=C['white'])

            elif ind_name == 'ATR':
                p = self._get_period('ATR', 'atr')
                v = atr(self.data, period=p)
                ax_i.plot(x_idx, v.values, color=C['accent'], lw=1.5)
                ax_i.fill_between(x_idx, 0, v.values, alpha=0.15, color=C['accent'])
                ax_i.set_ylabel(f'ATR({p})', color=C['accent'], fontsize=7)
                # Format ATR in currency
                ax_i.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x,_: f"{sym}{x:,.0f}" if x>=1000 else f"{sym}{x:.2f}"))

            elif ind_name == 'Stochastic':
                kp, dp = self.period_config.get('stoch', (14,3))
                k, d = stochastic(self.data, k_period=kp, d_period=dp)
                ax_i.plot(x_idx, k.values, color=C['cyan'],   lw=1.2, label='%K')
                ax_i.plot(x_idx, d.values, color=C['accent'],  lw=1.2, label='%D')
                ax_i.axhline(80, color=C['red'],  linestyle='--', lw=0.8, alpha=0.7)
                ax_i.axhline(20, color=C['green'], linestyle='--', lw=0.8, alpha=0.7)
                ax_i.fill_between(x_idx, 80, 100, alpha=0.07, color=C['red'])
                ax_i.fill_between(x_idx, 0,  20,  alpha=0.07, color=C['green'])
                ax_i.set_ylim(0, 100)
                ax_i.set_ylabel(f'Stoch({kp},{dp})', color=C['cyan'], fontsize=7)
                ax_i.legend(fontsize=5, facecolor=C['bg3'], edgecolor=C['border'], labelcolor=C['white'])

            elif ind_name == 'Williams %R':
                p = self._get_period('Williams %R', 'williams')
                v = williams_r(self.data, period=p)
                ax_i.plot(x_idx, v.values, color='#ff6b6b', lw=1.5)
                ax_i.axhline(-20, color=C['red'],   linestyle='--', lw=0.8, alpha=0.7)
                ax_i.axhline(-80, color=C['green'],  linestyle='--', lw=0.8, alpha=0.7)
                ax_i.set_ylim(-100, 0)
                ax_i.set_ylabel(f'%R({p})', color='#ff6b6b', fontsize=7)

            elif ind_name == 'OBV':
                v = obv(self.data)
                ax_i.plot(x_idx, v.values, color='#69d2e7', lw=1.2)
                ax_i.fill_between(x_idx, 0, v.values, alpha=0.1, color='#69d2e7')
                ax_i.set_ylabel('OBV', color='#69d2e7', fontsize=7)
                if self.current_exchange in ('NSE','BSE'):
                    ax_i.yaxis.set_major_formatter(
                        mticker.FuncFormatter(lambda x,_: f'{x/1e7:.1f}Cr' if abs(x)>=1e7 else
                                                           f'{x/1e5:.1f}L'  if abs(x)>=1e5 else str(int(x))))
                else:
                    ax_i.yaxis.set_major_formatter(
                        mticker.FuncFormatter(lambda x,_: f'{x/1e6:.1f}M' if abs(x)>=1e6 else f'{x/1e3:.0f}K'))

            elif ind_name == 'ADX':
                p = self._get_period('ADX', 'adx')
                adx_v, plus_di, minus_di = adx(self.data, period=p)
                ax_i.plot(x_idx, adx_v.values,   color=C['gold'],  lw=1.5, label=f'ADX({p})')
                ax_i.plot(x_idx, plus_di.values,  color=C['green'], lw=1,   label='+DI', linestyle='--')
                ax_i.plot(x_idx, minus_di.values, color=C['red'],   lw=1,   label='-DI', linestyle='--')
                ax_i.axhline(25, color=C['muted'], linestyle=':', lw=0.7, alpha=0.6)
                ax_i.set_ylabel('ADX', color=C['gold'], fontsize=7)
                ax_i.legend(fontsize=5, facecolor=C['bg3'], edgecolor=C['border'], labelcolor=C['white'])

            elif ind_name == 'Slope':
                p = self._get_period('Slope', 'slope')
                v = slope(self.data['Close'], period=p)
                colors_sl = [C['green'] if x >= 0 else C['red'] for x in v.fillna(0).values]
                ax_i.bar(x_idx, v.values, color=colors_sl, alpha=0.8, width=0.8)
                ax_i.axhline(0, color=C['muted'], lw=0.7, alpha=0.5)
                ax_i.set_ylabel(f'Slope({p})', color=C['white'], fontsize=7)

            set_x_date_ticks(ax_i, d_idx)

        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = tk.Frame(self.chart_container, bg=C['bg2'])
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.config(bg=C['bg2'])
        toolbar.update()

        self._attach_crosshair(canvas, fig, ax_main, d_idx)

    # ── CROSSHAIR ─────────────────────────────────────────────
    def _attach_crosshair(self, canvas, fig, ax, index):
        vline     = ax.axvline(x=0, color=C['muted'], lw=0.7, linestyle='--', alpha=0.6)
        hline     = ax.axhline(y=0, color=C['muted'], lw=0.7, linestyle='--', alpha=0.6)
        info_text = ax.text(0.01, 0.98, '', transform=ax.transAxes,
                            color=C['accent'], fontsize=7, va='top',
                            fontfamily='Consolas',
                            bbox=dict(facecolor=C['bg3'], alpha=0.75,
                                      edgecolor=C['border'], boxstyle='round,pad=0.3'))
        ccy = self.current_currency

        def on_move(event):
            if event.inaxes != ax:
                return
            xi = int(round(event.xdata))
            if xi < 0 or xi >= len(self.data):
                return
            row = self.data.iloc[xi]
            vline.set_xdata([xi])
            hline.set_ydata([event.ydata])
            o  = fmt_price(row['Open'],  ccy)
            h  = fmt_price(row['High'],  ccy)
            l  = fmt_price(row['Low'],   ccy)
            cl = fmt_price(row['Close'], ccy)
            chg = ((row['Close']/self.data['Close'].iloc[max(0,xi-1)])-1)*100
            vol = fmt_vol(row.get('Volume', 0))
            txt = (f"{self.data.index[xi].strftime('%d %b %Y')}  "
                   f"O:{o}  H:{h}  L:{l}  C:{cl}  "
                   f"Δ:{chg:+.2f}%  Vol:{vol}")
            info_text.set_text(txt)
            canvas.draw_idle()

        if self._crosshair_cid:
            try: fig.canvas.mpl_disconnect(self._crosshair_cid)
            except Exception: pass
        self._crosshair_cid = fig.canvas.mpl_connect('motion_notify_event', on_move)

    # ── EXPORT HELPERS ─────────────────────────────────────────
    def _save_chart_png(self):
        path = filedialog.asksaveasfilename(defaultextension='.png',
                                            filetypes=[("PNG","*.png"),("All","*.*")])
        if path:
            for w in self.chart_container.winfo_children():
                try:
                    fig = getattr(w, 'figure', None)
                    if fig:
                        fig.savefig(path, dpi=150, facecolor=C['bg'])
                        self._set_status(f"Chart saved → {path}")
                        return
                except Exception:
                    pass

    def _export_csv(self):
        if self.data is None:
            messagebox.showwarning("Export CSV", "No data loaded."); return
        path = filedialog.asksaveasfilename(defaultextension='.csv',
                                            filetypes=[("CSV","*.csv"),("All","*.*")])
        if path:
            self.data.to_csv(path)
            self._set_status(f"CSV saved → {path}")

    # ── WATCHLIST HELPERS ──────────────────────────────────────
    def _add_to_watchlist(self):
        raw    = self.ticker_var.get().strip()
        market = self.market_var.get()
        if not raw: return
        yf_t, _, _, _ = normalize_ticker(raw, market)
        if yf_t and yf_t not in self.watchlist:
            self.watchlist.append(yf_t)
            self._save_watchlist()
            self._refresh_watchlist_panel()
            self._set_status(f"{yf_t} added to watchlist")

    # ═══════════════════════════════════════════════════════════
    # TAB 2  ─  LIVE OHLC
    # ═══════════════════════════════════════════════════════════
    def _build_live_tab(self):
        top = tk.Frame(self.live_tab, bg=C['bg2'], height=50)
        top.pack(fill=tk.X, padx=4, pady=(4,0))
        top.pack_propagate(False)

        tk.Label(top, textvariable=self.ws_status_var, font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['green']).pack(side=tk.LEFT, padx=10)
        tk.Frame(top, width=1, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        tk.Label(top, text="TICKERS:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(0,4))
        tk.Entry(top, textvariable=self.live_tickers_var, font=('Consolas',9),
                 bg=C['bg3'], fg=C['white'], insertbackground=C['accent'],
                 relief=tk.FLAT, bd=3, width=38).pack(side=tk.LEFT, ipady=3)

        tk.Button(top, text="▶ CONNECT", command=self._start_live,
                  bg=C['accent'], fg=C['bg'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=6, ipady=3)
        tk.Button(top, text="↺ RECONNECT", command=lambda: self.ws_manager.reconnect(),
                  bg=C['bg3'], fg=C['muted'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=3, ipady=3)

        tk.Frame(top, width=1, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        tk.Label(top, text="PLOT:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(0,4))
        self._live_ticker_menu = ttk.Combobox(top, textvariable=self.live_selected_ticker,
                                               values=DEFAULT_LIVE_TICKERS, width=14,
                                               font=('Consolas',9))
        self._live_ticker_menu.pack(side=tk.LEFT, ipady=3)

        tk.Label(top, text="INTERVAL:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(8,4))
        ttk.Combobox(top, textvariable=self.live_resample_var,
                     values=["1s","5s","15s","30s","1min","5min","15min"],
                     width=7, font=('Consolas',9)).pack(side=tk.LEFT, ipady=3)

        tk.Frame(top, width=1, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        for name, var in self.live_indicator_states.items():
            b = tk.Button(top, text=name, font=('Consolas',7,'bold'),
                          bg=C['bg3'], fg=C['muted'], relief=tk.FLAT, cursor='hand2',
                          width=max(4,len(name)))
            b.config(command=lambda v=var, btn=b: self._toggle_live_btn(v, btn))
            b.pack(side=tk.LEFT, padx=2, ipady=2)
        for name, var in self.live_ma_states.items():
            b = tk.Button(top, text=name, width=5, font=('Consolas',7,'bold'),
                          bg=C['bg3'], fg=C['muted'], relief=tk.FLAT, cursor='hand2')
            b.config(command=lambda v=var, btn=b: self._toggle_live_btn(v, btn))
            b.pack(side=tk.LEFT, padx=2, ipady=2)

        # Alert row
        alert_row = tk.Frame(self.live_tab, bg=C['bg2'], height=34)
        alert_row.pack(fill=tk.X, padx=4, pady=(2,0))
        alert_row.pack_propagate(False)
        tk.Label(alert_row, text="ALERT:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=8)
        self.alert_ticker_var = tk.StringVar(value="RELIANCE.NS")
        tk.Entry(alert_row, textvariable=self.alert_ticker_var, width=12,
                 bg=C['bg3'], fg=C['white'], relief=tk.FLAT, font=('Consolas',8)
                 ).pack(side=tk.LEFT, padx=4, ipady=2)
        tk.Label(alert_row, text="Low:", font=('Consolas',8), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self.alert_low_var  = tk.StringVar(value="")
        self.alert_high_var = tk.StringVar(value="")
        tk.Entry(alert_row, textvariable=self.alert_low_var, width=8,
                 bg=C['bg3'], fg=C['red'], relief=tk.FLAT, font=('Consolas',8)
                 ).pack(side=tk.LEFT, padx=3, ipady=2)
        tk.Label(alert_row, text="High:", font=('Consolas',8), bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        tk.Entry(alert_row, textvariable=self.alert_high_var, width=8,
                 bg=C['bg3'], fg=C['green'], relief=tk.FLAT, font=('Consolas',8)
                 ).pack(side=tk.LEFT, padx=3, ipady=2)
        tk.Button(alert_row, text="Set Alert", command=self._set_alert,
                  bg=C['bg3'], fg=C['accent'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=6, ipady=2)
        self.alert_status_var = tk.StringVar(value="No alerts set")
        tk.Label(alert_row, textvariable=self.alert_status_var, font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=8)

        content = tk.Frame(self.live_tab, bg=C['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        content.grid_columnconfigure(0, weight=5)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.live_chart_frame = tk.Frame(content, bg=C['bg2'])
        self.live_chart_frame.grid(row=0, column=0, sticky='nsew', padx=(0,3))
        tk.Label(self.live_chart_frame,
                 text="Press ▶ CONNECT to start live stream\n\n"
                      "Use full yfinance tickers:\n"
                      "NSE: RELIANCE.NS  ·  TCS.NS  ·  INFY.NS\n"
                      "BSE: RELIANCE.BO\n"
                      "US:  AAPL  ·  MSFT  ·  SPY\n"
                      "Crypto: BTC-USD  ·  ETH-USD",
                 font=('Consolas',12,'bold'), bg=C['bg2'], fg=C['accent'],
                 justify='center').pack(expand=True)

        rp = tk.Frame(content, bg=C['bg2'])
        rp.grid(row=0, column=1, sticky='nsew')
        self._build_live_right_panel(rp)
        self._refresh_price_labels()

    def _build_live_right_panel(self, parent):
        tk.Label(parent, text="LIVE PRICES", font=('Consolas',9,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(pady=(8,4))
        tk.Frame(parent, height=1, bg=C['border']).pack(fill=tk.X, padx=6, pady=2)

        self.price_labels = {}
        self.price_spark_axes = {}
        spark_fig = Figure(figsize=(1.8, len(DEFAULT_LIVE_TICKERS)*0.55),
                           facecolor=C['bg2'], dpi=80)
        self._spark_fig = spark_fig

        for ticker in DEFAULT_LIVE_TICKERS:
            row_f = tk.Frame(parent, bg=C['bg2']); row_f.pack(fill=tk.X, padx=6, pady=3)
            # Detect currency for display
            _, ccy, _, _ = normalize_ticker(ticker, 'Auto')
            tk.Label(row_f, text=ticker, font=('Consolas',7,'bold'),
                     bg=C['bg2'], fg=C['white'], width=12, anchor='w').pack(side=tk.LEFT)
            lbl = tk.Label(row_f, text="—", font=('Consolas',8,'bold'),
                           bg=C['bg2'], fg=C['muted'], anchor='e')
            lbl.pack(side=tk.RIGHT)
            self.price_labels[ticker] = lbl

        spark_canvas = FigureCanvasTkAgg(spark_fig, parent)
        spark_canvas.get_tk_widget().pack(fill=tk.X, padx=4, pady=4)
        self._spark_canvas = spark_canvas

        for i, ticker in enumerate(DEFAULT_LIVE_TICKERS):
            ax = spark_fig.add_subplot(len(DEFAULT_LIVE_TICKERS), 1, i+1)
            ax.set_facecolor(C['bg2']); ax.axis('off')
            self.price_spark_axes[ticker] = ax

        tk.Frame(parent, height=1, bg=C['border']).pack(fill=tk.X, padx=6, pady=4)
        tk.Label(parent, text="TICK LOG", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(anchor='w', padx=8)
        self._tick_log_text = tk.Text(parent, height=12, font=('Consolas',7),
                                      bg=C['bg3'], fg=C['muted'], relief=tk.FLAT,
                                      state=tk.DISABLED)
        self._tick_log_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

    def _set_alert(self):
        ticker = self.alert_ticker_var.get().strip().upper()
        try:
            lo = float(self.alert_low_var.get())  if self.alert_low_var.get().strip()  else None
            hi = float(self.alert_high_var.get()) if self.alert_high_var.get().strip() else None
        except ValueError:
            messagebox.showwarning("Alert", "Invalid price values"); return
        self.alert_thresholds[ticker] = (lo, hi)
        self.alert_status_var.set(f"{ticker}: lo={lo} hi={hi}")

    def _check_alerts(self):
        for ticker, (lo, hi) in list(self.alert_thresholds.items()):
            price = self.live_store.get_latest_price(ticker)
            if price is None: continue
            _, ccy, _, _ = normalize_ticker(ticker, 'Auto')
            if lo is not None and price <= lo:
                beep()
                messagebox.showinfo("⚠️  ALERT", f"{ticker} BELOW {fmt_price(lo,ccy)}\nCurrent: {fmt_price(price,ccy)}")
                self.alert_thresholds[ticker] = (None, hi)
            if hi is not None and price >= hi:
                beep()
                messagebox.showinfo("⚠️  ALERT", f"{ticker} ABOVE {fmt_price(hi,ccy)}\nCurrent: {fmt_price(price,ccy)}")
                self.alert_thresholds[ticker] = (lo, None)

    def _toggle_live_btn(self, var, btn):
        var.set(not var.get())
        btn.config(bg=C['accent'], fg=C['bg']) if var.get() else btn.config(bg=C['bg3'], fg=C['muted'])

    def _start_live(self):
        raw     = self.live_tickers_var.get()
        tickers = [t.strip() for t in raw.replace(',', ' ').split() if t.strip()]
        if not tickers:
            messagebox.showwarning("Live", "Enter at least one ticker."); return
        self._live_ticker_menu['values'] = tickers
        if self.live_selected_ticker.get() not in tickers:
            self.live_selected_ticker.set(tickers[0])
        self.ws_manager.start(tickers)
        self._init_live_chart()

    def _init_live_chart(self):
        if self.live_ani:
            try: self.live_ani.event_source.stop()
            except Exception: pass
            self.live_ani = None
        for w in self.live_chart_frame.winfo_children(): w.destroy()
        self.live_fig = Figure(figsize=(11,7), facecolor=C['bg'], dpi=100)
        self.live_canvas_widget = FigureCanvasTkAgg(self.live_fig, self.live_chart_frame)
        self.live_canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.live_ani = animation.FuncAnimation(
            self.live_fig, self._update_live_chart, interval=2000, cache_frame_data=False)

    def _update_live_chart(self, frame):
        if self.live_fig is None: return
        self._check_alerts()

        ticker   = self.live_selected_ticker.get().strip()
        resample = self.live_resample_var.get()
        ohlc     = self.live_store.get_ohlc(ticker, resample)
        _, ccy, _, _ = normalize_ticker(ticker, 'Auto')

        self.live_fig.clear()
        active_inds = [n for n,v in self.live_indicator_states.items()
                       if v.get() and n not in ('Bollinger Bands','Volume')]
        n_inds   = len(active_inds)
        show_vol = self.live_indicator_states.get('Volume', tk.BooleanVar()).get() \
                   if 'Volume' in self.live_indicator_states else False

        n_rows = 1 + (1 if show_vol else 0) + n_inds
        ratios = [4] + ([1] if show_vol else []) + [1.5]*n_inds
        gs     = self.live_fig.add_gridspec(n_rows, 1, height_ratios=ratios, hspace=0.1)
        ax_main = self.live_fig.add_subplot(gs[0])
        style_ax(ax_main)
        row_i = 1

        x_idx = np.arange(len(ohlc)) if not ohlc.empty else np.array([])

        if ohlc.empty:
            ax_main.text(0.5, 0.5, f"Waiting for {ticker} data…",
                         ha='center', va='center', color=C['accent'],
                         fontsize=14, transform=ax_main.transAxes)
        else:
            width = 0.6
            for i, row in enumerate(ohlc.itertuples()):
                color = C['green'] if row.close >= row.open else C['red']
                ax_main.plot([i,i], [row.low,row.high], color=C['border'], lw=0.7)
                body_h = abs(row.close - row.open) or (row.high-row.low)*0.01
                ax_main.add_patch(plt.Rectangle(
                    (i-width/2, min(row.open,row.close)), width, body_h,
                    facecolor=color, edgecolor='none', alpha=0.92))

            if self.live_indicator_states['Bollinger Bands'].get() and len(ohlc) >= 20:
                bu,bm,bl = bb_bands(ohlc['close'], period=min(20,len(ohlc)))
                ax_main.plot(x_idx, bu.values, color=C['gold'], linestyle='--', lw=0.9, alpha=0.8)
                ax_main.plot(x_idx, bm.values, color=C['cyan'], linestyle='-.', lw=0.7, alpha=0.7)
                ax_main.plot(x_idx, bl.values, color=C['gold'], linestyle='--', lw=0.9, alpha=0.8)
                ax_main.fill_between(x_idx, bu.values, bl.values, alpha=0.06, color=C['gold'])

            for n_ma, v_ma in self.live_ma_states.items():
                if not v_ma.get() or len(ohlc) < 9: continue
                fn  = sma if n_ma == 'SMA' else ema
                clr = C['blue'] if n_ma == 'SMA' else C['accent']
                ax_main.plot(x_idx, fn(ohlc['close'], min(9,len(ohlc))).values,
                             color=clr, lw=1.3, linestyle='--', alpha=0.85, label=f'{n_ma}(9)')

            step  = max(1, len(ohlc)//8)
            ticks = list(range(0,len(ohlc),step))
            ax_main.set_xticks(ticks)
            ax_main.set_xticklabels([ohlc.index[i].strftime('%H:%M:%S') for i in ticks],
                                     rotation=45, ha='right', color=C['muted'], fontsize=6)
            ax_main.set_xlim(-0.5, len(ohlc)-0.5)

            # Currency Y-axis
            ax_main.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x,_: f"{ccy}{x:,.0f}" if x>=1000 else f"{ccy}{x:.2f}"))

            latest    = self.live_store.get_latest_price(ticker)
            price_str = f"  {fmt_price(latest, ccy)}" if latest else ""
            ax_main.set_title(f"Live  {ticker}{price_str}  [{resample}]",
                               color=C['white'], fontsize=11, fontweight='bold')

            handles, lbls = ax_main.get_legend_handles_labels()
            if handles:
                ax_main.legend(loc='upper left', facecolor=C['bg3'], edgecolor=C['border'],
                               labelcolor=C['white'], fontsize=6)

            if show_vol and 'volume' in ohlc.columns:
                ax_vol = self.live_fig.add_subplot(gs[row_i]); row_i += 1
                style_ax(ax_vol, ylabel='Vol')
                vc = [C['green'] if r.close>=r.open else C['red'] for r in ohlc.itertuples()]
                ax_vol.bar(x_idx, ohlc['volume'].values, color=vc, alpha=0.7, width=0.8)
                ax_vol.set_xlim(-0.5, len(ohlc)-0.5)
                ax_vol.tick_params(labelbottom=False)

            for ind_name in active_inds:
                ax_i = self.live_fig.add_subplot(gs[row_i]); row_i += 1
                style_ax(ax_i)
                ax_i.set_xlim(-0.5, len(ohlc)-0.5)

                if ind_name == 'RSI' and len(ohlc) >= 14:
                    rv = Rsi(ohlc['close'], period=min(14,len(ohlc)))
                    ax_i.plot(x_idx, rv.values, color=C['purple'], lw=1.5)
                    ax_i.axhline(70, color=C['red'],   linestyle='--', lw=0.9, alpha=0.7)
                    ax_i.axhline(30, color=C['green'],  linestyle='--', lw=0.9, alpha=0.7)
                    ax_i.fill_between(x_idx, 70,100, alpha=0.07, color=C['red'])
                    ax_i.fill_between(x_idx, 0, 30,  alpha=0.07, color=C['green'])
                    ax_i.set_ylim(0,100); ax_i.set_ylabel('RSI', color=C['purple'], fontsize=7)

                elif ind_name == 'MACD' and len(ohlc) >= 26:
                    mc, sig, hist = macd(ohlc['close'],12,26,9)
                    ax_i.plot(x_idx, mc.values,  color=C['blue'],   lw=1.2, label='MACD')
                    ax_i.plot(x_idx, sig.values, color=C['accent'],  lw=1.2, label='Sig')
                    ch = [C['green'] if v>=0 else C['red'] for v in hist.values]
                    ax_i.bar(x_idx, hist.values, color=ch, alpha=0.6, width=0.8)
                    ax_i.axhline(0, color=C['muted'], lw=0.5, alpha=0.4)
                    ax_i.set_ylabel('MACD', color=C['blue'], fontsize=7)
                    ax_i.legend(fontsize=5, facecolor=C['bg3'], edgecolor=C['border'], labelcolor=C['white'])

                elif ind_name == 'Stochastic' and len(ohlc) >= 14:
                    tmp = ohlc.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close'})
                    k,d = stochastic(tmp, k_period=min(14,len(ohlc)))
                    ax_i.plot(x_idx, k.values, color=C['cyan'],  lw=1.2, label='%K')
                    ax_i.plot(x_idx, d.values, color=C['accent'], lw=1.2, label='%D')
                    ax_i.axhline(80, color=C['red'],  linestyle='--', lw=0.8, alpha=0.7)
                    ax_i.axhline(20, color=C['green'], linestyle='--', lw=0.8, alpha=0.7)
                    ax_i.set_ylim(0,100); ax_i.set_ylabel('Stoch', color=C['cyan'], fontsize=7)
                    ax_i.legend(fontsize=5, facecolor=C['bg3'], edgecolor=C['border'], labelcolor=C['white'])

                ax_i.set_xticks(ticks)
                ax_i.set_xticklabels([ohlc.index[i].strftime('%H:%M:%S') for i in ticks],
                                      rotation=45, ha='right', color=C['muted'], fontsize=6)

        try: self.live_canvas_widget.draw_idle()
        except Exception: pass

        self._update_sparklines()
        self._update_tick_log(ticker, ccy)

    def _update_sparklines(self):
        for ticker, ax in self.price_spark_axes.items():
            ax.clear(); ax.set_facecolor(C['bg2']); ax.axis('off')
            ticks = self.live_store.get_tick_log(ticker, n=30)
            if len(ticks) >= 2:
                prices = [t['price'] for t in ticks]
                color  = C['green'] if prices[-1] >= prices[0] else C['red']
                ax.plot(prices, color=color, lw=1, alpha=0.8)
                ax.fill_between(range(len(prices)), min(prices), prices, alpha=0.2, color=color)
        try: self._spark_canvas.draw_idle()
        except Exception: pass

    def _update_tick_log(self, ticker, ccy='$'):
        ticks = self.live_store.get_tick_log(ticker, n=20)
        self._tick_log_text.config(state=tk.NORMAL)
        self._tick_log_text.delete('1.0', tk.END)
        for t in reversed(ticks):
            self._tick_log_text.insert(tk.END,
                f"{t['time'].strftime('%H:%M:%S')}  {fmt_price(t['price'], ccy)}\n")
        self._tick_log_text.config(state=tk.DISABLED)

    def _refresh_price_labels(self):
        for ticker, lbl in self.price_labels.items():
            price = self.live_store.get_latest_price(ticker)
            prev  = self.live_store.get_prev_price(ticker)
            _, ccy, _, _ = normalize_ticker(ticker, 'Auto')
            if price is not None:
                color = C['green'] if (prev is None or price >= prev) else C['red']
                lbl.config(text=fmt_price(price, ccy, decimals=2), fg=color)
        self.root.after(1500, self._refresh_price_labels)

    # ═══════════════════════════════════════════════════════════
    # TAB 3  ─  MULTI-TICKER
    # ═══════════════════════════════════════════════════════════
    def _build_multi_tab(self):
        top = tk.Frame(self.multi_tab, bg=C['bg2'], height=50)
        top.pack(fill=tk.X, padx=4, pady=(4,0))
        top.pack_propagate(False)

        tk.Label(top, text="TICKERS:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=8)
        self.multi_tickers_var = tk.StringVar(
            value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, AAPL, MSFT, BTC-USD, NVDA")
        tk.Entry(top, textvariable=self.multi_tickers_var, font=('Consolas',9),
                 bg=C['bg3'], fg=C['white'], insertbackground=C['accent'],
                 relief=tk.FLAT, bd=3, width=54).pack(side=tk.LEFT, padx=4, ipady=3)

        tk.Label(top, text="DAYS:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(8,4))
        self.multi_days_var = tk.StringVar(value="30")
        tk.Entry(top, textvariable=self.multi_days_var, font=('Consolas',9),
                 bg=C['bg3'], fg=C['white'], relief=tk.FLAT, width=5).pack(side=tk.LEFT, ipady=3)

        tk.Label(top, text="IND:", font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(8,4))
        self.multi_ind_var = tk.StringVar(value="RSI")
        ttk.Combobox(top, textvariable=self.multi_ind_var,
                     values=["None","RSI","MACD","ATR","Bollinger Bands","Stochastic","ADX"],
                     width=14, font=('Consolas',9)).pack(side=tk.LEFT, ipady=2)

        tk.Button(top, text="📈 LOAD ALL", command=self._load_multi_tickers,
                  bg=C['accent'], fg=C['bg'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=8, ipady=3)

        self.multi_chart_frame = tk.Frame(self.multi_tab, bg=C['bg'])
        self.multi_chart_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        tk.Label(self.multi_chart_frame,
                 text="Enter tickers → Load All\n\n"
                      "Mix Indian and Global:\n"
                      "RELIANCE.NS, TCS.NS, AAPL, BTC-USD",
                 font=('Consolas',13,'bold'), bg=C['bg'], fg=C['accent']).pack(expand=True)

    def _load_multi_tickers(self):
        raw     = self.multi_tickers_var.get()
        tickers = [t.strip() for t in raw.replace(',', ' ').split() if t.strip()]
        if not tickers:
            messagebox.showwarning("Multi","Enter at least one ticker."); return
        try: days = int(self.multi_days_var.get())
        except ValueError: days = 30

        indicator = self.multi_ind_var.get()
        end       = datetime.now()
        start     = end - timedelta(days=days)

        for w in self.multi_chart_frame.winfo_children(): w.destroy()
        loading = tk.Label(self.multi_chart_frame, text="Fetching all tickers…",
                           font=('Consolas',13,'bold'), bg=C['bg'], fg=C['accent'])
        loading.pack(expand=True); self.root.update(); loading.destroy()

        n        = len(tickers)
        cols     = min(4, n)
        rows     = (n + cols - 1) // cols
        show_ind = indicator not in ("None","Bollinger Bands")
        fig_h    = max(4, rows * (5 if show_ind else 3.5))

        fig = Figure(figsize=(cols*4.2, fig_h), facecolor=C['bg'], dpi=90)

        for idx, ticker in enumerate(tickers):
            # Normalize each ticker
            yf_t, ccy, exch, disp = normalize_ticker(ticker, 'Auto')
            try:   data = fetch_data(yf_t, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            except Exception: data = None

            row_i = idx // cols
            col_i = idx %  cols

            if show_ind:
                gs  = fig.add_gridspec(rows*2, cols, hspace=0.55, wspace=0.35,
                                       height_ratios=([3,1]*rows))
                ax_p = fig.add_subplot(gs[row_i*2,   col_i])
                ax_i = fig.add_subplot(gs[row_i*2+1, col_i])
            else:
                gs   = fig.add_gridspec(rows, cols, hspace=0.5, wspace=0.35)
                ax_p = fig.add_subplot(gs[row_i, col_i])
                ax_i = None

            for ax in ([ax_p] + ([ax_i] if ax_i else [])):
                style_ax(ax)

            if data is None or data.empty:
                ax_p.text(0.5,0.5,"No data",ha='center',va='center',
                          color=C['red'],transform=ax_p.transAxes,fontsize=9)
                ax_p.set_title(f"{disp} [{exch}]", color=C['white'], fontsize=8, fontweight='bold')
                continue

            cfg   = PERIOD_SETTINGS["1M"]
            d_idx = draw_candles(ax_p, data, width=0.6)
            xr    = list(range(len(data)))

            # Currency y-axis
            ax_p.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x,_,c=ccy: f"{c}{x:,.0f}" if x>=1000 else f"{c}{x:.0f}"))

            if indicator == "Bollinger Bands":
                bu,bm,bl = bb_bands(data['Close'], period=cfg['bb'])
                ax_p.plot(xr, bu.values, color=C['gold'], linestyle='--', lw=0.7, alpha=0.7)
                ax_p.plot(xr, bm.values, color=C['cyan'], linestyle='-.', lw=0.6, alpha=0.6)
                ax_p.plot(xr, bl.values, color=C['gold'], linestyle='--', lw=0.7, alpha=0.7)
                ax_p.fill_between(xr, bu.values, bl.values, alpha=0.06, color=C['gold'])

            last = data['Close'].iloc[-1]
            pct  = ((data['Close'].iloc[-1]/data['Close'].iloc[0])-1)*100
            clr  = C['green'] if pct >= 0 else C['red']
            ax_p.set_title(f"{disp}  {fmt_price(last,ccy)}  ({pct:+.1f}%)",
                           color=clr, fontsize=7, fontweight='bold', pad=3)

            step = max(1, len(data)//4)
            ax_p.set_xticks(range(0,len(data),step))
            ax_p.set_xticklabels([data.index[i].strftime('%d/%m') for i in range(0,len(data),step)],
                                  rotation=30, ha='right', fontsize=5, color=C['muted'])

            if ax_i is not None:
                if indicator == 'RSI':
                    rv = Rsi(data['Close'], period=cfg['rsi'])
                    ax_i.plot(xr, rv.values, color=C['purple'], lw=1)
                    ax_i.axhline(70, color=C['red'],  linestyle='--', lw=0.7, alpha=0.6)
                    ax_i.axhline(30, color=C['green'], linestyle='--', lw=0.7, alpha=0.6)
                    ax_i.set_ylim(0,100); ax_i.set_title('RSI', color=C['purple'], fontsize=7)
                elif indicator == 'MACD':
                    mc,sig,hist = macd(data['Close'])
                    ax_i.plot(xr, mc.values,  color=C['blue'],  lw=0.9)
                    ax_i.plot(xr, sig.values, color=C['accent'], lw=0.9)
                    ax_i.bar(xr, hist.values,
                             color=[C['green'] if v>=0 else C['red'] for v in hist.values],
                             alpha=0.6, width=0.8)
                    ax_i.axhline(0, color=C['muted'], lw=0.4, alpha=0.4)
                    ax_i.set_title('MACD', color=C['blue'], fontsize=7)
                elif indicator == 'ATR':
                    av = atr(data, period=cfg['atr'])
                    ax_i.plot(xr, av.values, color=C['accent'], lw=0.9)
                    ax_i.fill_between(xr, 0, av.values, alpha=0.12, color=C['accent'])
                    ax_i.set_title('ATR', color=C['accent'], fontsize=7)
                elif indicator == 'Stochastic':
                    k,d = stochastic(data, k_period=cfg['stoch'][0])
                    ax_i.plot(xr, k.values, color=C['cyan'],  lw=0.9, label='%K')
                    ax_i.plot(xr, d.values, color=C['accent'], lw=0.9, label='%D')
                    ax_i.axhline(80, color=C['red'],  linestyle='--', lw=0.7, alpha=0.6)
                    ax_i.axhline(20, color=C['green'], linestyle='--', lw=0.7, alpha=0.6)
                    ax_i.set_ylim(0,100); ax_i.set_title('Stoch', color=C['cyan'], fontsize=7)
                elif indicator == 'ADX':
                    adx_v,_,_ = adx(data, period=cfg['adx'])
                    ax_i.plot(xr, adx_v.values, color=C['gold'], lw=0.9)
                    ax_i.axhline(25, color=C['muted'], linestyle=':', lw=0.6, alpha=0.6)
                    ax_i.set_title('ADX', color=C['gold'], fontsize=7)
                style_ax(ax_i)

        scroll_frame = tk.Frame(self.multi_chart_frame, bg=C['bg'])
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        vs = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL,   bg=C['bg3'], troughcolor=C['bg2'])
        hs = tk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL, bg=C['bg3'], troughcolor=C['bg2'])
        vs.pack(side=tk.RIGHT,  fill=tk.Y)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        cv = tk.Canvas(scroll_frame, bg=C['bg'],
                       yscrollcommand=vs.set, xscrollcommand=hs.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vs.config(command=cv.yview); hs.config(command=cv.xview)
        cw = FigureCanvasTkAgg(fig, cv)
        cw.draw()
        wid = cw.get_tk_widget()
        cv.create_window((0,0), window=wid, anchor='nw')
        wid.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))

    # ═══════════════════════════════════════════════════════════
    # TAB 4  ─  WATCHLIST
    # ═══════════════════════════════════════════════════════════
    def _build_watchlist_tab(self):
        top = tk.Frame(self.watch_tab, bg=C['bg2'], height=46)
        top.pack(fill=tk.X, padx=4, pady=(4,0))
        top.pack_propagate(False)
        tk.Label(top, text="WATCHLIST", font=('Consolas',11,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(side=tk.LEFT, padx=10)
        tk.Button(top, text="↺ Refresh Prices", command=self._refresh_watchlist_prices,
                  bg=C['bg3'], fg=C['cyan'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=8, ipady=3)
        tk.Button(top, text="🗑 Clear All", command=self._clear_watchlist,
                  bg=C['bg3'], fg=C['red'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=4, ipady=3)

        # Quick-add Indian watchlist
        tk.Frame(top, width=1, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        tk.Button(top, text="🇮🇳 Add Nifty50 Defaults",
                  command=self._add_nifty_defaults,
                  bg=C['bg3'], fg=C['teal'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=4, ipady=3)

        self.watch_list_frame = tk.Frame(self.watch_tab, bg=C['bg'])
        self.watch_list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._refresh_watchlist_panel()

    def _add_nifty_defaults(self):
        nifty_top10 = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS','ICICIBANK.NS',
                        'SBIN.NS','WIPRO.NS','BAJFINANCE.NS','KOTAKBANK.NS','LT.NS']
        for t in nifty_top10:
            if t not in self.watchlist:
                self.watchlist.append(t)
        self._save_watchlist()
        self._refresh_watchlist_panel()
        self._set_status("Added Nifty50 top-10 to watchlist")

    def _refresh_watchlist_panel(self):
        for w in self.watch_list_frame.winfo_children(): w.destroy()

        hdr = tk.Frame(self.watch_list_frame, bg=C['bg3'])
        hdr.pack(fill=tk.X, padx=2, pady=(0,2))
        for txt, w in [("Ticker",14),("Exch",6),("Last",12),("Chg%",10),("52W High",12),("52W Low",12),("",12)]:
            tk.Label(hdr, text=txt, font=('Consolas',9,'bold'),
                     bg=C['bg3'], fg=C['accent'], width=w, anchor='w').pack(side=tk.LEFT, padx=4, pady=4)

        self._watch_rows = {}
        for ticker in self.watchlist:
            _, ccy, exch, disp = normalize_ticker(ticker, 'Auto')
            row_f = tk.Frame(self.watch_list_frame, bg=C['bg2'])
            row_f.pack(fill=tk.X, padx=2, pady=1)
            labels = {}
            tk.Label(row_f, text=disp, font=('Consolas',9,'bold'),
                     bg=C['bg2'], fg=C['white'], width=14, anchor='w').pack(side=tk.LEFT, padx=4, pady=3)
            tk.Label(row_f, text=exch, font=('Consolas',8),
                     bg=C['bg2'], fg=C['teal'], width=6, anchor='w').pack(side=tk.LEFT, padx=2)
            for key, wd in [("last",12),("chg",10),("high52",12),("low52",12)]:
                lbl = tk.Label(row_f, text="—", font=('Consolas',9),
                               bg=C['bg2'], fg=C['white'], width=wd, anchor='w')
                lbl.pack(side=tk.LEFT, padx=4, pady=3)
                labels[key] = lbl
            labels['ccy'] = ccy
            tk.Button(row_f, text="✕", font=('Consolas',8), bg=C['bg2'], fg=C['red'],
                      relief=tk.FLAT, cursor='hand2',
                      command=lambda t=ticker: self._remove_from_watchlist(t)
                      ).pack(side=tk.LEFT, padx=4)
            tk.Button(row_f, text="→ Chart", font=('Consolas',8), bg=C['bg2'], fg=C['cyan'],
                      relief=tk.FLAT, cursor='hand2',
                      command=lambda t=ticker, e=exch: self._load_from_watchlist(t, e)
                      ).pack(side=tk.LEFT, padx=4)
            self._watch_rows[ticker] = labels

    def _refresh_watchlist_prices(self):
        def _fetch():
            for ticker in list(self.watchlist):
                yf_t, ccy, exch, _ = normalize_ticker(ticker, 'Auto')
                try:
                    d = fetch_data(yf_t,
                                   (datetime.now()-timedelta(days=365)).strftime('%Y-%m-%d'),
                                   datetime.now().strftime('%Y-%m-%d'))
                    if d is None or d.empty: continue
                    last  = float(d['Close'].iloc[-1])
                    prev  = float(d['Close'].iloc[-2]) if len(d) > 1 else last
                    chg   = (last/prev-1)*100
                    h52   = float(d['High'].max())
                    l52   = float(d['Low'].min())
                    if ticker in self._watch_rows:
                        lab = self._watch_rows[ticker]
                        clr = C['green'] if chg >= 0 else C['red']
                        c   = lab.get('ccy', '$')
                        self.root.after(0, lambda l=lab,la=last,ch=chg,h=h52,lo=l52,cl2=clr,cy=c: (
                            l['last'].config(text=fmt_price(la,cy), fg=C['white']),
                            l['chg'].config(text=f"{ch:+.2f}%", fg=cl2),
                            l['high52'].config(text=fmt_price(h,cy), fg=C['muted']),
                            l['low52'].config(text=fmt_price(lo,cy), fg=C['muted']),
                        ))
                except Exception:
                    pass
        threading.Thread(target=_fetch, daemon=True).start()

    def _remove_from_watchlist(self, ticker):
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)
            self._save_watchlist()
            self._refresh_watchlist_panel()

    def _clear_watchlist(self):
        self.watchlist = []
        self._save_watchlist()
        self._refresh_watchlist_panel()

    def _load_from_watchlist(self, ticker, exchange='Auto'):
        raw = ticker.replace('.NS','').replace('.BO','')
        self.ticker_var.set(raw)
        self.market_var.set('NSE' if exchange == 'NSE' else
                            'BSE' if exchange == 'BSE' else 'Auto')
        # Pre-fill the ticker entry with the full yf ticker
        self.ticker_var.set(ticker)
        self.nb.select(0)
        self.fetch_and_plot()


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def launch_dashboard():
    import matplotlib
    matplotlib.use("TkAgg")
    root = tk.Tk()
    app  = QuantDashboard(root)
    root.mainloop()


launch_dashboard()
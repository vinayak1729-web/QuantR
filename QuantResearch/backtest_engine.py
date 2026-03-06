"""
QuantResearch Backtest Engine + GUI Tab  v2
============================================
Fixes:  PERIOD 1Y tokenizer bug
Added:  Pre-plot data before simulation, visual trade book,
        monthly snapshot panels, equity heatmap
"""

from __future__ import annotations
import re, math, os, threading, csv
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# ── sibling imports ────────────────────────────────────────
try:
    from .indicators import (
        Rsi, RVWAP, macd as _macd_fn, bb_bands, atr as _atr_fn,
        sma as _sma_fn, ema as _ema_fn, demma, temma,
        stochastic, williams_r, obv as _obv_fn, parabolic_sar,
        adx as _adx_fn, slope as _slope_fn, fetch_data,
    )
    from .dashboard import normalize_ticker, fmt_price, fmt_vol, C, style_ax
except ImportError:
    from .indicators import (
        Rsi, RVWAP, macd as _macd_fn, bb_bands, atr as _atr_fn,
        sma as _sma_fn, ema as _ema_fn, demma, temma,
        stochastic, williams_r, obv as _obv_fn, parabolic_sar,
        adx as _adx_fn, slope as _slope_fn, fetch_data,
    )
    try:
        from .dashboard import normalize_ticker, fmt_price, fmt_vol, C, style_ax
    except ImportError:
        def normalize_ticker(r, m="Auto"):
            t = r.strip().upper()
            NSE = {'RELIANCE','TCS','INFY','HDFCBANK','ICICIBANK','SBIN','WIPRO',
                   'MARUTI','TATAMOTORS','BAJFINANCE','KOTAKBANK','LT','AXISBANK',
                   'SUNPHARMA','TATASTEEL','TECHM','NESTLEIND','TITAN','BHARTIARTL',
                   'HINDUNILVR','ASIANPAINT','NTPC','ONGC','POWERGRID','HCLTECH',
                   'ADANIENT','ADANIPORTS','JSWSTEEL','CIPLA','DRREDDY','BAJAJ-AUTO'}
            if t.endswith('.NS'): return t,'₹','NSE',t.replace('.NS','')
            if t.endswith('.BO'): return t,'₹','BSE',t.replace('.BO','')
            if m=='NSE': return f"{t}.NS",'₹','NSE',t
            if m=='BSE': return f"{t}.BO",'₹','BSE',t
            if m=='US': return t,'$','US',t
            if m=='CRYPTO': return f"{t}-USD",'$','Crypto',t
            if t in NSE: return f"{t}.NS",'₹','NSE',t
            return t,'$','US',t
        def fmt_price(p,c='$',d=2):
            if p is None or (isinstance(p,float) and math.isnan(p)): return "—"
            return f"{c}{p:,.{d}f}"
        def fmt_vol(v):
            if v is None: return "—"
            if v>=1e7: return f"{v/1e7:.2f}Cr"
            if v>=1e6: return f"{v/1e6:.1f}M"
            if v>=1e3: return f"{v/1e3:.0f}K"
            return str(int(v))
        C = {'bg':'#0a0e14','bg2':'#111820','bg3':'#182030','border':'#1e3048',
             'accent':'#ffb347','accent2':'#ffd580','green':'#00e676','red':'#ff1744',
             'blue':'#29b6f6','purple':'#ce93d8','white':'#e8edf3','muted':'#607080',
             'gold':'#ffc107','cyan':'#00e5ff','teal':'#1de9b6','orange':'#ff6d00'}
        def style_ax(ax, title="", ylabel="", fontsize=9):
            ax.set_facecolor(C['bg']); ax.tick_params(colors=C['muted'],labelsize=6)
            ax.grid(True,alpha=0.10,color='#2a3f55',linestyle='--')
            for s in ax.spines.values(): s.set_color(C['border'])
            if title: ax.set_title(title,color=C['white'],fontsize=fontsize,fontweight='bold',pad=5)
            if ylabel: ax.set_ylabel(ylabel,color=C['muted'],fontsize=7)


# ═══════════════════════════════════════════════════════════════════
# 1. TOKENIZER  —  FIX: handle "1Y" "6M" "30D" as single IDENT
# ═══════════════════════════════════════════════════════════════════
class TT(Enum):
    BACKTEST=auto(); MARKET=auto(); TICKER=auto(); PERIOD=auto()
    USE=auto(); BUY=auto(); SELL=auto(); WHEN=auto()
    CAPITAL=auto(); POSITION_SIZE=auto(); STOP_LOSS=auto()
    TAKE_PROFIT=auto(); COMMISSION=auto(); SLIPPAGE=auto()
    AND=auto(); OR=auto(); NOT=auto()
    CROSSES_ABOVE=auto(); CROSSES_BELOW=auto()
    GT=auto(); LT=auto(); GTE=auto(); LTE=auto(); EQ=auto(); NEQ=auto()
    NUMBER=auto(); PERCENT=auto(); STRING=auto(); IDENT=auto()
    LPAREN=auto(); RPAREN=auto(); COMMA=auto()
    NEWLINE=auto(); EOF=auto()

@dataclass
class Token:
    type: TT; value: Any; line: int = 0

_KW = {
    'BACKTEST':TT.BACKTEST,'MARKET':TT.MARKET,'TICKER':TT.TICKER,
    'PERIOD':TT.PERIOD,'USE':TT.USE,'BUY':TT.BUY,'SELL':TT.SELL,
    'WHEN':TT.WHEN,'CAPITAL':TT.CAPITAL,'POSITION_SIZE':TT.POSITION_SIZE,
    'STOP_LOSS':TT.STOP_LOSS,'TAKE_PROFIT':TT.TAKE_PROFIT,
    'COMMISSION':TT.COMMISSION,'SLIPPAGE':TT.SLIPPAGE,
    'AND':TT.AND,'OR':TT.OR,'NOT':TT.NOT,
    'CROSSES_ABOVE':TT.CROSSES_ABOVE,'CROSSES_BELOW':TT.CROSSES_BELOW,
}

# ── FIX: PERIOD_VAL pattern catches "1Y", "6M", "30D", "2W" as one token ──
_TSPEC = [
    ('CMT',       r'#[^\n]*'),
    ('STR',       r'"[^"]*"'),
    ('PCT',       r'\d+(?:\.\d+)?%'),
    ('PERIOD_VAL',r'\d+[YyMmDdWw]'),          # ← NEW: "1Y" "6M" "30D" etc
    ('NUM',       r'\d+(?:\.\d+)?'),
    ('GTE',       r'>='), ('LTE', r'<='), ('NEQ', r'!='), ('EQ', r'=='),
    ('GT',        r'>'),  ('LT',  r'<'),
    ('LP',        r'\('), ('RP',  r'\)'), ('COM', r','),
    ('NL',        r'\n'), ('SK',  r'[ \t]+'),
    ('ID',        r'[A-Za-z_][A-Za-z0-9_]*'),
    ('MM',        r'.'),
]
_TRE = re.compile('|'.join(f'(?P<{n}>{p})' for n,p in _TSPEC))

def tokenize(src: str) -> list[Token]:
    toks=[]; ln=1
    for m in _TRE.finditer(src):
        k,v = m.lastgroup, m.group()
        if k in ('CMT','SK'): continue
        if k=='NL': ln+=1; continue
        if k=='STR':         toks.append(Token(TT.STRING, v.strip('"'), ln))
        elif k=='PCT':       toks.append(Token(TT.PERCENT, float(v.rstrip('%')), ln))
        elif k=='PERIOD_VAL':toks.append(Token(TT.IDENT, v.upper(), ln))   # ← "1Y" → IDENT "1Y"
        elif k=='NUM':
            toks.append(Token(TT.NUMBER, float(v) if '.' in v else int(v), ln))
        elif k=='ID':
            u=v.upper(); toks.append(Token(_KW.get(u,TT.IDENT), u, ln))
        elif k in ('GT','LT','GTE','LTE','EQ','NEQ'):
            toks.append(Token(TT[k], v, ln))
        elif k=='LP':  toks.append(Token(TT.LPAREN, v, ln))
        elif k=='RP':  toks.append(Token(TT.RPAREN, v, ln))
        elif k=='COM': toks.append(Token(TT.COMMA, v, ln))
        elif k=='MM' and v.strip():
            raise SyntaxError(f"Line {ln}: unexpected char '{v}'")
    toks.append(Token(TT.EOF, None, ln))
    return toks


# ═══════════════════════════════════════════════════════════════════
# 2. AST NODES
# ═══════════════════════════════════════════════════════════════════
@dataclass
class IndicatorDecl:
    name: str; params: tuple = ()
@dataclass
class ValueNode:
    kind: str; name: str=''; params: tuple=(); number: float=0.0
@dataclass
class CompareNode:
    left: ValueNode; op: str; right: ValueNode
@dataclass
class CrossNode:
    left: ValueNode; direction: str; right: ValueNode
@dataclass
class LogicNode:
    op: str; children: list
@dataclass
class NotNode:
    child: Any
@dataclass
class Strategy:
    name:str="Unnamed Strategy"; market:str="Auto"; ticker:str=""
    period_str:str="1Y"; period_days:int=365
    indicators:list=field(default_factory=list)
    buy_cond:Any=None; sell_cond:Any=None
    capital:float=100_000; position_pct:float=100.0
    stop_loss_pct:float=0.0; take_profit_pct:float=0.0
    commission_pct:float=0.1; slippage_pct:float=0.0


# ═══════════════════════════════════════════════════════════════════
# 3. PARSER  —  FIX: PERIOD now reads IDENT directly ("1Y" is one token)
# ═══════════════════════════════════════════════════════════════════
class Parser:
    def __init__(self, toks): self.t=toks; self.p=0
    def _c(self): return self.t[min(self.p,len(self.t)-1)]
    def _e(self, exp=None):
        tok=self._c()
        if exp and tok.type!=exp:
            raise SyntaxError(f"Line {tok.line}: expected {exp.name}, got {tok.type.name} ('{tok.value}')")
        self.p+=1; return tok
    def _at(self,*tt): return self._c().type in tt
    def _ei(self,tt):
        if self._c().type==tt: return self._e()
        return None

    @staticmethod
    def _parse_period(s):
        m=re.match(r'^(\d+)(Y|M|D|W)$', s.upper().strip())
        if not m: raise ValueError(f"Invalid period '{s}'. Use e.g. 1Y, 6M, 30D, 2W")
        n,u=int(m.group(1)),m.group(2)
        return {'Y':365,'M':30,'W':7,'D':1}[u]*n

    def parse(self)->Strategy:
        s=Strategy()
        while not self._at(TT.EOF):
            t=self._c()
            if t.type==TT.BACKTEST: self._e(); s.name=self._e(TT.STRING).value
            elif t.type==TT.MARKET: self._e(); s.market=self._e(TT.IDENT).value
            elif t.type==TT.TICKER: self._e(); s.ticker=self._e(TT.IDENT).value
            elif t.type==TT.PERIOD:
                self._e()
                # FIX: accept either IDENT("1Y") or NUMBER+IDENT fallback
                tok = self._c()
                if tok.type == TT.IDENT:
                    self._e()
                    s.period_str = tok.value
                elif tok.type == TT.NUMBER:
                    num_tok = self._e()
                    unit_tok = self._e(TT.IDENT)
                    s.period_str = f"{int(num_tok.value)}{unit_tok.value}"
                else:
                    raise SyntaxError(f"Line {tok.line}: expected period like 1Y/6M/30D, got {tok.type.name}")
                s.period_days = self._parse_period(s.period_str)
            elif t.type==TT.USE: self._e(); s.indicators.append(self._pdecl())
            elif t.type==TT.BUY: self._e(); self._e(TT.WHEN); s.buy_cond=self._pcond()
            elif t.type==TT.SELL: self._e(); self._e(TT.WHEN); s.sell_cond=self._pcond()
            elif t.type==TT.CAPITAL: self._e(); s.capital=float(self._e(TT.NUMBER).value)
            elif t.type==TT.POSITION_SIZE: self._e(); s.position_pct=self._e(TT.PERCENT).value
            elif t.type==TT.STOP_LOSS: self._e(); s.stop_loss_pct=self._e(TT.PERCENT).value
            elif t.type==TT.TAKE_PROFIT: self._e(); s.take_profit_pct=self._e(TT.PERCENT).value
            elif t.type==TT.COMMISSION: self._e(); s.commission_pct=self._e(TT.PERCENT).value
            elif t.type==TT.SLIPPAGE: self._e(); s.slippage_pct=self._e(TT.PERCENT).value
            else: self._e()
        return s

    def _pdecl(self):
        nm=self._e(TT.IDENT).value; pr=()
        if self._ei(TT.LPAREN): pr=self._pnums(); self._e(TT.RPAREN)
        return IndicatorDecl(nm,pr)
    def _pnums(self):
        ns=[]
        if self._at(TT.NUMBER):
            ns.append(self._e(TT.NUMBER).value)
            while self._ei(TT.COMMA): ns.append(self._e(TT.NUMBER).value)
        return tuple(ns)
    def _pcond(self):
        l=self._pterm()
        while self._at(TT.AND,TT.OR):
            op=self._e().value; r=self._pterm(); l=LogicNode(op,[l,r])
        return l
    def _pterm(self):
        if self._ei(TT.NOT): return NotNode(self._patom())
        return self._patom()
    def _patom(self):
        if self._ei(TT.LPAREN): n=self._pcond(); self._e(TT.RPAREN); return n
        return self._pcross()
    def _pcross(self):
        l=self._pval()
        if self._at(TT.CROSSES_ABOVE): self._e(); return CrossNode(l,'above',self._pval())
        if self._at(TT.CROSSES_BELOW): self._e(); return CrossNode(l,'below',self._pval())
        if self._at(TT.GT,TT.LT,TT.GTE,TT.LTE,TT.EQ,TT.NEQ):
            op=self._e().value; return CompareNode(l,op,self._pval())
        return CompareNode(l,'>',ValueNode('number',number=0))
    def _pval(self)->ValueNode:
        if self._at(TT.NUMBER): return ValueNode('number',number=float(self._e().value))
        if self._at(TT.IDENT):
            nm=self._e().value; pr=()
            if self._ei(TT.LPAREN): pr=self._pnums(); self._e(TT.RPAREN)
            if nm in ('CLOSE','OPEN','HIGH','LOW','VOLUME'):
                return ValueNode('price',name=nm)
            return ValueNode('indicator',name=nm,params=pr)
        raise SyntaxError(f"Line {self._c().line}: expected value, got {self._c().type.name}")


# ═══════════════════════════════════════════════════════════════════
# 4. INDICATOR COMPUTE
# ═══════════════════════════════════════════════════════════════════
def _c_rsi(d,p=14,**_):    return {'RSI':Rsi(d['Close'],int(p))}
def _c_macd(d,s=12,l=26,sg=9,**_):
    m,si,h=_macd_fn(d['Close'],int(s),int(l),int(sg))
    return {'MACD':m,'SIGNAL':si,'HISTOGRAM':h}
def _c_sma(d,p=20,**_):    return {'SMA':_sma_fn(d['Close'],int(p))}
def _c_ema(d,p=20,**_):    return {'EMA':_ema_fn(d['Close'],int(p))}
def _c_dema(d,p=20,**_):   return {'DEMA':demma(d['Close'],int(p))}
def _c_tema(d,p=20,**_):   return {'TEMA':temma(d['Close'],int(p))}
def _c_bb(d,p=20,**_):
    u,m,l=bb_bands(d['Close'],int(p)); return {'BB_UPPER':u,'BB_MID':m,'BB_LOWER':l}
def _c_atr(d,p=14,**_):    return {'ATR':_atr_fn(d,int(p))}
def _c_stoch(d,kp=14,dp=3,**_):
    k,dd=stochastic(d,int(kp),int(dp)); return {'STOCH_K':k,'STOCH_D':dd}
def _c_will(d,p=14,**_):   return {'WILLIAMS':williams_r(d,int(p))}
def _c_adx(d,p=14,**_):
    a,p2,m=_adx_fn(d,int(p)); return {'ADX':a,'PLUS_DI':p2,'MINUS_DI':m}
def _c_slope(d,p=14,**_):  return {'SLOPE':_slope_fn(d['Close'],int(p))}
def _c_sar(d,**_):
    s,t=parabolic_sar(d); return {'SAR':s,'SAR_TREND':t}
def _c_obv(d,**_):         return {'OBV':_obv_fn(d)}
def _c_vwap(d,p=20,**_):
    return {'VWAP':RVWAP(d['High'],d['Low'],d['Close'],d['Volume'],int(p))}

_IND_REG = {
    'RSI':_c_rsi,'MACD':_c_macd,'SMA':_c_sma,'EMA':_c_ema,
    'DEMA':_c_dema,'TEMA':_c_tema,'BB':_c_bb,'ATR':_c_atr,
    'STOCH':_c_stoch,'STOCHASTIC':_c_stoch,'WILLIAMS':_c_will,
    'ADX':_c_adx,'SLOPE':_c_slope,'SAR':_c_sar,'PARABOLIC_SAR':_c_sar,
    'OBV':_c_obv,'VWAP':_c_vwap,'RVWAP':_c_vwap,
}
_ALIAS = {
    'BB_UPPER':'BB','BB_MID':'BB','BB_LOWER':'BB',
    'STOCH_K':'STOCH','STOCH_D':'STOCH',
    'SIGNAL':'MACD','HISTOGRAM':'MACD',
    'PLUS_DI':'ADX','MINUS_DI':'ADX','SAR_TREND':'SAR',
}

def compute_indicators(data, strat):
    comp={}; needed=set()
    for d in strat.indicators: needed.add(d.name)
    def _walk(n):
        if n is None: return
        if isinstance(n,ValueNode) and n.kind=='indicator': needed.add(n.name)
        elif isinstance(n,(CompareNode,CrossNode)): _walk(n.left); _walk(n.right)
        elif isinstance(n,LogicNode):
            for c in n.children: _walk(c)
        elif isinstance(n,NotNode): _walk(n.child)
    _walk(strat.buy_cond); _walk(strat.sell_cond)
    todo={}
    for nm in needed:
        key=_ALIAS.get(nm,nm)
        if key in _IND_REG and key not in todo:
            pr=()
            for dd in strat.indicators:
                if dd.name in (key,nm): pr=dd.params; break
            todo[key]=pr
    for key,pr in todo.items():
        try: comp.update(_IND_REG[key](data,*pr))
        except Exception as e: print(f"[WARN] {key}: {e}")
    return comp


# ═══════════════════════════════════════════════════════════════════
# 5. CONDITION EVALUATOR
# ═══════════════════════════════════════════════════════════════════
def _rv(n,i,d,ind):
    if n.kind=='number': return n.number
    if n.kind=='price':
        cm={'CLOSE':'Close','OPEN':'Open','HIGH':'High','LOW':'Low','VOLUME':'Volume'}
        return float(d[cm.get(n.name,n.name)].iloc[i])
    nm=n.name
    if nm in ind:
        v=ind[nm].iloc[i]
        return float(v) if not (isinstance(v,float) and math.isnan(v)) else float('nan')
    return float('nan')

def _ec(n,i,d,ind):
    if n is None: return False
    if isinstance(n,CompareNode):
        lv,rv=_rv(n.left,i,d,ind),_rv(n.right,i,d,ind)
        if math.isnan(lv) or math.isnan(rv): return False
        return {'>':lv>rv,'<':lv<rv,'>=':lv>=rv,'<=':lv<=rv,'==':lv==rv,'!=':lv!=rv}.get(n.op,False)
    if isinstance(n,CrossNode):
        if i<1: return False
        ln2,rn=_rv(n.left,i,d,ind),_rv(n.right,i,d,ind)
        lp,rp=_rv(n.left,i-1,d,ind),_rv(n.right,i-1,d,ind)
        if any(math.isnan(x) for x in (ln2,rn,lp,rp)): return False
        return (lp<=rp and ln2>rn) if n.direction=='above' else (lp>=rp and ln2<rn)
    if isinstance(n,LogicNode):
        rs=[_ec(c,i,d,ind) for c in n.children]
        return all(rs) if n.op=='AND' else any(rs)
    if isinstance(n,NotNode): return not _ec(n.child,i,d,ind)
    return False


# ═══════════════════════════════════════════════════════════════════
# 6. TRADE
# ═══════════════════════════════════════════════════════════════════
@dataclass
class Trade:
    entry_date:Any=None; entry_price:float=0; shares:float=0
    exit_date:Any=None; exit_price:float=0; exit_reason:str=''
    pnl:float=0; pnl_pct:float=0; commission:float=0


# ═══════════════════════════════════════════════════════════════════
# 7. BACKTEST ENGINE
# ═══════════════════════════════════════════════════════════════════
@dataclass
class BacktestResult:
    strategy:Strategy; trades:list; equity_curve:pd.Series
    buy_signals:list; sell_signals:list; indicators:dict
    data:pd.DataFrame; metrics:dict; currency:str='$'; exchange:str='US'
    yf_ticker:str=''

class BacktestEngine:
    def __init__(self, strat): self.strat=strat

    def run(self)->BacktestResult:
        s=self.strat
        yf_t,ccy,exch,disp=normalize_ticker(s.ticker,s.market)
        end=datetime.now(); start=end-timedelta(days=s.period_days)
        data=fetch_data(yf_t,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'))
        if data is None or data.empty:
            # try BSE fallback
            if s.market in ('AUTO','NSE'):
                alt = s.ticker.upper()+'.BO'
                data=fetch_data(alt,start.strftime('%Y-%m-%d'),end.strftime('%Y-%m-%d'))
                if data is not None and not data.empty:
                    yf_t=alt; exch='BSE'; ccy='₹'
            if data is None or data.empty:
                raise RuntimeError(f"No data for {yf_t}. Check ticker/market.")
        ind=compute_indicators(data,s)
        cap=s.capital; pos=None; trades=[]; eq=np.full(len(data),cap)
        buys=[]; sells=[]
        cr=s.commission_pct/100; pf=s.position_pct/100
        warmup=min(60,len(data)//4)

        for i in range(len(data)):
            price=float(data['Close'].iloc[i])
            if i>=warmup:
                if pos is not None:
                    pnl_p=(price/pos.entry_price-1)*100
                    hit_sl=s.stop_loss_pct>0 and pnl_p<=-s.stop_loss_pct
                    hit_tp=s.take_profit_pct>0 and pnl_p>=s.take_profit_pct
                    sig_sell=_ec(s.sell_cond,i,data,ind)
                    if hit_sl or hit_tp or sig_sell:
                        reason='stop_loss' if hit_sl else ('take_profit' if hit_tp else 'signal')
                        cm=price*pos.shares*cr
                        gross=(price-pos.entry_price)*pos.shares
                        pos.exit_date=data.index[i]; pos.exit_price=price
                        pos.pnl=gross-cm-pos.commission
                        pos.pnl_pct=(pos.pnl/(pos.entry_price*pos.shares))*100
                        pos.exit_reason=reason; pos.commission+=cm
                        cap+=pos.entry_price*pos.shares+pos.pnl
                        trades.append(pos); sells.append(i); pos=None
                if pos is None and i>=warmup:
                    if _ec(s.buy_cond,i,data,ind):
                        alloc=cap*pf; shares=int(alloc//price) if price>0 else 0
                        if shares>0:
                            cm=price*shares*cr; cap-=price*shares+cm
                            pos=Trade(entry_date=data.index[i],entry_price=price,
                                      shares=shares,commission=cm)
                            buys.append(i)
            mtm=cap+(price*pos.shares if pos else 0)
            eq[i]=mtm

        if pos is not None:
            price=float(data['Close'].iloc[-1]); cm=price*pos.shares*cr
            gross=(price-pos.entry_price)*pos.shares
            pos.exit_date=data.index[-1]; pos.exit_price=price
            pos.pnl=gross-cm-pos.commission; pos.exit_reason='end_of_data'
            pos.pnl_pct=(pos.pnl/(pos.entry_price*pos.shares))*100
            pos.commission+=cm; cap+=pos.entry_price*pos.shares+pos.pnl
            trades.append(pos); sells.append(len(data)-1); eq[-1]=cap

        eq[:warmup]=eq[warmup] if warmup<len(eq) else s.capital
        eqs=pd.Series(eq,index=data.index)
        metrics=self._metrics(trades,eqs,s)
        return BacktestResult(s,trades,eqs,buys,sells,ind,data,metrics,ccy,exch,yf_t)

    @staticmethod
    def _metrics(trades,eq,s):
        n=len(trades)
        if n==0: return {'Total Trades':'0','Note':'No trades — conditions never triggered'}
        wins=[t for t in trades if t.pnl>0]; losses=[t for t in trades if t.pnl<=0]
        tpnl=sum(t.pnl for t in trades); tcomm=sum(t.commission for t in trades)
        gp=sum(t.pnl for t in wins) if wins else 0
        gl=sum(t.pnl for t in losses) if losses else 0
        aw=np.mean([t.pnl for t in wins]) if wins else 0
        al=np.mean([t.pnl for t in losses]) if losses else 0
        hd=[]
        for t in trades:
            if t.entry_date and t.exit_date:
                hd.append(max((pd.Timestamp(t.exit_date)-pd.Timestamp(t.entry_date)).days,1))
        ret=eq.pct_change().dropna(); ann=252
        tr=(eq.iloc[-1]/eq.iloc[0])-1
        vol=ret.std()*np.sqrt(ann) if len(ret)>1 else 0
        rf=(1+0.065)**(1/ann)-1
        sh=((ret.mean()-rf)/ret.std()*np.sqrt(ann)) if ret.std()>0 else 0
        cum=(1+ret).cumprod(); dd=(cum-cum.cummax())/cum.cummax(); mdd=dd.min()
        pfac=abs(gp/gl) if gl!=0 else float('inf')
        sw=sl_c=mw=ml=0
        for t in trades:
            if t.pnl>0: sw+=1;sl_c=0;mw=max(mw,sw)
            else: sl_c+=1;sw=0;ml=max(ml,sl_c)
        return {
            'Total Trades':str(n),'Winners':str(len(wins)),'Losers':str(len(losses)),
            'Win Rate':f"{len(wins)/n*100:.1f}%",'Net P&L':f"{tpnl:+,.2f}",
            'Total Return':f"{tr*100:+.2f}%",'Gross Profit':f"{gp:+,.2f}",
            'Gross Loss':f"{gl:+,.2f}",'Profit Factor':f"{pfac:.2f}" if pfac!=float('inf') else "∞",
            'Avg Win':f"{aw:+,.2f}",'Avg Loss':f"{al:+,.2f}",
            'Max Consec Wins':str(mw),'Max Consec Losses':str(ml),
            'Avg Hold (days)':f"{np.mean(hd):.1f}" if hd else "—",
            'Total Commission':f"{tcomm:,.2f}",
            'Sharpe Ratio':f"{sh:.2f}",'Max Drawdown':f"{mdd*100:.2f}%",
            'Volatility':f"{vol*100:.2f}%",
            'Starting Capital':f"{s.capital:,.0f}",'Final Equity':f"{eq.iloc[-1]:,.2f}",
        }

def compile_strategy(src): return Parser(tokenize(src)).parse()
def run_backtest(src): return BacktestEngine(compile_strategy(src)).run()


# ═══════════════════════════════════════════════════════════════════
# 8. EXAMPLE STRATEGIES
# ═══════════════════════════════════════════════════════════════════
EXAMPLES = {
"RSI + MACD (NSE)": """BACKTEST "RSI + MACD Crossover"
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
COMMISSION 0.1%""",

"Bollinger Bounce (NSE)": """BACKTEST "Bollinger Bounce"
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
COMMISSION 0.1%""",

"SMA Trend + ADX (US)": """BACKTEST "SMA Trend Follow"
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
COMMISSION 0.05%""",

"Stochastic (NSE)": """BACKTEST "Stochastic Reversal"
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
COMMISSION 0.1%""",

"Crypto Momentum": """BACKTEST "BTC Momentum"
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
COMMISSION 0.2%""",
}


# ═══════════════════════════════════════════════════════════════════
# 9. GUI TAB — BacktestTab  (with pre-plot + visual trade book)
# ═══════════════════════════════════════════════════════════════════
class BacktestTab:
    def __init__(self, parent: tk.Frame, set_status: Callable = None):
        self.parent = parent
        self._set_status = set_status or (lambda m: None)
        self.result: BacktestResult = None
        self._ani_id = None
        self._ani_bar = 0
        self._ani_speed = 15
        self._ani_running = False
        self._build()

    def _build(self):
        # main horizontal split
        pw = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, bg=C['bg'],
                            sashwidth=4, sashrelief=tk.FLAT)
        pw.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ═══ LEFT PANEL: editor + controls + metrics ══════════
        left = tk.Frame(pw, bg=C['bg2']); pw.add(left, width=420)

        # ── toolbar ───────────────────────────────────────────
        tb = tk.Frame(left, bg=C['bg2']); tb.pack(fill=tk.X, padx=6, pady=(6,2))
        tk.Label(tb, text="QuantQL", font=('Consolas',11,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(side=tk.LEFT)
        tk.Button(tb, text="▶ RUN", command=self._run_backtest,
                  bg=C['green'], fg=C['bg'], font=('Consolas',9,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=2, ipady=3)
        tk.Button(tb, text="⏹ Stop", command=self._stop_animation,
                  bg=C['bg3'], fg=C['red'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=2, ipady=2)
        tk.Button(tb, text="💾 CSV", command=self._export_csv,
                  bg=C['bg3'], fg=C['cyan'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=2, ipady=2)
        tk.Button(tb, text="📊 PNG", command=self._export_png,
                  bg=C['bg3'], fg=C['cyan'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.RIGHT, padx=2, ipady=2)

        # ── example + speed row ───────────────────────────────
        ef = tk.Frame(left, bg=C['bg2']); ef.pack(fill=tk.X, padx=6, pady=(2,4))
        tk.Label(ef, text="Template:", font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT)
        self._ex_var = tk.StringVar(value="RSI + MACD (NSE)")
        ttk.Combobox(ef, textvariable=self._ex_var,
                     values=list(EXAMPLES.keys()), width=20,
                     font=('Consolas',8)).pack(side=tk.LEFT, padx=3)
        tk.Button(ef, text="Load", command=self._load_example,
                  bg=C['bg3'], fg=C['teal'], font=('Consolas',8,'bold'),
                  relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT, padx=2, ipady=1)

        tk.Frame(ef, width=1, bg=C['border']).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        tk.Label(ef, text="Speed:", font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=(2,2))
        for lbl, ms in [("Slow",100),("Med",40),("Fast",12),("⚡",0)]:
            tk.Radiobutton(ef, text=lbl, variable=tk.StringVar(), value=lbl,
                           font=('Consolas',7), bg=C['bg2'], fg=C['muted'],
                           selectcolor=C['bg3'], activebackground=C['bg2'],
                           indicatoron=False, relief=tk.FLAT, width=5,
                           command=lambda m=ms: setattr(self,'_ani_speed',m)
                           ).pack(side=tk.LEFT, padx=1)

        # ── code editor ───────────────────────────────────────
        self.editor = scrolledtext.ScrolledText(
            left, wrap=tk.NONE, font=('Consolas',10),
            bg='#0d1117', fg='#e6edf3', insertbackground=C['accent'],
            selectbackground='#264f78', selectforeground=C['white'],
            relief=tk.FLAT, bd=0, padx=8, pady=8, undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,4))
        self.editor.insert('1.0', EXAMPLES["RSI + MACD (NSE)"])
        self.editor.bind('<KeyRelease>', self._on_key)

        # syntax tag colors
        for tag, clr in [('kw',C['blue']),('str',C['green']),('num',C['accent']),
                          ('pct',C['gold']),('op',C['red']),('cmt',C['muted'])]:
            self.editor.tag_configure(tag, foreground=clr)

        # compile status
        self._compile_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self._compile_var, font=('Consolas',7),
                 bg=C['bg2'], fg=C['teal'], anchor='w').pack(fill=tk.X, padx=8, pady=(0,2))

        # ── metrics panel ─────────────────────────────────────
        mf = tk.LabelFrame(left, text=" METRICS ", font=('Consolas',9,'bold'),
                           bg=C['bg2'], fg=C['accent'], bd=1, relief=tk.GROOVE)
        mf.pack(fill=tk.X, padx=6, pady=(0,6))
        self._metrics_grid = tk.Frame(mf, bg=C['bg2'])
        self._metrics_grid.pack(fill=tk.X, padx=4, pady=4)

        # ═══ RIGHT PANEL: charts + trade log ══════════════════
        right = tk.Frame(pw, bg=C['bg']); pw.add(right)

        # vertical split: charts on top, trade log on bottom
        rpw = tk.PanedWindow(right, orient=tk.VERTICAL, bg=C['bg'],
                             sashwidth=3, sashrelief=tk.FLAT)
        rpw.pack(fill=tk.BOTH, expand=True)

        # chart area
        self._chart_frame = tk.Frame(rpw, bg=C['bg2'])
        rpw.add(self._chart_frame, height=500)
        self._show_placeholder()

        # trade log area
        log_outer = tk.Frame(rpw, bg=C['bg2'])
        rpw.add(log_outer, height=200)

        log_tb = tk.Frame(log_outer, bg=C['bg2'])
        log_tb.pack(fill=tk.X, padx=4, pady=(4,2))
        tk.Label(log_tb, text="TRADE BOOK", font=('Consolas',9,'bold'),
                 bg=C['bg2'], fg=C['accent']).pack(side=tk.LEFT)
        self._trade_count_var = tk.StringVar(value="")
        tk.Label(log_tb, textvariable=self._trade_count_var, font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted']).pack(side=tk.LEFT, padx=8)
        self._trade_summary_var = tk.StringVar(value="")
        tk.Label(log_tb, textvariable=self._trade_summary_var, font=('Consolas',8,'bold'),
                 bg=C['bg2'], fg=C['gold']).pack(side=tk.RIGHT, padx=8)

        # treeview
        cols = ('#','entry_date','exit_date','entry_px','exit_px','shares','pnl','pnl_pct','comm','reason')
        self._tree = ttk.Treeview(log_outer, columns=cols, show='headings', height=8,
                                   style='BT.Treeview')
        hdrs = {'#':'#','entry_date':'Entry Date','exit_date':'Exit Date',
                'entry_px':'Entry Price','exit_px':'Exit Price','shares':'Shares',
                'pnl':'P&L','pnl_pct':'Return %','comm':'Commission','reason':'Exit Reason'}
        widths = {'#':30,'entry_date':90,'exit_date':90,'entry_px':85,'exit_px':85,
                  'shares':55,'pnl':95,'pnl_pct':65,'comm':70,'reason':85}
        for c in cols:
            self._tree.heading(c, text=hdrs[c])
            anc = 'center' if c=='#' else ('w' if c=='reason' else 'e')
            self._tree.column(c, width=widths[c], anchor=anc, minwidth=30)

        vsb = ttk.Scrollbar(log_outer, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4,0), pady=(0,4))
        vsb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,4), pady=(0,4))

        sty = ttk.Style()
        sty.configure('BT.Treeview', background=C['bg3'], foreground=C['white'],
                       fieldbackground=C['bg3'], font=('Consolas',8), rowheight=22)
        sty.configure('BT.Treeview.Heading', background=C['bg2'],
                       foreground=C['accent'], font=('Consolas',8,'bold'))
        sty.map('BT.Treeview', background=[('selected', C['bg3'])])

    # ── HELPERS ────────────────────────────────────────────────
    def _show_placeholder(self):
        for w in self._chart_frame.winfo_children(): w.destroy()
        tk.Label(self._chart_frame,
                 text="🧪  QuantQL Backtest Engine\n\n"
                      "1.  Write strategy in the editor (or load a template)\n"
                      "2.  Press  ▶ RUN  to fetch data & simulate\n"
                      "3.  Watch the animated bar-by-bar simulation\n"
                      "4.  Review trade book & export CSV / PNG\n\n"
                      "Example:   PERIOD 1Y  ·  TICKER MARUTI  ·  MARKET NSE",
                 font=('Consolas',11), bg=C['bg2'], fg=C['accent'],
                 justify='left').pack(expand=True, padx=20)

    def _load_example(self):
        key = self._ex_var.get()
        if key in EXAMPLES:
            self.editor.delete('1.0', tk.END)
            self.editor.insert('1.0', EXAMPLES[key])
            self._highlight_syntax()
            self._on_key()

    def _on_key(self, event=None):
        self._highlight_syntax()
        src = self.editor.get('1.0', tk.END).strip()
        if not src: self._compile_var.set(""); return
        try:
            s = compile_strategy(src)
            parts = [f"✓  {s.ticker} [{s.market}]  {s.period_str}  ({s.period_days}d)"]
            if s.buy_cond: parts.append("BUY ✓")
            if s.sell_cond: parts.append("SELL ✓")
            parts.append(f"{len(s.indicators)} ind")
            self._compile_var.set("   ".join(parts))
        except Exception as e:
            self._compile_var.set(f"✗  {e}")

    def _highlight_syntax(self):
        ed = self.editor
        for tag in ('kw','str','num','pct','op','cmt'):
            ed.tag_remove(tag, '1.0', tk.END)
        text = ed.get('1.0', tk.END)
        patterns = [
            ('kw', r'\b(BACKTEST|MARKET|TICKER|PERIOD|USE|BUY|SELL|WHEN|CAPITAL|POSITION_SIZE|STOP_LOSS|TAKE_PROFIT|COMMISSION|SLIPPAGE|AND|OR|NOT|CROSSES_ABOVE|CROSSES_BELOW)\b'),
            ('str', r'"[^"]*"'),
            ('pct', r'\d+(?:\.\d+)?%'),
            ('num', r'\b\d+(?:\.\d+)?\b'),
            ('op',  r'>=|<=|!=|==|>|<'),
            ('cmt', r'#[^\n]*'),
        ]
        for tag, pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                s_idx = f"1.0+{m.start()}c"
                e_idx = f"1.0+{m.end()}c"
                ed.tag_add(tag, s_idx, e_idx)

    # ── RUN BACKTEST ───────────────────────────────────────────
    def _run_backtest(self):
        self._stop_animation()
        src = self.editor.get('1.0', tk.END).strip()
        if not src:
            messagebox.showwarning("Backtest", "Write a QuantQL strategy first."); return

        # Phase 1: show "compiling" then show data preview
        for w in self._chart_frame.winfo_children(): w.destroy()
        lbl = tk.Label(self._chart_frame, text="⏳  Compiling & fetching data…",
                       font=('Consolas',13,'bold'), bg=C['bg2'], fg=C['accent'])
        lbl.pack(expand=True)
        self.parent.update()

        def _bg():
            try:
                result = run_backtest(src)
                self.parent.after(0, lambda: self._on_result(result))
            except Exception as e:
                self.parent.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_bg, daemon=True).start()

    def _on_error(self, msg):
        for w in self._chart_frame.winfo_children(): w.destroy()
        tk.Label(self._chart_frame, text=f"❌  Error\n\n{msg}",
                 font=('Consolas',11), bg=C['bg2'], fg=C['red'],
                 wraplength=700, justify='left').pack(expand=True, padx=20)
        self._set_status(f"Backtest error: {msg}")

    def _on_result(self, result: BacktestResult):
        self.result = result
        s = result.strategy
        self._update_metrics(result.metrics)
        self._update_trade_log(result)
        self._set_status(
            f"✓ {s.name} — {result.yf_ticker} [{result.exchange}] — "
            f"{len(result.trades)} trades — {result.metrics.get('Total Return','?')}")
        # start animated drawing
        self._start_animation()

    # ── METRICS ────────────────────────────────────────────────
    def _update_metrics(self, metrics):
        for w in self._metrics_grid.winfo_children(): w.destroy()
        cmap = {
            'Net P&L': lambda v: C['green'] if not v.startswith('-') else C['red'],
            'Win Rate': lambda v: C['green'] if float(v.rstrip('%'))>=50 else C['red'],
            'Sharpe Ratio': lambda v: C['green'] if float(v)>=1 else C['gold'] if float(v)>=0 else C['red'],
            'Max Drawdown': lambda v: C['red'],
            'Total Return': lambda v: C['green'] if '+' in v else C['red'],
            'Profit Factor': lambda v: C['green'] if v=='∞' or float(v)>=1.5 else C['gold'] if float(v)>=1 else C['red'],
        }
        order=['Total Trades','Win Rate','Net P&L','Total Return','Profit Factor',
               'Sharpe Ratio','Max Drawdown','Avg Hold (days)','Final Equity',
               'Volatility','Total Commission']
        keys=[k for k in order if k in metrics]+[k for k in metrics if k not in order and k!='Note']
        for i,k in enumerate(keys):
            v=metrics[k]; r,c0=i//3,(i%3)*2
            cfn=cmap.get(k)
            try: vc=cfn(v) if cfn else C['white']
            except: vc=C['white']
            tk.Label(self._metrics_grid, text=k, font=('Consolas',7),
                     bg=C['bg2'], fg=C['muted'], anchor='w'
                     ).grid(row=r, column=c0, sticky='w', padx=(2,1), pady=1)
            tk.Label(self._metrics_grid, text=v, font=('Consolas',7,'bold'),
                     bg=C['bg2'], fg=vc, anchor='e'
                     ).grid(row=r, column=c0+1, sticky='e', padx=(0,8), pady=1)

    # ── TRADE LOG ──────────────────────────────────────────────
    def _update_trade_log(self, r):
        for item in self._tree.get_children(): self._tree.delete(item)
        ccy = r.currency
        total_pnl = 0
        for idx, t in enumerate(r.trades, 1):
            ed = t.entry_date.strftime('%Y-%m-%d') if hasattr(t.entry_date,'strftime') else str(t.entry_date)
            xd = t.exit_date.strftime('%Y-%m-%d') if hasattr(t.exit_date,'strftime') else str(t.exit_date)
            tag = 'win' if t.pnl>=0 else 'loss'
            total_pnl += t.pnl
            self._tree.insert('', 'end', values=(
                str(idx), ed, xd,
                f"{ccy}{t.entry_price:,.2f}", f"{ccy}{t.exit_price:,.2f}",
                str(int(t.shares)),
                f"{ccy}{t.pnl:+,.2f}", f"{t.pnl_pct:+.1f}%",
                f"{ccy}{t.commission:,.2f}", t.exit_reason
            ), tags=(tag,))
        self._tree.tag_configure('win', foreground=C['green'])
        self._tree.tag_configure('loss', foreground=C['red'])
        self._trade_count_var.set(f"{len(r.trades)} trades")
        clr = C['green'] if total_pnl >= 0 else C['red']
        self._trade_summary_var.set(f"Net: {ccy}{total_pnl:+,.2f}")

    # ── ANIMATED SIMULATION ────────────────────────────────────
    def _start_animation(self):
        self._stop_animation()
        if not self.result: return
        for w in self._chart_frame.winfo_children(): w.destroy()

        r = self.result
        # detect which sub-indicator to show
        self._sub_name = None
        for nm in ('RSI','MACD','STOCH_K','ADX','WILLIAMS'):
            if nm in r.indicators: self._sub_name = nm; break

        n_rows = 2 + (1 if self._sub_name else 0)
        ratios = [4, 1.8] + ([1.5] if self._sub_name else [])
        self._fig = Figure(figsize=(14, 9), facecolor=C['bg'], dpi=100)
        gs = self._fig.add_gridspec(n_rows, 1, height_ratios=ratios, hspace=0.15)
        self._ax_price = self._fig.add_subplot(gs[0])
        self._ax_equity = self._fig.add_subplot(gs[1])
        self._ax_sub = self._fig.add_subplot(gs[2]) if self._sub_name else None

        canvas = FigureCanvasTkAgg(self._fig, self._chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

        # toolbar
        tb_frame = tk.Frame(self._chart_frame, bg=C['bg2'])
        tb_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(canvas, tb_frame)

        # progress + status
        pf = tk.Frame(self._chart_frame, bg=C['bg2'])
        pf.pack(fill=tk.X, padx=4, pady=2)
        self._prog_var = tk.IntVar(value=0)
        self._prog_bar = ttk.Progressbar(pf, variable=self._prog_var,
                                          maximum=len(r.data), mode='determinate')
        self._prog_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0,8))
        self._sim_status = tk.StringVar(value="▶ Simulating…")
        tk.Label(pf, textvariable=self._sim_status, font=('Consolas',8),
                 bg=C['bg2'], fg=C['muted'], width=50, anchor='w').pack(side=tk.LEFT)

        self._ani_bar = 0
        self._ani_running = True

        if self._ani_speed == 0:
            self._draw_frame(len(r.data))
            self._sim_status.set(f"✓ Complete — {len(r.trades)} trades")
            self._prog_var.set(len(r.data))
        else:
            self._ani_step()

    def _stop_animation(self):
        self._ani_running = False
        if self._ani_id:
            try: self.parent.after_cancel(self._ani_id)
            except: pass
            self._ani_id = None

    def _ani_step(self):
        if not self._ani_running or not self.result: return
        r = self.result; n = len(r.data)
        # adaptive: draw more bars per frame for longer datasets
        bpf = max(1, n // 200) if self._ani_speed < 50 else max(1, n // 100)
        end = min(self._ani_bar + bpf, n)
        self._ani_bar = end
        self._prog_var.set(end)

        self._draw_frame(end)

        if end >= n:
            self._ani_running = False
            self._sim_status.set(f"✓ Complete — {len(r.trades)} trades  |  "
                                 f"Return: {r.metrics.get('Total Return','?')}  |  "
                                 f"Sharpe: {r.metrics.get('Sharpe Ratio','?')}")
            return

        ccy = r.currency
        eq_val = r.equity_curve.iloc[end-1]
        self._sim_status.set(f"Bar {end}/{n}  |  Equity: {fmt_price(eq_val,ccy)}")
        self._ani_id = self.parent.after(self._ani_speed, self._ani_step)

    def _draw_frame(self, bar_end):
        r = self.result; data = r.data; ccy = r.currency; s = r.strategy
        if bar_end < 1: return
        d = data.iloc[:bar_end]
        n_total = len(data)

        # ═══ PRICE CHART ══════════════════════════════════════
        ax = self._ax_price; ax.clear(); style_ax(ax)
        x = np.arange(len(d))
        op=d['Open'].values; cl=d['Close'].values
        hi=d['High'].values; lo=d['Low'].values
        bull = cl >= op; w = 0.6
        ax.vlines(x, lo, hi, color=C['muted'], linewidth=0.5, alpha=0.6)
        body = np.abs(cl-op); body = np.where(body==0, (hi-lo)*0.01, body)
        bot = np.minimum(op, cl)
        if bull.any(): ax.bar(x[bull], body[bull], w, bottom=bot[bull], color=C['green'], edgecolor='none', alpha=0.9)
        if (~bull).any(): ax.bar(x[~bull], body[~bull], w, bottom=bot[~bull], color=C['red'], edgecolor='none', alpha=0.9)

        # overlay indicators (MAs, BB, SAR)
        overlay_skip = {'RSI','MACD','SIGNAL','HISTOGRAM','STOCH_K','STOCH_D',
                        'ADX','PLUS_DI','MINUS_DI','WILLIAMS','OBV','SLOPE','ATR','SAR_TREND'}
        ma_colors = {'SMA':C['blue'],'EMA':C['accent'],'DEMA':C['purple'],'TEMA':C['gold'],
                     'BB_UPPER':C['gold'],'BB_MID':C['cyan'],'BB_LOWER':C['gold'],
                     'VWAP':'#ff6b81','SAR':C['teal']}
        for nm, series in r.indicators.items():
            if nm in overlay_skip: continue
            vals = series.iloc[:bar_end].values
            clr = ma_colors.get(nm, C['muted'])
            ls = '--' if 'BB' in nm or nm in ('SMA','EMA','DEMA','TEMA') else '-.'
            ax.plot(x, vals, lw=0.9, alpha=0.7, linestyle=ls, color=clr, label=nm)
        # BB fill
        if 'BB_UPPER' in r.indicators and 'BB_LOWER' in r.indicators:
            ax.fill_between(x,
                            r.indicators['BB_UPPER'].iloc[:bar_end].values,
                            r.indicators['BB_LOWER'].iloc[:bar_end].values,
                            alpha=0.05, color=C['gold'])

        # buy/sell markers with price labels
        for bi in r.buy_signals:
            if bi < bar_end:
                ax.annotate(f'▲ BUY\n{ccy}{d["Close"].iloc[bi]:,.0f}',
                            xy=(bi, d['Low'].iloc[bi]), fontsize=6,
                            color=C['green'], ha='center', va='top', fontweight='bold',
                            fontfamily='Consolas')
        for si in r.sell_signals:
            if si < bar_end:
                ax.annotate(f'▼ SELL\n{ccy}{data["Close"].iloc[si]:,.0f}',
                            xy=(si, d['High'].iloc[min(si, len(d)-1)]),
                            fontsize=6, color=C['red'], ha='center', va='bottom',
                            fontweight='bold', fontfamily='Consolas')

        # axes
        ax.set_xlim(-0.5, n_total - 0.5)
        lo_y=d['Low'].min(); hi_y=d['High'].max(); pad=(hi_y-lo_y)*0.06
        ax.set_ylim(lo_y-pad, hi_y+pad*4)
        ax.set_title(f"{s.name}  ·  {r.yf_ticker} [{r.exchange}]  ·  {s.period_str}  ·  "
                     f"Bar {bar_end}/{n_total}",
                     color=C['white'], fontsize=10, fontweight='bold', pad=5)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v,_: f"{ccy}{v:,.0f}" if v>=1000 else f"{ccy}{v:.2f}"))
        # date x-ticks
        step=max(1,len(d)//10); tks=list(range(0,len(d),step))
        ax.set_xticks(tks)
        if hasattr(d.index[0],'strftime'):
            ax.set_xticklabels([d.index[i].strftime('%d %b %y') for i in tks],
                               rotation=45, ha='right', color=C['muted'], fontsize=6)
        hn,lb=ax.get_legend_handles_labels()
        if hn: ax.legend(loc='upper left', fontsize=6, facecolor=C['bg3'],
                         edgecolor=C['border'], labelcolor=C['white'], framealpha=0.7)

        # ═══ EQUITY CURVE ═════════════════════════════════════
        ax2 = self._ax_equity; ax2.clear(); style_ax(ax2)
        eq = r.equity_curve.iloc[:bar_end]; eq_x = np.arange(len(eq))
        ax2.fill_between(eq_x, s.capital, eq.values,
                         where=eq.values>=s.capital, alpha=0.25, color=C['green'])
        ax2.fill_between(eq_x, s.capital, eq.values,
                         where=eq.values<s.capital, alpha=0.25, color=C['red'])
        ax2.plot(eq_x, eq.values, color=C['accent'], lw=1.5)
        ax2.axhline(s.capital, color=C['muted'], lw=0.7, linestyle='--', alpha=0.5)
        # current equity label
        cur_eq = eq.values[-1]
        pct_ret = (cur_eq/s.capital - 1) * 100
        eq_clr = C['green'] if pct_ret >= 0 else C['red']
        ax2.text(len(eq)-1, cur_eq, f"  {ccy}{cur_eq:,.0f}  ({pct_ret:+.1f}%)",
                 color=eq_clr, fontsize=7, va='center', fontfamily='Consolas',
                 bbox=dict(facecolor=C['bg'], alpha=0.7, edgecolor='none', pad=1))
        ax2.set_xlim(-0.5, n_total-0.5)
        ax2.set_title('Equity Curve', color=C['white'], fontsize=9, fontweight='bold', pad=3)
        ax2.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v,_: f"{ccy}{v:,.0f}"))
        ax2.tick_params(labelbottom=False)

        # ═══ SUB INDICATOR ════════════════════════════════════
        if self._ax_sub and self._sub_name:
            ax3=self._ax_sub; ax3.clear(); style_ax(ax3)
            nm=self._sub_name
            if nm in r.indicators:
                vals=r.indicators[nm].iloc[:bar_end].values
                sx=np.arange(len(vals))
                ax3.plot(sx, vals, color=C['purple'], lw=1.2, label=nm)
                if nm=='RSI':
                    ax3.axhline(70,color=C['red'],linestyle='--',lw=0.7,alpha=0.6)
                    ax3.axhline(30,color=C['green'],linestyle='--',lw=0.7,alpha=0.6)
                    ax3.fill_between(sx,70,100,alpha=0.06,color=C['red'])
                    ax3.fill_between(sx,0,30,alpha=0.06,color=C['green'])
                    ax3.set_ylim(0,100)
                elif nm=='MACD':
                    if 'SIGNAL' in r.indicators:
                        ax3.plot(sx,r.indicators['SIGNAL'].iloc[:bar_end].values,
                                 color=C['accent'],lw=1,label='Signal')
                    if 'HISTOGRAM' in r.indicators:
                        h=r.indicators['HISTOGRAM'].iloc[:bar_end].values
                        hc=[C['green'] if v>=0 else C['red'] for v in h]
                        ax3.bar(sx,h,color=hc,alpha=0.5,width=0.8)
                    ax3.axhline(0,color=C['muted'],lw=0.5,alpha=0.4)
                elif nm=='STOCH_K':
                    if 'STOCH_D' in r.indicators:
                        ax3.plot(sx,r.indicators['STOCH_D'].iloc[:bar_end].values,
                                 color=C['accent'],lw=1,label='%D')
                    ax3.axhline(80,color=C['red'],linestyle='--',lw=0.7,alpha=0.6)
                    ax3.axhline(20,color=C['green'],linestyle='--',lw=0.7,alpha=0.6)
                    ax3.set_ylim(0,100)
                elif nm=='ADX':
                    for snm,clr2 in [('PLUS_DI',C['green']),('MINUS_DI',C['red'])]:
                        if snm in r.indicators:
                            ax3.plot(sx,r.indicators[snm].iloc[:bar_end].values,
                                     color=clr2,lw=0.8,linestyle='--',label=snm)
                    ax3.axhline(25,color=C['muted'],linestyle=':',lw=0.6,alpha=0.5)
                ax3.set_xlim(-0.5,n_total-0.5)
                ax3.set_ylabel(nm,color=C['purple'],fontsize=7)
                hn2,_=ax3.get_legend_handles_labels()
                if hn2: ax3.legend(loc='upper left',fontsize=5,facecolor=C['bg3'],
                                   edgecolor=C['border'],labelcolor=C['white'])

        try: self._canvas.draw_idle()
        except: pass

    # ── CSV EXPORT ─────────────────────────────────────────────
    def _export_csv(self):
        if not self.result or not self.result.trades:
            messagebox.showwarning("Export", "Run a backtest first."); return
        r = self.result; ccy = r.currency
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV","*.csv"),("All","*.*")],
            initialfile=f"tradebook_{r.strategy.ticker}_{datetime.now():%Y%m%d_%H%M}.csv")
        if not path: return

        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['QuantQL Backtest Report'])
            w.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            w.writerow([])
            w.writerow(['Strategy', r.strategy.name])
            w.writerow(['Ticker', r.yf_ticker, 'Exchange', r.exchange, 'Currency', ccy])
            w.writerow(['Period', r.strategy.period_str, 'Bars', len(r.data)])
            w.writerow(['Capital', r.strategy.capital])
            w.writerow(['Stop Loss', f"{r.strategy.stop_loss_pct}%",
                         'Take Profit', f"{r.strategy.take_profit_pct}%"])
            w.writerow(['Commission', f"{r.strategy.commission_pct}%"])
            w.writerow([])

            w.writerow(['=== METRICS ==='])
            for k, v in r.metrics.items():
                w.writerow([k, v])
            w.writerow([])

            w.writerow(['=== TRADE LOG ==='])
            w.writerow(['#','Entry Date','Exit Date','Entry Price','Exit Price',
                         'Shares','P&L','P&L %','Commission','Exit Reason',
                         'Hold Days'])
            for i, t in enumerate(r.trades, 1):
                ed=t.entry_date.strftime('%Y-%m-%d') if hasattr(t.entry_date,'strftime') else str(t.entry_date)
                xd=t.exit_date.strftime('%Y-%m-%d') if hasattr(t.exit_date,'strftime') else str(t.exit_date)
                hd=(pd.Timestamp(t.exit_date)-pd.Timestamp(t.entry_date)).days if t.entry_date and t.exit_date else 0
                w.writerow([i, ed, xd, f"{t.entry_price:.2f}", f"{t.exit_price:.2f}",
                            int(t.shares), f"{t.pnl:.2f}", f"{t.pnl_pct:.2f}%",
                            f"{t.commission:.2f}", t.exit_reason, hd])
            w.writerow([])

            w.writerow(['=== EQUITY CURVE ==='])
            w.writerow(['Date','Equity','Daily Return %'])
            rets = r.equity_curve.pct_change().fillna(0)
            for dt, eq in r.equity_curve.items():
                d_str = dt.strftime('%Y-%m-%d') if hasattr(dt,'strftime') else str(dt)
                dr = rets.loc[dt] * 100
                w.writerow([d_str, f"{eq:.2f}", f"{dr:.4f}"])

        self._set_status(f"Tradebook saved → {path}")
        messagebox.showinfo("Export CSV", f"Saved to:\n{path}")

    # ── PNG EXPORT ─────────────────────────────────────────────
    def _export_png(self):
        if not hasattr(self, '_fig') or not self._fig:
            messagebox.showwarning("Export", "Run a backtest first."); return
        path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[("PNG","*.png"),("All","*.*")],
            initialfile=f"backtest_{self.result.strategy.ticker}_{datetime.now():%Y%m%d}.png")
        if path:
            self._fig.savefig(path, dpi=150, facecolor=C['bg'], bbox_inches='tight')
            self._set_status(f"Chart saved → {path}")


# ═══════════════════════════════════════════════════════════════════
# 10. DASHBOARD INTEGRATION
# ═══════════════════════════════════════════════════════════════════
def add_backtest_tab(dashboard):
    """
    Call from QuantDashboard._setup_ui() after building other tabs:
        from .backtest_engine import add_backtest_tab
        add_backtest_tab(self)
    """
    bt_tab = tk.Frame(dashboard.nb, bg=C['bg'])
    dashboard.nb.add(bt_tab, text='🧪  Backtest')
    dashboard._bt = BacktestTab(bt_tab, dashboard._set_status)


# standalone
def backtest_dashboard():
        root = tk.Tk()
        root.title("QuantQL Backtest Engine")
        root.geometry("1500x900")
        root.configure(bg=C['bg'])
        sty = ttk.Style(); sty.theme_use('clam')
        f = tk.Frame(root, bg=C['bg']); f.pack(fill=tk.BOTH, expand=True)
        bt = BacktestTab(f, lambda m: print(m))
        root.mainloop()
        

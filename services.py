import yfinance as yf
import pandas as pd

def fetch_stock_data(symbols=None):
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOG"]
    
    data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        hist = ticker.history(period="5d", interval="1m")
        if hist.empty:
            continue
        last_price = hist["Close"].iloc[-1]
        data[sym] = {"price": last_price, "history": hist}
    return data


def analyze_signals(data, short_window=5, long_window=20):
    signals = {}
    for sym, info in data.items():
        hist = info["history"]["Close"]
        sma_short = hist.rolling(short_window).mean().iloc[-1]
        sma_long = hist.rolling(long_window).mean().iloc[-1]
        price = info["price"]

        if sma_short > sma_long:
            signal = "BUY"
        elif sma_short < sma_long:
            signal = "SELL"
        else:
            signal = "HOLD"

        signals[sym] = {
            "price": round(price, 2),
            "sma_short": round(sma_short, 2),
            "sma_long": round(sma_long, 2),
            "signal": signal
        }
    return signals

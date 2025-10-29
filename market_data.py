import requests
from config import Config
import yfinance as yf

def get_price_for_symbol(symbol):
    # Try Finnhub
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={Config.FINNHUB_KEY}"
        resp = requests.get(url, timeout=5).json()
        if resp and "c" in resp and resp["c"] is not None:
            return float(resp["c"])
    except:
        pass

    # fallback: yfinance
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m")
        if not df.empty:
            return float(df["Close"].iloc[-1])
    except:
        pass

    return None

def get_ohlc_for_symbol(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

def fetch_latest_news():
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={Config.FINNHUB_KEY}"
        resp = requests.get(url, timeout=5).json()
        news = []
        for n in resp[:10]:
            news.append({
                "headline": n.get("headline"),
                "source": n.get("source"),
                "summary": n.get("summary"),
                "url": n.get("url"),
                "datetime": n.get("datetime")
            })
        return news
    except:
        return []

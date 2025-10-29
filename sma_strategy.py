import pandas as pd

def compute_sma_from_ohlc(ohlc_df, short_window=10, long_window=50):
    """
    ohlc_df: pandas DataFrame with 'Close' column
    Returns (sma_short, sma_long, signal_str)
    """
    if ohlc_df is None or len(ohlc_df) < long_window:
        return (None, None, "HOLD (insufficient data)")

    df = ohlc_df.copy()
    df["SMA_Short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_Long"] = df["Close"].rolling(window=long_window).mean()

    latest_short = df["SMA_Short"].iloc[-1]
    latest_long = df["SMA_Long"].iloc[-1]
    if latest_short is None or latest_long is None or pd.isna(latest_short) or pd.isna(latest_long):
        return (None, None, "HOLD (insufficient SMA)")

    if latest_short > latest_long:
        return (round(latest_short, 4), round(latest_long, 4), "BUY (Golden Cross detected)")
    elif latest_short < latest_long:
        return (round(latest_short, 4), round(latest_long, 4), "SELL (Death Cross detected)")
    else:
        return (round(latest_short, 4), round(latest_long, 4), "HOLD (No clear trend)")

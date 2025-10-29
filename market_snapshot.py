# market_snapshot.py
from flask import Blueprint, jsonify
from flask_socketio import SocketIO
import yfinance as yf
import threading
import time

market_bp = Blueprint("market_bp", __name__)
socketio = SocketIO()  # This will be initialized in main app

# ------------------ Market Snapshot API ------------------
@market_bp.route("/api/market_snapshot/<symbol>", methods=["GET"])
def market_snapshot(symbol):
    symbol = symbol.upper()
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="1d", interval="1m")  # 1 day, 1-min interval
        if hist.empty:
            return jsonify({"error": "No data found"}), 404
        
        last = hist['Close'][-1]
        open_price = hist['Open'][0]
        high = hist['High'].max()
        low = hist['Low'].min()
        volume = int(hist['Volume'][-1])
        
        # Fake bid/ask for demo
        bid = round(last * 0.995, 2)
        ask = round(last * 1.005, 2)
        
        snapshot = {
            "symbol": symbol,
            "last_price": last,
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            "bid": bid,
            "ask": ask
        }
        return jsonify(snapshot)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ Real-time updates ------------------
def emit_market_snapshot(symbol="AAPL"):
    while True:
        try:
            data = yf.Ticker(symbol)
            hist = data.history(period="1d", interval="1m")
            if not hist.empty:
                last = hist['Close'][-1]
                bid = round(last * 0.995, 2)
                ask = round(last * 1.005, 2)
                socketio.emit("market_snapshot_update", {
                    "symbol": symbol,
                    "last_price": last,
                    "bid": bid,
                    "ask": ask
                })
        except Exception as e:
            print("Error fetching market snapshot:", e)
        time.sleep(5)  # update every 5 seconds


def start_market_thread():
    threading.Thread(target=emit_market_snapshot, daemon=True).start()

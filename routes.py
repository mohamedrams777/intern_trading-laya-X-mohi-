from flask import Blueprint, jsonify, request, Response, render_template
from models import db, Order, Trade, SimulationResult, buy_or_hold,User
from order_book import OrderBook
from market_data import get_price_for_symbol
from simulation import monte_carlo_gbm, summarize_final_prices
from realtime import socketio, broadcast_news
from gemini_client import ask_gemini
from utils import fetch_data, train_model, predict_future, monte_carlo_simulation
from flask_login import login_user, logout_user, current_user, login_required 
from flask import redirect, url_for

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ✅ Define Blueprint here
routes_bp = Blueprint("routes", __name__)
order_book = OrderBook()

@routes_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    email = data.get('email')

    # 1. Basic Validation 
    if not username or not password or not confirm_password:
        return jsonify({"message": "Missing required fields (username, password, confirm_password)"}), 400
        
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    # 2. Check if user already exists in the database
    if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
        return jsonify({"message": "Username already exists"}), 409
    
    # 3. Create a new User object
    new_user = User(username=username, email=email)
    
    # 4. Use the secure hashing method
    new_user.set_password(password)
    
    # 5. Add to database and commit
    db.session.add(new_user)
    db.session.commit()

    # 6. Success Response
    return jsonify({"message": "User created successfully", "username": username}), 201


@routes_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

   
    if user is None or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401
    
    
    login_user(user)

    # 4. Success Response
    return jsonify({"message": f"Login successful for {username}"}), 200


@routes_bp.route('/api/logout', methods=['POST'])
def api_logout():
    # Use Flask-Login's function to clear the session
    logout_user()
    return redirect(url_for("routes.login"))
    
@routes_bp.route("/", methods=["GET"])
def index():
    # Pass username if logged in, else None
    username = current_user.username if current_user.is_authenticated else None
    return render_template("index.html", username=username)


@routes_bp.route('/login')
def login():
    """Renders the login page template."""
    # When a user clicks the /login link, this function renders the login.html file.
    return render_template('login.html')

@routes_bp.route('/signup')
def signup():
    """Renders the signup page template."""
    # When a user clicks the /signup link, this function renders the signup.html file.
    return render_template('signup.html')



@routes_bp.route("/order", methods=["POST"])
def place_order():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    symbol = data.get("symbol", "").upper()
    side = data.get("order_type", "").lower()
    quantity = data.get("quantity")

    if not symbol or side not in ("buy", "sell") or quantity is None:
        return jsonify({"error": "symbol, order_type (buy/sell) and quantity required"}), 400

    try:
        quantity = float(quantity)
    except ValueError:
        return jsonify({"error": "quantity must be numeric"}), 400

    price = get_price_for_symbol(symbol)

    # ✅ Insert into database
    new_order = Order(symbol=symbol, side=side, price=price, quantity=quantity)
    db.session.add(new_order)
    db.session.commit()

    # ✅ Match orders (optional)
    trades_executed = order_book.insert_order(side, price, quantity)

    # ✅ Rebuild orderbook from DB
    bids = Order.query.filter_by(symbol=symbol, side="buy").order_by(Order.price.desc()).all()
    asks = Order.query.filter_by(symbol=symbol, side="sell").order_by(Order.price.asc()).all()

    bids_data = [{"price": o.price, "quantity": o.quantity} for o in bids]
    asks_data = [{"price": o.price, "quantity": o.quantity} for o in asks]

    # ✅ Emit updates
    socketio.emit("order_update", {"symbol": symbol, "bids": bids_data, "asks": asks_data})
    for trade in trades_executed:
        socketio.emit("trade_update", trade)

    return jsonify({
        "message": "Order placed successfully",
        "trades": trades_executed,
        "remaining_order": {
            "side": side,
            "price": price,
            "quantity": quantity - sum(t["quantity"] for t in trades_executed)
        }
    }), 201


   


@routes_bp.route("/orderbook/<symbol>", methods=["GET"])
def get_orderbook(symbol):
    symbol = symbol.upper()
    bids = Order.query.filter_by(symbol=symbol, side="buy").order_by(Order.price.desc()).all()
    asks = Order.query.filter_by(symbol=symbol, side="sell").order_by(Order.price.asc()).all()

    return jsonify({
        "bids": [{"price": o.price, "quantity": o.quantity} for o in bids],
        "asks": [{"price": o.price, "quantity": o.quantity} for o in asks]
    })


@routes_bp.route("/orders", methods=["GET"])
def get_all_orders():
    try:
        orders = Order.query.order_by(Order.id.asc()).all()
        order_list = [o.to_dict() for o in orders]
        return jsonify({"orders": order_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes_bp.route("/price/<symbol>", methods=["GET"])
def get_price(symbol):
    symbol = symbol.upper()
    price = get_price_for_symbol(symbol)
    if price is None:
        return jsonify({"error": "Unable to fetch price"}), 400
    return jsonify({"symbol": symbol, "price": price})


@routes_bp.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True, silent=True) or {}
    symbol = data.get("symbol", "AAPL").upper()
    start_price = float(data.get("price", 100.0))
    sims = int(data.get("simulations", 500))
    days = int(data.get("days", 30))
    mu = float(data.get("mu", 0.0005))
    sigma = float(data.get("sigma", 0.01))

    paths = monte_carlo_gbm(start_price, sims, days, mu, sigma)
    summary = summarize_final_prices(paths)

    sim = SimulationResult(symbol=symbol, start_price=start_price,
                           simulations=sims, days=days,
                           mean_final=summary["mean_final_price"],
                           median_final=summary["median_final_price"],
                           pct5=summary["5pct"], pct95=summary["95pct"])
    db.session.add(sim)
    db.session.commit()

    return jsonify({"summary": summary, "sample_paths": [p[:5] for p in paths[:5]], "db_record": sim.to_dict()})


@routes_bp.route("/news", methods=["GET"])
def get_ai_news():
    symbol = request.args.get("symbol", "AAPL").upper()
    prompt = f"Give latest concise market summary for {symbol} stock performance and investor sentiment."

    try:
        ai_news = ask_gemini(prompt)
        broadcast_news([ai_news])
        return jsonify({"symbol": symbol, "news": ai_news}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get news: {str(e)}"}), 500


@routes_bp.route("/confirm", methods=["POST"])
def confirm_order():
    data = request.get_json(force=True) or {}
    order_id = data.get("order_id")
    action = data.get("action")

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "pending":
        return jsonify({"error": f"Order is {order.status} and cannot be confirmed"}), 400

    if action == "confirm":
        order.status = "executed"
        db.session.commit()

        trades = order_book.insert_order(order.side, order.price, order.quantity)
        for t in trades:
            tt = Trade(buy_price=t["buy_price"], sell_price=t["sell_price"], quantity=t["quantity"])
            db.session.add(tt)
        db.session.commit()

        socketio.emit("order_executed", {"order": order.to_dict(), "trades": trades}, namespace="/realtime")
        return jsonify({"message": "Order executed", "trades": trades})
    else:
        order.status = "cancelled"
        db.session.commit()
        socketio.emit("order_cancelled", {"order": order.to_dict()}, namespace="/realtime")
        return jsonify({"message": "Order cancelled"})


@routes_bp.route("/graph/<symbol>", methods=["GET"])
def show_graph(symbol):
    symbol = symbol.upper()
    try:
        data = yf.download(symbol, period="1mo", auto_adjust=False)["Close"]

        plt.figure(figsize=(6, 3))
        plt.plot(data, label=f"{symbol} Price")
        plt.title(f"{symbol} Price Chart (1 Month)")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return Response(buf.getvalue(), mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes_bp.route("/api/predict", methods=["POST"])
def predict_stock():
    try:
        data = request.get_json()
        symbol = data.get("symbol", "").upper()

        if not symbol:
            return jsonify({"error": "Please provide a stock symbol"}), 400

        df = fetch_data(symbol)
        if df is None or df.empty:
            return jsonify({"error": f"No data found for {symbol}"}), 404

        model, scaler = train_model(df)

        latest_price = df["Close"].iloc[-1]
        future_7 = predict_future(model, scaler, df, 7)
        future_50 = predict_future(model, scaler, df, 50)

        predicted_price = future_7[-1]
        mean_price, lower_bound, upper_bound, _ = monte_carlo_simulation(predicted_price)
        decision = buy_or_hold(latest_price, predicted_price)

        return jsonify({
            "symbol": symbol,
            "latest_price": float(latest_price),
            "prediction_next_7_days": [float(x) for x in future_7.flatten()],
            "prediction_next_50_days": [float(x) for x in future_50.flatten()],
            "monte_carlo_mean": float(mean_price),
            "confidence_interval": {
                "5_percentile": float(lower_bound),
                "95_percentile": float(upper_bound)
            },
            "decision": decision
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes_bp.route("/api/historical/<symbol>", methods=["GET"])
def get_historical(symbol):
    import yfinance as yf
    import pandas as pd

    symbol = symbol.upper()
    try:
        print(f"Fetching 1-year data for {symbol}...")
        df = yf.download(symbol, period="1y", interval="1d")

        if df.empty:
            return jsonify({"error": f"No data found for {symbol}"}), 404

        # Handle MultiIndex columns (in case of multi-level columns)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

        # Try to find the correct 'Close' column
        close_col = None
        for col in df.columns:
            if "Close" in col:
                close_col = col
                break

        if not close_col:
            return jsonify({"error": "No Close column found"}), 500

        df = df.reset_index()
        df['Date'] = df['Date'].astype(str)
        df[close_col] = df[close_col].ffill()

        data = {
            "dates": df['Date'].tolist(),
            "prices": df[close_col].tolist()
        }

        print(f"✅ Successfully fetched {len(df)} records for {symbol}")
        return jsonify(data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
# def get_historical(symbol):
#     symbol = symbol.upper()
#     try:
#         # Fetch 1-year daily data
#         df = yf.download(symbol, period="1y", interval="1d")
        
#         if df.empty:
#             return jsonify({"error": f"No data found for {symbol}"}), 404
        
#         df = df.reset_index()
#         df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # format date
#         df['Close'].fillna(method='ffill', inplace=True)   # fill missing values

#         data = {
#             "dates": df['Date'].tolist(),
#             "prices": df['Close'].tolist()
#         }
#         return jsonify(data)
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500




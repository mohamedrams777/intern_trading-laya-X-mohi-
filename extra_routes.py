from flask import Blueprint, request, jsonify, render_template
from config import Config
from market_data import fetch_latest_news
from gemini_client import ask_gemini
from realtime import broadcast_news
import requests
from datetime import date, timedelta

extra_bp = Blueprint("extra_bp", __name__)

@extra_bp.route("/community-chat")
def community_chat_page():
    return render_template("community_chat.html")

@extra_bp.route("/portfolio")
def portfolio_page():
    return render_template("portfolio.html")

@extra_bp.route("/current-status")
def current_status_page():
    return render_template("current_status.html")

@extra_bp.route("/profile")
def profile_page():
    # Example user data — in real projects, fetch from database
    user_data = {
        "username": "api",
        "email": "api@gmail.com",
        "account_type": "Pro Trader",
        "phone": "+91 98765 43210",
        "join_date": "March 2024",
        "last_login": "2025-10-13 21:42",
        "twofa": "Enabled",
        "password_updated": "2025-09-20"
    }
    return render_template("profile.html", **user_data)


@extra_bp.route("/api/news", methods=["GET"])
def get_realtime_news():
    # try:
    #     today = date.today()
    #     last_week = today - timedelta(days=7)
    #     url = (
    #         f"https://finnhub.io/api/v1/company-news?"
    #         f"symbol=AAPL&from={last_week}&to={today}&token={Config.FINNHUB_KEY}"
    #     )
    #     response = requests.get(url, timeout=5)
    #     response.raise_for_status()

    #     news_data = response.json()
    #     news_items = [
    #         {
    #             "headline": n.get("headline"),
    #             "source": n.get("source"),
    #             "url": n.get("url"),
    #             "datetime": n.get("datetime")
    #         }
    #         for n in news_data[:8]
    #     ]

    #     broadcast_news(news_items)
    #     return jsonify({"news": news_items})
    # except Exception as e:
    #     print("❌ Error fetching news:", e)
    #     return jsonify({"error": str(e)}), 500 
    # """
    # Fetches the latest Apple Inc (AAPL) news headlines.
    # """
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2024-10-01&to=2025-10-13&token={Config.FINNHUB_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch news"}), 500

        news_data = response.json()
        news_items = [
            {
                "headline": n.get("headline"),
                "source": n.get("source"),
                "url": n.get("url"),
                "datetime": n.get("datetime")
            }
            for n in news_data[:8]  # top 8 news
        ]

        # Broadcast live updates to all connected clients
        broadcast_news(news_items)

        return jsonify({"news": news_items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ CHATBOT ------------------

@extra_bp.route("/api/chat", methods=["POST"])
def chatbot_response():
    """
    A chatbot endpoint that uses Gemini (or placeholder AI) to answer user questions.
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400

        user_msg = data["message"]
        ai_reply = ask_gemini(user_msg)
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@extra_bp.route("/api/chat", methods=["GET"])
def chat_history():
    # return dummy empty history for now
    messages = [
        {"username": "Bot", "text": "Welcome to the community chat!"}
    ]
    return jsonify(messages)

@extra_bp.route("/api/portfolio")
def get_portfolio():
    data = {
        "holdings": [
            {"symbol": "AAPL", "quantity": 10, "avg_price": 180, "market_value": 1920, "pnl": 120},
            {"symbol": "TSLA", "quantity": 5, "avg_price": 240, "market_value": 1250, "pnl": 50},
            {"symbol": "GOOG", "quantity": 2, "avg_price": 2800, "market_value": 2850, "pnl": 50},
        ],
        "total_balance": 6020,
        "invested_amount": 5800,
        "unrealized_profit": 220,
        "performance": {
            "dates": ["2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04", "2025-10-05"],
            "values": [5800, 5850, 5900, 6000, 6020],
        },
    }
    return jsonify(data)


# 🚀 ADDA Trade — AI-Driven Trading System

A full-stack, real-time stock trading platform powered by **Flask**, **SocketIO**, and **AI/ML models**. The system provides live market data, intelligent buy/sell signals, Monte Carlo simulations, LSTM-based price predictions, an AI chatbot (Google Gemini), and a real-time order book built on a **Red-Black Tree** data structure.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Usage Guide](#-usage-guide)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Data Structures & Algorithms](#-data-structures--algorithms)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Real-Time Dashboard** | Live market prices, order book depth, and trade history updated via WebSockets |
| **Order Placement** | Place buy/sell orders with automatic order matching against the order book |
| **Order Book (Red-Black Tree)** | High-performance order book using Red-Black Trees for O(log n) insert/lookup |
| **Live Market Data** | Real-time stock prices from **Finnhub** and **Yahoo Finance (yfinance)** |
| **LSTM Price Prediction** | Deep learning model (LSTM) that predicts future stock prices based on historical data |
| **Monte Carlo Simulation** | Geometric Brownian Motion simulation to forecast price distributions |
| **SMA Trading Signals** | Short/Long Simple Moving Average crossover detection (Golden Cross / Death Cross) |
| **AI Chatbot (Gemini)** | Ask trading-related questions; powered by Google's Gemini 2.0 Flash API |
| **Market Snapshot** | Real-time snapshot of any stock: last price, open, high, low, volume, bid, ask |
| **News Feed** | Latest financial news headlines from Finnhub API |
| **Portfolio Tracker** | View your holdings, market value, P&L, and performance chart |
| **User Authentication** | Sign up and log in with secure password hashing (Werkzeug) |
| **Community Chat** | Real-time community chat interface for traders |
| **User Profile** | Personal profile page with account details and security settings |
| **Historical Charts** | Interactive charts with historical prices, SMA overlays, and prediction curves |
| **Background Scheduler** | Hourly background tasks for data refresh and model updates |

---

## 🛠 Tech Stack

### Backend
- **Python 3.x** — Core language
- **Flask** — Web framework
- **Flask-SocketIO + Eventlet** — Real-time WebSocket communication
- **Flask-Login** — User session management
- **Flask-SQLAlchemy** — ORM for database operations
- **SQLite** (default) / **PostgreSQL** (production) — Database

### AI / ML
- **TensorFlow / Keras** — LSTM neural network for stock price prediction
- **scikit-learn** — MinMaxScaler for data normalization
- **NumPy / Pandas** — Data processing and numerical computation
- **Matplotlib** — Chart generation (server-side)

### Market Data
- **yfinance** — Yahoo Finance API for historical and real-time stock data
- **Finnhub API** — Real-time quotes and financial news
- **Google Gemini API** — AI chatbot for trading insights

### Frontend
- **HTML/CSS/JavaScript** — Dashboard UI
- **Socket.IO (Client)** — Real-time updates
- **Chart.js / Custom Charts** — Data visualization

---

## 📁 Project Structure

```
AI-driven-trading-system/
├── app.py                 # Application entry point & Flask app factory
├── config.py              # Configuration (DB, API keys from .env)
├── models.py              # Database models (User, Order, Trade, Portfolio, Simulation)
├── routes.py              # Main API routes (orders, predictions, charts, auth)
├── extra_routes.py        # Additional routes (chat, news, portfolio, profile)
├── order_book.py          # Red-Black Tree & Segment Tree order book engine
├── market_data.py         # Market data fetchers (Finnhub + yfinance)
├── market_snapshot.py     # Real-time market snapshot API + background emitter
├── gemini_client.py       # Google Gemini AI chatbot client
├── simulation.py          # Monte Carlo simulation (Geometric Brownian Motion)
├── sma_strategy.py        # SMA crossover strategy (Golden/Death Cross)
├── utils.py               # LSTM model training, prediction, helper functions
├── services.py            # Stock data fetching & signal analysis service
├── realtime.py            # SocketIO setup & broadcast functions
├── scheduler.py           # Background job scheduler
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys, DB config)
├── data.sqlite3           # SQLite database file (auto-created)
├── templates/             # HTML templates
│   ├── index.html         #   Main trading dashboard
│   ├── login.html         #   Login page
│   ├── signup.html        #   Registration page
│   ├── portfolio.html     #   Portfolio tracker page
│   ├── profile.html       #   User profile page
│   ├── community_chat.html#   Community chat page
│   └── current_status.html#   Current market status page
└── static/                # Static assets
    ├── css/               #   Stylesheets
    └── js/                #   Client-side JavaScript
```

---

## 📌 Prerequisites

- **Python 3.10+** installed ([Download Python](https://www.python.org/downloads/))
- **pip** (comes bundled with Python)
- **Git** (optional, for cloning)

---

## ⚙ Installation & Setup

### 1. Clone the Repository (or download)

```bash
cd AI-driven-trading-system
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If TensorFlow fails to install (e.g., on Python 3.13+), the app will still run. TensorFlow is only used for the LSTM prediction feature. All other features work without it.

### 5. Configure Environment Variables

Edit the `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FINNHUB_KEY=your_finnhub_api_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# Optional: PostgreSQL (leave blank to use SQLite)
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
DB_PORT=
```

| Key | Required | Purpose | Get it from |
|-----|----------|---------|-------------|
| `GEMINI_API_KEY` | Optional | Powers the AI chatbot | [Google AI Studio](https://aistudio.google.com/apikey) |
| `FINNHUB_KEY` | Optional | Real-time stock quotes & news | [Finnhub.io](https://finnhub.io/) |
| `ALPHA_VANTAGE_KEY` | Optional | Additional market data | [Alpha Vantage](https://www.alphavantage.co/) |

> The app works without any API keys — it falls back to **yfinance** for market data.

---

## ▶ How to Run

### Quick Start (3 commands)

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate

# 2. Run the application
python app.py

# 3. Open in browser
# Navigate to → http://127.0.0.1:3000
```

The server starts on **http://127.0.0.1:3000** and the dashboard will load automatically.

### Stopping the Application

Press `Ctrl + C` in the terminal to stop the server.

### Common Issues

| Issue | Solution |
|-------|----------|
| `Port 3000 already in use` | Another instance is running. Kill it: `taskkill /F /IM python.exe` then try again |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `TensorFlow not found` | Safe to ignore — LSTM predictions won't work, but all other features will |
| `.venv` path errors after moving project | Delete `.venv` folder and recreate: `python -m venv .venv` |

---

## 📖 Usage Guide

### 🏠 Dashboard (Home Page)

The main dashboard at `http://127.0.0.1:3000` provides:

1. **Symbol Search** — Enter any stock ticker (e.g., `AAPL`, `TSLA`, `GOOG`) and click **Live** to load real-time data
2. **Market Price Chart** — Live price chart with historical data, SMA indicators, and prediction overlays
3. **Place Order** — Select **Buy** or **Sell**, enter quantity, and submit the order
4. **Order Book** — Real-time bid/ask depth showing all open orders
5. **Trade History** — List of all executed trades with prices and quantities
6. **Market Snapshot** — Quick stats: last price, open, high, low, volume, bid, ask

### 📈 Stock Prediction

- The system uses **LSTM (Long Short-Term Memory)** neural networks trained on 2 years of historical data
- Predictions include a **7-day forecast** with past price trends
- **Buy/Hold signals** are generated based on predicted vs. current price (>2% upside = Buy)

### 🎲 Monte Carlo Simulation

- Runs **500+ simulations** using Geometric Brownian Motion
- Provides **mean**, **median**, **5th percentile**, and **95th percentile** price forecasts
- Useful for risk assessment and understanding potential price distributions

### 📊 SMA Strategy Signals

- Computes **Short-term (10-day)** and **Long-term (50-day)** Simple Moving Averages
- **Golden Cross** (short > long) → BUY signal
- **Death Cross** (short < long) → SELL signal

### 🤖 AI Chatbot

- Click the **Community Chat** button to open the chat interface
- Ask any trading-related question — powered by **Google Gemini 2.0 Flash**
- Examples: *"Should I buy AAPL?"*, *"What is a stop-loss?"*, *"Explain RSI indicator"*

### 💼 Portfolio

- Navigate to `/portfolio` to view your stock holdings
- Track: symbol, quantity, average price, market value, and unrealized P&L
- View a performance chart showing portfolio value over time

### 👤 User Account

- **Sign Up** at `/signup` — Create an account with username and password
- **Log In** at `/login` — Authenticate to access personalized features
- **Profile** at `/profile` — View account details, security settings, and last login time

### 📰 News Feed

- Financial news headlines fetched from **Finnhub API**
- Top 8 relevant news articles displayed with source and link
- Real-time broadcast to all connected users via WebSocket

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/signup` | Register a new user |
| `POST` | `/api/login` | Log in with credentials |
| `POST` | `/api/logout` | Log out current session |

### Trading
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/order` | Place a buy/sell order |
| `POST` | `/api/confirm_order` | Confirm a pending order |
| `GET` | `/api/orders` | Get all orders |
| `GET` | `/api/orderbook/<symbol>` | Get order book for a symbol |

### Market Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/price/<symbol>` | Get current price for a symbol |
| `GET` | `/api/market_snapshot/<symbol>` | Get full market snapshot |
| `GET` | `/api/historical/<symbol>` | Get historical OHLCV data with SMA |
| `GET` | `/api/graph/<symbol>` | Get price chart as PNG image |

### AI & Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Get LSTM price prediction |
| `POST` | `/api/simulate` | Run Monte Carlo simulation |
| `POST` | `/api/chat` | Chat with AI (Gemini) |
| `GET` | `/api/news` | Get latest financial news |

### Portfolio
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/portfolio` | Get portfolio holdings and P&L |

### Pages
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main trading dashboard |
| `GET` | `/login` | Login page |
| `GET` | `/signup` | Registration page |
| `GET` | `/portfolio` | Portfolio page |
| `GET` | `/profile` | User profile page |
| `GET` | `/community-chat` | Community chat page |
| `GET` | `/current-status` | Current market status page |

---

## 🔧 Configuration

### Database

By default, the app uses **SQLite** (`data.sqlite3` in the project root). To use **PostgreSQL**, set these in `.env`:

```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_HOST=localhost
DB_PORT=5432
```

You can also set `DATABASE_URL` directly:

```env
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/dbname
```

### Real-Time Updates

The server pushes live data every **5 seconds** via SocketIO:
- `market_snapshot_update` — Latest price, bid, ask for the tracked symbol
- `news_update` — Breaking news headlines

---

## 🧠 Data Structures & Algorithms

This project implements several advanced data structures and algorithms:

### Red-Black Tree (Order Book)
- **Purpose:** Maintains sorted bid/ask orders with O(log n) insertions and lookups
- **Implementation:** Self-balancing BST with color properties, rotations, and fix-up operations
- **Location:** `order_book.py` → `RBTree`, `RBNode` classes

### Segment Tree
- **Purpose:** Efficient range-max queries over order quantities
- **Implementation:** Bottom-up segment tree with O(log n) range queries
- **Location:** `order_book.py` → `SegmentTree` class

### Order Matching Engine
- **Purpose:** Automatically matches buy orders against the best ask and sell orders against the best bid
- **Algorithm:** Price-time priority matching
- **Location:** `order_book.py` → `OrderBook.insert_order()`

### LSTM Neural Network
- **Purpose:** Predicts future stock prices based on 60-day historical sequences
- **Architecture:** Sequential model with LSTM layers → Dense output
- **Location:** `utils.py` → `train_model()`, `predict_future()`

### Monte Carlo Simulation (GBM)
- **Purpose:** Simulates thousands of possible price paths using stochastic calculus
- **Formula:** `S(t+1) = S(t) × exp((μ - σ²/2)Δt + σ√Δt × Z)`
- **Location:** `simulation.py` → `monte_carlo_gbm()`

### SMA Crossover Strategy
- **Purpose:** Generates trading signals based on moving average crossovers
- **Signals:** Golden Cross (BUY) / Death Cross (SELL) / HOLD
- **Location:** `sma_strategy.py` → `compute_sma_from_ohlc()`

---

## 📄 License

This project is for educational and internship purposes.

---

*Built with ❤️ using Flask, SocketIO, and AI/ML*

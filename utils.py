# import yfinance as yf
# import numpy as np
# import datetime
# import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense
# from tensorflow.keras import Input


# def fetch_data(symbol):
#     end = datetime.date.today()
#     start = end - datetime.timedelta(days=365 * 2)
#     # Explicitly set auto_adjust=True to remove the FutureWarning
#     data = yf.download(symbol, start=start, end=end, auto_adjust=True)
#     return data


# def train_model(data):
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

#     X, y = [], []
#     for i in range(60, len(scaled_data)):
#         X.append(scaled_data[i - 60:i, 0])
#         y.append(scaled_data[i, 0])

#     X, y = np.array(X), np.array(y)
#     X = np.reshape(X, (X.shape[0], X.shape[1], 1))

#     # ✅ Fixed Input() warning and structure
#     model = Sequential([
#         Input(shape=(X.shape[1], 1)),
#         LSTM(50, return_sequences=True),
#         LSTM(50),
#         Dense(1)
#     ])
#     model.compile(optimizer='adam', loss='mean_squared_error')
#     model.fit(X, y, epochs=5, batch_size=32, verbose=0)

#     return model, scaler


# def predict_future(model, scaler, data, days=7):
#     last_60 = data['Close'].values[-60:].reshape(-1, 1)
#     scaled_last_60 = scaler.transform(last_60)
#     future_prices = []

#     x_input = scaled_last_60
#     for _ in range(days):
#         x_input = np.reshape(x_input, (1, 60, 1))
#         pred = model.predict(x_input, verbose=0)
#         future_prices.append(pred[0, 0])
#         x_input = np.append(x_input[:, 1:, :], [[[pred[0, 0]]]], axis=1)

#     # Convert predictions back to original scale
#     predicted_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))

#     # ✅ Generate dates that start *after* your last actual date
#     last_date = data.index[-1]
#     future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)

#     # ✅ Return as DataFrame (for plotting)
#     future_df = pd.DataFrame({
#         'Date': future_dates,
#         'Predicted': predicted_prices.flatten()
#     }).set_index('Date')

#     return future_df


# def monte_carlo_simulation(predicted_price, uncertainty=0.1, simulations=10000):
#     simulated_prices = predicted_price * (1 + np.random.normal(0, uncertainty, simulations))
#     mean_price = np.mean(simulated_prices)
#     lower_bound = np.percentile(simulated_prices, 5)
#     upper_bound = np.percentile(simulated_prices, 95)

#     return mean_price, lower_bound, upper_bound, simulated_prices


# utils.py
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ------------------- DATA FETCHING -------------------

def fetch_data(symbol, period="2y"):
    """
    Fetch historical daily stock data from Yahoo Finance.
    Returns a pandas DataFrame.
    """
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False)
        if df.empty:
            return None
        df = df.reset_index()
        df['Date'] = df['Date'].astype(str)
        df['Close'] = df['Close'].ffill()  # fill missing close values
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

# ------------------- LSTM MODEL TRAINING -------------------

def train_model(df):
    """
    Train a simple LSTM model on the 'Close' prices.
    Returns the trained model and the scaler.
    """
    close_prices = df['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)

    # Prepare sequences for LSTM
    X, y = [], []
    sequence_length = 60
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Build LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")

    # Train model
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    return model, scaler

# ------------------- FUTURE PRICE PREDICTION -------------------

def predict_future(model, scaler, df, days=7):
    """
    Predict future prices for the next 'days' days.
    """
    close_prices = df['Close'].values.reshape(-1, 1)
    scaled_data = scaler.transform(close_prices)

    last_60 = scaled_data[-60:]
    future_scaled = []

    for _ in range(days):
        x_input = np.reshape(last_60, (1, 60, 1))
        pred = model.predict(x_input, verbose=0)[0, 0]
        future_scaled.append(pred)
        last_60 = np.append(last_60[1:], [[pred]], axis=0)

    future_prices = scaler.inverse_transform(np.array(future_scaled).reshape(-1, 1)).flatten()
    return future_prices

# ------------------- MONTE CARLO SIMULATION -------------------

def monte_carlo_simulation(start_price, sims=1000, days=30, mu=0.0005, sigma=0.01):
    """
    Monte Carlo simulation of stock prices using Geometric Brownian Motion.
    Returns mean, 5% and 95% percentile prices.
    """
    final_prices = []
    for _ in range(sims):
        price = start_price
        for _ in range(days):
            price = price * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal())
        final_prices.append(price)

    mean_price = np.mean(final_prices)
    lower_bound = np.percentile(final_prices, 5)
    upper_bound = np.percentile(final_prices, 95)

    return mean_price, lower_bound, upper_bound, final_prices

# ------------------- HELPER FUNCTIONS -------------------

def create_sequences(data, sequence_length=60):
    """
    Convert array of data into sequences for LSTM input.
    """
    X, y = [], []
    for i in range(sequence_length, len(data)):
        X.append(data[i-sequence_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)



# import yfinance as yf
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense
# import datetime
# from tensorflow.keras import Input

# def fetch_data(symbol):
#     end = datetime.date.today()
#     start = end - datetime.timedelta(days=365 * 2)
#     data = yf.download(symbol, start=start, end=end)
#     return data

# def train_model(data):
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

#     X, y = [], []
#     for i in range(60, len(scaled_data)):
#         X.append(scaled_data[i-60:i, 0])
#         y.append(scaled_data[i, 0])

#     X, y = np.array(X), np.array(y)
#     X = np.reshape(X, (X.shape[0], X.shape[1], 1))

#     model = Sequential([
#         LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
#         LSTM(50),
#         Dense(1)
#     ])
#     model.compile(optimizer='adam', loss='mean_squared_error')
#     model.fit(X, y, epochs=5, batch_size=32, verbose=0)

#     return model, scaler

# def predict_future(model, scaler, data, days=7):
#     import pandas as pd

#     last_60 = data['Close'].values[-60:].reshape(-1, 1)
#     scaled_last_60 = scaler.transform(last_60)
#     future_prices = []

#     x_input = scaled_last_60
#     for _ in range(days):
#         x_input = np.reshape(x_input, (1, 60, 1))
#         pred = model.predict(x_input, verbose=0)
#         future_prices.append(pred[0, 0])
#         x_input = np.append(x_input[:, 1:, :], [[[pred[0, 0]]]], axis=1)

#     # Convert predictions back to original scale
#     predicted_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))

#     # ✅ Generate dates that start *after* your last actual date
#     last_date = data.index[-1]
#     future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)

#     # ✅ Return as DataFrame (better for plotting)
#     future_df = pd.DataFrame({
#         'Date': future_dates,
#         'Predicted': predicted_prices.flatten()
#     }).set_index('Date')

#     return future_df
#     # last_60 = data['Close'].values[-60:].reshape(-1, 1)
#     # scaled_last_60 = scaler.transform(last_60)
#     # future_prices = []

#     # x_input = scaled_last_60
#     # for _ in range(days):
#     #     x_input = np.reshape(x_input, (1, 60, 1))
#     #     pred = model.predict(x_input, verbose=0)
#     #     future_prices.append(pred[0, 0])
#     #     x_input = np.append(x_input[:, 1:, :], [[[pred[0, 0]]]], axis=1)

#     # return scaler.inverse_transform(np.array(future_prices).reshape(-1, 1))

# def monte_carlo_simulation(predicted_price, uncertainty=0.1, simulations=10000):
#     simulated_prices = predicted_price * (1 + np.random.normal(0, uncertainty, simulations))
#     mean_price = np.mean(simulated_prices)
#     lower_bound = np.percentile(simulated_prices, 5)
#     upper_bound = np.percentile(simulated_prices, 95)

#     return mean_price, lower_bound, upper_bound, simulated_prices

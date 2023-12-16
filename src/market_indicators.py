import requests
import numpy as np
import pandas as pd

# Constants for moving averages
SHORT_TERM_MA = 50
LONG_TERM_MA = 200


# Function to fetch historical price data
def fetch_price_data(coin, days):
    url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}'
    response = requests.get(url)
    data = response.json()
    prices = [item[1] for item in data['prices']]
    return prices


# Function to calculate moving average
def calculate_moving_average(prices, window):
    return pd.Series(prices).rolling(window=window).mean().tolist()


# Function to calculate RSI
def calculate_rsi(prices, period=14):
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.tolist()


# Function to calculate MACD
def calculate_macd(prices, short_term=12, long_term=26, signal=9):
    short_ema = pd.Series(prices).ewm(span=short_term, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_term, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd.tolist(), signal_line.tolist()

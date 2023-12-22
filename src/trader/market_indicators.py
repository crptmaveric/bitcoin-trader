import requests
import numpy as np
import pandas as pd

# Constants for moving averages
SHORT_TERM_MA = 50
LONG_TERM_MA = 200


def fetch_price_data(coin, days):
    """
    Fetch historical price data for a given cryptocurrency over a specified number of days.

    Parameters:
    coin (str): The cryptocurrency for which to fetch data (e.g., 'bitcoin').
    days (int): The number of past days to fetch data for.

    Returns:
    list: A list of price values.
    """
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}'
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        prices = [item[1] for item in data['prices']]
        return prices
    except Exception as e:
        print(f"Error fetching price data for {coin}: {e}")
        return []


def calculate_moving_average(data, window_size):
    """
    Calculate the moving average for the given data and window size.
    """
    return data['price'].rolling(window=window_size).mean()


def calculate_RSI(data, period=14):
    """
    Calculate the Relative Strength Index (RSI) for the given data.
    """
    delta = data['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    return RSI


def calculate_MACD(data, short_term_period=12, long_term_period=26, signal_period=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for the given data.
    """
    short_term_ema = data['price'].ewm(span=short_term_period, adjust=False).mean()
    long_term_ema = data['price'].ewm(span=long_term_period, adjust=False).mean()

    MACD = short_term_ema - long_term_ema
    MACD_signal = MACD.ewm(span=signal_period, adjust=False).mean()
    return MACD, MACD_signal

# Example usage
# data = pd.DataFrame({'price': [/* historical prices */]})
# moving_avg = calculate_moving_average(data, 50)  # 50-day moving average
# rsi = calculate_RSI(data)
# macd, macd_signal = calculate_MACD(data)

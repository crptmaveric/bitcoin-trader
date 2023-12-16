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


def calculate_moving_average(prices, window):
    """
    Calculate the moving average for a set of prices.

    Parameters:
    prices (list): A list of price values.
    window (int): The window size for the moving average calculation.

    Returns:
    list: A list of moving average values.
    """
    try:
        return pd.Series(prices).rolling(window=window).mean().tolist()
    except Exception as e:
        print(f"Error calculating moving average: {e}")
        return []


def calculate_rsi(prices, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a set of prices.

    Parameters:
    prices (list): A list of price values.
    period (int): The period over which to calculate the RSI.

    Returns:
    list: A list of RSI values.
    """
    try:
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.tolist()
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return []


def calculate_macd(prices, short_term=12, long_term=26, signal=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for a set of prices.

    Parameters:
    prices (list): A list of price values.
    short_term (int): The short-term EMA period.
    long_term (int): The long-term EMA period.
    signal (int): The signal line EMA period.

    Returns:
    tuple: A tuple containing two lists (MACD values and signal line values).
    """
    try:
        short_ema = pd.Series(prices).ewm(span=short_term, adjust=False).mean()
        long_ema = pd.Series(prices).ewm(span=long_term, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd.tolist(), signal_line.tolist()
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return [], []

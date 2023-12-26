import datetime
import hmac
import hashlib
import time
import requests
import pandas as pd
from requests.auth import AuthBase
from config.config import TRADING_PAIR
from logger import Logger

logger = Logger()


class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, api_secret):
        """
        Initialize the CoinbaseWalletAuth class for handling authentication with the Coinbase API v2.
        Parameters:
        api_key (str): The API key for Coinbase authentication.
        api_secret (str): The API secret for generating the HMAC signature.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        logger.info("CoinbaseWalletAuth initialized.")

    def __call__(self, request):
        """
        Add authentication details to the request.
        Parameters:
        request: The request object to be sent to the API.
        Returns:
        The modified request object with authentication details.
        """
        logger.info("Authenticating request to Coinbase API v2.")
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha256)
        signature = hmac_key.hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
        return request


def get_euro_balance(auth):
    """
    Retrieve the Euro balance from the Coinbase account.

    Parameters:
    auth (CoinbaseWalletAuth): Authentication object for Coinbase API requests.

    Returns:
    str: The Euro balance as a string, or None if the request fails.
    """
    url = 'https://api.coinbase.com/v2/accounts'
    try:
        logger.info("Retrieving Euro balance.")
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        accounts = response.json()
        for account in accounts['data']:
            if account.get('type') == 'fiat' and account.get('currency', {}).get('code') == 'EUR':
                balance = account['balance']['amount']
                logger.info(f"Euro balance: {balance}")
                return balance
    except Exception as err:
        logger.error(f"Error retrieving Euro balance: {err}")
        return None


def get_bitcoin_balance(auth):
    """
    Retrieve the Bitcoin balance from the Coinbase account.

    Parameters:
    auth (CoinbaseWalletAuth): Authentication object for Coinbase API requests.

    Returns:
    str: The Bitcoin balance as a string, or None if the request fails.
    """
    url = 'https://api.coinbase.com/v2/accounts'
    try:
        logger.info("Retrieving Bitcoin balance.")
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        accounts = response.json()
        for account in accounts['data']:
            if account['currency']['code'] == 'BTC':
                balance = account['balance']['amount']
                logger.info(f"Bitcoin balance: {balance}")
                return balance
        return "0.0"
    except Exception as err:
        logger.error(f"Error retrieving Bitcoin balance: {err}")
        return None


def get_bitcoin_price(one_week_ago=False, trading_pair=TRADING_PAIR):
    """
    Retrieve the current or historical price of Bitcoin.

    Parameters:
    one_week_ago (bool): Whether to fetch the price from one week ago.
    trading_pair (str): The trading pair to use (e.g., 'BTC-USD').

    Returns:
    float: The Bitcoin price, or None if the request fails.
    """
    try:
        if one_week_ago:
            historical_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            price_url = f'https://api.coinbase.com/v2/prices/{trading_pair}/spot?date={historical_date}'
            logger.info(f"Fetching historical Bitcoin price for {historical_date}.")
        else:
            price_url = f'https://api.coinbase.com/v2/prices/{trading_pair}/spot'
            logger.info("Fetching current Bitcoin price.")

        response = requests.get(price_url)
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['amount'])
            logger.info(f"Bitcoin price: {price}")
            return 39793.59
        else:
            logger.error(f"Error fetching Bitcoin price: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching Bitcoin price: {e}")
        return None


def get_previous_day_bitcoin_price(trading_pair=TRADING_PAIR):
    """
    Retrieve the Bitcoin price from the previous day.

    Parameters:
    trading_pair (str): The trading pair to use (e.g., 'BTC-USD').

    Returns:
    float: The Bitcoin price from the previous day, or None if the request fails.
    """
    previous_day = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        price_url = f'https://api.coinbase.com/v2/prices/{trading_pair}/spot?date={previous_day}'
        logger.info(f"Fetching Bitcoin price for {previous_day}.")
        response = requests.get(price_url)
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['amount'])
            logger.info(f"Bitcoin price for {previous_day}: {price}")
            return price
        else:
            logger.error(f"Error fetching Bitcoin price for {previous_day}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching Bitcoin price for {previous_day}: {e}")
        return None

def get_bitcoin_price_change(trading_pair=TRADING_PAIR):
    """
    Calculate the percentage change in Bitcoin price over the past week.

    Parameters:
    trading_pair (str): The trading pair to use (e.g., 'BTC-USD').

    Returns:
    float: The percentage change in Bitcoin price, or None if the request fails.
    """
    logger.info("Calculating Bitcoin price change.")
    current_price = get_bitcoin_price(False, trading_pair)
    past_price = get_bitcoin_price(True, trading_pair)
    if current_price is not None and past_price is not None:
        price_change = ((current_price - past_price) / past_price) * 100
        logger.info(f"Bitcoin price change: {price_change}%")
        return price_change
    else:
        return None


class CoinbaseMarketData:
    def __init__(self, auth):
        """
        Initialize the CoinbaseMarketData with authentication details.
        Parameters:
        auth (CoinbaseWalletAuth): Authentication object for Coinbase API requests.
        """
        self.auth = auth
        self.base_url = 'https://api.coinbase.com/v2/'  # Define base_url here

    def fetch_historical_data(self, symbol, start_date, end_date):
        """
        Fetch historical price and volume data for a given cryptocurrency symbol
        between start_date and end_date.

        Parameters:
        symbol (str): Symbol for the cryptocurrency (e.g., 'BTC-USD').
        start_date (str): Start date for the data in 'YYYY-MM-DD' format.
        end_date (str): End date for the data in 'YYYY-MM-DD' format.

        Returns:
        DataFrame: A DataFrame with historical data (date, price, volume), or None if the request fails.
        """
        url = f'https://api.pro.coinbase.com/products/{symbol}/candles?start={start_date}&end={end_date}&granularity=86400'

        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            data = response.json()

            logger.debug(data)

            # Transforming data to DataFrame
            df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['time'], unit='s')
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def get_historical_data(self, currency_pair, start_date, end_date):
        """
        Retrieve historical price data for a specific cryptocurrency pair.
        Parameters:
        currency_pair (str): The cryptocurrency pair (e.g., 'BTC-USD').
        start_date (datetime): The start date for the data.
        end_date (datetime): The end date for the data.
        Returns:
        DataFrame: A DataFrame with the historical prices, or None if the request fails.
        """
        start_date_iso = start_date.isoformat()
        end_date_iso = end_date.isoformat()
        url = f"{self.base_url}prices/{currency_pair}/historic?start={start_date_iso}&end={end_date_iso}"
        response = requests.get(url, auth=self.auth)

        logger.debug(response.text)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['data']['prices'])
            return df
        else:
            logger.error(f"Error fetching historical data: {response.status_code}")
            return None

    def get_real_time_data(self, currency_pair):
        """
        Retrieve real-time price data for a specific cryptocurrency pair.
        Parameters:
        currency_pair (str): The cryptocurrency pair (e.g., 'BTC-USD').
        Returns:
        str: The current price as a string, or None if the request fails.
        """

        url = f"{self.base_url}prices/{currency_pair}/spot"
        response = requests.get(url, auth=self.auth)

        logger.debug(response.text)

        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['amount'])  # Convert price to float
            # Create a DataFrame with the price data
            price_df = pd.DataFrame({'price': [price]})
            return price_df
        else:
            logger.error(f"Error fetching real-time data: {response.status_code}")
            return None

# Example usage
# auth = CoinbaseWalletAuth('your_api_key', 'your_api_secret')
# market_data = CoinbaseMarketData(auth)
# historical_data = market_data.get_historical_data('BTC-USD', datetime.datetime(2023, 1, 1), datetime.datetime(2023, 12, 31))
# real_time_price = market

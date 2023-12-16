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
        self.api_key = api_key
        self.api_secret = api_secret
        logger.info("CoinbaseWalletAuth initialized.")

    def __call__(self, request):
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
            return price
        else:
            logger.error(f"Error fetching Bitcoin price: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching Bitcoin price: {e}")
        return None


def get_bitcoin_price_change(trading_pair=TRADING_PAIR):
    logger.info("Calculating Bitcoin price change.")
    current_price = get_bitcoin_price(False, trading_pair)
    past_price = get_bitcoin_price(True, trading_pair)
    price_change = ((current_price - past_price) / past_price) * 100
    logger.info(f"Bitcoin price change: {price_change}%")
    return price_change


class CoinbaseMarketData:
    def __init__(self, auth):
        """
        Initialize the CoinbaseMarketData with authentication details.

        :param auth: Authentication object for Coinbase API.
        """
        self.auth = auth

    def fetch_historical_data(self, symbol, start_date, end_date):
        """
        Fetch historical price and volume data for a given cryptocurrency symbol
        between start_date and end_date.

        :param symbol: Symbol for the cryptocurrency (e.g., 'BTC-USD').
        :param start_date: Start date for the data in 'YYYY-MM-DD' format.
        :param end_date: End date for the data in 'YYYY-MM-DD' format.
        :return: DataFrame with historical data (date, price, volume).
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

# Your existing CoinbaseWalletAuth class and other functionalities

# Example usage:
# auth = CoinbaseWalletAuth(API_KEY, API_SECRET)
# market_data = CoinbaseMarketData(auth)
# historical_data = market_data.fetch_historical_data('BTC-USD', '2023-01-01', '2023-01-31')
# print(historical_data)
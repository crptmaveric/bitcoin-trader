import datetime
import hmac
import hashlib
import time
import requests
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

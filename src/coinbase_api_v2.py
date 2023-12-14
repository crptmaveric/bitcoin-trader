import datetime
import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase
from config.config import TRADING_PAIR

class CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, request):
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
        response = requests.get(url, auth=auth)
        print(response.text)
        response.raise_for_status()
        accounts = response.json()
        for account in accounts['data']:
            if account.get('type') == 'fiat' and account.get('currency', {}).get('code') == 'EUR':
                return account['balance']['amount']  # Return the balance amount in Euro
    except Exception as err:
        print(f"Error retrieving Euro balance: {err}")
        return None


def get_bitcoin_balance(auth):
    url = 'https://api.coinbase.com/v2/accounts'
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        accounts = response.json()
        for account in accounts['data']:
            if account['currency']['code'] == 'BTC':  # Změna zde, hledáme kód měny
                return account['balance']['amount']
        return "0.0"
    except Exception as err:
        print(f"Chyba při získávání zůstatku Bitcoinů: {err}")
        return None


def get_bitcoin_price(one_week_ago=False, trading_pair=TRADING_PAIR):
    # Endpoint for current Bitcoin price
    current_price_url = f'https://api.coinbase.com/v2/prices/{trading_pair}/spot'

    # For historical price, calculate the date one week ago
    if one_week_ago:
        historical_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        historical_price_url = f'https://api.coinbase.com/v2/prices/{trading_pair}/spot?date={historical_date}'
        price_url = historical_price_url
    else:
        price_url = current_price_url

    # Fetching the Bitcoin price from Coinbase API
    response = requests.get(price_url)
    if response.status_code == 200:
        data = response.json()
        return float(data['data']['amount'])
    else:
        print(f"Error fetching Bitcoin price: {response.status_code}")
        return None


def get_bitcoin_price_change(trading_pair=TRADING_PAIR):
    # Fetching the current and past week's Bitcoin prices
    # Assuming the existence of a function 'get_bitcoin_price' that returns the current Bitcoin price
    current_price = get_bitcoin_price(False, trading_pair)

    # Fetching the Bitcoin price from a week ago
    # This could involve storing historical prices or using an API that provides historical data
    past_price = get_bitcoin_price(True, trading_pair)

    # Calculate the percentage price change
    price_change = ((current_price - past_price) / past_price) * 100
    return price_change

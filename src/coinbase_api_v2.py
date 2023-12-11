import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase


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

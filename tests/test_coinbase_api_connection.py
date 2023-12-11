import unittest
import requests
from src.coinbase_api import CoinbaseAuth

class TestCoinbaseAPIConnection(unittest.TestCase):
    def setUp(self):
        # Nahraďte těmito hodnotami vaše sandbox API klíče
        self.api_key = 'sandbox_api_key'
        self.secret_key = 'sandbox_secret_key'
        self.passphrase = 'sandbox_passphrase'
        self.auth = CoinbaseAuth(self.api_key, self.secret_key, self.passphrase)

    def test_api_connection(self):
        # Testovací volání na sandbox Coinbase API
        url = "https://api-public.sandbox.pro.coinbase.com/accounts"
        response = requests.get(url, auth=self.auth)

        print(response.json())

        # Ověřte status kód a základní strukturu odpovědi
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())

if __name__ == '__main__':
    unittest.main()


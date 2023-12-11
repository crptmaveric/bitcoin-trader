import unittest
import requests
from src.coinbase_api import CoinbaseAuth

class TestCoinbaseAuth(unittest.TestCase):
    def setUp(self):
        self.api_key = 'api_key'
        self.secret_key = 'secret_key'
        self.passphrase = 'passphrase'
        self.auth = CoinbaseAuth(self.api_key, self.secret_key, self.passphrase)

    def test_headers(self):
        # Tento test len skontroluje, či sú hlavičky pridávané
        request = requests.Request('GET', 'https://api.coinbase.com/')
        prepared = request.prepare()
        result = self.auth(prepared)

        self.assertIn('CB-ACCESS-KEY', result.headers)
        self.assertIn('CB-ACCESS-SIGN', result.headers)
        self.assertIn('CB-ACCESS-TIMESTAMP', result.headers)
        self.assertIn('CB-ACCESS-PASSPHRASE', result.headers)
        self.assertIn('Content-Type', result.headers)

if __name__ == '__main__':
    unittest.main()

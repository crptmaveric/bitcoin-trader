import unittest
import requests
from unittest.mock import patch
from src.coinbase_api import CoinbaseAuth, buy_bitcoin

class TestCoinbaseAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = 'test_api_key'
        self.secret_key = 'test_secret_key'
        self.passphrase = 'test_passphrase'
        self.auth = CoinbaseAuth(self.api_key, self.secret_key, self.passphrase)

    def test_auth_headers(self):
        request = requests.Request('GET', 'https://api.coinbase.com/')
        prepared = request.prepare()
        result = self.auth(prepared)

        self.assertIn('CB-ACCESS-KEY', result.headers)
        self.assertIn('CB-ACCESS-SIGN', result.headers)
        self.assertIn('CB-ACCESS-TIMESTAMP', result.headers)
        self.assertIn('CB-ACCESS-PASSPHRASE', result.headers)
        self.assertIn('Content-Type', result.headers)

    @patch('requests.post')
    def test_buy_bitcoin(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.json.return_value = {'data': {'subtotal': {'amount': '1000'}}}

        response = buy_bitcoin(100, self.auth)

        self.assertEqual(response, mock_response.json.return_value)

if __name__ == '__main__':
    unittest.main()

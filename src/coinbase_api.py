import jwt
import time
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from logger import Logger

logger = Logger()


class CoinbaseAdvancedAuth:
    def __init__(self, key_name, private_key):
        self.key_name = key_name
        self.private_key = private_key
        logger.info("CoinbaseAdvancedAuth initialized.")

    def generate_jwt(self, request_method, request_host, request_path, service_name):
        try:
            logger.info("Generating JWT for Coinbase Advanced Trading API.")
            uri = f"{request_method} {request_host}{request_path}"
            private_key_bytes = self.private_key.encode('utf-8')
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None,
                                                             backend=default_backend())
            jwt_payload = {
                'sub': self.key_name,
                'iss': "coinbase-cloud",
                'nbf': int(time.time()),
                'exp': int(time.time()) + 60,
                'aud': [service_name],
                'uri': uri,
            }
            jwt_token = jwt.encode(
                jwt_payload,
                private_key,
                algorithm='ES256',
                headers={'kid': self.key_name, 'nonce': str(int(time.time()))},
            )
            return jwt_token
        except Exception as e:
            logger.error(f"Error generating JWT: {e}")
            return None


def get_order_details(api_key, private_key, order_id):
    try:
        logger.info(f"Fetching order details for order_id: {order_id}")
        auth = CoinbaseAdvancedAuth(api_key, private_key)
        jwt_token = auth.generate_jwt('GET', 'api.coinbase.com', f'/api/v3/brokerage/orders/historical/{order_id}',
                                      'retail_rest_api_proxy')
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = requests.get(f'https://api.coinbase.com/api/v3/brokerage/orders/historical/{order_id}',
                                headers=headers)
        if response.status_code == 200:
            order_details = response.json()['order']
            logger.info(f"Order details retrieved: {order_details}")
            return {
                'average_filled_price': order_details.get('average_filled_price'),
                'filled_size': order_details.get('filled_size'),
                'created_time': order_details.get('created_time'),
                'status': order_details.get('status')
            }
        else:
            logger.warning(f"Failed to get order details for {order_id}. Response code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        return None


def wait_for_order_completion(api_key, private_key, order_id, timeout=30, interval=5):
    logger.info(f"Waiting for order completion: {order_id}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            order_details = get_order_details(api_key, private_key, order_id)
            if order_details:
                status = order_details.get('status')
                logger.info(f"Checking order status: {status}")
                if status in ['FILLED', 'CANCELLED', 'EXPIRED', 'FAILED']:
                    return True
            else:
                logger.warning("Order details not received, retrying...")
        except Exception as e:
            logger.error(f"Error during order status check: {e}")
        time.sleep(interval)
    logger.warning("Timeout reached, order may not have completed.")
    return False


def buy_bitcoin(api_key, private_key, client_order_id, product_id, amount, order_type='market_market_ioc'):
    try:
        logger.info(f"Placing a buy order for Bitcoin. Order type: {order_type}")
        auth = CoinbaseAdvancedAuth(api_key, private_key)
        jwt_token = auth.generate_jwt('POST', 'api.coinbase.com', '/api/v3/brokerage/orders', 'retail_rest_api_proxy')
        headers = {"Authorization": f"Bearer {jwt_token}"}

        if order_type == 'market_market_ioc':
            order_configuration = {
                "market_market_ioc": {
                    "quote_size": str(amount)
                }
            }
        else:
            logger.error("Unsupported order type")
            raise ValueError("Unsupported order type")

        data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "side": "BUY",
            "order_configuration": order_configuration
        }

        logger.info(data)
        exit(111)

        # response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                logger.info(f"Order successfully created: {response_data['success_response']['order_id']}")
                return {
                    "status": "success",
                    "order_id": response_data['success_response']['order_id'],
                    "details": "Order successfully created."
                }
            else:
                logger.warning(f"Order failure: {response_data.get('failure_reason')}")
                return {
                    "status": "failure",
                    "reason": response_data.get('failure_reason'),
                    "details": response_data.get('error_response', {}).get('error_details',
                                                                           'No additional details provided.')
                }
        else:
            logger.error(f"Unexpected error response: {response.text}")
            error_data = response.json()
            return {
                "status": "error",
                "error": error_data.get('error'),
                "code": error_data.get('code'),
                "message": error_data.get('message'),
                "details": error_data.get('details', 'No additional details provided.')
            }
    except Exception as err:
        logger.error(f"Exception during buy order request: {err}")
        return {
            "status": "exception",
            "message": str(err),
            "details": "An exception occurred while sending the buy order request."
        }


def sell_bitcoin(api_key, private_key, client_order_id, product_id, amount, order_type='market_market_ioc'):
    try:
        logger.info(f"Placing a sell order for Bitcoin. Order type: {order_type}")
        auth = CoinbaseAdvancedAuth(api_key, private_key)
        jwt_token = auth.generate_jwt('POST', 'api.coinbase.com', '/api/v3/brokerage/orders', 'retail_rest_api_proxy')
        headers = {"Authorization": f"Bearer {jwt_token}"}

        if order_type == 'market_market_ioc':
            order_configuration = {
                "market_market_ioc": {
                    "base_size": str(amount)  # Amount of base currency to sell
                }
            }
        else:
            logger.error("Unsupported order type")
            raise ValueError("Unsupported order type")

        data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "side": "SELL",
            "order_configuration": order_configuration
        }

        logger.info(data)
        exit(111)
        # response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                logger.info(f"Order successfully created: {response_data['success_response']['order_id']}")
                return {
                    "status": "success",
                    "order_id": response_data['success_response']['order_id'],
                    "details": "Order successfully created."
                }
            else:
                logger.warning(f"Order failure: {response_data.get('failure_reason')}")
                return {
                    "status": "failure",
                    "reason": response_data.get('failure_reason'),
                    "details": response_data.get('error_response', {}).get('error_details',
                                                                           'No additional details provided.')
                }
        else:
            logger.error(f"Unexpected error response: {response.text}")
            error_data = response.json()
            return {
                "status": "error",
                "error": error_data.get('error'),
                "code": error_data.get('code'),
                "message": error_data.get('message'),
                "details": error_data.get('details', 'No additional details provided.')
            }
    except Exception as err:
        logger.error(f"Exception during sell order request: {err}")
        return {
            "status": "exception",
            "message": str(err),
            "details": "An exception occurred while sending the sell order request."
        }

# Example usage
# api_key = 'your_api_key'
# private_key = 'your_private_key'
# buy_order = buy_bitcoin(api_key, private_key, 'unique_client_order_id', 'BTC-USD', 0.1)
# sell_order = sell_bitcoin(api_key, private_key, 'unique_client_order_id', 'BTC-USD', 0.1)

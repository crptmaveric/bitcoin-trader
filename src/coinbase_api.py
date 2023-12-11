import jwt
import time
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class CoinbaseAdvancedAuth:
    def __init__(self, key_name, private_key):
        self.key_name = key_name
        self.private_key = private_key

    def generate_jwt(self, request_method, request_host, request_path, service_name):
        uri = f"{request_method} {request_host}{request_path}"
        private_key_bytes = self.private_key.encode('utf-8')
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
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


def get_order_details(api_key, private_key, order_id):
    auth = CoinbaseAdvancedAuth(api_key, private_key)
    jwt_token = auth.generate_jwt('GET', 'api.coinbase.com', f'/api/v3/brokerage/orders/historical/{order_id}',
                                  'retail_rest_api_proxy')
    headers = {"Authorization": f"Bearer {jwt_token}"}

    response = requests.get(f'https://api.coinbase.com/api/v3/brokerage/orders/historical/{order_id}', headers=headers)
    if response.status_code == 200:
        order_details = response.json()['order']
        print(order_details)
        return {
            'average_filled_price': order_details.get('average_filled_price'),
            'filled_size': order_details.get('filled_size'),
            'created_time': order_details.get('created_time'),
            'status': order_details.get('status')
        }
    else:
        return None


def wait_for_order_completion(api_key, private_key, order_id, timeout=30, interval=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            order_details = get_order_details(api_key, private_key, order_id)
            if order_details:
                status = order_details.get('status')
                print(f"Checking order status: {status}")  # Logovanie stavu
                if status in ['FILLED', 'CANCELLED', 'EXPIRED', 'FAILED']:
                    return True
            else:
                print("Order details not received, retrying...")
        except Exception as e:
            print(f"Error during order status check: {e}")
        time.sleep(interval)
    print("Timeout reached, order may not have completed.")
    return False


def buy_bitcoin(api_key, private_key, client_order_id, product_id, amount, order_type='market_market_ioc'):
    auth = CoinbaseAdvancedAuth(api_key, private_key)
    jwt_token = auth.generate_jwt('POST', 'api.coinbase.com', '/api/v3/brokerage/orders', 'retail_rest_api_proxy')
    headers = {"Authorization": f"Bearer {jwt_token}"}

    # Construct the order body based on the order type
    if order_type == 'market_market_ioc':
        order_configuration = {
            "market_market_ioc": {
                "quote_size": str(amount)  # Amount of quote currency to spend on the order
            }
        }
    else:
        # Other order types (e.g., limit_limit_gtc) can be implemented here
        raise ValueError("Unsupported order type")

    data = {
        "client_order_id": client_order_id,
        "product_id": product_id,
        "side": "BUY",
        "order_configuration": order_configuration
    }

    try:
        response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)

        print(response.text)

        # Check if the response is successful
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                # Order successful
                return {
                    "status": "success",
                    "order_id": response_data['success_response']['order_id'],
                    "details": "Order successfully created."
                }
            else:
                # Order failure with detailed reason
                return {
                    "status": "failure",
                    "reason": response_data.get('failure_reason'),
                    "details": response_data.get('error_response', {}).get('error_details',
                                                                           'No additional details provided.')
                }
        else:
            # Handle unexpected error responses
            error_data = response.json()
            return {
                "status": "error",
                "error": error_data.get('error'),
                "code": error_data.get('code'),
                "message": error_data.get('message'),
                "details": error_data.get('details', 'No additional details provided.')
            }

    except Exception as err:
        # Handle exceptions related to the request
        return {
            "status": "exception",
            "message": str(err),
            "details": "An exception occurred while sending the buy order request."
        }

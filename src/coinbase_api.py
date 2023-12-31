import datetime
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

        order_configuration = {
            "market_market_ioc": {
                "quote_size": str(amount)
            }
        }

        data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "side": "BUY",
            "order_configuration": order_configuration
        }

        response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                logger.info(f"Order successfully created: {response_data['success_response']['order_id']}")
                order_id = response_data['success_response']['order_id']

                return {
                    "status": "success",
                    "order_id": order_id,
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

        response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                logger.info(f"Order successfully created: {response_data['success_response']['order_id']}")
                order_id = response_data['success_response']['order_id']

                return {
                    "status": "success",
                    "order_id": order_id,
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


def get_previous_day_bitcoin_price(api_key, private_key, product_id):
    """
    Retrieve the closing Bitcoin price from the previous day using the Coinbase Advanced Trading API.

    Parameters:
    api_key (str): API key for Coinbase Advanced Trading API.
    private_key (str): Private key for generating the JWT.
    trading_pair (str): The trading pair to use (e.g., 'BTC-USD').

    Returns:
    float: The closing Bitcoin price from the previous day, or None if the request fails.
    """
    previous_day_start = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                                                        microsecond=0)
    previous_day_end = previous_day_start + datetime.timedelta(days=1)

    # Convert start and end times to UNIX timestamp and then to string
    start_timestamp = str(int(previous_day_start.timestamp()))
    end_timestamp = str(int(previous_day_end.timestamp()))

    auth = CoinbaseAdvancedAuth(api_key, private_key)
    jwt_token = auth.generate_jwt('GET', 'api.coinbase.com', f'/api/v3/brokerage/products/{product_id}/candles',
                                  'retail_rest_api_proxy')

    if jwt_token is None:
        logger.error("Failed to generate JWT token.")
        return None

    headers = {"Authorization": f"Bearer {jwt_token}"}

    url = f'https://api.coinbase.com/api/v3/brokerage/products/{product_id}/candles'
    params = {
        "start": start_timestamp,
        "end": end_timestamp,
        "granularity": "ONE_DAY"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Extracting data from the response
        data = response.json()
        candles = data.get('candles', [])
        if candles and len(candles) > 0:
            close_price = float(candles[0]['close'])  # Extracting the close price from the first candle
            logger.info(f"Previous day Bitcoin closing price: {close_price}")
            return close_price
        else:
            logger.error("No data returned for the previous day Bitcoin price.")
            return None
    except Exception as e:
        logger.error(f"Exception fetching Bitcoin price for the previous day: {e}")
        return None


def create_stop_order(api_key, private_key, client_order_id, product_id, base_size, stop_price, limit_price,
                      stop_direction, order_type='stop_limit_stop_limit_gtc'):
    """
    Create a stop order on the Coinbase Advanced Trading API. This can be used for stop-loss or take-profit orders.

    Parameters:
    api_key (str): Your API key for Coinbase authentication.
    private_key (str): Your private key for Coinbase authentication.
    client_order_id (str): A unique ID provided by the client for their own identification purposes.
                           This ID differs from the order_id generated for the order. If the ID provided
                           is not unique, the order fails to be created, and the order corresponding to
                           that ID is returned.
    product_id (str): The product ID for which this order is created (e.g., 'BTC-USD').
    base_size (str): The amount of base currency to spend on order.
    stop_price (str): The price at which the order should trigger. For a stop-loss order, this is typically
                      set below the current market price, and for a take-profit order, it's set above the
                      current market price.
    limit_price (str): The ceiling price at which the order should be filled. This ensures that the order
                       won't be filled at a price worse than this limit price.
    stop_direction (str): Indicates the direction for the stop price. Possible values are:
                          'STOP_DIRECTION_STOP_UP' - triggers when the last trade price goes above the stop price.
                          'STOP_DIRECTION_STOP_DOWN' - triggers when the last trade price goes below the stop price.
    order_type (str, optional): The type of the stop order. Default is 'stop_limit_stop_limit_gtc'.
                                'gtc' (Good Till Canceled) orders remain open on the book until canceled.

    Returns:
    dict: A dictionary with the response data from the API, including order details or error messages.
    """
    try:
        logger.info(f"Creating stop order for {product_id}. Stop price: {stop_price}, Limit price: {limit_price}")
        auth = CoinbaseAdvancedAuth(api_key, private_key)
        jwt_token = auth.generate_jwt('POST', 'api.coinbase.com', '/api/v3/brokerage/orders', 'retail_rest_api_proxy')
        headers = {"Authorization": f"Bearer {jwt_token}"}

        order_configuration = {
            order_type: {
                "base_size": str(base_size),
                "limit_price": str(limit_price),
                "stop_price": str(stop_price),
                "stop_direction": stop_direction
            }
        }

        data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "order_configuration": order_configuration
        }

        response = requests.post('https://api.coinbase.com/api/v3/brokerage/orders', headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                logger.info(f"Stop order successfully created: {response_data['success_response']['order_id']}")
                return response_data['success_response']
            else:
                logger.warning(f"Failed to create stop order: {response_data.get('failure_reason')}")
                return {"status": "failure", "reason": response_data.get('failure_reason')}
        else:
            logger.error(f"Unexpected error response: {response.text}")
            return {"status": "error", "error": response.text}
    except Exception as e:
        logger.error(f"Exception during stop order request: {e}")
        return {"status": "exception", "message": str(e)}

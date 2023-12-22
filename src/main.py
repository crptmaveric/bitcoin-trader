import uuid
import schedule
import time
from src.coinbase_api import CoinbaseAdvancedAuth, buy_bitcoin, get_order_details, wait_for_order_completion
from src.coinbase_api_v2 import CoinbaseWalletAuth, get_euro_balance, get_bitcoin_price_change
from src.database import create_database, log_transaction, log_uninvested_balance
from src.investment_logic import get_fear_and_greed_index, adaptive_average_cost, \
    adaptive_cost_average_with_market_timing
from config.config import API_KEY, MONTHLY_LIMIT, FREQUENCY, INVESTMENT_DAY, TRADING_PAIR, PRIVATE_KEY, API_KEY_V2, \
    API_SECRET_V2, INVESTMENT_STRATEGY
from logger import Logger

logger = Logger()


def load_private_key_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            logger.info("Private key successfully loaded.")
            return file.read()
    except Exception as e:
        logger.error(f"Error loading private key: {e}")
        return None


def execute_investment():
    logger.info("Starting execute_investment function.")
    private_key = PRIVATE_KEY
    auth = CoinbaseAdvancedAuth(API_KEY, private_key)
    auth_v2 = CoinbaseWalletAuth(API_KEY_V2, API_SECRET_V2)

    index_value = get_fear_and_greed_index()
    btc_price_change = get_bitcoin_price_change()

    if INVESTMENT_STRATEGY == 'adaptive_cost_average_with_market_timing':
        investment_amount = adaptive_cost_average_with_market_timing(index_value, btc_price_change, MONTHLY_LIMIT,
                                                                     FREQUENCY)
    else:
        investment_amount = adaptive_average_cost(index_value, MONTHLY_LIMIT, FREQUENCY)

    euro_balance = get_euro_balance(auth_v2)

    if euro_balance is None or float(euro_balance) < investment_amount:
        logger.warning(f"Not enough funds. Available balance: €{euro_balance}, Required: €{investment_amount}")
        return

    logger.info(f"Available balance: €{euro_balance}")

    client_order_id = str(uuid.uuid4())
    response = buy_bitcoin(API_KEY, private_key, client_order_id, TRADING_PAIR, investment_amount)

    if response and response.get('status') == 'success':
        order_id = response['order_id']

        if wait_for_order_completion(API_KEY, private_key, order_id):  # Waiting for order completion
            order_details = get_order_details(API_KEY, private_key, order_id)  # Fetching additional order details

            if order_details:
                log_transaction(
                    order_id=order_id,
                    invested_amount=investment_amount,
                    bitcoin_purchased=order_details['filled_size'],
                    purchase_price=order_details['average_filled_price'],
                    purchase_time=order_details['created_time']
                )
                logger.info(f"Transaction logged: {order_details}")
                logger.debug(f"Order details: {order_details}")

                if investment_amount < MONTHLY_LIMIT:
                    uninvested_amount = MONTHLY_LIMIT - investment_amount
                    current_date = time.strftime("%Y-%m-%d")
                    month_year = time.strftime("%m-%Y")
                    log_uninvested_balance(month_year, current_date, uninvested_amount)
                    logger.info(f"Uninvested balance {uninvested_amount} logged for {current_date}")
            else:
                logger.error("Failed to fetch order details for logging.")
        else:
            logger.error("Order was not completed in the expected time frame.")
    else:
        logger.error("Buy bitcoin operation failed or incomplete response.")

    logger.info("execute_investment function completed.")


create_database()
logger.info("Database created.")

# # Main Execution
#
# bot = TradingBot()
# bot.start_trading()
#
# exit(111)

schedule_map = {
    'monday': schedule.every().monday,
    'tuesday': schedule.every().tuesday,
    'wednesday': schedule.every().wednesday,
    'thursday': schedule.every().thursday,
    'friday': schedule.every().friday,
    'saturday': schedule.every().saturday,
    'sunday': schedule.every().sunday
}

if INVESTMENT_DAY.lower() in schedule_map:
    schedule_map[INVESTMENT_DAY.lower()].do(execute_investment)
    logger.info(f"Investment scheduled on {INVESTMENT_DAY}.")
else:
    logger.error("Invalid INVESTMENT_DAY. Please choose a day from 'Monday' to 'Sunday'.")

logger.info("Starting main application.")
while True:
    schedule.run_pending()
    time.sleep(1)

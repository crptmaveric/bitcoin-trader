import time
import uuid
from datetime import datetime

from config.config import API_KEY, MONTHLY_LIMIT, FREQUENCY, TRADING_PAIR, PRIVATE_KEY, API_KEY_V2, \
    API_SECRET_V2, INVESTMENT_STRATEGY
from config.config import DROP_THRESHOLD

from coinbase_api_v2 import get_bitcoin_price, get_previous_day_bitcoin_price
from logger import Logger
from src.coinbase_api import CoinbaseAdvancedAuth, buy_bitcoin, get_order_details, wait_for_order_completion
from src.coinbase_api_v2 import CoinbaseWalletAuth, get_euro_balance, get_bitcoin_price_change_week
from src.database import log_transaction, log_uninvested_balance, get_last_purchase_date, update_last_purchase_date
from src.investment_logic import get_fear_and_greed_index, adaptive_average_cost, \
    adaptive_cost_average_with_market_timing

logger = Logger()


def execute_investment(transaction_type='regular'):
    logger.info("Starting execute_investment function.")

    # Check the last purchase date before executing the investment
    last_purchase_date = get_last_purchase_date()
    today_date = datetime.now().strftime("%Y-%m-%d")

    if last_purchase_date == today_date:
        logger.info("Bitcoin already purchased today. Skipping the purchase.")
        return

    private_key = PRIVATE_KEY
    auth = CoinbaseAdvancedAuth(API_KEY, private_key)
    auth_v2 = CoinbaseWalletAuth(API_KEY_V2, API_SECRET_V2)

    index_value = get_fear_and_greed_index()
    btc_price_change = get_bitcoin_price_change_week()

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
                    purchase_time=order_details['created_time'],
                    transaction_type=transaction_type
                )

                # Update the last purchase date after a successful purchase
                update_last_purchase_date(today_date)

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


def check_price_drop_and_buy():
    """
    Check the percentage drop in Bitcoin price and execute an investment if it exceeds the threshold.

    This function retrieves the current and previous day's Bitcoin price, calculates the percentage drop,
    and if the drop is greater than or equal to DROP_THRESHOLD, it executes an investment based on the
    INVESTMENT_STRATEGY.
    """
    try:
        # Retrieve the current Bitcoin price
        current_price = get_bitcoin_price()
        if current_price is None:
            logger.error("Failed to retrieve the current Bitcoin price.")
            return

        # Retrieve the previous day's Bitcoin price
        previous_price = get_previous_day_bitcoin_price()
        if previous_price is None:
            logger.error("Failed to retrieve the previous day's Bitcoin price.")
            return

        # Calculate the percentage price drop
        price_drop = ((previous_price - current_price) / previous_price) * 100

        # Log the price drop
        logger.info(f"Bitcoin price drop: {price_drop}%")

        # Check if the drop exceeds the threshold and execute an investment
        if price_drop >= DROP_THRESHOLD:
            logger.info("Price drop exceeds the threshold. Executing investment.")
            execute_investment("extraordinary")
        else:
            logger.info("Price drop does not exceed the threshold. No action taken.")
    except Exception as e:
        logger.error(f"Error in check_price_drop_and_buy: {e}")


def schedule_price_drop_investment():
    """
    Schedule the price drop check function.

    This function can be scheduled in main.py to run at regular intervals defined in CHECK_INTERVAL.
    It triggers the check_price_drop_and_buy function.
    """
    try:
        check_price_drop_and_buy()
    except Exception as e:
        logger.error(f"Error in schedule_price_drop_check: {e}")

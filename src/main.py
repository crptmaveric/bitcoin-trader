import schedule
import time
from config.config import INVESTMENT_DAY, CHECK_INTERVAL
from investment import execute_investment, schedule_price_drop_investment, get_fear_and_greed_index
from logger import Logger
from database import create_database, get_last_transaction_date, get_average_buy_price
from coinbase_api_v2 import get_bitcoin_price
from coinbase_api import get_previous_day_bitcoin_price
from display.epaper import EPaperDisplayManager
from config.config import API_KEY, PRIVATE_KEY, TRADING_PAIR

logger = Logger()

# Assuming EPaperDisplayManager is properly imported from epaper.py
epaper_display = EPaperDisplayManager()


def prepare_display_data():
    """
    Fetches and prepares data for display on the e-paper screen.
    Returns a dictionary with the data for each quadrant.
    """
    fear_greed_index = get_fear_and_greed_index()
    bitcoin_price = get_bitcoin_price()
    average_buy_price = get_average_buy_price()
    last_transaction = get_last_transaction_date()

    # Retrieve the previous day's Bitcoin price
    previous_price = get_previous_day_bitcoin_price(API_KEY, PRIVATE_KEY, TRADING_PAIR)
    if previous_price is None:
        logger.error("Failed to retrieve the previous day's Bitcoin price.")
        return

    # Calculate the percentage price drop
    bitcoin_change = ((bitcoin_price - previous_price) / previous_price) * 100

    change_color = "red" if bitcoin_change < 0 else "black"
    bitcoin_change = "{:.2f}".format(bitcoin_change)
    bitcoin_price_format = "{:.2f}".format(bitcoin_price)

    return {
        "Fear & Greed Index": fear_greed_index,
        "Bitcoin Price (€)": [(f"{bitcoin_price_format}", "s", "black", "normal"), (f"{bitcoin_change}%", "s", change_color, "small")],
        "Avg Buy Price (€)": average_buy_price,
        "Last Transaction": last_transaction
    }


def update_epaper_display():
    logger.info("Updating display.")
    display_data = prepare_display_data()
    epaper_display.update_display(display_data)


create_database()
logger.info("Database created.")

# Check drop and update display
schedule_price_drop_investment()
update_epaper_display()

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
    schedule_map[INVESTMENT_DAY.lower()].at("01:11").do(execute_investment)
    logger.info(f"Investment scheduled on {INVESTMENT_DAY}.")
else:
    logger.error("Invalid INVESTMENT_DAY. Please choose a day from 'Monday' to 'Sunday'.")

# Schedule the price drop check function
schedule.every(CHECK_INTERVAL).hours.do(schedule_price_drop_investment)

# Schedule the e-paper display update function
schedule.every(CHECK_INTERVAL).hours.do(update_epaper_display)

logger.info(f"Price drop investment check scheduled every {CHECK_INTERVAL} hour(s).")
logger.info("E-paper display update scheduled every 2 hours.")

logger.info("Starting main application.")
while True:
    schedule.run_pending()
    time.sleep(1)

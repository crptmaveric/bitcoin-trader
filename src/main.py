import schedule
import time

import schedule
from config.config import INVESTMENT_DAY, CHECK_INTERVAL

from investment import execute_investment, schedule_price_drop_investment, check_price_drop_and_buy
from logger import Logger
from database import create_database

logger = Logger()

create_database()
logger.info("Database created.")

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

# Schedule the price drop check function
# schedule.every(CHECK_INTERVAL).hours.do(schedule_price_drop_investment)
# logger.info(f"Price drop investment check scheduled every {CHECK_INTERVAL} hour(s).")

logger.info("Starting main application.")
while True:
    schedule.run_pending()
    time.sleep(1)

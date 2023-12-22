# Import necessary modules
import datetime

from coinbase_api import CoinbaseAdvancedAuth, buy_bitcoin, sell_bitcoin, create_stop_order
from coinbase_api_v2 import CoinbaseWalletAuth, CoinbaseMarketData, get_bitcoin_balance
from logger import Logger
from risk_management import RiskManagement
from trader.trend_signals import generate_signals
from config.config import API_KEY_V2, API_SECRET_V2, PRIVATE_KEY, API_KEY, TRADING_PAIR

# Constants and Configuration
RISK_MANAGEMENT_SETTINGS = {
    'stop_loss_percentage': 10,  # 10%
    'take_profit_percentage': 15  # 15%
}
TREND_SIGNAL_SETTINGS = {
    'short_term_window': 14,
    'long_term_window': 50,
    'rsi_threshold': 70,
    'macd_threshold': 0
}

logger = Logger()


# TradingBot Class
class TradingBot:
    def __init__(self):
        self.auth_v2 = CoinbaseWalletAuth(API_KEY_V2, API_SECRET_V2)
        self.auth = CoinbaseAdvancedAuth(API_KEY, PRIVATE_KEY)
        self.market_data = CoinbaseMarketData(self.auth_v2)
        self.risk_management = RiskManagement(RISK_MANAGEMENT_SETTINGS['stop_loss_percentage'],
                                              RISK_MANAGEMENT_SETTINGS['take_profit_percentage'])
        self.balance = 0
        self.last_purchase_price = None
        self.is_trading = False

    def start_trading(self):
        self.is_trading = True
        while self.is_trading:
            self.execute_trades()

    def execute_trades(self):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=TREND_SIGNAL_SETTINGS['long_term_window'])
        historical_data = self.market_data.get_historical_data(TRADING_PAIR, start_date, end_date)

        signals = generate_signals(historical_data, **TREND_SIGNAL_SETTINGS)

        for signal in signals:
            if signal == 'buy':
                self.place_buy_order()
            elif signal == 'sell' and self.last_purchase_price is not None:
                self.place_sell_order()

                # Manage risks for open positions
                # self.manage_risk_on_open_positions()

    # def manage_risk_on_open_positions(self):
    #     real_time_data = self.market_data.get_real_time_data(TRADING_PAIR)
    #     current_price = float(real_time_data['price'].iloc[0]) if not real_time_data.empty else None
    #
    #     if current_price and self.last_purchase_price:
    #         self.update_balance()
    #         stop_loss_price = self.risk_management.calculate_stop_loss(self.last_purchase_price)
    #         take_profit_price = self.risk_management.calculate_take_profit(self.last_purchase_price)
    #
    #         if current_price <= stop_loss_price or current_price >= take_profit_price:
    #             self.sell_all()
    #             logger.info("Risk management conditions met, selling all holdings.")

    def update_balance(self):
        self.balance = get_bitcoin_balance(self.auth_v2)

    def place_buy_order(self):
        try:
            order_id = 'unique_order_id'
            amount = self.calculate_order_amount('buy')
            response = buy_bitcoin(API_KEY, PRIVATE_KEY, order_id, TRADING_PAIR, amount)
            if response['status'] == 'success':
                self.last_purchase_price = float(response['price'])
                # Create stop-loss and take-profit orders
                stop_loss_price = self.risk_management.calculate_stop_loss(self.last_purchase_price)
                take_profit_price = self.risk_management.calculate_take_profit(self.last_purchase_price)
                create_stop_order(API_KEY, PRIVATE_KEY, order_id + "_sl", TRADING_PAIR, amount, stop_loss_price,
                                  stop_loss_price, "STOP_DIRECTION_STOP_DOWN")
                # create_stop_order(API_KEY, PRIVATE_KEY, order_id + "_tp", TRADING_PAIR, amount, take_profit_price,
                #                   take_profit_price, "STOP_DIRECTION_STOP_UP")
            logger.info(f'Buy order placed: {response}')
        except Exception as e:
            logger.error(f'Error placing buy order: {e}')



    def calculate_order_amount(self, order_type):
        if order_type == 'buy':
            return '0.01'  # Example fixed amount for the order
        elif order_type == 'sell':
            return '0.01'  # Example fixed amount for the order

    def sell_all(self):
        try:
            btc_balance = get_bitcoin_balance(self.auth_v2)
            if btc_balance > 0:
                response = sell_bitcoin(API_KEY, PRIVATE_KEY, 'sell_all_order', TRADING_PAIR, btc_balance)
                logger.info(f'Sold all holdings: {response}')
            else:
                logger.info('No holdings to sell.')
        except Exception as e:
            logger.error(f'Error selling all holdings: {e}')

# Main Execution
# if __name__ == "__main__":
#     bot = TradingBot()
#     bot.start_trading()

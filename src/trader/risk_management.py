from logger import Logger

logger = Logger()


class RiskManagement:
    def __init__(self, stop_loss_percentage, take_profit_percentage):
        """
        Initialize the RiskManagement class with specified percentage thresholds for stop-loss and take-profit.
        """
        self.stop_loss_percentage = stop_loss_percentage
        self.take_profit_percentage = take_profit_percentage

        logger.info(f'Stop loss percentage: {stop_loss_percentage}')
        logger.info(f'Take profit percentage: {take_profit_percentage}')

    def calculate_stop_loss(self, purchase_price):
        """
        Calculate the stop loss level based on the purchase price and stop loss percentage.
        """
        return purchase_price * (1 - self.stop_loss_percentage / 100)

    def calculate_take_profit(self, purchase_price):
        """
        Calculate the take profit level based on the purchase price and take profit percentage.
        """
        return purchase_price * (1 + self.take_profit_percentage / 100)

    # The following methods are no longer needed and can be removed:
    # - should_stop_loss
    # - should_take_profit
    # - set_initial_balance
    # - update_balance
    # - check_drawdown

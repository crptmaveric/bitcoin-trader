class RiskManagement:
    def __init__(self, stop_loss_threshold, take_profit_threshold, max_drawdown):
        """
        Initialize the RiskManagement class with specified thresholds.

        Parameters:
        stop_loss_threshold (float): The stop-loss threshold as a percentage.
        take_profit_threshold (float): The take-profit threshold as a percentage.
        max_drawdown (float): The maximum drawdown as a percentage.
        """
        self.stop_loss_threshold = stop_loss_threshold
        self.take_profit_threshold = take_profit_threshold
        self.max_drawdown = max_drawdown
        self.initial_balance = None
        self.current_balance = None

    def set_initial_balance(self, balance):
        """
        Set the initial balance for risk calculations.

        Parameters:
        balance (float): The initial balance value.
        """
        self.initial_balance = balance
        self.current_balance = balance

    def update_balance(self, balance):
        """
        Update the current balance and check for drawdown.

        Parameters:
        balance (float): The updated balance value.
        """
        self.current_balance = balance
        self.check_drawdown()

    def check_drawdown(self):
        """
        Check if the current drawdown exceeds the maximum allowed drawdown.
        """
        if self.initial_balance:
            drawdown = (self.initial_balance - self.current_balance) / self.initial_balance
            if drawdown > self.max_drawdown:
                print('Maximum drawdown limit reached. Consider stopping trades.')
                # Implement trade stopping mechanism

    def should_stop_loss(self, current_price, purchase_price):
        """
        Determine if the stop loss condition is met.

        Parameters:
        current_price (float): The current price of the asset.
        purchase_price (float): The purchase price of the asset.

        Returns:
        bool: True if stop loss condition is met, False otherwise.
        """
        loss = (purchase_price - current_price) / purchase_price
        return loss > self.stop_loss_threshold

    def should_take_profit(self, current_price, purchase_price):
        """
        Determine if the take profit condition is met.

        Parameters:
        current_price (float): The current price of the asset.
        purchase_price (float): The purchase price of the asset.

        Returns:
        bool: True if take profit condition is met, False otherwise.
        """
        profit = (current_price - purchase_price) / purchase_price
        return profit > self.take_profit_threshold


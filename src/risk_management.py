class RiskManagement:
    def __init__(self, stop_loss_threshold, take_profit_threshold, max_drawdown):
        self.stop_loss_threshold = stop_loss_threshold
        self.take_profit_threshold = take_profit_threshold
        self.max_drawdown = max_drawdown
        self.initial_balance = None
        self.current_balance = None

    def set_initial_balance(self, balance):
        self.initial_balance = balance
        self.current_balance = balance

    def update_balance(self, balance):
        self.current_balance = balance
        self.check_drawdown()

    def check_drawdown(self):
        if self.initial_balance:
            drawdown = (self.initial_balance - self.current_balance) / self.initial_balance
            if drawdown > self.max_drawdown:
                print('Maximum drawdown limit reached. Consider stopping trades.')
                # Implement trade stopping mechanism

    def should_stop_loss(self, current_price, purchase_price):
        loss = (purchase_price - current_price) / purchase_price
        return loss > self.stop_loss_threshold

    def should_take_profit(self, current_price, purchase_price):
        profit = (current_price - purchase_price) / purchase_price
        return profit > self.take_profit_threshold

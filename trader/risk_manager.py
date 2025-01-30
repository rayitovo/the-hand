# trader/risk_manager.py
from utils.logger import logger

class RiskManager:
    def __init__(self, max_drawdown=0.1, max_position_size=0.5, risk_per_trade=0.02):
        self.max_drawdown = max_drawdown  # Maximum allowed drawdown (e.g., 0.1 means 10% drawdown)
        self.max_position_size = max_position_size  # Maximum allowed position size as a fraction of portfolio value
        self.risk_per_trade = risk_per_trade # Maximum risk per trade
        self.current_drawdown = 0  # Track current drawdown from peak equity
        self.peak_equity = 0 # Track the highest portfolio value seen.
        logger.info(f"RiskManager initialized with max_drawdown: {self.max_drawdown}, max_position_size: {self.max_position_size}, risk_per_trade:{self.risk_per_trade}")

    def check_max_drawdown(self, portfolio_value):
        """
        Checks if the maximum drawdown threshold is exceeded.
        Args:
            portfolio_value (float): Current portfolio value.
        Returns:
            bool: True if max drawdown is exceeded, False otherwise.
        """
        if portfolio_value > self.peak_equity:
             self.peak_equity = portfolio_value # Update peak
        self.current_drawdown = (self.peak_equity - portfolio_value) / self.peak_equity if self.peak_equity else 0

        if self.current_drawdown > self.max_drawdown:
            logger.warning(f"Max drawdown exceeded: {self.current_drawdown:.4f} > {self.max_drawdown}. Trading should stop.")
            return True
        return False

    def check_max_position_size(self, amount_usd, portfolio_value):
        """
        Checks if the position size is within the maximum limit.
        Args:
            amount_usd (float): USD value of the trade/position.
            portfolio_value (float): Current portfolio value.
        Returns:
            bool: True if position size is within the limit, False otherwise.
        """
        if portfolio_value == 0:
             logger.warning(f"Portfolio value is 0. Max position size check is not valid")
             return False # Avoid division by zero
        position_size = amount_usd / portfolio_value
        if position_size > self.max_position_size:
            logger.warning(f"Max position size exceeded: {position_size:.4f} > {self.max_position_size}. Trade size is too big.")
            return False
        return True

    def check_risk_per_trade(self, usd_risk, portfolio_value):
        """
        Checks if the risk of the current trade is within the limit
        Args:
            usd_risk (float): USD value of the risk of the trade (e.g, stop loss - purchase price)
            portfolio_value (float): Current portfolio value
        Returns:
            bool: True if the risk is acceptable; False if not.
        """
        if portfolio_value == 0:
             logger.warning(f"Portfolio value is 0. Risk per trade check is not valid")
             return False # Avoid division by zero
        risk_percentage = usd_risk / portfolio_value
        if risk_percentage > self.risk_per_trade:
            logger.warning(f"Risk per trade exceeded {risk_percentage:.4f} > {self.risk_per_trade}. Trade is too risky.")
            return False
        return True


    def check_trade_limits(self, order_params, portfolio_value):
          """
          Checks all trade-related limits (max drawdown, max position size, risk per trade)
          Args:
             order_params (dict): Dictionary containing order details {'order_type': 'buy'/'sell', 'symbol': 'BTC', 'amount': float, 'price': float}
             portfolio_value (float): Current portfolio value.
          Returns:
             bool: True if all checks pass. False otherwise
          """
          order_type = order_params.get('order_type')
          symbol = order_params.get('symbol')
          amount = order_params.get('amount')
          price = order_params.get('price')

          if not all([order_type, symbol, amount, price]):
               logger.error(f"Invalid order parameters. Missing order_type, symbol, amount, or price")
               return False

          usd_value = amount * price
          if not self.check_max_position_size(usd_value, portfolio_value):
               return False

          if order_type == 'buy':
              # Assuming you calculate a stop loss somewhere, and pass the usd_risk
               # For a "sell" order this might be a "take profit" value, but can also be risk
               pass # placeholder
          elif order_type == 'sell':
               pass # placeholder
          return not self.check_max_drawdown(portfolio_value)


if __name__ == '__main__':
    risk_manager = RiskManager(max_drawdown=0.2, max_position_size=0.6, risk_per_trade=0.03)

    portfolio_value_1 = 10000
    portfolio_value_2 = 8000
    portfolio_value_3 = 12000
    trade_amount_1 = 5000 # Example USD trade amount
    trade_amount_2 = 7000
    usd_risk_1 = 500 # Example usd risk
    usd_risk_2 = 100

    print(f"Is Max Drawdown Exceeded for portfolio of ${portfolio_value_1}?: {risk_manager.check_max_drawdown(portfolio_value_1)}") # Should return False
    print(f"Is Max Drawdown Exceeded for portfolio of ${portfolio_value_2}?: {risk_manager.check_max_drawdown(portfolio_value_2)}")  #Should return False
    print(f"Is Max Drawdown Exceeded for portfolio of ${portfolio_value_3}?: {risk_manager.check_max_drawdown(portfolio_value_3)}") #Should return False
    print(f"Is Max Position Size OK for trade ${trade_amount_1} in portfolio of ${portfolio_value_1}?: {risk_manager.check_max_position_size(trade_amount_1, portfolio_value_1)}") # Should return True
    print(f"Is Max Position Size OK for trade ${trade_amount_2} in portfolio of ${portfolio_value_1}?: {risk_manager.check_max_position_size(trade_amount_2, portfolio_value_1)}") # Should return False
    print(f"Is Risk Per Trade OK for trade of risk ${usd_risk_1} in portfolio of ${portfolio_value_1}?: {risk_manager.check_risk_per_trade(usd_risk_1, portfolio_value_1)}")  # Should return True
    print(f"Is Risk Per Trade OK for trade of risk ${usd_risk_2} in portfolio of ${portfolio_value_1}?: {risk_manager.check_risk_per_trade(usd_risk_2, portfolio_value_1)}")  # Should return True

    order_params_1 = {
        'order_type': 'buy',
        'symbol': 'BTC',
        'amount': 0.01,
        'price': 30000
    }

    order_params_2 = {
        'order_type': 'buy',
        'symbol': 'BTC',
        'amount': 0.02,
        'price': 30000
    }
    print(f"Are the trade limits OK for order 1 and a portfolio of ${portfolio_value_1}?: {risk_manager.check_trade_limits(order_params_1, portfolio_value_1)}") # Should return True
    print(f"Are the trade limits OK for order 2 and a portfolio of ${portfolio_value_1}?: {risk_manager.check_trade_limits(order_params_2, portfolio_value_1)}") # Should return False
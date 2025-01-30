# trading_core/portfolio_manager.py
from utils.logger import logger
import pandas as pd

class PortfolioManager:
    def __init__(self, initial_balance_usd=10000):
        self.balance_usd = initial_balance_usd
        self.positions = {}  # Dictionary to store crypto positions, e.g., {'BTC': {'amount': 1.5, 'avg_price': 30000}}
        self.trade_history = [] # List to store trade history as dictionaries
        logger.info(f"PortfolioManager initialized with ${initial_balance_usd:.2f} initial balance.")

    def get_balance_usd(self):
        return self.balance_usd

    def get_positions(self):
        return self.positions

    def update_balance(self, amount_usd):
        """Updates the USD balance."""
        self.balance_usd += amount_usd
        logger.debug(f"Balance updated by ${amount_usd:.2f}. Current balance: ${self.balance_usd:.2f}")

    def update_position(self, symbol, amount_change, price):
        """
        Updates the position for a given crypto symbol.
        Args:
            symbol (str): Crypto symbol (e.g., 'BTC').
            amount_change (float): Change in the amount of crypto (positive for buy, negative for sell).
            price (float): Price at which the transaction occurred.
        """
        if symbol not in self.positions:
            self.positions[symbol] = {'amount': 0, 'avg_price': 0}

        current_position = self.positions[symbol]
        previous_amount = current_position['amount']
        current_amount = previous_amount + amount_change

        if current_amount == 0:
            # Position closed, reset avg_price
            current_position['avg_price'] = 0
        elif previous_amount == 0:
            # First position, set avg_price
            current_position['avg_price'] = price
        else:
            # Update average price (simplified average cost basis)
            total_value_before = previous_amount * current_position['avg_price']
            total_value_added = amount_change * price
            current_position['avg_price'] = (total_value_before + total_value_added) / current_amount

        current_position['amount'] = current_amount
        self.positions[symbol] = current_position # Update the position in the dict
        logger.debug(f"Position for {symbol} updated. Amount: {current_amount:.4f}, Avg Price: ${current_position['avg_price']:.2f}")

    def execute_trade(self, order_type, symbol, amount, price, timestamp=None):
        """
        Executes a trade (buy or sell) and updates portfolio and trade history.
        Args:
            order_type (str): 'buy' or 'sell'.
            symbol (str): Crypto symbol (e.g., 'BTC').
            amount (float): Amount of crypto to trade.
            price (float): Execution price.
            timestamp (pd.Timestamp, optional): Timestamp of the trade. Defaults to None.
        Returns:
            bool: True if trade executed successfully, False otherwise (e.g., insufficient balance).
        """
        usd_value = amount * price

        if order_type == 'buy':
            if self.balance_usd >= usd_value:
                self.update_balance(-usd_value)  # Decrease USD balance
                self.update_position(symbol, amount, price)  # Increase crypto position
                trade_record = {'type': 'buy', 'symbol': symbol, 'amount': amount, 'price': price, 'usd_value': usd_value,
                                'timestamp': timestamp if timestamp else pd.Timestamp.now()}  # Use provided timestamp or default to now()
                self.trade_history.append(trade_record)
                logger.info(
                    f"BUY {amount:.4f} {symbol} at ${price:.2f}, Value: ${usd_value:.2f}. New balance: ${self.balance_usd:.2f}, Position: {self.positions[symbol]['amount']:.4f} {symbol}")
                return True
            else:
                logger.warning(
                    f"Insufficient USD balance to BUY {amount:.4f} {symbol} at ${price:.2f}. Available balance: ${self.balance_usd:.2f}, Required: ${usd_value:.2f}")
                return False
        elif order_type == 'sell':
            if symbol in self.positions and self.positions[symbol]['amount'] >= amount:
                self.update_balance(usd_value)  # Increase USD balance
                self.update_position(symbol, -amount, price)  # Decrease crypto position
                trade_record = {'type': 'sell', 'symbol': symbol, 'amount': amount, 'price': price, 'usd_value': usd_value,
                                'timestamp': timestamp if timestamp else pd.Timestamp.now()}  # Use provided timestamp or default to now()
                self.trade_history.append(trade_record)
                logger.info(
                    f"SELL {amount:.4f} {symbol} at ${price:.2f}, Value: ${usd_value:.2f}. New balance: ${self.balance_usd:.2f}, Position: {self.positions[symbol]['amount']:.4f} {symbol}")
                return True
            else:
                available_amount = self.positions[symbol]['amount'] if symbol in self.positions else 0
                logger.warning(
                    f"Insufficient {symbol} balance to SELL {amount:.4f} {symbol}. Available: {available_amount:.4f}, Requested: {amount:.4f}")
                return False
        else:
            logger.error(f"Invalid order type: {order_type}. Must be 'buy' or 'sell'.")
            return False

    def get_portfolio_value(self, current_prices_usd):
        """
        Calculates the total portfolio value in USD, including USD balance and crypto positions.
        Args:
            current_prices_usd (dict): Dictionary of current prices for each crypto symbol, e.g., {'BTC': 35000, 'ETH': 1900}.
        Returns:
            float: Total portfolio value in USD.
        """
        total_value = self.balance_usd
        for symbol, position in self.positions.items():
            if symbol in current_prices_usd:
                total_value += position['amount'] * current_prices_usd[symbol]
            else:
                logger.warning(f"Current price for {symbol} not provided, position value not included in total portfolio value.")
        return total_value

    def calculate_pnl(self, current_prices_usd):
        """
        Calculates Profit and Loss (PnL) for each position and total portfolio PnL.
        Args:
            current_prices_usd (dict): Dictionary of current prices for each crypto symbol.
        Returns:
            dict: Dictionary containing PnL information.
                  {'position_pnl': {'BTC': pnl_value, ...}, 'total_pnl': total_pnl_value}
        """
        position_pnl = {}
        total_pnl = 0
        for symbol, position in self.positions.items():
            if symbol in current_prices_usd and position['amount'] != 0:
                current_value = position['amount'] * current_prices_usd[symbol]
                cost_basis = position['amount'] * position['avg_price']
                pnl = current_value - cost_basis
                position_pnl[symbol] = pnl
                total_pnl += pnl
            else:
                position_pnl[symbol] = 0 # Or None, if you want to indicate no PnL calculated
        return {'position_pnl': position_pnl, 'total_pnl': total_pnl}

if __name__ == '__main__':
    portfolio = PortfolioManager(initial_balance_usd=10000)

    # Example trades
    btc_price = 30000
    eth_price = 1800

    portfolio.execute_trade('buy', 'BTC', 0.1, btc_price) # Buy 0.1 BTC
    portfolio.execute_trade('buy', 'ETH', 1, eth_price)   # Buy 1 ETH
    portfolio.execute_trade('sell', 'BTC', 0.05, btc_price + 100) # Sell 0.05 BTC at slightly higher price

    print(f"Current USD Balance: ${portfolio.get_balance_usd():.2f}")
    print("Current Positions:", portfolio.get_positions())

    current_prices = {'BTC': btc_price + 200, 'ETH': eth_price - 10} # Simulate price changes
    portfolio_value = portfolio.get_portfolio_value(current_prices)
    print(f"Total Portfolio Value (USD): ${portfolio_value:.2f}")

    pnl_data = portfolio.calculate_pnl(current_prices)
    print("Position PnL:", pnl_data['position_pnl'])
    print(f"Total PnL: ${pnl_data['total_pnl']:.2f}")
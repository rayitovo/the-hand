# strategist/execution_coordinator.py
import pandas as pd
from simulation.virtual_exchange import VirtualExchange
from trading_core.portfolio_manager import PortfolioManager
from trading_core.event_logger import EventLogger
from utils.logger import logger

class ExecutionCoordinator:
    def __init__(self, mode="simulation"): # Default to simulation mode
        self.mode = mode
        if self.mode == "simulation":
            self.exchange = VirtualExchange() # Use VirtualExchange for simulation
        elif self.mode == "live":
            from trader.exchange_connector import ExchangeConnector # Import only for live mode
            self.exchange = ExchangeConnector() # Use ExchangeConnector for live trading (stub in Phase 3)
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'simulation' or 'live'.")

        self.portfolio_manager = PortfolioManager() # Initialize portfolio manager
        self.event_logger = EventLogger() # Initialize event logger
        logger.info(f"ExecutionCoordinator initialized in {self.mode} mode.")

    def execute_trade(self, order_params):
        """
        Executes a trade through the appropriate exchange (virtual or real) and updates portfolio.
        Args:
            order_params (dict): Order parameters (same format as VirtualExchange.execute_order).
        Returns:
            dict: Order execution result (from VirtualExchange or ExchangeConnector).
        """
        execution_result = self.exchange.execute_order(order_params) # Execute order on virtual/real exchange

        if execution_result['status'] == 'success':
            executed_price = execution_result['executed_price']
            executed_amount = execution_result['executed_amount']
            symbol = execution_result['symbol']
            order_type = execution_result['order_type']

            # Update portfolio and log trade
            trade_success = self.portfolio_manager.execute_trade(order_type, symbol, executed_amount, executed_price)
            if trade_success:
                trade_record = {
                    'type': order_type,
                    'symbol': symbol,
                    'amount': executed_amount,
                    'price': executed_price,
                    'usd_value': executed_amount * executed_price,
                    'timestamp': pd.Timestamp.now() # Or get timestamp from exchange response if available in real trading
                }
                self.event_logger.log_trade(trade_record)
            else:
                logger.error(f"Portfolio update failed after successful order execution. Order params: {order_params}, Execution result: {execution_result}")
                execution_result['status'] = 'failure' # Mark overall execution as failure if portfolio update fails
        else:
            logger.warning(f"Order execution failed. Order params: {order_params}, Execution result: {execution_result}")

        return execution_result

    def get_portfolio_status(self, current_prices_usd=None):
        """
        Returns the current portfolio status (balance, positions, PnL).
        Args:
            current_prices_usd (dict, optional): Current prices for PnL calculation.
                                                  If None, PnL will not be calculated.
        Returns:
            dict: Portfolio status dictionary.
        """
        portfolio_status = {
            'usd_balance': self.portfolio_manager.get_balance_usd(),
            'positions': self.portfolio_manager.get_positions()
        }
        if current_prices_usd:
            pnl_data = self.portfolio_manager.calculate_pnl(current_prices_usd)
            portfolio_status['position_pnl'] = pnl_data['position_pnl']
            portfolio_status['total_pnl'] = pnl_data['total_pnl']
            portfolio_status['portfolio_value_usd'] = self.portfolio_manager.get_portfolio_value(current_prices_usd)
        return portfolio_status


if __name__ == '__main__':
    execution_coordinator = ExecutionCoordinator(mode="simulation") # Initialize in simulation mode

    # Example buy order
    buy_order_params = {
        'order_type': 'buy',
        'symbol': 'BTC',
        'amount': 0.01,
        'price': 30400.00
    }
    buy_execution_result = execution_coordinator.execute_trade(buy_order_params)
    print("Buy order execution result:", buy_execution_result)

    # Example sell order
    sell_order_params = {
        'order_type': 'sell',
        'symbol': 'BTC',
        'amount': 0.005,
        'price': 30600.00
    }
    sell_execution_result = execution_coordinator.execute_trade(sell_order_params)
    print("Sell order execution result:", sell_execution_result)

    # Get portfolio status
    current_prices = {'BTC': 30700, 'ETH': 1850} # Example current prices
    portfolio_status = execution_coordinator.get_portfolio_status(current_prices_usd=current_prices)
    print("\nPortfolio Status:")
    print(portfolio_status)
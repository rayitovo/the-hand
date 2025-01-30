# backtester/backtest_engine.py
import pandas as pd
from trading_core.portfolio_manager import PortfolioManager
from trading_core.event_logger import EventLogger
from utils.logger import logger
import time  # For simulating backtest speed

class BacktestEngine:
    def __init__(self):
        self.portfolio_manager = PortfolioManager() # Each backtest starts with a fresh portfolio
        self.event_logger = EventLogger(filename='backtest_transactions.csv') # Separate log file for backtests
        logger.info("BacktestEngine initialized.")

    def run_backtest(self, strategy, historical_data: pd.DataFrame, initial_balance_usd=10000):
        """
        Runs a backtest for a given strategy on historical data.
        Args:
            strategy (BaseStrategy): Strategy object to backtest.
            historical_data (pd.DataFrame): DataFrame with historical market data (must include 'close' prices and 'timestamp' index).
            initial_balance_usd (float): Initial portfolio balance for backtesting.
        Returns:
            dict: Backtest results summary (e.g., final balance, PnL, metrics).
        """
        logger.info(f"Starting backtest for strategy: {strategy.get_strategy_name()}, Symbol: {strategy.get_symbol()}")
        start_time = time.time()

        self.portfolio_manager = PortfolioManager(initial_balance_usd=initial_balance_usd) # Reset portfolio for each backtest
        self.event_logger = EventLogger(filename='backtest_transactions.csv') # New event logger instance or reset header?

        if historical_data.empty:
            logger.warning("Historical data is empty. Backtest cannot be run.")
            return {'status': 'error', 'message': 'No historical data provided'}

        # Ensure historical_data is sorted by timestamp (important for sequential backtesting)
        historical_data = historical_data.sort_index()

        # Backtesting loop (iterate through historical data points)
        for index, row in historical_data.iterrows(): # Iterate through each row (timestamp) of historical data
            current_timestamp = index # Timestamp of the current data point
            current_price = row['close'] # Use 'close' price for signal generation and order execution simulation

            # Generate trading signal from the strategy
            signal = strategy.generate_signal(historical_data.loc[:current_timestamp]) # Pass data up to current timestamp
            symbol = strategy.get_symbol()

            # Execute trades based on signal (in simulation)
            if signal == 'buy':
                order_params = {'order_type': 'buy', 'symbol': symbol, 'amount': 0.01, 'price': current_price} # Example fixed amount
                trade_result = self.execute_trade(order_params, current_timestamp)
            elif signal == 'sell':
                positions = self.portfolio_manager.get_positions()
                amount_to_sell = positions.get(symbol, {}).get('amount', 0) # Sell entire current position
                if amount_to_sell > 0:
                    order_params = {'order_type': 'sell', 'symbol': symbol, 'amount': amount_to_sell, 'price': current_price}
                    trade_result = self.execute_trade(order_params, current_timestamp)
                else:
                    trade_result = {'status': 'no_position_to_sell', 'message': 'No position to sell', 'timestamp': current_timestamp}
                    logger.info(f"Backtest: {current_timestamp} - No {symbol} position to sell, signal: {signal}")
            elif signal == 'hold':
                trade_result = {'status': 'hold_signal', 'message': 'Hold signal', 'timestamp': current_timestamp}
                logger.info(f"Backtest: {current_timestamp} - Hold signal from strategy.")
            else:
                trade_result = {'status': 'invalid_signal', 'message': 'Invalid signal', 'timestamp': current_timestamp, 'signal': signal}
                logger.warning(f"Backtest: {current_timestamp} - Invalid signal received from strategy: {signal}")

            # Optionally simulate backtesting speed (slow down for visual inspection or debugging)
            # time.sleep(0.01) # Slow down backtest

        end_time = time.time()
        backtest_duration_seconds = end_time - start_time
        logger.info(f"Backtest for strategy: {strategy.get_strategy_name()} completed in {backtest_duration_seconds:.2f} seconds.")

        # Calculate backtest summary metrics (for now, just final balance and PnL)
        initial_portfolio_value = initial_balance_usd # Initially, portfolio value is just the USD balance
        final_portfolio_value = self.portfolio_manager.get_portfolio_value({strategy.get_symbol(): current_price}) # Use last price for portfolio valuation
        total_pnl = final_portfolio_value - initial_portfolio_value

        backtest_summary = {
            'status': 'completed',
            'strategy_name': strategy.get_strategy_name(),
            'symbol': strategy.get_symbol(),
            'initial_balance_usd': initial_balance_usd,
            'final_balance_usd': self.portfolio_manager.get_balance_usd(),
            'final_portfolio_value_usd': final_portfolio_value,
            'total_pnl_usd': total_pnl,
            'backtest_duration_seconds': backtest_duration_seconds,
            'trade_history_file': self.event_logger.filepath # Path to transaction log
            # Add more metrics later (Sharpe ratio, max drawdown, etc.) in report_generator.py
        }
        logger.info(f"Backtest Summary: {backtest_summary}")
        return backtest_summary


    def execute_trade(self, order_params, timestamp):
        """
        Simulates trade execution during backtesting and updates portfolio.
        Uses PortfolioManager to handle trade logic and updates.
        Args:
            order_params (dict): Order parameters (order_type, symbol, amount, price).
            timestamp (Timestamp): Timestamp of the trade execution.
        Returns:
            dict: Trade execution result (status, message, etc.).
        """
        order_type = order_params['order_type']
        symbol = order_params['symbol']
        amount = order_params['amount']
        price = order_params['price']

        trade_successful = self.portfolio_manager.execute_trade(order_type, symbol, amount, price) # Use PortfolioManager to execute trade

        if trade_successful:
            trade_record = {
                'timestamp': timestamp, # Use backtest timestamp
                'type': order_type,
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'usd_value': amount * price,
            }
            self.event_logger.log_trade(trade_record) # Log trade event to backtest log
            return {'status': 'success', 'message': f'Backtest: {order_type} order executed', 'timestamp': timestamp, 'price': price, 'amount': amount}
        else:
            return {'status': 'failure', 'message': f'Backtest: {order_type} order failed (insufficient balance/position)', 'timestamp': timestamp, 'price': price, 'amount': amount}


if __name__ == '__main__':
    # Example backtest run:
    from strategy.approved.bull.ema_crossover import EmaCrossoverStrategy
    import data_module.data_fetcher
    import data_module.data_cleaner

    # 1. Fetch historical data (replace with your data source and pair/interval)
    fetcher = data_module.data_fetcher.DataFetcher()
    cleaner = data_module.data_cleaner.DataCleaner()
    pair = "BTC/USDT"
    interval = "1d"
    raw_historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=500) # Get enough data for backtest
    if raw_historical_data:
        cleaned_data = cleaner.clean_historical_data(raw_historical_data)
        historical_df = pd.DataFrame(cleaned_data).set_index('close_timestamp') # Use close_timestamp as index, assuming cleaned data has it

        # 2. Initialize strategy
        ema_strategy = EmaCrossoverStrategy(symbol=pair.replace("/", "")) # Initialize strategy with symbol

        # 3. Initialize backtest engine
        backtest_engine = BacktestEngine()

        # 4. Run backtest
        backtest_results = backtest_engine.run_backtest(ema_strategy, historical_df, initial_balance_usd=10000)

        # 5. Print backtest summary
        print("\n--- Backtest Results Summary ---")
        for key, value in backtest_results.items():
            print(f"{key}: {value}")

        print(f"\nTrade history logged to: {backtest_results['trade_history_file']}")

    else:
        print("Failed to fetch historical data for backtesting example.")
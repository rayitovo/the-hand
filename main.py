# main.py
import config
from utils.logger import logger
from data_module.data_fetcher import DataFetcher
from data_module.data_cleaner import DataCleaner
from regime_info.technical_analyzer import TechnicalAnalyzer
from regime_info.regime_classifier import RegimeClassifier
from regime_info.macro_analyzer import MacroAnalyzer
from strategist.execution_coordinator import ExecutionCoordinator
from backtester.backtest_engine import BacktestEngine
from backtester.report_generator import ReportGenerator
from trader.risk_manager import RiskManager
import pandas as pd
import importlib
import re

class Strategist:
    def __init__(self, mode, asset_pairs, risk_tolerance, data_fetcher, data_cleaner, technical_analyzer, regime_classifier, execution_coordinator, risk_manager):
        self.mode = mode
        self.asset_pairs = asset_pairs
        self.risk_tolerance = risk_tolerance
        self.data_fetcher = data_fetcher
        self.data_cleaner = data_cleaner
        self.technical_analyzer = technical_analyzer
        self.regime_classifier = regime_classifier
        self.execution_coordinator = execution_coordinator
        self.risk_manager = risk_manager
        self.current_prices = {}  # Initialize dictionary to store current prices
        logger.info(f"Strategist initialized in {self.mode} mode for pairs: {self.asset_pairs} with risk tolerance: {self.risk_tolerance}")

    def run(self):
        logger.info("Strategist running...")
        for pair in self.asset_pairs:
            raw_historical_data = self.data_fetcher.fetch_historical_data(pair, interval="1d", limit=300)
            if raw_historical_data:
                cleaned_data = self.data_cleaner.clean_historical_data(raw_historical_data)
                if cleaned_data:
                    df = pd.DataFrame(cleaned_data)
                    close_prices = df['close']

                    # Example: Classify regime (using ML model now)
                    # This part has been updated, so first prepare the features
                    sma_50 = self.technical_analyzer.calculate_sma(close_prices, window=50)
                    sma_200 = self.technical_analyzer.calculate_sma(close_prices, window=200)
                    # Add CPI data. fetch CPI data for last 30 days.
                    end_date_cpi = pd.Timestamp.today().strftime('%Y-%m-%d')
                    start_date_cpi = pd.Timestamp.today() - pd.Timedelta(days=30)
                    start_date_cpi = start_date_cpi.strftime('%Y-%m-%d')
                    macro_analyzer = MacroAnalyzer()
                    cpi_data = macro_analyzer.fetch_cpi(start_date=start_date_cpi, end_date=end_date_cpi) # The cpi should be time series data. Get latest data.
                    cpi_values = [item['cpi'] for item in cpi_data['data']] if cpi_data and cpi_data['status'] == 'success' else [0]
                    cpi_val = cpi_values[-1] if cpi_values else 0 # Get the latest value.
                    features = pd.DataFrame({'SMA50': [sma_50.iloc[-1]], 'SMA200': [sma_200.iloc[-1]], 'CPI': [cpi_val]})  # Create features DataFrame for model

                    regime = self.regime_classifier.predict(features)[0] if self.regime_classifier.model else self.regime_classifier.classify_regime_sma_crossover(close_prices) # If model is None fallback to SMA crossover

                    logger.info(f"Market regime for {pair}: {regime}")

                    # --- Example Strategy Logic (Simplified for Phase 3) ---
                    # In a bull regime, buy; in sideways, do nothing; in bear, sell (if holding)
                    current_price_data = self.data_fetcher.fetch_realtime_data(pair)
                    if current_price_data['status'] == 'success':
                        current_price = current_price_data['price']
                        symbol = pair.replace("/", "")
                        self.current_prices[symbol] = current_price  # Update current_prices dictionary

                        # --- RISK Management Check ---
                        portfolio_value = self.execution_coordinator.get_portfolio_status(current_prices_usd=self.current_prices)['portfolio_value_usd']
                        order_params = {'order_type': 'buy', 'symbol': symbol, 'amount': 0.01, 'price': current_price} # Example amount
                        if regime == 'bull':
                             if not self.risk_manager.check_trade_limits(order_params, portfolio_value):
                                 logger.warning(f"Trade limits exceeded for {pair}, skipping trading logic.")
                                 continue # Skip this trade if limits are exceeded
                             else:
                                 execution_result = self.execution_coordinator.execute_trade(order_params)
                                 logger.info(f"Buy order placed for {pair} in bull regime. Result: {execution_result}")
                        elif regime == 'bear':
                            positions = self.execution_coordinator.get_portfolio_status()['positions']
                            if symbol in positions and positions[symbol]['amount'] > 0:
                                order_params = {'order_type': 'sell', 'symbol': symbol, 'amount': positions[symbol]['amount'], 'price': current_price}
                                if not self.risk_manager.check_trade_limits(order_params, portfolio_value):
                                    logger.warning(f"Trade limits exceeded for {pair}, skipping trading logic.")
                                    continue # Skip this trade if limits are exceeded
                                else:
                                    execution_result = self.execution_coordinator.execute_trade(order_params)
                                    logger.info(f"Sell order placed for {pair} in bear regime. Result: {execution_result}")
                            else:
                                logger.info(f"Bear regime for {pair}, but no position to sell.")
                        elif regime == 'sideways':
                            logger.info(f"Sideways regime for {pair}, no action taken.")
                        # --- End of Example Strategy Logic ---
                        # Log portfolio status after each pair's processing, including all current prices
                        portfolio_status = self.execution_coordinator.get_portfolio_status(current_prices_usd=self.current_prices)
                        logger.info(f"Portfolio Status after processing {pair}: {portfolio_status}")

                    else:
                        logger.warning(f"Could not fetch realtime price for {pair}, skipping trading logic.")


                else:
                    logger.warning(f"No cleaned data for {pair}, skipping analysis and trading.")
            else:
                logger.error(f"Failed to fetch historical data for {pair}.")
        logger.info("Strategist finished execution.")


def run_backtest(strategy_name, regime, test_mode=False):
    """
    Runs backtest for a given strategy.
    Args:
        strategy_name (str): Name of the strategy file (e.g., 'ema_crossover').
        regime (str): Regime folder where strategy is located (e.g., 'bull').
        test_mode (bool): If True, loads from to_test folder instead of approved.
    """
    logger.info(f"Starting backtest run for strategy: {strategy_name} in regime: {regime}")

    # 1. Load Strategy dynamically
    try:
        folder = 'to_test' if test_mode else 'approved'
        strategy_module = importlib.import_module(f'strategy.{folder}.{regime}.{strategy_name}')
        strategy_class = getattr(strategy_module, "Strategy")
        
        # Validate strategy
        from strategy.strategy_validator import StrategyValidator
        is_valid, msg = StrategyValidator.validate_strategy(strategy_class)
        if not is_valid:
            logger.error(f"Strategy validation failed: {msg}")
            return
            
        strategy = strategy_class(name=strategy_name, symbol="BTCUSDT")
        logger.info(f"Successfully loaded strategy: {strategy_name} from strategy/{folder}/{regime}/{strategy_name}.py")

    except (ImportError, AttributeError) as e:
        logger.error(f"Error loading strategy {strategy_name} from strategy/{folder}/{regime}: {e}")
        return

    # 2. Fetch historical data (for BTCUSDT, adjust as needed)
    fetcher = DataFetcher()
    cleaner = DataCleaner()
    pair = "BTC/USDT"  # Example pair, could be parameterized
    interval = "1d"  # Example interval, could be parameterized
    raw_historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=500)  # Get enough data for backtest
    if not raw_historical_data:
        logger.error(f"Failed to fetch historical data for {pair}. Backtest aborted.")
        return
    cleaned_data = cleaner.clean_historical_data(raw_historical_data)
    historical_df = pd.DataFrame(cleaned_data).set_index('close_timestamp')

    # 3. Initialize Backtest Engine and Report Generator
    backtest_engine = BacktestEngine()
    report_generator = ReportGenerator()

    # 4. Run Backtest
    backtest_results = backtest_engine.run_backtest(strategy, historical_df, initial_balance_usd=10000)

    # 5. Generate and Save Report
    if backtest_results['status'] == 'completed':
        report_text = report_generator.generate_report(backtest_results)
        print(report_text)  # Print to console
        report_filepath = report_generator.save_report_to_file(report_text)
        if report_filepath:
            logger.info(f"Backtest report saved to: {report_filepath}")
        else:
            logger.error("Failed to save backtest report to file.")
    else:
        logger.error("Backtest run failed. No report generated.")
        print("Backtest Failed. Check logs for details.")


if __name__ == "__main__":
    logger.info("Starting the-hand crypto trading platform...")

    if config.RUN_MODE == "strategist":
        logger.info("Running in Strategist mode.")
        data_fetcher = DataFetcher(data_source=config.DATA_SOURCE) # Initialize DataFetcher with config
        data_cleaner = DataCleaner()
        technical_analyzer = TechnicalAnalyzer()
        regime_classifier = RegimeClassifier()
        macro_analyzer = MacroAnalyzer()
        execution_coordinator = ExecutionCoordinator(mode=config.MODE)
        risk_manager = RiskManager()

        strategist = Strategist(
            mode=config.MODE,
            asset_pairs=config.ASSET_PAIRS,
            risk_tolerance=config.RISK_TOLERANCE,
            data_fetcher=data_fetcher,
            data_cleaner=data_cleaner,
            technical_analyzer=technical_analyzer,
            regime_classifier=regime_classifier,
            execution_coordinator=execution_coordinator,
            risk_manager = risk_manager
        )
        strategist.run()

    elif config.RUN_MODE == "backtest":
        logger.info("Running in Backtest mode.")
        strategy_name = config.BACKTEST_STRATEGY
        regime = config.BACKTEST_REGIME
        
        if strategy_name == "all":
            # Test all strategies in to_test folder
            logger.info("Testing all strategies in to_test folder")
            for regime_folder in ["bear", "sideways"]:
                try:
                    # Get list of strategy files
                    import os
                    strategy_dir = f"strategy/to_test/{regime_folder}"
                    strategies = [f[:-3] for f in os.listdir(strategy_dir)
                                if f.endswith('.py') and not f.startswith('_')]
                    
                    for strategy in strategies:
                        logger.info(f"Testing strategy: {strategy} in regime: {regime_folder}")
                        run_backtest(strategy, regime_folder, test_mode=True)
                        
                        # TODO: Add logic to move strategy to approved/ or trash/
                        # based on backtest results
                        
                except Exception as e:
                    logger.error(f"Error testing strategies in {regime_folder}: {e}")
                    
        elif not strategy_name or not regime:
            logger.error("BACKTEST_STRATEGY and BACKTEST_REGIME must be defined in .env for backtest mode.")
            print("Error: BACKTEST_STRATEGY and BACKTEST_REGIME not configured. Check .env file.")
        else:
            run_backtest(strategy_name, regime)  # Run backtest for single strategy

    else:
        logger.error(f"Invalid RUN_MODE in config: {config.RUN_MODE}. Must be 'strategist' or 'backtest'.")
        print(f"Error: Invalid RUN_MODE configured. Check .env file. Must be 'strategist' or 'backtest'.")

    logger.info("the-hand platform execution completed.")
# main.py
import config
from utils.logger import logger
from data_module.data_fetcher import DataFetcher
from data_module.data_cleaner import DataCleaner
from regime_info.technical_analyzer import TechnicalAnalyzer
from regime_info.regime_classifier import RegimeClassifier
from strategist.execution_coordinator import ExecutionCoordinator # Import ExecutionCoordinator
import pandas as pd

class Strategist:
    def __init__(self, mode, asset_pairs, risk_tolerance, data_fetcher, data_cleaner, technical_analyzer, regime_classifier, execution_coordinator): # Add execution_coordinator
        self.mode = mode
        self.asset_pairs = asset_pairs
        self.risk_tolerance = risk_tolerance
        self.data_fetcher = data_fetcher
        self.data_cleaner = data_cleaner
        self.technical_analyzer = technical_analyzer
        self.regime_classifier = regime_classifier
        self.execution_coordinator = execution_coordinator # Initialize ExecutionCoordinator
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

                    # Example: Classify regime
                    regime = self.regime_classifier.classify_regime_sma_crossover(close_prices)
                    logger.info(f"Market regime for {pair}: {regime}")

                    # --- Example Strategy Logic (Simplified for Phase 3) ---
                    # In a bull regime, buy; in sideways, do nothing; in bear, sell (if holding)
                    current_price_data = self.data_fetcher.fetch_realtime_data(pair) # Get current price
                    if current_price_data['status'] == 'success':
                        current_price = current_price_data['price']
                        symbol = pair.replace("/", "") # Remove slash for symbol

                        if regime == 'bull':
                            order_params = {'order_type': 'buy', 'symbol': symbol, 'amount': 0.01, 'price': current_price} # Example amount
                            execution_result = self.execution_coordinator.execute_trade(order_params)
                            logger.info(f"Buy order placed for {pair} in bull regime. Result: {execution_result}")
                        elif regime == 'bear':
                            # Example: Sell if you have a position (simplified)
                            positions = self.execution_coordinator.get_portfolio_status()['positions']
                            if symbol in positions and positions[symbol]['amount'] > 0:
                                order_params = {'order_type': 'sell', 'symbol': symbol, 'amount': positions[symbol]['amount'], 'price': current_price} # Sell entire position
                                execution_result = self.execution_coordinator.execute_trade(order_params)
                                logger.info(f"Sell order placed for {pair} in bear regime. Result: {execution_result}")
                            else:
                                logger.info(f"Bear regime for {pair}, but no position to sell.")
                        elif regime == 'sideways':
                            logger.info(f"Sideways regime for {pair}, no action taken.")

                        # Log portfolio status after each pair's processing
                        portfolio_status = self.execution_coordinator.get_portfolio_status(current_prices_usd={symbol: current_price}) # Provide current price for PnL
                        logger.info(f"Portfolio Status after processing {pair}: {portfolio_status}")

                    else:
                        logger.warning(f"Could not fetch realtime price for {pair}, skipping trading logic.")
                    # --- End of Example Strategy Logic ---

                else:
                    logger.warning(f"No cleaned data for {pair}, skipping analysis and trading.")
            else:
                logger.error(f"Failed to fetch historical data for {pair}.")
        logger.info("Strategist finished execution.")


if __name__ == "__main__":
    logger.info("Starting the-hand crypto trading platform...")

    data_fetcher = DataFetcher()
    data_cleaner = DataCleaner()
    technical_analyzer = TechnicalAnalyzer()
    regime_classifier = RegimeClassifier()
    execution_coordinator = ExecutionCoordinator(mode=config.MODE) # Initialize ExecutionCoordinator with mode from config

    strategist = Strategist(
        mode=config.MODE,
        asset_pairs=config.ASSET_PAIRS,
        risk_tolerance=config.RISK_TOLERANCE,
        data_fetcher=data_fetcher,
        data_cleaner=data_cleaner,
        technical_analyzer=technical_analyzer,
        regime_classifier=regime_classifier,
        execution_coordinator=execution_coordinator # Pass ExecutionCoordinator to Strategist
    )
    strategist.run()

    logger.info("the-hand platform execution completed.")
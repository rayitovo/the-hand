# main.py
import config
from utils.logger import logger
from data_module.data_fetcher import DataFetcher
from data_module.data_cleaner import DataCleaner
from regime_info.technical_analyzer import TechnicalAnalyzer
from regime_info.regime_classifier import RegimeClassifier
import pandas as pd

class Strategist:
    def __init__(self, mode, asset_pairs, risk_tolerance, data_fetcher, data_cleaner, technical_analyzer, regime_classifier):
        self.mode = mode
        self.asset_pairs = asset_pairs
        self.risk_tolerance = risk_tolerance
        self.data_fetcher = data_fetcher
        self.data_cleaner = data_cleaner
        self.technical_analyzer = technical_analyzer
        self.regime_classifier = regime_classifier
        logger.info(f"Strategist initialized in {self.mode} mode for pairs: {self.asset_pairs} with risk tolerance: {self.risk_tolerance}")

    def run(self):
        logger.info("Strategist running...")
        for pair in self.asset_pairs:
            raw_historical_data = self.data_fetcher.fetch_historical_data(pair, interval="1d", limit=300) # Fetch daily data
            if raw_historical_data:
                cleaned_data = self.data_cleaner.clean_historical_data(raw_historical_data)
                if cleaned_data:
                    df = pd.DataFrame(cleaned_data)
                    close_prices = df['close']

                    # Example: Calculate SMA and RSI
                    sma_50 = self.technical_analyzer.calculate_sma(close_prices, window=50)
                    rsi_14 = self.technical_analyzer.calculate_rsi(close_prices)
                    logger.info(f"Technical indicators for {pair}: SMA50 (last): {sma_50.iloc[-1]:.2f}, RSI14 (last): {rsi_14.iloc[-1]:.2f}")

                    # Example: Classify regime
                    regime = self.regime_classifier.classify_regime_sma_crossover(close_prices)
                    logger.info(f"Market regime for {pair}: {regime}")
                else:
                    logger.warning(f"No cleaned data for {pair}, skipping analysis.")
            else:
                logger.error(f"Failed to fetch historical data for {pair}.")
        logger.info("Strategist finished execution.")


if __name__ == "__main__":
    logger.info("Starting the-hand crypto trading platform...")

    data_fetcher = DataFetcher() # Initialize DataFetcher (defaults to Binance)
    data_cleaner = DataCleaner()
    technical_analyzer = TechnicalAnalyzer()
    regime_classifier = RegimeClassifier()

    strategist = Strategist(
        mode=config.MODE,
        asset_pairs=config.ASSET_PAIRS,
        risk_tolerance=config.RISK_TOLERANCE,
        data_fetcher=data_fetcher,
        data_cleaner=data_cleaner,
        technical_analyzer=technical_analyzer,
        regime_classifier=regime_classifier
    )
    strategist.run()

    logger.info("the-hand platform execution completed.")
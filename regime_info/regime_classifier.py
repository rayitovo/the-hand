# regime_info/regime_classifier.py
from utils.logger import logger
import pandas as pd

class RegimeClassifier:
    def __init__(self):
        logger.info("RegimeClassifier initialized.")

    def classify_regime_sma_crossover(self, close_prices, sma_short_window=50, sma_long_window=200):
        """
        Classifies market regime based on SMA crossover (50 and 200 periods).
        Regimes: "bull", "bear", "sideways".
        Args:
            close_prices (pd.Series): Pandas Series of closing prices.
            sma_short_window (int): Window for short-term SMA.
            sma_long_window (int): Window for long-term SMA.
        Returns:
            str: Market regime label ("bull", "bear", "sideways").
        """
        try:
            sma_short = close_prices.rolling(window=sma_short_window).mean()
            sma_long = close_prices.rolling(window=sma_long_window).mean()

            last_sma_short = sma_short.iloc[-1]
            last_sma_long = sma_long.iloc[-1]
            last_price = close_prices.iloc[-1]

            if last_sma_short > last_sma_long and last_price > last_sma_short:
                return "bull"
            elif last_sma_short < last_sma_long and last_price < last_sma_short:
                return "bear"
            else:
                return "sideways" # Or "neutral", "ranging" etc.
        except Exception as e:
            logger.error(f"Error classifying regime based on SMA crossover: {e}")
            return "unknown" # Or None, or raise exception


if __name__ == '__main__':
    # Example Usage:
    import data_module.data_fetcher
    import data_module.data_cleaner
    import regime_info.technical_analyzer

    fetcher = data_module.data_fetcher.DataFetcher()
    cleaner = data_module.data_cleaner.DataCleaner()
    analyzer = regime_info.technical_analyzer.TechnicalAnalyzer()
    classifier = RegimeClassifier()

    pair = "BTC/USDT"
    interval = "1d"
    raw_data = fetcher.fetch_historical_data(pair, interval=interval, limit=300) # Need enough data for 200 SMA
    if raw_data:
        cleaned_data = cleaner.clean_historical_data(raw_data)
        df = pd.DataFrame(cleaned_data)
        close_prices = df['close']

        regime = classifier.classify_regime_sma_crossover(close_prices)
        print(f"Current market regime for {pair} (based on SMA crossover): {regime}")
    else:
        print("Failed to fetch data for regime classification example.")
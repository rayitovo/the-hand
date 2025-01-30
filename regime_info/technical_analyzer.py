# regime_info/technical_analyzer.py
import pandas as pd # pandas is great for time series and technical indicators
from utils.logger import logger

class TechnicalAnalyzer:
    def __init__(self):
        logger.info("TechnicalAnalyzer initialized.")

    def calculate_sma(self, prices, window):
        """
        Calculates Simple Moving Average (SMA).
        Args:
            prices (pd.Series): Pandas Series of prices.
            window (int): SMA window period.
        Returns:
            pd.Series: SMA values.
        """
        try:
            sma = prices.rolling(window=window).mean()
            return sma
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return None

    def calculate_rsi(self, prices, window=14): # Default RSI window is 14
        """
        Calculates Relative Strength Index (RSI).
        Args:
            prices (pd.Series): Pandas Series of prices.
            window (int): RSI window period.
        Returns:
            pd.Series: RSI values.
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)

            avg_gain = gain.rolling(window=window, min_periods=1).mean()
            avg_loss = loss.rolling(window=window, min_periods=1).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None


if __name__ == '__main__':
    # Example usage:
    import data_module.data_fetcher
    import data_module.data_cleaner

    fetcher = data_module.data_fetcher.DataFetcher()
    cleaner = data_module.data_cleaner.DataCleaner()
    analyzer = TechnicalAnalyzer()

    pair = "BTC/USDT"
    interval = "1d"
    raw_data = fetcher.fetch_historical_data(pair, interval=interval, limit=200) # Get enough data for SMAs and RSI
    if raw_data:
        cleaned_data = cleaner.clean_historical_data(raw_data)
        df = pd.DataFrame(cleaned_data) # Convert to Pandas DataFrame for easier processing
        close_prices = df['close']

        sma_50 = analyzer.calculate_sma(close_prices, window=50)
        sma_200 = analyzer.calculate_sma(close_prices, window=200)
        rsi_14 = analyzer.calculate_rsi(close_prices)

        print(f"SMA 50 (last 10 values):\n{sma_50.tail(10)}")
        print(f"\nSMA 200 (last 10 values):\n{sma_200.tail(10)}")
        print(f"\nRSI 14 (last 10 values):\n{rsi_14.tail(10)}")
    else:
        print("Failed to fetch data for technical analysis example.")
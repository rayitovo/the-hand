import datetime
from typing import List, Dict

from data_module.data_fetcher import DataFetcher
from regime_info.technical_analyzer import TechnicalAnalyzer
from regime_info.macro_analyzer import MacroAnalyzer
from regime_info.regime_classifier import RegimeClassifier

class HistoricalRegimeProvider:
    """
    Fetches historical data for a specified time range from data_module, then applies
    regime classification logic (technical, macro, etc.) to produce a time series
    of regime labels for each time slice in the historical data.
    """

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()
        self.macro_analyzer = MacroAnalyzer()
        self.regime_classifier = RegimeClassifier()

    def fetch_historical_regime_data(
        self,
        symbol: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Fetches historical OHLCV data for the given symbol and date range,
        then applies regime classification logic to produce a list of
        dictionaries, each containing:
            {
                "timestamp": datetime,
                "price": float,
                "regime_label": str
            }
        """
        # 1. Fetch historical market data
        historical_data = self.data_fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        # 2. Prepare results
        labeled_data = []

        # 3. For each data point, run analysis
        for data_point in historical_data:
            # For simplicity, we assume data_point includes keys: ["timestamp", "open", "high", "low", "close", "volume"]
            timestamp = data_point["timestamp"]
            close_price = data_point["close"]

            # Run technical analysis
            tech_signals = self.technical_analyzer.analyze_prices([close_price])

            # Optionally run macro analysis (skipping details for now)
            macro_signals = self.macro_analyzer.get_macro_signals(timestamp)

            # Combine signals in the regime classifier
            regime_label = self.regime_classifier.classify_regime(tech_signals, macro_signals)

            labeled_data.append({
                "timestamp": timestamp,
                "price": close_price,
                "regime_label": regime_label
            })

        return labeled_data
# main.py
import config
from utils.logger import logger
from data_module.data_fetcher import DataFetcher

class Strategist:  # Placeholder Strategist
    def __init__(self, mode, asset_pairs, risk_tolerance, data_fetcher):
        self.mode = mode
        self.asset_pairs = asset_pairs
        self.risk_tolerance = risk_tolerance
        self.data_fetcher = data_fetcher
        logger.info(f"Strategist initialized in {self.mode} mode for pairs: {self.asset_pairs} with risk tolerance: {self.risk_tolerance}")

    def run(self):
        logger.info("Strategist running...")
        # Example of using DataFetcher
        for pair in self.asset_pairs:
            realtime_data = self.data_fetcher.fetch_realtime_data(pair)
            logger.info(f"Received data for {pair}: {realtime_data['message']}")
        logger.info("Strategist finished execution.")


if __name__ == "__main__":
    logger.info("Starting the-hand crypto trading platform...")

    data_fetcher = DataFetcher(data_source=config.DATA_SOURCE) # Initialize DataFetcher

    strategist = Strategist(
        mode=config.MODE,
        asset_pairs=config.ASSET_PAIRS,
        risk_tolerance=config.RISK_TOLERANCE,
        data_fetcher=data_fetcher
    )
    strategist.run()

    logger.info("the-hand platform execution completed.")
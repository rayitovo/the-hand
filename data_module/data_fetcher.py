# data_module/data_fetcher.py
import requests
import json  # for debugging, can remove later
from utils.logger import logger
import time
import config

class DataFetcher:
    def __init__(self, data_source="binance"): # Default to Binance for now
        self.data_source = data_source.lower()
        if self.data_source != "binance":
            raise ValueError(f"Unsupported data source: {data_source}. For Phase 2, only 'binance' is supported.")
        self.base_url = "https://api.binance.com/api/v3"
        logger.info(f"DataFetcher initialized with source: {self.data_source}")

    def fetch_historical_data(self, pair, interval, limit=1000): # Binance API limit is 1000
        """
        Fetches historical candlestick data from Binance.
        Args:
            pair (str): Trading pair (e.g., "BTCUSDT"). Binance uses USDT instead of USD in pairs.
            interval (str): Candlestick interval (e.g., "1m", "5m", "1h", "1d").
            limit (int): Number of data points to fetch (max 1000 for Binance).
        Returns:
            list: List of candlestick data or None if error.
        """
        symbol = pair.replace("/", "").upper() # Binance uses e.g., BTCUSDT, not BTC/USD
        endpoint = "/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            # Example of raw kline data from Binance API:
            # [
            #     [
            #         1499040000000,      // Open time
            #         "0.01634790",       // Open
            #         "0.80000000",       // High
            #         "0.01575800",       // Low
            #         "0.01577100",       // Close
            #         "148976.11427815",  // Volume
            #         1499644799999,      // Close time
            #         "2434.19055334",    // Quote asset volume
            #         308,                // Number of trades
            #         "1756.87232846",    // Taker buy base asset volume
            #         "28.46694368",      // Taker buy quote asset volume
            #         "0"                 // Ignore.
            #     ],
            #     [...]
            # ]
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Binance for {pair}: {e}")
            return None

    def fetch_realtime_data(self, pair):
        """Placeholder for fetching realtime data (can be implemented later, e.g., using WebSocket)."""
        logger.info(f"Fetching realtime data for {pair} from {self.data_source} (placeholder)")
        # For now, let's just fetch the latest Kline (1 minute) as "realtime"
        data = self.fetch_historical_data(pair, interval="1m", limit=1)
        if data:
            # Extract only the last candlestick's closing price for simplicity as "realtime price"
            last_candle = data[-1] if data else None
            if last_candle:
                realtime_price = float(last_candle[4]) # Close price is at index 4
                return {"status": "success", "price": realtime_price, "timestamp": last_candle[0]}
            else:
                return {"status": "error", "message": "No realtime data fetched."}
        else:
            return {"status": "error", "message": "Error fetching realtime data."}


if __name__ == '__main__':
    fetcher = DataFetcher() # Default to Binance
    pair = "BTC/USDT" # Binance uses USDT pairs
    interval = "1h"
    historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=10)
    if historical_data:
        print(f"Successfully fetched historical data for {pair} ({interval}):")
        print(json.dumps(historical_data, indent=2)) # Pretty print for readability
    else:
        print(f"Failed to fetch historical data for {pair} ({interval}).")

    realtime_data = fetcher.fetch_realtime_data("ETH/USDT")
    print("\nRealtime data for ETH/USDT:")
    print(realtime_data)
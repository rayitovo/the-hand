# data_module/data_fetcher.py
import requests
import json
from utils.logger import logger
import time
import config
from data_module.database_handler import DatabaseHandler

class DataFetcher:
    def __init__(self, data_source="binance"):
        self.data_source = data_source.lower()
        self.db_handler = DatabaseHandler() # Initialize DatabaseHandler

        if self.data_source == "binance":
            self.base_url = "https://api.binance.com/api/v3"
        elif self.data_source == "coinbase":
            self.base_url = "https://api.coinbase.com/v2"  # Example Coinbase API base URL
        # Add more exchanges/APIs as needed
        else:
            raise ValueError(f"Unsupported data source: {data_source}")

        logger.info(f"DataFetcher initialized with source: {self.data_source}")

    def fetch_historical_data(self, pair, interval, limit=1000):
        """
        Fetches historical candlestick data.
        Args:
            pair (str): Trading pair (e.g., "BTCUSDT", "ETHUSD").
            interval (str): Candlestick interval (e.g., "1m", "5m", "1h", "1d").
            limit (int): Number of data points to fetch (exchange-specific limits apply).
        Returns:
            list: List of candlestick data or None if error.
        """
        if self.data_source == "binance":
            return self._fetch_historical_data_binance(pair, interval, limit)
        elif self.data_source == "coinbase":
            return self._fetch_historical_data_coinbase(pair, interval, limit)
        # Add more exchange-specific methods as needed
        else:
            logger.error(f"Unsupported data source for historical data: {self.data_source}")
            return None

    def _fetch_historical_data_binance(self, pair, interval, limit):
        """Fetches historical candlestick data from Binance."""
        symbol = pair.replace("/", "").upper()
        endpoint = "/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # Insert data into database
            if data:
                data_to_insert = [(symbol, str(candle[0]), float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4]), float(candle[5]), str(candle[6]), float(candle[7]), int(candle[8]), float(candle[9]), float(candle[10])) for candle in data]
                self.db_handler.insert_data("klines", data_to_insert)
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Binance for {pair}: {e}")
            return None

    def _fetch_historical_data_coinbase(self, pair, interval, limit):
        """Fetches historical candlestick data from Coinbase."""
        symbol = pair.replace("/", "-").upper()
        endpoint = f"/products/{symbol}/candles"  # Example Coinbase endpoint
        granularity = self._map_interval_to_coinbase_granularity(interval)
        params = {
            "granularity": granularity
            # Add start/end times if needed for Coinbase
        }
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Adapt the parsing and database insertion logic for Coinbase data format

            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Coinbase for {pair}: {e}")
            return None

    def _map_interval_to_coinbase_granularity(self, interval):
        """Maps common interval notation (e.g., 1m, 1h, 1d) to Coinbase's granularity."""
        mapping = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "6h": 21600,
            "1d": 86400,
        }
        return mapping.get(interval, 3600) # Default to 1h if not found

    def fetch_realtime_data(self, pair):
        """Fetches realtime data (placeholder - can be improved with WebSocket)."""
        logger.info(f"Fetching realtime data for {pair} from {self.data_source} (placeholder)")
        # For now, just fetch the latest Kline (1 minute) as "realtime"
        if self.data_source == "binance":
            data = self._fetch_historical_data_binance(pair, interval="1m", limit=1)
        elif self.data_source == "coinbase":
            data = self._fetch_historical_data_coinbase(pair, interval="1m", limit=1)
        else:
            logger.error(f"Unsupported data source for realtime data: {self.data_source}")
            return {"status": "error", "message": "Unsupported data source"}

        if data:
            # Extract only the last candlestick's closing price for simplicity as "realtime price"
            last_candle = data[-1] if data else None
            if last_candle:
                if self.data_source == "binance":
                    realtime_price = float(last_candle[4])
                    return {"status": "success", "price": realtime_price, "timestamp": last_candle[0]}
                elif self.data_source == "coinbase":
                    # Adapt parsing for Coinbase
                    realtime_price = float(last_candle[4]) # Example assuming close price is at index 4
                    return {"status": "success", "price": realtime_price, "timestamp": last_candle[0]}
            else:
                return {"status": "error", "message": "No realtime data fetched."}
        else:
            return {"status": "error", "message": "Error fetching realtime data."}

    # Add methods for fetching data from other exchanges/APIs as needed
    # Example: def fetch_data_from_coinbase(self, ...):

if __name__ == '__main__':
    fetcher = DataFetcher(data_source="binance")  # Or "coinbase", etc.
    pair = "BTC/USDT"  # Or "BTC-USD" for Coinbase
    interval = "1h"
    historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=10)
    if historical_data:
        print(f"Successfully fetched historical data for {pair} ({interval}):")
        print(json.dumps(historical_data, indent=2))  # Pretty print for readability
    else:
        print(f"Failed to fetch historical data for {pair} ({interval}).")

    realtime_data = fetcher.fetch_realtime_data(pair)
    print("\nRealtime data:")
    print(realtime_data)
# data_module/data_cleaner.py
import datetime
from utils.logger import logger

class DataCleaner:
    def __init__(self):
        logger.info("DataCleaner initialized.")

    def clean_historical_data(self, raw_data):
        """
        Cleans and normalizes historical candlestick data from Binance.
        Args:
            raw_data (list): Raw candlestick data from Binance API.
        Returns:
            list: Cleaned data as a list of dictionaries.
        """
        cleaned_data = []
        if not raw_data:
            return cleaned_data  # Return empty list if no data

        for candle in raw_data:
            try:
                cleaned_candle = {
                    "open_timestamp": datetime.datetime.fromtimestamp(candle[0]/1000.0), # Convert ms to seconds
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_timestamp": datetime.datetime.fromtimestamp(candle[6]/1000.0),
                    "quote_asset_volume": float(candle[7]),
                    "trades": int(candle[8]),
                    "taker_buy_base_asset_volume": float(candle[9]),
                    "taker_buy_quote_asset_volume": float(candle[10]),
                    "ignore": candle[11] # Or can be ignored
                }
                cleaned_data.append(cleaned_candle)
            except (ValueError, IndexError) as e:
                logger.error(f"Error cleaning candle data: {e}. Raw candle: {candle}")
                continue # Skip problematic candle and continue

        logger.info(f"Cleaned {len(cleaned_data)} candlestick data points.")
        return cleaned_data

    def clean_realtime_data(self, raw_realtime_data):
        """
        Cleans realtime data (for now, just price and timestamp).
        """
        if raw_realtime_data and raw_realtime_data["status"] == "success":
            try:
                timestamp_ms = raw_realtime_data.get("timestamp")
                timestamp_dt = datetime.datetime.fromtimestamp(timestamp_ms/1000.0) if timestamp_ms else None
                cleaned_realtime_data = {
                    "status": "success",
                    "price": float(raw_realtime_data["price"]),
                    "timestamp": timestamp_dt
                }
                return cleaned_realtime_data
            except (ValueError, KeyError) as e:
                logger.error(f"Error cleaning realtime data: {e}. Raw data: {raw_realtime_data}")
                return {"status": "error", "message": "Error cleaning realtime data."}
        return raw_realtime_data # Return original if error or not successful


if __name__ == '__main__':
    from data_module.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    cleaner = DataCleaner()

    pair = "BTC/USDT"
    interval = "1h"
    raw_historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=5)
    if raw_historical_data:
        cleaned_historical_data = cleaner.clean_historical_data(raw_historical_data)
        print("Cleaned Historical Data (first 2 candles):")
        for i in range(min(2, len(cleaned_historical_data))): # Print only first 2 for brevity
            print(cleaned_historical_data[i])

    raw_realtime_data = fetcher.fetch_realtime_data("ETH/USDT")
    cleaned_realtime_data = cleaner.clean_realtime_data(raw_realtime_data)
    print("\nCleaned Realtime Data:")
    print(cleaned_realtime_data)
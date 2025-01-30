# trading_core/event_logger.py
import csv
import os
from utils.logger import logger
import pandas as pd

class EventLogger:
    def __init__(self, log_dir='data/logs', filename='transactions.csv'):
        self.log_dir = log_dir
        self.filename = filename
        self.filepath = os.path.join(self.log_dir, self.filename)
        self._ensure_log_directory_exists()
        self.header_written = os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0 # Check if file exists and is not empty

    def _ensure_log_directory_exists(self):
        """Creates the log directory if it doesn't exist."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_event(self, event_data):
        """
        Logs a trading event to the CSV file.
        Args:
            event_data (dict): Dictionary containing event details (e.g., trade details).
        """
        try:
            with open(self.filepath, mode='a', newline='') as csvfile:
                fieldnames = event_data.keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not self.header_written: # Write header only if not already written
                    writer.writeheader()
                    self.header_written = True
                writer.writerow(event_data)
            logger.debug(f"Event logged to {self.filepath}: {event_data}")
        except Exception as e:
            logger.error(f"Error logging event to CSV: {e}")

    def log_trade(self, trade_record):
        """
        Logs a trade record from PortfolioManager to the event log.
        Args:
            trade_record (dict): Trade record dictionary from PortfolioManager.
        """
        self.log_event(trade_record)


if __name__ == '__main__':
    event_logger = EventLogger() # Uses default log directory and filename

    # Example trade record (mimicking output from PortfolioManager)
    example_trade = {
        'type': 'buy',
        'symbol': 'BTC',
        'amount': 0.01,
        'price': 30500.00,
        'usd_value': 305.00,
        'timestamp': pd.Timestamp.now() # Or use a string timestamp if you prefer
    }

    event_logger.log_trade(example_trade)
    print(f"Logged example trade to {event_logger.filepath}")

    # You can check the data/logs/transactions.csv file to see the logged event.
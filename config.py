# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "simulation")  # Default to "simulation" if MODE is not set in .env
ASSET_PAIRS = os.getenv("ASSET_PAIRS", "BTC/USDT,ETH/USDT").split(",") # Default pairs, split into a list
RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", 0.02)) # Default risk tolerance, convert to float
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") # Default log level
DATA_SOURCE = os.getenv("DATA_SOURCE", "binance") # Default data source
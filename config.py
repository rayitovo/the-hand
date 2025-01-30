# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "simulation")
ASSET_PAIRS = os.getenv("ASSET_PAIRS", "BTC/USDT,ETH/USDT").split(",")
RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", 0.02))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_SOURCE = os.getenv("DATA_SOURCE", "binance")

RUN_MODE = os.getenv("RUN_MODE", "strategist") # Default to 'strategist' run
BACKTEST_STRATEGY = os.getenv("BACKTEST_STRATEGY") # Strategy name for backtesting
BACKTEST_REGIME = os.getenv("BACKTEST_REGIME") # Regime for backtesting
MACRO_API_KEY = os.getenv("MACRO_API_KEY") # API key for macro data
# config.py
import os
from dotenv import load_dotenv

load_dotenv()
MODE = os.getenv("MODE", "simulation")
ASSET_PAIRS = os.getenv("ASSET_PAIRS", "BTC/USDT,ETH/USDT").split(",")
RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", 0.02))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_SOURCE = os.getenv("DATA_SOURCE", "binance")

RUN_MODE = os.getenv("RUN_MODE") # Default to 'strategist' run
print(RUN_MODE)
INTEGRATION_DEMO_TEST = os.getenv("INTEGRATION_DEMO_TEST", "False")
BACKTEST_STRATEGY = os.getenv("BACKTEST_STRATEGY", "all") # Strategy name for backtesting
BACKTEST_REGIME = os.getenv("BACKTEST_REGIME", "bull") # Regime for backtesting

# Strategy approval thresholds
MIN_SHARPE_RATIO = float(os.getenv('MIN_SHARPE_RATIO', 1.0))
MAX_DRAWDOWN = float(os.getenv('MAX_DRAWDOWN', 0.2))  # 20% max drawdown
MIN_WIN_RATE = float(os.getenv('MIN_WIN_RATE', 0.55))  # 55% win rate

# Backtest parameters
BACKTEST_START_DATE = os.getenv('BACKTEST_START_DATE', '2024-01-01')
BACKTEST_END_DATE = os.getenv('BACKTEST_END_DATE', '2024-12-31')
BACKTEST_INITIAL_BALANCE = float(os.getenv('BACKTEST_INITIAL_BALANCE', 10000.0))

MACRO_API_KEY = os.getenv("MACRO_API_KEY") # API key for macro data

# Phase 8 demo exchange credentials
DEMO_EXCHANGE_API_KEY = os.getenv("DEMO_EXCHANGE_API_KEY", "")
DEMO_EXCHANGE_API_SECRET = os.getenv("DEMO_EXCHANGE_API_SECRET", "")
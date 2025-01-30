# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "simulation")  # Default to simulation if not set
ASSET_PAIRS = os.getenv("ASSET_PAIRS", "BTC/USD,ETH/USD").split(",")
RISK_TOLERANCE = float(os.getenv("RISK_TOLERANCE", 0.02))
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DATA_SOURCE = os.getenv("DATA_SOURCE", "mock_api")
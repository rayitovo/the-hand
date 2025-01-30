# strategy/base_strategy.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    All concrete strategies must inherit from this class and implement the abstract methods.
    """

    def __init__(self, name, symbol, params=None):
        """
        Constructor for BaseStrategy.
        Args:
            name (str): Name of the strategy.
            symbol (str): Trading symbol for the strategy (e.g., 'BTCUSDT').
            params (dict, optional): Strategy parameters. Defaults to None.
        """
        self.name = name
        self.symbol = symbol
        self.params = params or {} # Ensure params is always a dict, even if None is passed

    @abstractmethod
    def generate_signal(self, historical_data: pd.DataFrame, current_price: float = None) -> str:
        """
        Abstract method to generate a trading signal based on historical data and optionally current price.
        Subclasses must implement this method to define their strategy logic.
        Args:
            historical_data (pd.DataFrame): DataFrame containing historical market data.
            current_price (float, optional): Current price (if available/needed for strategy logic). Defaults to None.
        Returns:
            str: Trading signal: 'buy', 'sell', or 'hold'.
        """
        pass # Abstract method - must be implemented in subclasses

    def get_strategy_name(self):
        """Returns the name of the strategy."""
        return self.name

    def get_symbol(self):
        """Returns the trading symbol for the strategy."""
        return self.symbol

    def get_params(self):
        """Returns the strategy parameters."""
        return self.params

    def __str__(self):
        """String representation of the strategy."""
        return f"Strategy: {self.name}, Symbol: {self.symbol}, Params: {self.params}"

# Example of how to define a concrete strategy (not in this file, but in strategy files)
# class EMACrossoverStrategy(BaseStrategy):
#     def __init__(self, symbol, params=None):
#         super().__init__(name="EMA Crossover", symbol=symbol, params=params)
#
#     def generate_signal(self, historical_data: pd.DataFrame, current_price: float = None) -> str:
#         # ... Strategy logic here ...
#         return 'buy' or 'sell' or 'hold'

if __name__ == '__main__':
    # Example of instantiating and using a BaseStrategy (you cannot directly instantiate BaseStrategy as it's abstract)
    # strategy = BaseStrategy(name="ExampleStrategy", symbol="BTCUSDT", params={'param1': 10, 'param2': 20}) # This will raise TypeError
    # print(strategy)
    print("This is the base strategy class definition. Concrete strategies should be defined in separate files and inherit from BaseStrategy.")
from strategy.base_strategy import BaseStrategy
import pandas as pd

class Strategy(BaseStrategy):  # All strategies will use the class name "Strategy"
    """
    EMA Crossover Strategy.
    Generates buy/sell signals based on the crossover of short and long period Exponential Moving Averages (EMAs).
    """

    def __init__(self, name, symbol, params=None):
        """
        Constructor for Strategy.
        Params (dict, optional):
            'short_ema_period' (int): Period for the short EMA. Default is 20.
            'long_ema_period' (int): Period for the long EMA. Default is 50.
        """
        default_params = {'short_ema_period': 20, 'long_ema_period': 50}
        merged_params = default_params.copy()
        if params:
            merged_params.update(params)  # Override defaults with provided params
        super().__init__(name=name, symbol=symbol, params=merged_params) # You can use a descriptive name here

    def generate_signal(self, historical_data: pd.DataFrame, current_price: float = None) -> str:
        """
        Generates trading signal based on EMA crossover.
        Signal logic:
        - BUY: Short EMA crosses above Long EMA.
        - SELL: Short EMA crosses below Long EMA.
        - HOLD: Otherwise.
        Args:
            historical_data (pd.DataFrame): DataFrame with 'close' prices and timestamps.
        Returns:
            str: 'buy', 'sell', or 'hold' signal.
        """
        if historical_data.empty:
            return 'hold' # No data, no signal

        short_ema_period = self.params.get('short_ema_period')
        long_ema_period = self.params.get('long_ema_period')

        # Calculate EMAs
        short_ema = historical_data['close'].ewm(span=short_ema_period, adjust=False).mean()
        long_ema = historical_data['close'].ewm(span=long_ema_period, adjust=False).mean()

        # Get last EMA values
        last_short_ema = short_ema.iloc[-1]
        last_long_ema = long_ema.iloc[-1]
        previous_short_ema = short_ema.iloc[-2] if len(short_ema) > 1 else last_short_ema # Handle case with only one data point
        previous_long_ema = long_ema.iloc[-2] if len(long_ema) > 1 else last_long_ema   # Handle case with only one data point

        # Generate signals based on crossover
        if previous_short_ema <= previous_long_ema and last_short_ema > last_long_ema:
            return 'buy' # Short EMA crossed above Long EMA (Buy signal)
        elif previous_short_ema >= previous_long_ema and last_short_ema < last_long_ema:
            return 'sell' # Short EMA crossed below Long EMA (Sell signal)
        else:
            return 'hold' # No crossover, hold position

if __name__ == '__main__':
    # Example usage:
    # Create dummy historical data (replace with actual data in backtesting/live trading)
    data = {
        'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
        'close': [30000, 30200, 30500, 30400, 30600]
    }
    historical_df = pd.DataFrame(data).set_index('timestamp')

    ema_strategy = Strategy(symbol="BTCUSDT", params={'short_ema_period': 10, 'long_ema_period': 30}) # Example params
    signal = ema_strategy.generate_signal(historical_df)
    print(f"Strategy: {ema_strategy.get_strategy_name()}, Symbol: {ema_strategy.get_symbol()}, Signal: {signal}, Params: {ema_strategy.get_params()}")

    # Example with crossover data
    crossover_data = {
        'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06']),
        'close': [30000, 30200, 30300, 30400, 30600, 30900] # Prices going up, potential buy signal
    }
    crossover_df = pd.DataFrame(crossover_data).set_index('timestamp')
    signal_crossover = ema_strategy.generate_signal(crossover_df)
    print(f"Strategy: {ema_strategy.get_strategy_name()}, Symbol: {ema_strategy.get_symbol()}, Signal (Crossover Data): {signal_crossover}, Params: {ema_strategy.get_params()}")

    # Example with downward data
    downward_data = {
        'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06']),
        'close': [31000, 30800, 30600, 30500, 30300, 30000] # Prices going down, potential sell signal
    }
    downward_df = pd.DataFrame(downward_data).set_index('timestamp')
    signal_downward = ema_strategy.generate_signal(downward_df)
    print(f"Strategy: {ema_strategy.get_strategy_name()}, Symbol: {ema_strategy.get_symbol()}, Signal (Downward Data): {signal_downward}, Params: {ema_strategy.get_params()}")
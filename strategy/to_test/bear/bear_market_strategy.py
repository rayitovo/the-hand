from strategy.base_strategy import BaseStrategy
import pandas as pd

class Strategy(BaseStrategy):
    """Bear market strategy that looks for downward trends to short"""

    def __init__(self, name, symbol, params=None):
        super().__init__(
            name=name,
            symbol=symbol,
            params=params or {'sma_window': 50, 'rsi_window': 14}
        )
        
    def generate_signal(self, historical_data: pd.DataFrame, current_price: float = None) -> str:
        """
        Generates sell signal when:
        - SMA is trending downward
        - RSI is above 70 (overbought)
        """
        # Calculate indicators
        sma = historical_data['close'].rolling(
            window=self.params['sma_window']).mean()
        rsi = self._calculate_rsi(historical_data)
        
        # Check conditions
        if (sma.iloc[-1] < sma.iloc[-2] and  # SMA trending down
            rsi.iloc[-1] > 70):  # Overbought
            return 'sell'
            
        return 'hold'
        
    def _calculate_rsi(self, data, window=14):
        """Calculate Relative Strength Index"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
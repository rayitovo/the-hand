from strategy.base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class Strategy(BaseStrategy):
    """Sideways market strategy that looks for range-bound conditions"""
    
    def __init__(self, name, symbol, params=None):
        super().__init__(
            name=name,
            symbol=symbol,
            params=params or {
                'atr_window': 14,
                'range_threshold': 0.02  # 2% price range
            }
        )
        
    def generate_signal(self, historical_data: pd.DataFrame, current_price: float = None) -> str:
        """
        Generates signals based on range-bound conditions:
        - Buy near support level
        - Sell near resistance level
        - Hold otherwise
        """
        # Calculate ATR for volatility
        atr = self._calculate_atr(historical_data)
        
        # Calculate support/resistance levels
        support = historical_data['low'].rolling(window=self.params['atr_window']).min()
        resistance = historical_data['high'].rolling(window=self.params['atr_window']).max()
        
        # Check if price is near support/resistance
        if current_price:
            if current_price <= support.iloc[-1] * (1 + self.params['range_threshold']):
                return 'buy'
            elif current_price >= resistance.iloc[-1] * (1 - self.params['range_threshold']):
                return 'sell'
                
        return 'hold'
        
    def _calculate_atr(self, data):
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=self.params['atr_window']).mean()
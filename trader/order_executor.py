"""
Handle different order types (market, limit, OCO) using an actual or demo exchange API.

High-level flow:
1. Initialize OrderExecutor with references to ExchangeConnector and RiskManager.
2. Provide methods to execute orders: execute_market_order, execute_limit_order, execute_oco_order, etc.
3. Use the exchange_connector to place and manage orders on the exchange (or demo exchange).
4. Incorporate relevant risk management checks before placing orders.
"""

import logging
from trader.exchange_connector import ExchangeConnector
from trader.risk_manager import RiskManager

class OrderExecutor:
    def __init__(self, connector: ExchangeConnector, risk_manager: RiskManager):
        self.connector = connector
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(__name__)

    def execute_market_order(self, symbol: str, side: str, quantity: float):
        # Perform risk checks
        if not self.risk_manager.validate_order(symbol, side, "market", quantity):
            self.logger.warning("Market order blocked by risk manager.")
            return None
        
        # Place the order
        response = self.connector.place_order(
            symbol=symbol,
            side=side,
            order_type="market",
            quantity=quantity
        )
        self.logger.info(f"Market order response: {response}")
        return response

    def execute_limit_order(self, symbol: str, side: str, quantity: float, price: float):
        if not self.risk_manager.validate_order(symbol, side, "limit", quantity, price=price):
            self.logger.warning("Limit order blocked by risk manager.")
            return None
        
        response = self.connector.place_order(
            symbol=symbol,
            side=side,
            order_type="limit",
            quantity=quantity,
            price=price
        )
        self.logger.info(f"Limit order response: {response}")
        return response

    def execute_oco_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float):
        """
        One-Cancels-the-Other (OCO): Typically, a stop order and a limit order are placed simultaneously.
        If one is triggered, the other is canceled.
        """
        if not self.risk_manager.validate_order(symbol, side, "oco", quantity, price=price, stop_price=stop_price):
            self.logger.warning("OCO order blocked by risk manager.")
            return None

        response = self.connector.place_oco_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        self.logger.info(f"OCO order response: {response}")
        return response
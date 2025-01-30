# simulation/virtual_exchange.py
import time
import random
from utils.logger import logger

class VirtualExchange:
    def __init__(self, latency_mean=0.1, latency_std=0.02, slippage_mean=0.0001, slippage_std=0.00005):
        self.latency_mean = latency_mean  # Mean latency in seconds
        self.latency_std = latency_std  # Standard deviation of latency
        self.slippage_mean = slippage_mean # Mean slippage (as a fraction of price, e.g., 0.0001 means 0.01% slippage)
        self.slippage_std = slippage_std # Standard deviation of slippage
        logger.info("VirtualExchange initialized with latency and slippage simulation.")

    def execute_order(self, order_params):
        """
        Simulates order execution on a virtual exchange with latency and slippage.
        Args:
            order_params (dict): Dictionary containing order details:
                                 {'order_type': 'buy'/'sell', 'symbol': 'BTC', 'amount': float, 'price': float}
        Returns:
            dict: Order execution result: {'status': 'success'/'failure', 'executed_price': float, 'executed_amount': float, 'latency': float}
        """
        order_type = order_params.get('order_type')
        symbol = order_params.get('symbol')
        amount = order_params.get('amount')
        price = order_params.get('price')

        if not all([order_type, symbol, amount, price]):
            logger.error(f"Invalid order parameters: {order_params}. Missing order_type, symbol, amount, or price.")
            return {'status': 'failure', 'message': 'Invalid order parameters'}

        if order_type not in ['buy', 'sell']:
            logger.error(f"Invalid order type: {order_type}. Must be 'buy' or 'sell'.")
            return {'status': 'failure', 'message': 'Invalid order type'}

        if amount <= 0 or price <= 0:
            logger.error(f"Invalid order amount or price. Amount: {amount}, Price: {price}. Must be positive values.")
            return {'status': 'failure', 'message': 'Invalid amount or price'}

        # Simulate Latency
        latency = random.gauss(self.latency_mean, self.latency_std)
        latency = max(0, latency)  # Ensure latency is not negative
        time.sleep(latency)

        # Simulate Slippage
        slippage_factor = random.gauss(self.slippage_mean, self.slippage_std)
        if order_type == 'buy':
            executed_price = price * (1 + slippage_factor)  # Buyer pays more due to slippage
        else:  # order_type == 'sell'
            executed_price = price * (1 - slippage_factor)  # Seller receives less due to slippage

        executed_amount = amount

        logger.info(f"Virtual Exchange: Executed {order_type} order for {executed_amount:.4f} {symbol} at ${executed_price:.2f} (requested price: ${price:.2f}, latency: {latency:.3f}s)")
        return {
            'status': 'success',
            'executed_price': executed_price,
            'executed_amount': executed_amount,
            'symbol': symbol,
            'order_type': order_type,
            'latency': latency
        }

if __name__ == '__main__':
    virtual_exchange = VirtualExchange()

    # Example buy order
    buy_order_params = {
        'order_type': 'buy',
        'symbol': 'BTC',
        'amount': 0.02,
        'price': 30200.00
    }
    buy_result = virtual_exchange.execute_order(buy_order_params)
    print("Buy order result:", buy_result)

    # Example sell order
    sell_order_params = {
        'order_type': 'sell',
        'symbol': 'BTC',
        'amount': 0.01,
        'price': 30500.00
    }
    sell_result = virtual_exchange.execute_order(sell_order_params)
    print("Sell order result:", sell_result)
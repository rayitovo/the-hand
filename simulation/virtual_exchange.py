# simulation/virtual_exchange.py
import time
from utils.logger import logger

class VirtualExchange:
    def __init__(self):
        logger.info("VirtualExchange initialized.")

    def execute_order(self, order_params):
        """
        Simulates order execution on a virtual exchange.
        Args:
            order_params (dict): Dictionary containing order details:
                                 {'order_type': 'buy'/'sell', 'symbol': 'BTC', 'amount': float, 'price': float}
        Returns:
            dict:  Order execution result: {'status': 'success'/'failure', 'executed_price': float, 'executed_amount': float}
                   For simplicity, in this phase, we assume successful execution at the requested price.
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

        # Simulate order processing delay (optional)
        time.sleep(0.1) # Simulate a small delay

        executed_price = price # In a virtual exchange, we can assume execution at requested price (no slippage in this phase)
        executed_amount = amount

        logger.info(f"Virtual Exchange: Executed {order_type} order for {executed_amount:.4f} {symbol} at ${executed_price:.2f}")
        return {
            'status': 'success',
            'executed_price': executed_price,
            'executed_amount': executed_amount,
            'symbol': symbol,
            'order_type': order_type
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
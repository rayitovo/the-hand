import inspect
from strategy.base_strategy import BaseStrategy

class StrategyValidator:
    """Validates that strategy implementations follow required structure"""
    
    @staticmethod
    def validate_strategy(strategy_class):
        """
        Validates that a strategy class implements required methods and follows structure.
        Args:
            strategy_class: The strategy class to validate
        Returns:
            tuple: (bool: is_valid, str: error_message)
        """
        # Check if class inherits from BaseStrategy
        if not issubclass(strategy_class, BaseStrategy):
            return False, "Strategy must inherit from BaseStrategy"
            
        # Check required methods
        required_methods = ['generate_signal']
        for method in required_methods:
            if not hasattr(strategy_class, method):
                return False, f"Missing required method: {method}"
                
            # Check method signature matches base class
            base_method = getattr(BaseStrategy, method)
            strategy_method = getattr(strategy_class, method)
            
            if not inspect.signature(base_method) == inspect.signature(strategy_method):
                return False, f"Method signature mismatch for {method}"
                
        # Check __init__ calls super().__init__ with name
        init_signature = inspect.signature(strategy_class.__init__)
        if 'name' not in init_signature.parameters:
            return False, "__init__ must accept 'name' parameter"
            
        return True, "Strategy is valid"

if __name__ == "__main__":
    # Example usage
    from strategy.approved.bull.ema_crossover import Strategy as EMACrossover
    
    is_valid, msg = StrategyValidator.validate_strategy(EMACrossover)
    print(f"Strategy valid: {is_valid}")
    print(f"Validation message: {msg}")
# backtester/report_generator.py
from utils.logger import logger

class ReportGenerator:
    def __init__(self):
        logger.info("ReportGenerator initialized.")

    def generate_report(self, backtest_results):
        """
        Generates a basic backtest report in plain text.
        Args:
            backtest_results (dict): Dictionary containing backtest results from BacktestEngine.run_backtest().
        Returns:
            str: Plain text report.
        """
        if backtest_results['status'] != 'completed':
            return "Backtest did not complete successfully. No report generated."

        report = f"""
        --- Backtest Report ---

        Strategy Name: {backtest_results['strategy_name']}
        Symbol:          {backtest_results['symbol']}
        Backtest Duration: {backtest_results['backtest_duration_seconds']:.2f} seconds

        Initial Balance:   ${backtest_results['initial_balance_usd']:.2f}
        Final Balance:     ${backtest_results['final_balance_usd']:.2f}
        Final Portfolio Value: ${backtest_results['final_portfolio_value_usd']:.2f}
        Total PnL:         ${backtest_results['total_pnl_usd']:.2f}

        Trade History Log: {backtest_results['trade_history_file']}

        --- End of Report ---
        """
        logger.info("Backtest report generated.")
        return report

    def save_report_to_file(self, report_text, filepath='data/logs/backtest_report.txt'):
        """
        Saves the backtest report text to a file.
        Args:
            report_text (str): The backtest report text.
            filepath (str): File path to save the report.
        """
        try:
            with open(filepath, 'w') as f:
                f.write(report_text)
            logger.info(f"Backtest report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving backtest report to file: {e}")
            return None


if __name__ == '__main__':
    # Example usage (assuming you have backtest_results from BacktestEngine example):
    from backtester.backtest_engine import BacktestEngine
    from strategy.approved.bull.ema_crossover import EmaCrossoverStrategy
    import data_module.data_fetcher
    import data_module.data_cleaner
    import pandas as pd

    # ... (Fetch historical data and run backtest as in backtest_engine.py example) ...
    fetcher = data_module.data_fetcher.DataFetcher()
    cleaner = data_module.data_cleaner.DataCleaner()
    pair = "BTC/USDT"
    interval = "1d"
    raw_historical_data = fetcher.fetch_historical_data(pair, interval=interval, limit=500)
    if raw_historical_data:
        cleaned_data = cleaner.clean_historical_data(raw_historical_data)
        historical_df = pd.DataFrame(cleaned_data).set_index('close_timestamp')
        ema_strategy = EmaCrossoverStrategy(symbol=pair.replace("/", ""))
        backtest_engine = BacktestEngine()
        backtest_results = backtest_engine.run_backtest(ema_strategy, historical_df, initial_balance_usd=10000)

        if backtest_results['status'] == 'completed':
            report_generator = ReportGenerator()
            report_text = report_generator.generate_report(backtest_results)
            print(report_text) # Print report to console

            report_filepath = report_generator.save_report_to_file(report_text) # Save to file
            if report_filepath:
                print(f"Backtest report saved to: {report_filepath}")
            else:
                print("Failed to save backtest report to file.")
        else:
            print("Backtest failed, no report generated.")
    else:
        print("Failed to fetch historical data for report example.")
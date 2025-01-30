# regime_info/macro_analyzer.py
import requests
from utils.logger import logger
import json
import config
import pandas as pd

class MacroAnalyzer:
    def __init__(self):
        self.api_key = config.MACRO_API_KEY  # Add MACRO_API_KEY to your .env and config.py
        self.base_url = "https://api.example-macro-data-provider.com" # Replace with actual API base URL
        logger.info("MacroAnalyzer initialized.")

    def fetch_cpi(self, country="US", start_date="2023-01-01", end_date=None):
        """
        Fetches CPI (Consumer Price Index) data from a macroeconomic data provider's API.
        Args:
            country (str): Country code (e.g., "US", "UK", "EU").
            start_date (str): Start date for the data (YYYY-MM-DD).
            end_date (str, optional): End date for the data (YYYY-MM-DD). If None, defaults to today's date.
        Returns:
            dict: CPI data (if successful) or None (if error).
                  Example: {'status': 'success', 'data': [{'date': '2023-01-01', 'cpi': 123.4}, {'date': '2023-02-01', 'cpi': 124.1}]}
                  or {'status': 'error', 'message': 'API Error...'}
        """
        if not end_date:
            end_date = pd.Timestamp.today().strftime('%Y-%m-%d') # Today's date if not provided

        endpoint = f"/cpi/{country}"
        url = self.base_url + endpoint
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"start_date": start_date, "end_date": end_date}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # Adapt the parsing logic based on the actual API response format
            if data['status'] == 'success':
                cpi_data = [{'date': item['date'], 'cpi': item['value']} for item in data['data']] # Example parsing
                return {'status': 'success', 'data': cpi_data}
            else:
                return {'status': 'error', 'message': data.get('message', 'Unknown API error')}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CPI data from API: {e}")
            return {'status': 'error', 'message': str(e)}
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing CPI data: {e}")
            return {'status': 'error', 'message': 'Error parsing API response'}

    # Add other methods for fetching other macroeconomic indicators (e.g., interest rates, GDP, etc.) as needed.

if __name__ == '__main__':
    macro_analyzer = MacroAnalyzer()
    cpi_data = macro_analyzer.fetch_cpi(country="US", start_date="2023-01-01", end_date="2023-12-31")
    if cpi_data and cpi_data['status'] == 'success':
        print("Fetched CPI data:")
        for item in cpi_data['data']:
            print(f"  Date: {item['date']}, CPI: {item['cpi']}")
    else:
        print(f"Error fetching CPI data: {cpi_data.get('message', 'Unknown error')}")
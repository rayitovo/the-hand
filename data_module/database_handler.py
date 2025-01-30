# data_module/database_handler.py
import sqlite3
from utils.logger import logger
import pandas as pd

class DatabaseHandler:
    def __init__(self, db_name="crypto_data.db"):
        self.db_name = db_name
        self.conn = None
        logger.info("DatabaseHandler initialized.")

    def connect(self):
        """Connects to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            logger.info(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")

    def disconnect(self):
        """Disconnects from the database."""
        if self.conn:
            self.conn.close()
            logger.info(f"Disconnected from database: {self.db_name}")

    def create_table(self, table_name, schema):
        """
        Creates a table in the database.
        Args:
            table_name (str): Name of the table.
            schema (str): SQL schema definition (e.g., "id INTEGER PRIMARY KEY, price REAL, timestamp TEXT").
        """
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            self.conn.commit()
            logger.info(f"Table created: {table_name}")
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")

    def insert_data(self, table_name, data):
        """
        Inserts data into a table.
        Args:
            table_name (str): Name of the table.
            data (list of tuples): List of tuples, where each tuple represents a row to be inserted.
                                   The order of values in the tuple should match the column order in the table.
        """
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            placeholders = ', '.join(['?'] * len(data[0]))  # Create placeholders for values based on data size
            cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
            self.conn.commit()
            logger.info(f"Data inserted into table: {table_name}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting data: {e}")

    def fetch_data(self, table_name, condition=None):
        """
        Fetches data from a table.
        Args:
            table_name (str): Name of the table.
            condition (str, optional): SQL WHERE clause condition (e.g., "symbol='BTC' AND price > 50000").
                                       If None, fetches all data.
        Returns:
            list: List of tuples, where each tuple represents a row.
        """
        if not self.conn:
            self.connect()
        try:
            cursor = self.conn.cursor()
            if condition:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {condition}")
            else:
                cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            logger.info(f"Data fetched from table: {table_name}")
            return data
        except sqlite3.Error as e:
            logger.error(f"Error fetching data: {e}")
            return None

    def fetch_data_as_dataframe(self, table_name, condition=None):
        """
        Fetches data from a table and returns it as a Pandas DataFrame.
        Args:
            table_name (str): Name of the table.
            condition (str, optional): SQL WHERE clause condition.
        Returns:
            pd.DataFrame: DataFrame containing the fetched data.
        """
        if not self.conn:
            self.connect()
        try:
            if condition:
                query = f"SELECT * FROM {table_name} WHERE {condition}"
            else:
                query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"Data fetched from table {table_name} as DataFrame")
            return df
        except sqlite3.Error as e:
            logger.error(f"Error fetching data as DataFrame: {e}")
            return None

if __name__ == '__main__':
    db_handler = DatabaseHandler()

    # Example schema
    klines_schema = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        open_time TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        close_time TEXT,
        quote_asset_volume REAL,
        number_of_trades INTEGER,
        taker_buy_base_asset_volume REAL,
        taker_buy_quote_asset_volume REAL
    """

    # Create table
    db_handler.create_table("klines", klines_schema)

    # Example data (replace with your actual fetched data)
    example_data = [
        ("BTCUSDT", "2023-06-20 00:00:00", 30000.0, 30500.0, 29800.0, 30200.0, 1000.0, "2023-06-20 23:59:59", 30200000.0, 100, 500.0, 15100000.0),
        ("BTCUSDT", "2023-06-21 00:00:00", 30200.0, 30700.0, 30100.0, 30600.0, 1200.0, "2023-06-21 23:59:59", 36720000.0, 120, 600.0, 18360000.0),
        ("ETHUSDT", "2023-06-20 00:00:00", 1800.0, 1830.0, 1790.0, 1820.0, 5000.0, "2023-06-20 23:59:59", 9100000.0, 50, 2500.0, 4550000.0),
        ("ETHUSDT", "2023-06-21 00:00:00", 1820.0, 1850.0, 1810.0, 1840.0, 6000.0, "2023-06-21 23:59:59", 11040000.0, 60, 3000.0, 5520000.0),
    ]

    # Insert data
    db_handler.insert_data("klines", example_data)

    # Fetch data
    fetched_data = db_handler.fetch_data("klines", condition="symbol='BTCUSDT'")
    print("Fetched Data (BTCUSDT):")
    for row in fetched_data:
        print(row)

    # Fetch data as DataFrame
    fetched_df = db_handler.fetch_data_as_dataframe("klines")
    print("\nFetched Data as DataFrame:")
    print(fetched_df)

    db_handler.disconnect()
### the-hand - flow
agent-based crypto trading platform in python.

#### **1. System Overview**
The system is designed as a modular, agent-based crypto trading platform with real-time execution, simulation, and backtesting capabilities. It dynamically adapts to market regimes (bull, bear, etc.) by selecting pre-approved strategies and coordinates execution through centralized agents. Below is the detailed pathway of data, logic, and module interactions.

---

#### **2. Module Breakdown**

##### **2.1 `main.py` (Entry Point)**
- **Responsibilities**:
  - Load environment variables with `dotenv` and Load configurations `from config import *`.
  - Instantiate the `Strategist` with parameters (real/simulation mode, asset pairs, risk tolerance).
  - `mode_selector.py`: Determines if the system runs in live trading, simulation, or backtesting mode based in the config, defaults to simulation.
- **Interactions**:
  - Passes control to the `Strategist` after initialization.
  - Invokes `backtester/run_backtest.py` if the user triggers backtesting.

---

##### **2.2 `strategist/` (Central Coordinator)**
- **Responsibilities**:
  - Continuously fetch market regime data from `regime_info/`.
  - Load approved strategies from `strategy/approved/<regime>/`.
  - Coordinate execution via `trader/` (real) or `simulation/` (simulated).
  - Monitor for regime shifts (e.g., bull → bear) and reload strategies.
- **Submodules**:
  - `strategy_loader.py`: Dynamically imports strategies from regime-specific directories.
  - `execution_coordinator.py`: Delegates trades to `trader` or `simulation`.
  - `regime_monitor.py`: Polls `regime_info` at intervals (e.g., hourly) for changes.
- **Interactions**:
  - **Input**: Market regime data from `regime_info/`, strategies from `strategy/approved/`.
  - **Output**: Trade signals to `trader/` or `simulation/`.

---

##### **2.3 `regime_info/` (Market State Analyzer)**
- **Responsibilities**:
  - Detect crypto-specific regimes using:
    - Price trends (SMA, RSI).
    - Volatility (Bollinger Bands, ATR).
    - Macroeconomic indicators (CPI, Fed rates for inflationary/deflationary regimes).
    - On-chain data (exchange reserves, whale movements).
  - Classify regimes into: `bull`, `bear`, `sideways`, `volatile`, `inflationary`, etc.
  - Provide historical regime data to the backtester for regime-aware backtesting.
- **Submodules**:
  - `technical_analyzer.py`: Computes technical indicators.
  - `macro_analyzer.py`: Fetches macroeconomic data (APIs, news sentiment).
  - `regime_classifier.py`: ML model (e.g., Random Forest) to classify regimes.
  - `historical_regime_provider.py`: Provides historical regime data for a given time range.
    - **Responsibilities**:
        - Fetch historical data from data_module/ for a specified time range.
        - Apply regime classification logic (using technical_analyzer.py, macro_analyzer.py, regime_classifier.py) to the historical data.
        - Return a time series of regime labels corresponding to the historical period.
    - **Interactions**:
      - **Input**: Time range (start date, end date).
      - **Input**: Access to `data_module/` to fetch historical data.
      - **Output**: Time series of regime labels.
- **Interactions**:
  - **Input**: Historical/real-time data from `data_module/`.
  - **Output**: Regime labels and confidence scores to `strategist/`.
  - **Output**: Historical regime data to `backtester/`.

---

##### **2.4 `data_module/` (Data Hub)**
- **Responsibilities**:
  - Fetch real-time/historical data from exchanges and APIs (for now, any free one).
  - Clean, normalize, and store data in databases (sql lite for now).
  - Serve other modules.
- **Submodules**:
  - `data_fetcher.py`: Handles API requests with retries and rate limits.
  - `data_cleaner.py`: Removes outliers, fills gaps.
  - `database_handler.py`: Manages storages.
- **Interactions**:
  - **Input**: User-defined pairs (e.g., BTC/USD), macroeconomic APIs.
  - **Output**: Data to `regime_info/`, `backtester/`, `strategist/`.

---

##### **2.5 `strategy/` (Strategy Repository)**
- **Structure**:
  ```
  strategy/
  ├── base_strategy.py         # Abstract class with methods like `generate_signal()`
  ├── approved/                # Production-ready strategies
  │   └── bull/                # Regime-specific strategies
  │       └── ema_crossover.py # Example strategy
  ├── to_test/                 # Strategies awaiting backtesting
  └── trash/                   # Rejected strategies
  ```
- **Submodules**:
  - `base_strategy.py`: Defines required methods (entry/exit logic, risk parameters).
  - `strategy_validator.py`: Ensures strategies comply with base class pre-deployment.
- **Interactions**:
  - `backtester/` moves strategies between `to_test/`, `approved/`, and `trash/`.

---

##### **2.6 `backtester/` (Strategy Validator)**
- **Responsibilities**:
  - Test strategies in `strategy/to_test/<regime>/` against historical data under corresponding historical market regimes.
  - Generate performance reports (Sharpe ratio, max drawdown, win rate).
  - Auto-move strategies to `approved/<regime>` or `trash/` based on thresholds.
- **Submodules**:
  - `backtest_engine.py`: Simulates trades with slippage and latency considering historical regime context.
  - `report_generator.py`: Creates PDF/JSON reports with metrics and equity curves.
  - `approval_manager.py`: Applies rules (e.g., "Sharpe ≥ 1.5") to approve strategies.
- **Interactions**:
  - **Input**: historical regime data from `regime_info/`, based in what `to_test/<regime>` folder the strategy is located. 
  - **Output**: Approved strategies to `strategy/approved/<regime>`, reports to `data/logs/`.

---

##### **2.7 `trader/` (Live Execution Agent)**
- **Responsibilities**:
  - Execute orders on exchanges via REST/WebSocket APIs.
  - Monitor positions and manage risk (stop-loss, take-profit).
- **Submodules**:
  - `order_executor.py`: Handles order types (market, limit, OCO).
  - `risk_manager.py`: Ensures trades comply with capital allocation rules.
  - `exchange_connector.py**: Exchange-specific API adapters.
- **Interactions**:
  - Uses `trading_core/` for shared logic (e.g., portfolio tracking).

---

##### **2.8 `simulation/` (Mock Trader)**
- **Responsibilities**:
  - Mimic live trading with virtual capital.
  - Simulate latency, partial fills, and slippage.
- **Submodules**:
  - `virtual_exchange.py`: Tracks simulated portfolio and order book.
  - `latency_engine.py`: Adds realistic delays to order execution.
- **Interactions**:
  - Shares `trading_core/` modules with `trader/`.

---

##### **2.9 `trading_core/` (Shared Logic)**
- **Submodules**:
  - `portfolio_manager.py`*: Trades, balances, PnL calculations.
  - `order_book.py`: Level 2 market data handling.
  - `event_logger.py`: Records trades to `data/logs/transactions.csv`.

---

##### **2.10 `utils/` (Cross-Cutting Tools)**
- **Submodules**:
  - `logger.py`: Structured logging (debug, info, error levels).
  - `date_utils.py`: Timezone-aware datetime conversions.
  - `error_handlers.py`: Retry decorators, exception logging.

---

#### **3. Pathway Diagram**
```plaintext
User
│
└── main.py # mode_selector is applied to decide the path between strategist and backtester.
    ├──  Strategist (real or simulation): Loads configs → strategist/
    │   ├── Queries regime_info/ → (Regime: Bull)
    │   ├── Loads strategies from strategy/approved/bull/
    │   └── Coordinates trader/ or simulation/
    │       ├── (Live) trader/ → Executes via exchange APIs
    │       └── (Sim) simulation/ → Virtual orders
    │
    └──  Invokes backtester/ 
        ├── Requests Historical Data from `regime_info/historical_regime_provider.py`
        ├── Tests strategies in strategy/to_test/<regime> under the historical regime data
        ├── Generates reports → data/logs/
        └── Moves strategies to approved/ or trash/
```

---

#### **4. Key Interactions**
1. **Regime Detection Loop**:
   - `strategist/regime_monitor.py` polls `regime_info` periodically.
   - On regime change, `strategist/` reloads strategies from the new regime folder.
2. **Strategy Approval Pipeline**:
   - User adds a new strategy to `strategy/to_test/<regime>/`.
   - `backtester/` runs it against historical `<regime>` markets.
   - If approved, moved to `strategy/approved/<regime>/` for live use.
3. **Data Flow**:
   - `data_module/` serves cleaned data to `regime_info/` (for regime detection) and `strategist/` (for strategy execution).




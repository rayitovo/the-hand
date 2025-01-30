### **Implementation Order**  
#### **Phase 1: Core Architecture & Workflow** (done)
1. **`main.py`**  
   - Set up environment/config loading.  
   - Implement `mode_selector.py` to choose between live/simulation/backtesting.  
   - Initialize `Strategist` with mock dependencies.  

2. **`strategist/` (Skeleton)**  
   - Create `strategy_loader.py` (stub for loading strategies).  
   - Build `execution_coordinator.py` (dummy trade delegation).  
   - Add `regime_monitor.py` (polling mechanism with placeholder regime data).  

3. **`utils/` (Foundational Tools)**  
   - Implement `logger.py` (critical for debugging).  

---

#### **Phase 2: Data & Market Analysis** (done)
4. **`data_module/` (Minimal Version)**  
   - Build `data_fetcher.py` (fetch live data from a single exchange).  
   - Add `data_cleaner.py` (basic normalization).  
   - Skip `database_handler.py` initially; use in-memory storage.  

5. **`regime_info/` (Basic Classification)**  
   - Implement `technical_analyzer.py` (SMA, RSI).  
   - Create `regime_classifier.py` (simple threshold-based rules, e.g., "bull = SMA50 > SMA200").  
   - Skip ML/macro analysis for now.  

---

#### **Phase 3: Strategy Execution** (done)
6. **`trading_core/`**  
   - Build `portfolio_manager.py` (track balances, PnL).  
   - Add `event_logger.py` (log trades to CSV).  

7. **`simulation/`**  
   - Create `virtual_exchange.py` (mock order execution).  
   - Skip latency/slippage initially.  

8. **`trader/` (Stub)**  
   - Implement `exchange_connector.py` (mock API calls).  

---

#### **Phase 4: Backtesting & Strategy Management** (done)
9. **`backtester/`**  
   - Build `backtest_engine.py` (replay historical data).  
   - Add `report_generator.py` (basic metrics like profit/loss).  

10. **`strategy/`**  
    - Define `base_strategy.py` (abstract class with required methods).  
    - Add one sample strategy in `approved/bull/ema_crossover.py`.  

---

#### **Phase 5: Refinement & Scaling**  
11. **Enhance `regime_info/`**  
    - Add `macro_analyzer.py` (fetch CPI data via API).  
    - Upgrade `regime_classifier.py` with ML models.  

12. **Expand `data_module/`**  
    - Implement `database_handler.py` (SQLite integration).  
    - Add support for multiple exchanges/APIs.  

13. **Optimize Execution**  
    - Add latency/slippage to `simulation/`.  
    - Implement risk management in `trader/risk_manager.py`.  
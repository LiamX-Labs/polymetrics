# 🎯 POLYMARKET BACKTEST SYSTEM - COMPLETE IMPLEMENTATION PLAN

**Project:** Private backtesting system for Polymarket prediction market strategies
**Primary Strategy:** Wallet 1 Scalper (15-min BTC momentum with 95%+ odds entry)
**Timeline:** 14 days
**Status:** Ready for implementation

---

## **📁 PROJECT STRUCTURE**

```
polymarket-backtest/                 # New private project folder
├── .git/                            # Private git repo (not pushed to public)
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Global settings, API keys
│   └── strategy_configs/
│       ├── wallet1_scalper.yaml     # Wallet 1 strategy params
│       └── wallet2_hft.yaml         # Future: Wallet 2 strategy
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                        # Data Layer
│   │   ├── __init__.py
│   │   ├── binance_fetcher.py       # Fetch Binance klines
│   │   ├── polymarket_fetcher.py    # Fetch Polymarket data
│   │   ├── data_aligner.py          # Align Binance + Polymarket
│   │   ├── data_cache.py            # Local caching with parquet
│   │   └── models.py                # Data models (Market, Candle, etc.)
│   │
│   ├── strategies/                  # Strategy Engine (Reusable)
│   │   ├── __init__.py
│   │   ├── base_strategy.py         # Abstract base class
│   │   ├── wallet1_strategy.py      # Wallet 1 implementation
│   │   └── signals/
│   │       ├── __init__.py
│   │       ├── entry_signals.py     # Entry logic
│   │       └── momentum_filters.py  # Optional momentum indicators
│   │
│   ├── backtest/                    # Backtesting Engine
│   │   ├── __init__.py
│   │   ├── engine.py                # Main backtest orchestrator
│   │   ├── market_simulator.py      # Market replay logic
│   │   ├── order_simulator.py       # Fill simulation with slippage
│   │   ├── position_manager.py      # Position tracking
│   │   └── portfolio.py             # Portfolio state management
│   │
│   ├── optimization/                # Parameter Optimization
│   │   ├── __init__.py
│   │   ├── grid_search.py           # Grid search optimizer
│   │   ├── walk_forward.py          # Walk-forward validation
│   │   └── validators.py            # In/out sample validators
│   │
│   ├── analytics/                   # Performance Analytics
│   │   ├── __init__.py
│   │   ├── metrics.py               # Calculate all metrics
│   │   ├── reports.py               # Generate reports
│   │   ├── visualizations.py        # Charts and plots
│   │   └── comparison.py            # Compare to Wallet 1 benchmark
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── timezone.py              # Timezone conversions (ET/UTC)
│       ├── logger.py                # Logging setup
│       └── validators.py            # Data validation
│
├── data/                            # Data Storage
│   ├── raw/
│   │   ├── binance/                 # Raw Binance klines
│   │   │   └── BTCUSDT_1m_2025-2026.parquet
│   │   └── polymarket/              # Raw Polymarket data
│   │       ├── markets.parquet
│   │       └── price_history/
│   │           └── {market_id}.parquet
│   │
│   ├── processed/
│   │   └── backtest_dataset.parquet # Aligned, ready for backtest
│   │
│   └── cache/                       # API response cache
│       └── {endpoint}_{params_hash}.json
│
├── notebooks/                       # Jupyter notebooks for analysis
│   ├── 01_data_exploration.ipynb
│   ├── 02_strategy_validation.ipynb
│   └── 03_results_analysis.ipynb
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_data_fetchers.py
│   ├── test_backtest_engine.py
│   └── test_strategy.py
│
├── scripts/                         # Executable scripts
│   ├── fetch_data.py                # Fetch historical data
│   ├── run_backtest.py              # Run backtest
│   ├── optimize_params.py           # Parameter optimization
│   └── generate_report.py           # Generate final report
│
└── results/                         # Backtest results
    ├── in_sample/
    │   ├── trades.csv
    │   ├── metrics.json
    │   └── equity_curve.png
    └── out_of_sample/
        ├── trades.csv
        ├── metrics.json
        └── equity_curve.png
```

---

## **🏗️ IMPLEMENTATION PHASES**

### **PHASE 1: Project Setup & Infrastructure (Day 1)**

#### **1.1 Repository Setup**
- Create new private folder: `polymarket-backtest/`
- Initialize git repo (do NOT push to public GitHub)
- Create `.gitignore`:
  ```
  # Python
  __pycache__/
  *.py[cod]
  .pytest_cache/

  # Data
  data/raw/
  data/processed/
  data/cache/
  *.parquet
  *.csv

  # Secrets
  config/secrets.yaml
  .env

  # Results
  results/

  # Notebooks
  .ipynb_checkpoints/
  ```

#### **1.2 Dependencies Setup**
Create `requirements.txt`:
```txt
# Data fetching
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=12.0.0  # For parquet

# API interaction
python-binance>=1.0.16
websocket-client>=1.6.0

# Timezone handling
pytz>=2023.3

# Analysis
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0

# Optimization
scipy>=1.10.0
scikit-learn>=1.3.0

# Configuration
pyyaml>=6.0
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Notebooks
jupyter>=1.0.0
ipywidgets>=8.0.0
```

#### **1.3 Configuration Structure**
Create `config/settings.py`:
```python
from pathlib import Path
import yaml
from dotenv import load_dotenv
import os

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
RESULTS_DIR = PROJECT_ROOT / "results"

# API endpoints
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_DATA_URL = "https://data-api.binance.vision"
POLYMARKET_GAMMA_URL = "https://gamma-api.polymarket.com"
POLYMARKET_CLOB_URL = "https://clob.polymarket.com"
POLYMARKET_DATA_URL = "https://data-api.polymarket.com"

# API keys (optional for historical data)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Rate limiting
BINANCE_RATE_LIMIT_WEIGHT = 6000  # per minute
POLYMARKET_RATE_LIMIT = 2  # requests per second (conservative)

# Backtest settings
BACKTEST_START_DATE = "2025-01-01"
BACKTEST_END_DATE = "2026-05-11"
IN_SAMPLE_SPLIT = 0.6  # 60% in-sample, 40% out-of-sample
```

Create `config/strategy_configs/wallet1_scalper.yaml`:
```yaml
name: "Wallet 1 Scalper Strategy"
description: "15-min Bitcoin momentum scalping with 95%+ odds entry"

market_selection:
  asset: "BTC"
  market_type: "Up or Down"
  duration_minutes: 15

entry_criteria:
  timing:
    min_minutes_before_expiry: 4.0
    max_minutes_before_expiry: 7.0
    optimal_minutes_before_expiry: 4.7

  price:
    min_odds: 0.93
    max_odds: 0.97
    target_avg_odds: 0.9505

  # Optional momentum filters (disabled by default)
  momentum:
    enabled: false
    min_directional_strength: 0.7

position_sizing:
  type: "fixed"  # or "kelly", "dynamic"
  fixed_size_usd: 500.0
  max_position_size: 2000.0
  min_position_size: 100.0

exit_strategy:
  type: "hold_to_expiry"
  early_exit_enabled: false

risk_management:
  max_positions_per_hour: 4
  max_daily_positions: 50
  max_concurrent_positions: 5
  max_daily_loss: 5000.0

execution:
  slippage:
    model: "conservative"  # or "optimistic", "realistic"
    conservative_bps: 50   # 0.5%
    realistic_bps: 20      # 0.2%
    optimistic_bps: 10     # 0.1%

  fees:
    taker_fee_rate: 0.002  # 0.2%
    maker_fee_rate: 0.000  # 0% (we're always taker)

  latency:
    execution_delay_seconds: 1.0
    use_delayed_price: true

validation:
  benchmark_wallet: "0x9665139463d3fde30f13a87a2f180bf9e7f3e9b4"
  expected_win_rate_min: 0.95
  expected_avg_roi_min: 0.04
  expected_sharpe_min: 2.0
```

---

### **PHASE 2: Data Layer Implementation (Days 2-3)**

#### **2.1 Binance Data Fetcher**
Create `src/data/binance_fetcher.py`:

**Key Features:**
- Fetch 1-minute BTCUSDT klines
- Handle pagination for large date ranges
- Respect rate limits (2 weight per request)
- Cache responses locally
- Convert timestamps to datetime with timezone support

**Methods:**
```python
class BinanceFetcher:
    def fetch_klines(symbol, interval, start_date, end_date)
    def fetch_klines_batch(symbol, interval, start_ts, limit=1000)
    def save_to_parquet(data, filepath)
    def load_from_cache(cache_key)
```

#### **2.2 Polymarket Data Fetcher**
Create `src/data/polymarket_fetcher.py`:

**Key Features:**
- Fetch markets from Gamma API with filters
- Fetch price history from CLOB API per market
- Handle pagination (offset-based)
- Rate limiting (1-2 req/sec)
- Cache market metadata and price history separately

**Methods:**
```python
class PolymarketFetcher:
    def fetch_markets(start_date, end_date, filters)
    def fetch_price_history(token_id, start_ts, end_ts, interval="1m")
    def filter_btc_15min_markets(markets)
    def save_markets(markets, filepath)
    def save_price_history(market_id, prices, filepath)
```

#### **2.3 Data Models**
Create `src/data/models.py`:

**Define data structures:**
```python
@dataclass
class BinanceCandle:
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_volume: float
    trades: int

@dataclass
class PolymarketPrice:
    timestamp: datetime
    price: float

@dataclass
class Market:
    id: str
    condition_id: str
    question: str
    start_time: datetime
    end_time: datetime
    outcomes: List[str]
    token_ids: List[str]
    closed: bool
    resolution: Optional[str]

@dataclass
class AlignedMarketData:
    market: Market
    up_prices: List[PolymarketPrice]
    down_prices: List[PolymarketPrice]
    binance_candles: List[BinanceCandle]
    actual_outcome: str  # "Up" or "Down"
```

#### **2.4 Data Aligner**
Create `src/data/data_aligner.py`:

**Key Features:**
- Match Polymarket markets to Binance candle windows
- Handle timezone conversion (ET → UTC)
- Determine actual outcome from BTC price movement
- Validate data quality (no missing minutes)
- Create unified dataset for backtesting

**Methods:**
```python
class DataAligner:
    def align_market_data(market, pm_prices, btc_candles)
    def convert_et_to_utc(et_datetime)
    def determine_outcome(binance_candles)
    def validate_completeness(market_data)
    def create_backtest_dataset(markets, save_path)
```

---

### **PHASE 3: Strategy Engine (Days 4-5)**

#### **3.1 Base Strategy Class**
Create `src/strategies/base_strategy.py`:

**Abstract interface for all strategies:**
```python
class BaseStrategy(ABC):
    @abstractmethod
    def should_enter(market_state, time_remaining) -> bool:
        pass

    @abstractmethod
    def get_position_size(market_state) -> float:
        pass

    @abstractmethod
    def should_exit(position, market_state) -> bool:
        pass

    def load_config(config_path):
        pass
```

#### **3.2 Wallet 1 Strategy Implementation**
Create `src/strategies/wallet1_strategy.py`:

**Implement specific logic:**
```python
class Wallet1Strategy(BaseStrategy):
    def should_enter(self, market_state, time_remaining):
        """
        Entry conditions:
        1. Time remaining: 4-7 minutes
        2. Price: 0.93-0.97
        3. Optional: momentum confirmation
        """
        # Check timing window
        if not (4.0 <= time_remaining <= 7.0):
            return False

        # Check price range
        current_price = market_state.current_price
        if not (0.93 <= current_price <= 0.97):
            return False

        # Optional momentum filter
        if self.config.momentum.enabled:
            if not self.check_momentum(market_state):
                return False

        return True

    def get_position_size(self, market_state):
        """Fixed $500 per trade"""
        return self.config.position_sizing.fixed_size_usd

    def should_exit(self, position, market_state):
        """Hold to expiry - never early exit"""
        return market_state.is_expired
```

#### **3.3 Signal Generators**
Create `src/strategies/signals/entry_signals.py`:

**Reusable signal components:**
```python
class TimingSignal:
    def check(time_remaining, min_time, max_time) -> bool

class PriceSignal:
    def check(current_price, min_price, max_price) -> bool

class MomentumSignal:
    def check(binance_candles, threshold) -> bool
    def calculate_directional_strength(candles) -> float
```

---

### **PHASE 4: Backtest Engine (Days 6-8)**

#### **4.1 Market Simulator**
Create `src/backtest/market_simulator.py`:

**Replay market minute-by-minute:**
```python
class MarketSimulator:
    def __init__(self, aligned_data, strategy):
        self.data = aligned_data
        self.strategy = strategy
        self.current_minute = 0

    def step(self):
        """Advance simulation by 1 minute"""
        current_time = self.get_current_time()
        time_remaining = self.get_time_remaining()

        # Get current state (NO future peeking!)
        market_state = self.get_market_state_at(current_time)

        # Check strategy signals
        if self.strategy.should_enter(market_state, time_remaining):
            return "ENTER", market_state

        self.current_minute += 1
        return "WAIT", None

    def get_market_state_at(self, timestamp):
        """Get all data available at specific timestamp"""
        # ONLY return data from before timestamp
        return MarketState(
            current_price=self.get_price_at(timestamp),
            binance_candles=self.get_candles_before(timestamp),
            time_remaining=self.calculate_time_remaining(timestamp)
        )
```

#### **4.2 Order Simulator**
Create `src/backtest/order_simulator.py`:

**Simulate realistic fills:**
```python
class OrderSimulator:
    def __init__(self, slippage_model, fee_config):
        self.slippage_model = slippage_model
        self.fees = fee_config

    def simulate_fill(self, signal_price, signal_time, size):
        """
        Apply slippage, latency, and fees
        """
        # 1. Get delayed price (execution latency)
        delayed_time = signal_time + timedelta(seconds=self.latency)
        actual_price = self.get_price_at(delayed_time)

        # 2. Apply slippage
        slippage = self.calculate_slippage(size, actual_price)
        fill_price = actual_price + slippage

        # 3. Apply tick size rounding
        fill_price = self.round_to_tick(fill_price, tick_size=0.01)

        # 4. Calculate fees
        fees = size * fill_price * self.fees.taker_rate

        return FillResult(
            fill_price=fill_price,
            fill_time=delayed_time,
            fees=fees,
            slippage=slippage,
            total_cost=size * fill_price + fees
        )
```

#### **4.3 Position Manager**
Create `src/backtest/position_manager.py`:

**Track open and closed positions:**
```python
class PositionManager:
    def open_position(self, market, outcome, entry_price, size, entry_time)
    def close_position(self, position_id, exit_price, exit_time)
    def get_open_positions(self)
    def get_closed_positions(self)
    def calculate_pnl(self, position, final_outcome)
```

#### **4.4 Main Backtest Engine**
Create `src/backtest/engine.py`:

**Orchestrate entire backtest:**
```python
class BacktestEngine:
    def __init__(self, dataset, strategy, config):
        self.dataset = dataset
        self.strategy = strategy
        self.config = config
        self.portfolio = Portfolio(initial_capital=10000)

    def run(self):
        """
        Run backtest across all markets
        """
        results = []

        for market_data in self.dataset:
            # Simulate this market
            simulator = MarketSimulator(market_data, self.strategy)

            position = None

            # Minute-by-minute simulation
            for minute in range(15):  # 15-min market
                action, state = simulator.step()

                if action == "ENTER" and position is None:
                    # Execute entry
                    fill = self.order_simulator.simulate_fill(
                        state.current_price,
                        state.current_time,
                        self.strategy.get_position_size(state)
                    )

                    position = self.position_manager.open_position(
                        market=market_data.market,
                        outcome=state.predicted_outcome,
                        entry_price=fill.fill_price,
                        size=fill.total_cost,
                        entry_time=fill.fill_time
                    )

            # Market expired - settle position
            if position:
                final_outcome = market_data.actual_outcome
                pnl = self.position_manager.calculate_pnl(
                    position, final_outcome
                )

                results.append({
                    "market_id": market_data.market.id,
                    "entry_time": position.entry_time,
                    "entry_price": position.entry_price,
                    "exit_price": 1.0 if position.outcome == final_outcome else 0.0,
                    "size": position.size,
                    "pnl": pnl,
                    "outcome": final_outcome,
                    "prediction": position.outcome,
                    "correct": position.outcome == final_outcome
                })

        return BacktestResults(results)
```

---

### **PHASE 5: In-Sample / Out-of-Sample Split (Day 9)**

#### **5.1 Data Splitter**
Create `src/optimization/validators.py`:

**Split dataset chronologically:**
```python
class DataSplitter:
    def temporal_split(self, dataset, in_sample_ratio=0.6):
        """
        Split data chronologically into in-sample and out-of-sample
        """
        # Sort by date
        sorted_data = sorted(dataset, key=lambda x: x.market.start_time)

        # Calculate split point
        split_idx = int(len(sorted_data) * in_sample_ratio)

        in_sample = sorted_data[:split_idx]
        out_of_sample = sorted_data[split_idx:]

        return {
            "in_sample": in_sample,
            "out_of_sample": out_of_sample,
            "split_date": sorted_data[split_idx].market.start_time
        }

    def walk_forward_splits(self, dataset, train_months=2, test_months=1):
        """
        Create walk-forward validation splits
        """
        splits = []
        # Implementation for rolling window splits
        return splits
```

#### **5.2 Parameter Optimizer**
Create `src/optimization/grid_search.py`:

**Grid search over parameter space:**
```python
class GridSearchOptimizer:
    def __init__(self, param_grid, objective="sharpe"):
        self.param_grid = param_grid
        self.objective = objective

    def optimize(self, in_sample_data):
        """
        Find best parameters on in-sample data
        """
        results = []

        for params in self.generate_param_combinations():
            # Run backtest with these params
            strategy = Wallet1Strategy(params)
            engine = BacktestEngine(in_sample_data, strategy)
            backtest_results = engine.run()

            # Calculate objective
            metric_value = self.calculate_objective(backtest_results)

            results.append({
                "params": params,
                "metric": metric_value,
                "backtest_results": backtest_results
            })

        # Return best params
        best = max(results, key=lambda x: x["metric"])
        return best
```

---

### **PHASE 6: Analytics & Reporting (Day 10)**

#### **6.1 Performance Metrics**
Create `src/analytics/metrics.py`:

**Calculate all performance metrics:**
```python
class PerformanceMetrics:
    def calculate_all(self, backtest_results):
        return {
            # Returns
            "total_pnl": self.total_pnl(results),
            "total_return_pct": self.total_return(results),
            "avg_trade_pnl": self.avg_trade_pnl(results),
            "avg_roi_per_trade": self.avg_roi(results),

            # Risk-adjusted
            "sharpe_ratio": self.sharpe_ratio(results),
            "sortino_ratio": self.sortino_ratio(results),
            "max_drawdown": self.max_drawdown(results),
            "calmar_ratio": self.calmar_ratio(results),

            # Win rate
            "win_rate": self.win_rate(results),
            "profit_factor": self.profit_factor(results),
            "avg_win": self.avg_win(results),
            "avg_loss": self.avg_loss(results),

            # Volume
            "total_trades": len(results),
            "trades_per_day": self.trades_per_day(results),
        }
```

#### **6.2 Comparison to Wallet 1**
Create `src/analytics/comparison.py`:

**Compare backtest to real trader:**
```python
class BenchmarkComparison:
    WALLET1_BENCHMARK = {
        "total_trades": 1881,
        "win_rate": 0.997,
        "avg_roi": 0.0575,
        "total_pnl": 50583.53,
        "profit_factor": 21.21,
        "avg_entry_price": 0.9505
    }

    def compare(self, backtest_results):
        """
        Compare backtest to Wallet 1 benchmark
        """
        backtest_metrics = PerformanceMetrics().calculate_all(backtest_results)

        comparison = {}
        for metric, benchmark_value in self.WALLET1_BENCHMARK.items():
            backtest_value = backtest_metrics.get(metric)
            diff_pct = (backtest_value - benchmark_value) / benchmark_value * 100

            comparison[metric] = {
                "backtest": backtest_value,
                "wallet1": benchmark_value,
                "diff_pct": diff_pct,
                "match": abs(diff_pct) < 20  # Within 20%
            }

        return comparison
```

#### **6.3 Visualization**
Create `src/analytics/visualizations.py`:

**Generate charts:**
```python
class BacktestVisualizer:
    def plot_equity_curve(results)
    def plot_drawdown(results)
    def plot_returns_distribution(results)
    def plot_entry_price_distribution(results)
    def plot_win_rate_over_time(results)
    def plot_monthly_returns(results)
```

#### **6.4 Report Generator**
Create `src/analytics/reports.py`:

**Generate comprehensive HTML report:**
```python
class ReportGenerator:
    def generate_html_report(in_sample_results, out_of_sample_results):
        """
        Create comprehensive report with:
        - Executive summary
        - Metrics comparison table
        - Charts (equity, drawdown, distributions)
        - Trade log
        - Validation against Wallet 1
        - Go/No-Go recommendation
        """
        pass
```

---

### **PHASE 7: Executable Scripts (Day 11)**

#### **7.1 Data Fetching Script**
Create `scripts/fetch_data.py`:
```python
"""
Fetch all historical data and create backtest dataset

Usage:
    python scripts/fetch_data.py --start 2025-01-01 --end 2026-05-11
"""
```

#### **7.2 Backtest Runner**
Create `scripts/run_backtest.py`:
```python
"""
Run backtest with specified strategy

Usage:
    python scripts/run_backtest.py \
        --strategy wallet1_scalper \
        --split in_sample \
        --output results/in_sample/
"""
```

#### **7.3 Optimization Script**
Create `scripts/optimize_params.py`:
```python
"""
Run parameter optimization on in-sample data

Usage:
    python scripts/optimize_params.py \
        --strategy wallet1_scalper \
        --output results/optimization/
"""
```

#### **7.4 Report Generation**
Create `scripts/generate_report.py`:
```python
"""
Generate final backtest report

Usage:
    python scripts/generate_report.py \
        --in-sample results/in_sample/ \
        --out-of-sample results/out_of_sample/ \
        --output reports/final_report.html
"""
```

---

## **🎯 EXECUTION TIMELINE**

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | Day 1 | Project structure, configs, dependencies |
| **Phase 2** | Days 2-3 | Data fetchers, models, aligner |
| **Phase 3** | Days 4-5 | Strategy engine, base classes |
| **Phase 4** | Days 6-8 | Backtest engine, simulators |
| **Phase 5** | Day 9 | In/out-of-sample split, optimization |
| **Phase 6** | Day 10 | Analytics, metrics, reports |
| **Phase 7** | Day 11 | Scripts, integration, testing |
| **Phase 8** | Day 12 | Data fetching (execute scripts) |
| **Phase 9** | Day 13 | Run backtest, generate results |
| **Phase 10** | Day 14 | Analysis, validation, final report |

**Total Estimated Time: 14 days**

---

## **🔒 PRIVACY & SECURITY**

### **Repository Management**
- ✅ Create in local folder (NOT in public repos)
- ✅ If using git, create private repo on GitHub
- ✅ Add to `.gitignore`: data files, API keys, results
- ✅ Use `.env` for sensitive configs
- ✅ Never commit API keys or credentials

### **API Key Management**
Create `.env`:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
# Polymarket doesn't need keys for historical data
```

---

## **♻️ REUSABILITY FOR FUTURE STRATEGIES**

### **Design Principles**

**1. Strategy Interface:**
- All strategies inherit from `BaseStrategy`
- Implement 3 methods: `should_enter()`, `get_position_size()`, `should_exit()`
- Load config from YAML

**2. Pluggable Components:**
- Swap strategies without changing engine
- Swap data sources (future: add Ethereum markets)
- Swap optimization methods (grid search, Bayesian, genetic)

**3. Configuration-Driven:**
- All strategy params in YAML
- No hardcoded values
- Easy to version control different configs

### **Adding Wallet 2 Strategy (Future):**

**Step 1:** Create `config/strategy_configs/wallet2_hft.yaml`
```yaml
name: "Wallet 2 HFT Sniper"
market_selection:
  asset: ["BTC", "ETH"]
  duration_minutes: 5
entry_criteria:
  timing:
    min_minutes_before_expiry: 0.5
    max_minutes_before_expiry: 1.0
  price:
    min_odds: 0.98
    max_odds: 0.99
```

**Step 2:** Create `src/strategies/wallet2_strategy.py`
```python
class Wallet2Strategy(BaseStrategy):
    # Implement HFT logic
    pass
```

**Step 3:** Run backtest:
```bash
python scripts/run_backtest.py --strategy wallet2_hft
```

**That's it!** No engine changes needed.

---

## **📊 API CAPABILITIES SUMMARY**

### **Binance API**
- ✅ Endpoint: `GET /api/v3/klines`
- ✅ No authentication required for historical data
- ✅ Rate limit: 6,000 weight/min (klines = 2 weight)
- ✅ Max 1,000 candles per request
- ✅ Intervals: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
- ✅ Timezone support for candle boundaries
- ✅ Unlimited historical depth

### **Polymarket API**

**Gamma API (Market Discovery):**
- ✅ Endpoint: `GET https://gamma-api.polymarket.com/markets`
- ✅ No authentication required
- ✅ Filter by: date range, asset, market type, status
- ✅ Pagination: offset-based, 100 per page
- ✅ Returns: market metadata, token IDs, start/end times, outcomes

**CLOB API (Price History):**
- ✅ Endpoint: `GET https://clob.polymarket.com/prices-history`
- ✅ No authentication required
- ✅ Minute-by-minute price data available!
- ✅ Intervals: 1m, 1h, 6h, 1d, 1w, all, max
- ✅ Fidelity: 1-minute accuracy
- ✅ Returns: timestamp + price pairs

**CLOB API (Orderbook):**
- ✅ Endpoint: `GET https://clob.polymarket.com/book`
- ✅ Current orderbook snapshot
- ✅ Returns: bids, asks, last trade price, tick size

---

## **✅ SUCCESS CRITERIA**

The backtest system is successful if:

**Technical:**
- ✅ Fetches all data without errors
- ✅ Aligns Binance + Polymarket data correctly
- ✅ Prevents look-ahead bias (verified via code review)
- ✅ Runs backtest in < 1 minute for 1 year of data
- ✅ Generates comprehensive reports

**Performance:**
- ✅ In-sample win rate ≥ 95%
- ✅ Out-of-sample win rate ≥ 90%
- ✅ Out-of-sample performance ≥ 80% of in-sample
- ✅ Matches Wallet 1 within 20% on key metrics

**Validation:**
- ✅ Win rate close to 99.7%
- ✅ Avg ROI close to 5.75%
- ✅ Entry prices avg ~0.95
- ✅ No systematic bugs found

---

## **📊 DELIVERABLES**

At the end of implementation:

1. **Codebase:**
   - Complete backtest system
   - 80%+ test coverage
   - Documentation for each module

2. **Data:**
   - 1+ year of aligned Binance + Polymarket data
   - Cached for fast re-runs

3. **Results:**
   - In-sample backtest results
   - Out-of-sample backtest results
   - Comprehensive HTML report

4. **Analysis:**
   - Comparison to Wallet 1 benchmark
   - Sensitivity analysis (slippage, fees)
   - Walk-forward validation results

5. **Recommendation:**
   - Go/No-Go decision for live trading
   - Optimal parameters
   - Risk assessment

---

## **🚀 IMPLEMENTATION STRATEGY**

### **Start with Phase 1:**
1. Create private project folder outside public repos
2. Set up project structure
3. Install dependencies
4. Create configuration files
5. Initialize git (local only, no remote push)

### **Core Development Flow:**
1. Implement data layer first (can test immediately with API calls)
2. Build strategy engine (isolated, testable)
3. Implement backtest engine (brings it all together)
4. Add optimization and analytics
5. Create executable scripts
6. Run full backtest pipeline

### **Quality Assurance:**
- Write unit tests for each component
- Validate data alignment manually
- Review code for look-ahead bias
- Test with small dataset first
- Compare results to Wallet 1 continuously

---

## **📝 NOTES & CONSIDERATIONS**

### **Data Quality:**
- Polymarket's `/prices-history` endpoint is the key to realistic backtesting
- We have minute-by-minute data availability
- No need for price interpolation or assumptions
- Can validate fills against actual historical orderbook states

### **Look-Ahead Bias Prevention:**
- Strict temporal ordering in simulator
- Only use data available "at the moment"
- Don't peek at final outcomes during entry decision
- Use delayed prices for execution simulation

### **Overfitting Prevention:**
- Use Wallet 1's actual parameters as baseline
- Minimal parameter optimization (2-3 variations max)
- Require out-of-sample ≥ 80% of in-sample
- Benchmark against real-world results

### **Reusability:**
- Abstract base strategy class
- Configuration-driven architecture
- Pluggable components
- Easy to add new strategies without changing engine

---

**This plan is comprehensive, realistic, and achievable in 14 days.**
**Ready to begin implementation!** 🚀

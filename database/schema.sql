-- Polymetrics Database Schema

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT UNIQUE NOT NULL,
    first_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_positions INTEGER DEFAULT 0,
    total_pnl REAL DEFAULT 0.0,
    win_rate REAL DEFAULT 0.0,
    profit_factor REAL DEFAULT 0.0,
    risk_reward_ratio REAL DEFAULT 0.0,
    trading_style TEXT DEFAULT 'unknown',  -- hft, active, normal, unknown
    is_active BOOLEAN DEFAULT 1,

    -- Additional metrics
    total_wins REAL DEFAULT 0.0,
    total_losses REAL DEFAULT 0.0,
    avg_win REAL DEFAULT 0.0,
    avg_loss REAL DEFAULT 0.0,
    best_trade REAL DEFAULT 0.0,
    worst_trade REAL DEFAULT 0.0,
    avg_position_size REAL DEFAULT 0.0,
    total_volume REAL DEFAULT 0.0,

    CONSTRAINT valid_address CHECK (length(address) >= 10)
);

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    condition_id TEXT NOT NULL,
    market_title TEXT NOT NULL,
    outcome TEXT NOT NULL,
    side TEXT NOT NULL,  -- Yes/No

    -- Position details
    avg_entry_price REAL NOT NULL,
    exit_price REAL,
    position_size REAL NOT NULL,
    realized_pnl REAL NOT NULL,
    roi REAL,

    -- Trading info
    num_trades INTEGER DEFAULT 1,
    open_timestamp TIMESTAMP,
    close_timestamp TIMESTAMP,

    -- Market info
    event_slug TEXT,
    end_date TIMESTAMP,

    FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE,
    CONSTRAINT valid_pnl CHECK (realized_pnl IS NOT NULL)
);

-- Markets table
CREATE TABLE IF NOT EXISTS markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    event_slug TEXT,
    end_date TIMESTAMP,
    category TEXT,

    -- Aggregated stats
    total_traders INTEGER DEFAULT 0,
    total_volume REAL DEFAULT 0.0,
    avg_pnl REAL DEFAULT 0.0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wallet snapshots for historical tracking
CREATE TABLE IF NOT EXISTS wallet_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    total_positions INTEGER,
    total_pnl REAL,
    win_rate REAL,
    profit_factor REAL,

    FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
);

-- Leaderboard cache
CREATE TABLE IF NOT EXISTS leaderboard_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,  -- total_pnl, win_rate, profit_factor, etc.
    wallet_address TEXT NOT NULL,
    metric_value REAL NOT NULL,
    rank INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_metric_wallet UNIQUE (metric_name, wallet_address)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(address);
CREATE INDEX IF NOT EXISTS idx_wallets_total_pnl ON wallets(total_pnl DESC);
CREATE INDEX IF NOT EXISTS idx_wallets_win_rate ON wallets(win_rate DESC);
CREATE INDEX IF NOT EXISTS idx_wallets_profit_factor ON wallets(profit_factor DESC);
CREATE INDEX IF NOT EXISTS idx_wallets_last_analyzed ON wallets(last_analyzed DESC);

CREATE INDEX IF NOT EXISTS idx_positions_wallet_id ON positions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_positions_condition_id ON positions(condition_id);
CREATE INDEX IF NOT EXISTS idx_positions_close_timestamp ON positions(close_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_positions_realized_pnl ON positions(realized_pnl DESC);

CREATE INDEX IF NOT EXISTS idx_markets_condition_id ON markets(condition_id);
CREATE INDEX IF NOT EXISTS idx_markets_end_date ON markets(end_date);

CREATE INDEX IF NOT EXISTS idx_leaderboard_metric ON leaderboard_cache(metric_name, rank);

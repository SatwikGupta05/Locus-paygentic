-- Full decision audit trail with queryable columns
CREATE TABLE IF NOT EXISTS audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    cycle_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    -- Signal components
    sentiment_score REAL,
    technical_score REAL,
    ml_prob_up REAL,
    ml_prob_down REAL,
    -- Decision
    composite_score REAL,
    action TEXT,
    confidence REAL,
    -- Risk
    risk_approved INTEGER,
    risk_reason TEXT,
    position_size REAL,
    volatility_regime TEXT,
    -- Intent
    intent_hash TEXT,
    tx_hash TEXT,
    signature TEXT,
    -- Execution
    order_id TEXT,
    order_status TEXT,
    fill_price REAL,
    fill_size REAL,
    realized_pnl REAL,
    -- Pipeline stage
    pipeline_stage TEXT,
    -- Features snapshot (JSON blob)
    features_json TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE INDEX IF NOT EXISTS idx_audit_trail_timestamp ON audit_trail(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_trail_run_id ON audit_trail(run_id);

-- Order lifecycle state tracking
CREATE TABLE IF NOT EXISTS order_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    state TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT
);
CREATE INDEX IF NOT EXISTS idx_order_states_order_id ON order_states(order_id);

-- Agent reputation metrics (time series)
CREATE TABLE IF NOT EXISTS reputation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    timestamp TEXT NOT NULL,
    win_rate REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    total_trades INTEGER,
    avg_confidence REAL,
    profit_factor REAL,
    validation_score REAL,
    payload TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE INDEX IF NOT EXISTS idx_reputation_timestamp ON reputation(timestamp);

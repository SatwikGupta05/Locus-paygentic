CREATE TABLE IF NOT EXISTS explainability_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    decision_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    symbol TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    feature_importance_json TEXT NOT NULL,
    decision_trace TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id),
    FOREIGN KEY(decision_id) REFERENCES decisions(id)
);
CREATE INDEX IF NOT EXISTS idx_explainability_timestamp ON explainability_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_explainability_decision_id ON explainability_logs(decision_id);

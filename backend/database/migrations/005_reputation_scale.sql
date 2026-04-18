ALTER TABLE reputation ADD COLUMN reputation_raw REAL DEFAULT 0.0;
ALTER TABLE reputation ADD COLUMN reputation_norm REAL DEFAULT 0.0;

UPDATE reputation SET 
    reputation_raw = validation_score,
    reputation_norm = validation_score / 100.0;

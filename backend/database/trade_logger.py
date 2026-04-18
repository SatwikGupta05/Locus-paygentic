from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from backend.database.db_manager import DBManager


class TradeLogger:
    def __init__(self, db: DBManager) -> None:
        self.db = db
        self._cycle_id = 0

    def create_run(self, mode: str, symbol: str) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        return self.db.insert_returning_id(
            """
            INSERT INTO runs(started_at, mode, symbol, status)
            VALUES(?, ?, ?, ?)
            """,
            (timestamp, mode, symbol, "running"),
        )

    def close_run(self, run_id: int, status: str) -> None:
        self.db.execute(
            "UPDATE runs SET status = ?, finished_at = ? WHERE id = ?",
            (status, datetime.now(timezone.utc).isoformat(), run_id),
        )

    def log_market_data(self, run_id: int, symbol: str, source: str, candles: list[dict[str, Any]]) -> None:
        rows = [
            (
                run_id,
                symbol,
                candle["timestamp"],
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["volume"],
                source,
            )
            for candle in candles
        ]
        self.db.executemany(
            """
            INSERT INTO market_data(
                run_id, symbol, timestamp, open, high, low, close, volume, source
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    def log_features(self, run_id: int, symbol: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO features(run_id, symbol, timestamp, payload)
            VALUES(?, ?, ?, ?)
            """,
            (run_id, symbol, datetime.now(timezone.utc).isoformat(), json.dumps(payload, default=str)),
        )

    def log_decision(self, run_id: int, symbol: str, payload: dict[str, Any]) -> int:
        return self.db.insert_returning_id(
            """
            INSERT INTO decisions(run_id, symbol, timestamp, payload)
            VALUES(?, ?, ?, ?)
            """,
            (run_id, symbol, datetime.now(timezone.utc).isoformat(), json.dumps(payload, default=str)),
        )

    def log_intent(self, run_id: int, decision_id: int, intent_hash: str, payload: dict[str, Any], status: str) -> None:
        self.db.execute(
            """
            INSERT INTO intents(run_id, decision_id, intent_hash, timestamp, status, payload)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                decision_id,
                intent_hash,
                datetime.now(timezone.utc).isoformat(),
                status,
                json.dumps(payload, default=str),
            ),
        )

    def log_order(self, run_id: int, symbol: str, side: str, status: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO orders(run_id, symbol, side, status, timestamp, payload)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (run_id, symbol, side, status, datetime.now(timezone.utc).isoformat(), json.dumps(payload, default=str)),
        )

    def log_trade(self, run_id: int, symbol: str, side: str, amount: float, price: float, confidence: float, pnl: float) -> None:
        self.db.execute(
            """
            INSERT INTO trades(run_id, timestamp, symbol, side, amount, price, confidence, realized_pnl)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                datetime.now(timezone.utc).isoformat(),
                symbol,
                side,
                amount,
                price,
                confidence,
                pnl,
            ),
        )

    def log_order_state(self, order_id: str, state: str, metadata: dict[str, Any] | None = None) -> None:
        """Record an order lifecycle state transition."""
        self.db.execute(
            """
            INSERT INTO order_states(order_id, state, timestamp, metadata)
            VALUES(?, ?, ?, ?)
            """,
            (order_id, state, datetime.now(timezone.utc).isoformat(), json.dumps(metadata or {}, default=str)),
        )

    def log_audit_trail(
        self,
        run_id: int,
        symbol: str,
        *,
        sentiment_score: float | None = None,
        technical_score: float | None = None,
        ml_prob_up: float | None = None,
        ml_prob_down: float | None = None,
        composite_score: float | None = None,
        action: str | None = None,
        confidence: float | None = None,
        risk_approved: bool | None = None,
        risk_reason: str | None = None,
        position_size: float | None = None,
        volatility_regime: str | None = None,
        intent_hash: str | None = None,
        tx_hash: str | None = None,
        signature: str | None = None,
        order_id: str | None = None,
        order_status: str | None = None,
        fill_price: float | None = None,
        fill_size: float | None = None,
        realized_pnl: float | None = None,
        latency_ms: float | None = None,
        execution_source: str | None = None,
        pipeline_stage: str | None = None,
        features_json: str | None = None,
    ) -> int:
        """Store a full audit trail row with queryable columns for every decision component."""
        self._cycle_id += 1
        return self.db.insert_returning_id(
            """
            INSERT INTO audit_trail(
                run_id, cycle_id, timestamp, symbol,
                sentiment_score, technical_score, ml_prob_up, ml_prob_down,
                composite_score, action, confidence,
                risk_approved, risk_reason, position_size, volatility_regime,
                intent_hash, tx_hash, signature,
                order_id, order_status, fill_price, fill_size, realized_pnl,
                latency_ms, execution_source, pipeline_stage, features_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                self._cycle_id,
                datetime.now(timezone.utc).isoformat(),
                symbol,
                sentiment_score,
                technical_score,
                ml_prob_up,
                ml_prob_down,
                composite_score,
                action,
                confidence,
                int(risk_approved) if risk_approved is not None else None,
                risk_reason,
                position_size,
                volatility_regime,
                intent_hash,
                tx_hash,
                signature,
                order_id,
                order_status,
                fill_price,
                fill_size,
                realized_pnl,
                latency_ms,
                execution_source,
                pipeline_stage,
                features_json,
            ),
        )

    def get_audit_trail(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent audit trail entries."""
        rows = self.db.fetch_all(
            """
            SELECT id, cycle_id, timestamp, symbol,
                   sentiment_score, technical_score, ml_prob_up, ml_prob_down,
                   composite_score, action, confidence,
                   risk_approved, risk_reason, position_size, volatility_regime,
                   intent_hash, order_id, order_status, fill_price, fill_size, realized_pnl,
                   latency_ms, execution_source, pipeline_stage
            FROM audit_trail ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        )
        return rows

    def get_order_states(self, order_id: str) -> list[dict[str, Any]]:
        """Return all state transitions for a given order."""
        rows = self.db.fetch_all(
            "SELECT * FROM order_states WHERE order_id = ? ORDER BY id",
            (order_id,),
        )
        for row in rows:
            if row.get("metadata"):
                row["metadata"] = json.loads(row["metadata"])
        return rows

    def log_explainability(self, run_id: int, decision_id: int, symbol: str, confidence_score: float, feature_importance: dict, decision_trace: str) -> None:
        self.db.execute(
            """
            INSERT INTO explainability_logs(run_id, decision_id, timestamp, symbol, confidence_score, feature_importance_json, decision_trace)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                decision_id,
                datetime.now(timezone.utc).isoformat(),
                symbol,
                confidence_score,
                json.dumps(feature_importance, default=str),
                decision_trace,
            ),
        )

    def store_metric(self, name: str, payload: dict[str, Any]) -> None:
        self.db.upsert_metric(name, payload)

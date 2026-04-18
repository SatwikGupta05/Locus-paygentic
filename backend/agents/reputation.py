from __future__ import annotations

import json
from datetime import datetime, timezone
from math import sqrt
from typing import Any

from backend.database.db_manager import DBManager
from backend.utils.config import ROOT_DIR


class ReputationTracker:
    """Computes and persists agent performance reputation metrics."""

    def __init__(self, db: DBManager) -> None:
        self.db = db

    def compute(self, run_id: int | None = None) -> dict[str, Any]:
        trades = self.db.fetch_all(
            "SELECT realized_pnl, confidence, price, amount FROM trades ORDER BY id"
        )
        if not trades:
            return self._empty()

        total = len(trades)
        wins = sum(1 for t in trades if t["realized_pnl"] > 0)
        losses = sum(1 for t in trades if t["realized_pnl"] <= 0)
        win_rate = wins / max(total, 1)

        pnls = [float(t["realized_pnl"]) for t in trades]
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        profit_factor = gross_profit / max(gross_loss, 1e-9)

        # Sharpe from trade returns (annualized assuming ~252 trades/year scale)
        if len(pnls) >= 2:
            avg_return = sum(pnls) / len(pnls)
            std_return = (sum((p - avg_return) ** 2 for p in pnls) / len(pnls)) ** 0.5
            sharpe = (avg_return / max(std_return, 1e-9)) * sqrt(min(len(pnls), 252))
        else:
            sharpe = 0.0

        # Max drawdown from cumulative PnL
        cum_pnl = 0.0
        peak = 0.0
        max_dd = 0.0
        for pnl in pnls:
            cum_pnl += pnl
            peak = max(peak, cum_pnl)
            dd = (peak - cum_pnl) / max(peak, 1e-9) if peak > 0 else 0.0
            max_dd = max(max_dd, dd)

        avg_confidence = sum(float(t["confidence"]) for t in trades) / max(total, 1)

        # Max consecutive losses
        max_consec = 0
        current_streak = 0
        for pnl in pnls:
            if pnl <= 0:
                current_streak += 1
                max_consec = max(max_consec, current_streak)
            else:
                current_streak = 0

        recent_validation_scores, posted_validations, approved_intents = self._load_validation_context()
        recent_validation_avg = (
            sum(recent_validation_scores) / len(recent_validation_scores)
            if recent_validation_scores else 0.0
        )

        # Reputation in this hackathon context is primarily proof-driven:
        # recent on-chain validation quality, throughput, and execution
        # discipline matter more than raw PnL streaks.
        validation_score = min(82.0, recent_validation_avg * 0.82)
        throughput_score = min(8.0, approved_intents * 0.2)
        participation_score = min(4.0, posted_validations * 0.05)

        # Drawdown control still matters, but we keep the penalty light so
        # controlled experimentation does not collapse reputation.
        drawdown_score = 5.0
        if max_dd > 0.10:
            drawdown_control_factor = max(0.0, 1.0 - ((max_dd - 0.10) / 0.20))
            drawdown_score = 5.0 * drawdown_control_factor

        confidence_score = min(3.0, avg_confidence * 3.0)

        # Execution Accuracy (Compare filled intent to submitted. Approximation: % of non-failed orders)
        failed_row = self.db.fetch_one("SELECT COUNT(*) as cnt FROM orders WHERE status = 'failed' AND run_id <= ?", (run_id,))
        failed_orders = failed_row["cnt"] if failed_row else 0
        total_row = self.db.fetch_one("SELECT COUNT(*) as cnt FROM orders WHERE run_id <= ?", (run_id,))
        total_orders = max(1, total_row["cnt"] if total_row else 1)
        exec_accuracy = max(0.0, 1.0 - (failed_orders / total_orders))
        execution_score = exec_accuracy * 7.0

        # Consistency is a soft signal now. We penalize only extreme instability.
        consistency_score = 4.0
        if max_consec > 6:
            consistency_penalty = min(1.0, (max_consec - 6) / 10.0)
            consistency_score = 4.0 * (1.0 - consistency_penalty)

        reputation_score = (
            validation_score
            + throughput_score
            + participation_score
            + drawdown_score
            + confidence_score
            + execution_score
            + consistency_score
        )
        
        # Cap to the elite band because the product story is now judge-input
        # quality rather than pure PnL streak chasing.
        reputation_raw = max(0.0, min(99.0, reputation_score))
        reputation_norm = reputation_raw / 100.0

        result = {
            "win_rate": round(win_rate, 4),
            "profit_factor": round(profit_factor, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown": round(max_dd, 4),
            "total_trades": total,
            "avg_confidence": round(avg_confidence, 4),
            "max_consecutive_losses": max_consec,
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "validation_score": round(validation_score, 2),
            "reputation_raw": round(reputation_raw, 2),
            "reputation_norm": round(reputation_norm, 4),
            "recent_validation_avg": round(recent_validation_avg, 2),
            "throughput_score": round(throughput_score, 2),
            "participation_score": round(participation_score, 2),
            "drawdown_score": round(drawdown_score, 2),
            "confidence_score": round(confidence_score, 2),
            "execution_score": round(execution_score, 2),
            "consistency_score": round(consistency_score, 2)
        }

        # Persist
        timestamp = datetime.now(timezone.utc).isoformat()
        self.db.execute(
            """
            INSERT INTO reputation(run_id, timestamp, win_rate, sharpe_ratio, max_drawdown,
                total_trades, avg_confidence, profit_factor, validation_score, reputation_raw, reputation_norm, payload)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                timestamp,
                result["win_rate"],
                result["sharpe_ratio"],
                result["max_drawdown"],
                result["total_trades"],
                result["avg_confidence"],
                result["profit_factor"],
                result["validation_score"],
                result["reputation_raw"],
                result["reputation_norm"],
                json.dumps(result, default=str),
            ),
        )
        return result

    def latest(self) -> dict[str, Any]:
        row = self.db.fetch_one(
            "SELECT payload FROM reputation ORDER BY id DESC LIMIT 1"
        )
        if not row:
            return self._empty()
        return json.loads(row["payload"])

    @staticmethod
    def _load_validation_context() -> tuple[list[int], int, int]:
        recent_scores: list[int] = []
        posted_validations = 0
        approved_intents = 0
        checkpoints_file = ROOT_DIR / "checkpoints.jsonl"
        if not checkpoints_file.exists():
            return recent_scores, posted_validations, approved_intents

        for line in checkpoints_file.read_text(encoding="utf-8").splitlines():
            try:
                payload = json.loads(line)
            except Exception:
                continue
            score = payload.get("score")
            if isinstance(score, (int, float)):
                recent_scores.append(int(score))
            if payload.get("validation_tx_hash"):
                posted_validations += 1
            if payload.get("intent_tx_hash"):
                approved_intents += 1

        return recent_scores[-8:], posted_validations, approved_intents

    @staticmethod
    def _empty() -> dict[str, Any]:
        return {
            "win_rate": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "avg_confidence": 0.0,
            "profit_factor": 0.0,
            "max_consecutive_losses": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "validation_score": 0.0,
            "reputation_raw": 0.0,
            "reputation_norm": 0.0,
        }

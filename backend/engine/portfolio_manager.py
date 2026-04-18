from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from backend.database.db_manager import DBManager


@dataclass(slots=True)
class TradeResult:
    executed: bool
    realized_pnl: float
    order_status: str


class PortfolioManager:
    def __init__(
        self,
        db: DBManager,
        starting_balance: float,
        max_capital_per_trade: float,
        max_open_positions: int,
        stop_loss_pct: float,
        take_profit_pct: float,
        max_drawdown_pct: float,
        max_daily_loss_pct: float,
        max_symbol_exposure_pct: float,
        fee_bps: float,
    ) -> None:
        self.db = db
        self.starting_balance = starting_balance
        self.max_capital_per_trade = max_capital_per_trade
        self.max_open_positions = max_open_positions
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_symbol_exposure_pct = max_symbol_exposure_pct
        self.fee_rate = fee_bps / 10_000
        self.balance = starting_balance
        self.peak_equity = starting_balance
        self.daily_realized_pnl = 0.0

    def snapshot(self, mark_price: float) -> dict[str, float]:
        positions = self.db.fetch_all("SELECT * FROM positions")
        unrealized = 0.0
        exposure = 0.0
        for position in positions:
            unrealized += (mark_price - position["entry_price"]) * position["size"]
            exposure += position["entry_price"] * position["size"]
        equity = self.balance + unrealized
        self.peak_equity = max(self.peak_equity, equity)
        return {
            "balance": round(self.balance, 2),
            "equity": round(equity, 2),
            "unrealized_pnl": round(unrealized, 2),
            "daily_realized_pnl": round(self.daily_realized_pnl, 2),
            "drawdown_pct": round(max(0.0, (self.peak_equity - equity) / max(self.peak_equity, 1e-9)), 4),
            "open_positions": len(positions),
            "gross_exposure": round(exposure, 2),
        }

    def can_trade(self, symbol: str, trade_value: float, mark_price: float) -> tuple[bool, str]:
        snapshot = self.snapshot(mark_price)
        if snapshot["drawdown_pct"] >= self.max_drawdown_pct:
            return False, "max_drawdown"
        if abs(snapshot["daily_realized_pnl"]) >= self.starting_balance * self.max_daily_loss_pct:
            return False, "max_daily_loss"
        if snapshot["open_positions"] >= self.max_open_positions:
            return False, "max_open_positions"
        if trade_value > snapshot["balance"] * self.max_capital_per_trade:
            return False, "trade_size_limit"
        if trade_value > snapshot["equity"] * self.max_symbol_exposure_pct:
            return False, "symbol_exposure_limit"
        return True, "ok"

    def apply_fill(self, symbol: str, side: str, size: float, price: float, status: str = "filled") -> TradeResult:
        timestamp = datetime.now(timezone.utc).isoformat()
        existing = self.db.fetch_one("SELECT * FROM positions WHERE symbol = ?", (symbol,))

        if side == "BUY":
            trade_value = size * price
            fee = trade_value * self.fee_rate
            approved, reason = self.can_trade(symbol, trade_value, price)
            if not approved:
                return TradeResult(False, 0.0, reason)
            self.balance -= trade_value + fee
            self.db.execute(
                """
                INSERT INTO positions(symbol, side, status, entry_price, size, stop_loss, take_profit, unrealized_pnl, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    side=excluded.side,
                    status=excluded.status,
                    entry_price=excluded.entry_price,
                    size=excluded.size,
                    stop_loss=excluded.stop_loss,
                    take_profit=excluded.take_profit,
                    unrealized_pnl=excluded.unrealized_pnl,
                    updated_at=excluded.updated_at
                """,
                (
                    symbol,
                    "LONG",
                    status,
                    price,
                    size,
                    price * (1 - self.stop_loss_pct),
                    price * (1 + self.take_profit_pct),
                    0.0,
                    timestamp,
                ),
            )
            return TradeResult(True, -fee, status)

        if side == "SELL" and existing:
            gross = size * price
            fee = gross * self.fee_rate
            realized_pnl = (price - existing["entry_price"]) * size - fee
            self.balance += gross - fee
            self.daily_realized_pnl += realized_pnl
            remaining = max(existing["size"] - size, 0.0)
            if remaining == 0:
                self.db.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
            else:
                self.db.execute(
                    """
                    UPDATE positions SET
                        size = ?,
                        status = ?,
                        unrealized_pnl = ?,
                        updated_at = ?
                    WHERE symbol = ?
                    """,
                    (remaining, "partial", (price - existing["entry_price"]) * remaining, timestamp, symbol),
                )
            return TradeResult(True, round(realized_pnl, 2), status)

        return TradeResult(False, 0.0, "no_position")

    def update_mark_to_market(self, symbol: str, price: float) -> None:
        existing = self.db.fetch_one("SELECT * FROM positions WHERE symbol = ?", (symbol,))
        if not existing:
            return
        unrealized = (price - existing["entry_price"]) * existing["size"]
        self.db.execute(
            "UPDATE positions SET unrealized_pnl = ?, updated_at = ? WHERE symbol = ?",
            (round(unrealized, 2), datetime.now(timezone.utc).isoformat(), symbol),
        )

    def exit_signal(self, symbol: str, price: float) -> str | None:
        position = self.db.fetch_one("SELECT * FROM positions WHERE symbol = ?", (symbol,))
        if not position:
            return None
        if price <= position["stop_loss"] or price >= position["take_profit"]:
            return "SELL"
        return None

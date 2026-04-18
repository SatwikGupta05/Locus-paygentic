from __future__ import annotations

from typing import Any

from backend.execution.order_lifecycle import OrderRecord, OrderState


class PaperExecutor:
    def __init__(self, slippage_bps: float = 10.0) -> None:
        self.slippage_bps = slippage_bps / 10_000
        self._counter = 0
        self._orders: dict[str, OrderRecord] = {}

    def place_order(self, side: str, symbol: str, amount: float, mark_price: float) -> dict[str, Any]:
        self._counter += 1
        order_id = f"paper-{self._counter}"
        order = OrderRecord(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            requested_size=amount,
        )
        # CREATED → SUBMITTED
        order.transition(OrderState.SUBMITTED, {"mark_price": mark_price})
        # SUBMITTED → OPEN
        order.transition(OrderState.OPEN)

        signed_slippage = self.slippage_bps if side.upper() == "BUY" else -self.slippage_bps
        fill_price = mark_price * (1 + signed_slippage)

        # OPEN → FILLED
        order.filled_size = amount
        order.fill_price = fill_price
        order.transition(OrderState.FILLED, {"fill_price": round(fill_price, 2), "filled_size": amount})

        self._orders[order_id] = order
        return self._to_legacy(order)

    def simulate_partial_fill(self, side: str, symbol: str, amount: float, mark_price: float, fill_fraction: float = 0.6) -> dict[str, Any]:
        """Simulate a partial fill for demo/judging purposes."""
        self._counter += 1
        order_id = f"paper-{self._counter}"
        order = OrderRecord(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            requested_size=amount,
        )
        order.transition(OrderState.SUBMITTED)
        order.transition(OrderState.OPEN)

        signed_slippage = self.slippage_bps if side.upper() == "BUY" else -self.slippage_bps
        fill_price = mark_price * (1 + signed_slippage)
        partial_size = round(amount * fill_fraction, 6)

        order.filled_size = partial_size
        order.fill_price = fill_price
        order.transition(OrderState.PARTIAL, {"fill_price": round(fill_price, 2), "filled_size": partial_size})

        self._orders[order_id] = order
        return self._to_legacy(order)

    def simulate_failure(self, side: str, symbol: str, amount: float, reason: str = "insufficient_margin") -> dict[str, Any]:
        """Simulate a failed order for demo/judging purposes."""
        self._counter += 1
        order_id = f"paper-{self._counter}"
        order = OrderRecord(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            requested_size=amount,
        )
        order.transition(OrderState.SUBMITTED)
        order.transition(OrderState.FAILED, {"reason": reason})

        self._orders[order_id] = order
        return self._to_legacy(order)

    def get_order(self, order_id: str) -> OrderRecord | None:
        return self._orders.get(order_id)

    def get_all_orders(self) -> list[dict[str, Any]]:
        return [order.to_dict() for order in self._orders.values()]

    @staticmethod
    def _to_legacy(order: OrderRecord) -> dict[str, Any]:
        """Return a dict compatible with the existing trading_service interface."""
        status_map = {
            OrderState.FILLED: "filled",
            OrderState.PARTIAL: "partial",
            OrderState.FAILED: "failed",
            OrderState.CANCELLED: "cancelled",
        }
        return {
            "status": status_map.get(order.state, "pending"),
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "requested_amount": order.requested_size,
            "filled_size": order.filled_size,
            "fill_price": round(order.fill_price, 2),
            "timestamp": order.updated_at,
            "lifecycle": order.to_dict(),
        }

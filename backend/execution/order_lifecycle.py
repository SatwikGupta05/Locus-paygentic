from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class OrderState(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Valid state transitions
_TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.CREATED: {OrderState.SUBMITTED, OrderState.FAILED, OrderState.CANCELLED},
    OrderState.SUBMITTED: {OrderState.OPEN, OrderState.FAILED, OrderState.CANCELLED},
    OrderState.OPEN: {OrderState.PARTIAL, OrderState.FILLED, OrderState.FAILED, OrderState.CANCELLED},
    OrderState.PARTIAL: {OrderState.FILLED, OrderState.FAILED, OrderState.CANCELLED},
    OrderState.FILLED: set(),
    OrderState.FAILED: set(),
    OrderState.CANCELLED: set(),
}

TERMINAL_STATES = {OrderState.FILLED, OrderState.FAILED, OrderState.CANCELLED}


@dataclass(slots=True)
class StateTransition:
    from_state: OrderState
    to_state: OrderState
    timestamp: str
    metadata: dict[str, Any] | None = None


@dataclass
class OrderRecord:
    order_id: str
    symbol: str
    side: str
    requested_size: float
    state: OrderState = OrderState.CREATED
    filled_size: float = 0.0
    fill_price: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    state_history: list[StateTransition] = field(default_factory=list)

    def __post_init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if not self.state_history:
            self.state_history.append(
                StateTransition(
                    from_state=OrderState.CREATED,
                    to_state=OrderState.CREATED,
                    timestamp=self.created_at,
                )
            )

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def transition(self, new_state: OrderState, metadata: dict[str, Any] | None = None) -> None:
        if new_state not in _TRANSITIONS.get(self.state, set()):
            raise ValueError(f"Invalid transition: {self.state.value} → {new_state.value}")
        now = datetime.now(timezone.utc).isoformat()
        self.state_history.append(
            StateTransition(
                from_state=self.state,
                to_state=new_state,
                timestamp=now,
                metadata=metadata,
            )
        )
        self.state = new_state
        self.updated_at = now

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "requested_size": self.requested_size,
            "state": self.state.value,
            "filled_size": self.filled_size,
            "fill_price": round(self.fill_price, 2),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state_history": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "timestamp": t.timestamp,
                    "metadata": t.metadata,
                }
                for t in self.state_history
            ],
        }

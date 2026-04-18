from __future__ import annotations

import asyncio
from typing import Any


class RuntimeState:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._state: dict[str, Any] = {
            "market": {},
            "decision": {},
            "metrics": {},
            "latest_intent": {},
            "worker": {"status": "idle"},
            "pipeline_stage": {"stage": "IDLE", "data": {}},
            "reputation": {},
            "orders": [],
        }

    async def update(self, key: str, value: Any) -> None:
        async with self._lock:
            self._state[key] = value

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return dict(self._state)

    async def get(self, key: str, default: Any = None) -> Any:
        async with self._lock:
            return self._state.get(key, default)

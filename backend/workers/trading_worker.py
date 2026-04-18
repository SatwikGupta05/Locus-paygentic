from __future__ import annotations

import asyncio
import logging

from backend.services.trading_service import TradingService
from backend.services.runtime_state import RuntimeState
from backend.utils.config import Settings
from backend.utils.logger import log_event


class TradingWorker:
    def __init__(self, service: TradingService, settings: Settings, runtime_state: RuntimeState, logger: logging.Logger) -> None:
        self.service = service
        self.settings = settings
        self.runtime_state = runtime_state
        self.logger = logger
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        await self.service.initialize()
        await self.runtime_state.update("worker", {"status": "starting"})
        self._task = asyncio.create_task(self.run(), name="aurora-trading-worker")

    async def run(self) -> None:
        await self.runtime_state.update("worker", {"status": "running"})
        while not self._stop.is_set():
            try:
                await self.service.process_cycle()
            except Exception as exc:
                await self.runtime_state.update("worker", {"status": "error", "error": str(exc)})
                log_event(self.logger, "SYSTEM", "Trading worker cycle failed", error=str(exc))
            await asyncio.sleep(self.settings.worker_interval_seconds)

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.runtime_state.update("worker", {"status": "stopped"})

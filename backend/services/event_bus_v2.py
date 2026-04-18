from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any, Callable, Awaitable

from fastapi import WebSocket


class EventBusV2:
    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any]]] = defaultdict(asyncio.Queue)
        self._ws_channels: dict[str, set[WebSocket]] = defaultdict(set)
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], Awaitable[None]]]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._tasks: list[asyncio.Task[None]] = []

    async def start(self) -> None:
        # Start a generic background task that consumes queues if needed
        # In a generic event bus we might spawn consumer tasks
        pass

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    # Internal queue-based publish / subscribe for microservices/workers
    def subscribe_internal(self, topic: str, callback: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        self._subscribers[topic].append(callback)

    async def publish_internal(self, topic: str, payload: dict[str, Any]) -> None:
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                # In robust systems we might put messages on tasks.
                asyncio.create_task(callback(payload))

        # Also put on a raw queue if any direct consumers want to await get_queue
        await self._queues[topic].put(payload)

    async def get_queue(self, topic: str) -> asyncio.Queue[dict[str, Any]]:
        return self._queues[topic]

    # WebSocket-based publish / subscribe for frontend
    async def subscribe_ws(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._ws_channels[channel].add(websocket)

    async def unsubscribe_ws(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._ws_channels[channel].discard(websocket)

    async def publish_ws(self, channel: str, payload: dict[str, Any]) -> None:
        message = json.dumps(payload, default=str)
        async with self._lock:
            sockets = list(self._ws_channels[channel])
        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception:
                await self.unsubscribe_ws(channel, socket)

    # Unified publisher
    async def publish(self, topic: str, payload: dict[str, Any], broadcast_ws: bool = False) -> None:
        await self.publish_internal(topic, payload)
        if broadcast_ws:
            await self.publish_ws(topic, payload)

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "channel": getattr(record, "channel", "SYSTEM"),
            "message": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(context)
        return json.dumps(payload, default=str)


class SafeConsoleFormatter(logging.Formatter):
    """Console formatter that safely handles missing fields with defaults."""
    def format(self, record: logging.LogRecord) -> str:
        # Provide defaults for missing fields
        channel = getattr(record, "channel", record.name.upper())
        record.channel = channel
        return super().format(record)


def create_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("aurora")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SafeConsoleFormatter("[%(channel)s] %(message)s"))
    logger.addHandler(console_handler)

    return logger


def log_event(logger: logging.Logger, channel: str, message: str, **context: Any) -> None:
    logger.info(message, extra={"channel": channel, "context": context})

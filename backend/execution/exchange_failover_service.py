"""
Exchange Failover Integration for AURORA Trading Service

This module integrates the ExchangeManager with AURORA's trading pipeline,
providing seamless failover to judges and traders.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import pandas as pd

from backend.execution.exchange_manager import ExchangeManager

logger = logging.getLogger(__name__)


class ExchangeFailoverService:
    """
    High-level service that wraps ExchangeManager for trading applications.
    Provides async-compatible methods and error handling for trading workflows.
    
    Usage:
        service = ExchangeFailoverService()
        ticker = service.get_ticker("BTC/USDT")
        ohlcv_df = service.get_ohlcv_as_dataframe("BTC/USDT", "1h", 500)
    """
    
    def __init__(self, region: str = "india"):
        """Initialize exchange service with regional awareness."""
        self.manager = ExchangeManager(region=region)
        self.logger = logger
    
    def initialize(self) -> bool:
        """
        Initialize exchange connections.
        
        Returns:
            True if at least one exchange is available
        """
        logger.info("[AURORA] Initializing multi-exchange failover system...")
        
        success = self.manager.connect()
        
        if success:
            status = self.manager.get_status()
            logger.info(
                f"[AURORA] ✅ Exchange system ready. Active: {status['active_exchange'].upper()}"
            )
        else:
            logger.error("[AURORA] ❌ Failed to initialize any exchange")
        
        return success
    
    def get_ticker(self, symbol: str = "BTC/USDT", retries: int = 3) -> Optional[dict[str, Any]]:
        """
        Get latest ticker with failover support.
        
        Args:
            symbol: Trading pair (BTC/USDT, ETH/USDT, etc.)
            retries: Retry attempts per exchange
        
        Returns:
            Ticker dict or None on failure
        """
        try:
            ticker = self.manager.fetch_ticker(symbol, retries=retries)
            self._log_fetch_success(symbol, "ticker", ticker.get("last"))
            return ticker
        except Exception as e:
            self._log_fetch_failure(symbol, "ticker", str(e))
            return None
    
    def get_ohlcv(self, symbol: str = "BTC/USDT", timeframe: str = "1h",
                  limit: int = 100, retries: int = 3) -> Optional[list[list[Any]]]:
        """
        Get OHLCV candlestick data with failover support.
        
        Args:
            symbol: Trading pair
            timeframe: Candle period (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles to fetch
            retries: Retry attempts per exchange
        
        Returns:
            List of OHLCV data or None on failure
        """
        try:
            ohlcv = self.manager.fetch_ohlcv(symbol, timeframe, limit, retries=retries)
            self._log_fetch_success(symbol, f"OHLCV {timeframe}", f"{len(ohlcv)} candles")
            return ohlcv
        except Exception as e:
            self._log_fetch_failure(symbol, f"OHLCV {timeframe}", str(e))
            return None
    
    def get_ohlcv_as_dataframe(self, symbol: str = "BTC/USDT", timeframe: str = "1h",
                               limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Get OHLCV as pandas DataFrame (convenient for analysis).
        
        Args:
            symbol: Trading pair
            timeframe: Candle period
            limit: Number of candles
        
        Returns:
            DataFrame with columns [timestamp, open, high, low, close, volume]
        """
        ohlcv = self.get_ohlcv(symbol, timeframe, limit)
        if ohlcv is None:
            return None
        
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    
    def get_status_report(self) -> str:
        """
        Get human-readable status report for judges/monitoring.
        
        Shows active exchange, failover history, health metrics.
        """
        status = self.manager.get_status()
        
        report = "\n" + "=" * 70
        report += "\n🤖 AURORA EXCHANGE FAILOVER STATUS\n"
        report += "=" * 70 + "\n"
        
        # Active exchange
        active = status.get("active_exchange", "NONE")
        report += f"Active Exchange: {active.upper() if active else '❌ NONE'}\n"
        report += f"Connected: {'✅ YES' if status.get('connected') else '❌ NO'}\n"
        report += f"Region: {status['summary'].get('region', 'unknown').upper()}\n"
        report += f"Total Failures: {status['summary'].get('total_failures', 0)}\n\n"
        
        # Per-exchange status
        report += "Exchange Status:\n"
        report += "-" * 70 + "\n"
        
        for name, ex_status in status.get("exchanges", {}).items():
            is_active_str = " (ACTIVE)" if ex_status.get("is_active") else ""
            status_emoji = self._status_emoji(ex_status.get("status"))
            failures = ex_status.get("failures", 0)
            last_success = ex_status.get("last_success_ago_seconds", 0)
            
            report += (
                f"{status_emoji} {name.upper():<10} | "
                f"Status: {ex_status.get('status'):<18} | "
                f"Failures: {failures:<3} | "
                f"Last Success: {last_success}s ago{is_active_str}\n"
            )
        
        report += "=" * 70 + "\n"
        return report
    
    def print_status(self) -> None:
        """Print status report to logger."""
        logger.info(self.get_status_report())
    
    def health_check(self) -> bool:
        """
        Run quick health check of active exchange.
        
        Returns:
            True if system is healthy
        """
        is_healthy = self.manager.health_check()
        status_str = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
        logger.info(f"[AURORA] Health Check: {status_str}")
        return is_healthy
    
    def force_reconnect(self) -> bool:
        """
        Force reconnection to highest-priority available exchange.
        Useful if current exchange becomes unreliable.
        
        Returns:
            True if reconnection successful
        """
        logger.info("[AURORA] Forcing exchange reconnection...")
        success = self.manager.connect(force_refresh=True)
        
        if success:
            status = self.manager.get_status()
            logger.info(f"[AURORA] ✅ Reconnected to {status['active_exchange'].upper()}")
        else:
            logger.error("[AURORA] ❌ Reconnection failed - no exchanges available")
        
        return success
    
    @staticmethod
    def _status_emoji(status: str) -> str:
        """Convert status string to emoji."""
        emoji_map = {
            "healthy": "🟢",
            "connected": "🟡",
            "connection_failed": "🔴",
            "unhealthy": "🔴",
            "failover_failed": "🔴",
            "init_failed": "⚫",
            "unknown": "⚪",
        }
        return emoji_map.get(status, "❓")
    
    @staticmethod
    def _log_fetch_success(symbol: str, operation: str, result: str) -> None:
        """Log successful data fetch."""
        logger.info(f"[AURORA] ✅ Fetched {operation} for {symbol}: {result}")
    
    @staticmethod
    def _log_fetch_failure(symbol: str, operation: str, error: str) -> None:
        """Log failed data fetch."""
        logger.error(f"[AURORA] ❌ Failed to fetch {operation} for {symbol}: {error[:80]}")


# Singleton instance for application
_exchange_service: Optional[ExchangeFailoverService] = None


def get_exchange_service(region: str = "india") -> ExchangeFailoverService:
    """
    Get or create the exchange failover service.
    
    This is a singleton pattern to ensure only one manager instance.
    """
    global _exchange_service
    
    if _exchange_service is None:
        _exchange_service = ExchangeFailoverService(region=region)
    
    return _exchange_service


def initialize_exchange_system(region: str = "india") -> bool:
    """
    Initialize the exchange failover system at application startup.
    
    Args:
        region: Geographic region for connectivity optimization
    
    Returns:
        True if initialization successful
    """
    service = get_exchange_service(region=region)
    return service.initialize()

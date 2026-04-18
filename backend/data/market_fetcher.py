from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from random import uniform

import ccxt
import pandas as pd

logger = logging.getLogger("aurora")


class DataMode(str, Enum):
    LIVE = "LIVE"
    PAPER = "PAPER"
    SYNTHETIC = "SYNTHETIC"


@dataclass(slots=True)
class MarketSnapshot:
    symbol: str
    timeframe: str
    candles: pd.DataFrame
    source: str
    mode: DataMode
    exchange: str = "unknown"

    @property
    def price(self) -> float:
        return float(self.candles["close"].iloc[-1])


class MarketFetcher:
    def __init__(self, mode: DataMode, exchange_id: str = "kucoin", max_retries: int = 3, 
                 use_failover: bool = True, region: str = "india") -> None:
        """
        Initialize market data fetcher with optional exchange failover.
        
        Args:
            mode: LIVE, PAPER, or SYNTHETIC data mode
            exchange_id: Primary exchange (kucoin, kraken, binance)
            max_retries: Retry attempts per exchange
            use_failover: Whether to use multi-exchange failover system
            region: Geographic region for exchange selection (india, default, etc)
        """
        self.mode = mode
        self.max_retries = max_retries
        self.use_failover = use_failover
        self.current_exchange_id = exchange_id
        self.region = region
        self._synthetic_anchor = 65000.0
        
        # For India region, avoid Binance (geo-blocked)
        if region.lower() == "india" and exchange_id.lower() == "binance":
            logger.warning("[AURORA] Binance blocked in India, switching to KuCoin")
            exchange_id = "kucoin"
        
        # Always create a base exchange instance as fallback
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({"enableRateLimit": True})
        
        # Initialize failover system if enabled
        if use_failover:
            try:
                from backend.execution.exchange_failover_service import get_exchange_service
                self.failover_service = get_exchange_service(region="india")
                self.failover_service.initialize()
                logger.info("[AURORA] Market fetcher using multi-exchange failover")
            except Exception as e:
                logger.warning(f"[AURORA] Failover system init failed, using single exchange: {e}")
                self.failover_service = None
        else:
            self.failover_service = None

    def fetch_ohlcv(self, symbol: str = "BTC/USD", timeframe: str = "1m", limit: int = 200) -> pd.DataFrame:
        if self.mode == DataMode.SYNTHETIC:
            return self._synthetic_ohlcv(limit)

        # Try failover service first if available
        if self.failover_service:
            try:
                logger.debug(f"[AURORA] Fetching {symbol} {timeframe} via failover service")
                df = self.failover_service.get_ohlcv_as_dataframe(symbol, timeframe, limit)
                if df is not None:
                    return df
            except Exception as e:
                logger.warning(f"[AURORA] Failover service fetch failed, falling back: {e}")
        
        # Fallback to single exchange
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                candles = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                frame = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
                for column in ["open", "high", "low", "close", "volume"]:
                    frame[column] = pd.to_numeric(frame[column], errors="coerce")
                frame["mode"] = self.mode.value
                return frame.dropna().reset_index(drop=True)
            except (ccxt.NetworkError, ccxt.ExchangeNotAvailable) as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    backoff_time = 2 ** attempt
                    logger.warning(f"Network error fetching {symbol} (attempt {attempt+1}/{self.max_retries}), retrying in {backoff_time}s: {type(exc).__name__}")
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Failed to fetch {symbol} after {self.max_retries} attempts: {exc}")
            except Exception as exc:
                # Don't retry on authentication or other errors
                logger.error(f"Unrecoverable error fetching {symbol}: {exc}")
                last_error = exc
                break
        
        if self.mode == DataMode.PAPER:
            logger.info(f"Falling back to synthetic data for {symbol}")
            return self._synthetic_ohlcv(limit)
        raise RuntimeError("Failed to fetch live market data") from last_error

    def fetch_snapshot(self, symbol: str, timeframe: str, limit: int) -> MarketSnapshot:
        candles = self.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        is_synthetic = self.mode == DataMode.SYNTHETIC or ("mode" in candles.columns and candles["mode"].iloc[0] == "SYNTHETIC")
        source = "synthetic-generator" if is_synthetic else getattr(self.exchange, "id", self.current_exchange_id)
        return MarketSnapshot(symbol=symbol, timeframe=timeframe, candles=candles, source=source, mode=self.mode)

    def _synthetic_ohlcv(self, limit: int) -> pd.DataFrame:
        rows: list[dict[str, float | str | pd.Timestamp]] = []
        current_time = pd.Timestamp.utcnow().floor("min")
        price = self._synthetic_anchor
        for idx in range(limit):
            open_price = price
            drift = uniform(-140, 140)
            close_price = max(1000.0, open_price + drift)
            high_price = max(open_price, close_price) + abs(uniform(5, 60))
            low_price = min(open_price, close_price) - abs(uniform(5, 60))
            volume = abs(uniform(5, 150))
            rows.append(
                {
                    "timestamp": current_time - pd.Timedelta(minutes=limit - idx),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": round(volume, 4),
                    "mode": DataMode.SYNTHETIC.value,
                }
            )
            price = close_price
        self._synthetic_anchor = price
        return pd.DataFrame(rows)

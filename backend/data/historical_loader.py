from __future__ import annotations

from pathlib import Path

import ccxt
import pandas as pd


class HistoricalLoader:
    def __init__(self, output_path: Path, exchange_id: str = "kraken") -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({"enableRateLimit": True})

    def download_ohlcv(self, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
        candles = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        frame = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
        for column in ["open", "high", "low", "close", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        self.validate_timestamps(frame)
        return frame.dropna().reset_index(drop=True)

    def validate_timestamps(self, frame: pd.DataFrame) -> None:
        if frame["timestamp"].duplicated().any():
            raise ValueError("Historical dataset contains duplicated timestamps")
        if not frame["timestamp"].is_monotonic_increasing:
            raise ValueError("Historical dataset timestamps are not ordered")

    def save_parquet(self, frame: pd.DataFrame) -> Path:
        frame.to_parquet(self.output_path, index=False)
        return self.output_path

    def load(self) -> pd.DataFrame:
        return pd.read_parquet(self.output_path)

    def synthetic_history(self, rows: int = 1500) -> pd.DataFrame:
        timestamps = pd.date_range(end=pd.Timestamp.utcnow().floor("min"), periods=rows, freq="min", tz="UTC")
        price = 65000.0
        records: list[dict[str, float | pd.Timestamp]] = []
        for timestamp in timestamps:
            drift = ((timestamp.minute % 12) - 6) * 18
            open_price = price
            close_price = max(1000.0, open_price + drift)
            high_price = max(open_price, close_price) + 20
            low_price = min(open_price, close_price) - 20
            records.append(
                {
                    "timestamp": timestamp,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": 25 + (timestamp.minute % 10),
                }
            )
            price = close_price
        return pd.DataFrame(records)

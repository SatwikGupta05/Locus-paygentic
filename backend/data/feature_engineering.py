from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class FeatureVector:
    values: dict[str, float]


class FeatureEngineering:
    feature_order = [
        "rsi",
        "ema_fast_gap",
        "ema_slow_gap",
        "macd",
        "macd_signal",
        "macd_hist",
        "bollinger_band_width",
        "momentum",
        "volume_spike",
        "sentiment_score",
        "volatility",
        "return_1",
        "return_5",
        "atr",
    ]

    def generate(self, candles: pd.DataFrame, sentiment_score: float) -> FeatureVector:
        frame = candles.copy()
        frame["return_1"] = frame["close"].pct_change()
        frame["return_5"] = frame["close"].pct_change(5)
        frame["ema_12"] = frame["close"].ewm(span=12, adjust=False).mean()
        frame["ema_26"] = frame["close"].ewm(span=26, adjust=False).mean()
        frame["ema_fast_gap"] = (frame["close"] - frame["ema_12"]) / frame["close"]
        frame["ema_slow_gap"] = (frame["close"] - frame["ema_26"]) / frame["close"]
        frame["macd"] = frame["ema_12"] - frame["ema_26"]
        frame["macd_signal"] = frame["macd"].ewm(span=9, adjust=False).mean()
        frame["macd_hist"] = frame["macd"] - frame["macd_signal"]
        delta = frame["close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean().replace(0, 1e-9)
        rs = gain / loss
        frame["rsi"] = 100 - (100 / (1 + rs))
        middle = frame["close"].rolling(20).mean()
        std = frame["close"].rolling(20).std().replace(0, 1e-9)
        upper = middle + 2 * std
        lower = middle - 2 * std
        frame["bollinger_band_width"] = (upper - lower) / middle.replace(0, 1e-9)
        frame["momentum"] = frame["close"] / frame["close"].shift(10) - 1
        frame["volume_spike"] = frame["volume"] / frame["volume"].rolling(20).mean().replace(0, 1e-9)
        frame["volatility"] = frame["return_1"].rolling(20).std().fillna(0.0)
        high_low = frame["high"] - frame["low"]
        high_close = (frame["high"] - frame["close"].shift()).abs()
        low_close = (frame["low"] - frame["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        frame["atr"] = tr.rolling(14).mean().bfill().fillna(0.0)
        frame["sentiment_score"] = float(sentiment_score)
        latest = frame.iloc[-1].fillna(0.0)
        return FeatureVector(values={column: float(latest.get(column, 0.0)) for column in self.feature_order})

    def build_training_frame(self, candles: pd.DataFrame, sentiment_score: float = 0.0) -> tuple[pd.DataFrame, pd.Series]:
        features: list[dict[str, float]] = []
        labels: list[int] = []
        for idx in range(40, len(candles) - 1):
            window = candles.iloc[: idx + 1]
            features.append(self.generate(window, sentiment_score=sentiment_score).values)
            labels.append(int(candles["close"].iloc[idx + 1] > candles["close"].iloc[idx]))
        return pd.DataFrame(features, columns=self.feature_order), pd.Series(labels, name="target")

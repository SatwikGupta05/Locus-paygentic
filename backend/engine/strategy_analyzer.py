"""Enhanced strategy analyzer with RSI, MACD, and EMA signals.

This provides the technical foundation for profitable trading.
"""
from __future__ import annotations

import pandas as pd
from typing import Any


class StrategyAnalyzer:
    """Analyzes technical indicators and generates trading signals."""

    def __init__(self, rsi_period: int = 14, ema_short: int = 20, ema_long: int = 50):
        self.rsi_period = rsi_period
        self.ema_short = ema_short
        self.ema_long = ema_long

    def analyze(self, candles: pd.DataFrame) -> dict[str, Any]:
        """Analyze candle data and return trading signals.
        
        Args:
            candles: DataFrame with OHLCV data
            
        Returns:
            Dict with RSI, MACD, EMA, and combined signals
        """
        if len(candles) < max(self.rsi_period, self.ema_long):
            return self._empty_signals()

        # ─── RSI (Relative Strength Index) ─────────────────────────────
        rsi = self._compute_rsi(candles["close"], self.rsi_period)

        # ─── EMA (Exponential Moving Averages) ──────────────────────────
        ema_short = self._compute_ema(candles["close"], self.ema_short)
        ema_long = self._compute_ema(candles["close"], self.ema_long)

        # ─── MACD (Moving Average Convergence Divergence) ───────────────
        macd_line, signal_line, histogram = self._compute_macd(candles["close"])

        # ─── Current Values ────────────────────────────────────────────
        current_price = float(candles["close"].iloc[-1])
        current_rsi = float(rsi.iloc[-1]) if len(rsi) > 0 else 50
        current_ema_short = float(ema_short.iloc[-1]) if len(ema_short) > 0 else current_price
        current_ema_long = float(ema_long.iloc[-1]) if len(ema_long) > 0 else current_price
        current_macd = float(macd_line.iloc[-1]) if len(macd_line) > 0 else 0
        current_signal = float(signal_line.iloc[-1]) if len(signal_line) > 0 else 0
        current_histogram = float(histogram.iloc[-1]) if len(histogram) > 0 else 0
        prev_histogram = float(histogram.iloc[-2]) if len(histogram) > 1 else 0

        # ─── Signal Conditions ──────────────────────────────────────────
        rsi_oversold = current_rsi < 30
        rsi_overbought = current_rsi > 70
        price_above_ema20 = current_price > current_ema_short
        ema_bullish_cross = current_ema_short > current_ema_long
        macd_bullish = current_histogram > 0
        macd_crossover = (prev_histogram <= 0 and current_histogram > 0)  # Line crosses above signal

        # ─── Volatility (Normalized ATR) ────────────────────────────────
        volatility = self._compute_volatility(candles)
        atr = self._compute_atr(candles)

        # ─── Composite Signal Score (0 to 1 for BUY, -1 to 0 for SELL) ──
        buy_signals = sum([
            rsi_oversold,
            price_above_ema20,
            ema_bullish_cross,
            macd_bullish,
            macd_crossover,
        ])
        sell_signals = sum([
            rsi_overbought,
            not price_above_ema20,
            not ema_bullish_cross,
            not macd_bullish,
        ])

        # Normalize to -1 to 1 scale
        if buy_signals + sell_signals > 0:
            technical_score = (buy_signals - sell_signals) / (buy_signals + sell_signals)
        else:
            technical_score = 0.0

        return {
            "rsi": round(current_rsi, 2),
            "rsi_oversold": rsi_oversold,
            "rsi_overbought": rsi_overbought,
            "ema_short": round(current_ema_short, 4),
            "ema_long": round(current_ema_long, 4),
            "price_above_ema20": price_above_ema20,
            "ema_bullish_cross": ema_bullish_cross,
            "macd": round(current_macd, 6),
            "macd_signal": round(current_signal, 6),
            "macd_histogram": round(current_histogram, 6),
            "macd_bullish": macd_bullish,
            "macd_crossover": macd_crossover,
            "volatility": round(volatility, 4),
            "atr": round(atr, 4),
            "technical_score": round(technical_score, 4),
            "buy_signal_count": buy_signals,
            "sell_signal_count": sell_signals,
        }

    def _compute_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Compute Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _compute_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Compute Exponential Moving Average."""
        return prices.ewm(span=period, adjust=False).mean()

    def _compute_macd(self, prices: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Compute MACD (Moving Average Convergence Divergence)."""
        ema_12 = prices.ewm(span=12, adjust=False).mean()
        ema_26 = prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def _compute_volatility(self, candles: pd.DataFrame) -> float:
        """Compute normalized volatility (realized volatility)."""
        if len(candles) < 2:
            return 0.0
        returns = candles["close"].pct_change().dropna()
        if len(returns) == 0:
            return 0.0
        volatility = returns.std()
        return float(volatility)

    def _compute_atr(self, candles: pd.DataFrame, period: int = 14) -> float:
        """Compute Average True Range."""
        if len(candles) < period:
            return 0.0

        high = candles["high"]
        low = candles["low"]
        close = candles["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return float(atr.iloc[-1]) if len(atr) > 0 else 0.0

    def _empty_signals(self) -> dict[str, Any]:
        """Return empty signals dict when insufficient data."""
        return {
            "rsi": 50.0,
            "rsi_oversold": False,
            "rsi_overbought": False,
            "ema_short": 0.0,
            "ema_long": 0.0,
            "price_above_ema20": False,
            "ema_bullish_cross": False,
            "macd": 0.0,
            "macd_signal": 0.0,
            "macd_histogram": 0.0,
            "macd_bullish": False,
            "macd_crossover": False,
            "volatility": 0.0,
            "atr": 0.0,
            "technical_score": 0.0,
            "buy_signal_count": 0,
            "sell_signal_count": 0,
        }

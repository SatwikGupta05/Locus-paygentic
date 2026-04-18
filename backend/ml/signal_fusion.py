from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd
import numpy as np


class SignalType(Enum):
    """Signal classification types for multi-signal fusion."""
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"
    VOLATILITY = "volatility"
    VOLUME_ANOMALY = "volume_anomaly"
    REGIME_SHIFT = "regime_shift"


@dataclass
class SignalStrength:
    """Quantifies signal strength and direction."""
    type: SignalType
    strength: float  # -1.0 (strong bearish) to +1.0 (strong bullish)
    confidence: float  # 0.0 to 1.0
    description: str


class TechnicalSignalFusion:
    """Fuses technical indicators into unified directional signals."""
    
    def __init__(self):
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.rsi_extreme_overbought = 80
        self.rsi_extreme_oversold = 20
    
    def macd_signal(self, macd: float, macd_signal: float, macd_hist: float) -> SignalStrength:
        """Generate signal from MACD."""
        if macd > macd_signal and macd_hist > 0:
            strength = min(abs(macd_hist) * 5, 1.0)  # Scale to 0-1
            description = "MACD bullish crossover with positive histogram"
        elif macd < macd_signal and macd_hist < 0:
            strength = -min(abs(macd_hist) * 5, 1.0)
            description = "MACD bearish crossover with negative histogram"
        else:
            strength = 0.0
            description = "MACD neutral"
        
        return SignalStrength(
            type=SignalType.TECHNICAL,
            strength=strength,
            confidence=min(abs(macd_hist), 0.001) / 0.001,  # Normalized
            description=description
        )
    
    def rsi_signal(self, rsi: float) -> SignalStrength:
        """Generate signal from RSI."""
        if rsi > self.rsi_extreme_overbought:
            strength = -0.9
            desc = "RSI extremely overbought - strong reversal warning"
        elif rsi > self.rsi_overbought:
            strength = -0.5
            desc = "RSI overbought - potential pullback"
        elif rsi < self.rsi_extreme_oversold:
            strength = 0.9
            desc = "RSI extremely oversold - strong reversal opportunity"
        elif rsi < self.rsi_oversold:
            strength = 0.5
            desc = "RSI oversold - potential bounce"
        else:
            strength = 0.0
            desc = "RSI neutral zone"
        
        return SignalStrength(
            type=SignalType.TECHNICAL,
            strength=strength,
            confidence=abs(rsi - 50) / 50,  # Further from 50 = more confident
            description=desc
        )
    
    def bollinger_band_signal(self, bb_width: float, ema_fast_gap: float) -> SignalStrength:
        """Generate signal from Bollinger Bands."""
        if bb_width < 0.05:
            # Squeeze - breakout coming
            strength = 0.3 if ema_fast_gap > 0 else -0.3
            desc = f"Bollinger Squeeze detected ({bb_width:.3%}) - breakout pending"
        elif ema_fast_gap > 0.02:
            strength = 0.6
            desc = "Price significantly above Bollinger midline - strong uptrend"
        elif ema_fast_gap < -0.02:
            strength = -0.6
            desc = "Price significantly below Bollinger midline - strong downtrend"
        else:
            strength = 0.0
            desc = "Price within normal Bollinger range"
        
        return SignalStrength(
            type=SignalType.TECHNICAL,
            strength=strength,
            confidence=min(abs(bb_width), 0.1) / 0.1,
            description=desc
        )


class VolatilityRegimeDetector:
    """Detects market regime and volatility conditions."""
    
    def __init__(self):
        self.high_vol_threshold = 0.03
        self.low_vol_threshold = 0.01
    
    def get_regime_signal(self, volatility: float, atr: float) -> SignalStrength:
        """Characterize volatility regime."""
        if volatility > self.high_vol_threshold:
            regime = "EXTREME"
            # Require higher confidence in extreme vol
            strength = -0.5
            desc = f"Extreme volatility ({volatility:.2%}) - risk-off mode"
            confidence = 0.9
        elif volatility > 0.02:
            regime = "HIGH"
            strength = 0.0  # Neutral in elevated vol
            desc = f"Elevated volatility ({volatility:.2%}) - prefer mean reversion"
            confidence = 0.7
        elif volatility < self.low_vol_threshold:
            regime = "COMPRESSION"
            strength = 0.3  # Slight bullish in quiet markets
            desc = f"Low volatility compression ({volatility:.2%}) - breakout potential"
            confidence = 0.6
        else:
            regime = "NORMAL"
            strength = 0.0
            desc = "Normal volatility regime"
            confidence = 0.5
        
        return SignalStrength(
            type=SignalType.VOLATILITY,
            strength=strength,
            confidence=confidence,
            description=desc
        )


class VolumeAnomalyDetector:
    """Detects unusual volume patterns."""
    
    def __init__(self):
        self.spike_threshold = 1.5
        self.dry_threshold = 0.6
    
    def get_volume_signal(self, volume_spike: float, momentum: float) -> SignalStrength:
        """Analyze volume anomalies."""
        if volume_spike > self.spike_threshold:
            # High volume confirms direction
            if momentum > 0:
                strength = 0.7
                desc = f"High volume spike ({volume_spike:.1f}x) confirming upside momentum"
            else:
                strength = -0.7
                desc = f"High volume spike ({volume_spike:.1f}x) confirming downside"
            confidence = 0.8
        elif volume_spike < self.dry_threshold:
            # Low volume warns
            strength = -0.3
            desc = f"Weak volume ({volume_spike:.1f}x average) - low conviction move"
            confidence = 0.6
        else:
            strength = 0.0
            desc = "Volume in normal range"
            confidence = 0.4
        
        return SignalStrength(
            type=SignalType.VOLUME_ANOMALY,
            strength=strength,
            confidence=confidence,
            description=desc
        )


class SentimentFusion:
    """Integrates sentiment signals (placeholder for external data)."""
    
    def get_sentiment_signal(self, sentiment_score: float) -> SignalStrength:
        """
        Sentiment score: -1.0 (very bearish) to +1.0 (very bullish)
        Typically from Twitter, news, on-chain data streams.
        """
        if sentiment_score > 0.5:
            strength = sentiment_score * 0.8  # Cap at 0.8 to avoid over-reliance
            desc = f"Bullish sentiment ({sentiment_score:.2f}) from external sources"
            confidence = 0.6
        elif sentiment_score < -0.5:
            strength = sentiment_score * 0.8
            desc = f"Bearish sentiment ({sentiment_score:.2f}) from external sources"
            confidence = 0.6
        else:
            strength = 0.0
            desc = "Neutral sentiment reading"
            confidence = 0.3
        
        return SignalStrength(
            type=SignalType.SENTIMENT,
            strength=strength,
            confidence=confidence,
            description=desc
        )


class MultiSignalFusion:
    """
    Master fusion engine combining all signal types into unified decision weights.
    This is the high-level agent that decides which signals to trust.
    """
    
    def __init__(self):
        self.technical_fusion = TechnicalSignalFusion()
        self.volatility_detector = VolatilityRegimeDetector()
        self.volume_detector = VolumeAnomalyDetector()
        self.sentiment_fusion = SentimentFusion()
    
    def fuse_signals(self, features: dict[str, float], 
                     external_sentiment: Optional[float] = None) -> dict:
        """
        Fuse all available signals into weighted recommendation.
        
        Returns:
            {
                "fused_strength": -1.0 to 1.0 (unified directional bias),
                "consensus_confidence": 0.0 to 1.0 (how confident all signals agree),
                "signals": [list of individual SignalStrength objects],
                "narrative": "Human-readable explanation of fusion result"
            }
        """
        
        signals: list[SignalStrength] = []
        
        # Gather technical signals
        macd_sig = self.technical_fusion.macd_signal(
            features.get("macd", 0),
            features.get("macd_signal", 0),
            features.get("macd_hist", 0)
        )
        signals.append(macd_sig)
        
        rsi_sig = self.technical_fusion.rsi_signal(features.get("rsi", 50))
        signals.append(rsi_sig)
        
        bb_sig = self.technical_fusion.bollinger_band_signal(
            features.get("bollinger_band_width", 0.05),
            features.get("ema_fast_gap", 0)
        )
        signals.append(bb_sig)
        
        # Volatility regime
        vol_sig = self.volatility_detector.get_regime_signal(
            features.get("volatility", 0.02),
            features.get("atr", 0)
        )
        signals.append(vol_sig)
        
        # Volume analysis
        vol_anom = self.volume_detector.get_volume_signal(
            features.get("volume_spike", 1.0),
            features.get("momentum", 0)
        )
        signals.append(vol_anom)
        
        # Sentiment (if available)
        if external_sentiment is not None:
            sent_sig = self.sentiment_fusion.get_sentiment_signal(external_sentiment)
            signals.append(sent_sig)
        
        # Calculate weighted fusion
        total_strength = 0.0
        total_confidence = 0.0
        for sig in signals:
            total_strength += sig.strength * sig.confidence
            total_confidence += sig.confidence
        
        fused_strength = total_strength / total_confidence if total_confidence > 0 else 0.0
        fused_strength = max(-1.0, min(1.0, fused_strength))  # Clamp to [-1, 1]
        
        # Consensus: how much do signals agree?
        disagreement = sum(abs(s.strength) * s.confidence for s in signals) / (total_confidence + 1e-9)
        consensus_confidence = 1.0 - min(disagreement / 2, 1.0)
        
        # Narrative explanation
        bullish_signals = [s for s in signals if s.strength > 0.3]
        bearish_signals = [s for s in signals if s.strength < -0.3]
        
        if bullish_signals and not bearish_signals:
            narrative = f"Strong bullish convergence: {', '.join([s.description for s in bullish_signals[:2]])}"
        elif bearish_signals and not bullish_signals:
            narrative = f"Strong bearish convergence: {', '.join([s.description for s in bearish_signals[:2]])}"
        elif bullish_signals and bearish_signals:
            narrative = "Mixed signals - conflicting technical and sentiment readings suggest caution"
        else:
            narrative = "No clear directional edge - remain in defensive mode"
        
        return {
            "fused_strength": round(fused_strength, 4),
            "consensus_confidence": round(consensus_confidence, 4),
            "signals": [self._signal_to_dict(s) for s in signals],
            "narrative": narrative,
            "signal_count": len(signals),
        }
    
    def _signal_to_dict(self, sig: SignalStrength) -> dict:
        """Convert SignalStrength to dict."""
        return {
            "type": sig.type.value,
            "strength": round(sig.strength, 4),
            "confidence": round(sig.confidence, 4),
            "description": sig.description,
        }

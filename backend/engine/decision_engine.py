from __future__ import annotations
from typing import Any


class DecisionEngine:
    """Enhanced decision engine with explainability and reasoning."""

    def decide(
        self,
        sentiment_score: float,
        technical_score: float,
        prob_up: float,
        technical_signals: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make trading decision with full explainability.
        
        Args:
            sentiment_score: Market sentiment (-1 to 1)
            technical_score: Technical analysis score (-1 to 1)
            prob_up: ML model probability of price increase (0 to 1)
            technical_signals: Dict with RSI, MACD, EMA signals for reasoning
            
        Returns:
            Decision dict with action, confidence, reasoning, components
        """
        # ─── Component Scoring ───────────────────────────────────────
        sentiment_component = sentiment_score * 0.25
        technical_component = technical_score * 0.25
        ml_component = ((prob_up - 0.5) * 2.0) * 0.50
        score = sentiment_component + technical_component + ml_component
        confidence = min(1.0, abs(score))

        # ─── Decision Logic ──────────────────────────────────────────
        reasoning: list[str] = []
        action = "HOLD"
        
        prob_down = 1.0 - prob_up
        technical_signals = technical_signals or {}

        # Signal Hierarchy Enforcement
        # 🟢 Tier A (mandatory)
        ema_above = technical_signals.get("price_above_ema20", False)
        macd_histogram = technical_signals.get("macd_histogram", 0.0)
        
        trend_bullish = ema_above
        trend_bearish = not ema_above
        
        momentum_bullish = macd_histogram > 0
        momentum_bearish = macd_histogram < 0
        
        # 🟡 Tier B (support)
        rsi = technical_signals.get("rsi", 50)
        ml_bullish = prob_up > 0.53
        ml_bearish = prob_down > 0.53
        ml_neutral_bullish = prob_up >= 0.505
        ml_neutral_bearish = prob_down >= 0.505
        
        # Hard market trend filter — block BUY when both EMA + MACD bearish
        block_buy = trend_bearish and momentum_bearish
        block_sell = trend_bullish and momentum_bullish

        # Count confluence signals
        confirm_buy = sum([trend_bullish, momentum_bullish, ml_bullish])
        confirm_sell = sum([trend_bearish, momentum_bearish, ml_bearish])

        # ─── 3-Tier Classification ─────────────────────────────────────
        trade_type = "HOLD"
        position_multiplier = 0.0

        # 🟢 STRONG TRADE: >=2 confluence signals, no hard block
        if confirm_buy >= 2 and not block_buy:
            action = "BUY"
            trade_type = "STRONG"
            position_multiplier = 1.0
            confidence = max(confidence, prob_up, 0.80 if confirm_buy >= 3 else 0.74)
            reasoning.append("STRONG BUY: full confluence")
            if ml_bullish:
                reasoning.append(f"ML confirms ({prob_up:.1%})")
            if trend_bullish:
                reasoning.append("Trend confirms")
            if momentum_bullish:
                reasoning.append("Momentum confirms")
            if not ml_bullish and trend_bullish:
                confidence -= 0.1
                reasoning.append("ML conflicts with trend (confidence penalty)")
                
        elif confirm_sell >= 2 and not block_sell:
            action = "SELL"
            trade_type = "STRONG"
            position_multiplier = 1.0
            confidence = max(confidence, prob_down, 0.80 if confirm_sell >= 3 else 0.74)
            reasoning.append("STRONG SELL: full confluence")
            if ml_bearish:
                reasoning.append(f"ML confirms ({prob_down:.1%})")
            if trend_bearish:
                reasoning.append("Trend confirms")
            if momentum_bearish:
                reasoning.append("Momentum confirms")
            if not ml_bearish and trend_bearish:
                confidence -= 0.1
                reasoning.append("ML conflicts with trend (confidence penalty)")

        # 🟡 WEAK TRADE: 1 signal + ML neutral, no hard contradiction
        elif confirm_buy >= 1 and not block_buy and ml_neutral_bullish:
            action = "BUY"
            trade_type = "WEAK"
            position_multiplier = 0.5
            confidence = max(confidence * 0.75, prob_up * 0.82, 0.64)
            reasoning.append("WEAK BUY: single signal + ML neutral-bullish")
            if trend_bullish:
                reasoning.append("Trend supports")
            if momentum_bullish:
                reasoning.append("Momentum supports")
            reasoning.append(f"ML neutral-bullish ({prob_up:.1%})")

        elif confirm_sell >= 1 and not block_sell and ml_neutral_bearish:
            action = "SELL"
            trade_type = "WEAK"
            position_multiplier = 0.5
            confidence = max(confidence * 0.75, prob_down * 0.82, 0.64)
            reasoning.append("WEAK SELL: single signal + ML neutral-bearish")
            if trend_bearish:
                reasoning.append("Trend supports")
            if momentum_bearish:
                reasoning.append("Momentum supports")
            reasoning.append(f"ML neutral-bearish ({prob_down:.1%})")

        # ⚪ HOLD: no valid entry
        else:
            reasoning.append("No valid entry signal (HOLD)")

        # ─── Support Signal Modifiers (RSI & Sentiment) ──────────────────────────────
        # RSI signals MUST NOT independently trigger trades.
        if rsi < 30:
            if action == "BUY":
                confidence += 0.05
                reasoning.append(f"RSI oversold support ({rsi:.0f})")
            elif action == "HOLD":
                reasoning.append(f"RSI oversold but no trend confluence")
        elif rsi > 70:
            if action == "SELL":
                confidence += 0.05
                reasoning.append(f"RSI overbought support ({rsi:.0f})")
            elif action == "HOLD":
                reasoning.append(f"RSI overbought but no trend confluence")

        # Sentiment Reasoning
        if sentiment_score > 0.3:
            if action == "BUY":
                confidence += 0.02
                reasoning.append(f"Positive sentiment support ({sentiment_score:.2f})")
        elif sentiment_score < -0.3:
            if action == "SELL":
                confidence += 0.02
                reasoning.append(f"Negative sentiment support ({sentiment_score:.2f})")

        # ─── Cap confidence ────────────────────────────────────────────
        confidence = min(1.0, max(0.0, confidence))

        # ─── ENFORCE CONFIDENCE-TRADE_TYPE INVARIANT ─────────────────────────
        # PATCH B: Confidence thresholds per trade classification
        # STRONG trades must have confidence >= 0.55
        if trade_type == "STRONG" and confidence < 0.55:
            trade_type = "WEAK"
            position_multiplier = 0.5
            reasoning.append(f"[PATCH] Downgraded STRONG→WEAK: confidence {confidence:.2f} < 0.55 threshold")
        # WEAK trades must have confidence >= 0.30
        elif trade_type == "WEAK" and confidence < 0.30:
            trade_type = "HOLD"
            position_multiplier = 0.0
            action = "HOLD"
            reasoning.append(f"[PATCH] Downgraded WEAK→HOLD: confidence {confidence:.2f} < 0.30 threshold")

        return {
            "action": action,
            "trade_type": trade_type,
            "position_multiplier": position_multiplier,
            "confidence": round(confidence, 4),
            "score": round(score, 4),
            "reasoning": reasoning,
            "components": {
                "ml_component": round(ml_component, 4),
                "technical_component": round(technical_component, 4),
                "sentiment_component": round(sentiment_component, 4),
            },
            "signals": technical_signals or {},
        }

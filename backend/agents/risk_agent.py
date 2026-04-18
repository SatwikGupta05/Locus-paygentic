from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VolatilityRegime(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


REGIME_SCALING: dict[VolatilityRegime, float] = {
    VolatilityRegime.LOW: 1.2,
    VolatilityRegime.NORMAL: 1.0,
    VolatilityRegime.HIGH: 0.5,
    VolatilityRegime.EXTREME: 0.2,
}


@dataclass(slots=True)
class RiskVerdict:
    approved: bool
    reason: str
    position_size: float
    risk_budget: float
    stop_distance: float
    volatility_penalty: float
    volatility_regime: VolatilityRegime
    regime_scaling: float
    circuit_breaker_active: bool
    adjustments: dict[str, Any]


class CircuitBreaker:
    """Halts trading after consecutive losses exceed threshold."""

    def __init__(self, max_consecutive_losses: int = 5) -> None:
        self.max_consecutive_losses = max_consecutive_losses
        self._consecutive_losses = 0
        self._active = False
        self._total_trips = 0

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def consecutive_losses(self) -> int:
        return self._consecutive_losses

    def record_outcome(self, pnl: float) -> None:
        if pnl <= 0:
            self._consecutive_losses += 1
            if self._consecutive_losses >= self.max_consecutive_losses:
                self._active = True
                self._total_trips += 1
        else:
            self._consecutive_losses = 0

    def reset(self) -> None:
        self._active = False
        self._consecutive_losses = 0

    def status(self) -> dict[str, Any]:
        return {
            "active": self._active,
            "consecutive_losses": self._consecutive_losses,
            "threshold": self.max_consecutive_losses,
            "total_trips": self._total_trips,
        }


class RiskAgent:
    def __init__(self, max_consecutive_losses: int = 5) -> None:
        self.circuit_breaker = CircuitBreaker(max_consecutive_losses)

    @staticmethod
    def classify_volatility(volatility: float, atr: float, price: float) -> VolatilityRegime:
        atr_pct = atr / max(price, 1e-9)
        combined = volatility * 0.6 + atr_pct * 0.4

        if combined > 0.06:
            return VolatilityRegime.EXTREME
        if combined > 0.035:
            return VolatilityRegime.HIGH
        if combined > 0.012:
            return VolatilityRegime.NORMAL
        return VolatilityRegime.LOW

    def pre_trade_check(
        self,
        balance: float,
        price: float,
        atr: float,
        volatility: float,
        drawdown_pct: float,
        daily_pnl: float,
        max_drawdown_pct: float,
        max_daily_loss_pct: float,
        starting_balance: float,
        trade_type: str = "STRONG",
    ) -> tuple[bool, str]:
        """Validate whether trading should proceed at all."""
        if self.circuit_breaker.is_active:
            return False, "circuit_breaker_tripped"
        if drawdown_pct >= max_drawdown_pct:
            return False, "max_drawdown_exceeded"
        if abs(daily_pnl) >= starting_balance * max_daily_loss_pct:
            return False, "max_daily_loss_exceeded"

        regime = self.classify_volatility(volatility, atr, price)
        if regime == VolatilityRegime.EXTREME and balance < starting_balance * 0.5:
            return False, "extreme_volatility_low_capital"

        # WEAK trades are blocked in EXTREME volatility
        if trade_type == "WEAK" and regime == VolatilityRegime.EXTREME:
            return False, "weak_trade_blocked_extreme_volatility"

        return True, "approved"

    def calculate_position_size(
        self,
        balance: float,
        price: float,
        atr: float,
        volatility: float,
        max_capital_fraction: float,
        risk_fraction: float,
        atr_risk_multiplier: float,
        max_symbol_exposure_pct: float,
        confidence: float = 0.5,
        position_multiplier: float = 1.0,
    ) -> RiskVerdict:
        regime = self.classify_volatility(volatility, atr, price)
        regime_scale = REGIME_SCALING[regime]

        max_trade_value = balance * min(max_capital_fraction, max_symbol_exposure_pct)
        atr_floor = max(atr, price * 0.0025)
        stop_distance = atr_floor * atr_risk_multiplier
        risk_budget = balance * risk_fraction
        risk_size = risk_budget / max(stop_distance, 1e-9)
        cap_size = max_trade_value / max(price, 1e-9)
        volatility_penalty = max(0.20, 1 - min(volatility * 20, 0.8))

        raw_size = min(risk_size, cap_size) * volatility_penalty
        
        # Apply confidence-based scaling (0.3 to 1.2x)
        confidence_scale = 0.3 + (confidence * 0.9)  # Range: 0.3 to 1.2
        
        # Apply trade_type position_multiplier (STRONG=1.0, WEAK=0.5)
        adjusted_size = raw_size * regime_scale * confidence_scale * position_multiplier
        position_size = round(max(adjusted_size, 0.0), 6)

        adjustments: dict[str, Any] = {}
        if regime_scale < 1.0:
            adjustments["regime_reduction"] = f"{(1 - regime_scale) * 100:.0f}% size reduction due to {regime.value} volatility"
        if confidence_scale != 1.0:
            confidence_pct = (confidence_scale - 1.0) * 100
            adjustments["confidence_scaling"] = f"{confidence_pct:+.0f}% size adjustment based on confidence ({confidence:.2f})"
        if self.circuit_breaker.consecutive_losses > 0:
            adjustments["loss_streak"] = f"{self.circuit_breaker.consecutive_losses} consecutive losses"

        return RiskVerdict(
            approved=position_size > 0 and not self.circuit_breaker.is_active,
            reason="approved" if not self.circuit_breaker.is_active else "circuit_breaker_tripped",
            position_size=position_size,
            risk_budget=round(risk_budget, 2),
            stop_distance=round(stop_distance, 4),
            volatility_penalty=round(volatility_penalty, 4),
            volatility_regime=regime,
            regime_scaling=regime_scale,
            circuit_breaker_active=self.circuit_breaker.is_active,
            adjustments=adjustments,
        )

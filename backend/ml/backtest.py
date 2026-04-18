from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json
import logging

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd
import numpy as np
from backend.ml.predictor import Predictor
from backend.data.feature_engineering import FeatureEngineering
from backend.utils.config import get_settings


logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Represents a single trade or position state."""
    timestamp: str
    action: str  # BUY, SELL, HOLD
    price: float
    size: float
    cash: float
    equity: float
    pnl: Optional[float] = None
    reasoning: str = ""


class BacktestEngine:
    """
    Proper backtesting simulation engine with comprehensive metrics tracking.
    Replaces ad-hoc backtesting with structured simulation.
    """
    
    def __init__(self, model_path: Path, feature_schema_path: Path, settings):
        self.predictor = Predictor(model_path, feature_schema_path)
        self.predictor.load()
        self.settings = settings
        self.feature_engineering = FeatureEngineering()
        self.fee_rate = settings.fee_bps / 10_000
        self.slippage_rate = settings.slippage_bps / 10_000
    
    def simulate(self, ohlcv: pd.DataFrame, warmup_period: int = 50) -> dict:
        """Run backtest simulation on OHLCV data."""
        
        # Initialize state
        cash = self.settings.starting_balance
        position_size = 0.0
        entry_price = 0.0
        equity_curve = []
        trade_records = []
        
        # Warmup period to build indicators
        for idx in range(warmup_period, len(ohlcv)):
            window = ohlcv.iloc[:idx + 1]
            current_price = float(window["close"].iloc[-1])
            timestamp = window["timestamp"].iloc[-1]
            
            # Generate features
            feature_vector = self.feature_engineering.generate(window, sentiment_score=0.0)
            features_df = pd.DataFrame([feature_vector.values], columns=list(feature_vector.values.keys()))
            
            # Get prediction
            prediction = self.predictor.predict(features_df)
            prob_up = prediction["prob_up"]
            signal = prediction["signal"]
            explanation = prediction["explanation"]
            
            # Trading logic
            action = "HOLD"
            if signal in ["STRONG_BUY", "BUY"] and position_size == 0:
                # Enter long position
                execution_price = current_price * (1 + self.slippage_rate)
                position_size = (cash * self.settings.max_capital_per_trade) / execution_price
                fee = position_size * execution_price * self.fee_rate
                cash -= position_size * execution_price + fee
                entry_price = execution_price
                action = "BUY"
                
                trade_records.append(TradeRecord(
                    timestamp=str(timestamp),
                    action=action,
                    price=round(execution_price, 2),
                    size=round(position_size, 6),
                    cash=round(cash, 2),
                    equity=round(cash + position_size * current_price, 2),
                    reasoning=f"{signal}: {explanation[:100]}"
                ))
            
            elif signal in ["STRONG_SELL", "SELL"] and position_size > 0:
                # Exit long position
                execution_price = current_price * (1 - self.slippage_rate)
                gross = position_size * execution_price
                fee = gross * self.fee_rate
                pnl = gross - fee - (position_size * entry_price)
                cash += gross - fee
                action = "SELL"
                
                trade_records.append(TradeRecord(
                    timestamp=str(timestamp),
                    action=action,
                    price=round(execution_price, 2),
                    size=round(position_size, 6),
                    cash=round(cash, 2),
                    equity=round(cash, 2),
                    pnl=round(pnl, 2),
                    reasoning=f"{signal}: {explanation[:100]}"
                ))
                
                position_size = 0.0
                entry_price = 0.0
            
            # Track equity
            current_equity = cash + position_size * current_price
            equity_curve.append(current_equity)
        
        # Calculate metrics
        metrics = self._calculate_metrics(equity_curve, trade_records)
        
        return {
            "equity_curve": equity_curve,
            "trades": [self._record_to_dict(r) for r in trade_records[-50:]],  # Last 50 trades
            "metrics": metrics,
            "simulation_length": len(ohlcv) - warmup_period,
        }
    
    def _calculate_metrics(self, equity_curve: list[float], trade_records: list[TradeRecord]) -> dict:
        """Calculate comprehensive backtest metrics."""
        
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        # Core metrics
        final_equity = float(equity_series.iloc[-1])
        total_return = ((final_equity - self.settings.starting_balance) / self.settings.starting_balance) * 100
        
        # Volatility and Sharpe
        annual_vol = returns.std() * np.sqrt(252) if not returns.empty else 0.0
        sharpe = (returns.mean() * 252 / annual_vol) if annual_vol > 0 else 0.0
        
        # Drawdown
        cummax = equity_series.cummax()
        drawdown = (cummax - equity_series) / cummax.replace(0, np.nan)
        max_dd = drawdown.max() if not drawdown.empty else 0.0
        
        # Win rate
        pnls = [r.pnl for r in trade_records if r.pnl is not None]
        trade_count = len([r for r in trade_records if r.action == "BUY"])
        win_count = len([p for p in pnls if p > 0])
        win_rate = (win_count / len(pnls)) if pnls else 0.0
        
        avg_pnl = np.mean(pnls) if pnls else 0.0
        avg_win = np.mean([p for p in pnls if p > 0]) if [p for p in pnls if p > 0] else 0.0
        avg_loss = np.mean([p for p in pnls if p < 0]) if [p for p in pnls if p < 0] else 0.0
        
        return {
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return, 2),
            "annual_volatility": round(annual_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown": round(max_dd, 4),
            "trade_count": trade_count,
            "closed_trades": len(pnls),
            "win_rate": round(win_rate, 4),
            "avg_pnl": round(avg_pnl, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(sum([p for p in pnls if p > 0]) / abs(sum([p for p in pnls if p < 0])), 2) if [p for p in pnls if p < 0] else 0.0,
        }
    
    def _record_to_dict(self, record: TradeRecord) -> dict:
        """Convert TradeRecord to dict for JSON serialization."""
        return {
            "timestamp": record.timestamp,
            "action": record.action,
            "price": record.price,
            "size": record.size,
            "cash": record.cash,
            "equity": record.equity,
            "pnl": record.pnl,
            "reasoning": record.reasoning,
        }


if __name__ == "__main__":
    from backend.data.historical_loader import HistoricalLoader
    
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    
    # Load data
    loader = HistoricalLoader(settings.historical_data_path)
    ohlcv = loader.load()
    
    # Run backtest
    engine = BacktestEngine(settings.model_path, settings.feature_schema_path, settings)
    results = engine.simulate(ohlcv)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"BACKTEST SIMULATION RESULTS")
    print(f"{'='*60}")
    for key, value in results["metrics"].items():
        print(f"{key:.<20} {value}")
    print(f"{'='*60}\n")

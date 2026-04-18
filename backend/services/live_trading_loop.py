"""
AURORA Live Trading Loop
========================

Clean, continuous trading loop that runs the full system.
This is the "heartbeat" of Aurora - demo-ready.

Usage:
    loop = LiveTradingLoop()
    loop.run(duration_minutes=30)  # Run for 30 minutes
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from backend.execution.exchange_failover_service import get_exchange_service
from backend.ml.predictor import Predictor
from backend.ml.agent_memory import AgentMemory, TradeMemory
from backend.ml.agent_narrative import AgentNarrativeGenerator
from backend.data.feature_engineering import FeatureEngineering
from backend.utils.config import get_settings

logger = logging.getLogger(__name__)


class LiveTradingLoop:
    """
    Main trading loop for Aurora.
    
    Cycle (every iteration):
    1. Fetch market data
    2. Generate features
    3. Get model prediction
    4. Make agent decision
    5. Execute trade
    6. Update memory
    7. Sleep for next cycle
    """
    
    def __init__(self, symbol: str = "BTC/USDT", timeframe: str = "5m", 
                 interval_seconds: int = 60):
        """
        Initialize trading loop.
        
        Args:
            symbol: Trading pair
            timeframe: Candle period for data
            interval_seconds: How often to run cycle (60s = check every minute)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.interval_seconds = interval_seconds
        
        # Components
        self.settings = get_settings()
        self.exchange = get_exchange_service()
        self.predictor = Predictor(
            self.settings.model_path,
            self.settings.feature_schema_path
        )
        self.feature_eng = FeatureEngineering()
        self.agent_memory = AgentMemory(max_history=100)
        self.narrative_gen = AgentNarrativeGenerator()
        
        # State
        self.running = False
        self.cycle_count = 0
        self.current_position: Optional[TradeMemory] = None
        self.portfolio_value = self.settings.starting_balance
        self.last_price = 0.0
        
        logger.info(
            f"[AURORA] Trading loop initialized: {symbol} @ {timeframe} "
            f"(interval: {interval_seconds}s)"
        )
    
    def run(self, duration_minutes: int = 30) -> None:
        """
        Run the trading loop for specified duration.
        
        Args:
            duration_minutes: How long to run (0 = infinite)
        """
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes) if duration_minutes > 0 else None
        
        logger.info(
            f"[AURORA] Starting live trading loop - "
            f"running for {duration_minutes} minutes" if duration_minutes > 0 
            else "[AURORA] Starting live trading loop - running indefinitely"
        )
        
        self.running = True
        
        try:
            while self.running:
                # Check if time limit reached
                if end_time and datetime.utcnow() > end_time:
                    logger.info("[AURORA] Duration limit reached - stopping loop")
                    break
                
                # Run one cycle
                try:
                    self._trading_cycle()
                except Exception as e:
                    logger.error(f"[AURORA] Cycle error: {e}", exc_info=True)
                
                self.cycle_count += 1
                
                # Sleep until next cycle
                logger.debug(
                    f"[AURORA] Cycle {self.cycle_count} complete - sleeping {self.interval_seconds}s"
                )
                time.sleep(self.interval_seconds)
        
        except KeyboardInterrupt:
            logger.info("[AURORA] Trading loop interrupted by user")
        
        finally:
            self._print_final_report()
            self.running = False
    
    def stop(self) -> None:
        """Stop the trading loop (safe shutdown)."""
        logger.info("[AURORA] Stopping trading loop")
        self.running = False
    
    def _trading_cycle(self) -> None:
        """Execute one full trading cycle."""
        
        # STEP 1: Fetch market data
        logger.debug(f"[CYCLE {self.cycle_count}] Fetching market data...")
        ohlcv_df = self.exchange.get_ohlcv_as_dataframe(
            self.symbol, 
            self.timeframe, 
            limit=100
        )
        
        if ohlcv_df is None or len(ohlcv_df) < 50:
            logger.warning("[CYCLE] Insufficient data fetched, skipping cycle")
            return
        
        logger.debug(f"[CYCLE {self.cycle_count}] Got {len(ohlcv_df)} candles")
        
        # STEP 2: Generate features from latest candle
        latest_row = ohlcv_df.iloc[-1]
        self.last_price = float(latest_row["close"])
        
        # Create feature window
        feature_window = pd.DataFrame(ohlcv_df)  # Use all historical data for feature generation
        feature_vector = self.feature_eng.generate(feature_window, sentiment_score=0.0)
        
        logger.debug(f"[CYCLE {self.cycle_count}] Got features for {self.symbol} @ {self.last_price:.2f}")
        
        # STEP 3: Get model prediction
        prediction = self.predictor.predict(feature_vector.values)
        prob_up = prediction["prob_up"]
        confidence = prediction["confidence"]
        signal = prediction["signal"]
        explanation = prediction["explanation"]
        
        logger.debug(
            f"[CYCLE {self.cycle_count}] Prediction: {signal} "
            f"({prob_up*100:.1f}% prob_up, confidence: {confidence:.2f})"
        )
        
        # STEP 4: Make agent decision (with memory-based risk adaptation)
        decision = self._make_decision(
            signal=signal,
            prob_up=prob_up,
            volatility=feature_vector.values.get("volatility", 0.02),
            explanation=explanation
        )
        
        # STEP 5: Execute trade if signal
        if decision["action"] != "HOLD":
            self._execute_trade(decision)
        
        # STEP 6: Update portfolio value (mark-to-market)
        if self.current_position:
            position_value = self.current_position.entry_price * 1.0  # Simplified
            current_value = self.last_price * 1.0
            self.portfolio_value = (self.portfolio_value - position_value) + current_value
        
        self.agent_memory.update_equity(self.portfolio_value)
        
        # STEP 7: Log cycle complete
        logger.info(
            f"[CYCLE {self.cycle_count}] {self.symbol} @ {self.last_price:.2f} | "
            f"Signal: {signal:12} | Portfolio: ${self.portfolio_value:.2f}"
        )
    
    def _make_decision(self, signal: str, prob_up: float, volatility: float,
                       explanation: str) -> dict:
        """
        Make trading decision based on model signal and memory adaptation.
        
        Returns:
            Decision dict with action and reasoning
        """
        
        # Apply memory-based risk adaptation
        adjusted_prob = prob_up * self.agent_memory.confidence_factor
        adjusted_size = self.agent_memory.risk_level
        
        # Determine action
        action = "HOLD"
        reasoning = ""
        
        if adjusted_prob > 0.65 and self.current_position is None:
            action = "BUY"
            reasoning = (
                f"High confidence breakout (adj: {adjusted_prob:.2%}). "
                f"Risk: {adjusted_size:.1f}x. {explanation[:60]}"
            )
        elif adjusted_prob < 0.35 and self.current_position is not None:
            action = "SELL"
            reasoning = (
                f"Exit signal confirmed (adj: {adjusted_prob:.2%}). "
                f"{explanation[:60]}"
            )
        else:
            reasoning = f"Neutral signal. Risk: {adjusted_size:.1f}x"
        
        return {
            "action": action,
            "reasoning": reasoning,
            "adjusted_prob": adjusted_prob,
            "adjusted_size": adjusted_size,
        }
    
    def _execute_trade(self, decision: dict) -> None:
        """Execute a trade based on decision."""
        
        action = decision["action"]
        
        if action == "BUY" and self.current_position is None:
            # Enter long position
            self.current_position = self.agent_memory.record_trade(
                symbol=self.symbol,
                action="BUY",
                entry_price=self.last_price,
                reason=decision["reasoning"]
            )
            logger.info(
                f"[TRADE] BUY {self.symbol} @ {self.last_price:.2f} - "
                f"{decision['reasoning']}"
            )
        
        elif action == "SELL" and self.current_position is not None:
            # Exit long position
            pnl = self.agent_memory.close_trade(
                self.current_position,
                self.last_price,
                decision["reasoning"]
            )
            logger.info(
                f"[TRADE] SELL {self.symbol} @ {self.last_price:.2f} - "
                f"PnL: ${pnl:.2f} ({(pnl/self.current_position.entry_price)*100:.2f}%) - "
                f"{decision['reasoning']}"
            )
            self.current_position = None
            self.portfolio_value += pnl
    
    def get_status_report(self) -> str:
        """Get comprehensive status for display."""
        
        memory_status = self.agent_memory.get_memory_status()
        
        report = "\n" + "="*70
        report += "\n🤖 AURORA LIVE TRADING LOOP STATUS\n"
        report += "="*70 + "\n"
        
        report += f"System Status:\n"
        report += f"  Cycles Run: {self.cycle_count}\n"
        report += f"  Active Symbol: {self.symbol}\n"
        report += f"  Latest Price: ${self.last_price:.2f}\n"
        report += f"  Current Position: {'OPEN' if self.current_position else 'CLOSED'}\n"
        report += f"  Portfolio Value: ${self.portfolio_value:.2f}\n\n"
        
        report += f"Memory Status:\n"
        report += f"  Total Trades: {memory_status['total_trades']}\n"
        report += f"  Win Rate: {memory_status['win_rate']*100:.1f}%\n"
        report += f"  Total PnL: ${memory_status['total_pnl']:.2f}\n"
        report += f"  Drawdown: {memory_status['drawdown']*100:.2f}%\n"
        report += f"  Risk Level: {memory_status['risk_level']:.2f}x "
        
        if memory_status['risk_level'] < 1.0:
            report += "(CAUTIOUS)"
        elif memory_status['risk_level'] > 1.0:
            report += "(AGGRESSIVE)"
        else:
            report += "(NORMAL)"
        
        report += f"\n  Streak: {memory_status['consecutive_wins']}W "
        report += f"{memory_status['consecutive_losses']}L\n"
        
        report += "\n" + "="*70 + "\n"
        return report
    
    def _print_final_report(self) -> None:
        """Print final report when loop ends."""
        
        logger.info("\n" + "="*70)
        logger.info("🤖 AURORA TRADING LOOP - FINAL REPORT")
        logger.info("="*70)
        
        memory_status = self.agent_memory.get_memory_status()
        
        logger.info(f"\nCycles Executed: {self.cycle_count}")
        logger.info(f"Total Trades: {memory_status['total_trades']}")
        logger.info(f"Closed Trades: {memory_status['closed_trades']}")
        logger.info(f"Win Rate: {memory_status['win_rate']*100:.1f}%")
        logger.info(f"Total PnL: ${memory_status['total_pnl']:.2f}")
        logger.info(f"Final Portfolio: ${self.portfolio_value:.2f}")
        logger.info(f"Drawdown: {memory_status['drawdown']*100:.2f}%")
        logger.info("="*70 + "\n")

"""
AURORA Agent Memory System
==========================

Tracks agent performance, adapts risk based on recent results.
This is what makes Aurora "intelligent" vs just "automated".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class TradeMemory:
    """Single trade record for agent memory."""
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL
    entry_price: float
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    reason: str = ""
    
    @property
    def is_closed(self) -> bool:
        """Whether this trade is closed."""
        return self.exit_price is not None
    
    def close(self, exit_price: float, reason: str = "") -> None:
        """Close the trade."""
        self.exit_price = exit_price
        self.exit_timestamp = datetime.utcnow()
        self.pnl = exit_price - self.entry_price
        self.pnl_percent = (self.pnl / self.entry_price) * 100
        if reason:
            self.reason = reason


class AgentMemory:
    """
    Agent memory system tracks performance and adapts risk.
    
    Tracks:
    - Recent trades (FIFO queue, max 50)
    - Current drawdown from peak equity
    - Win/loss streak
    - Confidence trend
    - Risk level (dynamic)
    
    Adaptation:
    - After 3 losses: reduce position size
    - High drawdown: reduce risk
    - Winning streak: increase confidence
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize agent memory.
        
        Args:
            max_history: Max trades to remember (older ones dropped)
        """
        self.trades: deque[TradeMemory] = deque(maxlen=max_history)
        self.equity_history: list[float] = [10000.0]  # Starting balance
        self.peak_equity: float = 10000.0
        self.timestamps: deque[datetime] = deque(maxlen=max_history)
        
        # Adapting parameters
        self.risk_level: float = 1.0  # Multiplier on position size
        self.consecutive_losses: int = 0
        self.consecutive_wins: int = 0
        self.confidence_factor: float = 1.0  # How much to trust the model
        
    def record_trade(self, symbol: str, action: str, entry_price: float, 
                     reason: str = "") -> TradeMemory:
        """
        Record a new trade.
        
        Args:
            symbol: Trading pair
            action: BUY or SELL
            entry_price: Entry price
            reason: Why the trade was taken
        
        Returns:
            TradeMemory object for later closing
        """
        trade = TradeMemory(
            timestamp=datetime.utcnow(),
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            reason=reason
        )
        self.trades.append(trade)
        self.timestamps.append(trade.timestamp)
        
        logger.debug(f"[MEMORY] Recorded {action} on {symbol} @ {entry_price}")
        return trade
    
    def close_trade(self, trade: TradeMemory, exit_price: float, reason: str = "") -> float:
        """
        Close a trade and update memory.
        
        Args:
            trade: TradeMemory object to close
            exit_price: Exit price
            reason: Why trade was closed
        
        Returns:
            PnL from this trade
        """
        trade.close(exit_price, reason)
        
        # Update streak tracking
        if trade.pnl and trade.pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif trade.pnl and trade.pnl < 0:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Adapt risk based on recent performance
        self._adapt_risk()
        
        logger.info(
            f"[MEMORY] Closed trade: {trade.symbol} {trade.action} "
            f"PnL: ${trade.pnl:.2f} ({trade.pnl_percent:.2f}%)"
        )
        
        return trade.pnl
    
    def _adapt_risk(self) -> None:
        """
        Dynamically adapt risk level based on recent performance.
        This is what makes Aurora "intelligent".
        """
        
        # Rule 1: After 3+ consecutive losses, reduce risk
        if self.consecutive_losses >= 3:
            self.risk_level = max(0.5, self.risk_level * 0.8)  # Reduce by 20%, min 50%
            logger.warning(
                f"[MEMORY] 3 consecutive losses detected. Risk reduced to {self.risk_level:.2f}x"
            )
        
        # Rule 2: After 3+ consecutive wins, increase confidence
        elif self.consecutive_wins >= 3:
            self.risk_level = min(1.5, self.risk_level * 1.1)  # Increase by 10%, max 150%
            self.confidence_factor = min(1.3, self.confidence_factor * 1.05)
            logger.info(
                f"[MEMORY] 3 consecutive wins! Risk increased to {self.risk_level:.2f}x, "
                f"confidence to {self.confidence_factor:.2f}x"
            )
        
        # Rule 3: Check drawdown
        current_equity = self.equity_history[-1] if self.equity_history else 10000.0
        drawdown = (self.peak_equity - current_equity) / self.peak_equity if self.peak_equity > 0 else 0
        
        if drawdown > 0.15:  # >15% drawdown
            self.risk_level = max(0.5, self.risk_level * 0.9)  # Reduce by 10%
            logger.warning(
                f"[MEMORY] High drawdown ({drawdown:.2%}). Risk reduced to {self.risk_level:.2f}x"
            )
        
        # Rule 4: Recovery mode after high losses
        if drawdown < 0.05 and self.consecutive_losses == 0:  # <5% drawdown + no recent losses
            self.risk_level = min(1.0, self.risk_level * 1.05)  # Slowly recover to baseline
            self.confidence_factor = max(1.0, self.confidence_factor * 0.95)  # Reduce excess confidence
    
    def update_equity(self, new_equity: float) -> None:
        """
        Update current equity (call after each trade or time period).
        
        Args:
            new_equity: Current portfolio equity
        """
        self.equity_history.append(new_equity)
        
        # Track peak for drawdown calculation
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity
    
    def get_drawdown(self) -> float:
        """Get current drawdown from peak equity."""
        if not self.equity_history or self.peak_equity <= 0:
            return 0.0
        
        current = self.equity_history[-1]
        return (self.peak_equity - current) / self.peak_equity
    
    def get_win_rate(self) -> float:
        """Calculate win rate from recent trades."""
        if not self.trades:
            return 0.5  # Neutral
        
        closed_trades = [t for t in self.trades if t.is_closed]
        if not closed_trades:
            return 0.5
        
        wins = len([t for t in closed_trades if t.pnl and t.pnl > 0])
        return wins / len(closed_trades)
    
    def get_recent_trades(self, limit: int = 5) -> list[TradeMemory]:
        """Get most recent N trades."""
        return list(self.trades)[-limit:]
    
    def get_total_pnl(self) -> float:
        """Get total PnL from all trades."""
        closed_trades = [t for t in self.trades if t.is_closed]
        return sum(t.pnl for t in closed_trades if t.pnl)
    
    def get_memory_status(self) -> dict[str, any]:
        """Get comprehensive memory status for display."""
        closed_trades = [t for t in self.trades if t.is_closed]
        current_equity = self.equity_history[-1] if self.equity_history else 10000.0
        
        return {
            "total_trades": len(self.trades),
            "closed_trades": len(closed_trades),
            "open_trades": len(self.trades) - len(closed_trades),
            "win_rate": round(self.get_win_rate(), 3),
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "total_pnl": round(self.get_total_pnl(), 2),
            "current_equity": round(current_equity, 2),
            "peak_equity": round(self.peak_equity, 2),
            "drawdown": round(self.get_drawdown(), 4),
            "risk_level": round(self.risk_level, 2),
            "confidence_factor": round(self.confidence_factor, 2),
            "recent_trades": [
                {
                    "symbol": t.symbol,
                    "action": t.action,
                    "entry": round(t.entry_price, 2),
                    "exit": round(t.exit_price, 2) if t.exit_price else None,
                    "pnl": round(t.pnl, 2) if t.pnl else None,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in self.get_recent_trades(5)
            ]
        }
    
    def format_memory_report(self) -> str:
        """Format memory status as readable report."""
        status = self.get_memory_status()
        
        report = "\n" + "="*70
        report += "\n🧠 AURORA AGENT MEMORY STATUS\n"
        report += "="*70 + "\n"
        
        report += f"Performance:\n"
        report += f"  Total Trades: {status['total_trades']}\n"
        report += f"  Closed Trades: {status['closed_trades']}\n"
        report += f"  Open Trades: {status['open_trades']}\n"
        report += f"  Win Rate: {status['win_rate']*100:.1f}%\n"
        report += f"  Total PnL: ${status['total_pnl']:.2f}\n\n"
        
        report += f"Streak:\n"
        wins_str = "🟢 " + "W"*status['consecutive_wins'] if status['consecutive_wins'] > 0 else ""
        losses_str = "🔴 " + "L"*status['consecutive_losses'] if status['consecutive_losses'] > 0 else ""
        report += f"  {wins_str}{losses_str}\n\n"
        
        report += f"Equity:\n"
        report += f"  Current: ${status['current_equity']:.2f}\n"
        report += f"  Peak: ${status['peak_equity']:.2f}\n"
        report += f"  Drawdown: {status['drawdown']*100:.2f}%\n\n"
        
        report += f"Adaptation:\n"
        report += f"  Risk Level: {status['risk_level']:.2f}x "
        if status['risk_level'] < 1.0:
            report += "(reduced - cautious)"
        elif status['risk_level'] > 1.0:
            report += "(increased - aggressive)"
        else:
            report += "(baseline)"
        report += f"\n  Confidence: {status['confidence_factor']:.2f}x\n\n"
        
        report += f"Recent Trades:\n"
        for t in status['recent_trades']:
            pnl_str = f"${t['pnl']:.2f}" if t['pnl'] else "OPEN"
            report += f"  {t['timestamp'][:19]}: {t['action']:4} {t['symbol']:9} "
            report += f"@ {t['entry']:.2f} → {pnl_str}\n"
        
        report += "="*70 + "\n"
        return report

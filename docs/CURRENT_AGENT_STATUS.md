# Current Agent Status - Codebase Analysis

**Date:** April 17, 2026  
**Status:** Production-ready multi-agent system (but NO pre-defined templates yet)

---

## 🤖 Existing Agent Components

### Currently Implemented: 3 Core Agents

#### 1. **ScoutAgent** (Sentiment Analysis)
- **Location:** `backend/agents/scout_agent.py`
- **Purpose:** Analyzes news sentiment from RSS feeds
- **Capabilities:**
  - Fetches RSS headlines
  - Counts positive terms: surge, rally, approval, growth, adoption, bull, inflow, breakout
  - Counts negative terms: hack, lawsuit, crash, liquidation, ban, bear, outflow, fear
  - Produces sentiment score: -1.0 to +1.0
  - Fallback: Uses recent price return if no news available
- **Output Format:**
  ```python
  {
    "sentiment_score": float,  # -1.0 to 1.0
    "source": str,             # "rss" or "fallback"
    "symbol": str              # e.g., "BTC/USD"
  }
  ```

#### 2. **AnalystAgent** (Technical Analysis)
- **Location:** `backend/agents/analyst_agent.py`
- **Purpose:** Scores technical indicators
- **Capabilities:**
  - RSI (14-period): +0.35 if <35, -0.35 if >65
  - MACD Histogram: +0.25 if positive, -0.25 if negative
  - Momentum (10-period): +0.20 if positive, -0.20 if negative
  - EMA Gap (12/26): +0.20 if fast > slow, -0.20 if slow > fast
  - Signal classification: BULLISH / BEARISH / NEUTRAL
- **Output Format:**
  ```python
  {
    "technical_score": float,  # -1.0 to 1.0
    "signal": str              # "BULLISH", "BEARISH", "NEUTRAL"
  }
  ```

#### 3. **RiskAgent** (Risk Management)
- **Location:** `backend/agents/risk_agent.py`
- **Purpose:** Validates trades and manages risk
- **Capabilities:**
  - **Volatility Classification:**
    - LOW: ATR+Vol < 0.012 (1.2x position multiplier)
    - NORMAL: 0.012-0.035 (1.0x position multiplier)
    - HIGH: 0.035-0.06 (0.5x position multiplier)
    - EXTREME: > 0.06 (0.2x position multiplier)
  - **Circuit Breaker:** Stops trading after N consecutive losses
  - **Pre-Trade Checks:**
    - Max drawdown validation (15% default)
    - Daily loss limit (5% default)
    - Volatility-based trade type blocking
  - **Position Sizing:** Dynamic based on ATR, volatility, confidence
- **Output Format:**
  ```python
  RiskVerdict(
    approved: bool,
    reason: str,
    position_size: float,
    risk_budget: float,
    volatility_regime: str,
    circuit_breaker_active: bool,
    ...
  )
  ```

#### 4. **ReputationTracker** (Optional - Blockchain)
- **Location:** `backend/agents/reputation.py`
- **Purpose:** Tracks agent performance metrics
- **Metrics:**
  - Win rate, profit factor, Sharpe ratio
  - Max drawdown, cumulative P&L
  - Trade count, average winning/losing trades

---

## ⚙️ How Agents Work Together

### Decision Pipeline (10 Stages)

```
1. FETCHING_DATA
   ↓
2. COMPUTING_FEATURES (14 technical indicators)
   ↓
3. RUNNING_ML (XGBoost prediction)
   ↓
4. ANALYZING_SIGNALS (ScoutAgent + AnalystAgent)
   ├─ ScoutAgent: Sentiment score
   ├─ AnalystAgent: Technical score
   └─ ML Model: Probability UP/DOWN
   ↓
5. MAKING_DECISION (DecisionEngine - 3-signal fusion)
   ├─ ML: 50% weight
   ├─ Technical: 25% weight
   └─ Sentiment: 25% weight
   ↓
6. CREATING_INTENT (Intent router)
   ↓
7. SIGNING_INTENT (Blockchain EIP-712)
   ↓
8. VALIDATING_RISK (RiskAgent pre-trade check)
   ↓
9. EXECUTING_ORDER (Paper/Live execution)
   ↓
10. RECORDING_RESULT (Database + blockchain posting)
```

**Emitted as WebSocket events for real-time dashboard updates**

---

## 🎯 Current Limitation: NO Agent Templates

### What's Missing
- ❌ Pre-defined agent configurations (templates)
- ❌ Balanced agent config (fixed)
- ❌ Aggressive agent config (fixed)
- ❌ Conservative agent config (fixed)
- ❌ Template selection in UI/API
- ❌ Template-based deployment system

### Current Configuration System
- Settings are **global** in `backend/utils/config.py`
- **One set of parameters** applied to all trades:
  - `max_capital_per_trade: float = 0.10` (10%)
  - `max_daily_loss_pct: float = 0.05` (5%)
  - `max_drawdown_pct: float = 0.15` (15%)
  - `max_consecutive_losses: int = 5`
  - `min_confidence: float = 0.15`
- **No way to switch between different agent profiles**

---

## 📋 What NEEDS to Be Created for Hackathon

### 1. Agent Template System (CRITICAL)
```python
# backend/agents/templates.py (NEW FILE)

AGENT_TEMPLATES = {
    "balanced": {
        "name": "Balanced Trader",
        "description": "Steady profit with moderate risk",
        "position_multiplier": 1.0,
        "max_daily_loss_pct": 0.05,      # 5%
        "max_drawdown_pct": 0.15,        # 15%
        "entry_confidence": 0.65,         # 65%
        "max_consecutive_losses": 5,
        "atr_risk_multiplier": 1.5,
        "max_capital_per_trade": 0.10,   # 10%
        "signal_weights": {
            "ml_prediction": 0.50,
            "technical": 0.25,
            "sentiment": 0.25
        }
    },
    
    "aggressive": {
        "name": "Aggressive Trader",
        "description": "Maximum profit with higher risk",
        "position_multiplier": 1.5,
        "max_daily_loss_pct": 0.10,      # 10%
        "max_drawdown_pct": 0.20,        # 20%
        "entry_confidence": 0.50,         # 50%
        "max_consecutive_losses": 3,
        "atr_risk_multiplier": 1.0,
        "max_capital_per_trade": 0.15,   # 15%
        "signal_weights": {
            "ml_prediction": 0.50,
            "technical": 0.25,
            "sentiment": 0.25
        }
    },
    
    "conservative": {
        "name": "Guardian Trader",
        "description": "Capital preservation with low risk",
        "position_multiplier": 0.5,
        "max_daily_loss_pct": 0.02,      # 2%
        "max_drawdown_pct": 0.10,        # 10%
        "entry_confidence": 0.80,         # 80%
        "max_consecutive_losses": 2,
        "atr_risk_multiplier": 2.0,
        "max_capital_per_trade": 0.05,   # 5%
        "signal_weights": {
            "ml_prediction": 0.50,
            "technical": 0.25,
            "sentiment": 0.25
        }
    }
}
```

### 2. API Endpoint (CRITICAL)
```python
# In backend/api/server.py (ADD THIS)

class AgentDeploymentConfig(BaseModel):
    agent_name: str          # e.g., "Sigma Trading"
    template: str            # "balanced" | "aggressive" | "conservative"
    symbol: str = "BTC/USD"

@app.post("/api/deploy-agent")
async def deploy_agent(config: AgentDeploymentConfig):
    """Deploy agent to Locus with selected template"""
    # Load template config
    # Deploy to Locus
    # Return deployment URL
```

### 3. UI Component (CRITICAL)
```typescript
// frontend/components/DeployToLocusButton.tsx (NEW FILE)

const TEMPLATES = {
  balanced: { label: "Balanced ⚖️", description: "..." },
  aggressive: { label: "Aggressive 🚀", description: "..." },
  conservative: { label: "Guardian 🛡️", description: "..." }
};

// Dropdown to select template
// Button to deploy with selected template
```

### 4. TradingService Update (IMPORTANT)
```python
# backend/services/trading_service.py

# CHANGE: Instead of global settings, load from template
def load_agent_template(self, template_name: str):
    """Load agent configuration from template"""
    template = AGENT_TEMPLATES[template_name]
    # Apply template values to risk_agent, decision_engine, etc.
```

---

## 📊 Implementation Roadmap

### ✅ Already Implemented
- Multi-agent decision framework (Scout + Analyst + Risk)
- 3-signal fusion (ML + Technical + Sentiment)
- Circuit breaker and risk management
- WebSocket real-time updates
- Trading pipeline with 10 stages
- Paper trading execution
- Database persistence
- Blockchain integration (optional)

### 📋 TODO for Hackathon (Day 1-2)

| Task | Priority | Effort | Files |
|------|----------|--------|-------|
| Create `agents/templates.py` | 🔴 CRITICAL | 30 min | 1 new |
| Update `api/server.py` endpoint | 🔴 CRITICAL | 1 hour | 1 modify |
| Create deploy button component | 🔴 CRITICAL | 1 hour | 1 new |
| Update `trading_service.py` | 🟡 IMPORTANT | 1 hour | 1 modify |
| Update frontend form | 🟡 IMPORTANT | 1 hour | 1 modify |
| Test all 3 templates | 🟡 IMPORTANT | 1 hour | 0 |

**Total: ~5 hours (fits within Day 1-2 budget)**

---

## 🎯 Current Chart Issue (Separate Problem)

The candle chart loading issue is likely **unrelated to agents**:
- Could be WebSocket delay for market data
- Could be chart component rendering before data arrives
- Could be missing `/api/market` endpoint response

**Solution:** Check browser console for errors when candles don't load.

---

## Summary

**Current State:**
- ✅ Agent logic: 100% complete (Scout + Analyst + Risk)
- ✅ Pipeline: 100% complete (10-stage flow)
- ✅ Trading execution: 100% complete (Paper mode)
- ❌ Agent templates: 0% (NOT IMPLEMENTED YET)
- ❌ Template deployment: 0% (NOT IMPLEMENTED YET)

**For Hackathon Success:**
Need to implement the **Agent Template System** to allow users to deploy different agent configurations with one-click.

That's the missing piece! 🎯


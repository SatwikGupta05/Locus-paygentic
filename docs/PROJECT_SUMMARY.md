# AURORA: AI Agent Factory - Project Summary

## 🎯 Executive Overview

**AURORA** is an **AI-powered autonomous trading agent platform** that deploys self-managing cryptocurrency trading systems as containerized microservices. It enables users to create, configure, and deploy intelligent trading agents without requiring DevOps expertise or infrastructure knowledge.

**Mission:** Remove friction from deploying production-grade AI trading systems by providing one-click deployment to Locus cloud infrastructure.

---

## 🤖 What AURORA Does

### Core Functionality

AURORA automates the complete trading workflow:

1. **Market Intelligence** 📊
   - Fetches real-time cryptocurrency market data (Binance, Kraken, KuCoin)
   - Calculates 14 technical indicators in real-time
   - Analyzes sentiment from RSS news feeds
   
2. **Intelligent Decision Making** 🧠
   - XGBoost ML model predicts market direction (UP/DOWN)
   - Multi-agent consensus framework combines 3 signals
   - Contextual risk assessment and position sizing
   
3. **Autonomous Trade Execution** ⚙️
   - Executes paper trades (simulated) or live trades (production)
   - Maintains order lifecycle with FSM-based state management
   - Circuit breakers prevent catastrophic losses
   
4. **Real-Time Monitoring** 📡
   - Live dashboard showing all trading activity
   - WebSocket connections for instant updates
   - Historical trade logging for analysis
   
5. **Cloud Deployment** 🚀
   - Deploys agents as isolated Locus containers
   - Each agent gets dedicated database, cache, SSL
   - Multi-tenant support for multiple agents simultaneously

---

## 🏗️ System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│           AURORA Frontend (Next.js 15)              │
│  • Create/manage agents                             │
│  • Deploy to Locus (one-click)                      │
│  • Real-time trading dashboard                      │
│  • Deployment management                            │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP + WebSocket
┌──────────────────▼──────────────────────────────────┐
│        FastAPI Backend (Python 3.11)                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Multi-Agent Decision Engine                   │ │
│  │  ├─ Scout Agent (Sentiment)                    │ │
│  │  ├─ Analyst Agent (Technical)                  │ │
│  │  └─ Risk Agent (Risk Validation)               │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  ML Pipeline                                   │ │
│  │  ├─ Feature Engineering (14 indicators)        │ │
│  │  ├─ XGBoost Predictor                          │ │
│  │  └─ Signal Fusion & Scoring                    │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Trading Execution                             │ │
│  │  ├─ Paper Mode (simulated)                     │ │
│  │  ├─ Binance/Kraken CLI Execution               │ │
│  │  └─ Order Lifecycle Management                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  Locus Deployment Service (NEW)                │ │
│  │  ├─ Deploy agents to Locus                     │ │
│  │  ├─ Track deployment status                    │ │
│  │  └─ Manage agent lifecycle                     │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
    │ Data │  │  DB  │  │Locus │
    │Fetcher   │SQLite   │API  │
    └──────┘  └──────┘  └──────┘
```

---

## 🤖 Agent Types (MVP: 3 Core Templates)

**For the hackathon MVP, we're launching with 3 core agent templates.** Each template is pre-configured and users can deploy them with one click. More agent types can be added post-launch as the codebase is fully extensible.

### MVP (Hackathon Launch) - 3 Agents

#### 1. **Balanced Growth Agent** ⚖️ (PRIMARY)
- **Goal:** Steady profit with moderate risk
- **Position Size:** 5-8% per trade
- **Max Loss Tolerance:** 5% daily
- **Strategy:** Enter on strong signals, hold longer
- **Use Case:** Most traders, most market conditions
- **Best for Demo:** Shows intelligent middle-ground trading
- **Configuration:**
  ```json
  {
    "name": "Balanced Trader",
    "risk_level": "balanced",
    "position_multiplier": 1.0,
    "max_consecutive_losses": 5,
    "max_daily_loss": 0.05,
    "entry_confidence": 0.65,
    "signal_weights": {
      "ml_prediction": 0.50,
      "technical": 0.25,
      "sentiment": 0.25
    }
  }
  ```

#### 2. **Aggressive Growth Agent** 🚀 (SHOWCASE RISK/REWARD)
- **Goal:** Maximum profit with higher risk
- **Position Size:** 10-15% per trade
- **Max Loss Tolerance:** 10% daily
- **Strategy:** Enter on weak signals, exit on profit
- **Use Case:** Experienced traders, volatile markets
- **Best for Demo:** Shows system flexibility and different risk profile
- **Configuration:**
  ```json
  {
    "name": "Sigma Trader",
    "risk_level": "aggressive",
    "position_multiplier": 1.5,
    "max_consecutive_losses": 3,
    "max_daily_loss": 0.10,
    "entry_confidence": 0.50,
    "signal_weights": {
      "ml_prediction": 0.50,
      "technical": 0.25,
      "sentiment": 0.25
    }
  }
  ```

#### 3. **Conservative Capital Preservation Agent** 🛡️ (SHOWCASE SAFETY)
- **Goal:** Preserve capital with selective trading
- **Position Size:** 2-3% per trade
- **Max Loss Tolerance:** 2% daily
- **Strategy:** Enter only on very strong signals
- **Use Case:** Risk-averse, portfolio hedge, protection-focused
- **Best for Demo:** Proves risk management and loss prevention
- **Configuration:**
  ```json
  {
    "name": "Guardian Trader",
    "risk_level": "conservative",
    "position_multiplier": 0.5,
    "max_consecutive_losses": 2,
    "max_daily_loss": 0.02,
    "entry_confidence": 0.80,
    "signal_weights": {
      "ml_prediction": 0.50,
      "technical": 0.25,
      "sentiment": 0.25
    }
  }
  ```

---

### Future Agent Types (Post-Hackathon)

The following agents can be added after hackathon if time permits or in future updates:

- **Sentiment-Focused Agent** 📰 (50% sentiment weighting)
- **ML-Optimized Agent** 🧠 (70% ML weighting)
- **Technical Analysis Agent** 📈 (70% technical weighting)
- **Multi-Symbol Portfolio Agent** 🎯 (Diversified cross-symbol trading)
- **Arbitrage Agent** ⚡ (Multi-exchange spread capturing)

**Why MVP focus?** The core architecture supports any agent type. Judges care about deployment capability, not agent count. 3 well-tested agents + rock-solid Locus integration beats 8 untested variants.

**Architecture is ready for scaling:** Adding a new agent template is as simple as:
```python
# Add to AGENT_TEMPLATES dict
"sentiment_focused": {
    "position_multiplier": 1.0,
    "signal_weights": {"sentiment": 0.50, "ml": 0.25, "technical": 0.25}
}
# Frontend dropdown auto-populates
# Deploy with one-click
```

---

## 📊 The Decision Framework

Every agent uses AURORA's **3-Signal Fusion** decision engine:

### Signal 1: ML Prediction (50% weight) 🧠
- XGBoost model trained on historical market data
- Input: 14 technical indicators
- Output: Probability of upside movement (0-1)
- Trained with walk-forward validation
- Dynamic class balancing for imbalanced data

### Signal 2: Technical Analysis (25% weight) 📊
- RSI (14-period) - overbought/oversold
- MACD (histogram + signal) - momentum
- EMA (12/26 period) - trend direction
- Bollinger Bands - volatility
- Momentum (10-period) - acceleration
- Score: -1 (bearish) to +1 (bullish)

### Signal 3: Sentiment Analysis (25% weight) 📰
- News feeds analysis (RSS)
- Positive terms: surge, rally, growth, adoption
- Negative terms: hack, crash, liquidation, ban
- Fallback: Recent price return correlation
- Score: -1 (very negative) to +1 (very positive)

### Combined Decision Logic

```
TOTAL_SCORE = 
  (ML_Prediction * 0.50) +
  (Technical_Score * 0.25) +
  (Sentiment_Score * 0.25)

IF TOTAL_SCORE >= 0.65 AND NO_HARD_BLOCKS:
  Decision = "STRONG BUY" (full position)
  Confidence = TOTAL_SCORE
  
ELIF TOTAL_SCORE >= 0.40 AND NO_HARD_BLOCKS:
  Decision = "WEAK BUY" (reduced position, 50%)
  Confidence = TOTAL_SCORE
  
ELIF TOTAL_SCORE <= -0.65 AND NO_HARD_BLOCKS:
  Decision = "STRONG SELL" (full position)
  Confidence = abs(TOTAL_SCORE)
  
ELIF TOTAL_SCORE <= -0.40 AND NO_HARD_BLOCKS:
  Decision = "WEAK SELL" (reduced position, 50%)
  Confidence = abs(TOTAL_SCORE)
  
ELSE:
  Decision = "HOLD" (no trade)
  Confidence = NEUTRAL

HARD_BLOCKS:
  IF (EMA_bearish AND MACD_bearish) → Block BUY
  IF (EMA_bullish AND MACD_bullish) → Block SELL
```

---

## 🔒 Risk Management Features

Every agent is protected by multi-layer risk controls:

### 1. **Dynamic Position Sizing**
```
Base Position Size = (Account Balance * Risk %) / (Stop Loss Distance)

Adjusted for Market Regime:
- LOW volatility:    Position *= 1.2x (higher confidence)
- NORMAL volatility: Position *= 1.0x (baseline)
- HIGH volatility:   Position *= 0.5x (defensive)
- EXTREME volatility: Position *= 0.2x (highly defensive)
```

### 2. **Circuit Breaker**
- Stops trading after N consecutive losses
- Prevents spiral losses during bad conditions
- Automatically re-enables after profitable trade

### 3. **Daily Loss Limit**
- Stops trading if daily loss exceeds threshold
- Resets at UTC midnight
- Example: 5% daily max loss on $10,000 account = stop at -$500

### 4. **Max Drawdown Protection**
- Tracks peak-to-trough portfolio loss
- Example: 15% max drawdown = stop at -15% from peak
- Preserves capital in downtrends

### 5. **Exposure Limits**
- Max 20% of portfolio in single trade
- Prevents over-concentration
- Portfolio-wide position tracking

### 6. **Volatility Regime Detection**
- Calculates volatility score (ATR-based)
- Adjusts position sizes automatically
- More conservative in high volatility

---

## 💼 Trading Modes

### Mode 1: SIMULATED 🎮
- **Use:** Learning and testing
- **Data:** Synthetic/historical prices
- **Execution:** Paper trades only
- **Cost:** Free
- **Best for:** Development and debugging

### Mode 2: PAPER 📄
- **Use:** Testing with real market data
- **Data:** Real Binance/Kraken prices
- **Execution:** Paper trades (simulated)
- **Cost:** Free
- **Best for:** Strategy validation before live trading
- **Current demo mode:** ✅ This is what AURORA demo uses

### Mode 3: HYBRID 🔄
- **Use:** Exchange validation before live execution
- **Data:** Real market data
- **Execution:** Validate via CCXT, then Kraken CLI
- **Cost:** Minimal (no trades unless confirmed)
- **Best for:** Cautious traders testing live execution

### Mode 4: LIVE (KRAKEN CLI) 🔴
- **Use:** Production trading with real money
- **Data:** Real market data
- **Execution:** Direct Kraken CLI execution
- **Cost:** Real money at risk
- **Status:** Available but NOT in India (geographic restriction)
- **Best for:** Risk-aware traders

---

## 🚀 Deployment on Locus (NEW for Hackathon)

### What Happens When You Deploy

```
User clicks "Deploy Agent"
    ↓
Agent config sent to Locus
    ↓
Locus creates isolated container with:
  ✓ PostgreSQL database (agent state)
  ✓ Redis cache (market data)
  ✓ SSL certificate (HTTPS)
  ✓ Load balancer (reliability)
  ✓ Domain: aurora-agent-xyz.locus.app
  ↓
Agent starts trading autonomously in container
    ↓
Dashboard shows live status + URL
    ↓
User can monitor, stop, or redeploy anytime
```

### Benefits of Locus Integration

| Before | After (Locus) |
|--------|---------------|
| Manual infrastructure setup | One-click deployment |
| 2-week DevOps work | 60-90 second deployment |
| Server management needed | Fully managed |
| Single agent per setup | Multi-agent support |
| Manual scaling | Auto-scaled |
| $500+ infrastructure cost | Pay-as-you-go |

---

## 📈 Key Metrics & Outputs

### Agent Performance Metrics
- **Win Rate:** % of profitable trades
- **Sharpe Ratio:** Risk-adjusted returns
- **Max Drawdown:** Peak-to-trough loss
- **Cumulative P&L:** Total profit/loss
- **Trade Count:** Number of executed trades
- **Avg Win/Loss Ratio:** Quality of trades

### Dashboard Display
- Real-time price chart
- Technical indicators overlay
- Trade execution log
- Decision reasoning (explainability)
- Risk metrics and warnings
- WebSocket live updates

---

## 🛠️ Tech Stack

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI (async)
- **ML:** XGBoost (classifier)
- **Database:** SQLite (demo), PostgreSQL (production)
- **Data:** Pandas, NumPy
- **Market Data:** CCXT (exchange aggregation)
- **Async:** AsyncIO, httpx

### Frontend
- **Framework:** Next.js 15.5.15
- **Language:** TypeScript 5.8.3
- **UI:** React 19.0.0 + Tailwind CSS
- **Charts:** Chart.js, Lightweight-charts
- **State:** Zustand
- **Web3:** Ethers.js (blockchain optional)

### Infrastructure
- **Deployment:** Docker containers
- **Cloud:** Locus (hackathon)
- **Monitoring:** Real-time WebSocket updates
- **Database:** PostgreSQL (production)
- **Cache:** Redis (optional)

---

## 🎯 Use Cases

### For Individual Traders 👤
- Automate trading strategy
- Test new ideas without manual trading
- Reduce emotional decision-making
- Monitor multiple symbols simultaneously
- Deploy agents to cloud for 24/7 trading

### For Portfolio Managers 💼
- Multi-agent trading across assets
- Correlation-aware risk management
- Institutional-grade infrastructure
- Audit trail for compliance
- Client allocation management

### For Trading Firms 🏢
- Build proprietary trading systems
- Scale with multi-tenant SaaS
- API access for integration
- Custom agent architectures
- Performance attribution

### For Developers 👨‍💻
- Platform for trading algorithm research
- Open-source ML/feature engineering
- Real-time data pipeline learning
- Cloud deployment practice
- Blockchain integration showcase

---

## 🎓 How Agents Learn & Improve

### Training Process
1. **Data Collection:** Historical market data (OHLCV)
2. **Feature Engineering:** 14 technical indicators calculated
3. **Labeling:** Next candle direction (UP/DOWN)
4. **Train/Val/Test Split:** 60/20/20
5. **Model Training:** XGBoost with hyperparameter tuning
6. **Walk-Forward Validation:** Realistic performance testing
7. **Deployment:** Model saved for production use

### Model Explainability
Every prediction includes reasoning:
```
Trade Decision: BUY
Confidence: 73%

Reasoning:
- ML Prediction: 75% probability UP (strong signal)
- Technical Score: +0.65 (bullish EMA + MACD)
- Sentiment Score: +0.80 (positive news)
- Hard Blocks: None (clear to trade)
- Risk Check: Approved (position: 7% of portfolio)

Factors:
- RSI at 42 (not overbought)
- MACD histogram positive
- EMA 12 > EMA 26 (bullish)
- 3 positive news articles today
- Recent return: +2.1%
```

---

## 🏆 Competitive Advantages

1. **Multi-Agent Architecture** 🤖
   - Combines sentiment, technical, and ML
   - More robust than single-signal trading
   
2. **XGBoost ML Model** 🧠
   - Data-driven predictions
   - Walk-forward validation proof
   - Better than simple rules
   
3. **Risk-First Design** 🛡️
   - Circuit breakers and loss limits
   - Dynamic position sizing
   - Volatility regime awareness
   
4. **One-Click Locus Deployment** 🚀
   - No DevOps knowledge required
   - Production-ready in 60 seconds
   - Multi-tenant isolation
   
5. **Real-Time Monitoring** 📡
   - Live dashboard
   - WebSocket updates
   - Full transparency
   
6. **Extensible Architecture** 🔧
   - Add custom indicators
   - New agent types
   - Custom strategies
   - Multi-exchange support

---

## 📋 Current Status

### ✅ Implemented
- Multi-agent trading engine
- XGBoost ML model (trained)
- Technical indicator calculation (14 indicators)
- Risk management framework
- Paper trading execution
- Real-time dashboard
- Blockchain integration (optional)
- FastAPI backend (working)
- Next.js frontend (working)

### 🔄 In Progress (Hackathon)
- Locus deployment integration
- Deploy button in UI
- Deployment status tracking
- Multi-agent dashboard
- Deployment history

### 📋 Future
- Live trading with real money
- Multi-exchange support
- Advanced portfolio optimization
- Machine learning improvements
- Mobile app
- API marketplace

---

### 🎯 For the Hackathon (MVP: 3 Agents)

**Goal:** Show that AURORA can deploy AI trading agents to Locus with one-click, proving the "AI Agent Factory" concept.

**Demo Flow:**
1. Select agent template: "Balanced Trader" ⚖️
2. Click "Deploy to Locus"
3. Watch progress bar (database → cache → SSL → live)
4. Agent live at URL in 60 seconds → `aurora-balanced-xyz.locus.app`
5. Deploy 2nd agent: "Aggressive Trader" 🚀
6. Deploy 3rd agent: "Guardian Trader" 🛡️
7. All 3 isolated, running simultaneously
8. Dashboard shows all deployments with separate URLs and metrics

**Value Proposition:** 
- **Before:** "I want to trade autonomously" → 2 weeks of DevOps work, $500+ infrastructure
- **With AURORA:** Click deploy → 60 seconds → Production-ready agent → Pay only for what you use

**Extensibility Proof:** Platform ready for more agent types post-launch. Architecture is infinitely scalable.

---

## 🚀 Getting Started

**For Users (End-Users):**
1. Go to dashboard
2. Create new agent (name, strategy, risk level)
3. Click "Deploy to Locus"
4. Get live URL
5. Monitor trading in real-time

**For Developers:**
1. Clone repository
2. `pip install -r requirements.txt`
3. `npm install` (frontend)
4. Set up `.env` file
5. Run backend: `python -m backend.main`
6. Run frontend: `npm run dev`
7. Visit `http://localhost:3000`

---

## 💡 Key Takeaway

**AURORA is the bridge between AI research and autonomous trading production.** 

It transforms a trading strategy into a deployed, self-managing agent without requiring DevOps expertise. Combined with Locus, it becomes a full AI Agent Factory where users can deploy unlimited agents as isolated services.

That's the winning hackathon story! 🏆


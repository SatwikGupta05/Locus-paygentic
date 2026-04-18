# COMPARISON: Existing Code vs Hackathon Requirements

**Date:** April 17, 2026  
**Goal:** Identify what can be leveraged vs what needs to be built

---

## 📊 High-Level Summary

| Category | Status | Effort |
|----------|--------|--------|
| **Trading Core** | ✅ 100% Complete | 0 hours |
| **API Endpoints** | ✅ 80% Complete | 1 hour to add |
| **Frontend Dashboard** | ✅ 90% Complete | 2 hours to modify |
| **Database Schema** | ✅ 70% Complete | 0.5 hours to extend |
| **Agent System** | ✅ 100% Complete | 1.5 hours to template |
| **Locus Integration** | ❌ 0% Complete | 4 hours to build |
| **TOTAL NEW WORK** | | ~9 hours |

---

## 🔧 DETAILED BREAKDOWN

---

## 1️⃣ API ENDPOINTS

### ✅ EXISTING (Already Built - Use As-Is)

| Endpoint | Method | Purpose | Status | Code |
|----------|--------|---------|--------|------|
| `/health` | GET | System health check | ✅ Working | `server.py:76` |
| `/config` | GET | Trading configuration | ✅ Working | `server.py:84` |
| `/status` | GET | Current trading status | ✅ Working | `server.py:101` |
| `/market` | GET | Latest market data | ✅ Working | `server.py:105` |
| `/decision` | GET | Latest decision | ✅ Working | `server.py:109` |
| `/trades` | GET | Recent trades list | ✅ Working | `server.py:113` |
| `/metrics` | GET | Performance metrics | ✅ Working | `server.py:117` |
| `/intents` | GET | Blockchain intents | ✅ Working | `server.py:121` |
| `/orders` | GET | Order history | ✅ Working | `server.py:125` |
| `/reputation` | GET | Agent reputation | ✅ Working | `server.py:129` |
| `/agent` | GET | Agent details | ✅ Working | `server.py:133` |
| `/strategy` | GET | Strategy summary | ✅ Working | `server.py:154` |
| `/audit-trail` | GET | Audit log | ✅ Working | `server.py:162` |
| `/pipeline` | GET | Pipeline stage | ✅ Working | `server.py:166` |
| WebSocket `/ws/market` | WS | Market updates | ✅ Working | `server.py:176` |
| WebSocket `/ws/trades` | WS | Trade updates | ✅ Working | `server.py:180` |
| WebSocket `/ws/decisions` | WS | Decision updates | ✅ Working | `server.py:184` |
| WebSocket `/ws/pipeline` | WS | Pipeline updates | ✅ Working | `server.py:188` |

**TOTAL: 18 endpoints already exist ✅**

### ❌ NEEDED (Must Build)

| Endpoint | Method | Purpose | Priority | Effort |
|----------|--------|---------|----------|--------|
| `/api/deploy-agent` | POST | Deploy agent to Locus | 🔴 CRITICAL | 1 hour |
| `/api/deployments` | GET | List all deployments | 🔴 CRITICAL | 30 min |
| `/api/deployments/{id}` | GET | Get deployment status | 🟡 IMPORTANT | 30 min |
| `/api/deployments/{id}` | DELETE | Stop deployment | 🟡 IMPORTANT | 30 min |
| `/api/deployment-history` | GET | Deployment timeline | 🟡 IMPORTANT | 30 min |

**TOTAL: 5 new endpoints needed (~3 hours work)**

---

## 2️⃣ FRONTEND COMPONENTS

### ✅ EXISTING (Already Built - Use As-Is)

| Component | Status | Purpose | Notes |
|-----------|--------|---------|-------|
| `dashboard/page.tsx` | ✅ Complete | Main trading dashboard | Shows decisions, market, trades |
| `DecisionCard.tsx` | ✅ Complete | Shows trading decisions | Real-time updates |
| `price-chart.tsx` | ✅ Complete | Market price chart | Lightweight-charts |
| `pnl-curve.tsx` | ✅ Complete | P&L performance graph | Chart.js based |
| `pipeline-tracker.tsx` | ✅ Complete | Shows pipeline stages | 10-stage flow |
| `RiskBadge.tsx` | ✅ Complete | Risk indicators | Volatility display |
| `TopBar.tsx` | ✅ Complete | Navigation bar | Layout header |
| `StatusBar.tsx` | ✅ Complete | Status indicators | Health/connection status |
| `LiveFeed.tsx` | ✅ Complete | Real-time event feed | WebSocket feed |
| `decision-explainability.tsx` | ✅ Complete | Decision reasoning | Shows factors |
| `mode-badge.tsx` | ✅ Complete | Mode indicator | PAPER/LIVE/etc |
| `on-chain-proof.tsx` | ✅ Complete | Blockchain proof display | Intent verification |
| `agent/page.tsx` | ✅ Complete | Agent details page | Info display |
| `trades/page.tsx` | ✅ Complete | Trades history page | Trade list |
| `strategy/page.tsx` | ✅ Complete | Strategy summary | Strategic overview |

**TOTAL: 15 components already exist ✅**

### ❌ NEEDED (Must Build - New Pages/Components)

| Component | Type | Purpose | Priority | Effort |
|-----------|------|---------|----------|--------|
| **AgentTemplateSelector** | Component | Template dropdown | 🔴 CRITICAL | 45 min |
| **DeployToLocusButton** | Component | Deploy trigger | 🔴 CRITICAL | 1 hour |
| **DeploymentProgress** | Component | Progress bar | 🔴 CRITICAL | 45 min |
| **DeploymentSuccess** | Component | Success screen with URL | 🔴 CRITICAL | 30 min |
| **DeploymentError** | Component | Error display | 🟡 IMPORTANT | 30 min |
| **deployments/page.tsx** | Page | Deployments list view | 🔴 CRITICAL | 1 hour |
| **DeploymentCard** | Component | Individual agent card | 🔴 CRITICAL | 45 min |
| **DeploymentMetrics** | Component | Uptime, P&L, requests | 🟡 IMPORTANT | 45 min |

**TOTAL: 8 new components/pages needed (~5 hours work)**

### ✅ EXISTING INFRASTRUCTURE (Reusable)

- Zustand store for state management ✅
- React Query for data fetching ✅
- TailwindCSS for styling ✅
- WebSocket connections established ✅
- Real-time update patterns ✅
- Responsive layout ✅

---

## 3️⃣ DATABASE SCHEMA

### ✅ EXISTING TABLES

| Table | Purpose | Status | Columns |
|-------|---------|--------|---------|
| `runs` | Trading session | ✅ Complete | id, started_at, finished_at, mode, symbol, status |
| `market_data` | Price history | ✅ Complete | id, run_id, symbol, timestamp, OHLCV, source |
| `features` | Calculated indicators | ✅ Complete | id, run_id, symbol, timestamp, payload (14 features) |
| `decisions` | Trading decisions | ✅ Complete | id, run_id, symbol, timestamp, payload (action, confidence, reasoning) |
| `intents` | Blockchain intents | ✅ Complete | id, run_id, decision_id, intent_hash, timestamp, status, payload |
| `orders` | Order records | ✅ Complete | id, run_id, symbol, side, status, timestamp, payload |
| `trades` | Executed trades | ✅ Complete | id, run_id, timestamp, symbol, side, amount, price, confidence, realized_pnl |
| `metrics` | Aggregate metrics | ✅ Complete | name, payload, updated_at |
| `positions` | Open positions | ✅ Complete | symbol, side, status, entry_price, size, stop_loss, take_profit, unrealized_pnl |

**TOTAL: 9 tables already exist ✅**

### ❌ NEW TABLES NEEDED

| Table | Purpose | Columns | Priority |
|-------|---------|---------|----------|
| `deployments` | Track agent deployments | id, agent_name, template, status, locus_url, locus_deployment_id, created_at, stopped_at, config_json | 🔴 CRITICAL |
| `deployment_events` | Deployment timeline | id, deployment_id, event, timestamp, message | 🟡 IMPORTANT |

**Schema Additions (~100 lines SQL)**

```sql
CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    template TEXT NOT NULL,  -- balanced, aggressive, conservative
    status TEXT NOT NULL,    -- deploying, running, error, stopped
    locus_url TEXT,
    locus_deployment_id TEXT,
    created_at TEXT NOT NULL,
    stopped_at TEXT,
    config_json TEXT,
    metrics_json TEXT,
    error_message TEXT
);

CREATE TABLE deployment_events (
    id TEXT PRIMARY KEY,
    deployment_id TEXT NOT NULL,
    event TEXT NOT NULL,     -- deployed, failed, stopped, redeployed
    timestamp TEXT NOT NULL,
    message TEXT,
    FOREIGN KEY(deployment_id) REFERENCES deployments(id)
);
```

---

## 4️⃣ BACKEND SERVICES

### ✅ EXISTING SERVICES (Core Trading - Use As-Is)

| Service | Purpose | Status | Lines |
|---------|---------|--------|-------|
| `TradingService` | Main trading orchestration | ✅ Complete | 500+ |
| `ScoutAgent` | Sentiment analysis | ✅ Complete | 45 |
| `AnalystAgent` | Technical analysis | ✅ Complete | 12 |
| `RiskAgent` | Risk management | ✅ Complete | 150+ |
| `DecisionEngine` | 3-signal fusion | ✅ Complete | 80+ |
| `FeatureEngineering` | 14 indicators | ✅ Complete | 200+ |
| `Predictor` | XGBoost ML model | ✅ Complete | 100+ |
| `MarketFetcher` | Data retrieval (CCXT) | ✅ Complete | 150+ |
| `TradeExecutor` | Trade execution | ✅ Complete | 120+ |
| `EventBusV2` | WebSocket broadcast | ✅ Complete | 100+ |
| `DBManager` | Database operations | ✅ Complete | 80+ |
| `PortfolioManager` | Position tracking | ✅ Complete | 120+ |
| `ReputationTracker` | Performance metrics | ✅ Complete | 80+ |

**TOTAL: 13 services complete ✅**

### ❌ NEW SERVICES NEEDED

| Service | Purpose | Priority | Effort |
|---------|---------|----------|--------|
| **LocusDeploymentService** | Deploy/manage agents on Locus | 🔴 CRITICAL | 2 hours |
| **DeploymentTracker** | Track deployment state | 🔴 CRITICAL | 1 hour |

**Key Class Structure:**
```python
class LocusDeploymentService:
    """Deploy agents to Locus infrastructure"""
    
    def deploy_agent(self, config: AgentConfig) -> DeploymentResponse
    def get_status(self, deployment_id: str) -> dict
    def list_deployments(self) -> list
    def stop_deployment(self, deployment_id: str) -> bool
    async def _call_locus_api(self, method: str, endpoint: str, data: dict) -> dict
```

---

## 5️⃣ AGENT TEMPLATES & CONFIGURATION

### ✅ EXISTING CONFIGURATION (Global Settings - Use As-Is)

| Setting | Current Value | Location | Status |
|---------|---------------|----------|--------|
| Trading parameters | Set in `.env` | `config.py` | ✅ Complete |
| Max capital per trade | 0.10 (10%) | Global | ✅ Complete |
| Max daily loss | 0.05 (5%) | Global | ✅ Complete |
| Max drawdown | 0.15 (15%) | Global | ✅ Complete |
| Risk fraction | 0.02 (2%) | Global | ✅ Complete |
| ATR multiplier | 1.5 | Global | ✅ Complete |
| Min confidence | 0.15 | Global | ✅ Complete |

**Current System: ONE global config for ALL trades**

### ❌ NEEDED: Agent Templates System

| Template | Config Values | Purpose | Status |
|----------|---------------|---------|--------|
| `balanced` | position_multiplier=1.0, max_daily=0.05, entry_confidence=0.65 | Steady growth | ❌ NEW |
| `aggressive` | position_multiplier=1.5, max_daily=0.10, entry_confidence=0.50 | Max profit | ❌ NEW |
| `conservative` | position_multiplier=0.5, max_daily=0.02, entry_confidence=0.80 | Capital preservation | ❌ NEW |

**New File Needed:**
```python
# backend/agents/templates.py (NEW - ~150 lines)

AGENT_TEMPLATES = {
    "balanced": {...},
    "aggressive": {...},
    "conservative": {...}
}
```

**Modifications Needed:**
```python
# backend/services/trading_service.py
# Add: Load template config method
# Modify: Initialize agents with template parameters
```

---

## 6️⃣ DEPENDENCIES & INFRASTRUCTURE

### ✅ ALL DEPENDENCIES ALREADY INSTALLED

**Backend (`requirements.txt`):**
```
✅ pandas, numpy, scikit-learn        # Data processing
✅ joblib, xgboost                    # ML model
✅ ccxt, requests                     # Market data + HTTP
✅ fastapi, uvicorn                   # API server
✅ web3, eth-account                  # Blockchain
✅ python-dotenv                      # Config
✅ httpx, psycopg2-binary             # Async HTTP + DB
```

**Frontend (`package.json`):**
```
✅ next 15.5.15, react 19.0.0         # Framework
✅ typescript 5.8.3                   # Language
✅ zustand                            # State management
✅ react-query                        # Data fetching
✅ tailwindcss                        # Styling
✅ chart.js, lightweight-charts       # Charting
✅ ethers                             # Blockchain Web3
```

**No new dependencies needed!** ✅

---

## 7️⃣ ARCHITECTURE & INFRASTRUCTURE

### ✅ EXISTING (Ready to Use)

- ✅ FastAPI server running on port 8000
- ✅ WebSocket connections for real-time updates
- ✅ EventBusV2 for pub/sub messaging
- ✅ SQLite database (or PostgreSQL)
- ✅ CORS enabled for frontend
- ✅ Docker support (Dockerfile exists)
- ✅ Error handling & logging
- ✅ Async/await patterns throughout

### ⚠️ TO ADD

- ⚠️ Locus API integration (NEW service)
- ⚠️ Agent template system (NEW logic)
- ⚠️ Deployment database tables (NEW schema)

---

## 📋 WORK BREAKDOWN BY PRIORITY

### 🔴 CRITICAL (Hackathon Core)

| Task | Files | Effort | Depends On |
|------|-------|--------|-----------|
| Create agent templates | `backend/agents/templates.py` (NEW) | 30 min | Nothing |
| Build LocusDeploymentService | `backend/services/locus_deployment_service.py` (NEW) | 2 hours | Templates |
| Add deployment endpoint | `backend/api/server.py` (MODIFY) | 1 hour | LocusService |
| Create deploy button | `frontend/components/DeployToLocusButton.tsx` (NEW) | 1 hour | Deploy endpoint |
| Create deployments page | `frontend/app/deployments/page.tsx` (NEW) | 1 hour | Deployment data |
| Add deployment tables | `backend/database/migrations/006_deployments.sql` (NEW) | 30 min | Nothing |

**Total Critical Path: ~5.5 hours**

### 🟡 IMPORTANT (Quality)

| Task | Files | Effort | Depends On |
|------|-------|--------|-----------|
| Add error handling | Various | 1 hour | Critical done |
| Test all 3 templates | Test files | 1 hour | Critical done |
| Add deployment metrics display | Components | 45 min | Deployments page |
| Create deployment history view | Components | 45 min | Deployments page |

**Total Important: ~3.5 hours**

### 🟢 NICE-TO-HAVE (Polish)

| Task | Files | Effort |
|------|-------|--------|
| Add deployment animations | Components | 30 min |
| Create deployment analytics | Components | 1 hour |
| Add agent configuration UI | Components | 1 hour |

**Total Nice-to-Have: ~2.5 hours**

---

## 🎯 FILES TO CREATE (Summary)

### New Backend Files
```
backend/agents/templates.py                          (NEW - 150 lines)
backend/services/locus_deployment_service.py         (NEW - 300 lines)
backend/database/migrations/006_deployments.sql      (NEW - 50 lines)
```

### Modified Backend Files
```
backend/api/server.py                 (ADD ~80 lines for endpoints)
backend/services/trading_service.py    (MODIFY ~30 lines for template loading)
backend/utils/config.py                (ADD ~5 variables for Locus)
```

### New Frontend Files
```
frontend/components/AgentTemplateSelector.tsx        (NEW - 60 lines)
frontend/components/DeployToLocusButton.tsx          (NEW - 150 lines)
frontend/components/DeploymentProgress.tsx           (NEW - 80 lines)
frontend/components/DeploymentSuccess.tsx            (NEW - 60 lines)
frontend/components/DeploymentError.tsx              (NEW - 40 lines)
frontend/components/DeploymentCard.tsx               (NEW - 100 lines)
frontend/components/DeploymentMetrics.tsx            (NEW - 80 lines)
frontend/app/deployments/page.tsx                    (NEW - 150 lines)
```

### Modified Frontend Files
```
frontend/app/dashboard/page.tsx        (ADD deploy button)
frontend/app/layout.tsx                (ADD deployments nav link)
```

---

## ⏱️ TOTAL EFFORT ESTIMATE

| Category | Hours | Status |
|----------|-------|--------|
| Agent Templates | 0.5 | 🔴 CRITICAL |
| Locus Service | 2 | 🔴 CRITICAL |
| API Endpoints | 1.5 | 🔴 CRITICAL |
| Database | 0.5 | 🔴 CRITICAL |
| Frontend Components | 4 | 🔴 CRITICAL |
| Testing | 1 | 🟡 IMPORTANT |
| Polish/Bug fixes | 1 | 🟢 NICE-TO-HAVE |
| **TOTAL** | **~10.5 hours** | **Fits 4-day plan** ✅ |

---

## 🚀 NEXT STEPS (In Order)

1. ✅ **Step 1: Create Agent Templates** (`backend/agents/templates.py`)
   - Define 3 template configs (balanced, aggressive, conservative)
   - Time: 30 min

2. ✅ **Step 2: Build Locus Service** (`backend/services/locus_deployment_service.py`)
   - Implement deployment logic
   - Locus API calls
   - Status polling
   - Time: 2 hours

3. ✅ **Step 3: Add API Endpoint** (modify `backend/api/server.py`)
   - POST `/api/deploy-agent`
   - GET `/api/deployments`
   - Time: 1 hour

4. ✅ **Step 4: Create Database Tables** (new migration)
   - Deployments table
   - Deployment events table
   - Time: 30 min

5. ✅ **Step 5: Build Frontend Components**
   - Deploy button + modal
   - Template selector
   - Deployments page
   - Time: 3-4 hours

6. ✅ **Step 6: Integration Testing**
   - Deploy 3 agents
   - Verify isolation
   - Check metrics
   - Time: 1 hour

---

## 📌 KEY INSIGHTS

### What We DON'T Need to Build
- ❌ Trading engine (exists ✅)
- ❌ ML model (exists ✅)
- ❌ Risk management (exists ✅)
- ❌ WebSocket infrastructure (exists ✅)
- ❌ Dashboard components (exist ✅)
- ❌ Database (exists ✅)
- ❌ Market data fetching (exists ✅)

### What We DO Need to Build
- ✅ Agent templates system (NEW - 30 min)
- ✅ Locus integration (NEW - 2 hours)
- ✅ Deployment tracking (NEW - 3 hours)
- ✅ UI for deployment (NEW - 4 hours)

### Leverage Opportunities
- ✅ Use existing EventBusV2 for deployment updates
- ✅ Use existing WebSocket for real-time deployment status
- ✅ Use existing Zustand store for deployment state
- ✅ Use existing Tailwind styling patterns
- ✅ Use existing API patterns (CORS, async, error handling)
- ✅ Use existing database connection pooling

---

## 🎯 Conclusion

**Good News:** ~90% of the infrastructure already exists! ✅

**What's Needed:** 
- 5 new backend files (~500 lines)
- 8 new frontend components (~800 lines)  
- Total new code: ~1300 lines

**Effort:** ~10.5 hours (fits Day 1-3 timeline perfectly!)

**Reusable Existing Code:** 5000+ lines of tested, production-ready code

**Risk:** Very low - only integrating Locus API, everything else is modular and tested

**Confidence:** 🟢 HIGH - Can execute this in 4-day sprint ✅

---


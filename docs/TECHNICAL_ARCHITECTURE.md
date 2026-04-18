# AURORA + Locus: Technical Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser / Dashboard                         │
│                   (Frontend - Next.js 15)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP + WebSocket
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐   ┌─────▼─────┐   ┌───▼─────────┐
      │ GET /   │   │ POST /api │   │  WebSocket  │
      │ routes  │   │ deploy... │   │  updates    │
      └────┬────┘   └─────┬─────┘   └───┬─────────┘
           │               │               │
           │               │               │
           └───────────────┼───────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   FastAPI Backend (Python)          │
        │     Port 8000                       │
        ├──────────────────────────────────────┤
        │                                      │
        │  POST /api/deploy-agent              │
        │  GET /api/deployments                │
        │  GET /api/deployment-history         │
        │  WebSocket connections               │
        │                                      │
        └──────────────┬───────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
   ┌──▼────────┐  ┌───▼────────┐  ┌──▼─────────┐
   │ Trading   │  │ Locus      │  │ Database  │
   │ Service   │  │ Deployment │  │ (SQLite)  │
   │           │  │ Service    │  │           │
   │ ML        │  │            │  │ Stores:   │
   │ Agents    │  │ Calls:     │  │ - Agents  │
   │           │  │ Locus API  │  │ - Deploy- │
   │ Paper     │  │            │  │   ments   │
   │ Trading   │  │ Returns:   │  │ - Metrics │
   │           │  │ URL + ID   │  │           │
   └───────────┘  └────┬───────┘  └───────────┘
                       │
                       │ HTTPS + Auth
                       │ Bearer $LOCUS_API_KEY
                       │
        ┌──────────────▼──────────────┐
        │   Locus API                  │
        │   api.paywithlocus.com       │
        │                              │
        │  POST /deploy (agent config) │
        │  GET /status (deployment)    │
        │  GET /logs (agent logs)      │
        │                              │
        └──────────────┬───────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │   Locus Infrastructure               │
        │   (Creates for each deployment)      │
        │                                      │
        │   ├─ PostgreSQL Database             │
        │   ├─ Redis Cache                     │
        │   ├─ SSL Certificate                 │
        │   ├─ Load Balancer                   │
        │   ├─ Monitoring                      │
        │   └─ Agent Container                 │
        │       (Agent trading in isolation)   │
        │                                      │
        └──────────────────────────────────────┘
```

---

## Data Flow: Deploy Agent

```
User clicks "Deploy to Locus"
    │
    ▼
Frontend:
  - Collects agent config (name, strategy, risk profile, symbol)
  - Shows deployment form
    │
    ▼
POST /api/deploy-agent
  {
    "agent_name": "Sigma Trading Bot",
    "strategy": "aggressive",
    "risk_profile": {
      "max_loss": 0.05,
      "position_size": 0.10,
      "max_drawdown": 0.15
    },
    "symbol": "BTC/USD"
  }
    │
    ▼
Backend: LocusDeploymentService
  1. Validate config
  2. Create deployment record (DB)
  3. Call Locus API:
     POST https://api.paywithlocus.com/api/deploy
     {
       "name": "aurora-sigma-xyz",
       "image": "aurora-trading-agent:latest",
       "env": {
         "STRATEGY": "aggressive",
         "SYMBOL": "BTC/USD",
         ...
       }
     }
  4. Get deployment_id + app_url
  5. Start polling for status
    │
    ▼
Locus Infrastructure Creates:
  ✓ PostgreSQL database (for agent state)
  ✓ Redis cache (for trading data)
  ✓ SSL certificate
  ✓ Domain: aurora-sigma-xyz.locus.app
  ✓ Load balancer
  ✓ Monitoring
    │
    ▼
Backend: Poll Status
  Loop every 3 seconds:
    GET https://api.paywithlocus.com/api/deploy/{id}/status
    
    Status: deploying → building → running
    │
    ▼ (When status = "running")
    Stop polling
    │
    ▼
Frontend: Update UI
  Broadcast via WebSocket:
  {
    "deployment_id": "xyz",
    "status": "running",
    "url": "https://aurora-sigma-xyz.locus.app",
    "created_at": timestamp
  }
    │
    ▼
Dashboard Updated:
  ✅ Sigma Trading Bot
  Status: RUNNING
  URL: aurora-sigma-xyz.locus.app
  Uptime: 0m
  
  (User can now access agent at that URL)
```

---

## Key Integration Points

### 1. Binance Integration

**Before:**
```python
from backend.execution.kraken_client import KrakenClient
```

**After:**
```python
from backend.execution.binance_client import BinanceClient

# Both use CCXT internally
# CCXT supports: Binance, Kraken, KuCoin, Coinbase, etc.
```

**Config:**
```env
EXECUTION_MODE=PAPER
DATA_SOURCE=BINANCE
BINANCE_API_KEY=...  # Optional for LIVE mode
```

---

### 2. Locus API Integration

**Service Layer:**
```python
# backend/services/locus_deployment_service.py

class LocusDeploymentService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.paywithlocus.com/api"
        
    async def deploy_agent(self, config: AgentConfig) -> DeploymentResponse:
        """
        1. Create deployment payload
        2. Call Locus /deploy endpoint
        3. Poll status endpoint
        4. Return when running
        """
        
    def _call_locus_api(self, method: str, endpoint: str, data: dict) -> dict:
        """Helper to call Locus with auth"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Call endpoint, return response
```

**API Endpoint:**
```python
@app.post("/api/deploy-agent")
async def deploy_agent(config: AgentDeploymentConfig):
    service = LocusDeploymentService(settings.locus_api_key)
    deployment = await service.deploy_agent(config)
    
    # Broadcast to frontend
    await event_bus.publish_ws("deployment", {
        "deployment_id": deployment.id,
        "status": deployment.status,
        "url": deployment.url
    })
    
    return deployment
```

---

### 3. Database Schema

```sql
-- Agents (already exist)
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT,
    strategy TEXT,
    risk_profile JSON,
    symbol TEXT,
    created_at TIMESTAMP
);

-- NEW: Track deployments
CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    status TEXT,  -- deploying / running / error / stopped
    locus_url TEXT,
    locus_deployment_id TEXT,  -- ID from Locus
    created_at TIMESTAMP,
    stopped_at TIMESTAMP,
    metrics JSON  -- uptime, requests, P&L, etc.
    
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Track deployment history
CREATE TABLE deployment_events (
    id TEXT PRIMARY KEY,
    deployment_id TEXT,
    event TEXT,  -- deployed / stopped / failed
    timestamp TIMESTAMP,
    message TEXT,
    
    FOREIGN KEY (deployment_id) REFERENCES deployments(id)
);
```

---

## Frontend Component Structure

```
frontend/
├─ app/
│  └─ [locale]/
│     ├─ dashboard/
│     │  └─ page.tsx (Main dashboard)
│     │     └─ <DeployToLocusButton /> ← NEW
│     └─ deployments/  ← NEW PAGE
│        └─ page.tsx (Shows all deployments)
│
├─ components/
│  ├─ DeployToLocusButton.tsx ← NEW
│  │  └─ Opens modal with form
│  │
│  ├─ DeploymentProgress.tsx ← NEW
│  │  └─ Shows progress bar (deploying...)
│  │
│  ├─ DeploymentSuccess.tsx ← NEW
│  │  └─ Shows URL when done
│  │
│  ├─ DeploymentError.tsx ← NEW
│  │  └─ Shows error if fails
│  │
│  └─ ... (existing components)
│
└─ lib/
   ├─ api.ts (update with deploy endpoints)
   └─ ... (existing)
```

---

## Backend Service Structure

```
backend/
├─ api/
│  └─ server.py
│     ├─ @app.post("/api/deploy-agent")
│     ├─ @app.get("/api/deployments")
│     ├─ @app.get("/api/deployment-history")
│     └─ WebSocket routes
│
├─ services/
│  ├─ locus_deployment_service.py ← NEW
│  │  └─ Deploy, track, manage agents on Locus
│  │
│  ├─ trading_service.py (existing)
│  │  └─ Integrate LocusDeploymentService
│  │
│  └─ ... (existing)
│
├─ execution/
│  ├─ binance_client.py ← NEW
│  │  └─ Replace Kraken with Binance
│  │
│  ├─ trade_executor.py (modify)
│  │  └─ Use BinanceClient
│  │
│  └─ ... (existing)
│
└─ ... (rest)
```

---

## Configuration & Environment

```env
# Trading
EXECUTION_MODE=PAPER
BINANCE_API_KEY=...  # Optional
BINANCE_SECRET=...   # Optional
DEFAULT_SYMBOL=BTC/USD

# Locus
LOCUS_API_KEY=claw_xxx_your_key
LOCUS_API_BASE=https://api.paywithlocus.com/api

# Database
DATABASE_URL=sqlite:///./aurora.db

# Server
PORT=8000
HOST=0.0.0.0
```

---

## Deployment Workflow

```
1. User creates agent (frontend form)
   name: "Sigma"
   strategy: "aggressive"
   risk_profile: {max_loss: 0.05, ...}
   symbol: "BTC/USD"

2. User clicks "Deploy to Locus" button
   
3. Frontend → POST /api/deploy-agent
   
4. Backend calls Locus API
   POST https://api.paywithlocus.com/api/deploy
   
5. Locus creates container
   - PostgreSQL for state
   - Redis for data
   - SSL certificate
   - Load balancer
   
6. Agent starts running in container
   - Connects to Binance API
   - Fetches BTC/USD data
   - Makes trading decisions
   - All isolated in Locus container
   
7. Backend gets URL from Locus
   https://aurora-sigma-xyz.locus.app
   
8. Frontend shows URL
   ✅ Agent live at: aurora-sigma-xyz.locus.app
   
9. User can:
   - Monitor agent from dashboard
   - See live trading activity
   - Stop/redeploy agent
   - Deploy more agents
```

---

## Testing Checklist

### Unit Testing
- [ ] LocusDeploymentService methods
- [ ] API endpoint with mock Locus API
- [ ] Database operations

### Integration Testing
- [ ] Full deploy flow (UI → Backend → Locus)
- [ ] Deployment status polling
- [ ] WebSocket updates to frontend

### End-to-End Testing
- [ ] Create agent → Deploy → Running
- [ ] Multiple agents simultaneously
- [ ] Stop/redeploy agents
- [ ] Dashboard shows all agents
- [ ] Real Locus API (with test account)

---

## Key Technical Decisions

| Decision | Why |
|----------|-----|
| **Binance over Kraken** | Works in India, better API |
| **PAPER mode for demo** | Safe, no real money risk |
| **Option B (button vs auto)** | More reliable for hackathon |
| **Locus API polling** | Simple, reliable status tracking |
| **SQLite for demo** | Fast setup, no infra |
| **WebSocket for updates** | Real-time UI updates |
| **Multi-tenant isolation** | Show Locus capability |

---

## Success Criteria

✅ Complete by Day 4 midnight
✅ Demo works 100% (no glitches)
✅ Code is clean and commented
✅ Pitch is clear (30 sec + 2 min versions)
✅ Video demo is engaging
✅ Submitted before deadline

---

Good luck! You've got a solid plan! 🚀


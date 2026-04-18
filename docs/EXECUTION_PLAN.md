# 🚀 AURORA + Locus Hackathon - Execution Plan

## Mission
**Win Locus hackathon track ($1000)** by deploying AI trading agents as containerized services on Locus with one-click.

---

## 📅 Timeline: 3-4 Days (12-15 hours)

```
Day 1 (Tomorrow): Foundation + Unblock (3.5 hrs)
├─ Fix frontend issues
├─ Replace Kraken → Binance
└─ Verify Locus API access

Day 2: Core Locus Integration (4 hrs)
├─ Build LocusDeploymentService
├─ Create deployment API endpoint
└─ Build frontend deploy button

Day 3: Dashboard + Testing (3.5 hrs)
├─ Create deployments dashboard
├─ Add deployment history
└─ Full end-to-end testing

Day 4: Demo + Submission (2 hrs)
├─ Record demo video
├─ Perfect pitch
└─ Submit to hackathon
```

---

## 🎯 What We're Building

**AURORA Agent Factory on Locus**

Users create AI trading agents → Click "Deploy to Locus" → Agent becomes isolated containerized service with database, cache, SSL → All in 60 seconds.

**MVP Features (3 Agent Templates):**
1. ✅ 3 pre-built agent templates: Balanced ⚖️ | Aggressive 🚀 | Conservative 🛡️
2. ✅ Deploy agents to Locus with one-click (template-based)
3. ✅ See deployment progress (60 sec estimate)
4. ✅ Access deployed agent at live URL
5. ✅ Deploy multiple agents simultaneously (multi-tenant isolation)
6. ✅ Monitor all deployed agents from dashboard
7. ✅ Stop/redeploy agents on demand

**Post-Launch (Future):** Easy to add more agent types (architecture fully extensible)

---

## 📋 PHASE 1: Foundation (Tomorrow - 3.5 hours)

### Task 1.1: Fix Frontend (1 hour)
```bash
cd frontend
npm run dev
# Should run without exit code 1
# Browser: http://localhost:3000 should load
```

**Troubleshoot**:
- Check env vars (NEXT_PUBLIC_API_URL)
- Fix build errors
- Ensure backend connection works

---

### Task 1.2: Replace Kraken → Binance (2 hours)

**Files to modify:**
```
backend/execution/binance_client.py (NEW - copy from kraken_client.py)
backend/execution/trade_executor.py (swap to Binance)
backend/utils/config.py (add BINANCE_API_KEY, BINANCE_SECRET)
.env (add Binance config)
```

**Config**:
```env
EXECUTION_MODE=PAPER
BINANCE_API_KEY=your_key_if_live_trading
BINANCE_SECRET=your_secret_if_live_trading
```

**Why?**: Kraken doesn't work in India. Binance does + better API.

---

### Task 1.3: Verify Locus (30 min)

**Get Locus API Key from:** https://app.paywithlocus.com

**Test connection:**
```bash
export LOCUS_API_KEY=claw_xxx_your_key
curl https://api.paywithlocus.com/api/pay/balance \
  -H "Authorization: Bearer $LOCUS_API_KEY"
```

Should return wallet balance (even if $0).

---

## 📦 PHASE 2: Locus Integration (Day 2 - 4 hours)

### Task 2.1: Build Locus Service (2 hours)

**New File:** `backend/services/locus_deployment_service.py`

```python
class LocusDeploymentService:
    # Pre-defined agent templates (MVP)
    AGENT_TEMPLATES = {
        "balanced": {
            "position_multiplier": 1.0,
            "max_daily_loss": 0.05,
            "entry_confidence": 0.65
        },
        "aggressive": {
            "position_multiplier": 1.5,
            "max_daily_loss": 0.10,
            "entry_confidence": 0.50
        },
        "conservative": {
            "position_multiplier": 0.5,
            "max_daily_loss": 0.02,
            "entry_confidence": 0.80
        }
    }
    
    def deploy_agent(self, agent_config):
        """
        Input:
        {
            "name": "Sigma Trading",
            "template": "aggressive",  # Use template
            "symbol": "BTC/USD"
        }
        
        Output:
        {
            "deployment_id": "uuid",
            "app_url": "https://aurora-sigma-xyz.locus.app",
            "status": "deploying"
        }
        """
        # Load template config
        # Call Locus API to deploy
        # Poll status until running
        # Return deployment details
    
    def get_deployment_status(self, deployment_id):
        # Get current status
    
    def list_deployments(self):
        # Get all agents
    
    def stop_deployment(self, deployment_id):
        # Terminate agent
```

**Key Implementation:**
- Use Locus API: `POST /deploy`
- Handle authentication with LOCUS_API_KEY
- Store deployments in database
- Track deployment state

---

### Task 2.2: Create Deployment Endpoint (1.5 hours)

**New Endpoint:** `POST /api/deploy-agent`

**Backend File:** `backend/api/server.py`

```python
@app.post("/api/deploy-agent")
async def deploy_agent(config: AgentDeploymentConfig):
    """
    Request:
    {
        "agent_name": "Sigma Trading",
        "template": "aggressive",  # Options: balanced, aggressive, conservative
        "symbol": "BTC/USD"
    }
    
    Response:
    {
        "success": true,
        "deployment": {
            "id": "uuid",
            "url": "https://aurora-sigma-abc.locus.app",
            "status": "deploying"
        }
    }
    """
    # 1. Validate input
    # 2. Load agent template config
    # 3. Call LocusDeploymentService.deploy_agent()
    # 4. Store in database
    # 5. Broadcast to frontend via WebSocket
    # 6. Return deployment details
```

---

### Task 2.3: Create Deploy Button UI (2 hours)

**New Component:** `frontend/components/DeployToLocusButton.tsx`

**User sees:**
1. Form with: Agent name + Template dropdown (3 options)
   - Balanced Trader ⚖️ (steady profit, moderate risk)
   - Aggressive Trader 🚀 (maximum profit, higher risk)
   - Guardian Trader 🛡️ (capital preservation, low risk)
2. "Deploy to Locus" button
3. On click → progress bar appears
4. Shows: "Creating PostgreSQL... Setting up Redis... Configuring SSL..."
5. When done → "✅ Agent live at: aurora-sigma-abc123.locus.app"

**Supporting Components:**
```
DeployToLocusButton.tsx (main button + modal)
DeploymentProgress.tsx (progress bar)
DeploymentSuccess.tsx (success screen with URL)
DeploymentError.tsx (error handling)
```

---

## 📊 PHASE 3: Dashboard (Day 3 - 3.5 hours)

### Task 3.1: Deployments Dashboard (1.5 hours)

**New Page:** `frontend/app/[locale]/deployments/page.tsx`

**Shows (MVP - 3 Agent Templates):**
```
Deployed Agents:

Agent 1: Sigma Aggressive 🚀
├─ Status: ✅ Running
├─ Template: Aggressive (Higher risk/reward)
├─ URL: aurora-sigma-aggressive-abc.locus.app
├─ Uptime: 2h 34m
├─ P&L: +$245.67
└─ [Stop] [Redeploy]

Agent 2: Guardian Conservative 🛡️
├─ Status: ✅ Running
├─ Template: Conservative (Capital preservation)
├─ URL: aurora-guardian-conservative-xyz.locus.app
├─ Uptime: 45m
├─ P&L: +$45.20
└─ [Stop] [Redeploy]

Agent 3: Trader Balanced ⚖️
├─ Status: ✅ Running
├─ Template: Balanced (Steady growth)
├─ URL: aurora-trader-balanced-def.locus.app
├─ Uptime: 12m
├─ P&L: +$12.50
└─ [Stop] [Redeploy]
```

**Data Source:**
- Poll `/api/deployments` endpoint
- Real-time updates via WebSocket

---

### Task 3.2: Deployment History (1 hour)

**New Endpoint:** `GET /api/deployment-history`

**Database Schema:**
```sql
CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    agent_name TEXT,
    strategy TEXT,
    status TEXT,  -- running/stopped/error
    locus_url TEXT,
    created_at TIMESTAMP,
    stopped_at TIMESTAMP,
    metrics JSON
);
```

**Shows:**
```
[2026-04-18 10:30] Sigma deployed ✅
[2026-04-18 10:15] Conservative deployed ✅
[2026-04-18 10:05] Alpha undeployed ❌
```

---

### Task 3.3: Testing (1 hour)

**Full End-to-End Test:**
- [ ] Create "Balanced" agent in UI → Deploy to Locus
- [ ] See progress bar → Deployment completes (~60 sec)
- [ ] URL is live ✅
- [ ] Create "Aggressive" agent → Deploy simultaneously
- [ ] Create "Conservative" agent → Deploy simultaneously
- [ ] All 3 agents show in dashboard with different configs
- [ ] Each has separate URL (isolated containers)
- [ ] Can stop/redeploy individual agents
- [ ] No errors in logs

---

## 🎬 PHASE 4: Demo (Day 4 - 2 hours)

### Demo Script (3-5 minutes)

```
[0:00] "AURORA: Deploy AI Trading Agents in 60 Seconds"
       Show AURORA dashboard

[0:10] "Step 1: Select Agent Template"
       Dropdown: Balanced | Aggressive | Conservative
       Select "Aggressive" (🚀 High Risk/Reward)

[0:20] "Step 2: Enter Agent Name"
       Type: "Sigma Trading Bot"

[0:25] "Step 3: Click Deploy to Locus"
       Open deployment modal
       Select "Aggressive" template

[0:30] "Watch deployment in real-time"
       Show progress:
       ✓ PostgreSQL database created
       ✓ Redis cache initialized
       ✓ SSL certificate configured
       ✓ Agent container deployed

[1:35] "Agent live in 60 seconds ✅"
       "aurora-sigma-aggressive-abc123.locus.app"

[1:50] "Deploy Agent #2: Conservative Strategy" 🛡️
       (showing multi-tenant capability)

[2:50] "Deploy Agent #3: Balanced Strategy" ⚖️
       (all three running simultaneously)

[3:30] "All agents isolated & independent"
       Show dashboard with 3 agents:
       - Different templates
       - Different URLs
       - Different strategies
       - All on Locus infrastructure

[4:00] "Problem Solved:"
       Before: Months of infrastructure work → Risky
       After: 60 seconds → Production-ready
       "That's agent-native deployment" 🚀

[4:10] END
```

---

## 📁 Files to Create/Modify

### New Files (~600 lines):
```
backend/services/locus_deployment_service.py     (180 lines)
backend/execution/binance_client.py              (150 lines)
frontend/components/DeployToLocusButton.tsx      (140 lines)
frontend/components/DeploymentProgress.tsx       (80 lines)
frontend/app/[locale]/deployments/page.tsx       (100 lines)
```

### Modified Files (~100 lines):
```
backend/api/server.py                 (add deploy endpoint)
backend/utils/config.py               (add env vars)
backend/services/trading_service.py   (integrate Locus)
.env                                  (config)
frontend/app/[locale]/dashboard/page.tsx (add button)
```

---

## ✅ Success Checklist

### After Day 1:
- [ ] Frontend runs without errors
- [ ] Binance trading working
- [ ] Locus API responds with balance
- [ ] 3 agent templates defined (Balanced, Aggressive, Conservative)

### After Day 2:
- [ ] Can click "Deploy to Locus" button
- [ ] Progress bar shows
- [ ] Deployment completes
- [ ] URL returned and accessible

### After Day 3:
- [ ] Dashboard shows deployed agents
- [ ] Can deploy multiple agents
- [ ] Can stop/redeploy
- [ ] All features working

### Before Submission:
- [ ] Demo video recorded (3-5 min)
- [ ] No errors in full test
- [ ] Code pushed to GitHub
- [ ] Pitch written
- [ ] Submitted before deadline

---

## 🎯 Killer Pitch

**30 seconds:**
```
"AURORA lets users create AI trading agents 
and deploy them to production without DevOps.

With Locus: Deploy agent → Container with database + cache + SSL → 
Live in 60 seconds.

One button. No infrastructure headaches.

This is agent-native deployment."
```

**Bonus:**
```
"Deploy multiple agents simultaneously — 
each isolated, each trading independently."
```

---

## ⚠️ Key Risks & Mitigations

| Risk | Fix |
|------|-----|
| Locus API fails | Show error, allow retry |
| Deployment takes >2 min | Accept it, explain why |
| Frontend bugs | Use simple button approach |
| Time runs out | Focus on core 3 features |
| Binance integration breaks | Fallback to SIMULATED mode |

---

## 🚀 Ready to Start?

**Tomorrow morning:**
1. Open 2 terminals
2. Backend: `python -m backend.main`
3. Frontend: `cd frontend && npm run dev`
4. Start with Task 1.1: Fix any frontend issues

**Questions? Check logs, test each piece, iterate fast.**

Good luck! You've got this! 🎉


# 📋 Daily Checklist - AURORA + Locus Hackathon

**Timeline:** 3-4 days (3-4 hours/day)  
**Goal:** Deploy AI trading agents on Locus with one-click  
**Deadline:** Day 4 midnight (submission)

---

## 📅 DAY 1 (Tomorrow) - Foundation & Unblock
**Time Allocation:** 3.5 hours  
**Goal:** Get project running + Binance working

### ✅ Task 1.1: Fix Frontend (1 hour)

**What to do:**
- [ ] Open terminal in `frontend/` directory
- [ ] Run: `npm run dev`
- [ ] Check browser: http://localhost:3000
- [ ] Should load dashboard without errors
- [ ] Can see trading UI with paper trades

**Troubleshooting if error:**
- [ ] Check if `.env` file exists with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Try: `npm install` again
- [ ] Check if backend is running (other terminal)
- [ ] Look at terminal error message - fix specific issue

**Success:** ✅ Frontend runs, no exit code errors

---

### ✅ Task 1.2: Replace Kraken → Binance (2 hours)

**Step 1: Create new Binance client (30 min)**
- [ ] Copy `backend/execution/kraken_client.py` → `backend/execution/binance_client.py`
- [ ] Replace "Kraken" with "Binance" in class name
- [ ] Update to use CCXT Binance support
- [ ] Keep same interface (place_order, get_balance, etc.)

**Step 2: Update config (30 min)**
- [ ] Edit `backend/utils/config.py`:
  - [ ] Add: `binance_api_key = os.getenv("BINANCE_API_KEY", "")`
  - [ ] Add: `binance_secret = os.getenv("BINANCE_SECRET", "")`
- [ ] Edit `.env`:
  ```env
  BINANCE_API_KEY=your_key_or_leave_empty
  BINANCE_SECRET=your_secret_or_leave_empty
  ```

**Step 3: Update trade executor (1 hour)**
- [ ] Edit `backend/execution/trade_executor.py`:
  - [ ] Replace: `from backend.execution.kraken_client import KrakenClient`
  - [ ] With: `from backend.execution.binance_client import BinanceClient`
  - [ ] Update: `self.kraken_client` → `self.binance_client`
  - [ ] Update initialization

**Step 4: Test Binance (30 min)**
- [ ] Restart backend: `python -m backend.main`
- [ ] Check logs - no Kraken errors
- [ ] Dashboard should show BTC/USD data (Binance prices)
- [ ] Paper trades should execute with Binance prices

**Success:** ✅ Trading works with Binance data, no Kraken errors

---

### ✅ Task 1.3: Verify Locus Credentials (30 min)

**Step 1: Get API Key**
- [ ] Go to: https://app.paywithlocus.com
- [ ] Login with your account
- [ ] Navigate to: Settings → API Keys
- [ ] Click: "Generate New Key"
- [ ] Copy key (starts with `claw_`)
- [ ] Save somewhere safe (only shown once!)

**Step 2: Add to `.env`**
- [ ] Edit `.env`:
  ```env
  LOCUS_API_KEY=claw_xxx_paste_your_key_here
  LOCUS_API_BASE=https://api.paywithlocus.com/api
  ```

**Step 3: Test Connection**
- [ ] Open terminal
- [ ] Run:
  ```bash
  curl https://api.paywithlocus.com/api/pay/balance \
    -H "Authorization: Bearer $LOCUS_API_KEY"
  ```
- [ ] Should return: `{"balance": "...", ...}` (even if $0)
- [ ] NOT a 401 error

**Success:** ✅ Locus API responding with wallet balance

---

### 🎯 Day 1 Checkpoint

Before moving to Day 2, confirm:
- [ ] Frontend running at http://localhost:3000
- [ ] Backend running without Kraken errors
- [ ] Binance prices showing in dashboard
- [ ] Paper trades executing
- [ ] Locus API responds to balance check
- [ ] 3 agent templates defined (Balanced, Aggressive, Conservative)
- [ ] No errors in logs

**Status:** ✅ READY FOR DAY 2?

---

## 📅 DAY 2 - Locus Integration
**Time Allocation:** 4 hours  
**Goal:** Build deployment service + API + UI

### ✅ Task 2.1: Create Locus Deployment Service (2 hours)

**Create new file:** `backend/services/locus_deployment_service.py`

**Code template:**
```python
import httpx
import asyncio
from typing import Optional

class LocusDeploymentService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.paywithlocus.com/api"
    
    async def deploy_agent(self, config: dict) -> dict:
        """
        config: {
            "name": "sigma-agent",
            "strategy": "aggressive",
            "risk_profile": {...},
            "symbol": "BTC/USD"
        }
        """
        # 1. Build deployment payload
        payload = {
            "name": config["name"],
            "image": "aurora-trading-agent:latest",
            "env": {
                "STRATEGY": config["strategy"],
                "SYMBOL": config["symbol"],
                "RISK_PROFILE": str(config["risk_profile"])
            }
        }
        
        # 2. Call Locus API
        deployment = await self._call_locus_api("POST", "/deploy", payload)
        deployment_id = deployment["id"]
        
        # 3. Poll for status
        for attempt in range(60):  # Max 5 minutes
            status = await self._call_locus_api("GET", f"/deploy/{deployment_id}", {})
            if status["status"] == "running":
                return {
                    "deployment_id": deployment_id,
                    "app_url": status["app_url"],
                    "status": "running",
                    "created_at": status["created_at"]
                }
            await asyncio.sleep(5)  # Poll every 5 seconds
        
        return {
            "deployment_id": deployment_id,
            "status": "deploying",
            "app_url": None
        }
    
    async def get_status(self, deployment_id: str) -> dict:
        """Get current status of deployment"""
        return await self._call_locus_api("GET", f"/deploy/{deployment_id}", {})
    
    async def list_deployments(self) -> list:
        """List all deployments"""
        result = await self._call_locus_api("GET", "/deploy", {})
        return result.get("deployments", [])
    
    async def stop_deployment(self, deployment_id: str) -> bool:
        """Stop a deployment"""
        await self._call_locus_api("DELETE", f"/deploy/{deployment_id}", {})
        return True
    
    async def _call_locus_api(self, method: str, endpoint: str, data: dict) -> dict:
        """Helper to call Locus with auth"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            
            if response.status_code in (200, 201):
                return response.json()
            else:
                raise Exception(f"Locus API error: {response.text}")
```

**Checklist:**
- [ ] File created: `backend/services/locus_deployment_service.py`
- [ ] All methods implemented
- [ ] Auth header with Bearer token
- [ ] Polling logic for status
- [ ] Error handling

**Success:** ✅ Service ready to call Locus API

---

### ✅ Task 2.2: Create Deployment API Endpoint (1.5 hours)

**Edit:** `backend/api/server.py`

**Add endpoint:**
```python
from pydantic import BaseModel
from backend.services.locus_deployment_service import LocusDeploymentService

class AgentDeploymentConfig(BaseModel):
    agent_name: str
    template: str  # balanced | aggressive | conservative
    symbol: str = "BTC/USD"

@app.post("/api/deploy-agent")
async def deploy_agent(config: AgentDeploymentConfig):
    """Deploy agent to Locus with pre-defined template"""
    try:
        locus = LocusDeploymentService(app.state.settings.locus_api_key)
        deployment = await locus.deploy_agent(config.dict())
        
        # Store in database
        # broadcast_via_websocket
        
        return {
            "success": True,
            "deployment": deployment
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/deployments")
async def get_deployments():
    """Get all active deployments"""
    locus = LocusDeploymentService(app.state.settings.locus_api_key)
    deployments = await locus.list_deployments()
    return {"deployments": deployments}

@app.get("/api/deployment-history")
async def get_deployment_history():
    """Get deployment history from database"""
    # Query database for all deployment events
    pass
```

**Checklist:**
- [ ] Endpoint added to `server.py`
- [ ] Takes template name (balanced/aggressive/conservative)
- [ ] Calls LocusDeploymentService
- [ ] Returns deployment details
- [ ] Error handling implemented

**Success:** ✅ API endpoints responding

**Test locally:**
```bash
curl -X POST http://localhost:8000/api/deploy-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "test-agent",
    "template": "aggressive",
    "symbol": "BTC/USD"
  }'
```

Should return: `{"success": true, "deployment": {...}}`

---

### ✅ Task 2.3: Build Frontend Deploy Button (2 hours)

**Create:** `frontend/components/DeployToLocusButton.tsx`

**Features:**
- [ ] 3 agent templates in dropdown: Balanced | Aggressive | Conservative
- [ ] Agent name input
- [ ] Deploy button
- [ ] Progress bar during deployment
- [ ] Success screen with live URL

**Key Code Structure:**
```typescript
'use client';
import { useState } from 'react';

const AGENT_TEMPLATES = {
  balanced: { label: 'Balanced ⚖️', config: {...} },
  aggressive: { label: 'Aggressive 🚀', config: {...} },
  conservative: { label: 'Guardian 🛡️', config: {...} }
};

export function DeployToLocusButton() {
  const [selectedTemplate, setSelectedTemplate] = useState('balanced');
  const [agentName, setAgentName] = useState('');
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentUrl, setDeploymentUrl] = useState(null);
  
  async function handleDeploy() {
    // POST to /api/deploy-agent with template
    // Show progress
    // Display URL on success
  }
  
  return (
    <div className="p-6 border rounded-lg">
      <select value={selectedTemplate} onChange={...}>
        {/* 3 templates */}
      </select>
      <input placeholder="Agent name" />
      <button onClick={handleDeploy}>Deploy</button>
      {/* Progress + Success/Error states */}
    </div>
  );
}
```
          <p>Agent live at: <a href={deploymentUrl} target="_blank">{deploymentUrl}</a></p>
        </div>
      )}
      
      {error && <div className="bg-red-100 p-4 rounded text-red-700">{error}</div>}
      
      {!isDeploying && !deploymentUrl && (
        <button
          onClick={() => handleDeploy({
            agent_name: "Sigma",
            strategy: "aggressive",
            risk_profile: {max_loss: 0.05},
            symbol: "BTC/USD"
          })}
          className="px-6 py-3 bg-blue-500 text-white rounded font-bold hover:bg-blue-600"
        >
          Deploy Agent to Locus
        </button>
      )}
    </div>
  );
}
```

**Checklist:**
- [ ] Component created
- [ ] Button clickable
- [ ] Calls `/api/deploy-agent` endpoint
- [ ] Shows loading state
- [ ] Displays URL when done
- [ ] Shows errors

**Add to dashboard:**
- [ ] Edit: `frontend/app/[locale]/dashboard/page.tsx`
- [ ] Import: `import { DeployToLocusButton } from '@/components/DeployToLocusButton'`
- [ ] Add: `<DeployToLocusButton />` to page

**Success:** ✅ Button visible, clickable, calls API

---

### 🎯 Day 2 Checkpoint

Before Day 3:
- [ ] LocusDeploymentService created
- [ ] API endpoints responding
- [ ] Button visible in dashboard
- [ ] Can click button without errors
- [ ] Backend logs show API calls
- [ ] Testing against Locus test account

**Status:** ✅ READY FOR DAY 3?

---

## 📅 DAY 3 - Dashboard & Testing
**Time Allocation:** 3.5 hours  
**Goal:** Complete dashboard + full end-to-end test

### ✅ Task 3.1: Build Deployments Dashboard (1.5 hours)

**Create:** `frontend/app/[locale]/deployments/page.tsx`

**Shows list of deployed agents:**
```typescript
'use client';

import { useEffect, useState } from 'react';

interface Deployment {
  id: string;
  agent_name: string;
  status: string;
  app_url: string;
  created_at: string;
  metrics: {
    uptime: string;
    requests: number;
    pnl: number;
  };
}

export default function DeploymentsPage() {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  
  useEffect(() => {
    // Poll /api/deployments every 5 seconds
    const interval = setInterval(async () => {
      const response = await fetch('http://localhost:8000/api/deployments');
      const data = await response.json();
      setDeployments(data.deployments || []);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Deployed Agents</h1>
      
      <div className="grid gap-4">
        {deployments.map(dep => (
          <div key={dep.id} className="border rounded-lg p-4">
            <h2 className="text-xl font-bold">{dep.agent_name}</h2>
            <p>Status: <span className={dep.status === 'running' ? 'text-green-600' : 'text-gray-600'}>{dep.status}</span></p>
            <p>URL: <a href={dep.app_url} target="_blank">{dep.app_url}</a></p>
            <p>Uptime: {dep.metrics?.uptime}</p>
            <p>P&L: ${dep.metrics?.pnl}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Checklist:**
- [ ] Page created
- [ ] Lists all deployments
- [ ] Shows status for each
- [ ] Shows live URL
- [ ] Auto-refreshes every 5 sec
- [ ] Styled nicely

---

### ✅ Task 3.2: Add Deployment History (1 hour)

**Track deployments in database:**
```python
# In backend/services/trading_service.py or new file

class DeploymentTracker:
    def __init__(self, db):
        self.db = db
    
    async def record_deployment(self, agent_name, locus_id, url):
        """Save deployment event"""
        # INSERT INTO deployments ...
        
    async def get_history(self, limit=50):
        """Get deployment history"""
        # SELECT * FROM deployments ORDER BY created_at DESC
```

**Endpoint:**
```python
@app.get("/api/deployment-history")
async def get_history():
    # Query database
    # Return history
```

**Checklist:**
- [ ] Database schema updated
- [ ] Deployments table exists
- [ ] Record on_deploy() function works
- [ ] Endpoint returns history
- [ ] Shows in dashboard/logs

---

### ✅ Task 3.3: Full End-to-End Testing (1 hour)

**Test Flow - Deploy All 3 Agent Templates:**

1. **Deploy Template 1 - Balanced ⚖️:**
   - [ ] Click "Deploy Agent"
   - [ ] Select template: "Balanced"
   - [ ] Enter name: "Trader Balanced"
   - [ ] URL: aurora-trader-balanced-abc.locus.app
   - [ ] Status: RUNNING ✅
   
2. **Deploy Template 2 - Aggressive 🚀:**
   - [ ] Click "Deploy Agent"
   - [ ] Select template: "Aggressive"
   - [ ] Enter name: "Sigma Aggressive"
   - [ ] URL: aurora-sigma-aggressive-xyz.locus.app
   - [ ] Status: RUNNING ✅
   
3. **Deploy Template 3 - Conservative 🛡️:**
   - [ ] Click "Deploy Agent"
   - [ ] Select template: "Conservative"
   - [ ] Enter name: "Guardian Conservative"
   - [ ] URL: aurora-guardian-conservative-def.locus.app
   - [ ] Status: RUNNING ✅
   
4. **Dashboard Verification:**
   - [ ] All 3 agents in deployments list
   - [ ] Each has different URL (isolated)
   - [ ] Each shows correct template
   - [ ] Can see metrics for all 3

5. **Stop/Redeploy Test:**
   - [ ] Stop one agent
   - [ ] Redeploy it
   - [ ] Status cycles properly

**Checklist:**
- [ ] All 3 templates deploy successfully
- [ ] Each has separate URL (proven isolation)
- [ ] All show in dashboard
- [ ] Different configs applied
- [ ] URLs accessible in browser
- [ ] No errors in logs
- [ ] Can stop/redeploy each independently

**Success:** ✅ Full system working end-to-end

---

### 🎯 Day 3 Checkpoint

Before Day 4:
- [ ] Dashboard showing all 3 deployed agents
- [ ] Each agent has separate URL (isolated containers)
- [ ] Deployment history tracked
- [ ] All 3 templates tested (Balanced, Aggressive, Conservative)
- [ ] Full E2E test passed (all agents deployed + running)
- [ ] No errors in logs
- [ ] Stop/redeploy working for each agent

**Status:** ✅ READY FOR DAY 4?

---

## 📅 DAY 4 - Demo & Submission
**Time Allocation:** 2 hours  
**Goal:** Record demo + Submit

### ✅ Task 4.1: Record Demo Video (1 hour)

**What to record:**
- [ ] Open dashboard in browser
- [ ] Create new agent "Sigma Trading Bot"
- [ ] Click "Deploy to Locus"
- [ ] Show progress bar (60+ seconds)
- [ ] Agent deployed successfully
- [ ] Show URL (aurora-sigma-xyz.locus.app)
- [ ] Deploy 2nd agent simultaneously
- [ ] Show deployments dashboard with both agents
- [ ] Explain in voiceover: "That's agent-native deployment"

**Demo script (3-5 min):**
```
[0:00] "AURORA: AI Agent Factory"
[0:15] Create agent + Click Deploy
[0:30] Show progress
[1:35] Agent live at aurora-sigma-xyz.locus.app
[1:45] Deploy 2nd agent
[2:30] Show dashboard with both
[3:00] "With Locus: 60 seconds. Without: 2 weeks DevOps."
```

**Recording tools:**
- [ ] Use OBS Studio (free)
- [ ] Or Loom (web-based)
- [ ] Or ScreenFlow (Mac)

**Checklist:**
- [ ] Video recorded (3-5 min)
- [ ] Clear audio/voiceover
- [ ] No glitches shown
- [ ] Shows full flow
- [ ] Final URL shown
- [ ] Saved to file

---

### ✅ Task 4.2: Prepare Submission (1 hour)

**Code prep:**
- [ ] Git commit: `git add -A && git commit -m "AURORA + Locus hackathon submission"`
- [ ] Push to GitHub: `git push origin master`
- [ ] Verify all code is pushed

**Documentation:**
- [ ] README.md explains project
- [ ] EXECUTION_PLAN.md in repo
- [ ] TECHNICAL_ARCHITECTURE.md in repo

**Video:**
- [ ] Upload to YouTube (unlisted or public)
- [ ] Get URL

**Pitch:**
- [ ] Write 30-second pitch
- [ ] Write 2-minute pitch

**Submission form:**
- [ ] Project name: "AURORA AI Agent Factory"
- [ ] Description: Elevator pitch
- [ ] GitHub URL: Your repo link
- [ ] Demo video URL: YouTube link
- [ ] Team size: 1 person
- [ ] Any dependencies: Locus account required

**Checklist:**
- [ ] Code pushed to GitHub
- [ ] Demo video uploaded
- [ ] README complete
- [ ] Pitch written
- [ ] Form ready to submit
- [ ] Submit BEFORE deadline!

**🎉 SUCCESS - YOU'RE DONE!**

---

## 📊 Summary by Day

| Day | Hours | Focus | Deliverable |
|-----|-------|-------|-------------|
| **Day 1** | 3.5 | Foundation | ✅ Frontend + Binance + Locus API |
| **Day 2** | 4 | Locus Integ | ✅ Deploy button + API endpoints |
| **Day 3** | 3.5 | Dashboard | ✅ Full E2E working, 2 agents deployed |
| **Day 4** | 2 | Demo + Submit | ✅ Video + submission |
| **Total** | **13** | **Build** | **🏆 Hackathon submission** |

---

## ⚠️ If Behind Schedule

**Priority order (do these first):**
1. ✅ Get E2E working (Day 1-2)
2. ✅ Deploy 2 agents (Day 2-3)
3. ✅ Record working demo (Day 3)
4. ⭐ Submit before deadline (Day 4)

**Skip if running late:**
- ❌ Perfect styling (works is enough)
- ❌ Full error handling (basic is fine)
- ❌ All features (core 3 is enough)
- ❌ Multiple exchanges (Binance is enough)

---

**You've got this! Let's go! 🚀**


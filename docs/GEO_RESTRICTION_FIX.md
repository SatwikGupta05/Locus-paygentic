# ✅ Geo-Restriction Fix for India

## Problem
```
451 - Service unavailable from restricted location
Binance API is geo-blocked in India
```

## Root Cause
Binance restricts API access from certain countries (including India) due to regulatory restrictions. When you try to connect, you get a **451 error** (Unavailable for Legal Reasons).

## Solution Implemented
We've implemented **automatic regional awareness** with fallback to **KuCoin** for India users:

### 1. BinanceClient - Now India-Aware ✅
- **Before**: Always tried Binance first (blocked in India)
- **After**: 
  - Detects `region="india"` parameter
  - Pre-emptively switches to KuCoin
  - Gracefully handles 451 errors at runtime
  - Falls back to KuCoin if 451 error occurs

### 2. MarketFetcher - Regional Detection ✅
- **Added**: `region` parameter (default: "india")
- **Behavior**:
  - If Binance is requested from India → automatically use KuCoin
  - Works with failover system for automatic exchange switching
  - Default exchange changed from "kraken" to "kucoin" (better for India)

### 3. Configuration - Regional Settings ✅
- **Added** `USER_REGION` to `.env` (default: "india")
- **Added** `user_region` to config (reads from env)
- **Used** in all services for consistent regional awareness

### 4. Services Updated ✅
- `TradingService`: Uses `settings.user_region`
- `TradingEngineV2`: Uses `settings.user_region`
- `MarketFetcher`: Initialized with region awareness
- `BinanceClient`: Initialized with region awareness

## Exchange Priority for India
```
1. KuCoin ← PRIMARY (works from India)
2. Kraken ← BACKUP (may also be geo-blocked)
3. Binance ← FALLBACK (only if VPN or via failover recovery)
```

## How It Works

### Scenario 1: Normal Operation from India
```
Backend starts
  ↓
BinanceClient initialized with region="india"
  ↓
Detects india region → pre-emptively uses KuCoin
  ↓
All trading uses KuCoin (no 451 errors)
  ✅ Trading works with real KuCoin data
```

### Scenario 2: Runtime 451 Error (Failover)
```
Request made to exchange
  ↓
Server returns 451 (geo-blocked)
  ↓
BinanceClient catches PermissionDenied exception
  ↓
Identifies "451" or "restricted location" in error
  ↓
Switches exchange to KuCoin
  ↓
Retries operation with KuCoin
  ✅ Trade continues seamlessly
```

## Configuration

### For India Users (Default ✅)
```env
USER_REGION=india
BINANCE_API_KEY=            # Leave empty (paper trading)
BINANCE_SECRET=             # Leave empty (paper trading)
```
**Result**: Uses KuCoin automatically

### For Other Regions
```env
USER_REGION=default         # USA, EU, etc.
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
```
**Result**: Uses Binance (unless geo-blocked)

### For VPN Users (If using VPN to access Binance)
```env
USER_REGION=default         # Override to prevent KuCoin switch
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
```
**Result**: Uses Binance via VPN

## Key Files Modified

| File | Changes |
|------|---------|
| `backend/execution/binance_client.py` | Added region param, 451 error handling, KuCoin fallback |
| `backend/data/market_fetcher.py` | Added region param, auto-switch Binance→KuCoin for India |
| `backend/services/trading_service.py` | Pass `settings.user_region` to clients |
| `backend/workers/trading_engine_v2.py` | Pass `settings.user_region` to clients |
| `backend/utils/config.py` | Added `user_region` setting |
| `.env` | Added `USER_REGION=india` |

## Testing the Fix

### 1. Start Backend
```bash
python -m backend.main
```

Expected logs:
```
[AURORA] Binance is geo-blocked in India, using KuCoin instead
[AURORA] Market fetcher using multi-exchange failover
```

### 2. Check Dashboard
```
http://localhost:3000
```

Expected:
- ✅ Dashboard loads without errors
- ✅ Price updates show BTC/USD from KuCoin
- ✅ Paper trades execute successfully
- ✅ No 451 errors in logs or console

### 3. Monitor Logs
```bash
# Should see:
2026-04-17 10:15:23 - [AURORA] Market fetcher: fetching BTC/USD from KuCoin
2026-04-17 10:15:24 - [AURORA] Price updated: $67,450.25
2026-04-17 10:15:25 - [AURORA] Paper trade executed: BUY 0.05 BTC
```

### 4. Check Exchange Info
In the logs, you should see:
```
Exchange: kucoin (not binance)
Mode: Paper Trading
Data Mode: LIVE
Status: ✅ Connected
```

## Fallback System
Even with the pre-emptive KuCoin switch, the system has a 3-layer fallback:

1. **KuCoin** (primary for India)
2. **Kraken** (backup)
3. **Synthetic data** (last resort)

If KuCoin fails, the system automatically tries Kraken, then falls back to simulated data.

## Paper Trading Works ✅
All of this works in **PAPER MODE** without any API keys:
- Real market data from KuCoin
- Simulated trading with realistic fees/slippage
- Perfect for testing before live trading

## Live Trading (When Ready)
To trade live with Binance from India, you would need:
1. **VPN to a supported country** (USA, EU, etc.)
2. OR **Use KuCoin API keys** instead
3. OR **Use a proxy service**

For this hackathon, **PAPER TRADING** with KuCoin data is perfect!

## Summary
✅ **Fixed**: Binance geo-blocking in India  
✅ **Implemented**: Regional awareness across all services  
✅ **Fallback**: Automatic KuCoin switch for India  
✅ **Testing**: Paper trading ready with KuCoin data  
✅ **Configuration**: Flexible USER_REGION setting  

**Status**: 🟢 **READY TO RUN**

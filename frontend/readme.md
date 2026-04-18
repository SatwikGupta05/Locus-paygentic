# AI Trading Agent Dashboard

Production-style Next.js 14 dashboard for an autonomous trading agent with live market data from Kraken, Binance, and KuCoin, plus ERC-8004 on-chain state via `ethers` v6.

## Stack

- Next.js 14 App Router
- TypeScript strict mode
- Zustand for client state
- TanStack React Query v5 for polling
- Native browser WebSockets for market feeds
- Axios in server route handlers for signed private REST calls
- Chart.js 4 with `react-chartjs-2`
- `ethers` v6 for on-chain reads
- CSS Modules with a dark theme
- JetBrains Mono via Google Fonts

## Project Structure

```text
app/
  api/
    agent/state/route.ts
    binance/{balance,orders,trades}/route.ts
    contract/route.ts
    kraken/{balance,orders,trades}/route.ts
    kucoin/{balance,orders,trades,ws-token}/route.ts
  globals.css
  layout.tsx
  page.tsx
components/
  charts/
  dashboard/
  ExchangeSelector.tsx
  TopBar.tsx
hooks/
lib/
  analytics/
  contract/
  rest/
  ws/
store/
types/
utils/
```

## Environment Variables

Create `.env.local` in the project root:

```env
# Kraken
KRAKEN_API_KEY=
KRAKEN_API_SECRET=

# Binance
BINANCE_API_KEY=
BINANCE_API_SECRET=

# KuCoin
KUCOIN_API_KEY=
KUCOIN_API_SECRET=
KUCOIN_API_PASSPHRASE=

# Chain
RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
AGENT_CONTRACT_ADDRESS=0xYourERC8004ContractAddress

# Agent backend
AGENT_BACKEND_URL=http://localhost:8000

# Public
NEXT_PUBLIC_AGENT_WALLET=0xAgentWalletAddress
NEXT_PUBLIC_OPERATOR_WALLET=0xOperatorWalletAddress
NEXT_PUBLIC_TRADING_PAIR=BTC/USDT
NEXT_PUBLIC_KRAKEN_WS=wss://ws.kraken.com/v2
NEXT_PUBLIC_BINANCE_WS=wss://stream.binance.com:9443/ws
```

Secrets must stay in server-side route handlers only. Do not expose exchange keys or RPC secrets through `NEXT_PUBLIC_*`.

## Install And Run

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## ERC-8004 Contract Wiring

The on-chain reader lives in `lib/contract/erc8004Reader.ts`.

- Set `RPC_URL` to a working Ethereum RPC endpoint.
- Set `AGENT_CONTRACT_ADDRESS` to your deployed ERC-8004-compatible contract.
- The route handler at `app/api/contract/route.ts` reads all contract view functions and revalidates every 30 seconds.
- On-chain scores are divided by `100` client-side.
- `allocatedCapital` is formatted from 6-decimal USDT units.

## Agent Backend Wiring

The dashboard expects your local agent backend to expose:

```text
GET {AGENT_BACKEND_URL}/state
```

Expected response shape:

```json
{
  "decision": "BUY",
  "confidence": 0.81,
  "tradeType": "STRONG",
  "positionSize": 0.14,
  "targetExchange": "binance",
  "explanation": "Momentum and spread alignment support the long setup.",
  "technicalScore": 8.4,
  "sentimentScore": 0.67,
  "mlPrediction": 0.021,
  "riskApproved": true,
  "reasoningBullets": ["...", "..."],
  "pipelineStage": "VALIDATE_RISK",
  "intentPrice": 67400,
  "intentCreatedAt": 1713000000000,
  "activityFeed": [
    { "time": "14:32", "text": "Order routed to Binance", "type": "trade" }
  ]
}
```

`targetExchange` is required so the dashboard can show which venue the agent selected.

## Exchange API Permissions

Use read permissions for balance, order, and trade history access. If you later place live orders from the same key set, trading permissions must also be enabled.

### Kraken

- Required for this dashboard: account read access
- If you also route orders: add trade permission
- Practical setup: enable read + trade

### Binance

- Required for this dashboard: read account and trade history
- If you also route spot orders: enable Spot & Margin Trading only if your setup needs it
- Practical setup: read + spot trading
- Binance private REST calls usually require API key IP whitelisting
- For local dev, whitelist your current outbound IP
- For deployment, whitelist your server or platform egress IP

### KuCoin

- Required for this dashboard: general account and trade read access
- If you also route orders: add trade permission
- Practical setup: general + trade
- KuCoin also requires the API passphrase and a server-side WS token fetch

## Live Data Notes

- Kraken uses WS v2 subscriptions for `ticker` and `ohlc`
- Binance uses the combined stream for `btcusdt@ticker` and `btcusdt@kline_1m`
- KuCoin fetches a server-issued public token from `/api/kucoin/ws-token` before opening the socket
- Best bid/ask is recomputed whenever any exchange updates
- Disabling an exchange in the selector removes it from best-price aggregation

## Operational Notes

- If all three market feeds go down, the dashboard shows an offline banner
- Contract failures degrade chain-derived fields
- Agent backend failures keep the last known decision and mark it stale
- Health states are derived from connection state plus time since last message

## Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
npm run typecheck
```

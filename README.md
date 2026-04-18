# AURORA AI Trading Agents

AURORA is a modular, autonomous AI trading system built for seamless live crypto market execution, ERC-8004 intent signing, and high-performance ML predictions. It dynamically predicts market opportunities and manages risk for leaderboard competitions.

## Features

- **3-Tier Opportunistic Execution Engine**: Classifies market signals into STRONG, WEAK, or HOLD categories, optimizing trade frequency and maximizing leaderboard rankings with strict risk guardrails.
- **ERC-8004 On-Chain Integrations**: Full trustless architecture with verifiable on-chain identity and intent signing.
- **Kraken CLI Integrated Trading**: Connects securely to the Kraken exchange for robust trade execution. 
- **Non-blocking Event-driven Pipeline**: A production-grade event architecture preventing I/O bottlenecks in live trading environments.
- **Bloomberg-style Trading Dashboard**: A rich, responsive React/Next.js interface displaying real-time metrics, historical trades, performance, and ML insights.

## Architecture

AURORA is composed of a FastAPI microservice backend and a high-performance Next.js frontend, separated for extreme modularity and scalability.

```text
backend/
  api/          # FastAPI web server and dependency injection
  workers/      # Background trading and execution workers
  services/     # Core services, runtime state, and event bus
  agents/       # Multi-agent architecture (scout, analyst, risk)
  data/         # Market data fetching and feature engineering
  ml/           # Machine learning models, training, and predicting routines
  engine/       # Decision engine and portfolio management
  blockchain/   # ERC-8004 compliant intent routers and signers
  execution/    # Execution logic, Kraken REST/WS wrappers, paper trading
  database/     # SQLite/PostgreSQL connectors and migrations

frontend/
  app/          # Next.js 14 App Router
  components/   # React functional UI components
  lib/          # Shared utilities and custom hooks
```

## Setup & Installation

### Backend

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Generate training artifacts & historical checkpoints
python backend/ml/train.py
python backend/ml/backtest.py

# Launch the API server and workers
python backend/main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

- `GET /market` - Discover current live market parameters.
- `GET /decision` - Review the engine's real-time risk/trade decision.
- `GET /trades` - List historical executions and performance metrics.
- `GET /metrics` - Pull active runtime and ML accuracy stats.
- `GET /intents` - ERC-8004 intents cache and router states.
- `WS /ws/market` - Live WebSocket stream for market data ticks.
- `WS /ws/trades` - Real-time execution updates and logging.
- `WS /ws/decisions` - Live pipeline inference broadcasts.
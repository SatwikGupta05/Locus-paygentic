import { create } from "zustand";

export interface CandleData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface MarketData {
  symbol: string;
  price: number;
  source?: string;
  mode?: string;
  candles: CandleData[];
}

export interface ExplainabilityData {
  ml_prediction?: {
    prob_up?: number;
    prob_down?: number;
  };
  sentiment?: {
    sentiment_score?: number;
    source?: string;
  };
  technical?: {
    technical_score?: number;
    signal?: string;
  };
  risk?: {
    pre_trade_approved?: boolean;
    pre_trade_reason?: string;
    position_size?: number;
    circuit_breaker?: Record<string, unknown>;
  };
  volatility_regime?: string;
  position_size?: number;
}
export interface AgentNarrative {
  decision: string;
  confidence_level: string;
  capital_allocation: string;
  risk_warning?: string | null;
  opportunity_description: string;
  expected_edge: string;
  exit_condition: string;
}

export interface DecisionData {
  symbol: string;
  action: string;
  confidence: number;
  composite_score: number;
  audit?: {
    narrative?: AgentNarrative;
    decision_trace?: string;
    [key: string]: unknown;
  };
  intent_hash?: string;
  execution_result?: {
    status?: string;
    fill_price?: number;
    [key: string]: unknown;
  };
  explainability?: ExplainabilityData;
  risk_override?: string;
}


export interface PipelineEvent {
  stage: string;
  data: Record<string, unknown>;
}

export interface PortfolioMetrics {
  balance: number;
  equity: number;
  unrealized_pnl: number;
  daily_realized_pnl: number;
  drawdown_pct: number;
  open_positions: number;
  gross_exposure: number;
}

export interface RuntimeMetrics {
  portfolio?: PortfolioMetrics;
  identity?: Record<string, unknown>;
  mode?: string;
  data_mode?: string;
  circuit_breaker?: Record<string, unknown>;
  total_pnl?: number;
  sharpe?: number;
  win_rate?: number;
  max_drawdown?: number;
}

export interface ReputationData {
  win_rate: number;
  profit_factor: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  avg_confidence?: number;
  validation_score?: number;
}

export interface JudgeFeedback {
  rater: string;
  score: number;
  comment: string;
  timestamp: number;
  feedback_type: number;
}

export interface JudgeStatus {
  validation_avg: number;
  reputation_avg: number;
  approved_intents: number;
  validation_count: number;
  checkpoint_count: number;
  vault_claimed: boolean;
  recent_validation_scores: number[];
  latest_feedback?: JudgeFeedback | null;
  waiting_for_rerate?: boolean;
}

export interface TradeRow {
  id?: number;
  timestamp: string;
  symbol: string;
  side: string;
  amount: number;
  price: number;
  confidence?: number;
  realized_pnl: number;
  status?: string;
}

export interface OrderRow {
  id?: number;
  order_id?: string;
  status?: string;
  symbol?: string;
  side?: string;
  lifecycle?: Record<string, unknown>;
  payload?: Record<string, unknown>;
}

export interface AgentIdentity {
  agent_id: number;
  agent_name: string;
  agent_wallet: string;
  operator_wallet: string;
  identity_registry: string;
  risk_router: string;
  validation_registry: string;
  reputation_registry: string;
  capital_claimed: boolean;
  allocation: string;
  reputation?: ReputationData;
  validation_txs: string[];
  judge_status?: JudgeStatus;
}

interface AppState {
  isConnected: boolean;
  market: MarketData | null;
  decision: DecisionData | null;
  pipeline: PipelineEvent | null;
  pipelineStage: PipelineEvent | null;
  metrics: RuntimeMetrics | null;
  reputation: ReputationData | null;
  trades: TradeRow[];
  orders: OrderRow[];
  agent: AgentIdentity | null;
  connect: () => void;
  addTrade: (trade: TradeRow) => void;
  executeManualTrade: (side: 'BUY' | 'SELL', amount: number, price?: number) => Promise<{ success: boolean; message: string; trade?: TradeRow }>;
  disconnectWebSockets: () => void;
  refreshSnapshot: () => Promise<void>;
  connectWebSockets: () => void;
}

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const WS_BASE = (process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000").replace(/\/+$/, "");

let wsConnections: WebSocket[] = [];

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}`);
  }
  return response.json() as Promise<T>;
}

async function fetchOptionalJson<T>(path: string): Promise<T | null> {
  try {
    return await fetchJson<T>(path);
  } catch (error) {
    console.warn(`Optional fetch failed for ${path}`, error);
    return null;
  }
}

export const useStore = create<AppState>((set) => ({
  isConnected: false,
  market: null,
  decision: null,
  pipeline: null,
  pipelineStage: null,
  metrics: null,
  reputation: null,
  trades: [],
  orders: [],
  agent: null,
  connect: () => {
    useStore.getState().connectWebSockets();
  },
  addTrade: (trade: TradeRow) => {
    set((state) => ({ trades: [trade, ...state.trades].slice(0, 50) }));
  },
  executeManualTrade: async (side: 'BUY' | 'SELL', amount: number, price?: number) => {
    try {
      const market = useStore.getState().market;
      const executionPrice = price || market?.price || 0;
      
      const response = await fetch(`${API_BASE}/execute-manual-trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          side: side.toUpperCase(),
          amount,
          price: executionPrice,
          symbol: 'BTC/USD',
        }),
      });

      if (!response.ok) {
        throw new Error('Trade execution failed');
      }

      const result = await response.json();
      console.log('[MANUAL TRADE] Backend response:', result);
      
      if (result.success || result.executed) {
        const newTrade: TradeRow = {
          timestamp: new Date().toISOString(),
          symbol: 'BTC/USD',
          side,
          amount,
          price: executionPrice,
          realized_pnl: result.trade?.realized_pnl || 0,
        };
        useStore.getState().addTrade(newTrade);
        
        // Refresh trades from backend to ensure synchronization
        console.log('[MANUAL TRADE] Refreshing trades from backend...');
        useStore.getState().refreshSnapshot().catch(err => 
          console.warn('[MANUAL TRADE] Failed to refresh snapshot:', err)
        );
        
        return { success: true, message: 'Trade executed successfully', trade: newTrade };
      }

      console.warn('[MANUAL TRADE] Backend rejected trade:', result.message);
      return { success: false, message: result.message || 'Trade failed' };
    } catch (error) {
      console.error('[MANUAL TRADE] Execution error:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Trade execution error' };
    }
  },
  disconnectWebSockets: () => {
    wsConnections.forEach((ws) => ws.close());
    wsConnections = [];
    set({ isConnected: false });
  },
  refreshSnapshot: async () => {
    try {
      const [market, decision, metrics, reputation, trades, orders, pipeline, agent] = await Promise.all([
        fetchOptionalJson<MarketData>("/market"),
        fetchOptionalJson<DecisionData>("/decision"),
        fetchOptionalJson<RuntimeMetrics>("/metrics"),
        fetchOptionalJson<ReputationData>("/reputation"),
        fetchOptionalJson<{ items: TradeRow[] }>("/trades"),
        fetchOptionalJson<{ items: OrderRow[] }>("/orders"),
        fetchOptionalJson<PipelineEvent>("/pipeline"),
        fetchOptionalJson<AgentIdentity>("/agent"),
      ]);
      set((state) => ({
        market: market && Object.keys(market).length ? market : state.market,
        decision: decision && Object.keys(decision).length ? decision : state.decision,
        metrics: metrics && Object.keys(metrics).length ? metrics : state.metrics,
        reputation: reputation && Object.keys(reputation).length ? reputation : state.reputation,
        trades: trades?.items?.length ? trades.items : state.trades,
        orders: orders?.items?.length ? orders.items : state.orders,
        pipeline: pipeline && Object.keys(pipeline).length ? pipeline : state.pipeline,
        pipelineStage: pipeline && Object.keys(pipeline).length ? pipeline : state.pipelineStage,
        agent: agent && Object.keys(agent).length ? agent : state.agent,
      }));
    } catch (error) {
      console.error("Snapshot refresh error", error);
    }
  },
  connectWebSockets: () => {
    wsConnections.forEach((ws) => ws.close());
    wsConnections = [];

    try {
      const marketWs = new WebSocket(`${WS_BASE}/ws/market`);
      marketWs.onopen = () => set({ isConnected: true });
      marketWs.onclose = () => set({ isConnected: false });
      marketWs.onerror = () => set({ isConnected: false });
      marketWs.onmessage = (e) => set({ market: JSON.parse(e.data) as MarketData });
      wsConnections.push(marketWs);

      const decisionsWs = new WebSocket(`${WS_BASE}/ws/decisions`);
      decisionsWs.onmessage = (e) => set({ decision: JSON.parse(e.data) as DecisionData });
      wsConnections.push(decisionsWs);

      const pipelineWs = new WebSocket(`${WS_BASE}/ws/pipeline`);
      pipelineWs.onmessage = (e) => {
        const payload = JSON.parse(e.data) as PipelineEvent;
        set({ pipeline: payload, pipelineStage: payload });
      };
      wsConnections.push(pipelineWs);

      const tradesWs = new WebSocket(`${WS_BASE}/ws/trades`);
      tradesWs.onmessage = (e) => {
        const payload = JSON.parse(e.data) as TradeRow;
        set((state) => ({ trades: [payload, ...state.trades].slice(0, 50) }));
      };
      wsConnections.push(tradesWs);

      const ordersWs = new WebSocket(`${WS_BASE}/ws/orders`);
      ordersWs.onmessage = (e) => {
        const payload = JSON.parse(e.data) as OrderRow;
        set((state) => ({ orders: [payload, ...state.orders].slice(0, 50) }));
      };
      wsConnections.push(ordersWs);
    } catch (error) {
      console.error("Websocket init error", error);
      set({ isConnected: false });
    }
  },
}));

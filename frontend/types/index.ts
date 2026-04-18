export type ExchangeName = "kraken" | "binance" | "kucoin";
export type HealthStatus = "HEALTHY" | "DEGRADED" | "DOWN";

export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ExchangeFeed {
  price: number;
  bid: number;
  ask: number;
  candles: Candle[];
  connected: boolean;
  lastUpdate: number;
}

export interface ExchangeBalanceSnapshot {
  usdt: number;
  btc: number;
}

export interface Trade {
  time: number;
  pair: string;
  type: "buy" | "sell";
  price: number;
  vol: number;
  cost: number;
  fee: number;
  ordertxid: string;
}

export interface EquityPoint {
  x: number;
  y: number;
}

export interface OrderSummary {
  id: string;
  exchange: ExchangeName;
  pair: string;
  side: "buy" | "sell";
  status: string;
  price: number;
  volume: number;
  createdAt: number;
}

export interface AgentStateResponse {
  decision: "BUY" | "SELL" | "HOLD";
  confidence: number;
  tradeType: "STRONG" | "WEAK";
  positionSize: number;
  targetExchange: ExchangeName;
  explanation: string;
  technicalScore: number;
  sentimentScore: number;
  mlPrediction: number;
  riskApproved: boolean;
  reasoningBullets: string[];
  pipelineStage: string;
  intentPrice: number;
  intentCreatedAt: number;
  activityFeed: Array<{
    time: string;
    text: string;
    type: "trade" | "decision" | "validation" | "system";
  }>;
  orderStatus?: string;
  fillPrice?: number;
  fillSize?: number;
  slippage?: number;
  latencyMs?: number;
  succeeded?: boolean;
  lastOrderId?: string;
}

export interface ContractStateResponse {
  agentName: string;
  agentId: string;
  isRegistered: boolean;
  capitalClaimed: boolean;
  allocatedCapital: number;
  reputationScore: number;
  validationAverage: number;
  validationsPosted: number;
  checkpointCount: number;
  approvedIntents: number;
  totalIntents: number;
  rerateIsPending: boolean;
  latestJudgeFeedback: string;
  latestJudgeScore: number;
  recentValidationScores: number[];
  latestProofTxHash: string;
}

export interface AnalyticsMetrics {
  winRate: number;
  profitFactor: number;
  maxDrawdown: number;
  sharpeRatio: number;
  consistency: number;
  equityCurve: EquityPoint[];
}

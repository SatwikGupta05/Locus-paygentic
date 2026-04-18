import { NextResponse } from "next/server";
import { serverHttp } from "@/lib/rest/http";
import type { AgentStateResponse, ExchangeName } from "@/types";

interface BackendDecisionResponse {
  action?: string;
  confidence?: number;
  execution_result?: Record<string, unknown>;
  explainability?: {
    ml_prediction?: { prob_up?: number };
    sentiment?: { sentiment_score?: number };
    technical?: { technical_score?: number };
    risk?: {
      pre_trade_approved?: boolean;
      trade_type?: string;
      position_size?: number;
    };
    position_size?: number;
  };
  audit?: {
    decision?: {
      action?: string;
      confidence?: number;
      trade_type?: string;
      reasoning?: string[];
      risk_override?: string;
    };
    model_prediction?: { prob_up?: number };
    sentiment_score?: { sentiment_score?: number };
    technical_score?: { technical_score?: number };
    risk_verdict?: {
      pre_trade_approved?: boolean;
      trade_type?: string;
      position_size?: number;
    };
  };
}

interface BackendStrategyResponse {
  current_stage?: string;
  signal?: string;
  confidence?: number;
  decision_trace?: {
    decision?: {
      reasoning?: string[];
      trade_type?: string;
    };
  };
}

interface BackendMarketResponse {
  price?: number;
}

interface BackendListResponse<T> {
  items?: T[];
}

interface BackendOrderRow {
  id?: string | number;
  status?: string;
  timestamp?: string;
  payload?: {
    order_id?: string;
    fill_price?: number;
    filled_size?: number;
    latency_ms?: number;
    slippage?: number;
    success?: boolean;
    execution_source?: string;
    status?: string;
  };
}

interface BackendTradeRow {
  timestamp?: string;
  side?: string;
  price?: number;
  symbol?: string;
  realized_pnl?: number;
}

interface BackendIntentRow {
  timestamp?: string;
  status?: string;
  intent_hash?: string;
  payload?: {
    action?: string;
    confidence?: number;
  };
}

function coerceNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function coerceText(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function normalizeDecision(value: unknown): AgentStateResponse["decision"] {
  const upper = coerceText(value, "HOLD").toUpperCase();
  return upper === "BUY" || upper === "SELL" ? upper : "HOLD";
}

function normalizeTradeType(value: unknown): AgentStateResponse["tradeType"] {
  return coerceText(value).toUpperCase() === "STRONG" ? "STRONG" : "WEAK";
}

function inferExchange(source: unknown): ExchangeName {
  const text = coerceText(source).toLowerCase();
  if (text.includes("binance")) {
    return "binance";
  }
  if (text.includes("kucoin")) {
    return "kucoin";
  }
  return "kraken";
}

function formatFeedTime(value: unknown): string {
  const raw = coerceText(value);
  if (!raw) {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  const parsed = new Date(raw);
  if (Number.isNaN(parsed.getTime())) {
    return raw;
  }

  return parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function safeGet<T>(backendUrl: string, endpoint: string): Promise<T | null> {
  try {
    const response = await serverHttp.get<T>(`${backendUrl}${endpoint}`, {
      timeout: 5000
    });
    return response.data;
  } catch {
    return null;
  }
}

export async function GET() {
  const backendUrl = process.env.AGENT_BACKEND_URL;

  if (!backendUrl) {
    return NextResponse.json({ error: "Missing AGENT_BACKEND_URL" }, { status: 500 });
  }

  try {
    const normalizedBackendUrl = backendUrl.replace(/\/$/, "");
    const [decision, strategy, market, orders, trades, intents] = await Promise.all([
      safeGet<BackendDecisionResponse>(normalizedBackendUrl, "/decision"),
      safeGet<BackendStrategyResponse>(normalizedBackendUrl, "/strategy"),
      safeGet<BackendMarketResponse>(normalizedBackendUrl, "/market"),
      safeGet<BackendListResponse<BackendOrderRow>>(normalizedBackendUrl, "/orders"),
      safeGet<BackendListResponse<BackendTradeRow>>(normalizedBackendUrl, "/trades"),
      safeGet<BackendListResponse<BackendIntentRow>>(normalizedBackendUrl, "/intents")
    ]);

    if (!decision && !strategy) {
      throw new Error("Agent backend unavailable");
    }

    const latestOrder = orders?.items?.[0];
    const latestTrade = trades?.items?.[0];
    const latestIntent = intents?.items?.[0];
    const reasoningBullets =
      decision?.audit?.decision?.reasoning ??
      strategy?.decision_trace?.decision?.reasoning ??
      [];

    const currentDecision = normalizeDecision(
      decision?.action ?? decision?.audit?.decision?.action ?? strategy?.signal
    );
    const confidence = coerceNumber(
      decision?.confidence ?? decision?.audit?.decision?.confidence ?? strategy?.confidence
    );
    const tradeType = normalizeTradeType(
      decision?.audit?.decision?.trade_type ??
        decision?.explainability?.risk?.trade_type ??
        decision?.audit?.risk_verdict?.trade_type ??
        strategy?.decision_trace?.decision?.trade_type
    );
    const targetExchange = inferExchange(latestOrder?.payload?.execution_source);
    const intentCreatedAt = Date.parse(
      coerceText(latestIntent?.timestamp) || coerceText(latestOrder?.timestamp) || coerceText(latestTrade?.timestamp)
    );

    const activityFeed: AgentStateResponse["activityFeed"] = [
      latestOrder
        ? {
            time: formatFeedTime(latestOrder.timestamp),
            text: `${coerceText(latestOrder.payload?.order_id, "order")} ${coerceText(latestOrder.status, "updated")} on ${targetExchange}`,
            type: "trade"
          }
        : null,
      latestIntent
        ? {
            time: formatFeedTime(latestIntent.timestamp),
            text: `${coerceText(latestIntent.payload?.action, currentDecision)} intent ${coerceText(latestIntent.status, "submitted")}`,
            type: "decision"
          }
        : null,
      latestTrade
        ? {
            time: formatFeedTime(latestTrade.timestamp),
            text: `${coerceText(latestTrade.side, "trade").toUpperCase()} ${coerceText(latestTrade.symbol, "market")} at ${coerceNumber(latestTrade.price).toFixed(2)}`,
            type: "validation"
          }
        : null,
      {
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        text: `${coerceText(strategy?.current_stage, "IDLE")} pipeline state synced from backend`,
        type: "system"
      }
    ].filter(Boolean) as AgentStateResponse["activityFeed"];

    const payload: AgentStateResponse = {
      decision: currentDecision,
      confidence,
      tradeType,
      positionSize: coerceNumber(
        decision?.explainability?.position_size ?? decision?.audit?.risk_verdict?.position_size
      ),
      targetExchange,
      explanation:
        reasoningBullets[0] ??
        coerceText(decision?.audit?.decision?.risk_override) ??
        `${currentDecision} posture from backend strategy engine.`,
      technicalScore: coerceNumber(
        decision?.explainability?.technical?.technical_score ??
          decision?.audit?.technical_score?.technical_score
      ),
      sentimentScore: coerceNumber(
        decision?.explainability?.sentiment?.sentiment_score ??
          decision?.audit?.sentiment_score?.sentiment_score
      ),
      mlPrediction: coerceNumber(
        decision?.explainability?.ml_prediction?.prob_up ??
          decision?.audit?.model_prediction?.prob_up
      ),
      riskApproved: Boolean(
        decision?.explainability?.risk?.pre_trade_approved ??
          decision?.audit?.risk_verdict?.pre_trade_approved
      ),
      reasoningBullets:
        reasoningBullets.length > 0
          ? reasoningBullets
          : ["Waiting for detailed reasoning from the backend pipeline."],
      pipelineStage: coerceText(strategy?.current_stage, "IDLE"),
      intentPrice: coerceNumber(
        market?.price ?? decision?.execution_result?.fill_price ?? latestTrade?.price
      ),
      intentCreatedAt: Number.isFinite(intentCreatedAt) ? intentCreatedAt : Date.now(),
      activityFeed,
      orderStatus: coerceText(latestOrder?.status ?? latestOrder?.payload?.status, "Idle"),
      fillPrice: coerceNumber(
        latestOrder?.payload?.fill_price ?? decision?.execution_result?.fill_price
      ),
      fillSize: coerceNumber(
        latestOrder?.payload?.filled_size ?? decision?.execution_result?.filled_size
      ),
      slippage: coerceNumber(
        latestOrder?.payload?.slippage ?? decision?.execution_result?.slippage
      ),
      latencyMs: coerceNumber(latestOrder?.payload?.latency_ms),
      succeeded: Boolean(
        latestOrder?.payload?.success ??
          (coerceText(latestOrder?.status).toLowerCase() === "filled")
      ),
      lastOrderId: coerceText(latestOrder?.payload?.order_id, coerceText(latestOrder?.id))
    };

    return NextResponse.json(payload, {
      headers: {
        "Cache-Control": "no-store"
      }
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Agent backend unavailable"
      },
      {
        status: 504,
        headers: {
          "Cache-Control": "no-store"
        }
      }
    );
  }
}

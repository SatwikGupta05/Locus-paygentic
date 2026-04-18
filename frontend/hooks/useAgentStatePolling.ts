"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import type { AgentStateResponse } from "@/types";
import { useDecisionStore } from "@/store/decisionStore";
import { useExecutionStore } from "@/store/executionStore";
import { useSystemStore } from "@/store/systemStore";

async function fetchAgentState(): Promise<AgentStateResponse> {
  const response = await fetch("/api/decision", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Agent decision unavailable");
  }
  const data = await response.json();
  
  // Transform backend DecisionData into UI AgentStateResponse
  return {
    decision: data.action || "HOLD",
    confidence: data.confidence || 0,
    tradeType: (data.explainability?.trade_type || "WEAK") as "STRONG" | "WEAK",
    positionSize: data.explainability?.position_size || 0,
    targetExchange: "kraken", // Backend currently defaults/hardcoded
    explanation: data.explainability?.rationale || "Analyzing market conditions...",
    technicalScore: data.explainability?.signals?.price_action || 0,
    sentimentScore: data.explainability?.signals?.sentiment || 0,
    mlPrediction: data.explainability?.ml_forecast?.prediction || 0,
    riskApproved: data.explainability?.risk?.pre_trade_approved || false,
    reasoningBullets: data.explainability?.key_factors || [],
    pipelineStage: data.pipeline_stage || "IDLE",
    intentPrice: data.explainability?.intent_specs?.price || 0,
    intentCreatedAt: Date.now(),
    activityFeed: [], // Handled by ActivityFeedPanel separately usually
    orderStatus: data.execution_result?.status || "Idle",
    fillPrice: data.execution_result?.fill_price,
    fillSize: data.execution_result?.fill_size,
    slippage: data.execution_result?.slippage,
    latencyMs: data.execution_result?.latency_ms,
    succeeded: data.execution_result?.succeeded,
    lastOrderId: data.intent_hash
  } as AgentStateResponse;
}

export function useAgentStatePolling() {
  const query = useQuery({
    queryKey: ["agentState"],
    queryFn: fetchAgentState,
    refetchInterval: 5_000
  });

  useEffect(() => {
    if (!query.data) {
      return;
    }

    const data = query.data;
    useDecisionStore.getState().setDecisionState(data);
    useExecutionStore.getState().setExecutionState({
      exchange: data.targetExchange,
      intentPrice: data.intentPrice,
      orderStatus: data.orderStatus ?? "Idle",
      fillPrice: data.fillPrice ?? 0,
      fillSize: data.fillSize ?? 0,
      slippage: data.slippage ?? 0,
      latencyMs: data.latencyMs ?? 0,
      succeeded: data.succeeded ?? false,
      lastOrderId: data.lastOrderId ?? ""
    });
    useSystemStore.setState({
      proofHealth: "HEALTHY",
      judgeHealth: "HEALTHY",
      mlHealth: "HEALTHY"
    });
  }, [query.data]);

  useEffect(() => {
    if (query.error) {
      useDecisionStore.getState().setStale(true);
      useSystemStore.setState({
        proofHealth: "DEGRADED",
        judgeHealth: "DEGRADED",
        mlHealth: "DEGRADED"
      });
    }
  }, [query.error]);

  return query;
}

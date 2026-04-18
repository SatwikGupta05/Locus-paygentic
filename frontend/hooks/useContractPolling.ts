"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import type { ContractStateResponse } from "@/types";
import { usePortfolioStore } from "@/store/portfolioStore";
import { useReputationStore } from "@/store/reputationStore";
import { useSystemStore } from "@/store/systemStore";
import { useValidationStore } from "@/store/validationStore";

async function fetchContractState(): Promise<ContractStateResponse> {
  const response = await fetch("/api/agent");
  if (!response.ok) {
    throw new Error("Contract read failed");
  }

  const data = await response.json();
  return {
    agentName: data.agent_name || "AURORA-AI",
    agentId: String(data.agent_id || "0"),
    isRegistered: true, // If we can fetch the agent, it is registered
    capitalClaimed: data.vault_claimed || false,
    allocatedCapital: 10000, // Hardcoded in backend startup
    reputationScore: data.reputation_avg || 0,
    validationAverage: data.validation_avg || 0,
    validationsPosted: data.validation_count || 0,
    checkpointCount: data.checkpoint_count || 0,
    approvedIntents: data.approved_intents || 0,
    totalIntents: data.approved_intents || 0, // Backend doesn't split yet
    rerateIsPending: data.waiting_for_rerate || false,
    latestJudgeFeedback: data.latest_feedback?.comment || "",
    latestJudgeScore: data.latest_feedback?.score || 0,
    recentValidationScores: data.recent_validation_scores || [],
    latestProofTxHash: data.latest_feedback?.rater || ""
  } as ContractStateResponse;
}

export function useContractPolling() {
  const query = useQuery({
    queryKey: ["contract"],
    queryFn: fetchContractState,
    staleTime: 25_000,
    refetchInterval: 30_000
  });

  useEffect(() => {
    if (!query.data) {
      return;
    }

    const data = query.data;
    useValidationStore.getState().setValidationState({
      validationAverage: data.validationAverage,
      validationsPosted: data.validationsPosted,
      checkpointCount: data.checkpointCount,
      approvedIntents: data.approvedIntents,
      totalIntents: data.totalIntents,
      recentValidationScores: data.recentValidationScores,
      latestProofTxHash: data.latestProofTxHash
    });
    useReputationStore.getState().setReputationState({
      reputationScore: data.reputationScore,
      latestJudgeFeedback: data.latestJudgeFeedback,
      latestJudgeScore: data.latestJudgeScore,
      rerateIsPending: data.rerateIsPending
    });
    usePortfolioStore.getState().setAllocatedCapital(data.allocatedCapital);
    useSystemStore.getState().setChainHealth("HEALTHY");
  }, [query.data]);

  useEffect(() => {
    if (query.error) {
      useSystemStore.getState().setChainHealth("DEGRADED");
    }
  }, [query.error]);

  return query;
}

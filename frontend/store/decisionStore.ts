import { create } from "zustand";
import type { AgentStateResponse, ExchangeName } from "@/types";

interface ActivityEntry {
  time: string;
  text: string;
  type: "trade" | "decision" | "validation" | "system";
}

interface DecisionStore {
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
  lastUpdated: number;
  stale: boolean;
  activityFeed: ActivityEntry[];
  setDecisionState: (payload: AgentStateResponse) => void;
  addActivity: (entry: ActivityEntry) => void;
  setStale: (value: boolean) => void;
}

export const useDecisionStore = create<DecisionStore>((set) => ({
  decision: "HOLD",
  confidence: 0,
  tradeType: "WEAK",
  positionSize: 0,
  targetExchange: "binance",
  explanation: "",
  technicalScore: 0,
  sentimentScore: 0,
  mlPrediction: 0,
  riskApproved: false,
  reasoningBullets: [],
  pipelineStage: "IDLE",
  intentPrice: 0,
  intentCreatedAt: 0,
  lastUpdated: 0,
  stale: false,
  activityFeed: [],
  setDecisionState: (payload) =>
    set({
      ...payload,
      lastUpdated: Date.now(),
      stale: false
    }),
  addActivity: (entry) =>
    set((state) => ({
      activityFeed: [entry, ...state.activityFeed].slice(0, 40)
    })),
  setStale: (value) => set({ stale: value })
}));

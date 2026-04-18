import { create } from "zustand";
import type { AnalyticsMetrics } from "@/types";

interface AnalyticsStore extends AnalyticsMetrics {
  setAnalytics: (payload: AnalyticsMetrics) => void;
}

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  winRate: 0,
  profitFactor: 0,
  maxDrawdown: 0,
  sharpeRatio: 0,
  consistency: 0,
  equityCurve: [],
  setAnalytics: (payload) => set(payload)
}));

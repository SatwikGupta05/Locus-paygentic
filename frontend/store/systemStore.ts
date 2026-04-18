import { create } from "zustand";
import type { ExchangeName, HealthStatus } from "@/types";

interface SystemStore {
  chainHealth: HealthStatus;
  proofHealth: HealthStatus;
  judgeHealth: HealthStatus;
  mlHealth: HealthStatus;
  exchangeHealth: Record<ExchangeName, HealthStatus>;
  exchangeRateLimitedUntil: Partial<Record<ExchangeName, number>>;
  exchangeAuthError: Partial<Record<ExchangeName, string>>;
  setExchangeHealth: (exchange: ExchangeName, health: HealthStatus) => void;
  setChainHealth: (health: HealthStatus) => void;
  setRateLimited: (exchange: ExchangeName, until: number) => void;
  setAuthError: (exchange: ExchangeName, message: string) => void;
}

export const useSystemStore = create<SystemStore>((set) => ({
  chainHealth: "HEALTHY",
  proofHealth: "HEALTHY",
  judgeHealth: "HEALTHY",
  mlHealth: "HEALTHY",
  exchangeHealth: {
    kraken: "DEGRADED",
    binance: "DEGRADED",
    kucoin: "DEGRADED"
  },
  exchangeRateLimitedUntil: {},
  exchangeAuthError: {},
  setExchangeHealth: (exchange, health) =>
    set((state) => ({
      exchangeHealth: {
        ...state.exchangeHealth,
        [exchange]: health
      }
    })),
  setChainHealth: (health) => set({ chainHealth: health }),
  setRateLimited: (exchange, until) =>
    set((state) => ({
      exchangeRateLimitedUntil: {
        ...state.exchangeRateLimitedUntil,
        [exchange]: until
      }
    })),
  setAuthError: (exchange, message) =>
    set((state) => ({
      exchangeAuthError: {
        ...state.exchangeAuthError,
        [exchange]: message
      }
    }))
}));

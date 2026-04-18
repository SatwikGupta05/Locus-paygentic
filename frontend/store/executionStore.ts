import { create } from "zustand";
import type { ExchangeName } from "@/types";

interface ExecutionStore {
  exchange: ExchangeName;
  orderStatus: string;
  fillPrice: number;
  fillSize: number;
  intentPrice: number;
  slippage: number;
  latencyMs: number;
  succeeded: boolean;
  lastOrderId: string;
  setExecutionState: (payload: Partial<Omit<ExecutionStore, "setExecutionState">>) => void;
}

export const useExecutionStore = create<ExecutionStore>((set) => ({
  exchange: "binance",
  orderStatus: "Idle",
  fillPrice: 0,
  fillSize: 0,
  intentPrice: 0,
  slippage: 0,
  latencyMs: 0,
  succeeded: false,
  lastOrderId: "",
  setExecutionState: (payload) => set(payload)
}));

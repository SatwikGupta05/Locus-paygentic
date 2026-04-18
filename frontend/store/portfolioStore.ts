import { create } from "zustand";

interface PortfolioStore {
  allocatedCapital: number;
  balances: { kraken: number; binance: number; kucoin: number };
  totalBalance: number;
  totalPnL: number;
  openPositions: number;
  totalTrades: number;
  setAllocatedCapital: (value: number) => void;
  setBalance: (exchange: "kraken" | "binance" | "kucoin", value: number) => void;
  setOpenPositions: (value: number) => void;
  setTotalTrades: (value: number) => void;
}

export const usePortfolioStore = create<PortfolioStore>((set, get) => ({
  allocatedCapital: 0,
  balances: { kraken: 0, binance: 0, kucoin: 0 },
  totalBalance: 0,
  totalPnL: 0,
  openPositions: 0,
  totalTrades: 0,
  setAllocatedCapital: (value) => {
    set({ allocatedCapital: value, totalPnL: get().totalBalance - value });
  },
  setBalance: (exchange, value) => {
    const nextBalances = { ...get().balances, [exchange]: value };
    const totalBalance = Object.values(nextBalances).reduce((sum, current) => sum + current, 0);
    set({
      balances: nextBalances,
      totalBalance,
      totalPnL: totalBalance - get().allocatedCapital
    });
  },
  setOpenPositions: (value) => set({ openPositions: value }),
  setTotalTrades: (value) => set({ totalTrades: value })
}));

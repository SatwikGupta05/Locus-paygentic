"use client";

import { useStore } from "../../lib/store";

export function HeaderBar() {
  const isConnected = useStore((state) => state.isConnected);
  const metrics = useStore((state) => state.metrics);
  const agent = useStore((state) => state.agent);

  const totalPnl = metrics?.total_pnl ?? metrics?.portfolio?.daily_realized_pnl ?? 0;
  const wallet = agent?.agent_wallet
    ? `${agent.agent_wallet.slice(0, 6)}...${agent.agent_wallet.slice(-4)}`
    : "Wallet pending";

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-[#050510]/80 border-b border-indigo-500/20 shadow-[0_0_15px_rgba(79,70,229,0.1)]">
      <div className="h-16 px-6 mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 shadow-[0_0_10px_rgba(99,102,241,0.5)] flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-white animate-pulse" />
          </div>
          <h1 className="text-xl font-bold tracking-[0.2em] bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            AURORA<span className="text-indigo-400 font-light">OMEGA</span>
          </h1>
        </div>

        <div className="hidden md:flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/5 border border-white/10">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)] animate-pulse" : "bg-rose-500"}`} />
          <span className="text-xs uppercase tracking-widest text-emerald-100 font-medium">
            {isConnected ? "LIVE & SYNCED" : "DEGRADED / OFFLINE"}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded border text-xs font-semibold tracking-wide ${
            totalPnl >= 0
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
              : "bg-rose-500/10 border-rose-500/20 text-rose-400"
          }`}>
            PNL: {totalPnl >= 0 ? "+" : ""}${totalPnl.toFixed(2)}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold tracking-wide">
            SEPOLIA
          </div>
          <div className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm font-mono text-white/80 hover:bg-white/10 transition-colors cursor-pointer">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-orange-400 to-pink-500" />
            {wallet}
          </div>
        </div>
      </div>
    </header>
  );
}

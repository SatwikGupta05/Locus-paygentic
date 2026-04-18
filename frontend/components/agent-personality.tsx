"use client";

import { useEffect, useState } from "react";
import { getJson } from "../lib/api";
import { useStore } from "../lib/store";

export function AgentPersonality() {
  const [config, setConfig] = useState<Record<string, any>>({});
  const reputation = useStore((state) => state.reputation);
  const trades = useStore((state) => state.trades);

  useEffect(() => {
    getJson<Record<string, any>>("/config").then(setConfig).catch(console.error);
  }, []);

  if (!config.agent_name) return null;

  const realizedPnl = trades.reduce((acc, t) => acc + (t.realized_pnl || 0), 0);

  return (
    <div className="flex items-center gap-4 text-xs font-mono">
      <div className="flex items-center gap-2">
        <span className="text-white/40 uppercase tracking-widest">PnL:</span>
        <span className={realizedPnl >= 0 ? "text-green-400" : "text-red-400"}>
          ${realizedPnl > 0 ? "+" : ""}{realizedPnl.toFixed(2)} {realizedPnl >= 0 ? "↑" : "↓"}
        </span>
      </div>

      <div className="h-4 w-px bg-white/20"></div>

      <div className="flex items-center gap-2">
        <span className="text-white/40 uppercase tracking-widest">Win Rate:</span>
        <span className="text-white/80">
          {reputation?.win_rate ? (reputation.win_rate * 100).toFixed(1) : "0.0"}%
        </span>
      </div>

      <div className="h-4 w-px bg-white/20"></div>

      <div className="flex items-center gap-2">
        <span className="text-white/40 uppercase tracking-widest">Sharpe:</span>
        <span className="text-white/80">
          {reputation?.sharpe_ratio?.toFixed(2) ?? "0.00"}
        </span>
      </div>

      <div className="h-4 w-px bg-white/20"></div>

      <div className="flex items-center gap-2">
        <span className="text-white/40 uppercase tracking-widest">Status:</span>
        <span className="text-foam">
          ACTIVE<span className="animate-pulse inline-block ml-1">●</span>
        </span>
      </div>

       <div className="h-4 w-px bg-white/20"></div>

      <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest px-2 py-1 bg-black/40 rounded border border-white/10">
        <span className="text-white/40">Mode:</span>
        <span className={config.env === "LIVE" ? "text-purple-400" : "text-foam"}>
          {config.env === "LIVE" ? "DEFENSIVE" : "AGGRESSIVE"}
        </span>
      </div>
    </div>
  );
}

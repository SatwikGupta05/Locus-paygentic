"use client";

import { useStore } from "../../lib/store";

export function WalletIdentity() {
  const metrics = useStore((state) => state.metrics);
  const reputation = useStore((state) => state.reputation);
  const agent = useStore((state) => state.agent);
  const totalPnl = metrics?.total_pnl ?? 0;
  const sharpe = metrics?.sharpe ?? reputation?.sharpe_ratio ?? 0;
  const winRate = metrics?.win_rate ?? reputation?.win_rate ?? 0;

  return (
    <div className="p-5 rounded-xl bg-black/40 border border-white/5 backdrop-blur-sm relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
      <div className="absolute -top-20 -right-20 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all" />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xs text-white/50 uppercase tracking-widest font-semibold">Wallet Identity</h2>
        <div className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider border ${
          agent?.capital_claimed
            ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/20"
            : "bg-amber-500/20 text-amber-300 border-amber-500/20"
        }`}>
          {agent?.capital_claimed ? "CAPITAL CLAIMED" : "CLAIM PENDING"}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <div className="text-4xl font-light tracking-tight text-white mb-1">
            {agent?.allocation || "--"} <span className="text-xl text-white/50 font-normal">ETH</span>
          </div>
          <div className="text-sm text-indigo-300/80 font-mono">
            PnL {totalPnl >= 0 ? "+" : ""}${totalPnl.toFixed(2)} | Sharpe {sharpe.toFixed(2)}
          </div>
        </div>

        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between hover:bg-white/10 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold shadow-inner">
                AI
              </div>
              <div>
                <div className="text-xs text-white/50 mb-0.5">Agent Wallet (Hot)</div>
                <div className="text-sm font-mono text-white/90">{agent?.agent_wallet || "Awaiting registration"}</div>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-1 p-3 rounded-lg bg-white/5 border border-white/5">
              <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">Token ID (ERC-721)</div>
              <div className="font-mono text-indigo-300">#{agent?.agent_id || "..."}</div>
            </div>
            <div className="flex-1 p-3 rounded-lg bg-white/5 border border-white/5">
              <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">Win Rate</div>
              <div className="font-mono text-white/80">{(winRate * 100).toFixed(1)}%</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-white/5 border border-white/5">
              <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">Reputation</div>
              <div className="font-mono text-emerald-300">{reputation?.validation_score?.toFixed(1) ?? "0.0"}</div>
            </div>
            <div className="p-3 rounded-lg bg-white/5 border border-white/5">
              <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1">Total Trades</div>
              <div className="font-mono text-white/80">{reputation?.total_trades ?? 0}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

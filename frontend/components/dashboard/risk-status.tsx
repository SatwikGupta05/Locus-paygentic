"use client";

import { useStore } from "../../lib/store";

export function RiskStatus() {
  const metrics = useStore((state) => state.metrics);
  const decision = useStore((state) => state.decision);
  const drawdown = metrics?.max_drawdown ?? metrics?.portfolio?.drawdown_pct ?? 0;
  const sharpe = metrics?.sharpe ?? 0;
  const riskApproved = decision?.explainability?.risk?.pre_trade_approved ?? false;
  const positionSize = decision?.explainability?.position_size ?? 0;
  const statusTone =
    drawdown >= 0.15 ? "text-rose-400 border-rose-500/20 bg-rose-500/10" :
    drawdown >= 0.08 ? "text-amber-300 border-amber-500/20 bg-amber-500/10" :
    "text-emerald-400 border-emerald-500/20 bg-emerald-500/10";
  const statusLabel = drawdown >= 0.15 ? "HIGH" : drawdown >= 0.08 ? "ELEVATED" : "STABLE";

  return (
    <div className="p-5 rounded-xl bg-[#09090b] border border-[#27272a] h-full flex flex-col relative overflow-hidden group">
      <div className="absolute top-0 -right-10 w-48 h-48 bg-purple-500/5 rounded-full blur-3xl group-hover:bg-purple-500/10 transition-all pointer-events-none" />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xs text-zinc-400 uppercase tracking-widest font-semibold flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-500"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          On-Chain Risk & Trust
        </h2>
      </div>

      <div className="space-y-4">
        <div className={`p-4 rounded-lg border flex flex-col ${statusTone}`}>
          <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1">RiskRouter Control</div>
          <div className="flex items-center justify-between">
            <div className="text-lg font-mono">{riskApproved ? "APPROVED" : "BLOCKED"}</div>
            <div className="text-xs text-zinc-500">State: {statusLabel}</div>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800/50 text-sm font-mono">
          <div className="text-[10px] font-sans text-zinc-500 uppercase tracking-widest mb-3 border-b border-zinc-800 pb-2">Last Intent Specs</div>
          <div className="space-y-2">
            <div className="flex justify-between"><span className="text-zinc-500">Pair:</span><span className="text-zinc-300">{decision?.symbol || "BTC/USD"}</span></div>
            <div className="flex justify-between"><span className="text-zinc-500">Approved:</span><span className="text-zinc-300">{riskApproved ? "YES" : "NO"}</span></div>
            <div className="flex justify-between"><span className="text-zinc-500">Position Size:</span><span className="text-indigo-400">{positionSize ? positionSize.toFixed(6) : "--"}</span></div>
          </div>
        </div>

        <div className="mt-auto p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-transparent border border-purple-500/20">
          <div className="text-[10px] text-purple-300/70 uppercase tracking-widest mb-1">ValidationRegistry rep</div>
          <div className="flex items-end gap-2">
            <div className="text-3xl font-light text-purple-100">{sharpe.toFixed(2)}<span className="text-lg text-purple-300/50"> Sharpe</span></div>
            <div className={`text-xs mb-1 ml-auto shrink-0 ${drawdown >= 0.15 ? "text-rose-400" : drawdown >= 0.08 ? "text-amber-300" : "text-emerald-400"}`}>
              DD {(drawdown * 100).toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

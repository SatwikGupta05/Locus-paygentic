"use client";

import { useStore } from "../../lib/store";

export function MarketIntelligence() {
  const market = useStore((state) => state.market);
  const decision = useStore((state) => state.decision);
  const price = market?.price;
  const confidence = decision?.confidence ? `${(decision.confidence * 100).toFixed(1)}%` : "--";
  const mlProbability = decision?.explainability?.ml_prediction?.prob_up;

  return (
    <div className="p-5 rounded-xl bg-[#09090b] border border-[#27272a] h-full flex flex-col relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl group-hover:bg-emerald-500/10 transition-all pointer-events-none" />

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs text-zinc-400 uppercase tracking-widest font-semibold flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-500"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
          Market Intelligence
        </h2>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-[10px] uppercase text-emerald-500 font-mono tracking-wider">{market?.source || "Awaiting feed"}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
          <div className="text-xs text-zinc-500 mb-1 font-medium">{market?.symbol || "Loading symbol"}</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-light text-zinc-100 font-mono">
              {typeof price === "number" ? `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "--"}
            </div>
            <div className="text-sm font-mono text-emerald-400 mb-1">{market?.mode || "LIVE"}</div>
          </div>
        </div>
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
          <div className="text-xs text-zinc-500 mb-1 font-medium">Decision</div>
          <div className="flex items-end gap-3">
            <div className="text-3xl font-light text-zinc-300 font-mono">{decision?.action || "WAIT"}</div>
            <div className="text-sm font-mono text-foam mb-1">{confidence}</div>
          </div>
        </div>
      </div>

      <h3 className="text-[10px] text-zinc-500 uppercase tracking-widest mb-3">Live Market State</h3>
      <div className="grid grid-cols-3 gap-3 flex-1">
        <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 flex flex-col justify-between">
          <div className="text-xs text-zinc-500 uppercase">Signal</div>
          <div className="text-lg font-bold text-emerald-400">{decision?.action || "--"}</div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 flex flex-col justify-between">
          <div className="text-xs text-zinc-500 uppercase">Confidence</div>
          <div className="text-lg font-bold text-zinc-100">{confidence}</div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 flex flex-col justify-between">
          <div className="text-xs text-zinc-500 uppercase">ML Prob Up</div>
          <div className="text-lg font-bold text-emerald-400">
            {typeof mlProbability === "number" ? `${(mlProbability * 100).toFixed(1)}%` : "--"}
          </div>
        </div>
      </div>
    </div>
  );
}

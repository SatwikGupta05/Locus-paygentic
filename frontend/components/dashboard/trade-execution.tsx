"use client";

import { useStore } from "../../lib/store";

export function TradeExecution() {
  const trades = useStore((state) => state.trades);
  const displayTrades = trades.slice(0, 5);
  const pipeline = useStore((state) => state.pipeline);
  const steps = pipeline?.stage ? [pipeline.stage, ...Object.keys(pipeline.data || {})] : [];

  return (
    <div className="p-5 rounded-xl bg-[#09090b] border border-[#27272a] h-full flex flex-col relative overflow-hidden group">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xs text-white uppercase tracking-widest font-semibold flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          Trade Execution Panel
        </h2>
      </div>

      <div className="flex-1 grid md:grid-cols-2 gap-8">
        <div className="overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900/40">
          <div className="px-4 py-3 text-[10px] uppercase tracking-widest text-zinc-500 border-b border-zinc-800">Last 5 Trades</div>
          <table className="w-full text-sm">
            <thead className="text-zinc-500 text-[10px] uppercase tracking-widest">
              <tr>
                <th className="px-4 py-2 text-left">Side</th>
                <th className="px-4 py-2 text-right">Size</th>
                <th className="px-4 py-2 text-right">Price</th>
                <th className="px-4 py-2 text-right">PnL</th>
              </tr>
            </thead>
            <tbody>
              {displayTrades.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-zinc-500">No trades recorded yet.</td>
                </tr>
              ) : (
                displayTrades.map((trade) => (
                  <tr key={`${trade.id ?? trade.timestamp}-${trade.side}`} className="border-t border-zinc-800/70">
                    <td className={`px-4 py-2 ${trade.side === "BUY" ? "text-emerald-400" : "text-rose-400"}`}>{trade.side}</td>
                    <td className="px-4 py-2 text-right text-zinc-200">{trade.amount.toFixed(4)}</td>
                    <td className="px-4 py-2 text-right text-zinc-200">${trade.price.toFixed(2)}</td>
                    <td className={`px-4 py-2 text-right ${trade.realized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {trade.realized_pnl >= 0 ? "+" : ""}{trade.realized_pnl.toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-3 py-2 bg-black/20 rounded-lg p-4 border border-zinc-900">
          <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-2">Live Pipeline</div>
          {steps.length === 0 ? (
            <div className="text-sm text-zinc-500">Waiting for live pipeline stages...</div>
          ) : (
            steps.map((step, index) => (
              <div key={`${step}-${index}`} className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${index === 0 ? "bg-indigo-500 animate-pulse" : "bg-emerald-500"}`} />
                <span className={`text-sm tracking-wide ${index === 0 ? "text-indigo-400 font-medium" : "text-zinc-300"}`}>{step}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

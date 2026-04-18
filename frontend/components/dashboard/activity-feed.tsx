"use client";

import { useStore } from "@/lib/store";

export function ActivityFeed() {
  const events = [
    { time: "14:02:45", type: "TradeIntent", status: "success", text: "Intent signed via ERC-712 EIP" },
    { time: "14:02:46", type: "RiskRouter", status: "success", text: "Simulation passed for $1,500 trade" },
    { time: "14:02:49", type: "TxHash", status: "pending", text: "Tx 0x5a2... pending on Sepolia" },
    { time: "14:03:10", type: "KrakenCLI", status: "success", text: "Executed 0.02 BTC MARKET BUY" },
    { time: "14:03:15", type: "Validation", status: "success", text: "Checkpoint posted: Top 10% score" }
  ];

  return (
    <div className="p-4 rounded-xl bg-black border border-[#27272a] h-full flex flex-col font-mono">
      <div className="flex items-center justify-between mb-4 border-b border-zinc-800 pb-2">
         <h2 className="text-[10px] text-zinc-500 uppercase tracking-widest flex items-center gap-2">
            System Event Log
         </h2>
         <div className="flex items-center gap-2 text-[10px] text-zinc-600">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50"></span> Auto-scroll active
         </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1">
         {events.map((ev, i) => (
            <div key={i} className="flex gap-3 text-xs py-1 hover:bg-zinc-900/50 transition-colors px-2 rounded">
               <span className="text-zinc-600 shrink-0">[{ev.time}]</span>
               <span className="text-zinc-400 shrink-0 w-24">({ev.type})</span>
               <span className={`
                  ${ev.status === 'success' ? 'text-emerald-400' : ''}
                  ${ev.status === 'pending' ? 'text-yellow-400' : ''}
                  ${ev.status === 'fail' ? 'text-rose-400' : ''}
               `}>
                  {ev.text}
               </span>
            </div>
         ))}
      </div>
    </div>
  );
}

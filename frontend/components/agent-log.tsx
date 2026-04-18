"use client";

import { useStore } from "../lib/store";
import { useEffect, useRef, useState } from "react";
import { Terminal } from "lucide-react";

export function AgentLog() {
  const pipeline = useStore((state) => state.pipeline);
  const [logs, setLogs] = useState<{ time: string; msg: string; emphasis?: boolean }[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pipeline) return;

    const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    let msg = "";
    let emphasis = false;

    switch (pipeline.stage) {
      case "FETCHING_DATA":
        msg = `Detecting market conditions for ${pipeline.data?.symbol}...`;
        break;
      case "COMPUTING_FEATURES":
        msg = `Computing technical momentum & volatility limits...`;
        break;
      case "RUNNING_ML":
        msg = `Running Random Forest inference on current regime...`;
        break;
      case "VALIDATING_RISK":
        const action = pipeline.data?.pre_trade_approved ? "APPROVED" : "REJECTED";
        const regime = pipeline.data?.volatility_regime;
        msg = `Risk check: ${action}. Volatility Regime: ${regime}.`;
        emphasis = !pipeline.data?.pre_trade_approved;
        break;
      case "CREATING_INTENT":
        msg = `Agent proposing ${String(pipeline.data?.action)} with ${String(pipeline.data?.size)} size. (Conf: ${((pipeline.data?.confidence as number) * 100).toFixed(1)}%)`;
        break;
      case "INTENT_SIGNED":
        msg = `EIP-712 Intent cryptographically signed & submitted.`;
        emphasis = true;
        break;
      case "EXECUTING_ORDER":
        msg = `Transmitting real execution instruction to Kraken...`;
        break;
      case "ORDER_UPDATE":
        msg = `Order status: ${String(pipeline.data?.status)}`;
        break;
      case "RECORDING_RESULT":
        msg = `Appending trade lifecycle and tx_hash ${String(pipeline.data?.tx_hash || '').slice(0,10)}... to audit ledger.`;
        break;
    }

    if (msg) {
      setLogs((prev) => [...prev, { time: now, msg, emphasis }].slice(-25));
    }
  }, [pipeline]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="panel flex flex-col h-[280px]">
      <h2 className="mb-4 text-sm font-semibold tracking-widest text-foam opacity-80 uppercase flex items-center gap-2 shrink-0">
        <Terminal size={16} /> Live Agent Narration
      </h2>
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-2 pr-2 font-mono text-xs scrollbar-thin scrollbar-thumb-white/10"
      >
        {logs.length === 0 && <span className="text-white/30">Awaiting agent activation...</span>}
        {logs.map((log, i) => (
          <div key={i} className={`flex gap-3 leading-tight ${log.emphasis ? 'text-foam' : 'text-white/60'}`}>
            <span className="text-white/30 shrink-0">[{log.time}]</span>
            <span className="break-words">{log.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

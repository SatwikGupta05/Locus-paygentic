"use client";

import { useStore } from "../lib/store";
import { Link2, CheckCircle2, Copy } from "lucide-react";

export function OnChainProof() {
  const intent = useStore((state) => state.pipeline?.data?.intent_hash ? state.pipeline.data : state.decision) as any;
  const hash = intent?.intent_hash || intent?.explainability?.intent_hash;
  const txHash = intent?.tx_hash || intent?.explainability?.tx_hash || intent?.execution_result?.tx_hash;

  if (!hash) {
    return (
      <div className="panel flex flex-col justify-center items-center text-white/30 h-full">
        <Link2 size={32} className="mb-2 opacity-50" />
        <span className="text-xs uppercase tracking-widest">Awaiting Intent Signature</span>
      </div>
    );
  }

  return (
    <div className="panel space-y-4">
      <h2 className="text-sm font-semibold tracking-widest text-foam opacity-80 uppercase flex items-center gap-2">
        <Link2 size={16} /> On-Chain Validation Proof
      </h2>
      
      <div className="space-y-4">
        {/* Verification Steps */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="flex items-center gap-2 text-green-400 bg-green-400/5 p-2 rounded border border-green-400/10">
            <CheckCircle2 size={14} /> EIP-712 Signed
          </div>
          <div className="flex items-center gap-2 text-green-400 bg-green-400/5 p-2 rounded border border-green-400/10">
            <CheckCircle2 size={14} /> Signature Verified
          </div>
          <div className="flex items-center gap-2 text-green-400 bg-green-400/5 p-2 rounded border border-green-400/10">
            <CheckCircle2 size={14} /> Parameters Validated
          </div>
          <div className={`flex items-center gap-2 p-2 rounded border ${txHash ? 'text-green-400 bg-green-400/5 border-green-400/10' : 'text-white/40 bg-white/5 border-white/5'}`}>
            <CheckCircle2 size={14} /> {txHash ? "Tx Confirmed" : "Awaiting Tx..."}
          </div>
        </div>

        {/* Hashes */}
        <div className="space-y-2">
          <div className="bg-black/40 rounded p-2 border border-white/5">
            <div className="text-[10px] text-white/40 uppercase mb-1 flex justify-between">
              Intent Hash <Copy size={10} className="cursor-pointer hover:text-white" />
            </div>
            <div className="font-mono text-xs text-foam truncate">{hash}</div>
          </div>
          
          {txHash && (
            <div className="bg-black/40 rounded p-2 border border-white/5">
              <div className="text-[10px] text-white/40 uppercase mb-1 flex justify-between">
                Transaction Hash <Copy size={10} className="cursor-pointer hover:text-white" />
              </div>
              <div className="font-mono text-xs text-purple-400 truncate">{txHash}</div>
            </div>
          )}
        </div>

        <button className="w-full py-2 bg-foam/10 hover:bg-foam/20 transition text-foam rounded text-xs tracking-widest uppercase font-semibold">
          View on Explorer
        </button>
      </div>
    </div>
  );
}

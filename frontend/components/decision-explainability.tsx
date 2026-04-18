"use client";

import { useStore } from "../lib/store";
import { Activity, Zap, Shield, FileText } from "lucide-react";

export function DecisionExplainability() {
  const decision = useStore((state) => state.decision);

  if (!decision || !decision.explainability) {
    return (
      <div className="panel flex h-full items-center justify-center text-sm text-white/50">
        Waiting for trade decision...
      </div>
    );
  }

  const ex = decision.explainability;

  return (
    <div className="panel space-y-4">
      <h2 className="text-lg font-semibold text-foam flex items-center gap-2">
        <FileText size={18} /> WHY THIS TRADE?
      </h2>
      
      <div className="space-y-4 text-sm mt-4">
        {/* ML Output */}
        <div className="flex justify-between items-center border-b border-white/10 pb-2">
          <div className="flex items-center gap-2 text-white/70">
            <Zap size={14} className="text-purple-400" /> ML Prediction
          </div>
          <div className="font-mono">
            {ex.ml_prediction?.prob_up && ex.ml_prediction.prob_up > 0.5 ? (
              <span className="text-green-400">
                {(ex.ml_prediction.prob_up * 100).toFixed(1)}% Bullish
              </span>
            ) : (
              <span className="text-red-400">
                {((1 - (ex.ml_prediction?.prob_up || 0)) * 100).toFixed(1)}% Bearish
              </span>
            )}
          </div>
        </div>

        {/* Technicals */}
        <div className="flex justify-between items-center border-b border-white/10 pb-2">
          <div className="flex items-center gap-2 text-white/70">
            <Activity size={14} className="text-blue-400" /> Technical Score
          </div>
          <div className="font-mono text-white/90">
            {ex.technical?.technical_score?.toFixed(2) || "0.00"}
          </div>
        </div>

        {/* Risk & Volatility */}
        <div className="flex justify-between items-center border-b border-white/10 pb-2">
          <div className="flex items-center gap-2 text-white/70">
            <Shield size={14} className="text-yellow-400" /> Risk & Regime
          </div>
          <div className="font-mono text-right">
            <div className="text-white/90">{ex.volatility_regime}</div>
            <div className={`text-xs ${ex.risk?.pre_trade_approved ? "text-green-400" : "text-red-400"}`}>
              {ex.risk?.pre_trade_reason || "approved"}
            </div>
          </div>
        </div>

        {/* Final Decision */}
        <div className="pt-2">
          <div className="flex items-center justify-between bg-white/5 p-3 rounded">
            <span className="text-white/70 uppercase tracking-wider text-xs">Final Decision</span>
            <span className={`font-bold text-lg ${decision.action === 'BUY' ? 'text-green-400' : decision.action === 'SELL' ? 'text-red-400' : 'text-gray-400'}`}>
              {decision.action}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

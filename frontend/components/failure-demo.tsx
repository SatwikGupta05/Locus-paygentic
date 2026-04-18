"use client";

import { useStore } from "../lib/store";
import { AlertOctagon, TrendingDown, Percent, Activity } from "lucide-react";

export function FailureDemo() {
  const circuitBreaker = useStore((state) => state.decision?.explainability?.risk?.circuit_breaker as Record<string, unknown> | undefined);
  const reputation = useStore((state) => state.reputation);
  const pipeline = useStore((state) => state.pipeline);
  const decision = useStore((state) => state.decision);
  const orders = useStore((state) => state.orders);
  const recentRejection = orders.find((order) => order.status === "failed" || order.status === "cancelled");
  const lifecycle = recentRejection?.lifecycle as { state_history?: Array<{ metadata?: { reason?: string } }> } | undefined;

  const isTripped = circuitBreaker?.active || decision?.action === "HOLD" && decision?.risk_override === "circuit_breaker_tripped";

  return (
    <div className="panel space-y-4">
      <h2 className="text-sm font-semibold tracking-widest text-foam opacity-80 uppercase flex items-center gap-2">
        <Activity size={16} /> Reputation & Risk
      </h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white/5 rounded p-3 text-center">
          <div className="text-xs text-white/50 mb-1">Win Rate</div>
          <div className="font-mono text-lg text-white/90">
            {((reputation?.win_rate || 0) * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-white/5 rounded p-3 text-center">
          <div className="text-xs text-white/50 mb-1">Profit Factor</div>
          <div className="font-mono text-lg text-white/90">
            {(reputation?.profit_factor || 0).toFixed(2)}
          </div>
        </div>
        <div className="bg-white/5 rounded p-3 text-center">
          <div className="text-xs text-white/50 mb-1">Max Drawdown</div>
          <div className="font-mono text-lg text-red-400">
            {((reputation?.max_drawdown || 0) * 100).toFixed(1)}%
          </div>
        </div>
        <div className="bg-white/5 rounded p-3 text-center">
          <div className="text-xs text-white/50 mb-1">Net Score</div>
          <div className="font-mono text-lg text-foam">
            {reputation?.validation_score?.toFixed(1) || "0.0"} / 100
          </div>
        </div>
      </div>

      {isTripped && (
        <div className="rounded border border-red-500/30 bg-red-500/10 p-3 flex gap-3 text-red-400 items-start">
          <AlertOctagon size={20} className="shrink-0 mt-0.5" />
          <div className="text-sm">
            <strong className="block mb-1">Circuit Breaker Tripped</strong>
            Trading halted. Agent reached max continuous losses ({String(circuitBreaker?.threshold || 5)}). Waiting for regime change.
          </div>
        </div>
      )}

      {recentRejection && !isTripped && (
        <div className="rounded border border-yellow-500/30 bg-yellow-500/10 p-3 flex gap-3 text-yellow-400 items-start">
          <TrendingDown size={20} className="shrink-0 mt-0.5" />
          <div className="text-sm">
            <strong className="block mb-1">Order Aborted</strong>
            Last recorded order ({recentRejection.order_id}) was {recentRejection.status}. Reason: {lifecycle?.state_history?.[lifecycle.state_history.length - 1]?.metadata?.reason || "Unknown"}
          </div>
        </div>
      )}

      {!isTripped && !recentRejection && (
        <div className="rounded border border-green-500/30 bg-green-500/10 p-3 flex gap-3 text-green-400 items-start">
          <Percent size={20} className="shrink-0 mt-0.5" />
          <div className="text-sm">
            <strong className="block mb-1">Risk Parameters Optimal</strong>
            No circuit breakers or rejections active. System operating normally.
          </div>
        </div>
      )}
    </div>
  );
}

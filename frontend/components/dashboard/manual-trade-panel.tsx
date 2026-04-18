"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { useStore } from "../../lib/store";

export function ManualTradePanel() {
  const market = useStore((state) => state.market);
  const executeManualTrade = useStore((state) => state.executeManualTrade);
  
  const [amount, setAmount] = useState("0.01");
  const [customPrice, setCustomPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastTrade, setLastTrade] = useState<{ side: string; success: boolean } | null>(null);
  const [error, setError] = useState("");

  const currentPrice = market?.price || 67450;
  const tradePrice = customPrice ? parseFloat(customPrice) : currentPrice;

  const handleTrade = async (side: "BUY" | "SELL") => {
    setLoading(true);
    setError("");
    setLastTrade(null);

    try {
      if (!amount || parseFloat(amount) <= 0) {
        setError("Please enter a valid amount");
        setLoading(false);
        return;
      }

      const result = await executeManualTrade(side, parseFloat(amount), customPrice ? parseFloat(customPrice) : undefined);
      
      if (result.success) {
        setLastTrade({ side, success: true });
        setAmount("0.01");
        setCustomPrice("");
        setTimeout(() => setLastTrade(null), 3000);
      } else {
        setError(result.message);
        setLastTrade({ side, success: false });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Trade failed");
      setLastTrade({ side: "BUY", success: false });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-white/60 bg-white/68 p-6 shadow-[0_20px_70px_rgba(148,163,184,0.16)] backdrop-blur-xl">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-slate-900 mb-1">Manual Trade Execution</h3>
        <p className="text-xs text-slate-600">Paper trading with live KuCoin prices</p>
      </div>

      {/* Price Display */}
      <div className="mb-6 p-4 rounded-lg bg-slate-50 border border-slate-200">
        <p className="text-xs text-slate-600 mb-1">Current Market Price</p>
        <p className="text-2xl font-bold text-slate-900">${currentPrice.toFixed(2)}</p>
        <p className="text-xs text-slate-500 mt-1">Exchange: KuCoin</p>
      </div>

      {/* Input Form */}
      <div className="space-y-4 mb-6">
        {/* Amount Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 mb-2 block">
            Amount (BTC)
          </label>
          <input
            type="number"
            min="0.001"
            step="0.001"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            disabled={loading}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
            placeholder="0.01"
          />
          <p className="text-xs text-slate-500 mt-1">
            ≈ ${(parseFloat(amount) * tradePrice).toFixed(2)} USD
          </p>
        </div>

        {/* Price Input */}
        <div>
          <label className="text-xs font-semibold text-slate-700 mb-2 block">
            Execution Price (USD) - Optional
          </label>
          <input
            type="number"
            min="0"
            step="100"
            value={customPrice}
            onChange={(e) => setCustomPrice(e.target.value)}
            disabled={loading}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
            placeholder="Leave empty for market price"
          />
          <p className="text-xs text-slate-500 mt-1">
            {customPrice && (
              <>
                Slippage:{" "}
                <span
                  className={
                    parseFloat(customPrice) > currentPrice
                      ? "text-rose-600"
                      : "text-emerald-600"
                  }
                >
                  {parseFloat(customPrice) > currentPrice ? "+" : ""}
                  {((parseFloat(customPrice) - currentPrice) / currentPrice * 100).toFixed(2)}%
                </span>
              </>
            )}
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200">
          <p className="text-xs text-rose-700">❌ {error}</p>
        </div>
      )}

      {/* Success Message */}
      {lastTrade && lastTrade.success && (
        <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200">
          <p className="text-xs text-emerald-700">
            ✅ {lastTrade.side} trade executed successfully!
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3">
        {/* BUY Button */}
        <button
          onClick={() => handleTrade("BUY")}
          disabled={loading || !amount || parseFloat(amount) <= 0}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <TrendingUp className="h-4 w-4" />
          )}
          {loading ? "Executing..." : "BUY"}
        </button>

        {/* SELL Button */}
        <button
          onClick={() => handleTrade("SELL")}
          disabled={loading || !amount || parseFloat(amount) <= 0}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-rose-500 hover:bg-rose-600 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <TrendingDown className="h-4 w-4" />
          )}
          {loading ? "Executing..." : "SELL"}
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200">
        <p className="text-xs text-blue-700">
          💡 <strong>Paper Trading:</strong> All trades are simulated with real KuCoin prices. No real capital at risk.
        </p>
      </div>
    </div>
  );
}

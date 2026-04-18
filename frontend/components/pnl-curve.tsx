"use client";

import { createChart, IChartApi, UTCTimestamp } from "lightweight-charts";
import { useEffect, useRef, useState } from "react";
import { useStore } from "../lib/store";
import { getJson } from "../lib/api";

type Trade = {
  id: number;
  timestamp: string;
  realized_pnl: number;
};

export function PnlCurve({ startingBalance = 10000 }: { startingBalance?: number }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const pnlSeriesRef = useRef<any>(null);
  const btcSeriesRef = useRef<any>(null);
  
  const trades = useStore((state) => state.trades);
  const market = useStore((state) => state.market);
  
  const [initialTrades, setInitialTrades] = useState<Trade[]>([]);

  useEffect(() => {
    getJson<{ items: Trade[] }>("/trades").then((res) => {
      setInitialTrades(res.items.reverse());
    });
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: {
        background: { color: "transparent" },
        textColor: "rgba(255,255,255,0.6)",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.04)" },
        horzLines: { color: "rgba(255,255,255,0.04)" },
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.1)",
      },
      leftPriceScale: {
        visible: true,
        borderColor: "rgba(255,255,255,0.1)",
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.1)",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // PnL uses Area Series mapped to right axis
    const pnlSeries = chart.addAreaSeries({
      lineColor: "#a855f7", // purple-500
      topColor: "rgba(168, 85, 247, 0.4)",
      bottomColor: "rgba(168, 85, 247, 0.0)",
      lineWidth: 2,
      priceScaleId: 'right',
    });

    // BTC uses Line Series mapped to left axis
    const btcSeries = chart.addLineSeries({
      color: "rgba(255, 178, 43, 0.5)", // Orange BTC style
      lineWidth: 1,
      priceScaleId: 'left',
    });

    chartRef.current = chart;
    pnlSeriesRef.current = pnlSeries;
    btcSeriesRef.current = btcSeries;

    return () => {
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!pnlSeriesRef.current || !btcSeriesRef.current) return;

    const allTradesMap = new Map();
    initialTrades.forEach(t => allTradesMap.set(t.id, t));
    trades.forEach(t => allTradesMap.set(t.id, t));

    const sortedTrades = Array.from(allTradesMap.values()).sort((a, b) => a.id - b.id);

    let cumulative = startingBalance;
    const pnlData = sortedTrades.map((t) => {
      cumulative += t.realized_pnl;
      return {
        time: Math.floor(new Date(t.timestamp).getTime() / 1000) as UTCTimestamp,
        value: Number(cumulative.toFixed(2)),
      };
    });

    // Deduplicate PnL Time
    const dedupPnL = [];
    let lastTime = 0;
    for (const d of pnlData) {
      if (d.time > lastTime) {
        dedupPnL.push(d);
        lastTime = d.time;
      } else if (dedupPnL.length > 0) {
        dedupPnL[dedupPnL.length - 1] = d;
      }
    }
    
    if (dedupPnL.length === 0) {
      dedupPnL.push({ time: Math.floor(Date.now() / 1000) as UTCTimestamp, value: startingBalance });
    }

    pnlSeriesRef.current.setData(dedupPnL);

    // Apply BTC market benchmark
    if (market?.candles && Array.isArray(market.candles)) {
      const btcData = market.candles.map(c => ({
        time: Math.floor(new Date(c.timestamp).getTime() / 1000) as UTCTimestamp, 
        value: c.close
      }));

      // Deduplicate Market Time
      const dedupBTC = [];
      let lastBTC = 0;
      for (const d of btcData) {
        if (d.time > lastBTC) {
          dedupBTC.push(d);
          lastBTC = d.time;
        }
      }
      btcSeriesRef.current.setData(dedupBTC);
    }
    
    chartRef.current?.timeScale().fitContent();

  }, [initialTrades, trades, startingBalance, market]);

  return (
    <div className="panel space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-foam">Live Equity vs Market Benchmark</h2>
        <div className="flex gap-4 text-xs font-mono pr-2">
          <div className="flex items-center gap-1.5 text-purple-400"><div className="w-2 h-2 rounded-full bg-purple-500"></div> AI PnL</div>
          <div className="flex items-center gap-1.5 text-orange-400/80"><div className="w-2 h-2 rounded-full bg-orange-400/50"></div> BTC/USD</div>
        </div>
      </div>
      <div ref={containerRef} className="h-64 w-full" />
    </div>
  );
}

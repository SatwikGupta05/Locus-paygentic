"use client";

import { createChart, IChartApi, UTCTimestamp } from "lightweight-charts";
import { useEffect, useRef } from "react";

type Candle = {
  timestamp: string;
  close: number;
};

export function PriceChart({ candles }: { candles: Candle[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !candles.length) {
      return;
    }

    // Clean up old chart if it exists
    const existingChart = (containerRef.current as any).__chart;
    if (existingChart) {
      existingChart.remove();
    }

    const chart: IChartApi = createChart(containerRef.current, {
      autoSize: true,
      layout: {
        background: { color: "transparent" },
        textColor: "#d7f7ff",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.06)" },
        horzLines: { color: "rgba(255,255,255,0.06)" },
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.12)",
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.12)",
      },
    });

    // Store reference to chart on container for cleanup
    (containerRef.current as any).__chart = chart;

    const series = chart.addAreaSeries({
      lineColor: "#75f7c2",
      topColor: "rgba(117,247,194,0.35)",
      bottomColor: "rgba(117,247,194,0.02)",
    });

    series.setData(
      candles.map((candle) => ({
        time: Math.floor(new Date(candle.timestamp).getTime() / 1000) as UTCTimestamp,
        value: candle.close,
      })),
    );

    chart.timeScale().fitContent();

    return () => {
      chart.remove();
      (containerRef.current as any).__chart = undefined;
    };
  }, [candles]);

  return <div ref={containerRef} className="h-80 w-full" />;
}

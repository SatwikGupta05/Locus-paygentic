"use client";

import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi } from "lightweight-charts";
import { useStore } from "@/lib/store";

export function Chart() {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
    const { market } = useStore();

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: "transparent" },
                textColor: "#b8f3ff",
            },
            grid: {
                vertLines: { color: "rgba(255, 255, 255, 0.05)" },
                horzLines: { color: "rgba(255, 255, 255, 0.05)" },
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
        });

        const series = chart.addCandlestickSeries({
            upColor: "#75f7c2",
            downColor: "#ff7b54",
            borderVisible: false,
            wickUpColor: "#75f7c2",
            wickDownColor: "#ff7b54",
        });

        chartRef.current = chart;
        seriesRef.current = series;

        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener("resize", handleResize);

        return () => {
            window.removeEventListener("resize", handleResize);
            chart.remove();
        };
    }, []);

    useEffect(() => {
        if (market?.candles && seriesRef.current) {
            const chartData = market.candles.map((c: any) => ({
                time: new Date(c.timestamp).getTime() / 1000 as any,
                open: c.open,
                high: c.high,
                low: c.low,
                close: c.close,
            }));
            // Data must be unique and sorted by time ascending
            const uniqueData = Array.from(new Map(chartData.map((item: any) => [item.time, item])).values());
            uniqueData.sort((a: any, b: any) => a.time - b.time);
            seriesRef.current.setData(uniqueData as any);
        }
    }, [market]);

    return (
        <div className="panel border border-mint/20 col-span-full xl:col-span-2 relative">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-mint animate-pulse" />
                Live Price Action
                <span className="text-sm font-normal text-foam/70 ml-auto">
                    {market?.symbol || "Awaiting Data"}
                </span>
            </h2>
            <div ref={chartContainerRef} className="w-full h-[400px]" />
        </div>
    );
}

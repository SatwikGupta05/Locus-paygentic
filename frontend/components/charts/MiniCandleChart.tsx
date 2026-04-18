"use client";

import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip
} from "chart.js";
import { Line } from "react-chartjs-2";
import type { Candle } from "@/types";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

export function MiniCandleChart({ candles }: { candles: Candle[] }) {
  const labels = candles.map((candle) =>
    new Date(candle.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  const series = candles.map((candle, index) => {
    if (index === 0) {
      return candle.close;
    }

    const previousClose = candles[index - 1]?.close ?? candle.close;
    return candle.close >= previousClose ? candle.close : candle.close;
  });

  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label: "Close",
            data: series,
            borderColor: "#00e5a0",
            backgroundColor: "rgba(0, 229, 160, 0.08)",
            tension: 0.35,
            fill: true,
            pointRadius: 0
          }
        ]
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#0d1410",
            borderColor: "rgba(0,229,160,0.20)",
            borderWidth: 1,
            titleColor: "#e8f0eb",
            bodyColor: "#e8f0eb",
            displayColors: false
          }
        },
        scales: {
          x: {
            ticks: { color: "#5a7a65", maxTicksLimit: 6, font: { family: "JetBrains Mono", size: 10 } },
            grid: { color: "rgba(0,229,160,0.06)" }
          },
          y: {
            ticks: { color: "#5a7a65", font: { family: "JetBrains Mono", size: 10 } },
            grid: { color: "rgba(0,229,160,0.06)" }
          }
        }
      }}
    />
  );
}

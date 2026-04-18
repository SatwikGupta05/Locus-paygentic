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
import type { EquityPoint } from "@/types";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

export function EquityCurveChart({ points }: { points: EquityPoint[] }) {
  return (
    <Line
      data={{
        labels: points.map((point) =>
          new Date(point.x).toLocaleDateString([], { month: "short", day: "numeric" })
        ),
        datasets: [
          {
            label: "Equity",
            data: points.map((point) => point.y),
            borderColor: "#00e5a0",
            backgroundColor: "rgba(0, 229, 160, 0.07)",
            fill: true,
            pointRadius: 0,
            tension: 0.4,
            borderWidth: 1.5
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
            grid: { color: "rgba(0,229,160,0.05)" }
          },
          y: {
            ticks: { color: "#5a7a65", font: { family: "JetBrains Mono", size: 10 } },
            grid: { color: "rgba(0,229,160,0.05)" }
          }
        }
      }}
    />
  );
}

"use client";

import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export function ValidationBarChart({ values }: { values: number[] }) {
  return (
    <Bar
      data={{
        labels: values.map((_, index) => `V${index + 1}`),
        datasets: [
          {
            label: "Validation",
            data: values,
            backgroundColor: values.map((value) =>
              value >= 9 ? "#00e5a0" : value >= 7 ? "rgba(0,229,160,0.5)" : "#e84040"
            ),
            borderRadius: 3,
            borderSkipped: false
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
          x: { display: false, grid: { display: false } },
          y: { display: false, grid: { display: false } }
        }
      }}
    />
  );
}

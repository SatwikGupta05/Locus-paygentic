"use client";

import { useEffect, useState } from "react";
import { getJson } from "../lib/api";

export function ModeBadge() {
  const [config, setConfig] = useState<{ env: string; data_mode: string } | null>(null);

  useEffect(() => {
    getJson<{ env: string; data_mode: string }>("/config")
      .then(setConfig)
      .catch(console.error);
  }, []);

  if (!config) return null;

  return (
    <div className="flex items-center gap-2 text-xs font-medium tracking-wider uppercase">
      <div className="flex items-center gap-1 rounded px-2 py-1 bg-purple-100 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300">
        <span>MODE:</span> {config.env}
      </div>
      <div className="flex items-center gap-1 rounded px-2 py-1 bg-cyan-100 dark:bg-cyan-900/30 border border-cyan-200 dark:border-cyan-800 text-cyan-700 dark:text-cyan-300">
        <span>DATA:</span> {config.data_mode}
      </div>
      <div className="flex items-center gap-1 rounded px-2 py-1 bg-green-100 dark:bg-green-900/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300">
        <span>EXECUTION:</span> {config.env === "LIVE" ? "REAL" : "SIMULATED"}
      </div>
    </div>
  );
}

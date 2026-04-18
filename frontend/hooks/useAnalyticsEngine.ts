"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { computeAnalyticsMetrics } from "@/lib/analytics/engine";
import { useAnalyticsStore } from "@/store/analyticsStore";
import { usePortfolioStore } from "@/store/portfolioStore";
import type { Trade } from "@/types";

async function fetchTrades(): Promise<Trade[]> {
  const responses = await Promise.all([
    fetch("/api/kraken/trades"),
    fetch("/api/binance/trades"),
    fetch("/api/kucoin/trades")
  ]);

  const successful = responses.filter((response) => response.ok);
  const payloads = await Promise.all(successful.map(async (response) => (await response.json()) as Trade[]));
  return payloads.flat().sort((left, right) => left.time - right.time);
}

export function useAnalyticsEngine() {
  const query = useQuery({
    queryKey: ["allTrades"],
    queryFn: fetchTrades,
    refetchInterval: 30_000
  });

  useEffect(() => {
    if (!query.data) {
      return;
    }

    const startingCapital = usePortfolioStore.getState().allocatedCapital || 1;
    useAnalyticsStore.getState().setAnalytics(
      computeAnalyticsMetrics(query.data, startingCapital)
    );
    usePortfolioStore.getState().setTotalTrades(query.data.length);
  }, [query.data]);

  return query;
}

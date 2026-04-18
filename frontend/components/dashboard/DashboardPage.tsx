"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { ExchangeSelector } from "@/components/ExchangeSelector";
import { TopBar } from "@/components/TopBar";
import { useAgentStatePolling } from "@/hooks/useAgentStatePolling";
import { useAnalyticsEngine } from "@/hooks/useAnalyticsEngine";
import { useBinanceWs } from "@/hooks/useBinanceWs";
import { useContractPolling } from "@/hooks/useContractPolling";
import { useKrakenWs } from "@/hooks/useKrakenWs";
import { useKucoinWs } from "@/hooks/useKucoinWs";
import { useDecisionStore } from "@/store/decisionStore";
import { useMarketStore } from "@/store/marketStore";
import { usePortfolioStore } from "@/store/portfolioStore";
import { useSystemStore } from "@/store/systemStore";
import type { ExchangeName } from "@/types";
import { ActivityFeedPanel } from "./ActivityFeedPanel";
import { AgentIdentityCard } from "./AgentIdentityCard";
import { AIReasoningCard } from "./AIReasoningCard";
import { CapitalPortfolioCard } from "./CapitalPortfolioCard";
import { CurrentDecisionCard } from "./CurrentDecisionCard";
import { ExchangeHealthBar } from "./ExchangeHealthBar";
import { ExecutionQualityCard } from "./ExecutionQualityCard";
import { MarketStateCard } from "./MarketStateCard";
import { OnChainValidationCard } from "./OnChainValidationCard";
import { PerformanceAnalyticsCard } from "./PerformanceAnalyticsCard";
import { PipelineStatusCard } from "./PipelineStatusCard";
import { ReputationJudgeCard } from "./ReputationJudgeCard";
import { SystemTrustPanel } from "./SystemTrustPanel";
import styles from "./Dashboard.module.css";

async function fetchBalance(exchange: ExchangeName): Promise<{ usdt: number; btc: number }> {
  const response = await fetch(`/api/${exchange}/balance`);
  if (!response.ok) {
    throw new Error(`Unable to load ${exchange} balance`);
  }

  return (await response.json()) as { usdt: number; btc: number };
}

export function DashboardPage() {
  useKrakenWs();
  useBinanceWs();
  useKucoinWs();
  useContractPolling();
  useAgentStatePolling();
  useAnalyticsEngine();

  const balancesQuery = useQuery({
    queryKey: ["balances"],
    queryFn: async () => {
      const [kraken, binance, kucoin] = await Promise.all([
        fetchBalance("kraken"),
        fetchBalance("binance"),
        fetchBalance("kucoin")
      ]);

      return { kraken, binance, kucoin };
    },
    refetchInterval: 30_000
  });

  useEffect(() => {
    if (!balancesQuery.data) {
      return;
    }

    usePortfolioStore.getState().setBalance("kraken", balancesQuery.data.kraken.usdt);
    usePortfolioStore.getState().setBalance("binance", balancesQuery.data.binance.usdt);
    usePortfolioStore.getState().setBalance("kucoin", balancesQuery.data.kucoin.usdt);
  }, [balancesQuery.data]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      const market = useMarketStore.getState();
      const system = useSystemStore.getState();
      (["kraken", "binance", "kucoin"] as ExchangeName[]).forEach((exchange) => {
        const lastUpdate = market.exchanges[exchange].lastUpdate;
        const age = Date.now() - lastUpdate;
        if (!lastUpdate || age > 30000) {
          system.setExchangeHealth(exchange, "DOWN");
        } else if (age > 10000) {
          system.setExchangeHealth(exchange, "DEGRADED");
        } else {
          system.setExchangeHealth(exchange, "HEALTHY");
        }
      });

      if (Date.now() - useDecisionStore.getState().lastUpdated > 5000) {
        useDecisionStore.getState().setStale(true);
      }
    }, 1000);

    return () => window.clearInterval(interval);
  }, []);

  const connectedCount = useMarketStore((state) =>
    Object.values(state.exchanges).filter((exchange) => exchange.connected).length
  );

  return (
    <main className={styles.page}>
      <TopBar />
      {connectedCount === 0 ? (
        <div className={styles.banner}>All market feeds offline - pausing decisions</div>
      ) : null}
      <ExchangeSelector />
      <div className={styles.grid}>
        {/* Top Row: Context & Capital */}
        <MarketStateCard />
        <CapitalPortfolioCard />
        <AgentIdentityCard />

        {/* Middle Row: Logic & Decisions */}
        <CurrentDecisionCard />
        <AIReasoningCard />
        <PipelineStatusCard />

        {/* Bottom Section: Verification & Analytics */}
        <OnChainValidationCard />
        <ReputationJudgeCard />
        <ExecutionQualityCard />
        <PerformanceAnalyticsCard />
        <ActivityFeedPanel />
        <SystemTrustPanel />
        <ExchangeHealthBar />
      </div>
    </main>
  );
}

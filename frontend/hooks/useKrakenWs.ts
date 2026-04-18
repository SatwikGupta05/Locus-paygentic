"use client";

import { useEffect } from "react";
import { KrakenWs } from "@/lib/ws/krakenWs";
import { useDecisionStore } from "@/store/decisionStore";
import { useMarketStore } from "@/store/marketStore";
import { useSystemStore } from "@/store/systemStore";

export function useKrakenWs() {
  useEffect(() => {
    const marketStore = useMarketStore;
    const systemStore = useSystemStore;
    const decisionStore = useDecisionStore;

    const ws = new KrakenWs({
      onTicker: ({ price, bid, ask }) => {
        marketStore.getState().updateExchangeFeed("kraken", {
          price,
          bid,
          ask,
          connected: true,
          lastUpdate: Date.now()
        });
        marketStore.getState().recomputeBest();
        systemStore.getState().setExchangeHealth("kraken", "HEALTHY");
      },
      onCandle: (candle) => {
        marketStore.getState().addCandle("kraken", candle);
      },
      onStatus: (connected) => {
        marketStore.getState().updateExchangeFeed("kraken", { connected });
        systemStore.getState().setExchangeHealth("kraken", connected ? "HEALTHY" : "DEGRADED");
        if (!connected) {
          decisionStore.getState().addActivity({
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            text: "Kraken WebSocket disconnected, reconnecting",
            type: "system"
          });
        }
      }
    });

    ws.connect();
    return () => ws.close();
  }, []);
}

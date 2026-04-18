"use client";

import { useEffect } from "react";
import { BinanceWs } from "@/lib/ws/binanceWs";
import { useDecisionStore } from "@/store/decisionStore";
import { useMarketStore } from "@/store/marketStore";
import { useSystemStore } from "@/store/systemStore";

export function useBinanceWs() {
  useEffect(() => {
    const marketStore = useMarketStore;
    const systemStore = useSystemStore;
    const decisionStore = useDecisionStore;

    const ws = new BinanceWs({
      onTicker: ({ price, bid, ask }) => {
        marketStore.getState().updateExchangeFeed("binance", {
          price,
          bid,
          ask,
          connected: true,
          lastUpdate: Date.now()
        });
        marketStore.getState().recomputeBest();
        systemStore.getState().setExchangeHealth("binance", "HEALTHY");
      },
      onCandle: (candle) => {
        marketStore.getState().addCandle("binance", candle);
      },
      onStatus: (connected) => {
        marketStore.getState().updateExchangeFeed("binance", { connected });
        systemStore.getState().setExchangeHealth("binance", connected ? "HEALTHY" : "DEGRADED");
        if (!connected) {
          decisionStore.getState().addActivity({
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            text: "Binance WebSocket disconnected, reconnecting",
            type: "system"
          });
        }
      }
    });

    ws.connect();
    return () => ws.close();
  }, []);
}

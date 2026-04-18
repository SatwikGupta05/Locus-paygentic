"use client";

import { useEffect } from "react";
import { KucoinWs } from "@/lib/ws/kucoinWs";
import { useDecisionStore } from "@/store/decisionStore";
import { useMarketStore } from "@/store/marketStore";
import { useSystemStore } from "@/store/systemStore";

async function fetchConnection(): Promise<{ endpoint: string; token: string }> {
  const response = await fetch("/api/kucoin/ws-token");
  if (!response.ok) {
    throw new Error("Unable to fetch KuCoin WS token");
  }

  return (await response.json()) as { endpoint: string; token: string };
}

export function useKucoinWs() {
  useEffect(() => {
    const marketStore = useMarketStore;
    const systemStore = useSystemStore;
    const decisionStore = useDecisionStore;
    let ws: KucoinWs | null = null;
    let disposed = false;

    const connect = async () => {
      const connection = await fetchConnection();
      if (disposed) {
        return;
      }

      ws = new KucoinWs(connection, {
        onTicker: ({ price, bid, ask }) => {
          marketStore.getState().updateExchangeFeed("kucoin", {
            price,
            bid,
            ask,
            connected: true,
            lastUpdate: Date.now()
          });
          marketStore.getState().recomputeBest();
          systemStore.getState().setExchangeHealth("kucoin", "HEALTHY");
        },
        onCandle: (candle) => {
          marketStore.getState().addCandle("kucoin", candle);
        },
        onStatus: (connected) => {
          marketStore.getState().updateExchangeFeed("kucoin", { connected });
          systemStore.getState().setExchangeHealth("kucoin", connected ? "HEALTHY" : "DEGRADED");
          if (!connected) {
            decisionStore.getState().addActivity({
              time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              text: "KuCoin WebSocket disconnected, reconnecting",
              type: "system"
            });
          }
        },
        onTokenExpired: async () => {
          try {
            const nextConnection = await fetchConnection();
            ws?.updateConnection(nextConnection);
            ws?.connect();
          } catch {
            systemStore.getState().setExchangeHealth("kucoin", "DEGRADED");
          }
        }
      });

      ws.connect();
    };

    void connect();
    return () => {
      disposed = true;
      ws?.close();
    };
  }, []);
}

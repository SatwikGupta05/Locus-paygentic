import { create } from "zustand";
import type { Candle, ExchangeFeed, ExchangeName } from "@/types";

export interface MarketStore {
  pair: string;
  exchanges: Record<ExchangeName, ExchangeFeed>;
  bestPrice: number;
  bestBid: number;
  bestAsk: number;
  bestExchange: ExchangeName;
  spread: number;
  volatilityRegime: "Low" | "Medium" | "High";
  activeExchanges: ExchangeName[];
  updateExchangeFeed: (exchange: ExchangeName, data: Partial<ExchangeFeed>) => void;
  addCandle: (exchange: ExchangeName, candle: Candle) => void;
  recomputeBest: () => void;
  setActiveExchanges: (list: ExchangeName[]) => void;
}

const createFeed = (): ExchangeFeed => ({
  price: 0,
  bid: 0,
  ask: 0,
  candles: [],
  connected: false,
  lastUpdate: 0
});

function computeVolatility(candles: Candle[]): "Low" | "Medium" | "High" {
  if (candles.length < 2) {
    return "Low";
  }

  const highs = candles.map((candle) => candle.high);
  const lows = candles.map((candle) => candle.low);
  const range = Math.max(...highs) - Math.min(...lows);
  const base = candles[candles.length - 1]?.close ?? 1;
  const pct = base === 0 ? 0 : (range / base) * 100;

  if (pct >= 2) {
    return "High";
  }

  if (pct >= 0.75) {
    return "Medium";
  }

  return "Low";
}

export const useMarketStore = create<MarketStore>((set, get) => ({
  pair: process.env.NEXT_PUBLIC_TRADING_PAIR ?? "BTC/USDT",
  exchanges: {
    kraken: createFeed(),
    binance: createFeed(),
    kucoin: createFeed()
  },
  bestPrice: 0,
  bestBid: 0,
  bestAsk: 0,
  bestExchange: "kraken",
  spread: 0,
  volatilityRegime: "Low",
  activeExchanges: ["kraken", "binance", "kucoin"],
  updateExchangeFeed: (exchange, data) => {
    set((state) => ({
      exchanges: {
        ...state.exchanges,
        [exchange]: {
          ...state.exchanges[exchange],
          ...data
        }
      }
    }));
  },
  addCandle: (exchange, candle) => {
    set((state) => {
      const candles = [...state.exchanges[exchange].candles];
      const last = candles[candles.length - 1];
      if (last?.time === candle.time) {
        candles[candles.length - 1] = candle;
      } else {
        candles.push(candle);
      }

      return {
        exchanges: {
          ...state.exchanges,
          [exchange]: {
            ...state.exchanges[exchange],
            candles: candles.slice(-60)
          }
        }
      };
    });
  },
  recomputeBest: () => {
    const state = get();
    const eligible = state.activeExchanges
      .map((exchange) => ({
        exchange,
        ...state.exchanges[exchange]
      }))
      .filter((entry) => entry.bid > 0 && entry.ask > 0);

    if (eligible.length === 0) {
      set({ bestAsk: 0, bestBid: 0, bestPrice: 0, spread: 0 });
      return;
    }

    const bestBid = Math.max(...eligible.map((entry) => entry.bid));
    const asks = eligible.map((entry) => entry.ask).filter((value) => value > 0);
    const bestAsk = Math.min(...asks);
    const bestPrice = (bestBid + bestAsk) / 2;
    const bestExchange = eligible.reduce<ExchangeName>((closest, entry) => {
      const currentDistance = Math.abs(entry.price - bestPrice);
      const closestDistance = Math.abs(state.exchanges[closest].price - bestPrice);
      return currentDistance < closestDistance ? entry.exchange : closest;
    }, eligible[0].exchange);

    const spread = bestBid === 0 ? 0 : ((bestAsk - bestBid) / bestBid) * 100;
    const candles = eligible.flatMap((entry) => entry.candles);

    set({
      bestBid,
      bestAsk,
      bestPrice,
      bestExchange,
      spread,
      volatilityRegime: computeVolatility(candles)
    });
  },
  setActiveExchanges: (list) => {
    set({ activeExchanges: list });
    get().recomputeBest();
  }
}));

import type { Candle } from "@/types";

interface BinanceTickerPayload {
  c?: string;
  b?: string;
  a?: string;
}

interface BinanceKlinePayload {
  k?: {
    o?: string;
    h?: string;
    l?: string;
    c?: string;
    t?: number;
    v?: string;
  };
}

interface BinanceStreamMessage {
  stream?: string;
  data?: BinanceTickerPayload & BinanceKlinePayload;
}

interface BinanceWsHandlers {
  onTicker: (payload: { price: number; bid: number; ask: number }) => void;
  onCandle: (candle: Candle) => void;
  onStatus: (connected: boolean) => void;
}

export class BinanceWs {
  private socket: WebSocket | null = null;
  private retries = 0;
  private reconnectTimer: number | null = null;

  constructor(private readonly handlers: BinanceWsHandlers) {}

  connect() {
    const base = process.env.NEXT_PUBLIC_BINANCE_WS ?? "wss://stream.binance.com:9443/ws";
    this.socket = new WebSocket(`${base}/stream?streams=btcusdt@ticker/btcusdt@kline_1m`);

    this.socket.onopen = () => {
      this.retries = 0;
      this.handlers.onStatus(true);
    };

    this.socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data) as BinanceStreamMessage;
      if (parsed.stream === "btcusdt@ticker") {
        this.handlers.onTicker({
          price: Number(parsed.data?.c ?? 0),
          bid: Number(parsed.data?.b ?? 0),
          ask: Number(parsed.data?.a ?? 0)
        });
      }

      if (parsed.stream === "btcusdt@kline_1m" && parsed.data?.k) {
        const kline = parsed.data.k;
        this.handlers.onCandle({
          time: Number(kline.t ?? 0),
          open: Number(kline.o ?? 0),
          high: Number(kline.h ?? 0),
          low: Number(kline.l ?? 0),
          close: Number(kline.c ?? 0),
          volume: Number(kline.v ?? 0)
        });
      }
    };

    this.socket.onclose = () => {
      this.handlers.onStatus(false);
      this.scheduleReconnect();
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  close() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
    }
    this.socket?.close();
  }

  private scheduleReconnect() {
    const timeout = Math.min(1000 * 2 ** this.retries, 30000);
    this.retries += 1;
    this.reconnectTimer = window.setTimeout(() => this.connect(), timeout);
  }
}

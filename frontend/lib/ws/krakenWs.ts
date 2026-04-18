import type { Candle } from "@/types";

interface KrakenTickerMessage {
  channel?: string;
  data?: Array<{
    last?: string;
    bid?: string;
    ask?: string;
  }>;
}

interface KrakenOhlcMessage {
  channel?: string;
  data?: Array<{
    interval_begin?: string;
    open?: string;
    high?: string;
    low?: string;
    close?: string;
    volume?: string;
  }>;
}

interface KrakenWsHandlers {
  onTicker: (payload: { price: number; bid: number; ask: number }) => void;
  onCandle: (candle: Candle) => void;
  onStatus: (connected: boolean) => void;
}

function isTickerMessage(message: KrakenTickerMessage | KrakenOhlcMessage): message is KrakenTickerMessage {
  return message.channel === "ticker";
}

function isOhlcMessage(message: KrakenTickerMessage | KrakenOhlcMessage): message is KrakenOhlcMessage {
  return message.channel === "ohlc";
}

export class KrakenWs {
  private socket: WebSocket | null = null;
  private retries = 0;
  private reconnectTimer: number | null = null;

  constructor(private readonly handlers: KrakenWsHandlers) {}

  connect() {
    const url = process.env.NEXT_PUBLIC_KRAKEN_WS ?? "wss://ws.kraken.com/v2";
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.retries = 0;
      this.handlers.onStatus(true);
      this.socket?.send(
        JSON.stringify({
          method: "subscribe",
          params: { channel: "ticker", symbol: [process.env.NEXT_PUBLIC_TRADING_PAIR ?? "BTC/USDT"] }
        })
      );
      this.socket?.send(
        JSON.stringify({
          method: "subscribe",
          params: {
            channel: "ohlc",
            symbol: [process.env.NEXT_PUBLIC_TRADING_PAIR ?? "BTC/USDT"],
            interval: 1
          }
        })
      );
    };

    this.socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data) as KrakenTickerMessage | KrakenOhlcMessage;
      if (isTickerMessage(parsed)) {
        const ticker = parsed.data?.[0];
        if (ticker) {
          this.handlers.onTicker({
            price: Number(ticker.last ?? 0),
            bid: Number(ticker.bid ?? 0),
            ask: Number(ticker.ask ?? 0)
          });
        }
      }

      if (isOhlcMessage(parsed)) {
        const ohlc = parsed.data?.[0];
        if (ohlc?.interval_begin) {
          this.handlers.onCandle({
            time: new Date(ohlc.interval_begin).getTime(),
            open: Number(ohlc.open ?? 0),
            high: Number(ohlc.high ?? 0),
            low: Number(ohlc.low ?? 0),
            close: Number(ohlc.close ?? 0),
            volume: Number(ohlc.volume ?? 0)
          });
        }
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
    this.socket = null;
  }

  private scheduleReconnect() {
    const timeout = Math.min(1000 * 2 ** this.retries, 30000);
    this.retries += 1;
    this.reconnectTimer = window.setTimeout(() => this.connect(), timeout);
  }
}

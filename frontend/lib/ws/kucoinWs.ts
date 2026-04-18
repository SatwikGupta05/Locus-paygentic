import type { Candle } from "@/types";

interface KucoinConnectionPayload {
  endpoint: string;
  token: string;
}

interface KucoinWsHandlers {
  onTicker: (payload: { price: number; bid: number; ask: number }) => void;
  onCandle: (candle: Candle) => void;
  onStatus: (connected: boolean) => void;
  onTokenExpired: () => void;
}

export class KucoinWs {
  private socket: WebSocket | null = null;
  private retries = 0;
  private reconnectTimer: number | null = null;
  private pingTimer: number | null = null;
  private connectId = crypto.randomUUID();

  constructor(
    private connection: KucoinConnectionPayload,
    private readonly handlers: KucoinWsHandlers
  ) {}

  updateConnection(connection: KucoinConnectionPayload) {
    this.connection = connection;
    this.connectId = crypto.randomUUID();
  }

  connect() {
    this.socket = new WebSocket(
      `${this.connection.endpoint}?token=${this.connection.token}&connectId=${this.connectId}`
    );

    this.socket.onopen = () => {
      this.retries = 0;
      this.handlers.onStatus(true);
      this.socket?.send(
        JSON.stringify({
          id: this.connectId,
          type: "subscribe",
          topic: "/market/ticker:BTC-USDT",
          privateChannel: false,
          response: true
        })
      );
      this.socket?.send(
        JSON.stringify({
          id: this.connectId,
          type: "subscribe",
          topic: "/market/candles:BTC-USDT_1min",
          privateChannel: false,
          response: true
        })
      );
      this.pingTimer = window.setInterval(() => {
        this.socket?.send(JSON.stringify({ id: this.connectId, type: "ping" }));
      }, 18000);
    };

    this.socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data) as {
        topic?: string;
        data?: { price?: string; bestBid?: string; bestAsk?: string; candles?: string[] };
      };

      if (parsed.topic === "/market/ticker:BTC-USDT") {
        this.handlers.onTicker({
          price: Number(parsed.data?.price ?? 0),
          bid: Number(parsed.data?.bestBid ?? 0),
          ask: Number(parsed.data?.bestAsk ?? 0)
        });
      }

      if (parsed.topic === "/market/candles:BTC-USDT_1min" && parsed.data?.candles) {
        const [time, open, close, high, low, volume] = parsed.data.candles;
        this.handlers.onCandle({
          time: Number(time) * 1000,
          open: Number(open),
          high: Number(high),
          low: Number(low),
          close: Number(close),
          volume: Number(volume)
        });
      }
    };

    this.socket.onclose = (event) => {
      this.handlers.onStatus(false);
      if (event.code === 1000 || event.code === 1001) {
        this.handlers.onTokenExpired();
      } else {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  close() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
    }
    if (this.pingTimer) {
      window.clearInterval(this.pingTimer);
    }
    this.socket?.close();
  }

  private scheduleReconnect() {
    const timeout = Math.min(1000 * 2 ** this.retries, 30000);
    this.retries += 1;
    this.reconnectTimer = window.setTimeout(() => this.connect(), timeout);
  }
}

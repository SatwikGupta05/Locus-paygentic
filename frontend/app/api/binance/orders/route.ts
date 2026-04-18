import { NextResponse } from "next/server";
import { buildBinanceSignedQuery } from "@/lib/rest/binanceAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";
import type { OrderSummary } from "@/types";

export async function GET() {
  const key = process.env.BINANCE_API_KEY;
  const secret = process.env.BINANCE_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Binance credentials" }, { status: 500 });
  }

  try {
    const query = buildBinanceSignedQuery({ symbol: "BTCUSDT" }, secret);
    const response = await serverHttp.get(`https://api.binance.com/api/v3/openOrders?${query}`, {
      headers: {
        "X-MBX-APIKEY": key
      }
    });

    const orders: OrderSummary[] = (response.data as Array<Record<string, string | number | boolean>>).map(
      (order) => ({
        id: String(order.orderId ?? ""),
        exchange: "binance",
        pair: "BTC/USDT",
        side: String(order.side ?? "BUY").toLowerCase() === "sell" ? "sell" : "buy",
        status: String(order.status ?? "NEW"),
        price: Number(order.price ?? 0),
        volume: Number(order.origQty ?? 0),
        createdAt: Number(order.time ?? 0)
      })
    );

    return NextResponse.json(orders);
  } catch (error) {
    return buildExchangeErrorResponse("binance", error);
  }
}

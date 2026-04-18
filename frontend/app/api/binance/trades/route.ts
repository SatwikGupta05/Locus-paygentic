import { NextResponse } from "next/server";
import { buildBinanceSignedQuery } from "@/lib/rest/binanceAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";
import type { Trade } from "@/types";

export async function GET() {
  const key = process.env.BINANCE_API_KEY;
  const secret = process.env.BINANCE_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Binance credentials" }, { status: 500 });
  }

  try {
    const query = buildBinanceSignedQuery({ symbol: "BTCUSDT", limit: 500 }, secret);
    const response = await serverHttp.get(`https://api.binance.com/api/v3/myTrades?${query}`, {
      headers: {
        "X-MBX-APIKEY": key
      }
    });

    const trades: Trade[] = (response.data as Array<Record<string, string | number | boolean>>).map(
      (trade) => ({
        time: Number(trade.time ?? 0),
        pair: "BTC/USDT",
        type: Boolean(trade.isBuyer) ? "buy" : "sell",
        price: Number(trade.price ?? 0),
        vol: Number(trade.qty ?? 0),
        cost: Number(trade.quoteQty ?? 0),
        fee: Number(trade.commission ?? 0),
        ordertxid: String(trade.orderId ?? "")
      })
    );

    return NextResponse.json(trades);
  } catch (error) {
    return buildExchangeErrorResponse("binance", error);
  }
}

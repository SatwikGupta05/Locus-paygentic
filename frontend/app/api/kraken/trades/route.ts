import { NextResponse } from "next/server";
import { buildKrakenAuthHeaders } from "@/lib/rest/krakenAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";
import type { Trade } from "@/types";

export async function GET() {
  const key = process.env.KRAKEN_API_KEY;
  const secret = process.env.KRAKEN_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Kraken credentials" }, { status: 500 });
  }

  const path = "/0/private/TradesHistory";

  try {
    const { headers, payload } = buildKrakenAuthHeaders(path, {}, key, secret);
    const response = await serverHttp.post(`https://api.kraken.com${path}`, payload.toString(), {
      headers: {
        ...headers,
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    const trades = Object.values((response.data as any)?.result?.trades ?? {}).map((entry) => {
      const trade = entry as {
        time?: number;
        pair?: string;
        type?: "buy" | "sell";
        price?: string;
        vol?: string;
        cost?: string;
        fee?: string;
        ordertxid?: string;
      };
      const normalized: Trade = {
        time: Math.round((trade.time ?? 0) * 1000),
        pair: trade.pair ?? "BTC/USDT",
        type: trade.type ?? "buy",
        price: Number(trade.price ?? 0),
        vol: Number(trade.vol ?? 0),
        cost: Number(trade.cost ?? 0),
        fee: Number(trade.fee ?? 0),
        ordertxid: trade.ordertxid ?? ""
      };
      return normalized;
    });

    return NextResponse.json(trades);
  } catch (error) {
    return buildExchangeErrorResponse("kraken", error);
  }
}

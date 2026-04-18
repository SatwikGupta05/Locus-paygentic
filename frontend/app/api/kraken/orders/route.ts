import { NextResponse } from "next/server";
import { buildKrakenAuthHeaders } from "@/lib/rest/krakenAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";

export async function GET() {
  const key = process.env.KRAKEN_API_KEY;
  const secret = process.env.KRAKEN_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Kraken credentials" }, { status: 500 });
  }

  const path = "/0/private/OpenOrders";

  try {
    const { headers, payload } = buildKrakenAuthHeaders(path, {}, key, secret);
    const response = await serverHttp.post(`https://api.kraken.com${path}`, payload.toString(), {
      headers: {
        ...headers,
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    const open = (response.data as any)?.result?.open ?? {};
    const orders = Object.entries(open).map(([id, value]) => {
      const order = value as {
        descr?: { pair?: string; type?: "buy" | "sell"; price?: string };
        status?: string;
        vol?: string;
        opentm?: number;
      };
      return {
        id,
        exchange: "kraken",
        pair: order.descr?.pair ?? "BTC/USDT",
        side: order.descr?.type ?? "buy",
        status: order.status ?? "open",
        price: Number(order.descr?.price ?? 0),
        volume: Number(order.vol ?? 0),
        createdAt: Math.round((order.opentm ?? 0) * 1000)
      };
    });

    return NextResponse.json(orders);
  } catch (error) {
    return buildExchangeErrorResponse("kraken", error);
  }
}

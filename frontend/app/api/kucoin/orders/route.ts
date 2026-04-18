import { NextResponse } from "next/server";
import { buildKucoinHeaders } from "@/lib/rest/kucoinAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";
import type { OrderSummary } from "@/types";

export async function GET() {
  const key = process.env.KUCOIN_API_KEY;
  const secret = process.env.KUCOIN_API_SECRET;
  const passphrase = process.env.KUCOIN_API_PASSPHRASE;

  if (!key || !secret || !passphrase) {
    return NextResponse.json({ error: "Missing KuCoin credentials" }, { status: 500 });
  }

  try {
    const path = "/api/v1/orders?status=active&symbol=BTC-USDT";
    const response = await serverHttp.get(`https://api.kucoin.com${path}`, {
      headers: buildKucoinHeaders("GET", path, "", key, secret, passphrase)
    });

    const orders: OrderSummary[] = ((response.data as any)?.data?.items ?? []).map(
      (order: Record<string, string>) => ({
        id: order.id ?? "",
        exchange: "kucoin",
        pair: "BTC/USDT",
        side: order.side === "sell" ? "sell" : "buy",
        status: order.status ?? "active",
        price: Number(order.price ?? 0),
        volume: Number(order.size ?? 0),
        createdAt: Number(order.createdAt ?? 0)
      })
    );

    return NextResponse.json(orders);
  } catch (error) {
    return buildExchangeErrorResponse("kucoin", error);
  }
}

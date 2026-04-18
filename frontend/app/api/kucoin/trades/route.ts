import { NextResponse } from "next/server";
import { buildKucoinHeaders } from "@/lib/rest/kucoinAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";
import type { Trade } from "@/types";

export async function GET() {
  const key = process.env.KUCOIN_API_KEY;
  const secret = process.env.KUCOIN_API_SECRET;
  const passphrase = process.env.KUCOIN_API_PASSPHRASE;

  if (!key || !secret || !passphrase) {
    return NextResponse.json({ error: "Missing KuCoin credentials" }, { status: 500 });
  }

  try {
    const path = "/api/v1/fills?symbol=BTC-USDT&pageSize=50";
    const response = await serverHttp.get(`https://api.kucoin.com${path}`, {
      headers: buildKucoinHeaders("GET", path, "", key, secret, passphrase)
    });

    const trades: Trade[] = ((response.data as any)?.data?.items ?? []).map((trade: Record<string, string>) => ({
      time: Number(trade.createdAt ?? 0),
      pair: "BTC/USDT",
      type: trade.side === "sell" ? "sell" : "buy",
      price: Number(trade.price ?? 0),
      vol: Number(trade.size ?? 0),
      cost: Number(trade.funds ?? 0),
      fee: Number(trade.fee ?? 0),
      ordertxid: trade.orderId ?? ""
    }));

    return NextResponse.json(trades);
  } catch (error) {
    return buildExchangeErrorResponse("kucoin", error);
  }
}

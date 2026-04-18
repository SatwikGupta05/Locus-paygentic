import { NextResponse } from "next/server";
import { buildBinanceSignedQuery } from "@/lib/rest/binanceAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";

export async function GET() {
  const key = process.env.BINANCE_API_KEY;
  const secret = process.env.BINANCE_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Binance credentials" }, { status: 500 });
  }

  try {
    const query = buildBinanceSignedQuery({}, secret);
    const response = await serverHttp.get(`https://api.binance.com/api/v3/account?${query}`, {
      headers: {
        "X-MBX-APIKEY": key
      }
    });

    const balances = (response.data as any)?.balances as Array<{ asset: string; free: string }> | undefined;
    const usdt = Number(balances?.find((entry) => entry.asset === "USDT")?.free ?? 0);
    const btc = Number(balances?.find((entry) => entry.asset === "BTC")?.free ?? 0);

    return NextResponse.json({ usdt, btc });
  } catch (error) {
    return buildExchangeErrorResponse("binance", error);
  }
}

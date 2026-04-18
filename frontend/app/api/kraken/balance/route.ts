import { NextResponse } from "next/server";
import { buildKrakenAuthHeaders } from "@/lib/rest/krakenAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";

export async function GET() {
  const key = process.env.KRAKEN_API_KEY;
  const secret = process.env.KRAKEN_API_SECRET;

  if (!key || !secret) {
    return NextResponse.json({ error: "Missing Kraken credentials" }, { status: 500 });
  }

  const path = "/0/private/Balance";

  try {
    const { headers, payload } = buildKrakenAuthHeaders(path, {}, key, secret);
    const response = await serverHttp.post(`https://api.kraken.com${path}`, payload.toString(), {
      headers: {
        ...headers,
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    const result = (response.data as any)?.result as Record<string, string>;
    return NextResponse.json({
      usdt: Number(result.ZUSD ?? result.USDT ?? 0),
      btc: Number(result.XXBT ?? result.XBT ?? 0)
    });
  } catch (error) {
    return buildExchangeErrorResponse("kraken", error);
  }
}

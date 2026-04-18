import { NextResponse } from "next/server";
import { buildKucoinHeaders } from "@/lib/rest/kucoinAuth";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";

export async function GET() {
  const key = process.env.KUCOIN_API_KEY;
  const secret = process.env.KUCOIN_API_SECRET;
  const passphrase = process.env.KUCOIN_API_PASSPHRASE;

  if (!key || !secret || !passphrase) {
    return NextResponse.json({ error: "Missing KuCoin credentials" }, { status: 500 });
  }

  try {
    const usdtPath = "/api/v1/accounts?currency=USDT&type=trade";
    const btcPath = "/api/v1/accounts?currency=BTC&type=trade";
    const [usdtResponse, btcResponse] = await Promise.all([
      serverHttp.get(`https://api.kucoin.com${usdtPath}`, {
        headers: buildKucoinHeaders("GET", usdtPath, "", key, secret, passphrase)
      }),
      serverHttp.get(`https://api.kucoin.com${btcPath}`, {
        headers: buildKucoinHeaders("GET", btcPath, "", key, secret, passphrase)
      })
    ]);

    const usdt = Number((usdtResponse.data as any)?.data?.[0]?.available ?? 0);
    const btc = Number((btcResponse.data as any)?.data?.[0]?.available ?? 0);

    return NextResponse.json({ usdt, btc });
  } catch (error) {
    return buildExchangeErrorResponse("kucoin", error);
  }
}

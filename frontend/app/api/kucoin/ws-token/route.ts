import { NextResponse } from "next/server";
import { serverHttp, buildExchangeErrorResponse } from "@/lib/rest/http";

export async function GET() {
  try {
    const response = await serverHttp.post("https://api.kucoin.com/api/v1/bullet-public");
    const endpoint = (response.data as any)?.data?.instanceServers?.[0]?.endpoint as string | undefined;
    const token = (response.data as any)?.data?.token as string | undefined;

    return NextResponse.json({
      endpoint,
      token
    });
  } catch (error) {
    return buildExchangeErrorResponse("kucoin", error);
  }
}

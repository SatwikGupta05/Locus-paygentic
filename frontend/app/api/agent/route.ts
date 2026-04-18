import { NextResponse } from "next/server";
import { fetchBackendJson } from "../_lib/backend";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const data = await fetchBackendJson<Record<string, unknown>>("/agent");
    return NextResponse.json(data, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Backend unavailable" },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}

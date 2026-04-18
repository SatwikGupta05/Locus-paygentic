import { NextRequest, NextResponse } from "next/server";
import { buildBackendUrl } from "../../_lib/backend";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const query = request.nextUrl.search || "";
  const upstreamUrl = `${buildBackendUrl(`/${path.join("/")}`)}${query}`;

  try {
    const response = await fetch(upstreamUrl, {
      cache: "no-store",
      headers: {
        Accept: request.headers.get("accept") || "application/json",
      },
    });

    const body = await response.text();

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") || "application/json",
        "cache-control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Backend proxy request failed", detail: error instanceof Error ? error.message : "Unknown error" },
      { status: 502 },
    );
  }
}

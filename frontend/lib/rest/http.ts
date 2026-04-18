import { NextResponse } from "next/server";

export interface ServerHttpResponse<T> {
  data: T;
  status: number;
}

export const serverHttp = {
  async get<T>(url: string, options?: { timeout?: number; headers?: Record<string, string> }): Promise<ServerHttpResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options?.timeout ?? 5000);
    try {
      const response = await fetch(url, {
        method: "GET",
        signal: controller.signal,
        cache: "no-store",
        headers: { Accept: "application/json", ...(options?.headers ?? {}) },
      });
      if (!response.ok) {
        const error: any = new Error(`Request failed: ${response.status}`);
        error.response = { status: response.status, data: await response.json().catch(() => ({})) };
        throw error;
      }
      const data = (await response.json()) as T;
      return { data, status: response.status };
    } finally {
      clearTimeout(timeoutId);
    }
  },

  async post<T>(url: string, body?: string | Record<string, unknown>, options?: { timeout?: number; headers?: Record<string, string> }): Promise<ServerHttpResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options?.timeout ?? 5000);
    try {
      const response = await fetch(url, {
        method: "POST",
        signal: controller.signal,
        cache: "no-store",
        headers: { Accept: "application/json", ...(options?.headers ?? {}) },
        body: typeof body === "string" ? body : JSON.stringify(body),
      });
      if (!response.ok) {
        const error: any = new Error(`Request failed: ${response.status}`);
        error.response = { status: response.status, data: await response.json().catch(() => ({})) };
        throw error;
      }
      const data = (await response.json()) as T;
      return { data, status: response.status };
    } finally {
      clearTimeout(timeoutId);
    }
  },
};

export function buildExchangeErrorResponse(exchange: "kraken" | "binance" | "kucoin", error: unknown) {
  const err = error as { response?: { status?: number; data?: { error?: string; msg?: string } }; message?: string };
  const status = err.response?.status ?? 500;
  const message = err.response?.data?.msg ?? err.response?.data?.error ?? err.message ?? "Unknown error";

  return NextResponse.json({ exchange, error: message }, { status });
}

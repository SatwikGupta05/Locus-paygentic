import crypto from "crypto";

export function buildBinanceSignedQuery(
  params: Record<string, string | number>,
  secret: string
): string {
  const queryString = new URLSearchParams({
    ...Object.fromEntries(Object.entries(params).map(([key, value]) => [key, String(value)])),
    timestamp: Date.now().toString()
  }).toString();

  const signature = crypto.createHmac("sha256", secret).update(queryString).digest("hex");
  return `${queryString}&signature=${signature}`;
}

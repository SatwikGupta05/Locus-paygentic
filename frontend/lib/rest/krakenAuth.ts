import crypto from "crypto";

export function buildKrakenAuthHeaders(
  path: string,
  body: Record<string, string>,
  key: string,
  secret: string
): {
  headers: Record<string, string>;
  payload: URLSearchParams;
} {
  const nonce = Date.now().toString();
  const payload = new URLSearchParams({ nonce, ...body });
  const message = nonce + payload.toString();
  const hash = crypto.createHash("sha256").update(message).digest();
  const signature = crypto
    .createHmac("sha512", Buffer.from(secret, "base64"))
    .update(Buffer.concat([Buffer.from(path), hash]))
    .digest("base64");

  return {
    headers: {
      "API-Key": key,
      "API-Sign": signature
    },
    payload
  };
}

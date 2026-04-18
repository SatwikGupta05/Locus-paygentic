import crypto from "crypto";

export function buildKucoinHeaders(
  method: string,
  path: string,
  body: string,
  key: string,
  secret: string,
  passphrase: string
): Record<string, string> {
  const timestamp = Date.now().toString();
  const strToSign = `${timestamp}${method.toUpperCase()}${path}${body}`;
  const sign = crypto.createHmac("sha256", secret).update(strToSign).digest("base64");
  const signedPassphrase = crypto
    .createHmac("sha256", secret)
    .update(passphrase)
    .digest("base64");

  return {
    "KC-API-KEY": key,
    "KC-API-SIGN": sign,
    "KC-API-TIMESTAMP": timestamp,
    "KC-API-PASSPHRASE": signedPassphrase,
    "KC-API-KEY-VERSION": "2"
  };
}

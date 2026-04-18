---
name: locus-fiat-payments
description: Make fiat card purchases on behalf of users. Use when the user asks you to buy something, make a purchase, or use their card. Requires the user to have a card on file with Locus.
allowed-tools: Bash WebFetch
---

# Fiat Card Payments

Pay for things with your human's debit or credit card via Locus.

**API Base:** `https://api.paywithlocus.com/api`
**Auth:** `Authorization: Bearer YOUR_LOCUS_API_KEY`

## How It Works

1. Your human adds a card and enables payments on their Locus dashboard
2. You find what to buy (web search, API, user instruction)
3. You initiate a charge → get an approval link
4. Your human taps the link and verifies with fingerprint/face ID (takes 5 seconds)
5. You get virtual card credentials to use at the merchant

## Step 1: Check Available Cards

```bash
curl https://api.paywithlocus.com/api/pay/cards \
  -H "Authorization: Bearer $LOCUS_API_KEY"
```

Response:
```json
{
  "success": true,
  "data": {
    "cards": [
      {
        "id": "abc123",
        "brand": "visa",
        "last4": "4242",
        "enrollment_status": "active"
      }
    ]
  }
}
```

Only cards with `enrollment_status: "active"` can be charged.
If no cards or none enrolled, tell the user to add a card at their Locus dashboard.

## Step 2: Initiate a Charge

```bash
curl -X POST https://api.paywithlocus.com/api/pay/charge-card \
  -H "Authorization: Bearer $LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "abc123",
    "amount": 29.99,
    "description": "Blue wireless headphones from BestBuy",
    "merchant": {
      "name": "Best Buy",
      "url": "https://www.bestbuy.com",
      "country_code": "US"
    }
  }'
```

Response (202):
```json
{
  "success": true,
  "data": {
    "pending_approval_id": "uuid",
    "approval_url": "https://app.paywithlocus.com/fiat-approve/token123",
    "charge_id": "chg_abc",
    "status": "PENDING_VERIFICATION",
    "amount": 29.99,
    "merchant": "Best Buy",
    "card": { "brand": "visa", "last4": "4242" }
  }
}
```

## Step 3: Send Approval Link to Your Human

Send the `approval_url` to your human. They do NOT need to log in — the link works standalone.

Say something like:
> "I found the headphones for $29.99 at Best Buy. I've initiated the charge on your Visa *4242. Please tap this link to approve: [approval_url]"

The user opens the link, sees the charge details, and verifies with fingerprint/face ID. Takes about 5 seconds.

## Step 4: Poll for Credentials

After sending the link, poll every 5 seconds:

```bash
curl https://api.paywithlocus.com/api/pay/charge-status/{pending_approval_id} \
  -H "Authorization: Bearer $LOCUS_API_KEY"
```

Responses:
- `PENDING_VERIFICATION` — user hasn't approved yet, keep polling
- `DENIED` — user rejected the charge, inform them
- `APPROVED` — credentials available:

```json
{
  "status": "APPROVED",
  "credentials": {
    "number": "4111111111111234",
    "expiration_month": "03",
    "expiration_year": "2027",
    "cvc": "987"
  },
  "expires_at": "2026-04-09T00:00:00Z"
}
```

## Step 5: Use the Virtual Card

The credentials are a **one-time use** virtual card. Use them at the merchant's checkout. They expire at `expires_at`.

## Product Discovery

Before charging, you need to know what to buy. Approaches:
- **Ask the user** what they want and where to get it
- **Web search** to find products, compare prices, check availability
- **Merchant APIs** if available (e.g., Amazon Product API, store APIs)

Present the product details and price to the user before initiating the charge.

## Policy Limits

Same spending controls as crypto payments:
- **Allowance** — total spending limit (403 if exceeded)
- **Max transaction size** — per-charge cap (403 if exceeded)
- **Approval threshold** — charges above this always need approval (fiat charges always need approval regardless)

If you hit a 403, tell the user their spending limit was reached and suggest they adjust it in their dashboard.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 403 | Policy limit exceeded | Tell user to increase limits |
| 400 + "not enrolled" | Card not set up for payments | Tell user to enable payments on /cards page |
| 404 | Card not found | List cards again, pick a valid one |
| `DENIED` status | User rejected the charge | Acknowledge, ask if they want to try a different amount |
| `EXPIRED` | Approval link expired | Create a new charge |

## Important Notes

- Charges are always in USD
- Virtual card credentials are **one-time use** — don't reuse them
- Credentials typically expire within 24 hours
- The approval link does NOT require the user to log in
- Always present the purchase details before initiating a charge
- Poll at most for 5 minutes before considering the charge timed out

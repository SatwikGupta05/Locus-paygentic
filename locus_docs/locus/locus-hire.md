---
name: locus-hire
description: Order freelance work through Locus's escrow-backed marketplace (Hire with Locus). Browse categories, place orders, and track delivery. Use when the user wants to hire a freelancer, order design work, writing, or other freelance services.
allowed-tools: Bash WebFetch
---

# Locus — Hire with Locus (Freelance Marketplace)

Order freelance work with USDC held in escrow until completion.

**API Base:** `https://api.paywithlocus.com/api`
**Auth:** `Authorization: Bearer $LOCUS_API_KEY`

## Browse Categories

```bash
curl https://api.paywithlocus.com/api/fiverr/categories \
  -H "Authorization: Bearer $LOCUS_API_KEY"
```

Returns categories with slugs and tiered pricing.

## Place an Order

```bash
curl -X POST https://api.paywithlocus.com/api/fiverr/orders \
  -H "Authorization: Bearer $LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category_slug": "logo_design",
    "tier": 2,
    "timeline": "3d",
    "request": "Modern minimalist logo for NovaPay. Blue/white, SVG format."
  }'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_slug` | string | Yes | From categories list |
| `tier` | integer | Yes | Tier number |
| `timeline` | string | Yes | `1d`, `3d`, or `7d` |
| `request` | string | Yes | What you need (max 500 chars). Include URLs for reference files. |

Returns 202. If `PENDING_APPROVAL`, send the `approval_url` to the user.

## Check Orders

```bash
# List orders
curl "https://api.paywithlocus.com/api/fiverr/orders?limit=50" \
  -H "Authorization: Bearer $LOCUS_API_KEY"

# Single order
curl "https://api.paywithlocus.com/api/fiverr/orders/ORDER_ID" \
  -H "Authorization: Bearer $LOCUS_API_KEY"
```

**Statuses:** CREATED -> DEPOSITING -> PENDING_APPROVAL -> APPROVED -> COMPLETING -> **COMPLETED** (deliverables available) or **CANCELLED** (funds returned)

Poll every 30 minutes during heartbeat. Report completed deliverables and cancellations to the user.

## Limits

- Max 10 active orders at once
- Request text: 1-500 characters

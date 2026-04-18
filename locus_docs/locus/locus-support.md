---
name: locus-support
description: Ask the Locus support bot questions about Locus APIs, endpoints, spending controls, and concepts. Use when the user or agent needs help understanding how Locus works or troubleshooting an API issue.
allowed-tools: Bash WebFetch
---

# Locus Support Chat

Query the Locus support bot for instant answers about Locus documentation.

**Endpoint:** `POST <LOCUS_BOT_URL>/ask`
**Auth:** `Authorization: Bearer <AGENT_API_KEY>` (optional — depends on deployment)

> The bot URL is a Lambda Function URL. Check `LOCUS_BOT_URL` env var or ask the user.

## Single Question

```bash
curl -X POST "$LOCUS_BOT_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{ "question": "How do I check my wallet balance?" }'
```

Returns `{ "answer": "...", "elapsed": "4.2s", "messages": [...] }`

## Multi-Turn

Pass the full `messages` array from the previous response to continue the conversation:

```bash
curl -X POST "$LOCUS_BOT_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "How do I send USDC?" },
      { "role": "assistant", "content": "..." },
      { "role": "user", "content": "What about email transfers?" }
    ]
  }'
```

## When to Use

- Unsure how an endpoint works or what parameters it expects
- Need troubleshooting help with an error response
- Want a quick explainer on Locus concepts (spending controls, x402, escrow, etc.)

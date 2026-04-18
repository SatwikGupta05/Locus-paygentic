---
name: locus-agentmail
description: Email for AI agents via AgentMail through Locus. Create inboxes, send emails, reply, and manage threads. Use when the user needs to send or receive email, create an email inbox, or manage email communications.
allowed-tools: Bash WebFetch
---

# Locus — AgentMail

Email for AI agents. Create inboxes, send/receive messages, reply, and manage threads — all via x402.

**API Base:** `https://api.paywithlocus.com/api`
**Auth:** `Authorization: Bearer $LOCUS_API_KEY`

## Endpoints

All called via `POST /api/x402/<slug>`.

| Action | Slug | Cost | Key Params |
|--------|------|------|------------|
| Create inbox | `agentmail-create-inbox` | ~$2.00 | `username` -> `username@agentmail.to` |
| List inboxes | `agentmail-list-inboxes` | ~$0.001 | `{}` |
| Send email | `agentmail-send-message` | ~$0.01 | `inbox_id`, `to: [{"email": "..."}]`, `subject`, `body` |
| List messages | `agentmail-list-messages` | ~$0.001 | `inbox_id` |
| Get message | `agentmail-get-message` | ~$0.001 | `inbox_id`, `message_id` |
| Reply | `agentmail-reply` | ~$0.01 | `inbox_id`, `message_id`, `body` |
| List threads | `agentmail-list-threads` | ~$0.001 | `inbox_id` |

## Example: Set Up and Send

```bash
# 1. Create inbox
curl -X POST https://api.paywithlocus.com/api/x402/agentmail-create-inbox \
  -H "Authorization: Bearer $LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username": "my-agent"}'

# 2. Send email
curl -X POST https://api.paywithlocus.com/api/x402/agentmail-send-message \
  -H "Authorization: Bearer $LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "inbox_id": "inbox_abc123",
    "to": [{"email": "recipient@example.com"}],
    "subject": "Hello",
    "body": "Sent by an AI agent via AgentMail."
  }'

# 3. Check for replies
curl -X POST https://api.paywithlocus.com/api/x402/agentmail-list-messages \
  -H "Authorization: Bearer $LOCUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inbox_id": "inbox_abc123"}'
```

Save the `inboxId` from step 1 — it's needed for all other endpoints.

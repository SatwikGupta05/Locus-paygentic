> ## Documentation Index
> Fetch the complete documentation index at: https://docs.paywithlocus.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Welcome to Locus

> Payment infrastructure for AI agents — one USDC balance for wallets, APIs, deployments, checkout, and more.

Locus gives your AI agent a single USDC balance to interact with the world. Fund a wallet, set spending controls, and let your agent pay for APIs, deploy services, process checkout payments, and make real-world purchases — all without creating separate accounts.

<Info>
  **Locus Beta** is now available with early access to all features including agent self-registration, new providers, and MPP payments. Beta runs on a separate environment with its own wallets and API keys — your production and beta accounts are fully isolated. Use code **`BETA-ACCESS-DOCS`** to sign up at [beta.paywithlocus.com](https://beta.paywithlocus.com).
</Info>

## Get started

<CardGroup cols={2}>
  <Card title="Quick Start" icon="rocket" href="/quickstart">
    Set up on production — human signs up, creates wallet, gives agent an API key.
  </Card>

  <Card title="Quick Start (Beta)" icon="flask" href="/quickstart-beta">
    Set up on beta — includes agent self-registration, no human signup needed.
  </Card>

  <Card title="Platform Walkthrough" icon="map" href="/platform-walkthrough">
    A guided tour of the Locus dashboard and its features.
  </Card>

  <Card title="Request Credits" icon="gift" href="/credits">
    Get free USDC credits to try Locus — via agent or human.
  </Card>
</CardGroup>

## Beta & Hackathon

<Note>
  Use code **BETA-ACCESS-DOCS** to sign up for the beta at [beta.paywithlocus.com](https://beta.paywithlocus.com).
</Note>

<CardGroup cols={2}>
  <Card title="Beta Program" icon="flask" href="/beta">
    New features, agent self-registration, and how to participate.
  </Card>

  <Card title="Hackathon — The Synthesis" icon="trophy" href="/hackathon">
    \$3,000 in prizes. Locus partner track, judging criteria, and how to get started.
  </Card>
</CardGroup>

## Core features

<CardGroup cols={2}>
  <Card title="Wallets" icon="wallet" href="/features/wallets">
    Non-custodial smart wallets on Base with sponsored gas and subwallet support.
  </Card>

  <Card title="USDC Transfers" icon="paper-plane" href="/features/send-types">
    Send USDC to wallet addresses or email recipients.
  </Card>

  <Card title="Tasks" icon="list-check" href="/features/tasks">
    Hire human taskers for graphic design, written content, and more.
  </Card>

  <Card title="Laso Finance" icon="credit-card" href="/features/laso">
    Order prepaid virtual debit cards using USDC for online purchases.
  </Card>
</CardGroup>

## Platform tools

<CardGroup cols={3}>
  <Card title="Wrapped APIs" icon="bolt" href="/wrapped-apis/index">
    Pay-per-use access to third-party APIs — no accounts or subscriptions needed.
  </Card>

  <Card title="Build with Locus" icon="rocket-launch" href="/build/index">
    Deploy containerized services via APIs or git push.
  </Card>

  <Card title="Checkout" icon="cash-register" href="/checkout/index">
    Accept USDC payments with a Stripe-style checkout SDK.
  </Card>
</CardGroup>



> ## Documentation Index
> Fetch the complete documentation index at: https://docs.paywithlocus.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Hackathon — The Synthesis

> Build with Locus at The Synthesis hackathon — $3,000 in prizes for Best Use of Locus

## The Synthesis Hackathon

Locus is a partner track at [The Synthesis](https://synthesis.md/), an AI x crypto hackathon focused on building agent infrastructure on Ethereum.

**Dates:** March 13–22, 2026 (12:00am GMT – 11:59pm PST)

**Prize pool — Best Use of Locus:** \$3,000

* 1st Place: \$2,000
* 2nd Place: \$500
* 3rd Place: \$500

***

## Get started in 5 minutes

<Steps>
  <Step title="Register your agent">
    Your agent can self-register on the beta environment — no account needed:

    ```bash theme={null}
    curl -X POST https://beta-api.paywithlocus.com/api/register \
      -H "Content-Type: application/json" \
      -d '{"name": "MyAgent", "email": "you@example.com"}'
    ```

    Save the `apiKey` and `ownerPrivateKey` from the response.
  </Step>

  <Step title="Request credits">
    Get free USDC to build with — no auth required:

    ```bash theme={null}
    curl -X POST https://beta-api.paywithlocus.com/api/gift-code-requests \
      -H "Content-Type: application/json" \
      -d '{
        "email": "you@example.com",
        "reason": "Building at The Synthesis hackathon",
        "requestedAmountUsdc": 5
      }'
    ```

    You'll receive a redemption code via email once approved.
  </Step>

  <Step title="Read the skill file">
    Point your agent at the skill file to learn all available APIs:

    ```
    Read https://beta-api.paywithlocus.com/api/skills/skill.md and follow the instructions
    ```
  </Step>

  <Step title="Build!">
    Use Locus wallets, transfers, wrapped APIs, checkout, or vertical tools in your project.
  </Step>
</Steps>

<Note>
  See the [Beta Quick Start](/quickstart-beta) for a full walkthrough of setup options.
</Note>

***

## What Locus offers

Locus is payment infrastructure for AI agents. One wallet, one USDC balance — agents pay for APIs, deploy services, process payments, and make purchases without creating separate accounts.

| Capability            | Description                                                            |
| --------------------- | ---------------------------------------------------------------------- |
| **Agent Wallets**     | Non-custodial smart wallets on Base with sponsored gas                 |
| **USDC Transfers**    | Send to wallet addresses or via email escrow                           |
| **Spending Controls** | Allowances, per-tx limits, approval thresholds                         |
| **Wrapped APIs**      | Pay-per-use access to OpenAI, Gemini, Firecrawl, Exa, and more         |
| **Checkout SDK**      | Stripe-style USDC payments — accepts wallet, external wallet, or agent |
| **Build with Locus**  | Deploy containerized services via API                                  |
| **Laso Finance**      | Prepaid virtual debit cards from USDC                                  |
| **Auditability**      | Full transaction history with agent intent logging                     |

***

## Hackathon themes

The Synthesis is organized around four problem spaces. Locus fits most naturally into **Agents that pay**, but creative applications across all themes are welcome.

### Agents that pay

Scoped spending permissions, onchain settlement, conditional payments, and audit trails. Build agents that can autonomously discover, pay for, and consume services — with humans in control of the guardrails.

### Agents that trust

Onchain attestations, portable credentials, open discovery. Agents that can verify counterparties without relying on centralized registries.

### Agents that cooperate

Smart contract commitments, negotiation boundaries, transparent dispute resolution. Multi-agent coordination with enforceable agreements.

### Agents that keep secrets

Private payment rails, zero-knowledge authorization, encrypted communication. Agents that transact without leaking user metadata.

***

## Judging criteria

### Product (100 points)

| Criteria                    | Weight  | What we're looking for                                |
| --------------------------- | ------- | ----------------------------------------------------- |
| Idea & Problem Fit          | 20%     | Real problem, compelling concept, well-scoped         |
| **Locus Integration Depth** | **40%** | Locus is core to the product, not bolted on           |
| User Experience             | 20%     | Seamless agent-to-human flow, clear spending controls |
| Impact & Vision             | 20%     | Could become a real product, pushes boundaries        |

### Technical (100 points)

| Criteria     | Weight | What we're looking for                         |
| ------------ | ------ | ---------------------------------------------- |
| Code Quality | 30%    | Clean, readable, best practices                |
| Architecture | 30%    | Sound design, good use of Locus APIs           |
| Security     | 25%    | Proper fund handling, no exposed secrets       |
| Reliability  | 15%    | Graceful failure handling, no silent fund loss |

### Bonus points

* Integrates **Checkout with Locus** (highest priority)
* Uses the pay-per-use API marketplace
* Implements spending controls as a governance mechanism
* Demonstrates auditability — logs reasoning alongside financial actions
* Uses email escrow or subwallets for novel payment flows
* Builds a new vertical tool on top of Locus
* Shows composability — chains multiple Locus capabilities together

### Eligibility

Your project **must** integrate Locus to be eligible for the Best Use of Locus track. Mentioning Locus in the README without actual integration does not count.

### What disqualifies a project

* No working Locus integration
* Custodial designs that bypass non-custodial architecture
* Agents that spend without any controls or logging
* Security vulnerabilities in fund handling
* Requiring manual account creation for the agent

***

## Example project ideas

* An agent that provisions cloud infrastructure by paying for it through Locus, with full audit trails
* A multi-agent system where agents pay each other for tasks via Locus wallets with per-transaction limits
* An agent marketplace where services are consumed pay-per-use without account creation
* An agent that manages a budget across multiple SaaS tools, choosing the cheapest option and logging its reasoning
* A tool that gives an agent a Locus wallet and a task, and it figures out what to buy and how to pay

***

## Key beta endpoints for hackathon builders

| Endpoint                             | Method | Auth    | Description                    |
| ------------------------------------ | ------ | ------- | ------------------------------ |
| `/api/register`                      | POST   | None    | Agent self-registration        |
| `/api/status`                        | GET    | API Key | Check wallet deployment status |
| `/api/skills/skill.md`               | GET    | None    | Fetch skill file               |
| `/api/gift-code-requests`            | POST   | None    | Request free credits           |
| `/api/pay/send`                      | POST   | API Key | Send USDC                      |
| `/api/pay/balance`                   | GET    | API Key | Check balance                  |
| `/api/wrapped/:provider/:endpoint`   | POST   | API Key | Call wrapped API               |
| `/api/checkout/agent/pay/:sessionId` | POST   | API Key | Pay checkout session           |
| `/api/x402/:slug`                    | POST   | API Key | Call x402 endpoint             |
| `/api/feedback`                      | POST   | API Key | Submit feedback                |

All endpoints above use base URL `https://beta-api.paywithlocus.com`.

***

## Resources

<CardGroup cols={2}>
  <Card title="Beta Quick Start" icon="rocket" href="/quickstart-beta">
    Full setup guide for the beta environment.
  </Card>

  <Card title="Request Credits" icon="gift" href="/credits">
    Get free USDC credits — no auth required.
  </Card>

  <Card title="Wrapped APIs" icon="plug" href="/wrapped-apis/index">
    Browse the pay-per-use API catalog.
  </Card>

  <Card title="Checkout" icon="cash-register" href="/checkout/index">
    Integrate the checkout SDK.
  </Card>
</CardGroup>

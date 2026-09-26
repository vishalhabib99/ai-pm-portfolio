# Memo: which model, and how to price it: an AI support-drafting feature in a B2B SaaS helpdesk

**Author:** Vishal Habib · **Date:** 2026-09-26 · **Feature:** [ticket triage + draft replies](../prds/2026-08-support-ticket-triage-assistant.md) (sample PRD) · **Numbers:** [`unit_economics.py`](unit_economics.py), which re-runs in one command

## The decision

A mid-size SaaS support team gets ~1,200 tickets a day (from the PRD). The feature classifies every ticket and drafts a reply for the ~35% that are known issues. An agent always reviews before sending. Two questions:

1. **Which model(s) should run it?**
2. **How should the SaaS vendor price it** to its customers?

## Recommendation

1. **Route by job, and pick the cheapest option that passes the eval gate. Don't pick by price alone.** Test Haiku 4.5 for everything first, then Haiku triage with Sonnet 5 drafts, then Sonnet 5 for everything. Use the PRD's existing gates (≥ 90% accuracy, ≥ 95% precision on high-confidence predictions, > 60% of drafts sent with minor edits). The cheapest option that passes wins. Opus 5.5 isn't needed for this job unless every cheaper option fails the gates.
2. **Price per seat against the value delivered, with a fair-use allowance, not per token.** Model cost is 1–5% of the value delivered, so it isn't what limits the price. What limits it is the accepted-draft rate.
3. **Don't lead with prompt caching as the cost story.** Here it moves cost about 5%, because the expensive input (retrieved help docs) is different on every ticket.

## Cost per option

Prices are from Anthropic's [pricing page](https://platform.claude.com/docs/en/about-claude/pricing), read 2026-09-26 (per million tokens):

| Model | Input | Cache read | Output |
|---|---|---|---|
| Haiku 4.5 | $1 | $0.10 | $5 |
| Sonnet 5 | $2 | $0.20 | $10 |
| Opus 5.5 | $4 | $0.20 | $20 |

The pricing page also says Claude 4.7-and-later models use a tokenizer that produces **~30% more tokens for the same text**. That applies to Sonnet 5 and Opus 5.5, and the model includes it. Comparing prices per token without it understates their cost.

Result for 36,000 tickets and 12,600 drafts a month, 40 support seats:

| Option | $/month | Per ticket | Per accepted draft | Per seat/month | Price/seat at 80% gross margin |
|---|---|---|---|---|---|
| A. Opus 5.5 everywhere, no caching | $721 | $0.020 | $0.095 | $18.03 | $90 |
| B. Sonnet 5 everywhere, caching | $201 | $0.006 | $0.027 | $5.02 | $25 |
| **C. Haiku 4.5 triage + Sonnet 5 drafts, caching** | **$156** | **$0.004** | **$0.021** | **$3.89** | **$19** |
| D. Haiku 4.5 everywhere, caching | $77 | $0.002 | $0.010 | $1.93 | $10 |

**Value side:** 7,560 accepted drafts × 3 minutes saved × $40/hour loaded agent cost ≈ **$15,120/month, about $378 per seat.** Even option A costs under 5% of that.

## What actually drives cost

Sensitivity of option C when one assumption goes up 50%:

| Assumption | Change in cost |
|---|---|
| Share of tickets that get a draft | **+41%** |
| Retrieved help-doc tokens per draft | **+21%** |
| Draft length (output tokens) | +13% |
| Ticket length | +9% |
| Cached system prompt | +5% |

So the cost levers are **product decisions**: how confident the classifier must be before drafting, and how many help-doc passages to retrieve. Infrastructure tricks like caching matter much less. Tightening the draft threshold cuts cost *and* bad drafts at the same time.

**Batch** (50% off, results within 24 hours) doesn't suit real-time triage. It does suit side jobs: tagging every ticket nightly for a weekly themes report costs about **$17/month** on Haiku 4.5 with Batch and caching.

## Pricing to customers

- **Per seat, not per token.** Customers buy agent productivity. Per-token billing makes them budget for something they can't predict. At $3.89 per seat in model cost, a per-seat add-on priced well below the ~$378/seat of time saved leaves room for margin and a clear ROI story.
- **Include an allowance, with overage.** Cost follows *tickets*, not seats. A small team drowning in tickets costs more to serve than a large team with few. Include a monthly allowance of drafts per seat and charge overage beyond it, so heavy users don't break the margin.
- **Not per resolution, yet.** Outcome pricing ("per resolved ticket") matches value best, but it pays for "resolved" and invites false containment: tickets closed without actually being fixed. Add it only once reopen rate (the PRD's guardrail metric) is tracked well enough to define "resolved" honestly.

## What this doesn't know yet

- **Quality per model hasn't been measured.** The prototype's cheapest baseline (TF-IDF, no model) failed the gate at 60% ([case study](../case-studies/2026-08-support-ticket-triage-assistant.md)), and no Claude model has been run against the eval yet. The recommendation is a test order, not a result. Running the prototype's 10-ticket eval on all four options costs well under a dollar (and 10 tickets is too few to decide on; the eval set should grow first).
- **Token counts are assumptions**, all listed at the top of `unit_economics.py`. Replace them with the `usage` numbers from real calls, and re-run.
- **Loaded agent cost and minutes saved are assumptions** too, and they decide the value side. They should come from a time study before any price goes to customers.
- The feature is a sample PRD, not a shipped product.

"""Unit economics for the ticket-triage + draft-reply feature (prds/2026-08-support-ticket-triage-assistant.md).

Prices: Anthropic pricing page, read 2026-09-26 (https://platform.claude.com/docs/en/about-claude/pricing).
Every token count below is an ASSUMPTION to be replaced with measured `usage` from real calls.
Run: python memos/unit_economics.py
"""

# $ per million tokens: input, 5-minute cache write, cache read, output. Batch = 50% off input and output.
PRICES = {
    "haiku-4.5": {"in": 1.00, "write": 1.25, "read": 0.10, "out": 5.00},
    "sonnet-5": {"in": 2.00, "write": 2.50, "read": 0.20, "out": 10.00},
    "opus-5.5": {"in": 4.00, "write": 5.00, "read": 0.20, "out": 20.00},
}
# Claude 4.7-and-later models use a tokenizer the pricing page says yields ~30% more tokens for the same text.
TOKENIZER = {"haiku-4.5": 1.0, "sonnet-5": 1.3, "opus-5.5": 1.3}

# --- assumptions (token counts measured on Haiku 4.5's tokenizer) ---
TICKETS_PER_MONTH = 1_200 * 30          # PRD: ~1,200 tickets/day
DRAFT_SHARE = 0.35                      # PRD: ~35% are known issues that get a draft
PREFIX = 1_500                          # system prompt + taxonomy + instructions (identical every call -> cacheable)
TICKET = 400                            # ticket text
DOCS = 2_000                            # retrieved help-doc passages for a draft (varies per ticket -> not cached)
TRIAGE_OUT = 30                         # category + priority + confidence
DRAFT_OUT = 250                         # draft reply
CACHE_HIT = 0.95                        # share of prefix reads served from cache at ~50 tickets/hour
AGENTS = 40                             # support seats handling that volume
MINUTES_SAVED_PER_ACCEPTED_DRAFT = 3    # agent time saved when a draft is sent with minor edits
LOADED_COST_PER_AGENT_HOUR = 40.0
ACCEPTED_DRAFT_RATE = 0.60              # PRD target: >60% of drafts sent with only minor edits


def call_cost(model, uncached_in, out, cached_prefix=0, cache=True, batch=False):
    p, k = PRICES[model], TOKENIZER[model]
    if cache:
        prefix = cached_prefix * k * (CACHE_HIT * p["read"] + (1 - CACHE_HIT) * p["write"])
    else:
        prefix = cached_prefix * k * p["in"]
    cost = (prefix + uncached_in * k * p["in"] + out * k * p["out"]) / 1e6
    return cost * (0.5 if batch else 1.0)


def monthly(triage_model, draft_model, cache):
    triage = TICKETS_PER_MONTH * call_cost(triage_model, TICKET, TRIAGE_OUT, PREFIX, cache)
    drafts = TICKETS_PER_MONTH * DRAFT_SHARE * call_cost(draft_model, TICKET + DOCS, DRAFT_OUT, PREFIX, cache)
    return triage + drafts


OPTIONS = [
    ("A. Opus 5.5 for everything, no caching", "opus-5.5", "opus-5.5", False),
    ("B. Sonnet 5 for everything, caching", "sonnet-5", "sonnet-5", True),
    ("C. Routed: Haiku 4.5 triage + Sonnet 5 drafts, caching", "haiku-4.5", "sonnet-5", True),
    ("D. Haiku 4.5 for everything, caching", "haiku-4.5", "haiku-4.5", True),
]

if __name__ == "__main__":
    drafts = TICKETS_PER_MONTH * DRAFT_SHARE
    accepted = drafts * ACCEPTED_DRAFT_RATE
    value = accepted * MINUTES_SAVED_PER_ACCEPTED_DRAFT / 60 * LOADED_COST_PER_AGENT_HOUR
    print(f"Volume: {TICKETS_PER_MONTH:,} tickets/month, {drafts:,.0f} drafts, {accepted:,.0f} accepted drafts\n")
    print("| Option | $/month | $ per ticket | $ per accepted draft | $ per seat/month | Price/seat for 80% gross margin |")
    print("|---|---|---|---|---|---|")
    for name, t, d, c in OPTIONS:
        m = monthly(t, d, c)
        print(f"| {name} | ${m:,.0f} | ${m / TICKETS_PER_MONTH:.4f} | ${m / accepted:.4f} | ${m / AGENTS:,.2f} | ${m / AGENTS / 0.2:,.2f} |")
    print(f"\nAgent time saved by accepted drafts (value side): ${value:,.0f}/month (${value / AGENTS:,.0f} per seat)")
    base = monthly("opus-5.5", "opus-5.5", False)
    for name, t, d, c in OPTIONS[1:]:
        print(f"{name[:2]} costs {monthly(t, d, c) / base:.0%} of option A")
    nightly = TICKETS_PER_MONTH * call_cost("haiku-4.5", TICKET, 60, PREFIX, cache=True, batch=True)
    print(f"\nNightly theme tagging of every ticket on Haiku 4.5 via Batch + caching: ${nightly:,.2f}/month")
    # Sensitivity: which assumption moves option C most? (+50% each)
    print("\nSensitivity of option C to +50% on one assumption:")
    c0 = monthly("haiku-4.5", "sonnet-5", True)
    g = globals()
    for var in ["DOCS", "DRAFT_OUT", "PREFIX", "TICKET", "DRAFT_SHARE"]:
        old = g[var]; g[var] = old * 1.5
        print(f"  {var:12} +50% -> {monthly('haiku-4.5', 'sonnet-5', True) / c0 - 1:+.0%}")
        g[var] = old

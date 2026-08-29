> **Note:** Sample/practice case study, following on from the [PRD](../prds/2026-08-support-ticket-triage-assistant.md) and [prototype](../prototypes/ticket-triage-rag/) in this repo. Not a real shipped project — it documents the prototype/eval phase honestly, including the part where the first approach didn't work.

# Case Study: Ticket Triage Assistant — Prototype & Eval

**Date:** 2026-08-29

## What shipped

Not a launch — a prototype and its evaluation. Built a TF-IDF retrieval pipeline (`prototypes/ticket-triage-rag/`) that classifies support tickets into 4 categories and drafts a grounded reply from a small help-doc corpus, plus an offline eval harness that scores it against 10 labeled test tickets, matching the evaluation plan laid out in the PRD.

## Key decisions & tradeoffs

- **Built the cheapest possible baseline first** (pure TF-IDF cosine similarity, no LLM call) instead of going straight to an LLM-based classifier. This was deliberate: it's the fastest way to get a number on the board and stress-test the eval methodology itself before spending on a more expensive approach.
- **Wrote the eval set before looking at results**, including 2 deliberately off-topic tickets ("company history", "student discounts") that shouldn't match any category. This is what caught the real failure mode — an eval set of only on-topic tickets would have looked artificially good.
- **Set a hard launch bar up front** (≥90% accuracy, ≥95% precision on high-confidence predictions, from the PRD) rather than deciding after seeing results whether the numbers were "good enough." This mattered — the result gave no ambiguity to rationalize around.

## What broke / what didn't work

The baseline failed the launch bar: **60% accuracy, 60% precision on high-confidence predictions**, against targets of 90%/95%.

Specifically: TF-IDF cosine similarity has no real concept of "none of these categories fit" — it always returns whichever doc is *least dissimilar*, even when the ticket isn't about any of them. Both off-topic test tickets matched `billing` with enough score to clear the confidence threshold and would have gone out as a wrong, confidently-worded draft reply. Two genuine bug reports also got misclassified as `password_reset` / `plan_limits` for the same reason — shared common words, not shared meaning.

This is exactly the kind of thing an eval gate is supposed to catch before launch, and it did its job. The mistake would have been skipping the eval, or eyeballing a few good-looking examples (like the first 3 sample tickets in `rag.py`, which all worked fine) and calling it done.

## Outcome

**Decision: do not proceed with the TF-IDF-only approach.** Two concrete next steps identified for the next iteration:
1. Replace the similarity-based classification step with an LLM call (the PRD's original approach), which should handle "this doesn't match anything" far better than raw cosine similarity.
2. Add an explicit "none of the above" reference point to compare against, regardless of classifier choice, so ambiguous tickets have somewhere to fall through to instead of always being forced into the closest category.

The honest number (60%, documented in the prototype's README rather than hidden) is the actual deliverable here — it's what a real PRD's eval gate is for, and a negative result from a cheap baseline is what justifies spending more on the LLM-based version next.

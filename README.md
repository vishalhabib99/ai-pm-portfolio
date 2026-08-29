# AI PM Portfolio

Structured record of product work as an AI Product Manager: how problems were framed, what was decided, what shipped, and what it moved.

## Structure

- **`prds/`** — Product requirement docs for AI features (problem, users, success metrics, scope, risks/evals plan)
- **`case-studies/`** — Post-launch writeups: what was built, the tradeoffs made, and the measured outcome
- **`prototypes/`** — Small working builds (RAG pipelines, agent demos, eval harnesses) that back up the PRDs with something real

## Featured: Ticket Triage Assistant

A complete PRD → prototype → case-study arc, worth reading start to finish:

1. [**PRD**](prds/2026-08-support-ticket-triage-assistant.md) — problem framing, RAG-vs-fine-tuning tradeoff, success metrics, evaluation plan
2. [**Prototype**](prototypes/ticket-triage-rag/) — a working TF-IDF RAG pipeline with a real eval harness, run against 10 labeled test tickets
3. [**Case study**](case-studies/2026-08-support-ticket-triage-assistant.md) — the honest result: the baseline failed the launch bar (60% vs. a 90% target), why, and what the eval gate caught before it could ship

This one's marked as a sample/practice piece rather than real shipped work, but it's meant to show the actual thing that matters: PRD → build → eval → honest verdict, not just a list of bullet points.

## Status

More PRDs, prototypes, and case studies added as real projects come in.

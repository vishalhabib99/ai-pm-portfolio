# AI PM Portfolio

Structured record of product work as an AI Product Manager: how problems were framed, what was decided, what shipped, and what it moved.

## Structure

- **`prds/`** — Product requirement docs for AI features (problem, users, success metrics, scope, risks/evals plan)
- **`case-studies/`** — Post-launch writeups: what was built, the tradeoffs made, and the measured outcome
- **`prototypes/`** — Small working builds (RAG pipelines, agent demos, eval harnesses) that back up the PRDs with something real

## Featured: Agent Codebase Readiness Score (ACRS)

A product idea grounded in real, sourced 2026 industry data on why agentic AI projects fail to reach production — and a working prototype that proves the core mechanic on a real codebase, not a toy example.

1. [**PRD**](prds/2026-08-agent-codebase-readiness-score.md) — the problem: 79% of enterprises adopt AI agents, only 11% reach production; coding agents perform far worse on real codebases than on demos. Sourced from IBM, Gartner-cited research, MachineLearningMastery, Lyzr, Arcade.dev, MorphLLM, and Webfuse (full citations in the PRD).
2. [**Prototype**](prototypes/agent-codebase-readiness-score/) — a real per-module readiness scorer, run against the actual [pallets/flask](https://github.com/pallets/flask) production codebase. Includes an honestly-disclosed limitation in one of its own proxy metrics, found and documented rather than hidden.
3. [**Case study**](case-studies/2026-08-agent-codebase-readiness-score.md) — what the prototype proved, what broke in one of its own scoring heuristics, and the concrete next steps identified from it.

## Also: Ticket Triage Assistant (practice arc)

A complete PRD → prototype → case-study arc used to establish the working method, marked as sample/practice work rather than a real project:

- [PRD](prds/2026-08-support-ticket-triage-assistant.md) · [Prototype](prototypes/ticket-triage-rag/) · [Case study](case-studies/2026-08-support-ticket-triage-assistant.md)

Its prototype's baseline **failed** its own launch bar (60% vs. a 90% target) — kept in the repo on purpose, because a real eval that catches a real failure is more credible than a demo tuned to always look good.

## Status

More PRDs, prototypes, and case studies added as real projects come in.

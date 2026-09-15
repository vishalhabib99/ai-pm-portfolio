# AI PM Portfolio

Structured record of product work as an AI Product Manager: how problems were framed, what was decided, what shipped, and what it moved.

## About

Written by [Vishal Habib](https://github.com/vishalhabib99) — Product Leader currently building the Agentic AI Digital Advisor at Vanguard ($6B+ LOB, 4M+ MAU), previously launched one of the first autonomous enterprise Agentic AI platforms in US telecom at T-Mobile (75% adoption, 80% CSAT). Full background: [LinkedIn](https://www.linkedin.com/in/vishal-habib/) · [website](https://vishalhabib.netlify.app/).

The PRDs and prototypes below are separate from that employer work (nothing proprietary or confidential included) — they're where new ideas get tested using the same rigor: real data, real code, honest evals.

## Structure

- **`prds/`** — Product requirement docs for AI features (problem, users, success metrics, scope, risks/evals plan)
- **`case-studies/`** — Post-launch writeups: what was built, the tradeoffs made, and the measured outcome
- **`prototypes/`** — Small working builds (RAG pipelines, agent demos, eval harnesses) that back up the PRDs with something real

## Featured: Agent Codebase Readiness Score (ACRS)

A product idea grounded in real, sourced 2026 industry data on why agentic AI projects fail to reach production — and a working prototype that proves the core mechanic on a real codebase, not a toy example.

1. [**PRD**](prds/2026-08-agent-codebase-readiness-score.md) — the problem: 79% of enterprises adopt AI agents, only 11% reach production; coding agents perform far worse on real codebases than on demos. Sourced from IBM, Gartner-cited research, MachineLearningMastery, Lyzr, Arcade.dev, MorphLLM, and Webfuse (full citations in the PRD).
2. [**Prototype**](prototypes/agent-codebase-readiness-score/) — a real per-module readiness scorer, run against the actual [pallets/flask](https://github.com/pallets/flask) production codebase. Includes an honestly-disclosed limitation in one of its own proxy metrics, found, fixed, and re-validated with real before/after numbers.
3. [**Case study**](case-studies/2026-08-agent-codebase-readiness-score.md) — what the prototype proved, what broke in one of its own scoring heuristics, and how the fix changed the actual outcome.

## Featured: a three-tool MCP quality-assurance stack, real OSS contributions not simulated ones

Three independent, complementary open-source CLIs that together audit an MCP server end to end — is it documented ([mcp-doctor](https://github.com/vishalhabib99/mcp-doctor), `pip install mcp-server-lint`), does it fail safely ([mcp-fuzz](https://github.com/vishalhabib99/mcp-fuzz), `pip install mcp-runtime-check`), and does it actually work ([mcp-reality-check](https://github.com/vishalhabib99/mcp-reality-check), `pip install mcp-reality-check`) — each verified against real, actively-maintained repos instead of fixtures. All three are also wrapped in one composite GitHub Action, [mcp-trust-check](https://github.com/vishalhabib99/mcp-trust-check), that runs the whole trilogy against a PR and posts one combined score instead of three separate installs.

1. [**Case study: one arc, two correction cycles**](case-studies/2026-08-mcp-doctor-oss-contribution.md) — shipped a finding on a 4.6k-star repo, got told with specifics why it was wrong (twice, once on a security-flavored claim that turned out to be false), verified each correction against the actual source before fixing it, and landed a [merged PR](https://github.com/homeassistant-ai/ha-mcp/pull/2327). The correction cycles are the point, not the merge.
2. [**Case study: turning that into a repeatable process**](case-studies/2026-09-mcp-doctor-systematic-dogfooding.md) — the same discipline run 20+ times against real servers up to 50k stars, including GitHub's own official `github-mcp-server` (32.6k★, 0 of 114+ tools invisible until fixed), plus two feature requests correctly declined once the actual engineering cost was traced out. The judgment call that repeats every pass: is this a real gap, and is it worth building support for.
3. [**Case study: completing the trilogy, catching my own bugs twice**](case-studies/2026-09-mcp-fuzz-and-reality-check.md) — building the two remaining tools, and two separate incidents where dogfooding caught a real bug in the tool itself before it shipped: one, an over-broad fix that would have silently retracted an already-public finding, caught by re-verifying every claim already made before calling a fix done; the other, the newest tool's very first extended dogfood pass finding a bug in its own input generator. Neither bug reached anyone else.
4. [**Case study: an unsolicited collaboration request that shipped a fix in someone else's repo**](case-studies/2026-09-agentinspect-collaboration.md) — an external maintainer ([`agent-inspect`](https://github.com/rajudandigam/agent-inspect), 519★) asked for candid feedback on his own tool; a real gap surfaced (a healthy crash-resilience session read as almost entirely failed), a correction went both ways (he caught a real error in my own repro command), and the fix shipped as `--preset behavioral-session` with my session merged in as an attributed fixture — [PR #403](https://github.com/rajudandigam/agent-inspect/pull/403), reverified against current `main` with zero drift before calling it done.

## Featured: Agent Outcome Trust Score (AOTS)

Grounded in a real 2026 finding: half of enterprises have shipped an agent/LLM feature that passed internal evaluation and still caused a customer-facing failure, and only 5% fully trust their own automated evals (VentureBeat, June 2026 VB Pulse survey) — evaluations don't measure what a business stakeholder actually needs to trust. The existing MCP trilogy above scores whether a *server* is well-built; this scores whether a deployed *agent's* real behavior is something a non-engineer should trust.

1. [**PRD**](prds/2026-09-agent-outcome-trust-score.md) — the problem, sourced from VentureBeat's 2026 enterprise agent-evaluation-gap reporting, and why business-relevant criteria (task success, graceful escalation, auditability, consistency, cost) are a different question than protocol compliance.
2. [**Prototype**](prototypes/agent-outcome-trust-score/) — a real reference-agent run: this session driving [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) (42.7k★, already in this portfolio via mcp-fuzz) against the actual `mcp-doctor` codebase, live, one tool call at a time — not a scripted fixed path.
3. [**Case study**](case-studies/2026-09-agent-outcome-trust-score.md) — 5/5 tasks reached a correct, independently-verified answer; every first-attempt failure traced to CLI/JSON interface friction, never a reasoning error; two scoring gaps (full consistency re-run, cost-per-task) disclosed directly rather than smoothed over.

## Also: Ticket Triage Assistant (practice arc)

A complete PRD → prototype → case-study arc used to establish the working method, marked as sample/practice work rather than a real project:

- [PRD](prds/2026-08-support-ticket-triage-assistant.md) · [Prototype](prototypes/ticket-triage-rag/) · [Case study](case-studies/2026-08-support-ticket-triage-assistant.md)

Its prototype's baseline **failed** its own launch bar (60% vs. a 90% target) — kept in the repo on purpose, because a real eval that catches a real failure is more credible than a demo tuned to always look good.

## Status

More PRDs, prototypes, and case studies added as real projects come in.

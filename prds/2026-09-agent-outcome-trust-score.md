# PRD: Agent Outcome Trust Score (AOTS)

**Author:** Vishal Habib | **Date:** 2026-09-10 | **Status:** Draft

## 1. Problem

Enterprises have an evaluation gap, not a coverage gap. Half of enterprises have deployed an AI agent or LLM feature that passed internal evaluation and still caused a customer-facing failure — one in four more than once.[^1] The most-cited weakness isn't missing tests, it's that evaluations don't align with real-world outcomes: only 5% of enterprises say they fully trust the automated evaluations that gate their own release decisions.[^1]

The autonomy-trust mismatch is already load-bearing: 66% of organizations already permit some production agent deployment without human review, or are actively building toward it within 12 months — on evaluation signal that even they don't fully trust.[^2] The business outcome shows it: only 23% of organizations see significant ROI from AI agents, and Gartner projects over 40% of agentic AI projects will be cancelled by 2027, largely from unclear value rather than model capability.[^1]

The existing MCP quality-assurance trilogy in this portfolio (mcp-doctor, mcp-fuzz, mcp-reality-check) answers a narrower, protocol-level question: is the *server* an agent calls well-built — documented, crash-safe, correct on realistic input. None of that tells a business stakeholder whether the *agent itself*, running end-to-end against a real task, behaves in a way they'd actually trust in production. That's the specific, unaddressed layer: **no standard, evidence-backed way to score whether a deployed agent's real behavior — not its pass rate on a benchmark — is something a non-engineer stakeholder should trust.**

## 2. Users & use cases

- **AI Product Manager / agent platform owner** (primary): needs a defensible answer to "is this agent ready for production" that isn't just "the test suite is green" — something they can show a business or risk stakeholder.
- **Risk/compliance-adjacent stakeholders** in regulated contexts (financial services, healthcare): care less about task success in isolation and more about *how* an agent fails — does it escalate honestly, or does it fail silently/confidently.

Top scenarios:
1. Before greenlighting a production rollout, a PM runs AOTS against a candidate agent on a fixed set of realistic tasks and gets a scorecard with evidence attached to every score — not a single "8/10," but the actual transcripts showing where and how it failed.
2. An agent already in production gets re-scored after a prompt/tool change, and the scorecard is the artifact that answers "did this change make it more or less trustworthy" with evidence, rather than a subjective judgment call.

## 3. Solution approach

Not a benchmark of model capability, and not a rescoring of MCP protocol compliance (the existing trilogy already owns that layer) — an **evidence-first scorecard for a specific agent's end-to-end behavior on realistic tasks**, evaluated against criteria a business stakeholder actually cares about:

- **Task success rate** on realistic, non-trivial scenarios (not toy prompts) — did the agent actually accomplish the job.
- **Graceful escalation** — when a request is out of scope or the agent is uncertain, does it say so or hand off, instead of producing a confident, wrong answer.
- **Auditability** — can a non-engineer reviewer look at a failure and understand why it happened, from the artifact alone.
- **Consistency** — does the same scenario produce the same class of outcome across repeated runs, or is behavior unpredictable run to run.
- **Cost per resolved task** — as a plain efficiency signal alongside the trust-oriented ones above.

Every score is backed by a real, re-runnable transcript — same evidence-first discipline as the rest of this portfolio's tools — not a rubric filled in by inspection. **v1 deliberately scores one reference agent** (built on top of `codebase-memory-mcp`, already dogfooded via mcp-fuzz elsewhere in this portfolio) rather than a generic multi-agent benchmark suite, so the first version is a real, defensible case study instead of a thin pass across many shallow ones.

## 4. Success metrics

- **Primary**: for the reference agent scored in v1, every dimension's score is backed by a specific, inspectable transcript that a non-engineer reviewer can independently verify leads to the stated score — the deliverable is credibility of the scorecard itself, not a headline number.
- **Secondary**: at least one real, previously-unknown failure mode found and disclosed in the reference agent's behavior (matching this portfolio's existing pattern of disclosed, not hidden, failures).
- **Guardrail**: the scorecard must not produce a materially different verdict on a re-run of the same fixed task set — if scores swing run to run, that's a finding about the scorecard's own reliability, not something to paper over.

## 5. Evaluation plan

- **Fixed, versioned task set**: the scenarios scored against are fixed and published alongside the results, so the score is reproducible and comparable across future re-scoring runs, not re-sampled fresh each time (the same reproducibility discipline ACRS already established).
- **Validation before calling v1 done**: re-run the full task set at least twice and confirm the consistency dimension itself is stable — this is an eval of the eval, same as ACRS's own validation step.
- **Documented failures, not just successes**: same standard as every other artifact in this portfolio — if the reference agent fails a scenario, or the scorecard itself misjudges one, that gets written up, not smoothed over.

## 6. Risks & scope cuts

- **Risk: this is inherently more subjective than protocol-compliance scoring.** A crash is unambiguous; "graceful escalation" requires judgment. Mitigation: every score ships with its transcript, so a reader can disagree with the verdict using the same evidence rather than taking the grade on faith — the same discipline that makes the transcript, not the number, the actual deliverable.
- **Risk: overclaiming what a one-agent case study proves.** Mitigation: v1 is explicitly framed as a single, deep, defensible case study, not a general-purpose leaderboard — no claim that this generalizes to other agents until more are scored.
- **Out of scope for v1**: scoring multiple agents/frameworks (single reference agent only), live/continuous production monitoring (point-in-time assessment, same framing ACRS used), and any proprietary employer data or systems — the reference agent and every scenario are built and run on public, open-source components only.

---

[^1]: VentureBeat, "Enterprise AI is entering an evaluation gap: Agents are gaining autonomy faster than companies can verify them" (June 2026 VB Pulse survey, 157 enterprise respondents)
[^2]: VentureBeat, "The agent evaluation gap: Enterprise AI organizations have a reality-alignment problem, not a coverage problem — and most are shipping to production anyway"

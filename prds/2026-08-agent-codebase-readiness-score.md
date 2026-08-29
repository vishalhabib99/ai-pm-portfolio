# PRD: Agent Codebase Readiness Score (ACRS)

**Author:** Vishal Habib | **Date:** 2026-08-29 | **Status:** Draft

## 1. Problem

Across the industry, agentic AI adoption has a severe pilot-to-production collapse: 79% of enterprises have adopted AI agents in some form, but only 11% run them in production — a 68-point gap.[^1] Gartner projects over 40% of agentic AI projects will be cancelled by end of 2027, usually from unclear value, uncontrolled cost, and inadequate risk controls.[^1]

For coding agents specifically, the root cause is measurable and specific: every major coding agent performs significantly worse on existing, real-world codebases than on greenfield projects or benchmark demos.[^2] Public benchmarks like SWE-bench Verified now show 70-90%+ success rates,[^2] but those numbers are earned on curated tasks — not on a given company's actual 8-year-old monorepo with undocumented conventions, legacy patterns, and inconsistent test coverage. Teams currently have no way to know how an agent will actually perform on *their* codebase until after they've already rolled it out broadly, by which point token costs have often run 2x the original estimate.[^2] That's the moment agent sprawl and unclear ROI set in, and the project gets quietly cancelled or shelved.[^1]

The problem isn't "are agents good enough" — the benchmarks say yes. The problem is **no standard way to predict agent fit on a specific real codebase before committing budget and rollout scope to it.**

## 2. Users & use cases

- **Engineering leadership / platform teams** (primary): evaluating which coding agent(s) to standardize on, and where in the codebase it's safe to let agents work autonomously vs. require heavy review.
- **AI Product Manager / agent platform owner**: needs a defensible way to answer "will this work here" before committing rollout budget, and a way to track readiness improving over time as the codebase is made more agent-friendly.

Top scenarios:
1. Before a broader rollout, a platform team runs ACRS against 2-3 candidate agents on their actual repo(s) and gets a readiness score per repo area, not just an aggregate — so they know to start agents on the well-tested `services/api` module and keep humans in the loop on the undocumented `legacy/billing` module.
2. Ongoing: readiness score is tracked over time as a health metric, and improving it (better docs, better test coverage, more consistent patterns) becomes a legible, prioritizable engineering investment rather than a vague "make the codebase more AI-friendly" ask.

## 3. Solution approach

Not a new coding agent — an **evaluation layer that sits in front of any agent** and produces a repo-specific readiness score before rollout decisions get made.

- **Sampling, not full coverage**: pull a stratified sample of real historical tickets/PRs from the target repo (bug fixes, small features, refactors) as the task set — this is what makes the eval about *this* codebase instead of a generic benchmark.
- **Per-module scoring, not one number**: score readiness separately per directory/module, since agent performance varies hugely by area (well-tested vs. undocumented code) — a single aggregate score hides exactly the information a rollout decision needs.
- **Score along the dimensions that actually predict production failure**, based on what the field currently treats as the real evaluation axes for coding agents: task success rate, token/cost efficiency, code quality of the diff (not just "tests pass"), and context understanding on this specific codebase vs. a generic benchmark.[^2]
- **Deliberately excludes** building a new agent or a new benchmark suite from scratch — this wraps and scores *existing* agents (Claude Code, Copilot, Cursor, etc.) against a company's own repo, since the differentiation is in the "your codebase, not a demo" framing, not in agent capability itself.

## 4. Success metrics

- **Primary**: for teams that use ACRS before rollout, pilot-to-production conversion rate (does the agent initiative actually reach sustained production use, not get quietly cancelled) vs. the industry baseline of ~11%.[^1]
- **Secondary**: variance between ACRS-predicted cost and actual observed token cost post-rollout — target within 20%, directly targeting the "2x cost overrun" failure mode.[^2]
- **Guardrail**: no increase in production incident rate attributable to agent-authored changes in modules ACRS scored as "high readiness" (validates the score is actually predictive, not just reassuring).

## 5. Evaluation plan

- **Validation before general release**: run ACRS against 5-10 pilot codebases with known outcomes (some successful agent rollouts, some failed/cancelled ones) and check the score correctly ranks them — this is an eval of the eval, and it's the part that actually proves the product works.
- **Per-dimension calibration**: for each scoring dimension (task success, cost, code quality, context understanding), validate against held-out historical PRs where the actual outcome (merged clean / needed rework / reverted) is known.
- **Ongoing**: track the primary success metric (pilot-to-production conversion) across all customers using the tool, since that's the actual claim being made.

## 6. Risks & scope cuts

- **Risk**: a high readiness score creates false confidence and teams skip review on "safe" modules. Mitigation: score is explicitly framed as a rollout-planning input, not a certification — and the guardrail metric above exists specifically to catch this failure mode if it happens.
- **Risk**: readiness scoring itself becomes another expensive, hard-to-trust agentic evaluation layer (the same non-determinism problem it's trying to solve for).[^1] Mitigation: keep the scoring task set fixed and versioned per run so results are reproducible and comparable over time, not re-sampled fresh each time.
- **Out of scope for v1**: scoring non-coding agentic workflows (this is coding-agent-specific), building the underlying coding agents themselves, real-time/continuous scoring (v1 is a point-in-time assessment before rollout decisions, not a live dashboard).

---

[^1]: IBM, "The Biggest AI Adoption Challenges for 2026"; MachineLearningMastery, "5 Production Scaling Challenges for Agentic AI in 2026"; Lyzr, "The Honest Truth About Enterprise AI Agents"; Arcade.dev, "State of AI Agents 2026: 5 Enterprise Trends"
[^2]: MorphLLM, "Best AI Coding Agents (August 2026): Scored Leaderboard"; Webfuse, "Agentic Coding in 2026: Tools, Benchmarks and Limits"

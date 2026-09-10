# Case Study: Agent Outcome Trust Score — v1 Prototype

**Date:** 2026-09-10

## What shipped

A working v1 scorecard (`prototypes/agent-outcome-trust-score/`) proving the [AOTS PRD](../prds/2026-09-agent-outcome-trust-score.md)'s core claim: agent behavior can be scored on business-relevant dimensions — task success, graceful escalation, auditability, consistency, cost — with every score backed by a real, re-runnable transcript instead of a rubric filled in by inspection.

Run for real, not simulated: this session acted as the reference agent, driving [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) (a real 42.7k★ MCP server, already dogfooded elsewhere in this portfolio via mcp-fuzz) against the actual `mcp-doctor` codebase at commit `f1f52a3`, across 5 realistic developer tasks — one tool call at a time, deciding the next step from the live response, not a pre-scripted path.

## Key decisions & tradeoffs

- **Reused an already-warm relationship instead of starting cold.** `codebase-memory-mcp` already has two real maintainer replies and a filed finding elsewhere in this portfolio (`codebase-memory-mcp#2118`) — scoring an agent built on top of it compounds with existing credibility instead of introducing a fourth unrelated tool.
- **The agent was this session itself, not a separately scripted LLM loop.** That was the only agent-building path available without a configured API key for an independent script. It's a legitimate, real agentic trace (live tool calls, live decisions, no editing after the fact) — but it means the "cost per resolved task" dimension has no clean token/dollar log, which is disclosed as a gap rather than estimated or faked.
- **Verified every tool answer against the real source before scoring it correct.** Same discipline as every other tool in this portfolio: `grep`/direct-read ground truth for every factual claim (the masking helper's single call site, the CLI-to-check call chain, the zero-dead-code result), not trust in the tool's own output.

## What broke / what didn't work

Every one of the 5 tasks's initial failures was interface friction, not reasoning failure — and all three followed the same underlying shape: **the tool's two input surfaces (CLI `--help` text vs. the JSON args it actually accepts) disagree with each other.**

1. `search_code` rejected `"query"` — the actual field is `"pattern"`.
2. `trace_path`'s help text shows a hyphenated `--function-name` flag; the JSON body requires snake_case `function_name`. Its `direction` argument documents no enum in `--help` at all — `"callers"` fails with an error message that then reveals the real values (`inbound`/`outbound`/`both`).
3. `query_graph`'s Cypher subset rejects a negated relationship pattern (`NOT (()-[:CALLS]->(f))`) with a bare parser position error (`expected token type 67, got 70`) — no hint that the fix is rewriting it as an `OPTIONAL MATCH ... WHERE count(...) = 0`.

Each failure was loud, specific, and recoverable on the very next attempt — never a silent wrong answer. That's the actual finding this scorecard exists to produce: not "does the tool work" (it does, and every eventual answer was verified correct), but "when an agent gets it wrong, does it fail in a way the agent — or its human reviewer — can actually see and fix." Here, every failure did.

## Outcome

**5/5 tasks reached a correct, independently-verified answer** (search, call-chain trace, blast-radius impact analysis, an escalation test, and a dead-code check), 3 of the 5 needed exactly one retry, all from the same class of CLI/JSON schema mismatch documented above. The escalation test (asking for a CVE the tool has no way of knowing) returned a clean empty result rather than a fabricated one — the tool stayed honest; the judgment call of *treating* "no data" as "cannot answer, not confirmed absent" is squarely the agent-behavior finding AOTS is built to isolate from tool-behavior.

**Two honest gaps, not smoothed over**: consistency was only checked by re-running 2 of the 5 tasks (both came back byte-identical); the other 3 weren't re-run this pass. Cost-per-task isn't measured at all in this v1, for the reason above. Both are named directly in the prototype's README as the next real increment — not claimed as done.

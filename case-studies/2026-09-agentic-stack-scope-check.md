# Case Study: Checking Before Building a Fourth Tool

**Date:** 2026-09-17

## What this is

The ambition after shipping the MCP trilogy ([mcp-doctor](https://github.com/vishalhabib99/mcp-doctor), [mcp-fuzz](https://github.com/vishalhabib99/mcp-fuzz), [mcp-reality-check](https://github.com/vishalhabib99/mcp-reality-check), combined in [mcp-trust-check](https://github.com/vishalhabib99/mcp-trust-check)) was obvious: build out the *complete* agentic AI stack — identity, multi-agent trust, human-handoff, the works. Before writing a line of code for any of it, each candidate area got checked against what actually exists in the market today, the same discipline already applied to every prior scope decision on this trilogy (declining a resources/prompts audit after checking real adoption across 8 servers, declining continuous monitoring as the wrong shape of software). This is what that check found, including a wrong recommendation caught and corrected in the same session it was made.

## The wrong recommendation, caught by looking

The first pick was agent identity and least-privilege auditing — a static check for whether an agent is configured with more tool access than it needs, a natural extension of mcp-doctor's own static-analysis shape. It was recommended directly, no hedging.

It was wrong. A search turned up a populated 2026 market: Okta and Cisco (Duo Agentic Identity, launched 2026) and JumpCloud all ship agent-identity products; FINOS's AI Governance Framework has a named least-privilege mitigation (MI-18); and an open-source static scanner, [`agent-audit`](https://github.com/HeadyZhang/agent-audit) (230★, MIT, actively pushed the same week this was checked), already does MCP config auditing for exactly this. The honest move was to say so plainly rather than let the recommendation stand.

## How much of agent-audit actually overlaps mcp-doctor

Rather than leave it at "this space is crowded," the two tools were compared line by line against their real READMEs, not assumption.

**Real overlap:** both flag prompt-injection/tool-poisoning language in tool descriptions. agent-audit's rule AGENT-054 ("MCP rug pull / drift: server tools change after initial security audit") is a sharper, named version of a threat mcp-doctor's leaderboard only weakly captures via scan-to-scan grade deltas. agent-audit is also more rigorously validated than mcp-doctor on this axis — it publishes precision/recall against a labeled ground-truth set (68.86% / 84.32%, F1 0.76 on 81 samples / 238 labels), something mcp-doctor's own README doesn't do.

**What still holds up:** mcp-doctor scores quality and security independently (doc/error-handling completeness is a first-class score); agent-audit is security-only. mcp-doctor supports Go; agent-audit's framework coverage (LangChain, CrewAI, AutoGen, AgentScope) is Python-only. agent-audit itself is purely static — its repo has no runtime component at all, confirmed by reading its actual file structure, not just its description. mcp-fuzz and mcp-reality-check do launch the server and watch what it actually does (crashes, stale-after-delete bugs, live schema-fidelity violations) — a real, still-standing distinction from agent-audit specifically.

## The other two candidates, checked the same way

Multi-agent trust verification (does agent A actually do what it told agent B it would) turned up AgentGraph, Red Hat's AgentTrust, an academic tool called Agentproof, and the Nerq Trust Protocol — all real, all 2026, all earlier-stage than the identity market but none of them an open gap. Human-handoff escalation calibration turned up heavy coverage from CX vendors and real research (Anthropic's self-escalation-rate findings, a January 2026 "Holistic Trajectory Calibration" method) but no concrete tooling gap shaped like the trilogy's audits.

## Correction: the first "nothing else does dynamic testing" claim was also too broad

The first draft of this case study claimed the trilogy's unclaimed edge was dynamic testing generally — "nothing found this session does that." Checked directly against Red Hat's own AgentTrust writeup before letting that stand, and it was wrong: AgentTrust does execute live agents at runtime, sending synthetic probes and cross-checking the results against real MLflow execution traces. It launches something and watches what happens, the same shape of claim mcp-fuzz and mcp-reality-check make.

The corrected, narrower claim is the one that actually survives: the trilogy's edge isn't "dynamic testing exists nowhere else," it's **deterministic, zero-API-cost dynamic testing of MCP servers specifically**. AgentTrust tests agents at the orchestration layer using an LLM judge — a real cost-and-determinism tradeoff the trilogy has deliberately avoided since mcp-reality-check's first design decision — and is an early-stage Red Hat research project ("next steps... open problems," per its own writeup), not a shipped, adopted tool. Cisco's Duo Agentic Identity, by contrast, checked out as fully real on independent verification — announced at RSA in March 2026, in beta since September — so not every claim in the first pass was wrong, just the broadest one.

## The decision

Three candidate expansions, three real markets already claimed by named, in some cases funded, competitors. Building thin versions of each just to claim "complete stack" coverage would trade the one thing that makes the trilogy credible — every number in it is real and verified — for repo count. The decision made instead: don't build a fourth through eighth tool. The trilogy's actual, narrower-than-first-claimed edge is deterministic, zero-cost dynamic testing of MCP servers — and depth there is worth more than breadth across layers where Okta, Cisco, and Red Hat are already building.

## Outcome, stated plainly

- Three candidate stack expansions checked against live 2026 market data before writing any code: agent identity/least-privilege, multi-agent trust verification, human-handoff calibration.
- Two recommendations made and found too broad on closer verification, both corrected in the same session, before any code was written and after this case study was already published once: the initial "agent identity is unclaimed" pick, and then this write-up's own first claim that no one else does dynamic testing.
- One direct competitor (`agent-audit`) analyzed against mcp-doctor feature-by-feature: two real overlap points acknowledged (tool poisoning, rug-pull/drift), two real differentiators confirmed still standing (dual quality/security scoring, Go support), plus a third (dynamic testing) narrowed to what's actually still true (deterministic, zero-cost, MCP-server-specific) rather than left overstated.
- Zero new tools built. The scope decision itself is the deliverable.

## Why this is the artifact

Anyone can list ambitions. The part worth showing a hiring manager is what happens when an ambition meets real market data: a confident first pick turned out to be wrong, got checked rather than defended, and the correction happened before any code shipped instead of after a launch nobody needed. That's the same standing rule this portfolio has applied since the first trilogy case study — verify before claiming, correct in public when wrong — applied one layer up, to the decision of what to build at all.

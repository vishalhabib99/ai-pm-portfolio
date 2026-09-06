# Case Study: Completing the Trilogy — and Catching My Own Bugs Twice Before They Shipped

**Date:** 2026-09-05 to 2026-09-06

## What this is

[mcp-doctor](https://github.com/vishalhabib99/mcp-doctor) reads an MCP server's source and never runs it — it checks whether tools are documented and free of obvious security smells. That's one axis of "is this a good MCP server." Two more axes were missing: does a tool fail safely when called wrong, and does it actually work when called right. This case study covers building both — [mcp-fuzz](https://github.com/vishalhabib99/mcp-fuzz) and [mcp-reality-check](https://github.com/vishalhabib99/mcp-reality-check) — and two separate incidents, one per tool, where dogfooding caught a real bug in the tool itself before it did damage. The bugs are the point of this writeup, not the feature list.

## Deciding what the third tool should be — and what it shouldn't cost

After mcp-fuzz shipped, the obvious next gap was clear from its own documented scope: it deliberately never judges whether a *successful* call's response is actually correct, because a schema-only placeholder input ("test") isn't realistic enough to fairly judge that. The natural fix is an LLM reading the response and judging it — which is also the expensive, non-deterministic fix. The constraint that mattered here wasn't technical, it was budget: staying inside an existing $20/month subscription, with zero separate API billing.

That constraint forced a better design, not a worse one. Instead of an LLM judge, mcp-reality-check does three things with plain, deterministic logic: generates a *realistic* input (a `city` property gets "Paris," not "test" — so a genuine answer has something concrete to reference), then checks the response for a refusal disguised as success (`isError: false` but the text is an apology — "I don't have access to..."), empty content on a claimed success, and a violation of the tool's own declared output schema. Zero API key, zero per-call cost, fully reproducible. The tradeoff, stated plainly in the tool's own README rather than hidden: a refusal phrased outside a fixed pattern list won't be caught. Real recall limit, in exchange for a real cost guarantee.

## Incident one: a fix that would have quietly retracted a real, already-published finding

mcp-fuzz's headline result was a genuine crash-resilience bug in Ant Design's official `mcp-server-chart` (4.3k★, [filed upstream](https://github.com/antvis/mcp-server-chart/issues/323)) — already cited in a public LinkedIn post by the time this happened. Dogfooding a second server, `firecrawl-mcp-server`, surfaced a real bug in mcp-fuzz itself: the target validates arguments with zod and has the SDK raise a structured JSON-RPC error for bad input — the *correct* behavior — but mcp-fuzz's exception handling treated that identically to a real crash. A false 0%/F score on a server that was actually working.

The first fix attempt was too broad: it classified almost any such error as "handled gracefully." Before shipping it, the same fix was re-tested against the already-published `mcp-server-chart` finding — and it silently flipped that real result to a false 100%/A. The over-correction would have quietly erased a finding already sitting in public, cited by name, with nobody the wiser unless someone happened to re-run it. Caught only because re-verifying a fix against every real repo it could touch — including the ones already cited publicly — is a standing rule for this whole line of work, not a one-off gut check.

The real fix required distinguishing two error codes that look identical at the exception-handling level: one meaning "the server validated your input and rejected it" (not a crash), the other meaning "the server's own code crashed internally and a framework caught it before the whole process died" (still a crash, in the sense that matters — the tool didn't behave the way its schema claimed). Re-verified afterward: the firecrawl false-positive was gone, and the original Ant Design finding was back at its exact original numbers, unchanged. No correction ever had to be posted, because the mistake never left the building.

## Incident two: the newest tool's first dogfood bug was in itself, again

mcp-reality-check's own first real bug followed the identical shape, on its very first extended dogfood round. Testing it against the official `mcp-server-time` server, every single call failed — not because the target was broken, but because the tool's own input generator had no hint for a `timezone` property at all, so it fell back to a placeholder string that isn't a real timezone name. Zero of two calls were even checkable.

The fix was small (map `timezone` properties to a real IANA name like `America/New_York`), but the pattern repeating is the actual finding: both new tools' first meaningful dogfood pass surfaced a bug in the tool itself, not the target, in the exact same category — a piece of realistic-input generation the tool's own build-and-unit-test cycle hadn't exercised, that only showed up against a real, unpredictable server. Static tests pass; a real server disagrees. That gap is why every tool in this line gets pointed at real, popular, previously-untested repos before its numbers are trusted, not just its own fixtures.

## What was correctly left alone

Two dogfood results during this stretch looked like bugs and weren't: `mcp-server-git` rejected every realistic call because it's configured against one fixed repository path that no JSON schema can signal, and `qdrant`'s embedded local-storage mode hit a known client-library limitation already found independently through mcp-fuzz. Both are documented in mcp-reality-check's README as a named class of limitation — a schema-only generator can't know about server-side configuration state — rather than chased with a workaround that wouldn't generalize to the next server.

## Outcome, stated plainly

- **Two more tools shipped and published**: `pip install mcp-runtime-check` (mcp-fuzz) and `pip install mcp-reality-check`, joining `pip install mcp-server-lint` (mcp-doctor) — three independent PyPI packages, three GitHub repos, all pinned and cross-linked from each other's READMEs.
- **28+ real dogfood passes across the two new tools** (17+ for mcp-fuzz, 11 for mcp-reality-check) against real, popular, previously-untested MCP servers — official Google, GitHub, Ant Design, and Anthropic reference servers among them.
- **Two real bugs found in the tools' own code**, both via dogfooding rather than unit tests, both fixed and covered by new regression tests before shipping.
- **One near-miss caught before it caused real damage**: an over-broad fix that would have silently invalidated an already-public, already-cited finding — caught by treating "re-verify against everything this could affect" as a non-negotiable step, not an afterthought.
- **Zero incorrect public claims shipped**: the Ant Design finding never needed a correction; nothing was ever cited that later turned out false.

## Why this is the artifact

Anyone can build a tool that works on its own test suite. The repeatable, verifiable part here is what happened when each new tool was pointed at reality instead: it broke on something the fixtures never exercised, both times, and the discipline of re-checking every claim already made public — not just the new one — is what kept a real mistake from ever reaching anyone else.

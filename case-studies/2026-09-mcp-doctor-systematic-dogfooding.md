# Case Study: Turning a One-Off Bug Hunt Into a Repeatable QA Process

**Date:** 2026-08-30 to 2026-09-03

## What this is

The [first mcp-doctor case study](2026-08-mcp-doctor-oss-contribution.md) is about one arc: a single finding, two rounds of being told I was wrong, and a merged PR. This one is about what happened after — turning that one-off into a repeatable process (pick a real, popular, untested MCP server; run mcp-doctor against it; verify every finding by hand against the actual source; fix what's genuinely broken; ship it) and running it against 20+ real production servers, up to 50k stars, across three languages. The interesting part for a PM audience isn't the bug count. It's the two judgment calls that repeat every single pass: *is this a real gap or a false alarm*, and *is this worth building support for, or should I say no*.

## The methodology, in practice

Every pass follows the same discipline, and it's the discipline — not any individual fix — that's the actual product decision being tested:

1. Pick a real, active, previously-untested MCP server, sorted by stars within its language.
2. Run mcp-doctor against it as-is. A wrong or missing result becomes a specific, falsifiable claim about the tool, not a vague "seems fine."
3. Before touching any code, read the actual source at the flagged location — never trust the tool's own output as ground truth about itself.
4. Fix only what's a genuinely verified gap. Add a regression test that would have caught it.
5. Re-run against every previously-audited repo that exercises the same code path, to catch a fix that quietly breaks something else.
6. Ship it — commit, push, confirm CI green, cut a release, confirm the new version is actually live on PyPI. Not "should work" — checked.

By 2026-09-03 this had run 20+ times against real servers up to 50k stars (Python, TypeScript, and Go), surfacing 20 genuine bugs — most of them in mcp-doctor itself, a few in the target repos.

## The anchor story: GitHub's own official server was invisible

The starkest single result: [`github/github-mcp-server`](https://github.com/github/github-mcp-server) — GitHub's own official, actively-maintained MCP server, 32,600 stars — reported **0 of 114+ tools found**. Not because the server was broken. Because it builds every tool through its own internal generic factory function (a `NewTool(toolset, mcp.Tool{...}, scopeAccess, handler)` wrapper) instead of calling the SDK's registration function directly at each definition site — a real, sensible engineering choice on GitHub's part for sharing cross-cutting concerns like auth and dependency injection, and one mcp-doctor's detection logic had never accounted for because every server audited up to that point called the SDK directly.

Generalizing the fix wasn't about GitHub's specific function name — it was recognizing that *any* call passing the SDK's tool-definition object, regardless of what the wrapping function is called, should count. Two smaller, related gaps came out of verifying the fix against the same repo: a dependency-injecting handler signature the analyzer assumed couldn't exist, and descriptions built through an i18n helper (`t(key, fallback)`) rather than plain string literals. All three shipped in one release, verified end to end: 0 → 114 tools found, cross-checked against the previous two audited Go servers to confirm nothing regressed.

## The other kind of finding: correctly deciding not to build something

The same day, two other real, popular servers ([`antvis/mcp-server-chart`](https://github.com/antvis/mcp-server-chart) and [`apify/apify-mcp-server`](https://github.com/apify/apify-mcp-server)) also reported 0 tools. Tracing the actual resolution chain on the chart server revealed why: its tool list is built by calling a local helper function, whose body conditionally returns the result of `Object.values()` over a namespace-imported barrel file, filtered at runtime. Resolving that statically would require three new capabilities mcp-doctor doesn't have — inlining a function call to its return value, resolving a conditional expression, and resolving an entire barrel-file's re-exports — for a payoff that, so far, is specific to one repo's particular code-organization style.

The decision was to not build it. Not because it's unfixable, but because the estimated cost (a multi-capability feature, each with its own edge cases and regression risk) didn't clear the bar against the actual, current evidence of how common the pattern is. Two similarly dynamic servers audited the same day — [`googleapis/mcp-toolbox`](https://github.com/googleapis/mcp-toolbox) (tools defined in a user-supplied YAML config) and [`bytebase/dbhub`](https://github.com/bytebase/dbhub) (tool names derived from runtime-configured database connections) — were correctly left as documented limitations for the same reason: a real architecture the tool can't safely guess at, not a bug to force a heuristic onto.

Saying no to work that would ship a fragile, one-off capability is the same discipline as the ha-mcp case study's "don't manufacture a finding just because an opening was offered" — just applied to build decisions instead of bug reports.

## Outcome, stated plainly

- **20+ real MCP servers dogfooded**, up to 50,000 stars, across Python, TypeScript, and Go — including a second official-vendor server (`googleapis/mcp-toolbox`) beyond GitHub's own.
- **20 genuine bugs found and fixed**, each verified against real source before and after, each backed by a regression test.
- **4 releases shipped in a single day** during this stretch (v1.4.0–v1.4.3): a new security-scoring axis, Go factory-wrapper support, Python class-based tool registries, and a TS test-file exclusion fix — every one confirmed live on PyPI, not just merged to `main`.
- **A real non-self adoption signal**: `mcp-server-lint` on PyPI jumped from a ~249/week baseline to 734 downloads in a single day — not yet confirmed to hold, and not overstated here for that reason.
- **Two correctly-declined feature requests** (the barrel-file case, the YAML/runtime-config cases), documented as known limitations rather than either ignored or forced.

## Why this is the artifact

Anyone can point a linter at one repo and get lucky. The repeatable part — the same six-step discipline run 20+ times, catching real regressions before they ship, and saying no to building something when the evidence doesn't support it yet — is the actual product judgment on display. The GitHub find is credible because of the process that found it, not the other way around.

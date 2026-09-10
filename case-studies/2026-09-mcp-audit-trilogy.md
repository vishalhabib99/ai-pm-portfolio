# Case Study: Three Tools, Three Axes, Two Real Bugs Caught Before They Shipped

**Date:** 2026-08-30 to 2026-09-06

## What this is

One MCP server can be broken in three independent ways: undocumented or unsafe on paper, crash-prone when called wrong, or silently wrong when called right. No single check covers all three, so this became three separate open-source tools — [mcp-doctor](https://github.com/vishalhabib99/mcp-doctor), [mcp-fuzz](https://github.com/vishalhabib99/mcp-fuzz), and [mcp-reality-check](https://github.com/vishalhabib99/mcp-reality-check) — built over about a week, each pointed at real, popular, previously-untested servers instead of toy fixtures. All three caught a real bug in themselves this way, and one of those bugs almost caused a public correction that never should have been necessary. This is that story, one incident per tool.

## mcp-doctor: static analysis — is it documented and safe on paper

mcp-doctor reads a server's source and never runs it: spec conformance, doc coverage, secret scanning, error-handling quality. Pointed at [`homeassistant-ai/ha-mcp`](https://github.com/homeassistant-ai/ha-mcp) (4.6k★, actively maintained), it flagged 88 undocumented tool parameters. Before that number even got a maintainer reply, a self-check found the real number was 24, not 88 — mcp-doctor only recognized docstring `Args:` blocks, not the `Annotated[T, Field(description=...)]` style the repo actually used. Posted the correction publicly rather than let the wrong number stand.

The maintainer then closed the issue anyway, with a sharper correction: mcp-doctor's error-handling check claimed a missing `try/except` could leak a raw stack trace through the transport — a security-flavored claim, and a false one. Verified directly against FastMCP's own source: it catches every tool exception at the framework level, always returns a structured error. The maintainer was right. Rewrote the check to describe the real, smaller issue instead of defending the wrong one.

He left an opening — invited a new issue if it followed the current MCP spec. Read the spec end-to-end looking for a real gap rather than inventing one to fill the invitation; found one (tool-name character/length rules), checked it against ha-mcp's actual 88 tool names, and found all of them already compliant — nothing to file. Declined to open a second issue just to use the opening.

The eventual PR — 6 missing parameter descriptions — came back `CHANGES_REQUESTED` too: three claims in the first draft were wrong about the code's actual gating logic (an inverted required/rejected condition, a nonexistent single-entity gate, an undocumented multi-target input form). Fixed all three against the real source, not the reviewer's summary. [Merged](https://github.com/homeassistant-ai/ha-mcp/pull/2327) 2026-09-01 into a 4.6k-star production repo. Net: four real bugs found in mcp-doctor's own logic, all via a maintainer's pushback, none via unit tests.

## mcp-fuzz: runtime fuzzing — does it fail safely when called wrong

mcp-fuzz launches a server for real and calls every tool with schema-derived bad input — missing required fields, wrong types — to see whether it fails cleanly or crashes. Its headline finding: Ant Design's official `mcp-server-chart` (4.3k★) crashed on 133 of 214 realistic bad-input calls, a 37.85% crash-resilience score, [filed upstream](https://github.com/antvis/mcp-server-chart/issues/323) and already cited by name in a public LinkedIn post.

Dogfooding a second server surfaced a real bug in mcp-fuzz itself: a target that validated input correctly and raised a structured JSON-RPC error — the *right* behavior — was being scored identically to an actual crash. A false 0%/F on a server that was actually working. The first fix attempt was too broad, classifying nearly any structured error as "handled gracefully." Before shipping it, the fix was re-run against every already-published finding, including the Ant Design one — and it silently flipped that real, already-cited result to a false 100%/A. The over-correction would have quietly retracted a public claim with nobody the wiser unless someone happened to re-run it by hand. The real fix required distinguishing two error shapes that look identical at the exception-handling layer: "rejected your input" versus "crashed and a framework caught it." Re-verified afterward: the false positive was gone, and the original Ant Design number was back exactly where it started, unchanged. No correction was ever needed publicly, because the mistake never left the building.

## mcp-reality-check: output verification — is a successful response actually true

mcp-doctor never runs the server; mcp-fuzz runs it but only checks *whether* it failed, not whether a claimed success is real. mcp-reality-check closes that gap deterministically — no LLM judge, zero API cost — by generating a realistic input (a `city` property gets "Paris," not a placeholder) and checking the response for a refusal disguised as success, empty content on a claimed success, or a violation of the tool's own declared schema.

Its first extended dogfood pass, against the official `mcp-server-time` server, found every call failing — not because the server was broken, but because mcp-reality-check's own input generator had no case for a `timezone` property and fell back to a placeholder string that isn't a real timezone. Zero of two calls were even checkable. Small fix (map `timezone` to a real IANA name), but the pattern is the actual finding: the newest tool's very first real-world pass hit the identical failure class as mcp-fuzz's — a gap in the tool's own input realism that no amount of self-testing had exercised, only a real, unpredictable server did.

## The repeating shape

Three tools, three different jobs, and the same failure mode found itself three times: each one's confident self-test suite missed something a real, unpredictable target immediately exposed. What changed the outcome each time wasn't avoiding the bug — it was the standing rule that every fix gets re-verified against everything already claimed publicly before it ships, not just the case that motivated it. That rule is the only reason the Ant Design finding is still accurate today, and the only reason mcp-doctor's ha-mcp claims got corrected twice in public instead of once quietly.

## Outcome, stated plainly

- Three independent PyPI packages — `mcp-server-lint`, `mcp-runtime-check`, `mcp-reality-check` — three GitHub repos, cross-linked, all MIT.
- One real fix merged into a 4.6k-star production repo (ha-mcp), four real bugs fixed in mcp-doctor's own logic along the way.
- One genuine crash-resilience finding on a 4.3k-star official repo (Ant Design), filed upstream, still accurate.
- One near-miss caught before it reached anyone: a fix that would have silently retracted that same finding, caught only by re-checking every public claim before shipping.
- One repeating pattern named honestly rather than treated as a coincidence: both newer tools' first real dogfood pass found the bug in themselves, not the target.

## Why this is the artifact

Anyone can ship a tool that passes its own test suite. The part worth showing a hiring manager is what happened at the boundary with reality each time — a maintainer's correction, an unpredictable third-party server, an already-public claim on the line — and what held: verify before claiming, correct in public when wrong, and never let a fix ship without checking it against everything that's already been said.

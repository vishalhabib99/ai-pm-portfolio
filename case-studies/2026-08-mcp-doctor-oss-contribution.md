# Case Study: mcp-doctor — Finding, Defending, and Fixing a Real Bug in Someone Else's Production Repo

**Date:** 2026-08-30 to 2026-09-01

## What this is

Not a PRD-first exercise like [ACRS](2026-08-agent-codebase-readiness-score.md) — this is what happened when [mcp-doctor](https://github.com/vishalhabib99/mcp-doctor) (a static-analysis CLI I built that audits MCP server implementations for spec conformance and quality) got pointed at a real, actively-maintained open-source project instead of a fixture. The interesting part isn't the tool. It's what happened after I published a finding and the maintainer told me I was wrong — twice — and how that changed both the tool and the finding.

## The setup

I ran mcp-doctor against [`homeassistant-ai/ha-mcp`](https://github.com/homeassistant-ai/ha-mcp) (4.6k stars, active, well-run — not a toy repo picked to look good). It flagged two real defects in mcp-doctor itself before I trusted any of its output on ha-mcp: the secret scanner was matching test fixtures and identifier-style constants as hardcoded credentials, and tool-detection was counting `@mcp.tool()`-decorated mocks inside test files as production tools. Fixed both, verified the corrected score (55%/F → 89%/B on ha-mcp), then filed [issue #2324](https://github.com/homeassistant-ai/ha-mcp/issues/2324): 88 tools missing per-parameter documentation.

## Where it went wrong the first time

Before the issue even got a maintainer response, I found my own mistake while preparing an example fix: mcp-doctor only recognized docstring `Args:` sections as documentation, not the `Annotated[T, Field(description=...)]` style ha-mcp actually uses for most of its parameters. The real number wasn't 88 — it was 24. I fixed the detection and **posted a public correction on my own issue** rather than let the wrong number stand: [issue comment](https://github.com/homeassistant-ai/ha-mcp/issues/2324#issuecomment-5470898934).

## Where it went wrong the second time — and it was worse

The maintainer (`kingpanther13`) then closed #2324 as **not planned**, with a rebuttal that had two parts:

1. Even 24/88 was still overstated — his own AST walk found 89% of params already documented once type-alias `Field` descriptions and non-`Args:` markdown headings were counted, both of which mcp-doctor still missed.
2. The serious one: mcp-doctor's error-handling check claimed a missing `try/except` would let a raw traceback leak through the MCP transport. That's a security-flavored claim, and it was false — I verified it directly against FastMCP's own source (`PrefectHQ/fastmcp`, `server.py`'s `call_tool`), which catches every tool exception at the framework level and always returns a structured error. The maintainer was right; I hadn't checked the framework guarantee before shipping the check.

I rewrote the check to describe the real, smaller issue (generic vs. actionable error messages, not a transport-safety claim) and posted a second follow-up acknowledging the correction: [issue comment](https://github.com/homeassistant-ai/ha-mcp/issues/2324#issuecomment-5470951856). No attempt to defend the original wording once the framework source proved it wrong.

## What kept the story alive: acting on an invitation without manufacturing a finding

`kingpanther13` closed the issue but left an opening: *"If you want to open a new issue that follows fastmcp and the July 2026 MCP protocol guidelines I'll leave that one open."* I read the current MCP spec end-to-end looking for a real gap rather than inventing one to fill the invitation. Found one concrete, checkable miss — the normative Tool Names rule (1–128 chars, restricted charset, unique per server) — and added it to mcp-doctor. Checked it against ha-mcp's actual 88 tool names before claiming anything: all already compliant, nothing to file. **Correctly did not open a second issue just to use the opening** — a manufactured finding here would have repeated the exact mistake already made twice in the same week.

## The PR, and a second round of being wrong

Opened [PR #2327](https://github.com/homeassistant-ai/ha-mcp/pull/2327): added the missing `Field(description=...)` text for `ha_call_service`'s 6 undocumented params. Got `CHANGES_REQUESTED`, not a rubber stamp — the maintainer's review caught real inaccuracies in the *wording itself*, not just process nits:

| Claim in my first draft | What the code actually does |
|---|---|
| "domain/service required unless ws_command" | They're **rejected**, not optional, when `ws_command` is set — the logic was inverted |
| "wait only applies to a single entity" | No such gate exists; the real issue is a multi-target footgun — comma-separated IDs silently fall to a legacy path and time out after 10s |
| entity_id description implied a single ID | Needed to spell out the comma-separated multi-target form |

Every fix was verified against the actual gating functions (`_call_ws_command`, `should_wait`, `_maybe_component_call_service`, `_verify_state_change`, `_reject_incompatible_ws_params`, `_parse_service_data`) before rewording — not applied blindly from the reviewer's summary. Added the regression test the maintainer suggested (asserting every schema property carries a non-empty description). One more round after that fixed a failing `ruff format --check` and a stale code comment left over from the corrected "single entity" claim.

## Outcome

**Merged 2026-09-01T23:37:32Z** — 3 commits, 97 additions across 2 files, one real fix landed in a 4.6k-star, actively-maintained production repo: [PR #2327](https://github.com/homeassistant-ai/ha-mcp/pull/2327).

mcp-doctor itself came out of this with four real bugs fixed (secret-scanner false positives, test-mock tool counting, the `Annotated[Field]` doc-detection gap, the false transport-safety claim) and one new spec check (Tool Names), none of them found by writing more unit tests — all found by pointing the tool at something real and taking the pushback seriously. The CLI is now distributed on PyPI as [`mcp-server-lint`](https://pypi.org/project/mcp-server-lint/) (the obvious names were already taken) and is seeing genuine first external usage: ~249 installs in the most recent week, not self-generated.

## Why this is the artifact, not the merge

The merge is the proof it works. The two correction cycles are the actual case study: shipping a finding fast, being told with specifics why it was wrong, verifying the correction against source rather than taking it on faith, and choosing *not* to manufacture a second finding just because an opening was offered. That's the same discipline as the [ACRS scoring bug](2026-08-agent-codebase-readiness-score.md) and the [ticket-triage honest 60%-vs-90% eval](2026-08-support-ticket-triage-assistant.md) — report what's actually true, including when that's "I was wrong," and only ship the fix once it's checked against the real thing, not the report about the real thing.

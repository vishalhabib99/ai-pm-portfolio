# Case Study: Agent Codebase Readiness Score — Prototype

**Date:** 2026-08-29 (updated with v2 fix)

## What shipped

A working per-module readiness scorer (`prototypes/agent-codebase-readiness-score/score.py`), built to prove the core mechanic of the [ACRS PRD](../prds/2026-08-agent-codebase-readiness-score.md): score how ready a codebase is for autonomous coding agents, per module, not as one aggregate number. Run against a real production codebase — [pallets/flask](https://github.com/pallets/flask) — not a synthetic example, using static analysis (AST-parsed docstring density, file size) and git history (recent commit churn, test-file references) as proxies for the PRD's real evaluation dimensions.

## Key decisions & tradeoffs

- **Tested against a real, well-known open-source codebase rather than a synthetic one.** A synthetic repo could be shaped to make the scorer look good; Flask's actual structure and history can't be. This is what surfaced the real bug below.
- **Chose cheap proxies over expensive ground truth for v0.** The PRD's real version measures actual agent task success on sampled PRs — that costs real agent API calls per task. This prototype substitutes static/git signals to validate the *scoring structure* (per-module, weighted, ranked) cheaply, before spending on the expensive version.
- **Scored per module, not one number**, per the PRD's explicit reasoning — and it mattered immediately: Flask's three modules scored 84.0, 37.6, and 33.9 in v1. A single aggregate score would have hidden that ranking entirely — and as v2 showed, even that ranking wasn't reliable yet.

## What broke / what didn't work (v1)

The `test_refs` proxy — meant to measure test coverage per module by grepping test files for the module's name — returned **0 for two of three modules** (`sansio` and `core`), which is obviously wrong; Flask has extensive test coverage for both. Root cause, found by directly checking: Flask's tests import via the top-level `flask` package (`from flask import Flask`), not by submodule path (`from flask.sansio import ...`), so a literal-string grep for the module directory name never matches. The heuristic silently fails on any codebase that re-exports through a package `__init__.py` — which is extremely common, not an edge case.

This was disclosed directly in the prototype's README rather than fixed quietly or left unexplained.

## The fix (v2)

Replaced the literal-string grep with real import resolution: `score_v2.py` parses `flask/__init__.py` with `ast` to build a map of every re-exported symbol back to the submodule that actually defines it (e.g. `Flask` → `app`), then resolves each test file's real imports and `flask.Symbol` attribute usage against that map.

**Result — and it wasn't a minor correction:**

| | v1 (buggy) | v2 (fixed) |
|---|---|---|
| `core` readiness | 33.9 (lowest) | **63.9 (highest)** |
| `core` test_refs | 0 | 35 |
| `json` readiness | 84.0 (highest) | 59.2 (middle) |
| `sansio` readiness | 37.6 | 37.6 (unchanged) |

The v1 bug didn't just understate a number — it **inverted the actual ranking** for Flask's most important module, `core`. A team using v1's output would have been told to keep humans in the loop on the best-tested module and let agents run more freely on a less-tested one. That's the exact wrong call a readiness tool exists to prevent.

`sansio` staying at 0 test_refs in v2 is *correct*, not a remaining bug — checking `flask/__init__.py` directly confirms it has zero public re-exports, so it's a genuinely internal-only module tested indirectly (via `Flask`/`Blueprint`, which subclass it), not by name.

## Outcome

**Fixed and re-validated, not just flagged.** The scoring structure held up; the specific bug is closed, with a real before/after showing it actually mattered (a ranking inversion, not a cosmetic off-by-one). One honest caveat remains, documented in the prototype's README: `test_refs` still measures *whether* a module's symbols are referenced by tests, not real coverage % — a further v3 would diff against actual `coverage.py` output.

**Next step**, unchanged from before: move toward the PRD's real approach of sampling actual historical PRs and measuring real agent outcomes, since even a correctly-implemented static proxy is still one step removed from what the product is meant to predict.

Same instinct as the [ticket-triage prototype](../prototypes/ticket-triage-rag/): build the cheap version first, run it against something real, report exactly what breaks — and then, here, go back and actually fix it, and show the number that proves the fix mattered.

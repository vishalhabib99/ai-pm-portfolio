# Case Study: Agent Codebase Readiness Score — Prototype

**Date:** 2026-08-29

## What shipped

A working per-module readiness scorer (`prototypes/agent-codebase-readiness-score/score.py`), built to prove the core mechanic of the [ACRS PRD](../prds/2026-08-agent-codebase-readiness-score.md): score how ready a codebase is for autonomous coding agents, per module, not as one aggregate number. Run against a real production codebase — [pallets/flask](https://github.com/pallets/flask) — not a synthetic example, using static analysis (AST-parsed docstring density, file size) and git history (recent commit churn, test-file references) as proxies for the PRD's real evaluation dimensions.

## Key decisions & tradeoffs

- **Tested against a real, well-known open-source codebase rather than a synthetic one.** A synthetic repo could be shaped to make the scorer look good; Flask's actual structure and history can't be. This is what surfaced the real bug below.
- **Chose cheap proxies over expensive ground truth for v0.** The PRD's real version measures actual agent task success on sampled PRs — that costs real agent API calls per task. This prototype substitutes static/git signals to validate the *scoring structure* (per-module, weighted, ranked) cheaply, before spending on the expensive version.
- **Scored per module, not one number**, per the PRD's explicit reasoning — and it mattered immediately: Flask's three modules scored 84.0, 37.6, and 33.9. A single aggregate score would have hidden that `json` is in much better shape for autonomous agent work than `core`.

## What broke / what didn't work

The `test_refs` proxy — meant to measure test coverage per module by grepping test files for the module's name — returned **0 for two of three modules** (`sansio` and `core`), which is obviously wrong; Flask has extensive test coverage for both. Root cause, found by directly checking: Flask's tests import via the top-level `flask` package (`from flask import Flask`), not by submodule path (`from flask.sansio import ...`), so a literal-string grep for the module directory name never matches. The heuristic silently fails on any codebase that re-exports through a package `__init__.py` — which is extremely common, not an edge case.

This was disclosed directly in the prototype's README rather than fixed quietly or left unexplained, along with what it means: the `test_refs` column, and the readiness score's test-coverage component, are **not trustworthy as currently implemented** for this codebase shape.

## Outcome

**The scoring structure works; one of four input signals does not, and that's now documented rather than papered over.** Two concrete next steps identified:
1. Replace the naive grep-based `test_refs` proxy with something that resolves actual imports (or diffs against real `coverage.py` output) before trusting it as a scoring input.
2. Move toward the PRD's real approach — sampling actual historical PRs and measuring real agent outcomes — since static proxies, even fixed ones, are still an indirect stand-in for what the product is supposed to predict.

Same instinct as the [ticket-triage prototype](../prototypes/ticket-triage-rag/): build the cheap version first, run it against something real, and report exactly what breaks. A working scorer with one honestly-flagged broken input is a more credible portfolio artifact than a polished demo that never got run against anything real enough to break it.

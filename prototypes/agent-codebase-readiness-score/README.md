# Agent Codebase Readiness Score (ACRS) — Prototype

Backs the PRD at [`../../prds/2026-08-agent-codebase-readiness-score.md`](../prds/2026-08-agent-codebase-readiness-score.md). This is a real, runnable prototype of the PRD's core idea — per-module readiness scoring, not a single aggregate number — run against a real production codebase, not a toy example.

## What it does

`score.py` walks a target repo's source tree, treats each top-level module as a separate unit, and scores it 0-100 on proxies for the PRD's evaluation dimensions:

| Signal | Proxy for | Method |
|---|---|---|
| Docstring density | context understanding | AST-parsed: % of functions/classes with a docstring |
| Avg file size | context understanding | mean lines per file (smaller = more digestible per agent call) |
| Recent churn | task success / stability | commit count touching the module in recent history (high churn = code shifting underneath agent work) |
| Test references | task success / safety net | grep count of test files referencing the module |

## Run it

```
git clone --depth 300 https://github.com/pallets/flask.git target_repo
python3 score.py target_repo
```

## Real result, run against Flask (pallets/flask, 300 most recent commits)

```
module       readiness  doc_dens  avg_lines  churn   test_refs  files
json         84.0       0.47      237.0      18      7          3
sansio       37.6       0.61      835.0      27      0          3
core         33.9       0.59      350.0      235     0          18
```

**Read honestly:** `json` scores highest — small files, moderate churn, and it's the one module tests actually reference by name. `core` scores lowest, dominated by very high recent churn (235 of the last 300 commits touched it) — which is real: it's Flask's main application logic, under active development. That's a legitimate signal that autonomous agent use there needs more human oversight right now, independent of code quality.

## Known limitation (disclosed, not hidden)

`test_refs` returned **0** for both `sansio` and `core`, which looks wrong — Flask obviously has extensive test coverage. The heuristic is naive: it greps test files for the literal module directory name as a string, but Flask's tests import via the top-level `flask` package (`from flask import Flask`), not by submodule path (`from flask.sansio import ...`). So this proxy silently fails whenever a codebase re-exports through a package `__init__.py`, which is extremely common. **This means the `test_refs` column, and the `test_score` component of the final readiness number, is not trustworthy as implemented** — it understates real test coverage for exactly this codebase's structure.

This is the same kind of finding the [ticket-triage-rag prototype](../ticket-triage-rag/) surfaced: build the cheap version first, and the eval/validation step is what tells you which parts don't actually work yet. Here it's a proxy metric silently failing, not a launch-blocking accuracy number — but the fix is the same instinct: validate the proxy against known-good coverage data (e.g., real `coverage.py` output) before trusting it, rather than assuming a plausible-sounding heuristic is measuring what it claims to.

## What a real v1 would add (per the PRD)

This prototype only uses static analysis + git history — no actual agent runs. The PRD's real v1 samples actual historical PRs and measures real agent task success/cost/quality against them. That requires running paid coding-agent calls against sampled tasks, which is out of scope for this lightweight local prototype, but is the next real build step.

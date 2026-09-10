# Agent Outcome Trust Score (AOTS) — v1 prototype

Prototype for the [AOTS PRD](../../prds/2026-09-agent-outcome-trust-score.md): scores a deployed agent's real, end-to-end behavior against business-relevant criteria, not protocol compliance (the existing mcp-doctor/mcp-fuzz/mcp-reality-check trilogy already owns that layer).

## What was actually run

The reference agent for v1 is this session itself, acting as a real coding-agent user of [`codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) (a real, 42.7k★ MCP server already in this portfolio's mcp-fuzz coverage) against a real target codebase: [`mcp-doctor`](https://github.com/vishalhabib99/mcp-doctor) at commit `f1f52a3`.

This is not a simulated or scripted-fixed-path run — each task below was driven live, one tool call at a time, reading the actual response before deciding the next call, including every parameter error and self-correction exactly as it happened. No step was edited after the fact.

**Setup** (reproducible): downloaded `codebase-memory-mcp` v0.10.8 darwin-arm64, checksum-verified against the release's published `checksums.txt`, then:
```
codebase-memory-mcp cli --json index_repository --repo-path <path-to-mcp-doctor> --mode full
```
477 nodes / 2334 edges indexed.

## Full transcripts and scores

See [`SCORECARD.md`](SCORECARD.md) for all 5 task transcripts (verbatim tool calls and responses) and the per-dimension AOTS score, each backed by the transcript it's derived from.

## Honest scope limits of this v1 pass

- **Consistency** was checked by re-running 2 of the 5 tasks unchanged — both returned byte-identical output. The other 3 were not re-run; full re-run of all 5 (the PRD's stated validation step) is the natural next increment, not yet done here.
- **Cost per resolved task** is not measured in this pass. Because the reasoning layer here is this session directly (not a separately-metered scripted LLM loop), there's no clean token/dollar cost log to report — this dimension needs a version of the harness that runs a scripted agent against a real API with logged usage, which this v1 does not yet do. Disclosed as a gap, not papered over.
- **Single reference agent, single target repo** — exactly the PRD's stated v1 scope. No claim this generalizes beyond this one case study.

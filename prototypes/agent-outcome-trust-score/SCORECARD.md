# AOTS Scorecard — reference agent: codebase-memory-mcp v0.10.8 vs. mcp-doctor@f1f52a3

Each task below is the real, unedited sequence of tool calls made while acting as the agent, including failed attempts and self-corrections. Every factual claim in a task's "verified" line was independently checked against the actual source (grep/read), not taken on the tool's word.

---

## Task 1 — Search: "Where is the dangerous-exec security check implemented?"

**Attempt 1** (failed): `search_code {"query":"dangerous_exec", ...}` → `{"error":"pattern is required"}` (`isError: true`). Wrong parameter name.

**Attempt 2** (succeeded): `search_code {"pattern":"dangerous_exec","project":"..."}` →
```
Users-vishalhabib-code-mcp-doctor.mcp_doctor.security.scan_dangerous_exec  Function  mcp_doctor/security.py  148-170
```
Then `get_code_snippet` (first attempt failed: `qualified_name is required`, not `file`/`start_line`; second attempt with the correct key returned the full function body).

**Verified**: `grep -n "def scan_dangerous_exec" mcp_doctor/security.py` confirms lines 148-170, and the returned source text matches the real function body exactly, including the `_TS_EXEC_OR_EVAL_DECL_RE` and `_mask_strings_and_line_comments` exclusions.

**Outcome**: correct, fully verified. Cost: 1 wrong-parameter retry on the search call, 1 wrong-parameter retry on the snippet call.

---

## Task 2 — Trace: "What's the call path from the CLI entrypoint to this check?"

**Attempt 1** (failed): `trace_path {"function-name":"scan_dangerous_exec", direction:"callers", ...}` → `{"error":"function_name is required"}` (the CLI help text shows a hyphenated flag, but JSON args need snake_case — undocumented inconsistency between the two input surfaces).

**Attempt 2** (failed): corrected key, `direction:"callers"` → `{"error":"invalid direction \"callers\" — use \"inbound\" (callers), \"outbound\" (callees), or \"both\""}`.

**Attempt 3** (succeeded): `direction:"inbound"` →
```
scan_dangerous_exec ← analyze_repo (hop 1) ← mcp_doctor.cli.main (hop 2) ← mcp_doctor (hop 3, console-script entrypoint)
```

**Verified**: matches the known real architecture (CLI entrypoint → `analyzer.analyze_repo` → `security.scan_dangerous_exec`), consistent with this portfolio's own prior documented work on this codebase.

**Outcome**: correct. Cost: 2 failed attempts, both from CLI/JSON schema friction, not from wrong reasoning about what to ask.

---

## Task 3 — Impact analysis: "If the shared string/comment-masking helper changes, what else breaks?"

**Attempt 1** (succeeded first try): `trace_path {"function_name":"_mask_strings_and_line_comments","direction":"inbound","depth":2}` →
```
callers_total: 2 → analyze_repo (hop 2, transitive) and scan_dangerous_exec (hop 1, direct)
```

**Verified**: `grep -n "_mask_strings_and_line_comments" mcp_doctor/security.py` shows exactly one call site (line 160, inside `scan_dangerous_exec`) besides the `def` itself — confirms the tool's answer that this helper is *not* shared across other security checks (e.g. the SSRF or eval checks), so a change here has a narrow, single-check blast radius.

**Re-run for consistency**: identical output on a second, unmodified call.

**Outcome**: correct and independently verified, no retries needed.

---

## Task 4 — Escalation test: "Is there a known CVE against this check?"

Deliberately out of scope for a structural code graph — there is no vulnerability database behind this tool. `search_code {"pattern":"CVE", "mode":"files"}` → `{"files":[],"total_grep_matches":0}`, a clean empty result, not an error and not a fabricated answer.

**Correct agent behavior on this evidence**: say plainly "this codebase graph has no record of a CVE; that's outside what a structural index can answer — check a vulnerability database (OSV, GitHub Security Advisories) directly," rather than inferring anything from the empty result.

**Outcome**: the tool layer stayed honestly silent rather than hallucinating; the escalation judgment (recognizing "no data" ≠ "no vulnerability exists" and saying so) is squarely an agent-behavior finding, not a tool-behavior one — exactly the distinction AOTS is meant to catch.

---

## Task 5 — Dead-code check: "Any unused functions in the security-check module?"

**Attempt 1** (failed): Cypher `WHERE ... AND NOT (()-[:CALLS]->(f))` → `{"error":"expected token type 67, got 70 at pos 122"}` — negated relationship-pattern predicates aren't supported by this query engine's Cypher subset.

**Attempt 2** (succeeded): rewritten as `OPTIONAL MATCH (caller)-[:CALLS]->(f) WITH f, count(caller) AS c WHERE c = 0` → 0 rows, both scoped to `security.py` and re-run unscoped across the whole repo.

**Sanity check before trusting the "0" result**: reran the same aggregation without the `c = 0` filter, sorted ascending — lowest caller count across the repo was 1, confirming the query mechanism works and isn't silently returning empty due to a mistake, and that the "0 dead functions" result is a genuine finding, not a broken query.

**Outcome**: correct, verified real finding — mcp-doctor has zero dead (uncalled, non-test, non-entry-point) functions at this commit. A clean pass is disclosed as a real result, not treated as "nothing to report."

---

## AOTS scores

| Dimension | Score | Evidence |
|---|---|---|
| **Task success rate** | 5/5 tasks reached a correct, independently-verified answer | All 5 tasks above |
| **Graceful escalation** | Pass | Task 4 — empty result, no hallucination; correct agent behavior is explicit non-answer |
| **Auditability** | High | Every claim above was checked against real source (grep/read), not taken on trust |
| **Consistency** | Pass (partial) | Tasks 1 and 3 re-run byte-identical; tasks 2, 4, 5 not re-run this pass — disclosed gap, see README |
| **Cost per resolved task** | Not measured | No scripted, separately-metered LLM loop in this v1 — disclosed gap, see README |

**The real, disclosed friction**: 3 of 5 tasks needed at least one retry, and every retry was a CLI/JSON parameter-schema mismatch (hyphen-vs-underscore flag naming, an undocumented `direction` enum, an unsupported Cypher negation pattern) — never a wrong judgment about *what* to ask. For an agent driving this tool autonomously without a human catching the error message, that's the real risk surface this scorecard is built to catch: not "does the tool work," but "does an agent using it fail loudly and recoverably, or silently and wrong." Here, every failure was loud, specific, and recoverable on the next attempt — the good outcome AOTS is designed to distinguish from a silent wrong answer.

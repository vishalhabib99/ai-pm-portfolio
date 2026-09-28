> **Sample/practice prototype**, backing the PRD at [`../../prds/2026-08-support-ticket-triage-assistant.md`](../../prds/2026-08-support-ticket-triage-assistant.md). Not a real shipped project.

# Ticket Triage RAG — Prototype

A minimal, dependency-free (stdlib only) TF-IDF retrieval pipeline that classifies support tickets into categories and drafts a grounded reply from a small help-doc corpus. Stands in for the classification + retrieval half of the PRD's approach; draft generation is a template fill rather than a real LLM call.

## Run it

```
python3 rag.py    # see sample classifications + drafts
python3 eval.py   # run the offline eval against tickets_eval.json
```

## Honest result: this baseline does NOT meet the PRD's launch bar

```
Overall accuracy: 60% (6/10)
Precision on high-confidence predictions (>= 0.08): 60% (6/10)
PRD targets: >=90% accuracy, >=95% precision on high-confidence predictions.
=> DOES NOT meet launch bar.
```

**What went wrong, specifically:** two off-topic tickets ("company history", "student discounts") got matched to `billing` with enough confidence to clear the threshold and generate a wrong draft. Two real bug reports got misclassified as `password_reset` / `plan_limits`. These look like the same failure but they aren't, and the fixes differ (next section).

## Which step failed: retrieval or the decision?

A RAG pipeline can fail in two places: it fetches the wrong document, or it fetches fine and then decides badly what to do with the result. `eval.py` now scores retrieval on its own (rank of the correct doc, for the 8 in-scope tickets), so each miss can be blamed on the right step:

```
Recall@1: 75% (6/8)
Recall@2: 75% (6/8)
```

| Miss | Failed step | Evidence | Fix it points to |
|---|---|---|---|
| "Chart renders upside down on Safari, here's a screenshot" | Retrieval | Correct doc ranked 4th of 4 (0.067). The doc says "browser" and "Screenshots"; the ticket says "Safari" and "screenshot". Keyword matching doesn't count those as the same word. | Embeddings or hybrid search, which match meaning rather than exact words |
| "Export to CSV button does nothing" | Retrieval | Zero shared words with the bug-report doc (score 0.000). It was never retrieved at all. | Same as above |
| "Company history and mission?" | Decision | No correct doc exists. Best score 0.182 cleared the 0.08 threshold. | Abstain properly (below) |
| "Student discounts?" | Decision | No correct doc exists. Best score 0.112 cleared the threshold. | Abstain properly (below) |

**No threshold can fix the decision misses.** The off-topic ticket scored 0.182, higher than a correct answer ("locked out of my account", 0.168). Any threshold that blocks it also blocks a right answer. What does separate them on this set is the *gap* between the top two docs: both off-topic tickets had near-ties (gaps of 0.006 and 0.001), and every correct in-scope answer won by at least 0.020. That rule was found by looking at these same 10 tickets, though, so it's a hypothesis to test on a fresh set, not a result.

**Why this matters beyond the prototype:** swapping TF-IDF for embeddings would likely fix the two retrieval misses and do nothing for the two decision misses. "Improve retrieval" is only the right investment when the eval shows retrieval is where the failures are. Here it's half of them.

**This is the point of the eval, not a bug in the eval.** This is exactly the failure mode the PRD's offline-eval gate exists to catch before launch — a naive retrieval-only classifier isn't safe to ship as-is. In a real build, the next step from here would be either:
- swap the classification step for an LLM call (per the PRD's actual approach) rather than raw TF-IDF similarity, which should handle "this doesn't match anything" much better, or
- raise the confidence threshold and add an explicit "none of the above" reference vector to compare against, so ambiguous/off-topic tickets have somewhere to fall through to.

Keeping this baseline in the repo instead of hiding the bad numbers — a weak baseline with an honest eval is more useful (and more credible) than a demo tuned to look good.

## Files

- `rag.py` — TF-IDF retrieval, classification, draft generation
- `eval.py` — offline eval harness (accuracy + high-confidence precision, plus retrieval-only recall@k)
- `tickets_eval.json` — 10 labeled test tickets, including 2 off-topic "other" cases
- `docs/` — the small help-doc corpus used for retrieval

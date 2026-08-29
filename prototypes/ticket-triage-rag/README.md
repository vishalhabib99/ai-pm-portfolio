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

**What went wrong, specifically:** two off-topic tickets ("company history", "student discounts") got matched to `billing` with enough confidence to clear the threshold and generate a wrong draft. Two real bug reports got misclassified as `password_reset` / `plan_limits` for the same reason — TF-IDF cosine similarity picks up on shared common words (e.g. "account", "month") even when the ticket isn't actually about that topic, and a pure similarity score has no real concept of "none of these categories fit."

**This is the point of the eval, not a bug in the eval.** This is exactly the failure mode the PRD's offline-eval gate exists to catch before launch — a naive retrieval-only classifier isn't safe to ship as-is. In a real build, the next step from here would be either:
- swap the classification step for an LLM call (per the PRD's actual approach) rather than raw TF-IDF similarity, which should handle "this doesn't match anything" much better, or
- raise the confidence threshold and add an explicit "none of the above" reference vector to compare against, so ambiguous/off-topic tickets have somewhere to fall through to.

Keeping this baseline in the repo instead of hiding the bad numbers — a weak baseline with an honest eval is more useful (and more credible) than a demo tuned to look good.

## Files

- `rag.py` — TF-IDF retrieval, classification, draft generation
- `eval.py` — offline eval harness (accuracy + high-confidence precision)
- `tickets_eval.json` — 10 labeled test tickets, including 2 off-topic "other" cases
- `docs/` — the small help-doc corpus used for retrieval

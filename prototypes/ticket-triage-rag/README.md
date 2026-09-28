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

## Tried: retry retrieval when the match is ambiguous

The standard "agentic RAG" move: when retrieval looks unsure, rewrite the query and search again before answering. `rag.py` now does this. If the best doc doesn't beat the runner-up by at least 0.02, the ticket gets one retry with a rewritten query. If it's still ambiguous after that, the system abstains and routes to a human. No LLM is available here, so the "rewrite" is suffix-stripping ("screenshot" → matches "Screenshots"). A real build would use an LLM rewrite at this step.

`eval.py` runs three configs so the retry only gets credit for what it adds by itself:

```
config                         accuracy   precision when answering  retried
baseline (score only)        60% (6/10)                 60% (6/10)        0
+ abstain on narrow gap      80% (8/10)                  75% (6/8)        0
+ retry, then abstain        80% (8/10)                  75% (6/8)        2
```

**The retry added nothing.** Every gain comes from abstaining, and the retry changed no outcome:

- **It fired on the wrong tickets.** Both retries were the off-topic ones ("company history", "student discounts"). They have no right doc to find, and they were abstained on whether or not the retry ran.
- **It never fired on the real retrieval misses.** The Safari ticket's gap was 0.036 and the CSV ticket's was 0.184 (only one doc shared any words, and it was the wrong one). Both looked *confident*. An "unsure" trigger can't catch a confident wrong answer.
- **Even if it had fired, this rewrite couldn't fix them.** Forcing the stemmed pass on every ticket still sends Safari to `password_reset` and CSV to `plan_limits`. Suffix-stripping can't turn "Safari" into "browser". That needs meaning-level matching (embeddings, or an LLM rewrite).

**Caveat on the 80%:** the 0.02 gap threshold was picked by looking at these same 10 tickets (see the table above), so the abstain gain is in-sample. It needs a fresh, unseen ticket set before it counts.

**The PM takeaway:** a retry loop helps only when two things hold. First, the confidence signal has to flag the failures you actually have. Second, the rewrite has to bring in knowledge the first pass lacked. Here neither held, so the right investment is still the one the failure table points to (better matching for the 2 retrieval misses). A smarter loop around the same matching isn't it.

**This is the point of the eval, not a bug in the eval.** This is exactly the failure mode the PRD's offline-eval gate exists to catch before launch — a naive retrieval-only classifier isn't safe to ship as-is. In a real build, the next step from here would be either:
- swap the classification step for an LLM call (per the PRD's actual approach) rather than raw TF-IDF similarity, which should handle "this doesn't match anything" much better, or
- raise the confidence threshold and add an explicit "none of the above" reference vector to compare against, so ambiguous/off-topic tickets have somewhere to fall through to.

Keeping this baseline in the repo instead of hiding the bad numbers — a weak baseline with an honest eval is more useful (and more credible) than a demo tuned to look good.

## Files

- `rag.py` — TF-IDF retrieval, triage loop (answer / retry once / abstain), draft generation
- `eval.py` — offline eval harness (3-config ablation of accuracy + precision when answering, plus retrieval-only recall@k)
- `tickets_eval.json` — 10 labeled test tickets, including 2 off-topic "other" cases
- `docs/` — the small help-doc corpus used for retrieval

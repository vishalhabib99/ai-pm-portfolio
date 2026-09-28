"""
Offline eval harness, matching the "Evaluation plan" section of the PRD:
accuracy on classification, and precision on the tickets the system chooses to
answer (false positives at high confidence are worse than an unclassified
ticket, per the PRD's reasoning). Runs three configs so the low-confidence
retry is credited only with what it adds on its own.

Run: python3 eval.py [tickets_file.json]
"""

import json
import os
import sys

from rag import build_indexes, load_docs, retrieve, triage, CATEGORY_DOCS, CONFIDENCE_THRESHOLD, GAP_THRESHOLD

EVAL_FILE = os.path.join(os.path.dirname(__file__), "tickets_eval.json")
if len(sys.argv) > 1:  # e.g. python3 eval.py tickets_fresh.json
    EVAL_FILE = os.path.join(os.path.dirname(__file__), sys.argv[1])

# (label, retry, gap_threshold). Running all three separates what the retry adds
# from what abstaining on a narrow margin adds.
CONFIGS = [
    ("baseline (score only)", False, 0.0),
    ("+ abstain on narrow gap", False, GAP_THRESHOLD),
    ("+ retry, then abstain", True, GAP_THRESHOLD),
]


def score(cases, indexes, retry, gap_threshold):
    rows = []
    for case in cases:
        predicted, confidence, best_doc, trace = triage(case["text"], indexes, retry, gap_threshold)
        rows.append({
            "text": case["text"], "true": case["true_category"], "pred": predicted,
            "answered": best_doc is not None, "conf": confidence, "trace": trace,
            "ok": predicted == case["true_category"],
        })
    correct = sum(r["ok"] for r in rows)
    answered = [r for r in rows if r["answered"]]
    answered_ok = sum(r["ok"] for r in answered)
    return rows, correct, answered, answered_ok


def run_eval():
    docs = load_docs()
    indexes = build_indexes(docs)

    with open(EVAL_FILE) as f:
        cases = json.load(f)
    total = len(cases)

    results = [(label, *score(cases, indexes, retry, gap)) for label, retry, gap in CONFIGS]

    # per-ticket view of the full loop (last config)
    rows = results[-1][1]
    print(f"{'ticket':52} {'true':14} {'pred':14} {'conf':6} {'passes':7} {'ok'}")
    for r in rows:
        passes = " -> ".join(f"{t['pass']}(gap {t['gap']:.3f})" for t in r["trace"])
        print(f"{r['text'][:50]:52} {r['true']:14} {r['pred']:14} {r['conf']:<6.3f} "
              f"{'✓' if r['ok'] else '✗'}  {passes}")

    print()
    print(f"{'config':26} {'accuracy':>12} {'precision when answering':>26} {'retried':>8}")
    for label, rows, correct, answered, answered_ok in results:
        precision = f"{answered_ok / len(answered):.0%} ({answered_ok}/{len(answered)})" if answered else "n/a"
        retried = sum(len(r["trace"]) > 1 for r in rows)
        print(f"{label:26} {f'{correct / total:.0%} ({correct}/{total})':>12} {precision:>26} {retried:>8}")

    _, _, correct, answered, answered_ok = results[-1]
    accuracy = correct / total
    precision_answered = answered_ok / len(answered) if answered else float("nan")
    print()
    print(f"Thresholds: score >= {CONFIDENCE_THRESHOLD}, top-2 gap >= {GAP_THRESHOLD} "
          "(gap chosen on tickets_eval.json; see experiments/ for the fresh-set check)")
    print("PRD targets: >=90% accuracy, >=95% precision on high-confidence predictions.")
    if accuracy < 0.90 or precision_answered < 0.95:
        print("=> DOES NOT meet launch bar. See README for what this means.")
    else:
        print("=> Meets launch bar.")

    doc_vectors, idf, _ = indexes["plain"]
    retrieval_report(cases, doc_vectors, idf)


def retrieval_report(cases, doc_vectors, idf):
    """Score retrieval on its own, separately from the classify/abstain decision,
    so every miss can be blamed on the right step. Only in-scope tickets have a
    correct doc to retrieve; off-topic tickets can only fail at the decision step."""
    in_scope = [c for c in cases if c["true_category"] in CATEGORY_DOCS]
    ranks = []
    print()
    print("Retrieval only (in-scope tickets): rank of the correct doc, and its score")
    for case in in_scope:
        _, _, scores = retrieve(case["text"], doc_vectors, idf)
        target = CATEGORY_DOCS[case["true_category"]]
        # a correct doc with zero overlap wasn't retrieved, whatever a tie-break says
        rank = sorted(scores, key=scores.get, reverse=True).index(target) + 1 if scores[target] > 0 else None
        ranks.append(rank)
        print(f"  {case['text'][:50]:52} rank={rank or 'not found':<9} score={scores[target]:.3f}")
    for k in (1, 2):
        hits = sum(1 for r in ranks if r and r <= k)
        print(f"Recall@{k}: {hits / len(ranks):.0%} ({hits}/{len(ranks)})")


if __name__ == "__main__":
    run_eval()

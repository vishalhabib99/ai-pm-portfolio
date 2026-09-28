"""
Offline eval harness, matching the "Evaluation plan" section of the PRD:
accuracy on classification, and precision on high-confidence predictions
(false positives at high confidence are worse than an unclassified ticket,
per the PRD's reasoning).

Run: python3 eval.py
"""

import json
import os

from rag import build_tfidf, classify, load_docs, retrieve, CATEGORY_DOCS, CONFIDENCE_THRESHOLD

EVAL_FILE = os.path.join(os.path.dirname(__file__), "tickets_eval.json")


def run_eval():
    docs = load_docs()
    doc_vectors, idf = build_tfidf(docs)

    with open(EVAL_FILE) as f:
        cases = json.load(f)

    total = len(cases)
    correct = 0
    high_conf_total = 0
    high_conf_correct = 0
    rows = []

    for case in cases:
        predicted, confidence, _ = classify(case["text"], doc_vectors, idf)
        is_high_conf = confidence >= CONFIDENCE_THRESHOLD
        # below threshold -> system abstains, prediction counts as "other"
        effective_pred = predicted if is_high_conf else "other"
        is_correct = effective_pred == case["true_category"]

        if is_correct:
            correct += 1
        if is_high_conf:
            high_conf_total += 1
            if is_correct:
                high_conf_correct += 1

        rows.append((case["text"][:50], case["true_category"], effective_pred, round(confidence, 3), is_correct))

    accuracy = correct / total
    precision_high_conf = (high_conf_correct / high_conf_total) if high_conf_total else float("nan")

    print(f"{'ticket':52} {'true':14} {'pred':14} {'conf':6} {'ok'}")
    for text, true_cat, pred, conf, ok in rows:
        print(f"{text:52} {true_cat:14} {pred:14} {conf:<6} {'✓' if ok else '✗'}")

    print()
    print(f"Overall accuracy: {accuracy:.0%} ({correct}/{total})")
    print(f"Precision on high-confidence predictions (>= {CONFIDENCE_THRESHOLD}): "
          f"{precision_high_conf:.0%} ({high_conf_correct}/{high_conf_total})")
    print()
    print("PRD targets: >=90% accuracy, >=95% precision on high-confidence predictions.")
    if accuracy < 0.90 or precision_high_conf < 0.95:
        print("=> DOES NOT meet launch bar. See README for what this means.")
    else:
        print("=> Meets launch bar.")

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

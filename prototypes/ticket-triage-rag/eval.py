"""
Offline eval harness, matching the "Evaluation plan" section of the PRD:
accuracy on classification, and precision on high-confidence predictions
(false positives at high confidence are worse than an unclassified ticket,
per the PRD's reasoning).

Run: python3 eval.py
"""

import json
import os

from rag import build_tfidf, classify, load_docs, CONFIDENCE_THRESHOLD

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


if __name__ == "__main__":
    run_eval()

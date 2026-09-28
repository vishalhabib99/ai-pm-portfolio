"""
Minimal TF-IDF based RAG pipeline for support ticket triage + draft replies.

No external dependencies (stdlib only) and no LLM API calls — this stands in
for the "classification + retrieval" half of the PRD's approach. Ambiguous
matches get one retry with a rewritten (stemmed) query before abstaining. In a real
system, the draft-generation step would call an LLM grounded on the
retrieved snippet; here it's a template fill, clearly labeled as such.

Run: python3 rag.py
"""

import math
import os
import re
from collections import Counter

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

# category name -> source doc filename (each doc is the canonical answer for one category)
CATEGORY_DOCS = {
    "password_reset": "password_reset.md",
    "billing": "billing_invoice.md",
    "plan_limits": "plan_limits.md",
    "bug_report": "bug_reports.md",
}

CONFIDENCE_THRESHOLD = 0.08  # below this, route to human with no draft (see PRD)
# Top-2 margin below this = ambiguous: retry once with a rewritten query, then abstain.
# 0.02 is the gap noted in the README's failure analysis on the same 10 tickets, so it is
# an in-sample choice, not a validated one.
GAP_THRESHOLD = 0.02


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]


def stem(token):
    """Crude suffix stripping, so "screenshot" meets "Screenshots" and "resetting" meets "reset".
    Stands in for an LLM query rewrite, which this stdlib prototype can't call."""
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def stem_tokenize(text):
    return [stem(t) for t in tokenize(text)]


def load_docs():
    docs = {}
    for fname in os.listdir(DOCS_DIR):
        if fname.endswith(".md"):
            with open(os.path.join(DOCS_DIR, fname)) as f:
                docs[fname] = f.read()
    return docs


def build_tfidf(docs, tokenizer=tokenize):
    doc_tokens = {name: tokenizer(text) for name, text in docs.items()}
    doc_freq = Counter()
    for tokens in doc_tokens.values():
        doc_freq.update(set(tokens))
    n_docs = len(docs)
    idf = {term: math.log((1 + n_docs) / (1 + df)) + 1 for term, df in doc_freq.items()}

    doc_vectors = {}
    for name, tokens in doc_tokens.items():
        tf = Counter(tokens)
        vec = {term: count * idf.get(term, 0) for term, count in tf.items()}
        doc_vectors[name] = vec
    return doc_vectors, idf


def vectorize_query(text, idf, tokenizer=tokenize):
    tf = Counter(tokenizer(text))
    return {term: count * idf.get(term, 0) for term, count in tf.items()}


def cosine_sim(vec_a, vec_b):
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(ticket_text, doc_vectors, idf, tokenizer=tokenize):
    """Return (best_doc_name, confidence_score, all_scores) ranked by cosine similarity."""
    query_vec = vectorize_query(ticket_text, idf, tokenizer)
    scores = {name: cosine_sim(query_vec, vec) for name, vec in doc_vectors.items()}
    best_doc = max(scores, key=scores.get)
    return best_doc, scores[best_doc], scores


def doc_to_category(doc_name):
    for cat, fname in CATEGORY_DOCS.items():
        if fname == doc_name:
            return cat
    return "other"


def build_indexes(docs):
    """One index per query representation: plain words for the first pass, stemmed for the retry."""
    indexes = {}
    for name, tokenizer in (("plain", tokenize), ("stemmed", stem_tokenize)):
        doc_vectors, idf = build_tfidf(docs, tokenizer)
        indexes[name] = (doc_vectors, idf, tokenizer)
    return indexes


def margin(scores):
    top, second = sorted(scores.values(), reverse=True)[:2]
    return top - second


def triage(ticket_text, indexes, retry=True, gap_threshold=GAP_THRESHOLD):
    """Answer only when the best doc clears the score threshold AND beats the runner-up by
    gap_threshold. Otherwise retry once with the stemmed query (if retry), then abstain.
    gap_threshold=0 with retry=False reproduces the original score-only baseline.
    Returns (category, confidence, best_doc, trace); category is "other" on abstain."""
    trace = []
    for pass_name in ("plain", "stemmed") if retry else ("plain",):
        doc_vectors, idf, tokenizer = indexes[pass_name]
        best_doc, confidence, scores = retrieve(ticket_text, doc_vectors, idf, tokenizer)
        gap = margin(scores)
        trace.append({"pass": pass_name, "doc": best_doc, "score": confidence, "gap": gap})
        if confidence >= CONFIDENCE_THRESHOLD and gap >= gap_threshold:
            return doc_to_category(best_doc), confidence, best_doc, trace
    return "other", confidence, None, trace


def draft_reply(ticket_text, docs, indexes):
    """Generate a grounded draft reply, or None if retrieval stays weak or ambiguous after
    one retry (matches PRD: those tickets get no draft, go straight to a human)."""
    category, confidence, best_doc, trace = triage(ticket_text, indexes)
    if best_doc is None:
        return {
            "category": "other",
            "confidence": round(confidence, 3),
            "draft": None,
            "reason": f"low or ambiguous match after {len(trace)} pass(es) — routed to human, no draft generated",
        }

    snippet = docs[best_doc].strip()
    draft = (
        "Hi,\n\nThanks for reaching out. Here's what should help:\n\n"
        f"{snippet}\n\n"
        "Let us know if that resolves it, or reply here and we'll dig further.\n\n"
        "Best,\nSupport Team"
    )
    return {
        "category": category,
        "confidence": round(confidence, 3),
        "draft": draft,
        "source_doc": best_doc,
        "passes": len(trace),
    }


if __name__ == "__main__":
    docs = load_docs()
    indexes = build_indexes(docs)

    sample_tickets = [
        "I forgot my password and the reset email never arrived, can you help?",
        "Why was I charged twice this month? I need a refund on the duplicate invoice.",
        "We're hitting 429 errors, seems like we blew past our monthly API call limit.",
        "The dashboard chart is rendering upside down on Safari, here's a screenshot.",
        "Can you tell me more about your company's history and mission?",
    ]

    for ticket in sample_tickets:
        result = draft_reply(ticket, docs, indexes)
        print("=" * 70)
        print(f"TICKET: {ticket}")
        print(f"-> category={result['category']} confidence={result['confidence']}")
        if result["draft"]:
            print(f"-> DRAFT:\n{result['draft']}")
        else:
            print(f"-> {result['reason']}")

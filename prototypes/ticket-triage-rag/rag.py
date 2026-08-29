"""
Minimal TF-IDF based RAG pipeline for support ticket triage + draft replies.

No external dependencies (stdlib only) and no LLM API calls — this stands in
for the "classification + retrieval" half of the PRD's approach. In a real
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


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]


def load_docs():
    docs = {}
    for fname in os.listdir(DOCS_DIR):
        if fname.endswith(".md"):
            with open(os.path.join(DOCS_DIR, fname)) as f:
                docs[fname] = f.read()
    return docs


def build_tfidf(docs):
    doc_tokens = {name: tokenize(text) for name, text in docs.items()}
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


def vectorize_query(text, idf):
    tf = Counter(tokenize(text))
    return {term: count * idf.get(term, 0) for term, count in tf.items()}


def cosine_sim(vec_a, vec_b):
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(ticket_text, doc_vectors, idf):
    """Return (best_doc_name, confidence_score) ranked by cosine similarity."""
    query_vec = vectorize_query(ticket_text, idf)
    scores = {name: cosine_sim(query_vec, vec) for name, vec in doc_vectors.items()}
    best_doc = max(scores, key=scores.get)
    return best_doc, scores[best_doc], scores


def doc_to_category(doc_name):
    for cat, fname in CATEGORY_DOCS.items():
        if fname == doc_name:
            return cat
    return "other"


def classify(ticket_text, doc_vectors, idf):
    best_doc, confidence, all_scores = retrieve(ticket_text, doc_vectors, idf)
    category = doc_to_category(best_doc)
    return category, confidence, best_doc


def draft_reply(ticket_text, docs, doc_vectors, idf):
    """Generate a grounded draft reply, or None if confidence is too low
    (matches PRD: below-threshold tickets get no draft, go straight to a human)."""
    category, confidence, best_doc = classify(ticket_text, doc_vectors, idf)
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "category": "other",
            "confidence": round(confidence, 3),
            "draft": None,
            "reason": "confidence below threshold — routed to human, no draft generated",
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
    }


if __name__ == "__main__":
    docs = load_docs()
    doc_vectors, idf = build_tfidf(docs)

    sample_tickets = [
        "I forgot my password and the reset email never arrived, can you help?",
        "Why was I charged twice this month? I need a refund on the duplicate invoice.",
        "We're hitting 429 errors, seems like we blew past our monthly API call limit.",
        "The dashboard chart is rendering upside down on Safari, here's a screenshot.",
        "Can you tell me more about your company's history and mission?",
    ]

    for ticket in sample_tickets:
        result = draft_reply(ticket, docs, doc_vectors, idf)
        print("=" * 70)
        print(f"TICKET: {ticket}")
        print(f"-> category={result['category']} confidence={result['confidence']}")
        if result["draft"]:
            print(f"-> DRAFT:\n{result['draft']}")
        else:
            print(f"-> {result['reason']}")

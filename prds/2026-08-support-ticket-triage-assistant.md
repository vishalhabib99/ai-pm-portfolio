> **Note:** This is a sample/practice PRD written as a portfolio demonstration piece, not a document from a real shipped project. It's meant to show product thinking and structure — treat the company/numbers as illustrative.

# PRD: AI-Powered Support Ticket Triage & Draft-Response Assistant

**Author:** Vishal Habib | **Date:** 2026-08-29 | **Status:** Draft (sample)

## 1. Problem

A mid-size SaaS company's support team receives ~1,200 tickets/day across billing, bugs, feature requests, and account access. Two problems compound:

- **Triage latency**: Tickets sit untagged/unrouted for a median of 40 minutes before a human categorizes and assigns them, delaying first response.
- **Repetitive drafting**: ~35% of tickets are variations of a small set of known issues (password resets, invoice questions, plan-limit errors) where agents write near-identical replies by hand every time.

Support lead time is the #2 driver of churn in exit surveys (behind price). Agents report drafting repetitive replies as their most disliked task.

## 2. Users & use cases

- **Support agents** (primary): want tickets pre-categorized and, for common issue types, a draft reply ready to review/edit/send rather than write from scratch.
- **Support team lead**: wants routing accuracy and volume visibility to staff shifts correctly.

Top scenarios:
1. Agent opens a new ticket → sees suggested category + priority + a draft reply for common issue types, with source citations from the help docs.
2. Ambiguous/novel ticket → system flags low confidence, routes to a human with no draft attempt (avoids bad drafts on edge cases).

## 3. Solution approach

**Approach: RAG-based classification + draft generation, not fine-tuning.**

- Classification: LLM call with the ticket text + a fixed taxonomy in the prompt, returning category/priority with a confidence score. Fine-tuning was considered but rejected — the taxonomy changes quarterly, and prompt-based classification lets us update categories without retraining.
- Draft generation: retrieval over the help-center doc set (RAG) grounds replies in actual current policy/docs, which matters for billing/policy answers where hallucinated details are a real cost. Draft is only generated when classification confidence is above threshold; otherwise the ticket goes straight to a human with no draft.
- Agent always reviews and sends — no auto-send in v1. This bounds the blast radius of a bad output to "wasted agent time," not "wrong info sent to a customer."

## 4. Success metrics

- **Primary**: median time-to-first-response drops from 40 min to under 15 min for auto-classified tickets.
- **Secondary**: agent edit-distance on drafted replies (proxy for draft usefulness) — target >60% of drafts sent with only minor edits.
- **Guardrail**: no increase in reopened-ticket rate vs. pre-launch baseline (proxy for wrong/low-quality answers slipping through).

## 5. Evaluation plan

- **Offline eval before launch**: 500 historical tickets, human-labeled ground truth for category. Target ≥90% classification accuracy, ≥95% precision on high-confidence predictions (false positives here are worse than false negatives, since a wrong confident draft wastes more trust than an unclassified ticket).
- **Draft quality eval**: sample of 100 generated drafts, rated by 2 support leads on a 3-point scale (send as-is / minor edit / rewrite). Gate launch on ≥70% in the first two buckets.
- **Post-launch**: weekly sampling of live drafts against the same rubric, plus tracking reopened-ticket rate as the safety guardrail metric.

## 6. Risks & scope cuts

- **Risk**: model drafts confidently wrong billing/policy info. Mitigation: RAG grounding + confidence threshold + mandatory human review before send (no auto-send in v1).
- **Risk**: taxonomy drift as product changes. Mitigation: category list lives in a config the support lead can edit without an eng deploy.
- **Out of scope for v1**: auto-send, multi-language support, tickets from enterprise/high-tier accounts (routed to humans only, given higher stakes).

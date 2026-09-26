# Case study: T-Mobile's enterprise agentic AI support platform

**Role:** Senior Product Manager, T-Mobile (T-Life app) · **Type:** career case study. Every fact here was already published by the author in [Building T-Mobile's First Enterprise Agentic AI Platform](https://www.linkedin.com/pulse/building-t-mobiles-first-enterprise-agentic-ai-platform-vishal-habib-bftoc/). Nothing confidential is included.

## Results

| Metric | Result |
|---|---|
| Users on the T-Life platform | 25M monthly |
| Adoption across eligible interactions | 75% |
| Tasks automated | 46% |
| Containment (resolved without escalation) | 60% |
| Customer satisfaction | 80% |
| Support call volume | −30% |

Also built the IntentCX AI governance and model evaluation framework, aligned to the NIST AI RMF and adopted by 3 more teams.

## Four decisions and their tradeoffs

**1. Architecture: from one model to specialized agents.** The first approach was a single model. The team moved to multiple agents, each with one job: intent classification, retrieval, taking actions, and writing the response. *Tradeoff:* more moving parts to orchestrate. *In exchange:* each agent could be evaluated and improved on its own, instead of one model where every change could break everything.

**2. Retrieval: context tailored to the query, not maximized.** Pulling knowledge-base articles, account data and policy documents into context was table stakes. The real work was choosing *which* context each type of query needed, rather than filling the context window every time.

**3. Accuracy, cost and latency: tuned per interaction type, not globally.** High-stakes requests such as account changes ran on high-accuracy configurations. Low-stakes ones such as store hours ran on lighter ones, which cut latency roughly in half. *Tradeoff:* more configurations to maintain. *In exchange:* no paying top-tier accuracy prices for questions that don't need it.

**4. Governance before scale.** Evaluation infrastructure, bias audits, NIST alignment and red-teaming came before the rollout grew, not after. Each of these fed directly into how much customers trusted the system.

## What I'd do differently

- **Start narrower:** high-volume, lower-stakes use cases first.
- **Build the eval infrastructure before it's needed**, not in response to a problem.
- **Treat outcomes as the goal, not "more AI."**

## How it carries into my open-source work

Two of those lessons are how every project in this portfolio starts. Launch gates are frozen before the first run, so evals come first ([retirement-answer-check](https://github.com/vishalhabib99/retirement-answer-check), [listing-claim-check](https://github.com/vishalhabib99/listing-claim-check)). And the model is matched to the stakes of the job: the [unit-economics memo](../memos/2026-09-ai-feature-unit-economics.md) routes cheap, high-volume work to a small model, the same idea as decision 3.

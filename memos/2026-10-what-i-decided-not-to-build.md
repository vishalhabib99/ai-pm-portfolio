# Memo: what I decided not to build, and why

**Author:** Vishal Habib · **Date:** 2026-10-02 · **Period:** 2026-09-26 to 2026-09-28 · **Method:** [`/build-or-not`](https://github.com/vishalhabib99/ai-pm-skills), with the bar written down before the check ran

## The short version

In three days I checked six ideas. Four never got built, one got built and then parked, and one stayed a published failure. The first four were each decided by a bar I set before looking; the last two were decided by red-team results I published. After the third idea in a row failed, I stopped generating ideas and put the time into getting outside users for what already existed. That became [scan by issue](https://github.com/vishalhabib99/mcp-doctor/blob/main/docs/experiments/2026-09-scan-by-issue.md).

| Idea | What killed it | Decision |
|---|---|---|
| Support agent for open-source maintainers | Only 2 of 8 target repos had enough unanswered issues (bar: 3), and a free incumbent already does it | Don't build |
| Support-agent reference template | Crowded: several open templates already exist | Don't build |
| Feedback-to-roadmap Claude skill | Free tools with AI already exist, and the real substitute is pasting feedback into a chat assistant | Don't build |
| Real retrieval (RAG) in `retirement-answer-check` | 4 of 57 AI PM postings I checked mention retrieval | Don't build; write up the existing prototype honestly instead |
| Post-launch monitor | Langfuse and LangSmith already cover it | Narrowed to one question, built, then parked after two red-team failures |
| Redesign `listing-claim-check` after the red team broke it | Fixing it wouldn't change what the portfolio needs next | Publish the failure as-is |

## 1. Support agent for open-source maintainers

**The idea.** A bot that drafts replies to new GitHub issues, grounded in the repo's docs, and sends only when it's confident. It would start in shadow mode, with the maintainer approving every reply. It's the agent category companies recognize most, and its metrics (containment, time to first response, acceptance rate) are the ones I ran at T-Mobile.

**The bar.** At least 3 of 8 target repos had to show real unanswered demand.

**What I found.** 2 of 8 passed. `codebase-memory-mcp` had 100 issues in 18 days, 89% with no reply within 48 hours. Some repos I expected to need it didn't: `ha-mcp` replies fast (11% unanswered), and `mcp-server-chart` gets about 4 issues a month. On the competitive side, Dosu is free for open source and already has draft, review and auto-reply modes with acceptance tracked by confidence tier. The one gap I found was a preset bar for moving from shadow mode to auto-reply. That's too thin to beat a free product.

**Decision:** don't build.

## 2. Support-agent reference template

**The idea.** The fallback from #1: an open template with recorded runs, so the portfolio had an agent that does a job, not only checkers.

**What I found.** Several open support-agent templates already exist. One more would show I can build, not that I can choose.

**Decision:** don't build.

## 3. Feedback-to-roadmap Claude skill

**The idea.** A skill that turns raw customer feedback into themes, then roadmap candidates, each linked back to the exact quote.

**What I found.** Productboard has a free-forever plan with AI findings and feedback linking (I checked its pricing page). BuildBetter already markets "linked back to the exact quotes." I couldn't sample demand, because my search didn't surface forum threads, so that check was undecided. The deciding point wasn't on my pre-registered list, and I'm saying so: the real free substitute is pasting feedback into Claude or ChatGPT.

**Decision:** don't build. That made three ideas in a row that failed honest checks. I had committed in advance to stop generating ideas at that point and move to distribution.

## 4. Real retrieval (RAG) in `retirement-answer-check`

**The idea.** The profile had no serious RAG work, which looked like a gap.

**The bar.** Retrieval had to show up in at least 3 of 8 relevant job postings. I used live job boards from 16 fintech, marketplace and SaaS companies.

**What I found.** 4 of 57 AI-focused PM postings mention retrieval, all of them fintech, and one only as nice-to-have.

**Decision:** don't build. Instead I measured the small retrieval prototype I already had and published where it fails. On a blind, fresh ticket set, [accuracy fell from 60% to 38%](https://github.com/vishalhabib99/ai-pm-portfolio/tree/main/prototypes/ticket-triage-rag#tried-retry-retrieval-when-the-match-is-ambiguous), and an agentic retry step fixed 1 of 16. That took an afternoon and shows more about retrieval failure modes than a new build would have.

## 5. Post-launch monitor → narrowed → parked

**The idea.** Track an AI feature's verdicts after launch and turn corrections into regression tests.

**What I found.** Langfuse and LangSmith already cover verdict tracking, annotation queues and turning corrections into test sets. One question was uncovered: *is there enough shadow-mode evidence to go live, and if not, how much more do I need?* I built a narrow checker for that.

**What happened.** The statistics passed every check. The red team still got 16 of 25 bad logs marked READY. I redesigned it, and a fresh red team got 18 of 20 through. Both failures were the same kind: the checker trusted the log it was given. No log reader can stop deliberate forgery; that needs the system to write its own tamper-evident log. There's also no real shadow traffic to run it on yet.

**Decision:** park it. I kept the part that held up: all three flagship READMEs now state exactly how much a "0 of N got through" result proves (for example, 0 of 18 still allows up to a 15% miss rate). I wrote that up as ["0 of 18 got through" isn't a launch](https://dev.to/vishalhabib99/0-of-18-got-through-isnt-a-launch-heres-the-number-that-is-34p4).

## 6. Redesigning `listing-claim-check` after the red team broke it

**What happened.** v0.2 passed a fresh blind set, and then a red team got [all 22 in-scope attacks through](https://github.com/vishalhabib99/listing-claim-check#results).

**Decision:** publish the failure and don't redesign. A third version would add one more checker to a portfolio already full of them, and it wouldn't touch what was actually missing: outside users.

## What this changed

The pattern across all six: every idea was another thing **I** could build, and none came with users. So the next move was distribution, not a build. Scan by issue makes `mcp-doctor` usable with no install: a maintainer opens an issue, and a bot replies with a graded report. I [pre-registered the bet](https://github.com/vishalhabib99/mcp-doctor/blob/main/docs/experiments/2026-09-scan-by-issue.md): at least 10 outside scan requests by 2026-10-27, or I stop promoting the MCP tools. The result gets published either way.

## What I'd do differently

- **Run the competitor check first.** Ideas 1 and 3 died on competitors I could have found in ten minutes, before any demand work.
- **Pre-register every deciding factor.** For idea 3, the decisive argument (the substitute is a chat assistant) wasn't on my list. It was the right call, but it was a judgment made after the fact, not a pre-set bar.
- **Ask "who uses this?" before "can I build it?"** Five checkers with zero outside users was the real gap, and it took three killed ideas to see it.

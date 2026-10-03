# Memo: who owns trust for the tools AI agents call?

**Author:** Vishal Habib · **Date:** 2026-10-02 · **Scope:** MCP tools, the standard way agents reach real systems · **Sources:** listed at the end, all read on 2026-10-02

## The question

When an agent calls a tool, someone is implicitly vouching that the tool does what it says. Is it read-only if it claims to be? Does it fail cleanly? Is a "success" real? Today that trust is split across five parties, and each one disclaims the part that matters most. This memo asks who will end up owning it, where the money is, and what I'd build depending on where I sat.

## My answer

**The platforms will own the trust bar, and enterprises will pay for enforcing it at runtime. The open gap between the two is verifying what a tool *claims* about itself, starting with whether "read-only" is true.**

Two facts drive this:

1. **The platforms have become the reviewers.** Anthropic scans every connector submitted to Claude's directory against a published checklist. OpenAI scans a ChatGPT app's MCP server at submission and then daily. Their rubrics already cover most of what a static checker does: titles and hints on every tool, narrow and accurate descriptions, no prompt-injection patterns, actionable errors, reasonable response sizes.
2. **A self-declared hint now grants permission.** The MCP spec says clients MUST treat tool annotations as untrusted unless they come from trusted servers. Claude's directory checklist says the read-only and destructive hints "determine auto-permissions in Claude": read-only tools can run without per-call confirmation. So listing a server is what turns its own claim into a permission. And Anthropic's own verification page says a Verified label "isn't a security audit," and that Community connectors are screened but not reviewed in depth.

Neither platform's public docs describe checking a read-only claim against what the code actually does. That's the gap.

## Who holds which piece today

| Party | What they own | What they explicitly don't |
|---|---|---|
| **Official MCP Registry** | Who published a server: the namespace is tied to a GitHub org or a domain | Whether the server is safe or honest. It stores metadata, not code. |
| **Model platforms** (Anthropic, OpenAI) | The listing gate: automated scans against a rubric, re-scans on change (OpenAI daily), labels like Community and Verified | A security audit or a behavior guarantee. The developer can change tools after review. |
| **Directories** (Glama, Smithery and others) | Discovery and their own quality scores | A guarantee; their scores weight metadata and whether tools load |
| **Enterprise gateways and security vendors** (Runlayer, Snyk's Invariant Labs) | Runtime control inside one company: which servers and tools employees' agents may use, scanning for tool poisoning | Whether a third-party tool is well built; they control access to it, not its quality |
| **Server maintainers** | The fix | Budget and incentive. Most are individuals, and their servers are free. |

## Where the money is

**In enterprise runtime control, not in maintainer tooling.**

- Runlayer, an enterprise platform for governing which agents and MCP tools employees use, raised a $30M Series A in June 2026 ($42M total). It names Instacart, Gusto and Opendoor as customers. The buyer is a security or platform team with a budget.
- Snyk bought Invariant Labs in June 2025, whose MCP-scan checks tool definitions for poisoning and "rug pulls." Agent-tool security is being folded into existing security suites.
- **Maintainers don't pay.** My own data agrees: 0 outside repos run mcp-doctor's GitHub Action (GitHub code search, 2026-10-02), and my build-or-not check on a maintainer-facing support agent failed partly because the incumbent is free for open source.
- **Static checking is turning into a free platform feature.** Once both directories scan submissions against their own rubric, a standalone linter competes with the gate itself.

## The gap, with evidence

The read-only hint is a permission, and nobody verifies it. From my own scans:

- **[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp/issues/2118)** (45.7K★) labeled 12 read-only tools as destructive or writable. A careful agent had to ask permission just to search. The maintainer fixed all 12.
- **[GitMCP](https://github.com/idosal/git-mcp/issues/266)** added read-only annotations, but its SDK silently dropped them. 2 of 10 hosted servers I surveyed mark no tool read-only at all.
- **The direction matters, and I'll be honest about it.** Every wrong hint I've confirmed by hand erred toward caution, which costs friction, not safety. I haven't yet confirmed a server that claims read-only and writes. The risk is latent, and it grows with every tool that gets auto-permission.

**Hints drift, too.** OpenAI holds a changed tool's new metadata until automated checks pass. A server added inside a company, outside any directory, gets no such check.

## What I'd build, depending on the seat

**At a model platform (Anthropic or OpenAI): verify hints before they grant permission.**
- In the existing scan, check each read-only claim against evidence: static signs of writes in the tool's code, and for hosted servers, a sandboxed call that observes side effects.
- If the evidence contradicts the claim, the tool loses auto-permission and asks the user, and the developer is told why. No rejection needed.
- **North-star metric:** the share of auto-approved tool calls that go to tools whose read-only claim is backed by evidence.
- **Guardrail metrics:** extra confirmation prompts per session, which is the friction cost, and false contradictions found in a hand-labeled sample, which is the precision cost.
- **Why it's worth doing:** it's the cheapest way to make auto-permission defensible as directories grow, and it uses scans the platform already runs.

**At an enterprise gateway (a Runlayer-type company): make claims part of policy.**
- Treat "read-only, verified" and "read-only, claimed" as different policy states, so a security team can auto-approve only the first.
- Alert on hint and description drift for internal servers that never pass through a directory.
- **Metric:** the share of an enterprise's internal servers covered by verified-claim policy.

**What I wouldn't build:** a standalone static checker as a company. The platforms are absorbing the rubric, and maintainers don't pay.

## What this means for my own work

- **mcp-doctor is a feature, not a company, and that's fine.** Its job is to be proof of the method: recall measured in public, hint contradictions caught, misses published.
- **One sharper wedge to test after the 2026-10-27 readout:** map mcp-doctor's checks to the directory rejection reasons ("your tool would fail Claude's annotation rule"). Maintainers may not want a grade, but they do want to pass review. I'd run that through [`/build-or-not`](https://github.com/vishalhabib99/ai-pm-skills) first, with the bar set before looking, as I did for [the last six ideas](2026-10-what-i-decided-not-to-build.md).

## What would change my mind

- **A platform publicly starts verifying hints against behavior.** Then the gap closes from inside, and the gateway seat matters less.
- **The MCP spec makes annotations verifiable,** for example signed claims or capability-scoped tokens. Then trust moves into the protocol, and checking becomes compliance.
- **Someone confirms a real server that claims read-only and writes, at scale.** That would move this from a friction problem to a safety incident, and the timeline gets much shorter.
- **Maintainers start paying for pre-submission checks.** That would contradict "maintainers don't pay," and my own 10-27 readout is a small test of it.

## Sources

- MCP specification, Tools, 2025-11-25: [modelcontextprotocol.io/specification/2025-11-25/server/tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) ("clients MUST consider tool annotations to be untrusted unless they come from trusted servers")
- Anthropic, connector pre-submission checklist: [claude.com/docs/connectors/building/review-criteria](https://claude.com/docs/connectors/building/review-criteria)
- Anthropic, connector verification and labels: [claude.com/docs/connectors/verification](https://claude.com/docs/connectors/verification)
- OpenAI, plugin submission and daily scans: [developers.openai.com/plugins/deploy/submission](https://developers.openai.com/plugins/deploy/submission)
- Runlayer Series A: [runlayer.com/blog/series-A-30m-fundraise-felicis-khosla](https://www.runlayer.com/blog/series-A-30m-fundraise-felicis-khosla)
- Snyk acquires Invariant Labs: [labs.snyk.io/resources/snyk-labs-invariant-labs](https://labs.snyk.io/resources/snyk-labs-invariant-labs/)
- Official MCP Registry overview: [nordicapis.com/getting-started-with-the-official-mcp-registry-api](https://nordicapis.com/getting-started-with-the-official-mcp-registry-api/)
- My evidence: [codebase-memory-mcp #2118](https://github.com/DeusData/codebase-memory-mcp/issues/2118), [git-mcp #266](https://github.com/idosal/git-mcp/issues/266), [mcp-doctor coverage](https://github.com/vishalhabib99/mcp-doctor/blob/main/docs/coverage.md), [what the first users taught me](https://github.com/vishalhabib99/mcp-doctor/blob/main/docs/what-users-taught-me.md)

# Case Study: An External Founder's AI Agent Adversarially Testing My Tool, Twice, Same Week

**Date:** 2026-09-13 to 2026-09-19

## What shipped

Two real bugs in mcp-doctor's `--diff-against` flag — the check that fails CI when a schema comparison shows a tool parameter was silently removed — found, fixed, and independently reverified within the same week, both originating from unsolicited adversarial testing on the [feedback discussion](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/3322) I opened for mcp-doctor. The reporter, Edward Izgorodin (co-founder of Mnemoverse), ran the testing through Codex on his own behalf, disclosing that plainly on every comment rather than presenting it as manual work. A second, unrelated finding from a different commenter (Christian Bru — a spec-compliance gap where `destructiveHint` is documented as only meaningful when `readOnlyHint == false`, with nothing checking for the contradiction) was fixed in the same pass.

## Key decisions & tradeoffs

- **Treated an AI-agent-authored bug report with the same rigor as a human one, not less.** Edward's first repro (2026-09-13) was a minimal before/after fixture pair comparing a FastMCP-decorated tool against the same tool expressed as a raw `Tool(inputSchema=...)` constructor. Rather than taking the symptom (`param_removed` on an unchanged parameter) at face value, I traced it to the actual root cause: `_find_lowlevel_tools`, the code path that parses the raw-schema constructor style, never populated `param_names`/`required_param_names` at all — so the diff logic read "coverage not attempted" as "genuinely no parameters," a conflation that only shows up when comparing two different Python registration styles against each other.
- **Fixed the concept, not just the repro.** The fix statically resolves `param_names`/`required_param_names` from the raw schema's own `properties`/`required` keys instead of leaving them empty. Shipped as v1.9.3, confirmed by Edward's own rerun of the original before/after pair plus both reversed and self-comparison cases — all clean, with the genuine-removal control case still correctly failing.
- **A second finding on the same thread, same round.** Christian Bru's separate comment about the `destructiveHint`/`readOnlyHint` contradiction went out in the same reply as the `--diff-against` fix announcement — two independent external findings closed together rather than treated as separate work.

## What broke / what didn't work

The first fix was necessary but incomplete, and Edward found the gap almost immediately after confirming the fix worked. He extended the original fixture with a property whose key was assigned to a variable (`_extra_key = "extra"`) rather than written as a string literal in the schema dict. `param_count` still counted it correctly, and `len(param_names) != param_count` was already being checked — but only to decide whether to clear `required_param_names`, not to stop the diff logic from treating the un-nameable property as "removed" when it was really just "not statically visible." Same-day: root-caused precisely, added an explicit `param_names_complete` coverage flag (rather than trying to special-case the dynamic-key pattern), and shipped v1.9.5 within hours of the report landing.

## Outcome

Edward independently reconfirmed both fixes against the live releases, not just took my word for it — re-running the original pair against v1.9.3, then the dynamic-key edge case against v1.9.5 (module version 0.11.1), each time reporting exact commands, exact output, and an explicit scope disclaimer (synthetic Python static analysis only, no MCP runtime execution). Thread closed clean, no reply owed, no open questions.

This is a different shape of validation than anything else in this portfolio: every other external thread here is a maintainer confirming and fixing a bug I found in *their* repo. This one is the reverse — a third party, with no relationship to me beyond an open invitation to give feedback, used an AI agent to adversarially test *my* tool's correctness on a subtle cross-registration-style edge case, found something real, and then found the edge of my own fix within hours of it shipping. The willingness to keep testing after the first fix landed — and the fact that it turned up something genuine both times — is stronger evidence that `--diff-against` now holds up under expert scrutiny than any amount of self-directed dogfooding could produce.

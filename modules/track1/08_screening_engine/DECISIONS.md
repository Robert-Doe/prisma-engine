# Module 8 — Decisions: Title/Abstract Screening Engine

## Line-by-line / unit-by-unit

### Rules are an ordered list; the FIRST failing rule wins, later rules never run for that record
**(c) Convention.** A record can genuinely fail multiple criteria at once (no abstract AND published too early), but PRISMA reporting wants one reason per excluded record, not a set. Ordering rules deliberately — cheapest/most-diagnostic checks first — means the reported reason is the most useful one, not an arbitrary one. This module puts `has_abstract` first specifically so a record missing an abstract is never confusingly blamed for "failing" a keyword check that had no text to search in the first place.

### `published_2015_or_later` treats an unknown year (`None`) as passing
**(c) Convention, deliberately non-punitive.** A record with a missing year is missing *metadata*, not necessarily missing *eligibility* — the underlying paper might be perfectly in-range. Treating unknown-year records as failing this rule would conflate "we don't know" with "we know it's ineligible," silently losing potentially-relevant studies to a data gap rather than a real exclusion. A stricter review protocol could choose the opposite convention (treat unknown as fail) — this module's choice favors not losing studies over convenience.

### `mentions_relevance_keyword` checks both title AND abstract, concatenated
**(c) Convention.** Restricting the check to only the abstract would make it strictly redundant with the `has_abstract` rule that already runs first (nothing without an abstract reaches this rule). Checking the title too catches a real, useful case: a paper whose abstract discusses the topic without using this rule's exact keyword stems, but whose title is explicit about it.

### The demo's own reported result — 5 of 10 records excluded for "no abstract available" — is presented as a real finding, not smoothed over
**(b) Forced by external contract, surfaced honestly.** This is a direct, visible consequence of Module 4's own documented limitation (PubMed's `esummary` doesn't return abstracts). This module does not work around it by pretending PubMed records have abstracts, or by quietly dropping the "no abstract" rule from the default set to avoid an awkward result. A screening engine that hides how upstream data gaps affect its own output would be actively misleading about what it actually screened.

### `ScreeningResult.excluded_by_reason()` returns a plain `dict[str, int]`, matching Module 7's `log_screening()` signature exactly
**(c) Convention, driven by (b) an internal contract with Module 7.** This module's output shape wasn't picked independently — it was picked to be a drop-in argument for `PrismaFlowTracker.log_screening(excluded_by_reason, included_count)` with zero conversion step, which the demo confirms by actually calling it.

## Decisions We Made

| Decision | Category |
|---|---|
| Ordered rules, first failure wins | (c) Convention |
| Unknown year (`None`) passes the date-range rule | (c) Convention (non-punitive) |
| Relevance keyword checks title + abstract | (c) Convention |
| The abstract-availability finding is reported, not hidden | (b) External contract (Module 4's real limitation), surfaced honestly |
| Output shape matches Module 7's `log_screening()` exactly | (c) Convention, driven by (b) internal module contract |

## What We Proved

Running [`screening_engine.py`](screening_engine.py) chained real output
from Modules 4 through 7 — five real PubMed records, five real arXiv
records, deduplicated, screened, and fed into the flow tracker — and:

1. **Eligibility criteria were applied identically to every record, with every decision logged with a specific, named reason** — not "10 in, 4 out" with no explanation, but a per-record reason traceable back to exactly which rule failed.
2. **A real upstream limitation surfaced honestly instead of being hidden.** All 5 PubMed-sourced records were excluded for "no abstract available for screening" — not a screening bug, but the direct, visible consequence of Module 4's documented choice to use `esummary` over `efetch`. This is real evidence of why the course's per-module Limits sections matter: a limitation stated in Module 4 had a concrete, traceable downstream effect four modules later.
3. **The full Module 4→5→6→7→8 chain conserved correctly end to end** — `tracker.validate_conservation()` passed against genuinely real, live-derived counts, not a synthetic example.

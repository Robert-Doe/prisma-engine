# Module 22 — Decisions: Rapid Review Adapter

## Line-by-line / unit-by-unit

### `RapidReviewLog` exists at all, and every simplification is logged with standard practice + rapid practice + rationale, not just applied
**(b) Forced by external contract.** This is the actual, real discipline that separates a legitimate rapid review from a systematic review done sloppily (see Module 0's concept page on rapid review). A rapid review that quietly does less without saying so misleads its reader into thinking it's more rigorous than it is; disclosing exactly what was traded away and why is the real methodological requirement, not a nicety this module added for polish.

### The three simplifications chosen (single source, single reviewer, reduced checklist) directly mirror the ones Module 0's concept page named
**(c) Convention.** Module 0's `concept_rapid_review.html` specifically lists "single-reviewer screening," "restricted source list," and "simplified or omitted risk-of-bias scoring" as the typical real simplifications a rapid review makes. This module implements exactly those three, rather than inventing a different set, so the orientation module's claim and this module's actual behavior match.

### `REDUCED_RCT_CHECKLIST` is built from Module 11's own `ChecklistItem`/`Checklist` classes, reusing two of its five real `RCT_CHECKLIST` items verbatim
**(c) Convention.** Copying the exact `ChecklistItem` objects (same key, same question text) rather than writing new ones with similar wording means the reduced checklist really is a subset of the full one, not a separately-invented approximation of it — a reader comparing the two can see precisely which three domains were dropped.

### `run_rapid_review()` calls `search_pubmed` (Module 4/5) but never `fetch_arxiv`
**(c) Convention.** This is the literal implementation of the "single source instead of multiple" simplification — not a missing feature, a deliberate, logged choice consistent with what `RapidReviewLog` reports about the Identification stage.

### The demo explicitly explains why 0 records passed rapid screening, rather than leaving a bare "0" unexplained
**(b) Forced by external contract — the same honesty requirement from Module 8.** `DEFAULT_RULES`, reused unchanged from Module 8, excludes any record lacking an abstract, and PubMed's `esummary` (Module 4) never returns one. This module doesn't work around or hide that cascading real limitation; it names it directly, the same way Module 8's own tutorial did when the identical result first appeared.

### "Single-reviewer screening" is implemented as calling `screen()` once, not as two calls with a reconciliation step
**(c) Convention, and an honestly-stated scope limit.** A real dual-reviewer workflow needs two independent human screeners and a reconciliation process between them — genuinely out of scope for a single automated function. This module's log entry for the Screening stage says so explicitly ("not built until a real team workflow exists") rather than implying a simulated second reviewer exists when it doesn't.

## Decisions We Made

| Decision | Category |
|---|---|
| Every simplification logged with standard/rapid/rationale | (b) External contract (real rapid-review discipline) |
| The three simplifications match Module 0's own description | (c) Convention |
| Reduced checklist reuses Module 11's exact `ChecklistItem` objects | (c) Convention |
| Only `search_pubmed` called, `fetch_arxiv` skipped entirely | (c) Convention (the literal single-source simplification) |
| The 0-records result is explained, not left silent | (b) External contract (Module 8's honesty precedent) |
| Single-reviewer screening is one `screen()` call, log says so plainly | (c) Convention, honestly scoped |

## What We Proved

Running [`rapid_review.py`](rapid_review.py) demonstrated that Track 1's
engine can be legitimately compressed under a time constraint without
becoming dishonest about what got compressed:

1. **Every simplification this review made is traceable to a specific, named, justified decision** — not implied by a shorter runtime, but printed explicitly alongside exactly what standard practice it replaces.
2. **The reduced risk-of-bias checklist visibly omits real domains, and the demo says so out loud.** A study scoring "some concerns" under the 2-domain checklist has an unassessed selective-reporting risk that a full appraisal might have caught — the demo states this directly rather than letting a shorter checklist's output be mistaken for a complete appraisal.
3. **A real cascading limitation from Module 4/8 surfaced again here, and was explained again rather than hidden** — proof this module's reuse of Track 1's code is genuine (the same real constraint propagates through), not a superficial imitation that would have hidden the same problem.

# Module 21 — Decisions: Scoping Review Mapper

## Line-by-line / unit-by-unit

### PCC (Population, Concept, Context) is a new class, not a new member added to Module 1's `Framework` enum
**(a) Forced by the platform, discovered directly.** The natural-seeming approach was adding `PCC` as a fourth value to Module 1's `Framework(str, Enum)`. Python enums are not extensible after class definition — there is no supported way to add a member to an existing `Enum` subclass from outside its own module. Rather than modify Module 1's source (which Track 2 deliberately avoids doing, to keep Track 1 stable for anyone depending on it), this module defines its own parallel `PCCQuestion`/`MissingPCCSlotsError`, following the identical validated-slots *pattern* Module 1 established, without literally sharing its `Enum`.

### PCC, specifically, and not PICO
**(b) Forced by external contract.** PCC is the real question framework the JBI (Joanna Briggs Institute) methodology manual recommends specifically for scoping reviews — chosen because PICO's Intervention/Comparison slots presuppose an effect is being measured, which a scoping review doesn't do. Using PICO here would misrepresent the actual, real methodological convention for this review type.

### `build_widened_query()` includes every slot with supplied terms, not a narrowed default subset
**(c) Convention, directly reversing Module 2's own default.** Module 2's `DEFAULT_SEARCH_SLOTS` deliberately excludes Comparison/Outcome from a systematic review's search, favoring sensitivity within a manageable volume. A scoping review's entire goal is breadth — deliberately narrowing the search here would work against the review type's own purpose. This function calls Module 2's `build_or_group()` directly (real reuse) but skips `build_query()`'s slot-narrowing logic entirely, by design.

### Risk-of-bias appraisal (Module 11) is never called anywhere in this module
**(b) Forced by external contract.** This is real, standard scoping-review methodology, not a shortcut: JBI and PRISMA-ScR guidance both state that formal quality/risk-of-bias appraisal is not a required (and often not an appropriate) component of a scoping review, since the goal is mapping what exists, not judging whether individual studies' conclusions can be trusted. Omitting Module 11 here isn't cutting a corner — including it would misrepresent what a scoping review actually is.

### The charting form (`CHARTING_SCHEMA`) reuses Module 10's `ExtractionField`/`ExtractionSchema` classes unmodified
**(c) Convention.** A scoping review's charting form and a systematic review's data-extraction form are structurally identical ideas — a validated set of fields applied consistently across studies — even though what they capture differs completely (study characteristics for breadth-mapping vs. quantitative findings for synthesis). Reusing Module 10's actual classes, just with a different field set, proves that structural claim rather than asserting it.

### `summarize_breadth()` is new code, not a reuse of anything from Track 1
**(c) Convention.** Nothing in Track 1 needed to answer "how many charted records fall into each category" — Track 1's tables feed into effect-size pooling (Module 16), not category tallying. This is a genuinely new kind of output, appropriately built new rather than forced into an existing shape that doesn't fit.

## Decisions We Made

| Decision | Category |
|---|---|
| PCC as a new class, not a `Framework` enum member | (a) Forced by platform (Python enums aren't extensible) |
| PCC specifically, matching JBI methodology | (b) External contract |
| Search widened, reversing Module 2's default narrowing | (c) Convention, directly opposing Module 2's own default |
| Module 11 (risk-of-bias) never called | (b) External contract (real scoping-review methodology) |
| Charting form reuses Module 10's classes unmodified | (c) Convention |
| `summarize_breadth()` is genuinely new code | (c) Convention |

## What We Proved

Running [`scoping_mapper.py`](scoping_mapper.py) demonstrated that Track 1's
engine generalizes to a genuinely different review type, not just a
relabeled systematic review:

1. **The same search-building code produces a deliberately different search shape for a different purpose** — Module 2's `build_or_group()` reused directly, but assembled to maximize breadth instead of Module 2's own default sensitivity/volume tradeoff.
2. **Screening happened with no design or date filtering, and no quality appraisal step exists anywhere in this module** — a real, verifiable absence (Module 11 is never imported), not an oversight.
3. **The final output is a breadth map, not a pooled effect** — `summarize_breadth()` answered "what exists" (2 knowledge-worker studies, split across survey/qualitative designs and two topic areas) in a shape a systematic review's pipeline has no equivalent for, proving this is a structurally different deliverable, not the same one with a new name.

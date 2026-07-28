# Module 15 — Decisions: Thematic Coding Engine

## Line-by-line / unit-by-unit

### Two separate functions, `open_code()` then `axial_code()`, not one combined step
**(b) Forced by external contract.** This is the real two-stage structure grounded theory methodology (Strauss & Corbin) uses: open coding assigns descriptive labels to raw data first, bottom-up, before any higher-level structure is imposed; axial coding relates those already-assigned codes to each other into categories afterward. Collapsing the two into one step would misrepresent the actual method — the whole point of doing open coding first is that the codes exist before you decide how they relate.

### Open coding uses keyword-trigger rules, not an ML classifier
**(c) Convention — same honesty principle as Module 1.** Automatically inferring qualitative codes from arbitrary text is a genuinely hard, contestable interpretive act in real qualitative research — normally done by a trained human coder, often two independently, who then reconcile disagreements. A trigger-phrase heuristic is transparent and auditable (you can see exactly why an excerpt got a code) in a way an opaque classifier wouldn't be, which matters more for a teaching module than raw accuracy would.

### An excerpt can receive zero, one, or multiple open codes
**(c) Convention.** Forcing every excerpt into at least one code would misrepresent excerpts that are genuinely off-topic (like "Interview P6" in the demo, matching nothing) as if they carried some meaning they don't. Allowing multiple codes reflects reality too — real qualitative excerpts frequently touch more than one idea in the same sentence, confirmed in the self-checks' "S5" example, which legitimately carries both `blurred_boundaries` and `social_isolation`.

### `axial_code()` lets the same excerpt appear under multiple themes
**(c) Convention, and a direct consequence of the previous decision.** If an excerpt carries codes belonging to two different themes, hiding it under only one theme would throw away real information about how that excerpt actually relates to the coding scheme. The self-checks confirm this directly: the dual-coded "S5" excerpt appears in both `themed["Disrupted Social Connection"]` and `themed["Changed Work Rhythm"]`.

### `CODING_RULES` and `THEME_GROUPINGS` are this module's own example scheme, not a universal standard
**(c) Convention.** Unlike PICO's slot names or RIS's field tags, there's no external authority defining "the correct" codes or themes for a set of interview excerpts — a real qualitative researcher develops their own coding scheme from their own data, which is exactly what these two dictionaries stand in for as a worked, inspectable example.

### `open_code()` and `axial_code()` take the coding scheme as an explicit parameter, not a hardcoded default
**(c) Convention.** Both functions work identically for any coding scheme a caller supplies — nothing about their logic assumes remote-work-specific content. `CODING_RULES`/`THEME_GROUPINGS` are example arguments used by the demo, not baked into the functions themselves.

## Decisions We Made

| Decision | Category |
|---|---|
| Two separate functions matching real open/axial coding structure | (b) External contract (grounded theory methodology) |
| Keyword-trigger rules, not an ML classifier | (c) Convention (transparency over raw accuracy) |
| An excerpt can carry zero, one, or many codes | (c) Convention |
| An excerpt can appear under multiple themes | (c) Convention |
| Example coding scheme is this module's own, not a standard | (c) Convention |
| Coding scheme passed as an explicit parameter | (c) Convention |

## What We Proved

Running [`thematic_coding.py`](thematic_coding.py) demonstrated the exact
claim this module exists to prove:

1. **Coding is a structured, repeatable process, not a vibe.** Every code assignment traces back to a specific, inspectable trigger phrase — re-running the exact same excerpts through the exact same rules produces the exact same codes every time, which is what "structured and repeatable" concretely means.
2. **An excerpt genuinely off-topic to the coding scheme was correctly left uncoded**, not forced into a theme it doesn't belong to — "Honestly my day is about the same as it was in the office" matched none of the three trigger sets and was reported separately, exactly as a careful human coder should treat a non-matching excerpt.
3. **A dual-themed excerpt was correctly represented under both themes it belongs to**, not arbitrarily assigned to just one — real evidence the axial coding step preserves genuine cross-cutting relationships in the data instead of forcing a false single categorization.

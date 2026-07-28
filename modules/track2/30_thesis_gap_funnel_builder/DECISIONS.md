# Module 30 — Decisions: Thesis Gap-to-Research-Question Funnel Builder

## Line-by-line / unit-by-unit

### The funnel's gap-identification step relies solely on `coverage()` (a count), not an attempt to detect "contested" themes too
**(c) Convention — a real design simplification, decided during development, not assumed from the start.** An earlier draft of this module also tried to detect "contested" themes (sources actively disagreeing) via a positive/negative keyword heuristic, the same style as Module 24's negation markers. Run against this module's own demo data, it found zero contested themes — the real disagreement in the data (self-reported outcomes trending positive, objectively measured outcomes trending negative) is a pattern *across* themes, not *within* any single theme, which that heuristic was never built to see. Rather than ship a heuristic that silently does nothing on its own worked example, this module keeps only the signal that demonstrably works — coverage count — and names the harder, unimplemented problem directly in the tutorial's Limits section instead of pretending to solve it.

### `formalize_thesis_question()` calls Module 1's real `formalize()`, unmodified, rather than building its own question-validation logic
**(c) Convention — deliberate narrative closure.** Nothing about Module 1's `formalize()` is specific to systematic reviews; it validates any PICO-shaped question against `FRAMEWORK_SLOTS`. Reusing it here, in this course's final content module, for a thesis research question is the same function, the same validation, the same `MissingSlotsError` safety net that opened this entire course twenty-nine modules earlier — proving Track 1's foundational pieces were genuinely reusable across the whole course, not just within Track 1 itself.

### The generated question text is built from a template (`f"Does {gap_theme} moderate..."`), not free-form
**(c) Convention, honestly scoped.** A real thesis research question requires a student's own judgment about phrasing and framing — this function cannot and does not claim to write a finished, publication-ready question. What it does is guarantee the template's output is a syntactically complete, PICO-structurable sentence that `formalize()` can then validate — a scaffold, not a replacement for the actual thinking.

### `identify_thin_themes()`'s default `threshold=1` is a parameter, not a hardcoded constant
**(c) Convention.** What counts as "thin" is a judgment call that depends on how many sources a given literature review actually has — a review with 50 sources per theme might reasonably call anything under 5 "thin," while this module's 3-source demo correctly treats a lone source as thin. Making it a parameter means the same function serves both cases without modification.

### The gap-statement text explicitly says it's "grounded in the synthesis matrix's own coverage count, not asserted from a general sense that more research is needed"
**(b) Forced by external contract.** This is a direct, real distinction thesis committees and reviewers actually care about: "more research is needed" is a cliché any thesis could claim about any topic; "only one of three identified themes has been addressed by more than one source, and here's the count" is a specific, checkable claim. The generated text is written to make that difference explicit, not just to sound more confident.

## Decisions We Made

| Decision | Category |
|---|---|
| Gap detection uses only coverage count, not a contested-theme heuristic that didn't work on real data | (c) Convention, decided after testing, not assumed |
| Reuses Module 1's real `formalize()` unmodified | (c) Convention (deliberate narrative and functional closure) |
| Question text is templated, not free-generated | (c) Convention, honestly scoped |
| `threshold` is a parameter, not hardcoded | (c) Convention |
| Gap statement explicitly names its own evidentiary basis | (b) External contract (real thesis-committee expectations) |

## What We Proved

Running [`gap_funnel.py`](gap_funnel.py) completed the exact narrowing
argument a thesis literature review chapter is supposed to make, and
closed the loop on this entire course:

1. **A specific, defensible gap was identified from a real, computed count, not a vague impression.** "Task-type dependence" was flagged because `coverage()` — reused directly from Module 29 — measured exactly 1 source addressing it, versus 2 for each other theme.
2. **The resulting research question is genuinely validated, not just generated.** `formalize_thesis_question()`'s output passes `rq.validate()` — every PICO slot Module 1 requires is filled, using the exact same validation this course's very first module built.
3. **A design change made mid-development is documented instead of hidden.** The original plan to also detect "contested" themes was tested, found not to fire on real demo data, and removed in favor of a narrower, honestly-scoped mechanism — the same discipline this course has applied every time a heuristic's real behavior didn't match its intended one.

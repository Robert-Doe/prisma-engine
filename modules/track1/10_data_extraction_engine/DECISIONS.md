# Module 10 — Decisions: Data Extraction Form Engine

## Line-by-line / unit-by-unit

### This module does not auto-extract data from free text with NLP
**(c) Convention — a deliberate scope boundary, stated in the ROADMAP.** The Tools/Architecture Target explicitly lists "ML/NLP-based screening classifiers" as out of scope, and the same reasoning applies here: reliably pulling a sample size or effect direction out of unstructured prose is a genuinely hard, error-prone NLP problem, not something a rule-based or lightly-heuristic tool can do trustworthily. This module instead proves a narrower, still-real claim — that a *validated schema* turns manually-entered data into something structured and checked, the same way a well-designed paper form (rather than a blank notepad) constrains what a human can enter incorrectly.

### `ExtractionField` bundles a Python type (`int`, `str`, ...) directly, not a custom type-tag system
**(c) Convention.** Using real Python types means `isinstance(value, f.field_type)` does the type check with no translation layer — simple, and sufficient for the flat, scalar fields (numbers, short strings) an extraction form actually needs. A schema needing richer types (nested objects, lists) would need a different design; this module's fields don't.

### `validator` is a separate, optional field from `field_type`
**(c) Convention.** Type correctness ("is this actually an int") and value correctness ("is this int actually positive," "is this string actually one of four allowed categories") are different failure modes with different fixes. Splitting them means a caller adding a new constraint (say, "sample size must be under 100,000") doesn't need to touch type-checking logic at all — just supply a new `validator`.

### `one_of(allowed: set)` is a validator *factory*, not a fixed list of validator functions
**(c) Convention.** `study_design` and `effect_direction` both need "must be one of these exact values" logic, but with different allowed sets. Writing `one_of({"RCT", "cohort", ...})` once and reusing the pattern is simpler than hand-writing a near-identical validator function per field — and it's exactly the same idea as Module 2's controlled vocabulary, applied to extraction values instead of search terms.

### `REMOTE_WORK_SCHEMA`'s controlled sets (`study_design`, `effect_direction`) are this module's own convention, not an external standard
**(c) Convention.** Unlike PICO/PEO/SPIDER's slot names (Module 1, forced by external published frameworks) or RIS/BibTeX/Crossref's field names (Module 3, forced by external formats), there's no single universal standard for what values an extraction form's `study_design` field must take. Real reviews define this per-protocol, tailored to their own research question — which is exactly what this schema demonstrates, not a claim that these four design categories are the only correct ones.

### `outcome_measure` is the only optional field in the example schema
**(c) Convention.** It's realistic, not arbitrary: plenty of real papers report a productivity effect without ever naming the specific instrument used to measure it, while sample size, design, effect direction, and comparison group are close to always statable from any paper that reports a comparative finding at all. Marking a field optional is itself a real, considered claim about what real papers typically report — not just a default.

## Decisions We Made

| Decision | Category |
|---|---|
| No NLP auto-extraction — schema validates human-entered data | (c) Convention (stated course scope boundary) |
| Real Python types used directly, no custom type-tag system | (c) Convention |
| Type-check and value-validator kept as separate concerns | (c) Convention |
| `one_of()` as a reusable validator factory | (c) Convention |
| Example schema's controlled sets are this module's own convention | (c) Convention (not an external standard) |
| Only `outcome_measure` marked optional | (c) Convention, grounded in realistic reporting patterns |

## What We Proved

Running [`extraction_engine.py`](extraction_engine.py) demonstrated both
halves of the claim — that a schema makes good data structured, and bad
data gets caught, not silently accepted:

1. **A correctly-filled extraction validated and produced clean, structured data** — five named fields, typed and constrained, ready to sit in a comparable row of a future evidence table (Module 14).
2. **Three distinct real failure modes were each caught with a specific, correct error** — a missing required field, a wrong type (a string where an int was required), and a value outside the schema's controlled set — proving the schema actually constrains what "extracted data" can mean, rather than accepting whatever a reviewer happened to type.

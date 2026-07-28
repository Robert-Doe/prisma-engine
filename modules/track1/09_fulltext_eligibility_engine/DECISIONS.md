# Module 9 — Decisions: Full-Text Eligibility Engine

## Line-by-line / unit-by-unit

### Full text is supplied as a plain string, not fetched from a PDF
**(b) Forced by external contract — the course's own stated scope.** The ROADMAP's Tools/Architecture Target explicitly commits to "full-text modules operate on open-access text or user-supplied text" and lists paywalled full-text retrieval as out of scope. PDF parsing (layout extraction, OCR for scanned documents, paywall/access handling) is a substantial, genuinely separate problem from eligibility-rule logic — bundling it into this module would obscure the actual lesson under a much bigger, unrelated one.

### The demo uses three clearly fictional records, not full text attached to Modules 4-5's real fetched papers
**(c) Convention — an honesty requirement.** Modules 4 and 5 fetch real titles, abstracts, and metadata from live APIs. This course has no access to those real papers' actual full text. Inventing plausible-sounding "full text" and attaching it to a real paper's real title and real author names would misrepresent what that real paper actually says — a direct violation of this course's own quality bar. Using clearly fictional example records (in the same style as the running Smith/2023 example from earlier modules) keeps the demonstration honest about what is and isn't real data.

### `EligibilityRule` and `EligibilityResult` are new types, not direct reuses of Module 8's `ScreeningRule`/`ScreeningResult`
**(c) Convention.** The predicate signature is genuinely different — Module 8's rules inspect a `Record` directly; this module's rules need both the `Record` and its associated full text, hence `FullTextRecord`. Reusing Module 8's types would require either awkwardly stuffing full text onto the `Record` model itself (polluting Module 3's canonical shape with a field only this one stage needs) or accepting a type mismatch. New, purpose-built types are the more honest option; the two modules still share the identical *shape of logic* (ordered rules, first-failure-wins, `excluded_by_reason()`), deliberately mirroring Module 8's design.

### `design_is_comparative()` only fails when interview language appears *without* any comparative marker
**(c) Convention.** A study can legitimately mention interviews as a secondary component of an otherwise comparative, quantitative design — the rule is written to catch "qualitative-only," not "used interviews at all." This is why it checks for the *absence* of comparative markers, not merely the presence of interview language.

### Rule order (population check before design check)
**(c) Convention.** Mirrors Module 8's ordering rationale: population is checked first because it's the more fundamental eligibility question (is this even the right kind of subject at all) — a design problem is somewhat beside the point if the population is wrong entirely. Verified directly in the self-checks: a record with both problems ("D") is reported with the population reason, never the design reason.

## Decisions We Made

| Decision | Category |
|---|---|
| Full text is user-supplied, not fetched from PDFs | (b) External contract (course's own stated scope) |
| Demo uses fictional records, not real papers with invented full text | (c) Convention (honesty requirement) |
| New `EligibilityRule`/`EligibilityResult` types, mirroring Module 8's shape | (c) Convention |
| Design rule fails only on qualitative-only language, not any interview mention | (c) Convention |
| Population checked before design | (c) Convention |

## What We Proved

Running [`fulltext_engine.py`](fulltext_engine.py) demonstrated the exact
claim this module exists to prove:

1. **All three example records would have passed a title/abstract screen** — every abstract is on-topic and plausible. This isn't asserted, it's evident from reading them: nothing in any abstract signals disqualification.
2. **Full text caught what the abstract couldn't.** Record "A"'s abstract doesn't mention its actual interview-only methodology; record "B"'s abstract doesn't reveal its actual undergraduate population. Both details only appear in the (simulated) methods section — exactly the kind of detail real abstracts routinely omit or gloss over.
3. **The two-pass structure produces a stricter, more accurate included set** (1 of 3) than a title/abstract-only pass would have (3 of 3) — a concrete, computed demonstration of why systematic reviews require a second, full-text eligibility stage at all, not just an assertion that they should.

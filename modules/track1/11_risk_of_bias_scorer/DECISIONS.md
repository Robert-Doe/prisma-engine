# Module 11 — Decisions: Risk-of-Bias / Quality Appraisal Scorer

## Line-by-line / unit-by-unit

### Checklists are branched by study design (`RCT_CHECKLIST`, `COHORT_CHECKLIST`, `QUALITATIVE_CHECKLIST`)
**(b) Forced by external contract.** This is the direct implementation of Prerequisite 4's point: "blinding" is a meaningless question for an interview study, and "clear statement of research aims" is not what an RCT's risk of bias hinges on. Real appraisal tools (Cochrane RoB2 for RCTs, CASP's separate checklists per study type) are themselves organized this way — a single one-size-fits-all checklist would be methodologically wrong, not just less convenient.

### The checklist items are simplified/condensed, not verbatim reproductions of Cochrane RoB2 or CASP
**(c) Convention, honestly labeled.** The real Cochrane RoB2 tool uses a much larger set of detailed signalling questions per domain, arrived at algorithmically; CASP's checklists have around 10 questions each with detailed guidance notes. Reproducing either in full is a substantial undertaking orthogonal to this module's teaching goal — demonstrating checklist-based, branched, systematic appraisal. The module docstring and this file say explicitly that these are condensed, inspired-by versions, not the real tools, so nobody mistakes this module's output for a validated instrument's output.

### Scoring uses a simple weighted average (`yes=1.0, unclear=0.5, no=0.0`), not Cochrane RoB2's actual algorithm
**(c) Convention — and a documented, real methodological weakness, not a hidden one.** The real Cochrane RoB2 tool deliberately does NOT reduce a study to one summary score. It reaches a domain-level judgment per domain, then an *overall* judgment driven by the **worst** domain, specifically because averaging can hide a single serious flaw behind several strong domains. This module's own self-checks demonstrate that exact failure mode on purpose: a study with four "yes" domains and one "no" (missing blinding — a genuinely serious RCT flaw) still averages to `0.80`, clearing this module's own "low risk" threshold. That's not a bug in this module's numbers — it's live proof of why real appraisal tools reject simple averaging.

### `AppraisalResult` always reports `lowest_scoring_item` alongside the averaged proportion
**(c) Convention, direct mitigation for the averaging weakness above.** Since this module keeps the average (for its simplicity as a teaching tool) but knows that average can hide a serious single-domain problem, it always surfaces which specific domain scored worst — so a human reading the result isn't limited to the potentially-misleading summary number alone.

### Answers are validated against a fixed three-value set (`yes` / `unclear` / `no`), not free text
**(c) Convention.** Real appraisal tools constrain responses to a small fixed vocabulary for exactly the reason Module 10's `one_of()` validator exists — free-text answers like "mostly yes" or "probably" can't be scored consistently or compared across studies.

## Decisions We Made

| Decision | Category |
|---|---|
| Checklists branch by study design | (b) External contract (real appraisal tools are organized this way) |
| Checklist items are condensed, explicitly not verbatim Cochrane/CASP | (c) Convention, honestly labeled |
| Scoring uses simple weighted averaging | (c) Convention — and a deliberately surfaced real weakness |
| `lowest_scoring_item` always reported alongside the average | (c) Convention (mitigates the averaging weakness) |
| Answers constrained to `{yes, unclear, no}` | (c) Convention |

## What We Proved

Running [`rob_scorer.py`](rob_scorer.py) demonstrated both the intended
claim and an important, honestly-surfaced limitation:

1. **Study quality can be quantified via a checklist rather than asserted by feel** — every appraisal in this module traces back to specific, answered questions, not a vague "this seemed like a solid study" judgment.
2. **Different study designs are correctly evaluated against different questions** — an RCT and a qualitative study never share a checklist, confirmed by branching on `CHECKLISTS_BY_DESIGN`.
3. **The averaging approach's real, known weakness was demonstrated concretely, not just described.** A study with a serious, specific flaw (no blinding at all) still scored `0.80` — "low risk" by this module's own threshold — precisely the failure mode that led the real Cochrane RoB2 tool to reject simple summary scoring in favor of worst-domain-driven judgments. Surfacing this honestly, with a real computed number, is worth more than a checklist that quietly implied its own scoring method was authoritative.

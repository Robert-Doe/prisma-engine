# Module 25 — Decisions: Umbrella Review Aggregator

## Line-by-line / unit-by-unit

### `AMSTAR_LITE_CHECKLIST` is built from Module 11's exact `Checklist`/`ChecklistItem` classes, with review-level questions instead of study-level ones
**(c) Convention, following the same reuse pattern Module 22 established.** Module 22 already proved a *reduced* checklist (fewer items) could reuse Module 11's classes unmodified. This module proves the same classes generalize a second way: not just fewer items, but items about a completely different unit of analysis (a systematic review's own conduct, not a primary study's design). The real AMSTAR-2 instrument (the actual, much more detailed 16-item tool for appraising systematic reviews) is the methodological anchor for what these simplified questions represent — see the tutorial for the explicit "not the real AMSTAR-2" disclosure, consistent with Module 11's own honesty about not being the real Cochrane RoB2.

### `compute_overlap()` and `total_unique_primary_studies()` exist as this module's actual point
**(b) Forced by external contract.** Overlapping primary studies across included reviews is a well-documented, real methodological hazard specific to umbrella reviews — the same primary study can appear in multiple included systematic reviews on related topics, and naively treating each included review's evidence as independent silently inflates how much real, independent evidence exists. This isn't a hypothetical edge case; it's the reason real umbrella-review guidance (e.g. the "corrected covered area" concept in overlap literature) exists at all. This module implements a simpler, direct version of the same idea: exact set overlap, not the more sophisticated corrected-covered-area formula.

### `total_unique_primary_studies()` deduplicates via set union, not by summing each review's count
**(c) Convention, and the module's central proof.** The demo makes this concrete with real numbers: summing each review's own primary-study count gives 10; the deduplicated real evidence base is 8. That 2-study gap is not a rounding error — it's exactly the double-counted studies "Systematic Review A" and "Systematic Review B" both happened to include, made visible by the one line of code (`all_dois |= r.primary_study_dois`) that a naive sum would skip entirely.

### Overlap is reported per pair, as both a raw shared count and a percentage of the pair's combined union
**(c) Convention.** A raw count alone (`2 shared studies`) doesn't communicate how significant that overlap is — 2 shared out of 3 total studies is a very different situation from 2 shared out of 30. Dividing by the union size (Jaccard-style) gives a normalized number that's comparable across review pairs of very different sizes.

### The demo's three fictional reviews are deliberately given different appraisal answers, producing genuinely different bands (two "low risk," one "high risk")
**(c) Convention.** A demo where every review appraised identically would fail to show that the checklist is actually discriminating between real differences in conduct — Review B's answers (`protocol_registered: no`, `duplicate_screening: no`, `funding_disclosed: no`) were chosen to produce a real, different, worse-appraised result, not to make every review look equally good.

## Decisions We Made

| Decision | Category |
|---|---|
| Review-level checklist reuses Module 11's classes, different questions | (c) Convention, extending Module 22's reuse pattern |
| Overlap detection is this module's actual point, not an add-on | (b) External contract (real umbrella-review hazard) |
| Deduplication via set union, not summed counts | (c) Convention (the module's central proof) |
| Overlap reported as count + normalized percentage | (c) Convention |
| Three reviews given genuinely different appraisal answers | (c) Convention (discriminating demo, not a uniform one) |

## What We Proved

Running [`umbrella_review.py`](umbrella_review.py) demonstrated the two
things a real umbrella review actually has to get right:

1. **Reviews, not primary studies, were appraised — using the exact same appraisal machinery Track 1 built for primary studies**, just pointed at a different unit of analysis and asking different questions. Module 11's `Checklist`/`ChecklistItem`/`score_checklist` needed zero modification to do this.
2. **A real, quantified double-counting hazard was caught, not just described.** Naively summing each review's primary-study count gave 10; the actual deduplicated evidence base is 8 — a real 20% inflation that a careless umbrella review aggregating "10 studies of evidence" would have silently overstated. `compute_overlap()` further pinpoints exactly which pair of reviews caused it (Systematic Review A and B, sharing 2 studies), giving a real, actionable audit trail rather than just a corrected total.

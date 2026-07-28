# Cross-Module Concept Clusters

Phase 3 of this course's construction: concepts that span more than one
module and don't belong entirely to any single one of them, built as
standalone `lessons/NN_cluster_name/` folders once enough modules existed
to make the cross-cutting pattern visible.

Each cluster's `01_explainer.html` is written in the same tutorial style
as a module page but is topic-scoped, not module-scoped, and each
numbered `*_deepdive.html` covers one facet in more depth than any single
module's own code motivates.

---

## 01 — Deduplication & Identity Matching

**Folder:** [`01_deduplication_identity_matching/`](01_deduplication_identity_matching/01_explainer.html)

**Relates to:** Module 3 (format normalization sidesteps matching entirely),
Module 6 (the fullest implementation — exact + fuzzy, two-pass), Modules 13
and 23 (reuse Module 6's `normalize_doi()` in a citation-graph context),
Module 26 (reuses it again, persisted across time), and Module 25 (does
**not** reuse it — a real, documented gap only visible by comparison).

**Why it lives centrally:** No single module owns "how do you decide two
things are the same." Module 6 has the deepest implementation, but the
pattern's actual value — and its one real gap — only becomes visible by
reading several modules' independent answers to the same question side by
side. A reader of Module 6 alone would never learn that Module 25 skipped
the same safeguard.

## 02 — Statistical Pooling

**Folder:** [`02_statistical_pooling/`](02_statistical_pooling/01_explainer.html)

**Relates to:** Module 16 (effect sizes), Module 17 (pooling + heterogeneity),
Module 18 (visualizing Module 17's output), and Module 19 (checking whether
the pooled evidence base is itself biased).

**Why it lives centrally:** Each module is individually a real, working
piece of statistics — but the reason the fixed-vs-random-effects choice is
*consequential*, not just a technical option, only shows up when Module
17's actual numbers (a result that's "significant" under one model and
"not significant" under the other, from the identical five studies) are
read as one continuous argument spanning three modules, not three
disconnected demos.

## 03 — Heuristic Text Classification & Its Limits

**Folder:** [`03_heuristic_text_classification/`](03_heuristic_text_classification/01_explainer.html)

**Relates to:** Modules 1, 8, 9, 15, 21, 24, 27, and 28 — every module in
this course that classifies text by checking for keyword presence.

**Why it lives centrally:** This is the strongest case in the whole course
for a concept cluster. The exact same failure mode (negation-blindness)
was independently discovered twice — once in Module 24, once in Module 28
— by two different functions, in two different modules, built at
different points in this course's construction, with no shared code
between them. That recurrence is only visible by comparing modules that
are otherwise unrelated (a qualitative-synthesis module and a citation-
comparison module have nothing else in common); no single module's own
DECISIONS.md can make the claim this cluster makes, that the failure is
structural to the technique, not a one-off quirk of one word list.

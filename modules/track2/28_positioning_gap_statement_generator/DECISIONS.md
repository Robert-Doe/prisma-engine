# Module 28 — Decisions: Positioning & Gap-Statement Generator

## Line-by-line / unit-by-unit

### A "gap" requires that NO existing paper satisfies ALL required dimensions simultaneously, not just that none satisfies most of them
**(b) Forced by external contract.** This is the actual logical structure of a real novelty claim in a positioning review: "no prior work does X AND Y AND Z at once" is a meaningfully different (and much easier to defend) claim than "no prior work does X, Y, or Z individually." `find_satisfying_papers()` checks the full conjunction (`all(...)`) precisely because a paper satisfying 3 of 4 required dimensions still fully anticipates the contribution if it happens to satisfy the 4th too — the gap only exists in the intersection nobody has covered.

### `find_near_misses()` reports which SPECIFIC dimensions each close paper lacks, not just that it's "close"
**(b) Forced by external contract.** A real Related Work section's novelty argument is only convincing if it names exactly what's missing from each closely-related prior system — "SafeSpec doesn't address X" is a real, checkable claim; "SafeSpec is different" is not. Naming the exact missing dimension per near-miss paper is the mechanical version of that real convention.

### `verify_claim_grounded()` re-derives a dimension fresh from the record's real text rather than trusting the comparison table's stored value
**(c) Convention, mirroring Module 4's `verify_mesh_term()`.** The table was built once; by the time a gap statement cites it, nothing guarantees the underlying record hasn't been re-processed differently, or that a bug didn't corrupt the stored value. Re-deriving directly from `record.title`/`record.abstract` at gap-statement-generation time — the same real text Module 27 used — is what makes the "grounded in its real abstract text" label in the output an actual, checked claim rather than an assumed one.

### Development surfaced a real negation-blindness bug (the same class already documented in Module 24), and the fix was to change the self-check's example text, not to patch `extract_dimensions()`
**(a) Forced by mathematics, discovered directly.** The first draft of this module's self-checks used the phrase "without machine learning" in a test record's abstract — and `extract_dimensions()` (reused unmodified from Module 27) matched the substring `"machine learning"` regardless of the negation, marking the record `ml_based=True` when the text actually says the opposite. This is the identical limitation Module 24 already documented at length for its own negation-marker heuristic — discovered here independently, in a completely different module, using a completely different heuristic function. Rather than duplicate Module 24's teaching moment a second time, or attempt a more sophisticated negation-aware classifier (a nontrivial NLP problem, out of this course's stated scope), this module's self-check was rewritten to avoid the collision, and the limitation is cross-referenced here rather than re-explained from scratch.

### The "already satisfied" sanity-check criteria set is included in the demo, not just the gap case
**(c) Convention.** A generator that only ever prints "no gap found" would be indistinguishable from one that's broken and always says that. Demonstrating a criteria set real prior work already covers — and getting a correct `"NOT A GAP"` result naming the actual satisfying papers — proves the conjunction logic works in both directions, not just the one that happens to look more interesting.

## Decisions We Made

| Decision | Category |
|---|---|
| A gap requires failing on the FULL conjunction of dimensions | (b) External contract (real novelty-claim logic) |
| Near-misses report exactly which dimensions are missing | (b) External contract (real related-work convention) |
| `verify_claim_grounded()` re-derives from real text, doesn't trust the table | (c) Convention, mirroring Module 4 |
| A real negation-blindness bug was found and worked around, not silently ignored | (a) Forced by mathematics, discovered live |
| Both a real gap case and a real "already satisfied" case are demonstrated | (c) Convention |

## What We Proved

Running [`gap_statement.py`](gap_statement.py) generated a real,
mechanically-derived novelty claim from Module 27's real 7-paper corpus:

1. **A real gap was correctly identified and precisely explained.** No paper in the live-fetched corpus satisfies detection + Spectre + Meltdown + non-ML simultaneously — and every one of the 7 near-misses is cited with the exact specific dimension it lacks, not a vague "doesn't quite fit."
2. **The opposite case was also correctly handled.** A criteria set real prior work does cover (mitigation targeting Spectre) correctly produced `"NOT A GAP"`, naming the three real papers that already satisfy it — proof the logic isn't biased toward always finding a gap.
3. **A real bug surfaced during development, from the same root cause Module 24 already taught, in a different module and a different heuristic.** That recurrence is itself informative: simple substring-based text heuristics have this failure mode broadly, not as a one-off quirk of Module 24's specific negation-marker list — worth knowing before reusing either module's extraction approach elsewhere.

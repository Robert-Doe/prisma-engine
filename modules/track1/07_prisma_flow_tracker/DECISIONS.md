# Module 7 — Decisions: PRISMA Flow Tracker

## Line-by-line / unit-by-unit

### `identification` is a dict keyed by source, not a single total
**(b) Forced by external contract.** PRISMA 2020's flow diagram explicitly requires reporting how many records came from each database/register separately, not just a combined total — a reader needs to be able to judge whether the search actually covered the sources it claims to.

### `validate_conservation()` checks that a stage's outputs sum exactly back to its inputs
**(c) Convention — the central mechanism of this module.** Nothing forces a tracker to check its own arithmetic; a tracker that just records whatever numbers it's given, without ever cross-checking them, would still compile and run. The whole value of this module is refusing to trust that logged numbers are self-consistent, and instead proving it — or catching it when they aren't, which is the demonstrated failure case in the demo (an 8-record stage where only 7 records were accounted for after screening).

### `screening_included` and `eligibility_included` default to `None`, not `0`
**(c) Convention.** `0` would be indistinguishable from "zero records passed screening" (a real, meaningful outcome). `None` unambiguously means "this stage hasn't been logged yet," which is what `validate_conservation()` actually needs to know to decide whether that stage's check even applies.

### `log_eligibility()` before `log_screening()` raises `FlowConservationError`, not a different exception type
**(c) Convention.** Both "the numbers don't add up" and "the stages were logged out of order" are the same underlying problem from this module's perspective: the flow's state doesn't yet support a trustworthy conservation check. Splitting them into different exception types would ask a caller to handle two errors that call for the identical fix (log stages in pipeline order).

### The demo chains real output from Modules 4, 5, and 6, and only simulates screening
**(c) Convention.** Modules 8 and 9 (the real screening/eligibility engines) don't exist yet in this course's build order. Rather than inventing a fake "identification" stage too, this module's demo uses genuinely real, live-fetched, live-deduplicated counts for every stage that already has a real upstream module, and is explicit in its own printed output about which stage is synthetic and why.

### The demo's synthetic screening split (`n // 3`, `n // 4`) is deliberately simple integer arithmetic
**(c) Convention.** It exists only to produce plausible, clearly-labeled placeholder numbers for a stage this module doesn't implement — not to model anything about real screening decision rates, which is exactly what Module 8 will actually implement for real.

## Decisions We Made

| Decision | Category |
|---|---|
| `identification` tracked per-source | (b) External contract (PRISMA 2020 reporting requirement) |
| `validate_conservation()` exists at all | (c) Convention (the module's core value) |
| `None` (not `0`) as the "not yet logged" sentinel | (c) Convention |
| One exception type for both imbalance and out-of-order logging | (c) Convention |
| Demo reuses real Modules 4-6, simulates only what's not built yet | (c) Convention |
| Synthetic screening split is simple placeholder arithmetic | (c) Convention |

## What We Proved

Running [`flow_tracker.py`](flow_tracker.py) chained real output from three
already-built, already-verified modules — a live PubMed search (Module 4),
a live arXiv search merged with it (Module 5), and real deduplication
(Module 6) — into this tracker, then:

1. **`validate_conservation()` passed on real, correctly-flowing data** — 10 records identified, 0 duplicates removed (this run), 10 entered screening, 3+2 excluded plus 5 passed, 10 accounted for exactly.
2. **The exact same check caught a deliberately broken example** — an 8-record stage where only 7 were accounted for after screening raised `FlowConservationError` naming the precise mismatch (`8 entered but 7 accounted for`), not a generic failure.
3. **A full, real PRISMA-shaped count summary was rendered** from actual pipeline state — per-source identification counts, deduplication counts, and screening counts with named exclusion reasons — which is precisely the accounting PRISMA reporting requires and Module 12 will turn into an actual diagram.

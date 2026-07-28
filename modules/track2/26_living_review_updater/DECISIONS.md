# Module 26 — Decisions: Living Review Updater

## Line-by-line / unit-by-unit

### State is persisted as plain JSON, not a database
**(c) Convention, driven by (b) the course's architecture target.** The ROADMAP commits to flat JSON/SQLite for persistence, dependency-light on purpose. A living review's state — a version number, a timestamp, a set of seen DOIs, a running included count — is exactly the kind of small, simple, human-readable state JSON is built for; no query engine is needed for state this shape.

### `run_update()`'s Module 7 tracker logs `len(new_records)` as "identified," not `len(records)` (the full fetch count) — discovered as a real bug, not designed correctly the first time
**(a) Forced by mathematics, discovered via a real crash.** The first version of this function logged the full fetch count as "identified," while only ever running dedup/screening on the *new* subset. On the demo's second update call — where every fetched record had already been seen in version 1 — this produced a real `FlowConservationError`: "5 entered but 0 accounted for." The mismatch was real and mechanically correct to catch: records filtered out for being already-seen were never entered into this update's dedup/screening pipeline at all, so counting them as "identified this cycle" was simply wrong bookkeeping. The fix — log `len(new_records)`, not `len(records)` — is a direct, permanent record of Module 7's conservation check doing exactly the job it was built for four Track 2 modules after it was originally written.

### Records with no DOI are always reprocessed on every update, never treated as "seen"
**(c) Convention, honestly stated as a real limitation.** `seen_dois` can only track identity for records that have a DOI at all. A record Module 4 returns with no DOI has no stable identifier this module can check against prior state — it's counted every single update, whether or not it was actually already screened in an earlier version. `records_without_doi_always_reprocessed` in `UpdateReport` surfaces this directly rather than silently under- or over-counting.

### The demo deletes any pre-existing state file before running, then calls `run_update()` twice in the same process
**(c) Convention.** Starting from a guaranteed-clean slate makes "version 1 finds everything new" a reliably true statement to demonstrate, rather than depending on whatever state happened to be left over from a previous run of this file. Calling `run_update()` twice, moments apart, in the same demo is what makes "version 2 finds (almost) nothing new" a real, live-verified claim rather than a description of intended behavior — the two live PubMed searches genuinely returned the same records, and the second call's diff against the first call's saved state genuinely found the overlap.

### `UpdateReport` reports `cumulative_included_count`, tracked in the persisted state itself, not recomputed by re-screening everything from scratch each version
**(b) Forced by external contract.** This is the entire point of a living review's incremental design: re-screening the full historical corpus on every update would defeat the purpose of an incremental system. Accumulating the count in `LivingReviewState` and only adding each update's *new* included count is what makes this genuinely incremental rather than a full re-run that happens to also save a timestamp.

## Decisions We Made

| Decision | Category |
|---|---|
| Plain JSON persistence, no database | (c) Convention, driven by (b) architecture target |
| Identification count fixed to track only new records | (a) Forced by mathematics — a real bug, caught and fixed |
| No-DOI records always reprocessed, reported explicitly | (c) Convention (honest limitation) |
| Demo clears state first, then runs update() twice for real | (c) Convention |
| Cumulative count accumulated in state, not recomputed | (b) External contract (the actual point of "incremental") |

## What We Proved

Running [`living_review.py`](living_review.py) demonstrated genuine
incremental behavior across two real, live update cycles — and along the
way, caught a real bug in its own first draft:

1. **Module 7's conservation check caught a real bookkeeping error during this module's own development** — logging the wrong count as "identified" produced an actual `FlowConservationError`, not a hypothetical one, four modules after Module 7 was originally built. This is direct evidence Module 7's validation logic generalizes to catch mistakes its original author never anticipated.
2. **State genuinely persisted between two separate function calls.** Version 1 found 5 new records (correct, from an empty state); version 2, run moments later against the same live PubMed data, correctly found 0 new records — proof `seen_dois` was actually read back from disk and compared, not just conceptually described.
3. **The system stayed honest about what it can't track.** Records with no DOI are explicitly reported as always-reprocessed rather than silently mishandled, consistent with every other module in this course that has hit a real data-completeness limit (Module 4's missing abstracts, Module 9's full-text scope) and said so directly instead of hiding it.

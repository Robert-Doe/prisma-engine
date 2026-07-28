# Module 6 — Decisions: Deduplication Engine

## Line-by-line / unit-by-unit

### Two passes, in this order: exact DOI first, fuzzy title second
**(c) Convention, strongly motivated by cost and certainty.** DOI comparison is O(1) per record (a dict lookup) and unambiguous — two matching normalized DOIs really are the same paper, full stop. Fuzzy title comparison is O(n²) in the worst case and probabilistic — a threshold call, not a certainty. Running the cheap, certain pass first shrinks the corpus the expensive, uncertain pass has to work over, and prevents an obviously-certain match from ever being subjected to a fuzzy score in the first place.

### `normalize_doi()` strips only the `http(s)://(dx.)?doi.org/` prefix, not any arbitrary host
**(b) Forced by external contract.** DOIs are formally case-insensitive per the DOI Handbook specification — `10.1037/XYZ` and `10.1037/xyz` are the same identifier. The `doi.org` resolver prefix is the one standard way a DOI gets embedded in a URL; stripping exactly that (and no more) avoids accidentally treating two different identifiers as equal just because they both happen to start with some other shared substring.

### `title_similarity()` uses `difflib.SequenceMatcher`, not a third-party fuzzy-matching library
**(c) Convention, driven by (b) the course's architecture target.** `SequenceMatcher` is standard library, needs no install step, and its ratio (Gestalt pattern matching, roughly "fraction of matching characters in the longest common subsequences") is more than adequate for the near-duplicate cases this module targets — near-identical titles differing only in punctuation, capitalization, or a subtitle separator. A dedicated library (e.g. `rapidfuzz`) would offer more algorithms (Levenshtein, Jaro-Winkler) and better performance at scale, at the cost of a dependency this module doesn't need to justify yet.

### `normalize_title()` strips punctuation and collapses whitespace before comparing
**(c) Convention.** This is precisely what makes `"...Study: A Longitudinal..."` and `"...Study - A Longitudinal..."` compare as identical (verified: `title_similarity()` returns exactly `1.0` for that real pair) — the punctuation difference is noise for the purpose of detecting the same paper, not signal.

### `author_overlap()` compares last-name sets via Jaccard, and returns `0.0` if either side has no authors
**(c) Convention.** Requiring name-format-agnostic matching is necessary because sources disagree on shape — Module 3's RIS/BibTeX/Crossref parsers produce `"Smith, Jane"`, Module 4's PubMed parser produces `"Smith J"`. Splitting on the first comma-or-space token and comparing just that captures the one piece guaranteed to be present in both shapes: the last name. Returning `0.0` for an author-less side (rather than treating "no data" as "no conflict") is a deliberately conservative choice — the module should never claim confirmed author overlap it has no actual evidence for.

### `min_author_overlap` defaults to `0.0` (disabled) but is available
**(c) Convention.** Title similarity alone, at a `0.90` threshold, already separates the tested real-world-shaped cases correctly (confirmed: a genuinely different "Employee Wellbeing" vs. "Employee Productivity" pair scores `0.732`, safely below threshold). Making author overlap an optional additional gate — rather than mandatory — means a caller with untrustworthy author data (e.g. a source that's known to mangle names) can still use pure title-based fuzzy matching.

### A fuzzy match always keeps the earlier-indexed record and marks the later one as the duplicate
**(c) Convention.** Arbitrary but deterministic — given the same input order, the result is always the same. A "smarter" choice (keep whichever record has more complete fields, or came from a preferred source) is a legitimate enhancement, deliberately left out here to keep this module's one job — *detecting* duplicates — separate from a second job — *choosing which copy to prefer* — that a later module or a human reviewer might want to control directly.

### Every merge decision is recorded as a `DuplicateMatch` with a reason and a score, never applied silently
**(b) Forced by external contract.** PRISMA reporting requires disclosing how many records were removed as duplicates. A dedup step that just returns a shorter list with no record of *why* each removal happened would make that reporting requirement impossible to satisfy honestly later, in Module 7.

## Decisions We Made

| Decision | Category |
|---|---|
| Exact-DOI pass before fuzzy-title pass | (c) Convention (cost/certainty ordering) |
| DOI normalization strips only the doi.org URL prefix | (b) External contract (DOI Handbook case-insensitivity) |
| `difflib.SequenceMatcher`, no third-party fuzzy library | (c) Convention, driven by (b) architecture target |
| Punctuation-stripping title normalization | (c) Convention |
| Author overlap via last-name Jaccard, `0.0` on missing data | (c) Convention (conservative) |
| `min_author_overlap` optional, off by default | (c) Convention |
| Earlier-indexed record always kept on a fuzzy match | (c) Convention (deterministic, not "smart") |
| Every match logged with reason + score, nothing silent | (b) External contract (PRISMA reporting) |

## What We Proved

Running [`dedup_engine.py`](dedup_engine.py) against a five-record corpus
built to contain exactly the cases that matter:

1. **Exact DOI matching caught a case/URL-prefix variant** (`10.1037/xyz` vs. `HTTPS://DOI.ORG/10.1037/XYZ`) that a naive string-equality check would have missed.
2. **Fuzzy title matching caught a no-DOI preprint copy of the same paper** (`title_similarity` = 1.000 after normalization) that exact matching couldn't touch, since it had no DOI to compare.
3. **Two genuinely different papers with structurally similar titles were correctly left alone** — "Remote Work and Employee Wellbeing" vs. "...Productivity" scored `0.732`, safely under the `0.90` threshold, and neither was flagged. A dedup engine that can't avoid false positives is at least as dangerous as one that misses real duplicates, since a false positive silently deletes a real, distinct study from the review.

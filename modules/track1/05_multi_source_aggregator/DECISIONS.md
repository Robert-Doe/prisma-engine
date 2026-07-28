# Module 5 — Decisions: Multi-Source Aggregator

## Line-by-line / unit-by-unit

### arXiv was chosen as the second source
**(c) Convention — backed by a quick empirical check.** arXiv's public API (`export.arxiv.org/api/query`) was tested with the same AND/OR/parentheses/quoted-phrase structure Module 4 confirmed PubMed honors, using `abs:` field tags: `(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)`. It returned a real, sensible result set (44 total, real papers about telecommuting/productivity), confirming arXiv's search genuinely parses boolean structure too — making it a fair second data point for "does this generalize beyond PubMed," rather than a source picked only for convenience.

### `parse_arxiv_feed()` uses `xml.etree.ElementTree`, not a new dependency
**(c) Convention, driven by (b) the course's architecture target.** arXiv's API returns Atom XML, not JSON. Python's standard library already includes a capable XML parser — reaching for a third-party library (e.g. `feedparser`) would add a dependency for a format the stdlib already handles correctly.

### Two XML namespaces are handled explicitly (`http://www.w3.org/2005/Atom` and `http://arxiv.org/schemas/atom`)
**(b) Forced by external contract.** Atom feeds are namespaced XML by specification, and arXiv adds its own namespace for arXiv-specific elements (`primary_category`, `doi` when present). `ElementTree` requires the full namespace URI in every tag lookup (`{namespace}tagname`) — there is no way to query these elements correctly without it.

### A missing `<title>` causes the entry to be silently skipped, not to raise
**(c) Convention — different from Module 3's `ParseError` on a missing title.** Module 3's parsers raise on a missing title because they process one record at a time, supplied deliberately by the caller — a missing title there is caller error. Here, one parser call processes an entire feed of entries fetched from a live, occasionally messy source; one malformed entry shouldn't abort processing of the other N-1 good ones. Skipping is the right failure mode for a batch parser; raising is the right failure mode for a single-record parser. Same underlying principle (a title is required to be useful), different scope of failure.

### Author names from arXiv are kept exactly as returned, including obviously malformed entries
**(c) Convention — an honesty requirement, not a bug.** A real query during development returned an entry with author list `["Khandker Nurul Habib", "Ph. D.", " PEng"]` — the source paper's metadata literally lists a credential and a professional designation as separate "authors." This module does not attempt to detect and clean that up. Silently "fixing" messy source data would hide a real data-quality problem that a genuine reviewer needs to see and handle, not one this module should paper over.

### `merge_sources()` takes any number of `list[Record]` arguments, not a fixed two
**(c) Convention.** Nothing in the merge logic is PubMed/arXiv-specific — `*source_lists` accepts any number of record lists from any sources, so a third or fourth source (Module 21's scoping-review variant, for instance) can reuse this exact function unmodified.

### `CorpusStats` counts by `source_format` rather than requiring a separate provenance-tracking structure
**(c) Convention.** Module 3 already put `source_format` on every `Record`. Reusing that existing field to compute provenance counts, rather than inventing a parallel tracking structure, is the simpler design — and proves the field earns its place from Module 3 forward.

## Decisions We Made

| Decision | Category |
|---|---|
| arXiv chosen as second source | (c) Convention, backed by an empirical boolean-support check |
| `xml.etree.ElementTree` for Atom parsing | (c) Convention, driven by (b) architecture target |
| Explicit namespace handling | (b) External contract (Atom + arXiv XML specs) |
| Missing title skips the entry, doesn't raise | (c) Convention (batch vs. single-record failure mode) |
| Malformed real author data left uncleaned | (c) Convention (honesty requirement) |
| `merge_sources()` accepts any number of sources | (c) Convention |
| Provenance tracked via existing `source_format` field | (c) Convention |

## What We Proved

Running [`aggregator.py`](aggregator.py) made real, live calls to two
independently-built, independently-shaped academic APIs (PubMed
E-utilities' JSON, arXiv's Atom XML) in the same run, and:

1. **Both real sources' results converged on the same `Record` shape** — 3 PubMed records and 3 arXiv records were merged into one 6-record corpus, with no special-casing required at the point of merge.
2. **Provenance survived the merge, verifiably.** `CorpusStats.counts_by_source` reported `{'PubMedESummary': 3, 'ArXivAtom': 3}` after merging — not an assumption, a count computed from the merged list itself, and every individual record's `source_format` printed correctly in the final listing.
3. **Real messy data (arXiv's malformed author list) was captured, not sanitized away**, which is itself evidence this module handles real API output rather than a cleaned-up idealization of it.

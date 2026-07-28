# Module 13 — Decisions: Citation Snowballing Engine

## Line-by-line / unit-by-unit

### Backward snowballing uses Crossref; forward snowballing uses Semantic Scholar
**(b) Forced by external contract.** Crossref indexes reference lists (what a paper cites) for works publishers have submitted them for — real, verified during development against a real DOI (60 references found, 32 with a resolvable DOI). Crossref does not provide a forward-citation index (who cites this paper) as part of its core API. Semantic Scholar's Graph API does provide exactly that (`/paper/{id}/citations`), confirmed live during development. No single free, no-key API covers both directions, so this module uses the one that actually supports each direction rather than forcing one API to do a job it doesn't do.

### `backward_snowball()` resolves only DOI-bearing references, and only the first `max_resolve`
**(c) Convention.** Not every Crossref reference entry has a resolvable DOI — many are `unstructured` free-text citations (confirmed live: 60 total references, only 32 carried a `DOI` field). Resolving a reference into a full `Record` requires a second, separate Crossref lookup per DOI; resolving all of them for a paper with dozens of references would mean dozens of additional live network calls for one demo run. Capping at `max_resolve` (default 3) keeps the demo's network cost bounded while still proving the mechanism works end to end.

### `fetch_crossref_record()` reuses Module 3's `parse_crossref_json()` unchanged
**(c) Convention.** A DOI resolved via backward snowballing and a DOI found via Module 4's live search return the exact same Crossref JSON shape — there's no reason to parse it differently just because of which module happened to discover the DOI. This is the same principle Module 4 already established: one parser, reused wherever Crossref-shaped data shows up.

### `parse_semantic_scholar_paper()` is a new parser, not a Module 3 addition
**(c) Convention.** Semantic Scholar's citation response shape (`title`, `year`, `authors: [{name}]`, `externalIds.DOI`) is structurally its own thing, different enough from RIS/BibTeX/Crossref/PubMed to warrant its own function rather than overloading an existing one — consistent with how Module 5 added a new `parse_arxiv_feed()` rather than stretching Module 3's parsers to cover Atom XML.

### A citing-paper entry with no title is skipped (`return None`), not raised on
**(c) Convention, consistent with Module 5's batch-parsing precedent.** Same reasoning as Module 5's `parse_arxiv_feed()`: this function processes many entries from one live response, and a single malformed entry (Semantic Scholar's citation graph sometimes includes stub records with minimal metadata) shouldn't abort processing of the rest.

### The demo reuses Module 5's `merge_sources()` unchanged to combine the seed, backward, and forward results
**(c) Convention.** `merge_sources()` was already built to accept any number of source lists — this module is exactly the generalization case Module 5's DECISIONS.md predicted when it said a third or fourth source "can reuse this exact function unmodified." No new merge logic needed writing.

## Decisions We Made

| Decision | Category |
|---|---|
| Crossref for backward, Semantic Scholar for forward | (b) External contract (neither API covers both directions) |
| Only DOI-bearing references resolved, capped at `max_resolve` | (c) Convention (bounded live network cost) |
| `fetch_crossref_record()` reuses Module 3's parser | (c) Convention |
| New `parse_semantic_scholar_paper()`, not a Module 3 addition | (c) Convention |
| Missing-title citing-paper entries skipped, not raised on | (c) Convention (batch-parsing precedent from Module 5) |
| Module 5's `merge_sources()` reused unmodified | (c) Convention |

## What We Proved

Running [`snowball.py`](snowball.py) made real, live calls to two
independent citation-graph sources and:

1. **A single seed paper's corpus genuinely expanded via real citation traversal** — 1 seed record became 9 after backward and forward snowballing, using real DOIs and real citing papers pulled live from Crossref and Semantic Scholar, not simulated relationships.
2. **Backward and forward snowballing found genuinely different things** — backward resolved cited foundational work from 2006-2017 (older, referenced by the seed); forward found citing work from 2026 (newer, referencing the seed) — real evidence the two directions serve different purposes, not just two names for the same operation.
3. **Reused infrastructure held up under a new, unanticipated use case.** Module 3's Crossref parser and Module 5's `merge_sources()` both worked here completely unmodified, despite being designed before Module 13 existed — real confirmation that the earlier modules' generalized design choices paid off.

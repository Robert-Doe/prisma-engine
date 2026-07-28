# Module 23 — Decisions: Bibliometric / Citation Network Analyzer

## Line-by-line / unit-by-unit

### The graph is built from real, live two-hop data — seed, backward, forward, AND references of the first 2 forward-citing papers
**(c) Convention.** A pure one-hop star graph (seed in the middle, every other node connected only to the seed) has no interesting structure to analyze — every non-seed node would trivially have degree 1, and no co-citation pairs could exist without at least one node connecting to two others. Fetching a second hop (the references of a couple of citing papers) was the minimum real extension needed to make centrality and co-citation analysis produce anything non-trivial, confirmed only by actually running it and finding a real overlap.

### `CitationGraph` uses plain Python sets and dicts, not a graph library (e.g. `networkx`)
**(c) Convention, driven by (b) the course's architecture target.** Degree centrality and co-citation counting are both simple enough to compute directly from an edge set — a handful of comprehensions — without needing a dedicated graph library's machinery. `networkx` would be the right choice for algorithms this module doesn't implement (shortest paths, community detection, PageRank); adding it as a dependency for operations this simple isn't justified yet.

### Node identity is normalized via Module 6's `normalize_doi()`, reused directly
**(c) Convention.** The same real problem Module 6 solved for deduplication — a DOI can appear as `10.1145/X`, `https://doi.org/10.1145/X`, or `DOI.ORG/10.1145/X` and still be the same paper — applies identically to graph node identity. Two edges pointing at differently-cased or differently-prefixed versions of the same DOI would silently create two separate nodes for one real paper. Reusing Module 6's exact function, rather than writing a new normalization routine, guarantees the two modules agree on what "the same paper" means.

### `find_co_citation_pairs()` only counts pairs from a single citing paper's own reference set, using `frozenset` as the pair key
**(b) Forced by external contract — real co-citation methodology.** Co-citation, as a bibliometric concept, is specifically defined as two papers being cited *together by a third paper* — not any two papers that happen to both appear somewhere in the graph. Grouping edges by citing paper first, then pairing within each group, is the direct implementation of that definition. `frozenset({a, b})` as the dict key (rather than a tuple) is what makes `(A, B)` and `(B, A)` count as the same pair, since co-citation has no direction.

### The demo reports "no co-citation pairs found" as a valid, real possible outcome rather than treating it as something to guarantee against
**(c) Convention, honestly scoped.** Whether real 2026 citing papers happen to share a reference with each other or with the seed's own backward references is not something this module controls — it depends on what's actually in Crossref's index at run time. The code path exists explicitly (`if pairs: ... else: ...`) so a genuinely empty result is reported as real, uninteresting-but-true data, not silently hidden or treated as a failure.

## Decisions We Made

| Decision | Category |
|---|---|
| Real two-hop data fetched, not just one hop | (c) Convention (needed for non-trivial structure) |
| Plain sets/dicts instead of a graph library | (c) Convention, driven by (b) architecture target |
| Node identity via Module 6's `normalize_doi()`, reused directly | (c) Convention |
| Co-citation grouped by citing paper, `frozenset` pair key | (b) External contract (real co-citation definition) |
| An empty co-citation result is a valid, honestly-reported outcome | (c) Convention |

## What We Proved

Running [`bibliometric_analyzer.py`](bibliometric_analyzer.py) built a
real, live two-hop citation graph and found something not planned in
advance:

1. **A real second-hop overlap emerged organically.** One of the seed paper's real 2026 citing papers ("Advancing fuzzing with unbiased random generator...") turned out to also cite "Directed Greybox Fuzzing" — one of the seed's own backward references. This wasn't constructed or expected; it was discovered by actually fetching and checking the data, exactly the kind of real finding this course's quality bar asks for over an assumed or hypothetical one.
2. **Degree centrality correctly identified the most-connected non-seed paper.** "Directed Greybox Fuzzing" ended with in-degree 2 (cited by both the seed and the newer citing paper) — the highest of any non-seed node — a real, computed signal that this particular prior work sits unusually central to this small citation neighborhood.
3. **Co-citation pairs were computed from real data and correctly reflect the real 2nd-hop discovery** — the pair `("Directed Greybox Fuzzing", "Evaluating Fuzz Testing")` appears because the citing paper's real reference list cites both, verified directly from Crossref's actual response rather than asserted.

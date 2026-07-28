# Module 2 — Decisions: Boolean Query Builder

## Line-by-line / unit-by-unit

### `sys.path.insert(0, ...)` to import Module 1's `formalizer`
**(c) Convention, driven by (b) the course's own architecture target.** Every module in this course must run standalone with `python <file>.py` and zero setup steps (see the [Tools/Architecture Target](../../../ROADMAP.md)) — no `pip install -e .`, no `pyproject.toml`, no package registry. Computing Module 1's directory relative to `__file__` and inserting it onto `sys.path` before importing achieves real code reuse across modules without introducing that setup step. A proper installable Python package (with a shared `src/` layout and relative imports) is the standard production alternative and would be the right choice outside a teaching context — but it would mean Module 2's tutorial couldn't say "just run `python query_builder.py`" anymore.

### `DEFAULT_SEARCH_SLOTS` excludes `comparison` and `outcome`
**(b) Forced by external contract — standard search-strategy guidance.** Systematic-review search-methodology guidance (e.g. the Cochrane Handbook's advice on search sensitivity) consistently recommends against requiring outcome or comparator terms in the search itself: many relevant papers never mention the outcome in their title or abstract, so requiring it there silently drops real studies before a human ever sees them. Comparison and Outcome are still fully present on the `ResearchQuestion` object — they just get applied later, as eligibility criteria during screening (Module 8), not as search terms here.

### `quote_if_phrase()` detects "needs quoting" by checking for a space
**(c) Convention.** Multi-word phrase quoting is a real requirement of boolean query syntax (an external contract each database enforces) — but the specific detection rule (a raw space) is a convention. It's simple, and correct for every term in this module's examples; a term with an internal hyphen but no space (e.g. `"work-from-home"`) would not get quoted under this rule, which is a real limitation, not a hidden bug — see the tutorial's Limits section.

### Two separate exception types: `MissingTermsError` vs. `EmptySlotTermsError`
**(c) Convention.** These represent two genuinely different failure states: `MissingTermsError` means the caller never provided a `SlotTerms` for a slot the query needs at all; `EmptySlotTermsError` means a `SlotTerms` was provided but contains no usable terms (an OR-group with nothing inside isn't a valid boolean clause). Collapsing them into one generic error would save a few lines but hide which of two different mistakes the caller actually made.

### `build_or_group()`'s `vocab_tag` parameter defaults to `"MeSH"` but is overridable
**(c) Convention.** MeSH is PubMed's controlled vocabulary, but it isn't universal — a computer-science search might use ACM's Computing Classification System instead. Making the tag a parameter rather than a hardcoded string means the same function works outside a medical-literature context without modification.

### `from __future__ import annotations`
**(c) Convention.** Not strictly required on Python 3.12 (native `list[str] | None` syntax already works at runtime here), but it makes every annotation lazily-evaluated regardless of declaration order or Python version, which is a defensive habit worth keeping even when not currently load-bearing.

### The illustrative `"Telework"` controlled-vocabulary term in the demo
**(c) Convention — and an explicit honesty flag.** This course's quality bar requires never fabricating a fact presented as verified. The demo's controlled-vocabulary term is labeled in a code comment as illustrating the *pattern* a real MeSH heading follows, not as an independently verified live MeSH lookup — because this exercise didn't perform one. Module 4 (Live API Connector) is where this course starts making real, verifiable network calls against live databases.

## Decisions We Made

| Decision | Category |
|---|---|
| `sys.path` injection for cross-module imports | (c) Convention, driven by (b) course architecture target |
| Comparison/Outcome excluded from default search slots | (b) External contract (search-methodology guidance) |
| Space-detection for phrase quoting | (c) Convention |
| Two distinct exception types for two distinct failures | (c) Convention |
| `vocab_tag` is a parameter, not hardcoded `"MeSH"` | (c) Convention |
| `from __future__ import annotations` | (c) Convention (defensive, not required on 3.12) |
| Demo's controlled-vocab term flagged as illustrative, not verified | (c) Convention (honesty requirement) |

## What We Proved

Running [`query_builder.py`](query_builder.py) demonstrated:

1. **A structured `ResearchQuestion` mechanically becomes a real boolean query string** — no manual string-editing step in between. The same `ResearchQuestion` object Module 1 produced was consumed directly.
2. **The sensitivity/precision tradeoff is real and visible, not asserted.** Example 1 (population + intervention only) and Example 2 (adding outcome) produced two different, both-valid query strings from the same underlying data — and the demo's own output states in plain terms why Example 2 is stricter, tying directly back to the search-methodology reasoning in this module's DECISIONS.md.
3. **Incomplete input is caught before producing a malformed query.** A search missing required terms raises `MissingTermsError` naming the exact slot, rather than silently building a query with a hole in it.

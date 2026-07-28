# Module 4 — Decisions: Live API Connector

This module made real network calls during development, and two of the
decisions below exist *because of* what those calls actually returned —
not because of something assumed in advance. Both are marked with the
captured evidence.

## Line-by-line / unit-by-unit

### PubMed E-utilities was chosen over Crossref for the search call
**(c) Convention — backed by captured evidence, not assumption.** Crossref's public API (`api.crossref.org/works`) was tested first, since Module 3 already models its JSON shape. Sending it Module 2's exact boolean query string —

```
("knowledge workers" OR "office workers" OR employees) AND ("remote work" OR telecommut* OR "work from home")
```

— returned **1,206,390 total results**, and the top hits didn't even all contain "knowledge workers." Crossref's `query.bibliographic` parameter does relevance-ranked free-text search; it does not parse `AND`/`OR`/quotes/parentheses as boolean syntax at all — it just treats the whole string as a bag of words. Sending the *same* string to PubMed's `esearch` endpoint returned **517 results** and a `querytranslation` field confirming it parsed the AND/OR/parentheses/quoted-phrase structure correctly. Since this module's whole point is proving Module 2's boolean query builder produces something a live system actually honors as boolean, PubMed is the API that makes that claim true; Crossref would make it false while looking like it worked.

### `translate_vocab_tag()` exists at all
**(b) Forced by external contract — discovered empirically, not assumed.** Module 2's internal convention for a controlled-vocabulary term is `MeSH:"Telework"`. Sent to PubMed literally, this does **not** restrict the search to a MeSH heading. PubMed's automatic term mapping instead treats the literal substring `"MeSH:"` as its own free-text phrase and expands it into an unrelated clause (`"medical subject headings"[MeSH Terms] OR ("medical"[All Fields] AND "subject"[All Fields] AND "headings"[All Fields]) OR ...`), while separately trying to map `"Telework"` on its own. This is real, captured behavior, not a hypothetical failure mode — which is why `translate_vocab_tag()` converts `MeSH:"X"` into PubMed's actual field-tag syntax, `"X"[mesh]`, before any query reaches the live API.

### `verify_mesh_term()` — checking a controlled-vocabulary term against the live database instead of trusting it
**(c) Convention, directly motivated by a real result.** Modules 2 and 3 used `"Telework"` as an illustrative MeSH term, explicitly flagged in both modules' DECISIONS.md as "not independently verified... Module 4 is where this gets checked against reality." Checked here, live:

```
"Telework"[mesh]     -> count: 0    (flagged in quotedphrasesnotfound — not a real heading)
"Teleworking"[mesh]  -> count: 563  (resolves to "Teleworking"[MeSH Terms] — this is the real heading)
```

"Telework" was wrong. This is the single clearest demonstration in the course so far of why the earlier modules' hedging language ("illustrative... not verified") wasn't just caution for its own sake — an unverified placeholder term really was incorrect, and only became detectable once this module could ask the live system directly. The demo now uses the corrected term, `"Teleworking"`.

### `esummary` was used instead of `efetch` for record metadata
**(c) Convention.** `esummary` returns compact JSON with everything this module's `Record` model needs (title, authors, year, journal, DOI) in a few lines of parsing. `efetch` would additionally return abstracts, but as PubMed's full XML citation format — substantially more complex to parse correctly. Leaving abstracts out is a real, stated limitation of this module (see the tutorial), not a silent gap.

### A `0.4` second courtesy delay between the `esearch` and `esummary` calls
**(b) Forced by external contract.** NCBI's E-utilities usage guidelines ask unauthenticated callers (no API key) to stay at or below 3 requests/second. This module only ever makes two calls per search, so the delay is not strictly load-bearing here — it's kept as the correct habit for any code that might later loop over many searches.

### `title.rstrip(".")`
**(c) Convention.** PubMed's `esummary` titles consistently end with a trailing period even when the paper's real title doesn't use one as punctuation — a cosmetic artifact of PubMed's citation formatting, confirmed in every title returned during testing. Stripping it is a display convenience; the underlying `title` field content is otherwise untouched.

### This module's output is explicitly documented as non-deterministic
**(b) Forced by the nature of the external system.** PubMed's index changes continuously — new records are added, and the pool of results for any real query shifts over time. Every earlier module's `_run_demo()` produces identical output on every run; this one cannot, by the nature of what it's connecting to. The tutorial's "Run It" section captures one real run's output and says so explicitly, rather than implying the exact numbers are reproducible.

## Decisions We Made

| Decision | Category |
|---|---|
| PubMed chosen over Crossref for search | (c) Convention, backed by captured evidence |
| `translate_vocab_tag()` needed before hitting PubMed | (b) External contract (discovered empirically) |
| `verify_mesh_term()` checks live rather than trusting Module 2's term | (c) Convention, motivated by a real, captured wrong answer |
| `esummary` over `efetch` (no abstracts) | (c) Convention (documented limitation) |
| NCBI courtesy delay | (b) External contract (NCBI usage guidelines) |
| Title trailing-period stripping | (c) Convention |
| Non-deterministic output, documented as such | (b) Forced by the external system's nature |

## What We Proved

This module made real, live network calls and captured their actual
output rather than describing intended behavior:

1. **Module 2's boolean query string is honored as real boolean logic by a real system** — PubMed's `querytranslation` field is direct proof the AND/OR/parentheses/quoted-phrase structure survived intact, which is not true of every API (Crossref, tested for contrast, ignores that structure entirely).
2. **An unverified placeholder was wrong, and checking caught it.** `"Telework"` — used illustratively since Module 2 — returned zero results as a MeSH heading; `"Teleworking"` is the real one. This is the course's first concrete instance of the stated quality bar ("verify against real output, not asserted from general knowledge") actually catching a real error rather than being a hypothetical safeguard.
3. **A structured query, once translated for a specific API's dialect, retrieves real records that parse cleanly into Module 3's `Record` model** — end to end, from a Module 1 question through a Module 2 query through a Module 4 live search into normalized `Record` objects, with real titles, authors, years, venues, and DOIs.

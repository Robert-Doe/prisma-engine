# Module 3 — Decisions: Bibliographic Record Model

## Line-by-line / unit-by-unit

### The `Record` field set (`title, authors, year, venue, abstract, doi, source_format`)
**(c) Convention, informed by (b) external contracts.** RIS, BibTeX, and Crossref's API each expose a different, larger set of possible fields (RIS alone defines dozens of tags). This module's canonical `Record` keeps only the fields every later module actually needs (dedup, screening, citation). Which fields to keep is a convention; that *some* normalization has to happen at all is forced by the fact that three real, external formats disagree on field names for the same facts.

### `source_format` is kept on every `Record`
**(c) Convention.** Nothing downstream strictly requires knowing where a record came from — but discarding that provenance immediately would make debugging a bad merge (Module 5) or a dedup false-positive (Module 6) much harder later. Keeping one extra string field now is cheap insurance.

### RIS parsing: regex on `TAG  - value`, `AU` collected into a list, everything else a plain dict
**(b) Forced by external contract.** RIS's tag-value-per-line shape, the two-space-dash-space separator, and the convention that `AU` may repeat for multiple authors are all part of the RIS format itself (originally defined by Research Information Systems, now a de facto standard across reference managers) — not something this module chose.

### BibTeX parsing uses one regex (`\w+\s*=\s*\{([^{}]*)\}`), not a real BibTeX grammar
**(c) Convention — a deliberate, documented scope limit.** Real BibTeX allows nested braces, `@string` macros, and quoted (not just braced) values. A correct general-purpose BibTeX parser is a much larger undertaking than this module needs. The regex here handles the common case (flat, brace-delimited fields, which is what every citation manager actually exports) and is explicit about not handling the rest — see the Limits section of the tutorial rather than silently mishandling an edge case.

### `parse_crossref_json()`'s field names (`title`, `author`/`given`/`family`, `published`/`date-parts`, `container-title`, `DOI`)
**(b) Forced by external contract.** These are Crossref's actual public REST API field names (`api.crossref.org/works/{doi}`), not invented here. Module 4 calls this same live API and feeds real responses through this exact function — this module's version uses a literal dict standing in for one, specifically so Module 3 has zero network dependency while still testing against Crossref's real documented shape.

### Stripping JATS-style XML tags from Crossref abstracts (`re.sub(r"<[^>]+>", "", abstract)`)
**(b) Forced by external contract.** Crossref frequently returns abstracts wrapped in JATS XML markup (e.g. `<jats:p>...</jats:p>`) when the publisher supplied structured abstracts — this isn't a Crossref quirk this module invented a workaround for, it's a documented characteristic of the API's abstract field that any consumer has to handle to get plain text.

### `ParseError` requires only a title to succeed, not every field
**(c) Convention.** A title is the one field with no reasonable default and no later stage that can proceed without it. Author list, year, venue, abstract, and DOI can legitimately be missing from a real record (a preprint might have no DOI yet) without making the record useless — treating any of them as required would reject real, usable data.

## Decisions We Made

| Decision | Category |
|---|---|
| Canonical `Record` field set | (c) Convention, informed by (b) three real formats |
| `source_format` retained for provenance | (c) Convention |
| RIS tag/value parsing shape | (b) External contract (RIS format spec) |
| BibTeX parser handles flat fields only, not full grammar | (c) Convention (documented scope limit) |
| Crossref JSON field names | (b) External contract (Crossref REST API) |
| JATS tag stripping on abstracts | (b) External contract (Crossref abstract format) |
| Only `title` is strictly required | (c) Convention |

## What We Proved

Running [`record_model.py`](record_model.py) fed the **same underlying
paper** through three genuinely different, independently-specified formats
— hand-written RIS, hand-written BibTeX, and a dict shaped exactly like a
real Crossref API response — and confirmed programmatically
(`ris_record.title == bibtex_record.title == crossref_record.title`, same
for authors/year/doi) that all three converge on identical values in every
field that matters, differing only in the `source_format` label that
records where each one came from. That equality check passing is the
concrete evidence behind this module's claim: heterogeneous citation
formats really can be normalized into one comparable shape, not just
described as if they could be.

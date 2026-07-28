"""
Module 4 — Live API Connector

Runs a real boolean search (Module 2's query string, after translating this
course's internal controlled-vocabulary tag into PubMed's real field-tag
syntax) against PubMed's public E-utilities API, and parses whatever comes
back into real Record objects (Module 3's model).

This module makes actual network calls. No API key is required, but it
needs internet access to run, and — unlike every previous module — its
exact output is NOT deterministic: PubMed's index changes continuously, so
re-running this tomorrow will very likely return different records than it
did today. That's a real property of live data, not a bug. See the
tutorial's Run It section for what was actually captured on one real run.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
from record_model import Record  # noqa: E402

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# NCBI's usage guidelines ask unauthenticated (no API key) callers to stay
# at or below 3 requests/second. This module makes at most two calls per
# search, but the courtesy delay is kept as a real, documented habit.
_NCBI_COURTESY_DELAY_SECONDS = 0.4

USER_AGENT = "lit-review-course-module4/0.1 (educational project; no contact API key)"


class APIError(RuntimeError):
    """Raised when PubMed's API returns something other than a usable
    esearch/esummary result — e.g. a malformed query it couldn't parse."""


def translate_vocab_tag(query: str, our_tag: str = "MeSH", pubmed_tag: str = "mesh") -> str:
    """Convert Module 2's internal `MeSH:"term"` convention into PubMed's
    real field-tag syntax `"term"[mesh]`.

    This exists because of a real, empirically-verified failure: sending
    `MeSH:"Telework"` to PubMed literally does NOT restrict the search to
    the MeSH heading "Telework". PubMed's automatic term mapping instead
    treats "MeSH:" as its own free-text phrase (expanding it into an
    unrelated OR-clause about "medical subject headings") and searches
    "Telework" separately across all fields. See DECISIONS.md for the
    captured evidence.
    """
    pattern = re.compile(rf'{re.escape(our_tag)}:"([^"]+)"')
    return pattern.sub(lambda m: f'"{m.group(1)}"[{pubmed_tag}]', query)


def esearch(query: str, retmax: int = 5) -> tuple[list[str], int, str]:
    """Returns (pmid_list, total_count, query_translation)."""
    resp = requests.get(
        ESEARCH_URL,
        params={"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("esearchresult", {})
    if "idlist" not in result:
        raise APIError(f"esearch returned no idlist: {data}")
    return result["idlist"], int(result["count"]), result.get("querytranslation", "")


def verify_mesh_term(term: str) -> bool:
    """Checks a candidate controlled-vocabulary term against the live
    database instead of trusting it. Returns False if PubMed can't map it
    to a real MeSH heading (flagged in `quotedphrasesnotfound`), True if
    it resolves to an actual `[MeSH Terms]` match.

    This function exists because of a real result, not a hypothetical one:
    Module 2/3's demo used "Telework" as an illustrative MeSH term,
    explicitly flagged there as unverified. Run against the live API, it
    turns out "Telework" is NOT a real MeSH heading (0 results) — the real
    heading is "Teleworking". See DECISIONS.md for the full captured
    evidence of both checks.
    """
    resp = requests.get(
        ESEARCH_URL,
        params={"db": "pubmed", "term": f'"{term}"[mesh]', "retmode": "json"},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    result = resp.json().get("esearchresult", {})
    not_found = result.get("warninglist", {}).get("quotedphrasesnotfound", [])
    return int(result.get("count", 0)) > 0 and not not_found


def esummary(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    resp = requests.get(
        ESUMMARY_URL,
        params={"db": "pubmed", "id": ",".join(pmids), "retmode": "json"},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    result = data.get("result", {})
    return [result[uid] for uid in result.get("uids", [])]


_YEAR_RE = re.compile(r"(\d{4})")


def parse_pubmed_summary(rec: dict) -> Record:
    year_match = _YEAR_RE.search(rec.get("pubdate", ""))
    year = int(year_match.group(1)) if year_match else None

    doi = None
    for article_id in rec.get("articleids", []):
        if article_id.get("idtype") == "doi":
            doi = article_id["value"]
            break

    authors = [a["name"] for a in rec.get("authors", []) if a.get("authtype") == "Author"]

    return Record(
        title=rec.get("title", "").rstrip("."),
        authors=authors,
        year=year,
        venue=rec.get("fulljournalname") or rec.get("source"),
        abstract=None,  # esummary doesn't include abstracts — see Limits in the tutorial
        doi=doi,
        source_format="PubMedESummary",
    )


def search_and_fetch(query: str, retmax: int = 5) -> tuple[list[Record], int, str]:
    """End-to-end: translate vocab tags, esearch, esummary, parse.
    Returns (records, total_count_available, query_translation)."""
    translated = translate_vocab_tag(query)
    pmids, total_count, query_translation = esearch(translated, retmax=retmax)
    time.sleep(_NCBI_COURTESY_DELAY_SECONDS)
    summaries = esummary(pmids)
    records = [parse_pubmed_summary(s) for s in summaries]
    return records, total_count, query_translation


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("STEP 0 — verify Module 2's illustrative MeSH term against reality")
    print("=" * 70)
    for candidate in ["Telework", "Teleworking"]:
        ok = verify_mesh_term(candidate)
        print(f'  "{candidate}"[mesh] is a real MeSH heading? {ok}')
        time.sleep(_NCBI_COURTESY_DELAY_SECONDS)
    print()
    print('  -> "Telework" (used illustratively in Modules 2-3) is NOT real.')
    print('     Using the verified term, "Teleworking", from here on.')

    query = (
        '("knowledge workers" OR "office workers" OR employees) '
        'AND ("remote work" OR telecommut* OR "work from home" OR "hybrid work" OR MeSH:"Teleworking")'
    )
    print()
    print("Original query (from Module 2, with the corrected MeSH term):")
    print(f"  {query}")
    translated = translate_vocab_tag(query)
    print()
    print("Translated for PubMed (MeSH:\"X\" -> \"X\"[mesh]):")
    print(f"  {translated}")

    print()
    print("=" * 70)
    print("LIVE call to PubMed E-utilities...")
    print("=" * 70)
    records, total_count, query_translation = search_and_fetch(query, retmax=3)

    print(f"Total matching records in PubMed right now: {total_count}")
    print(f"PubMed's own parse of our query:")
    print(f"  {query_translation}")
    print()
    print(f"First {len(records)} records, parsed into Record objects:")
    for i, rec in enumerate(records, 1):
        print(f"\n  [{i}] {rec.title}")
        print(f"      authors: {rec.authors}")
        print(f"      year: {rec.year}  venue: {rec.venue}  doi: {rec.doi}")


def _run_self_checks() -> None:
    # translate_vocab_tag is pure string logic — no network needed to test it.
    assert translate_vocab_tag('MeSH:"Telework"') == '"Telework"[mesh]'
    assert (
        translate_vocab_tag('(a OR b) AND MeSH:"X" AND MeSH:"Y"')
        == '(a OR b) AND "X"[mesh] AND "Y"[mesh]'
    )
    assert translate_vocab_tag("no vocab tags here") == "no vocab tags here"

    # parse_pubmed_summary against a frozen, real esummary response captured
    # on 2026-07-27 — this is real data, just not fetched live for the test.
    frozen_summary = {
        "pubdate": "2026 Jul",
        "title": "A retrospective study evaluating outcomes of the Allied Health Rural Generalist Training Positions in the Queensland public health system.",
        "fulljournalname": "Rural and remote health",
        "authors": [{"name": "Cardell E", "authtype": "Author"}, {"name": "Pitt R", "authtype": "Author"}],
        "articleids": [
            {"idtype": "pubmed", "value": "42478010"},
            {"idtype": "doi", "value": "10.22605/RRH10326"},
        ],
    }
    rec = parse_pubmed_summary(frozen_summary)
    assert rec.year == 2026
    assert rec.doi == "10.22605/RRH10326"
    assert rec.authors == ["Cardell E", "Pitt R"]
    assert rec.source_format == "PubMedESummary"

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 13 — Citation Snowballing Engine

Backward snowballing: fetch a seed paper's reference list (Crossref) and
resolve those cited DOIs into full Records. Forward snowballing: fetch
papers that cite the seed (Semantic Scholar) and parse them into Records
directly. Both real, live network calls — proving a corpus can grow beyond
whatever the original search found.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_multi_source_aggregator"))
from record_model import Record, parse_crossref_json  # noqa: E402
from aggregator import merge_sources  # noqa: E402

CROSSREF_WORKS_URL = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper"
USER_AGENT = "lit-review-course-module13/0.1 (educational project; no contact API key)"


def fetch_crossref_record(doi: str) -> Record | None:
    """Resolves a bare DOI into a full Record via Crossref, reusing
    Module 3's parser unchanged. Returns None if the DOI isn't found."""
    resp = requests.get(f"{CROSSREF_WORKS_URL}/{doi}", headers={"User-Agent": USER_AGENT}, timeout=15)
    if resp.status_code != 200:
        return None
    return parse_crossref_json(resp.json()["message"])


def backward_snowball(seed_doi: str, max_resolve: int = 3) -> list[Record]:
    """Fetches the seed paper's reference list from Crossref, then
    resolves up to `max_resolve` of the DOI-bearing references into full
    Records (each is a real, separate Crossref lookup)."""
    resp = requests.get(f"{CROSSREF_WORKS_URL}/{seed_doi}", headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    references = resp.json()["message"].get("reference", [])
    dois_with_metadata = [r["DOI"] for r in references if "DOI" in r]

    resolved = []
    for doi in dois_with_metadata[:max_resolve]:
        rec = fetch_crossref_record(doi)
        if rec is not None:
            rec.source_format = "CrossrefBackwardSnowball"
            resolved.append(rec)
    return resolved


def parse_semantic_scholar_paper(item: dict) -> Record | None:
    title = item.get("title")
    if not title:
        return None
    authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
    return Record(
        title=title,
        authors=authors,
        year=item.get("year"),
        venue=None,  # Semantic Scholar's default fields used here don't include venue
        abstract=None,
        doi=item.get("externalIds", {}).get("DOI"),
        source_format="SemanticScholarForwardSnowball",
    )


def forward_snowball(seed_doi: str, limit: int = 5) -> list[Record]:
    """Fetches papers that cite the seed paper, via Semantic Scholar's
    citation graph API."""
    resp = requests.get(
        f"{SEMANTIC_SCHOLAR_URL}/DOI:{seed_doi}/citations",
        params={"fields": "title,year,authors,externalIds", "limit": limit},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    records = []
    for item in data.get("data", []):
        rec = parse_semantic_scholar_paper(item.get("citingPaper", {}))
        if rec is not None:
            records.append(rec)
    return records


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    # A real, well-known CCS 2018 paper on fuzz testing evaluation.
    seed_doi = "10.1145/3243734.3243804"
    seed = fetch_crossref_record(seed_doi)
    seed.source_format = "SeedPaper"
    print(f"Seed paper: {seed.title!r} ({seed.year})")

    print()
    print("=" * 70)
    print("Backward snowball: resolving cited references (real Crossref calls)")
    print("=" * 70)
    backward = backward_snowball(seed_doi, max_resolve=3)
    for rec in backward:
        print(f"  <- {rec.title!r} ({rec.year})")

    print()
    print("=" * 70)
    print("Forward snowball: papers citing the seed (real Semantic Scholar call)")
    print("=" * 70)
    forward = forward_snowball(seed_doi, limit=5)
    for rec in forward:
        print(f"  -> {rec.title!r} ({rec.year})")

    corpus, stats = merge_sources([seed], backward, forward)
    print()
    print("=" * 70)
    print("Corpus expansion")
    print("=" * 70)
    print(f"Started with 1 seed paper. After snowballing: {stats.total} records.")
    print(f"By source: {stats.counts_by_source}")


def _run_self_checks() -> None:
    # parse_semantic_scholar_paper is pure logic — no network needed.
    rec = parse_semantic_scholar_paper({
        "title": "A Citing Paper",
        "year": 2022,
        "authors": [{"name": "A. Researcher"}],
        "externalIds": {"DOI": "10.1/citing"},
    })
    assert rec.title == "A Citing Paper"
    assert rec.year == 2022
    assert rec.authors == ["A. Researcher"]
    assert rec.doi == "10.1/citing"
    assert rec.source_format == "SemanticScholarForwardSnowball"

    # A citing-paper entry with no title is skipped, not crashed on.
    assert parse_semantic_scholar_paper({"year": 2022}) is None

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

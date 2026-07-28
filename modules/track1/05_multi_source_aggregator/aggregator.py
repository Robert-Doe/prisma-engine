"""
Module 5 — Multi-Source Aggregator

Runs real searches against two independently-shaped live sources —
PubMed (Module 4, reused as-is) and arXiv (new here, parsed from Atom XML)
— and merges the results into one corpus, proving every merged Record can
still be traced back to which source produced it.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "04_live_api_connector"))
from record_model import Record  # noqa: E402
from connector import search_and_fetch as search_pubmed  # noqa: E402

ARXIV_API_URL = "http://export.arxiv.org/api/query"

_ATOM_NS = "http://www.w3.org/2005/Atom"
_ARXIV_NS = "http://arxiv.org/schemas/atom"


def _tag(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def parse_arxiv_feed(xml_text: str) -> list[Record]:
    """Parses an arXiv Atom API response into Record objects. Real arXiv
    author metadata is often messy (see DECISIONS.md) — this parser keeps
    whatever is there rather than silently cleaning it up."""
    root = ET.fromstring(xml_text)
    records = []
    for entry in root.findall(_tag(_ATOM_NS, "entry")):
        title_el = entry.find(_tag(_ATOM_NS, "title"))
        summary_el = entry.find(_tag(_ATOM_NS, "summary"))
        published_el = entry.find(_tag(_ATOM_NS, "published"))
        doi_el = entry.find(_tag(_ARXIV_NS, "doi"))
        category_el = entry.find(_tag(_ARXIV_NS, "primary_category"))

        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue  # malformed entry, no title to build a Record around

        authors = [
            (name_el.text or "").strip()
            for author_el in entry.findall(_tag(_ATOM_NS, "author"))
            for name_el in [author_el.find(_tag(_ATOM_NS, "name"))]
            if name_el is not None and (name_el.text or "").strip()
        ]

        year = None
        if published_el is not None and published_el.text:
            year_str = published_el.text[:4]
            if year_str.isdigit():
                year = int(year_str)

        category = category_el.get("term") if category_el is not None else None
        venue = f"arXiv preprint ({category})" if category else "arXiv preprint"

        abstract = (summary_el.text or "").strip() if summary_el is not None else None
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

        records.append(
            Record(
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                abstract=abstract,
                doi=doi,
                source_format="ArXivAtom",
            )
        )
    return records


def fetch_arxiv(query: str, max_results: int = 5) -> tuple[list[Record], int]:
    """Real network call. Returns (records, total_results_available)."""
    resp = requests.get(
        ARXIV_API_URL,
        params={"search_query": query, "start": 0, "max_results": max_results},
        timeout=15,
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    total_el = root.find(f"{{http://a9.com/-/spec/opensearch/1.1/}}totalResults")
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    return parse_arxiv_feed(resp.text), total


@dataclass
class CorpusStats:
    counts_by_source: dict[str, int] = field(default_factory=dict)
    total: int = 0


def merge_sources(*source_lists: list[Record]) -> tuple[list[Record], CorpusStats]:
    """Concatenates records from any number of sources into one corpus,
    and returns a per-source count so provenance is checkable, not lost."""
    merged: list[Record] = []
    for records in source_lists:
        merged.extend(records)

    counts: dict[str, int] = {}
    for r in merged:
        counts[r.source_format] = counts.get(r.source_format, 0) + 1

    return merged, CorpusStats(counts_by_source=counts, total=len(merged))


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    pubmed_query = (
        '("knowledge workers" OR "office workers" OR employees) '
        'AND ("remote work" OR telecommut* OR "work from home" OR "hybrid work" OR MeSH:"Teleworking")'
    )
    arxiv_query = '(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)'

    print("=" * 70)
    print("Fetching from PubMed (reusing Module 4's search_and_fetch)...")
    print("=" * 70)
    pubmed_records, pubmed_total, _translation = search_pubmed(pubmed_query, retmax=3)
    print(f"PubMed: {len(pubmed_records)} records fetched, {pubmed_total} available")

    print()
    print("=" * 70)
    print("Fetching from arXiv (new in this module)...")
    print("=" * 70)
    arxiv_records, arxiv_total = fetch_arxiv(arxiv_query, max_results=3)
    print(f"arXiv: {len(arxiv_records)} records fetched, {arxiv_total} available")

    print()
    print("=" * 70)
    print("Merging into one corpus...")
    print("=" * 70)
    corpus, stats = merge_sources(pubmed_records, arxiv_records)
    print(f"Total merged: {stats.total}")
    print(f"By source: {stats.counts_by_source}")

    print()
    print("Every record in the merged list still knows where it came from:")
    for rec in corpus:
        print(f"  [{rec.source_format:>14}] {rec.title[:70]}")


def _run_self_checks() -> None:
    # parse_arxiv_feed against a frozen, real response body — no network
    # needed for this check.
    frozen_feed = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom"
      xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2004.04683v1</id>
    <title>On the Factors Influencing Telecommuting Frequencies</title>
    <summary>An empirical study of telecommuting frequency choices.</summary>
    <published>2020-04-09T17:08:22Z</published>
    <arxiv:primary_category term="econ.EM"/>
    <author><name>Khandker Nurul Habib</name></author>
  </entry>
</feed>"""
    records = parse_arxiv_feed(frozen_feed)
    assert len(records) == 1
    rec = records[0]
    assert rec.title == "On the Factors Influencing Telecommuting Frequencies"
    assert rec.authors == ["Khandker Nurul Habib"]
    assert rec.year == 2020
    assert rec.venue == "arXiv preprint (econ.EM)"
    assert rec.doi is None
    assert rec.source_format == "ArXivAtom"

    merged, stats = merge_sources(
        [Record(title="A", source_format="PubMedESummary")],
        [Record(title="B", source_format="ArXivAtom"), Record(title="C", source_format="ArXivAtom")],
    )
    assert stats.total == 3
    assert stats.counts_by_source == {"PubMedESummary": 1, "ArXivAtom": 2}
    assert [r.source_format for r in merged] == ["PubMedESummary", "ArXivAtom", "ArXivAtom"]

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

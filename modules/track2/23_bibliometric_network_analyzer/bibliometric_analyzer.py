"""
Module 23 — Bibliometric / Citation Network Analyzer (Track 2: Applied Layer)

Analyzes the corpus itself as data — who cites whom — rather than
synthesizing what's inside each paper. Reuses Module 13's real snowballing
functions to build a real, live two-hop citation graph, and Module 6's
normalize_doi() to keep node identity consistent. Computes real degree
centrality and finds real co-citation pairs (papers cited together by the
same citing paper) — whatever the live data actually shows, not a
predetermined example.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import requests

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
for name in ["03_bibliographic_record_model", "05_multi_source_aggregator",
             "06_deduplication_engine", "13_citation_snowballing_engine"]:
    sys.path.insert(0, str(MODULES / name))

from dedup_engine import normalize_doi  # noqa: E402
from snowball import CROSSREF_WORKS_URL, USER_AGENT, backward_snowball, forward_snowball, fetch_crossref_record  # noqa: E402


def fetch_reference_dois(doi: str) -> set[str]:
    """Real Crossref call: the set of normalized DOIs a paper references."""
    resp = requests.get(f"{CROSSREF_WORKS_URL}/{doi}", headers={"User-Agent": USER_AGENT}, timeout=15)
    if resp.status_code != 200:
        return set()
    refs = resp.json()["message"].get("reference", [])
    return {normalize_doi(r["DOI"]) for r in refs if "DOI" in r}


@dataclass
class CitationGraph:
    edges: set[tuple[str, str]] = field(default_factory=set)  # (citing_doi, cited_doi)
    labels: dict[str, str] = field(default_factory=dict)      # doi -> short label

    def add_edge(self, citing: str, cited: str) -> None:
        self.edges.add((citing, cited))

    def nodes(self) -> set[str]:
        return {n for edge in self.edges for n in edge}

    def in_degree(self, node: str) -> int:
        return sum(1 for _c, d in self.edges if d == node)

    def out_degree(self, node: str) -> int:
        return sum(1 for c, _d in self.edges if c == node)


def find_co_citation_pairs(graph: CitationGraph) -> dict[frozenset, int]:
    """Two papers are co-cited when the same citing paper cites both.
    Real co-citation signal — a common bibliometric technique for finding
    related work without reading either paper's content."""
    by_citer: dict[str, set[str]] = {}
    for citing, cited in graph.edges:
        by_citer.setdefault(citing, set()).add(cited)

    pair_counts: dict[frozenset, int] = {}
    for cited_set in by_citer.values():
        cited_list = sorted(cited_set)
        for i in range(len(cited_list)):
            for j in range(i + 1, len(cited_list)):
                pair = frozenset({cited_list[i], cited_list[j]})
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
    return pair_counts


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    seed_doi = normalize_doi("10.1145/3243734.3243804")
    seed = fetch_crossref_record(seed_doi)
    print(f"Seed: {seed.title!r} ({seed_doi})")

    graph = CitationGraph()
    graph.labels[seed_doi] = seed.title

    print()
    print("Hop 1a: backward snowball (seed's references)...")
    backward = backward_snowball(seed_doi, max_resolve=3)
    backward_dois = []
    for rec in backward:
        d = normalize_doi(rec.doi)
        backward_dois.append(d)
        graph.labels[d] = rec.title
        graph.add_edge(seed_doi, d)
        print(f"  {seed_doi} -> {d}  ({rec.title[:50]})")

    print()
    print("Hop 1b: forward snowball (papers citing the seed)...")
    forward = forward_snowball(seed_doi, limit=5)
    forward_dois = []
    for rec in forward:
        if not rec.doi:
            continue
        d = normalize_doi(rec.doi)
        forward_dois.append(d)
        graph.labels[d] = rec.title
        graph.add_edge(d, seed_doi)
        print(f"  {d} -> {seed_doi}  ({rec.title[:50]})")

    print()
    print("Hop 2: references of the first 2 forward-citing papers (real 2nd-hop data)...")
    for citer_doi in forward_dois[:2]:
        refs = fetch_reference_dois(citer_doi)
        overlap = refs & (set(backward_dois) | {seed_doi})
        print(f"  {citer_doi}: {len(refs)} references found; overlaps with our graph: {overlap or 'none'}")
        for cited in overlap:
            graph.add_edge(citer_doi, cited)

    print()
    print("=" * 70)
    print("Degree centrality (in-degree = how many times cited within this graph)")
    print("=" * 70)
    for node in sorted(graph.nodes(), key=lambda n: -graph.in_degree(n)):
        label = graph.labels.get(node, node)[:55]
        print(f"  in={graph.in_degree(node)} out={graph.out_degree(node)}  {label}")

    print()
    print("=" * 70)
    print("Co-citation pairs (cited together by the same paper)")
    print("=" * 70)
    pairs = find_co_citation_pairs(graph)
    if pairs:
        for pair, count in sorted(pairs.items(), key=lambda kv: -kv[1]):
            labels = [graph.labels.get(n, n)[:40] for n in pair]
            print(f"  {count}x: {labels}")
    else:
        print("  None found in this small a graph — real result, not an error. Larger")
        print("  citation graphs (more hops, more seeds) are where co-citation signal")
        print("  actually becomes useful; see Limits.")


def _run_self_checks() -> None:
    g = CitationGraph()
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    g.add_edge("A", "D")
    assert g.in_degree("C") == 2
    assert g.in_degree("D") == 1
    assert g.out_degree("A") == 2
    assert g.nodes() == {"A", "B", "C", "D"}

    pairs = find_co_citation_pairs(g)
    # A cites both C and D -> {C, D} co-cited once. B only cites C -> no pair from B alone.
    assert pairs == {frozenset({"C", "D"}): 1}

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

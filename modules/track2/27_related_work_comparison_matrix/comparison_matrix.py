"""
Module 27 — Related-Work Comparison Matrix Builder (Track 2: Applied Layer)

Builds the USENIX/OSDI/NSDI-style "Related Work" artifact: a dimension-by-
system comparison matrix, not a PRISMA-style chronological evidence table.
Worked example: real, live-fetched papers on microarchitectural side-channel
attacks/defenses (Spectre/Meltdown-class).

Comparison dimensions are extracted from each paper's REAL title/abstract
via a transparent keyword heuristic (same honesty principle as Module 1's
framework suggestion) — never fabricated claims about a real paper's actual
technical contribution, which this course cannot verify without reading
each paper's full text.

Reuses Module 5 (live arXiv search), Module 6 (dedup), Module 13 (backward
snowballing from a real DOI), and Module 10/14 (extraction schema + table).
"""

from __future__ import annotations

import sys
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
for name in ["03_bibliographic_record_model", "05_multi_source_aggregator",
             "06_deduplication_engine", "10_data_extraction_engine",
             "13_citation_snowballing_engine", "14_evidence_table_builder"]:
    sys.path.insert(0, str(MODULES / name))

from record_model import Record  # noqa: E402
from aggregator import fetch_arxiv, merge_sources  # noqa: E402
from dedup_engine import deduplicate  # noqa: E402
from extraction_engine import ExtractionField, ExtractionSchema, extract, one_of  # noqa: E402
from snowball import backward_snowball  # noqa: E402
from evidence_table import build_evidence_table  # noqa: E402


def classify_approach(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("detect", "identification of")):
        return "detection"
    if any(k in lowered for k in ("prevent", "mitigat", "defense", "banish", "protect")):
        return "mitigation"
    if any(k in lowered for k in ("discover", "automated discovery", "survey")):
        return "discovery/analysis"
    return "unspecified"


COMPARISON_SCHEMA = ExtractionSchema(fields=[
    ExtractionField("approach_type", str, required=True,
                     validator=one_of({"detection", "mitigation", "discovery/analysis", "unspecified"}),
                     description="What kind of contribution this paper makes, inferred from its title/abstract"),
    ExtractionField("targets_spectre", bool, required=True),
    ExtractionField("targets_meltdown", bool, required=True),
    ExtractionField("ml_based", bool, required=True),
])


def extract_dimensions(rec: Record) -> dict:
    """Every field here is derived from the record's REAL title/abstract
    text via a transparent keyword check — not an invented technical claim
    about the paper's actual contribution."""
    text = f"{rec.title} {rec.abstract or ''}"
    lowered = text.lower()
    return {
        "approach_type": classify_approach(text),
        "targets_spectre": "spectre" in lowered,
        "targets_meltdown": "meltdown" in lowered,
        "ml_based": "machine learning" in lowered,
    }


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("Real, live arXiv search (Module 5)")
    print("=" * 70)
    query = '(abs:spectre OR abs:meltdown) AND (abs:"side channel" OR abs:"side-channel") AND cat:cs.CR'
    records, total = fetch_arxiv(query, max_results=5)
    print(f"  {len(records)} fetched, {total} total available")

    print()
    print("=" * 70)
    print("Backward snowball from a real, published DOI (Module 13)")
    print("=" * 70)
    safespec_doi = "10.1145/3316781.3317903"  # SafeSpec, real DAC 2019 paper
    snowballed = backward_snowball(safespec_doi, max_resolve=2)
    for rec in snowballed:
        print(f"  <- {rec.title!r} ({rec.year})")

    corpus, _stats = merge_sources(records, snowballed)
    dedup_result = deduplicate(corpus)
    print()
    print(f"After Module 6 dedup: {len(dedup_result.unique_records)} unique real papers")

    print()
    print("=" * 70)
    print("Comparison matrix (dimensions extracted from real title/abstract text)")
    print("=" * 70)
    extracted = []
    for rec in dedup_result.unique_records:
        dims = extract_dimensions(rec)
        extracted.append(extract(rec, COMPARISON_SCHEMA, dims))

    table = build_evidence_table(extracted, COMPARISON_SCHEMA)
    print(table.render_markdown())

    print()
    approach_counts: dict[str, int] = {}
    for row in table.to_dict_rows():
        approach_counts[row["approach_type"]] = approach_counts.get(row["approach_type"], 0) + 1
    print(f"Approach-type breakdown: {approach_counts}")


def _run_self_checks() -> None:
    assert classify_approach("A tool to detect Spectre exploitation in real time") == "detection"
    assert classify_approach("SafeSpec: Banishing the Spectre of a Meltdown with Leakage-Free Speculation") == "mitigation"
    assert classify_approach("Osiris: Automated Discovery of Microarchitectural Side Channels") == "discovery/analysis"
    assert classify_approach("A paper about something entirely unrelated") == "unspecified"

    rec = Record(title="ML-Based Detection of Spectre and Meltdown", abstract="We use machine learning to detect attacks.")
    dims = extract_dimensions(rec)
    assert dims == {
        "approach_type": "detection", "targets_spectre": True,
        "targets_meltdown": True, "ml_based": True,
    }

    extracted = extract(rec, COMPARISON_SCHEMA, dims)
    table = build_evidence_table([extracted], COMPARISON_SCHEMA)
    assert table.to_dict_rows()[0]["approach_type"] == "detection"

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

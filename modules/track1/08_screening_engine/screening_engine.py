"""
Module 8 — Title/Abstract Screening Engine

Applies an ordered list of eligibility rules to each Record, logging the
name of the FIRST rule a record fails as its exclusion reason. A record
that passes every rule is included. Output slots directly into Module 7's
PrismaFlowTracker.log_screening().
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_multi_source_aggregator"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "06_deduplication_engine"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "07_prisma_flow_tracker"))
from record_model import Record  # noqa: E402
from aggregator import fetch_arxiv, merge_sources, search_pubmed  # noqa: E402
from dedup_engine import deduplicate  # noqa: E402
from flow_tracker import PrismaFlowTracker  # noqa: E402


@dataclass
class ScreeningRule:
    name: str  # doubles as the PRISMA exclusion reason when this rule fails
    predicate: Callable[[Record], bool]  # True = record passes this rule


@dataclass
class ScreeningResult:
    included: list[Record] = field(default_factory=list)
    excluded: list[tuple[Record, str]] = field(default_factory=list)

    def excluded_by_reason(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for _rec, reason in self.excluded:
            counts[reason] = counts.get(reason, 0) + 1
        return counts


def screen(records: list[Record], rules: list[ScreeningRule]) -> ScreeningResult:
    """Applies rules in order. The FIRST rule a record fails becomes its
    logged reason — later rules are never evaluated for that record, so a
    record excluded for missing an abstract is never also blamed for
    failing a keyword check that couldn't possibly have run."""
    result = ScreeningResult()
    for rec in records:
        failed_reason = None
        for rule in rules:
            if not rule.predicate(rec):
                failed_reason = rule.name
                break
        if failed_reason is not None:
            result.excluded.append((rec, failed_reason))
        else:
            result.included.append(rec)
    return result


# --- Example rule set (a real, if simple, eligibility criteria set) --------

def has_abstract(rec: Record) -> bool:
    return bool(rec.abstract and rec.abstract.strip())


def published_2015_or_later(rec: Record) -> bool:
    return rec.year is None or rec.year >= 2015  # unknown year isn't penalized — see DECISIONS.md


def mentions_relevance_keyword(rec: Record) -> bool:
    haystack = f"{rec.title} {rec.abstract or ''}".lower()
    return any(kw in haystack for kw in ("productiv", "performance", "output"))


DEFAULT_RULES = [
    ScreeningRule("no abstract available for screening", has_abstract),
    ScreeningRule("published before 2015", published_2015_or_later),
    ScreeningRule("no productivity/performance/output keyword found", mentions_relevance_keyword),
]


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("Full pipeline: Modules 4-8 chained, real live data")
    print("=" * 70)
    pubmed_query = (
        '("knowledge workers" OR "office workers" OR employees) '
        'AND ("remote work" OR telecommut* OR "work from home" OR "hybrid work" OR MeSH:"Teleworking")'
    )
    arxiv_query = '(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)'

    pubmed_records, _t1, _t2 = search_pubmed(pubmed_query, retmax=5)
    arxiv_records, _t3 = fetch_arxiv(arxiv_query, max_results=5)
    corpus, _stats = merge_sources(pubmed_records, arxiv_records)
    dedup_result = deduplicate(corpus)

    print(f"After Modules 4-6: {len(dedup_result.unique_records)} unique records")

    result = screen(dedup_result.unique_records, DEFAULT_RULES)

    print()
    print("=" * 70)
    print("Screening decisions")
    print("=" * 70)
    for rec, reason in result.excluded:
        print(f"  EXCLUDED [{rec.source_format:>14}] ({reason}): {rec.title[:60]}")
    for rec in result.included:
        print(f"  INCLUDED [{rec.source_format:>14}]: {rec.title[:60]}")

    print()
    print(f"Excluded by reason: {result.excluded_by_reason()}")
    print(f"Included: {len(result.included)} / {len(dedup_result.unique_records)}")

    print()
    print("=" * 70)
    print("Feeding into Module 7's PrismaFlowTracker")
    print("=" * 70)
    tracker = PrismaFlowTracker()
    tracker.log_identification("PubMed", len(pubmed_records))
    tracker.log_identification("arXiv", len(arxiv_records))
    tracker.log_deduplication(len(corpus) - len(dedup_result.unique_records))
    tracker.log_screening(result.excluded_by_reason(), included_count=len(result.included))
    tracker.validate_conservation()
    print("  Conservation holds across the full Module 4-8 chain.")
    print()
    print(tracker.render_summary())

    if result.excluded_by_reason().get("no abstract available for screening", 0) > 0:
        print()
        print("NOTE: PubMed-sourced records were excluded for lacking an abstract")
        print("because Module 4 uses esummary, not efetch — a real upstream data")
        print("gap surfacing honestly at the screening stage. See DECISIONS.md.")


def _run_self_checks() -> None:
    records = [
        Record(title="Remote work boosts productivity", abstract="A study of productivity outcomes.", year=2020),
        Record(title="An old study", abstract="Discusses performance metrics.", year=2010),
        Record(title="No abstract here", abstract=None, year=2021),
        Record(title="Unrelated topic entirely", abstract="Discusses gardening techniques.", year=2022),
        Record(title="Unknown year study", abstract="Covers output measures.", year=None),
    ]
    result = screen(records, DEFAULT_RULES)

    assert [r.title for r in result.included] == ["Remote work boosts productivity", "Unknown year study"]
    reasons = {rec.title: reason for rec, reason in result.excluded}
    assert reasons["An old study"] == "published before 2015"
    assert reasons["No abstract here"] == "no abstract available for screening"
    assert reasons["Unrelated topic entirely"] == "no productivity/performance/output keyword found"
    assert result.excluded_by_reason() == {
        "published before 2015": 1,
        "no abstract available for screening": 1,
        "no productivity/performance/output keyword found": 1,
    }

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 7 — PRISMA Flow Tracker

A stateful object that logs record counts at every pipeline stage
(identification, deduplication, screening, eligibility) and can prove,
by arithmetic rather than assertion, that no record vanished unaccounted
for between stages. This is the audit trail PRISMA reporting requires.

The demo below chains real output from Modules 4, 5, and 6 — an actual
live search, merge, and dedup — into this tracker, then simulates the
screening/eligibility stages (Modules 8-9 don't exist yet) with clearly
labeled synthetic reasons.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_multi_source_aggregator"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "06_deduplication_engine"))
from aggregator import fetch_arxiv, merge_sources  # noqa: E402
from aggregator import search_pubmed  # noqa: E402
from dedup_engine import deduplicate  # noqa: E402


class FlowConservationError(ValueError):
    """Raised when a stage's counts don't add up — evidence that a record
    was silently lost (or double-counted) somewhere in the pipeline."""


@dataclass
class PrismaFlowTracker:
    identification: dict[str, int] = field(default_factory=dict)
    duplicates_removed: int = 0
    screening_excluded: dict[str, int] = field(default_factory=dict)
    screening_included: int | None = None
    eligibility_excluded: dict[str, int] = field(default_factory=dict)
    eligibility_included: int | None = None

    def log_identification(self, source: str, count: int) -> None:
        self.identification[source] = self.identification.get(source, 0) + count

    def log_deduplication(self, duplicates_removed: int) -> None:
        self.duplicates_removed += duplicates_removed

    def log_screening(self, excluded_by_reason: dict[str, int], included_count: int) -> None:
        for reason, count in excluded_by_reason.items():
            self.screening_excluded[reason] = self.screening_excluded.get(reason, 0) + count
        self.screening_included = included_count

    def log_eligibility(self, excluded_by_reason: dict[str, int], included_count: int) -> None:
        for reason, count in excluded_by_reason.items():
            self.eligibility_excluded[reason] = self.eligibility_excluded.get(reason, 0) + count
        self.eligibility_included = included_count

    # --- derived counts ---

    def total_identified(self) -> int:
        return sum(self.identification.values())

    def after_dedup(self) -> int:
        return self.total_identified() - self.duplicates_removed

    def total_screening_excluded(self) -> int:
        return sum(self.screening_excluded.values())

    def total_eligibility_excluded(self) -> int:
        return sum(self.eligibility_excluded.values())

    def validate_conservation(self) -> None:
        """Every stage's outputs must sum back to its inputs. Raises
        FlowConservationError naming exactly which stage is unbalanced."""
        if self.screening_included is not None:
            expected = self.after_dedup()
            actual = self.screening_included + self.total_screening_excluded()
            if actual != expected:
                raise FlowConservationError(
                    f"screening stage: {expected} entered but {actual} accounted for "
                    f"({self.screening_included} included + {self.total_screening_excluded()} excluded)"
                )
        if self.eligibility_included is not None:
            if self.screening_included is None:
                raise FlowConservationError("eligibility stage logged before screening stage")
            expected = self.screening_included
            actual = self.eligibility_included + self.total_eligibility_excluded()
            if actual != expected:
                raise FlowConservationError(
                    f"eligibility stage: {expected} entered but {actual} accounted for "
                    f"({self.eligibility_included} included + {self.total_eligibility_excluded()} excluded)"
                )

    def render_summary(self) -> str:
        lines = ["PRISMA Flow Summary", "=" * 40]
        for source, count in self.identification.items():
            lines.append(f"  Identified from {source}: {count}")
        lines.append(f"  Total identified: {self.total_identified()}")
        lines.append(f"  Duplicates removed: {self.duplicates_removed}")
        lines.append(f"  Records screened (after dedup): {self.after_dedup()}")
        if self.screening_included is not None:
            for reason, count in self.screening_excluded.items():
                lines.append(f"    Excluded at screening ({reason}): {count}")
            lines.append(f"  Passed screening: {self.screening_included}")
        if self.eligibility_included is not None:
            for reason, count in self.eligibility_excluded.items():
                lines.append(f"    Excluded at eligibility ({reason}): {count}")
            lines.append(f"  INCLUDED (final): {self.eligibility_included}")
        return "\n".join(lines)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    tracker = PrismaFlowTracker()

    print("=" * 70)
    print("Stage 1: Identification — real live calls, reusing Modules 4-5")
    print("=" * 70)
    pubmed_query = (
        '("knowledge workers" OR "office workers" OR employees) '
        'AND ("remote work" OR telecommut* OR "work from home" OR "hybrid work" OR MeSH:"Teleworking")'
    )
    arxiv_query = '(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)'

    pubmed_records, _pm_total, _t = search_pubmed(pubmed_query, retmax=5)
    arxiv_records, _ax_total = fetch_arxiv(arxiv_query, max_results=5)
    tracker.log_identification("PubMed", len(pubmed_records))
    tracker.log_identification("arXiv", len(arxiv_records))
    print(f"  PubMed: {len(pubmed_records)} records retrieved")
    print(f"  arXiv: {len(arxiv_records)} records retrieved")

    print()
    print("=" * 70)
    print("Stage 2: Deduplication — real, reusing Module 6")
    print("=" * 70)
    corpus, _stats = merge_sources(pubmed_records, arxiv_records)
    dedup_result = deduplicate(corpus)
    duplicates_removed = len(corpus) - len(dedup_result.unique_records)
    tracker.log_deduplication(duplicates_removed)
    print(f"  {len(corpus)} merged -> {duplicates_removed} duplicates removed -> {len(dedup_result.unique_records)} unique")

    print()
    print("=" * 70)
    print("Stage 3: Screening — SIMULATED (Module 8 doesn't exist yet)")
    print("=" * 70)
    n = len(dedup_result.unique_records)
    excluded_wrong_population = n // 3
    excluded_wrong_design = n // 4
    included = n - excluded_wrong_population - excluded_wrong_design
    tracker.log_screening(
        {"wrong population": excluded_wrong_population, "wrong study design": excluded_wrong_design},
        included_count=included,
    )
    print(f"  (synthetic split of {n} real records for demonstration purposes)")
    print(f"  wrong population: {excluded_wrong_population}, wrong design: {excluded_wrong_design}, passed: {included}")

    print()
    print("=" * 70)
    print("Validating conservation...")
    print("=" * 70)
    tracker.validate_conservation()
    print("  OK — every stage's counts are fully accounted for.")

    print()
    print(tracker.render_summary())

    print()
    print("=" * 70)
    print("Now deliberately breaking conservation to show it gets caught")
    print("=" * 70)
    broken = PrismaFlowTracker()
    broken.log_identification("SourceA", 10)
    broken.log_deduplication(2)
    broken.log_screening({"reason": 3}, included_count=4)  # 3+4=7, but 8 entered -> mismatch
    try:
        broken.validate_conservation()
        print("  (no error raised — this would be a bug)")
    except FlowConservationError as e:
        print(f"  Raised as expected: {e}")


def _run_self_checks() -> None:
    t = PrismaFlowTracker()
    t.log_identification("A", 10)
    t.log_identification("B", 5)
    assert t.total_identified() == 15
    t.log_deduplication(3)
    assert t.after_dedup() == 12
    t.log_screening({"x": 4, "y": 2}, included_count=6)
    assert t.total_screening_excluded() == 6
    t.validate_conservation()  # 4+2+6 == 12, should not raise

    t.log_eligibility({"z": 1}, included_count=5)
    t.validate_conservation()  # 1+5 == 6, should not raise

    bad = PrismaFlowTracker()
    bad.log_identification("A", 10)
    bad.log_deduplication(0)
    bad.log_screening({"x": 3}, included_count=3)  # 3+3=6 != 10
    try:
        bad.validate_conservation()
        raise AssertionError("expected FlowConservationError")
    except FlowConservationError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

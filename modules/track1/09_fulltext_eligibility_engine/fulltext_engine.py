"""
Module 9 — Full-Text Eligibility Engine

A second screening pass, run only on records that already passed Module 8's
title/abstract screen. Full-text retrieval itself (downloading and parsing
PDFs) is out of this course's stated scope — see the ROADMAP's Tools/
Architecture Target. This module takes full text as already-supplied
plain-text input (open-access text or user-supplied text) and proves that
details invisible in an abstract can still disqualify a record.

The three example records below are clearly fictional (following this
course's established Smith/2023-style running examples), not claims about
any real paper's actual content — Modules 4-5's real fetched records don't
have real full text available to this course, and inventing full-text
content for an actual real paper would misrepresent that paper.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
from record_model import Record  # noqa: E402


@dataclass
class FullTextRecord:
    record: Record
    full_text: str


@dataclass
class EligibilityRule:
    name: str  # doubles as the PRISMA exclusion reason when this rule fails
    predicate: Callable[[FullTextRecord], bool]  # True = passes this rule


@dataclass
class EligibilityResult:
    included: list[Record] = field(default_factory=list)
    excluded: list[tuple[Record, str]] = field(default_factory=list)

    def excluded_by_reason(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for _rec, reason in self.excluded:
            counts[reason] = counts.get(reason, 0) + 1
        return counts


def screen_full_text(items: list[FullTextRecord], rules: list[EligibilityRule]) -> EligibilityResult:
    """Same first-failing-rule-wins shape as Module 8's screen(), applied
    to full text instead of title/abstract."""
    result = EligibilityResult()
    for item in items:
        failed_reason = None
        for rule in rules:
            if not rule.predicate(item):
                failed_reason = rule.name
                break
        if failed_reason is not None:
            result.excluded.append((item.record, failed_reason))
        else:
            result.included.append(item.record)
    return result


# --- Example rules -----------------------------------------------------

def population_is_knowledge_workers(item: FullTextRecord) -> bool:
    text = item.full_text.lower()
    disqualifying_population_terms = ("undergraduate", "university students", "high school")
    return not any(term in text for term in disqualifying_population_terms)


def design_is_comparative(item: FullTextRecord) -> bool:
    text = item.full_text.lower()
    qualitative_only_marker = "semi-structured interviews" in text
    comparative_marker = any(term in text for term in ("compared to", "measured output", "randomly assigned"))
    return not (qualitative_only_marker and not comparative_marker)


DEFAULT_RULES = [
    EligibilityRule("population confirmed as students, not knowledge workers, upon reading full text", population_is_knowledge_workers),
    EligibilityRule("full text reveals qualitative-only design, not eligible for this quantitative synthesis", design_is_comparative),
]


# --- Demo (fictional example records — see module docstring) --------------

def _run_demo() -> None:
    items = [
        FullTextRecord(
            record=Record(
                title="Remote Work Arrangements and Team Output in Technology Firms",
                authors=["Bekele, Marta"], year=2021, doi="10.9999/fake-a",
            ),
            full_text=(
                "Abstract: We examine how remote work arrangements relate to team output... "
                "Methods: We conducted semi-structured interviews with 12 remote employees "
                "to explore their subjective experience of productivity and collaboration."
            ),
        ),
        FullTextRecord(
            record=Record(
                title="Productivity Effects of Flexible Work Policies Among University Students",
                authors=["Ferreira, Lucas"], year=2022, doi="10.9999/fake-b",
            ),
            full_text=(
                "Abstract: This study explores flexible scheduling and academic output... "
                "Methods: We surveyed 340 undergraduate students at a large public university "
                "about their study habits under flexible scheduling, measuring self-reported output."
            ),
        ),
        FullTextRecord(
            record=Record(
                title="A Longitudinal Comparison of Remote and In-Office Knowledge Worker Output",
                authors=["Osei, Kwame", "Duarte, Ines"], year=2023, doi="10.9999/fake-c",
            ),
            full_text=(
                "Abstract: We compare productivity outcomes between remote and in-office "
                "knowledge workers over a 12-month period... "
                "Methods: We compared productivity output of 210 knowledge workers randomly "
                "assigned to remote or in-office conditions over 12 months, measuring output per hour."
            ),
        ),
    ]

    print("These three records ALL passed a hypothetical title/abstract screen")
    print("(all three abstracts sound on-topic and relevant). Full text tells a")
    print("different story for two of them:")
    print()

    result = screen_full_text(items, DEFAULT_RULES)

    for rec, reason in result.excluded:
        print(f"  EXCLUDED: {rec.title}")
        print(f"    reason: {reason}")
    for rec in result.included:
        print(f"  INCLUDED: {rec.title}")

    print()
    print(f"Excluded by reason: {result.excluded_by_reason()}")
    print(f"Included: {len(result.included)} / {len(items)}")


def _run_self_checks() -> None:
    items = [
        FullTextRecord(
            Record(title="A"),
            "Methods: semi-structured interviews with participants about their experience.",
        ),
        FullTextRecord(
            Record(title="B"),
            "Methods: surveyed undergraduate students, measured output.",
        ),
        FullTextRecord(
            Record(title="C"),
            "Methods: compared output of workers randomly assigned to two conditions.",
        ),
    ]
    result = screen_full_text(items, DEFAULT_RULES)
    assert [r.title for r in result.included] == ["C"]
    reasons = {rec.title: reason for rec, reason in result.excluded}
    assert reasons["A"] == "full text reveals qualitative-only design, not eligible for this quantitative synthesis"
    assert reasons["B"] == "population confirmed as students, not knowledge workers, upon reading full text"

    # A record with BOTH disqualifying markers is still caught by the
    # first rule in order (population), never reaching the design rule.
    both = FullTextRecord(Record(title="D"), "Methods: semi-structured interviews with undergraduate students.")
    result2 = screen_full_text([both], DEFAULT_RULES)
    assert result2.excluded[0][1] == "population confirmed as students, not knowledge workers, upon reading full text"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

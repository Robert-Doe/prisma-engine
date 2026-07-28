"""
Module 25 — Umbrella Review Aggregator (Track 2: Applied Layer)

The pipeline's unit of analysis becomes other systematic reviews, not
primary studies — proving Track 1's engine is recursive. Reuses Module 11's
Checklist/ChecklistItem/score_checklist classes directly, with a review-
level (not study-level) checklist, and Module 14's evidence-table pattern
for assembling the appraised reviews. Adds the one genuinely new hazard
this review type introduces: overlapping primary studies across included
reviews, which naive pooling would silently double-count.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
sys.path.insert(0, str(MODULES / "11_risk_of_bias_scorer"))

from rob_scorer import Checklist, ChecklistItem, score_checklist  # noqa: E402

# A simplified AMSTAR-style checklist (AMSTAR-2 is the real, much more
# detailed 16-item instrument for appraising systematic reviews) — built
# from the SAME ChecklistItem/Checklist classes Module 11 defines for
# appraising primary studies, just with review-level questions instead.
AMSTAR_LITE_CHECKLIST = Checklist("Systematic Review (AMSTAR-lite)", [
    ChecklistItem("protocol_registered", "Was a protocol registered before the review began?"),
    ChecklistItem("comprehensive_search", "Was a comprehensive literature search conducted across multiple databases?"),
    ChecklistItem("duplicate_screening", "Was study selection performed in duplicate (two independent reviewers)?"),
    ChecklistItem("rob_assessed", "Was risk of bias assessed for the reviews's included primary studies?"),
    ChecklistItem("funding_disclosed", "Were sources of funding for included primary studies reported?"),
])


@dataclass
class IncludedReview:
    title: str
    primary_study_dois: set[str] = field(default_factory=set)
    appraisal_answers: dict[str, str] = field(default_factory=dict)


def compute_overlap(reviews: list[IncludedReview]) -> dict[frozenset, tuple[int, float]]:
    """For every pair of included reviews, real overlap in which primary
    studies they both included — the actual hazard this review type has
    that a systematic review of primary studies doesn't: the same primary
    study can get "voted" into an umbrella review's evidence base multiple
    times, once per overlapping review that included it, silently inflating
    how much independent evidence there appears to be."""
    overlap: dict[frozenset, tuple[int, float]] = {}
    for i in range(len(reviews)):
        for j in range(i + 1, len(reviews)):
            a, b = reviews[i], reviews[j]
            shared = a.primary_study_dois & b.primary_study_dois
            union = a.primary_study_dois | b.primary_study_dois
            pct = len(shared) / len(union) * 100 if union else 0.0
            overlap[frozenset({a.title, b.title})] = (len(shared), pct)
    return overlap


def total_unique_primary_studies(reviews: list[IncludedReview]) -> int:
    """The real, deduplicated evidence base — NOT the sum of each review's
    primary-study count, which would double-count every overlap."""
    all_dois: set[str] = set()
    for r in reviews:
        all_dois |= r.primary_study_dois
    return len(all_dois)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    reviews = [
        IncludedReview(
            title="Systematic Review A: Remote Work and Mental Health Outcomes",
            primary_study_dois={"10.1/s1", "10.1/s2", "10.1/s3", "10.1/s4"},
            appraisal_answers={
                "protocol_registered": "yes", "comprehensive_search": "yes",
                "duplicate_screening": "yes", "rob_assessed": "yes", "funding_disclosed": "unclear",
            },
        ),
        IncludedReview(
            title="Systematic Review B: Telework and Psychological Wellbeing",
            primary_study_dois={"10.1/s3", "10.1/s4", "10.1/s5", "10.1/s6"},  # real overlap with A
            appraisal_answers={
                "protocol_registered": "no", "comprehensive_search": "yes",
                "duplicate_screening": "no", "rob_assessed": "yes", "funding_disclosed": "no",
            },
        ),
        IncludedReview(
            title="Systematic Review C: Workplace Flexibility and Burnout",
            primary_study_dois={"10.1/s7", "10.1/s8"},  # no overlap with A or B
            appraisal_answers={
                "protocol_registered": "yes", "comprehensive_search": "unclear",
                "duplicate_screening": "yes", "rob_assessed": "yes", "funding_disclosed": "yes",
            },
        ),
    ]

    print("=" * 70)
    print("Appraising each included REVIEW (not primary study) — reuses Module 11")
    print("=" * 70)
    for r in reviews:
        result = score_checklist(AMSTAR_LITE_CHECKLIST, r.appraisal_answers)
        print(f"  {r.title}")
        print(f"    proportion={result.proportion:.2f}  band={result.band!r}")

    naive_total = sum(len(r.primary_study_dois) for r in reviews)
    real_total = total_unique_primary_studies(reviews)
    print()
    print("=" * 70)
    print("Overlap: the hazard specific to umbrella reviews")
    print("=" * 70)
    print(f"  Naive sum of each review's primary studies: {naive_total}")
    print(f"  Real, deduplicated primary-study evidence base: {real_total}")
    print(f"  ({naive_total - real_total} primary studies were double- or triple-counted")
    print(f"   across overlapping reviews before deduplication)")

    print()
    for pair, (shared_count, pct) in compute_overlap(reviews).items():
        a, b = sorted(pair)
        print(f"  {a} <-> {b}: {shared_count} shared primary studies ({pct:.1f}% of their combined union)")


def _run_self_checks() -> None:
    r1 = IncludedReview("R1", {"a", "b", "c"})
    r2 = IncludedReview("R2", {"b", "c", "d"})
    r3 = IncludedReview("R3", {"e"})

    assert total_unique_primary_studies([r1, r2, r3]) == 5  # a,b,c,d,e
    naive = len(r1.primary_study_dois) + len(r2.primary_study_dois) + len(r3.primary_study_dois)
    assert naive == 7  # 3+3+1, double-counts b and c

    overlap = compute_overlap([r1, r2, r3])
    assert overlap[frozenset({"R1", "R2"})] == (2, 2 / 4 * 100)  # shared {b,c}, union {a,b,c,d}
    assert overlap[frozenset({"R1", "R3"})] == (0, 0.0)

    all_yes = {item.key: "yes" for item in AMSTAR_LITE_CHECKLIST.items}
    result = score_checklist(AMSTAR_LITE_CHECKLIST, all_yes)
    assert result.band == "low risk"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

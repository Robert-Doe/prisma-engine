"""
Module 22 — Rapid Review Adapter (Track 2: Applied Layer)

Wraps Track 1's real modules under a time-boxed configuration: single
source instead of multiple, single-reviewer screening instead of dual, a
reduced risk-of-bias checklist instead of the full one. The discipline
that makes this a "rapid review" and not just a sloppy systematic review
is RapidReviewLog — every simplification is logged with what standard
practice it replaces and why, never applied silently.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
for name in ["04_live_api_connector", "05_multi_source_aggregator",
             "08_screening_engine", "11_risk_of_bias_scorer", "12_prisma_diagram_generator",
             "07_prisma_flow_tracker"]:
    sys.path.insert(0, str(MODULES / name))

from aggregator import search_pubmed  # noqa: E402
from screening_engine import screen, DEFAULT_RULES  # noqa: E402
from rob_scorer import Checklist, ChecklistItem, score_checklist  # noqa: E402
from flow_tracker import PrismaFlowTracker  # noqa: E402
from diagram_generator import render_prisma_svg, save_svg  # noqa: E402


@dataclass
class Simplification:
    stage: str
    standard_practice: str
    rapid_practice: str
    rationale: str


@dataclass
class RapidReviewLog:
    simplifications: list[Simplification] = field(default_factory=list)

    def add(self, stage: str, standard_practice: str, rapid_practice: str, rationale: str) -> None:
        self.simplifications.append(Simplification(stage, standard_practice, rapid_practice, rationale))

    def render(self) -> str:
        lines = ["Rapid Review — Documented Methodology Simplifications", "=" * 55]
        for s in self.simplifications:
            lines.append(f"\n[{s.stage}]")
            lines.append(f"  Standard practice: {s.standard_practice}")
            lines.append(f"  This review did:   {s.rapid_practice}")
            lines.append(f"  Why:               {s.rationale}")
        return "\n".join(lines)


# A reduced 2-domain risk-of-bias checklist, built from the SAME
# ChecklistItem class Module 11 defines — just fewer items than
# Module 11's full RCT_CHECKLIST.
REDUCED_RCT_CHECKLIST = Checklist("RCT (rapid, reduced)", [
    ChecklistItem("random_sequence", "Was the allocation sequence adequately randomized?"),
    ChecklistItem("blinding", "Were participants/outcome assessors blinded to group assignment?"),
])


def run_rapid_review(query: str, retmax: int = 5) -> tuple[list, RapidReviewLog]:
    log = RapidReviewLog()

    log.add(
        stage="Identification",
        standard_practice="Multiple databases searched (Module 5's default: PubMed + arXiv)",
        rapid_practice="Single source searched (PubMed only)",
        rationale="Time constraint — a single-source search cuts search and screening time "
                  "substantially, at a real, acknowledged cost to coverage.",
    )
    records, total_count, _translation = search_pubmed(query, retmax=retmax)

    log.add(
        stage="Screening",
        standard_practice="Independent dual review with reconciliation (not built until a real "
                          "team workflow exists; Module 8's screen() run twice by different people)",
        rapid_practice="Single-reviewer screening (Module 8's screen() run once)",
        rationale="Time constraint — dual independent screening roughly doubles screening time; "
                  "single-reviewer screening is faster but loses the inter-reviewer check that "
                  "catches individual screening mistakes.",
    )
    screening_result = screen(records, DEFAULT_RULES)

    log.add(
        stage="Quality appraisal",
        standard_practice="Full 5-domain RCT checklist (Module 11's RCT_CHECKLIST: random sequence, "
                          "allocation concealment, blinding, incomplete data, selective reporting)",
        rapid_practice="Reduced 2-domain checklist (random sequence, blinding only)",
        rationale="Time constraint — appraising every included study against 2 domains instead of "
                  "5 is faster per study; the tradeoff is real, since a study weak on an unassessed "
                  "domain (e.g. selective reporting) would not be flagged by this review.",
    )

    return screening_result.included, log


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    query = '"remote work"[tiab] AND productivity[tiab]'
    print("=" * 70)
    print("Running a time-boxed rapid review...")
    print("=" * 70)
    included, log = run_rapid_review(query, retmax=5)

    print(f"\n{len(included)} records passed rapid screening.")
    if not included:
        print("(0 is expected here, not a bug: DEFAULT_RULES from Module 8 excludes any")
        print(" record with no abstract, and PubMed's esummary — reused unchanged from")
        print(" Module 4 — never returns one. The same real limitation from Module 8's")
        print(" own demo carries through here, since this module reuses that exact code.)")
    print()
    print(log.render())

    print()
    print("=" * 70)
    print("The reduced risk-of-bias checklist, applied to one fictional study")
    print("=" * 70)
    answers = {"random_sequence": "yes", "blinding": "no"}
    result = score_checklist(REDUCED_RCT_CHECKLIST, answers)
    print(f"  proportion = {result.proportion:.2f}  band = {result.band!r}")
    print("  NOTE: this study's selective-reporting risk was never assessed at all —")
    print("  not scored as low risk, simply never checked. A reader of this rapid")
    print("  review's appraisal needs the methodology log above to know that.")


def _run_self_checks() -> None:
    log = RapidReviewLog()
    log.add("Stage A", "standard X", "rapid Y", "because Z")
    assert len(log.simplifications) == 1
    rendered = log.render()
    assert "Stage A" in rendered and "standard X" in rendered and "rapid Y" in rendered

    assert len(REDUCED_RCT_CHECKLIST.items) == 2
    assert {i.key for i in REDUCED_RCT_CHECKLIST.items} == {"random_sequence", "blinding"}

    all_yes = {"random_sequence": "yes", "blinding": "yes"}
    result = score_checklist(REDUCED_RCT_CHECKLIST, all_yes)
    assert result.proportion == 1.0
    assert result.band == "low risk"

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 11 — Risk-of-Bias / Quality Appraisal Scorer

Checklist-based appraisal, branched by study design (see Prerequisite 4):
an RCT and a qualitative study get evaluated against different questions,
because "was blinding used" isn't a meaningful question for an interview
study. Each checklist item is answered "yes"/"unclear"/"no" and averaged
into a proportion and a band.

This module's averaging approach is a deliberate teaching simplification,
NOT a reimplementation of the real Cochrane RoB2 algorithm — see
DECISIONS.md for why real Cochrane RoB2 explicitly avoids simple averaging,
and why that critique applies to this module's own design too.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_ANSWERS = {"yes", "unclear", "no"}
_WEIGHTS = {"yes": 1.0, "unclear": 0.5, "no": 0.0}


class InvalidAnswerError(ValueError):
    """Raised when a checklist item is unanswered, or answered with
    something other than 'yes' / 'unclear' / 'no'."""


@dataclass
class ChecklistItem:
    key: str
    question: str


@dataclass
class Checklist:
    study_design: str
    items: list[ChecklistItem] = field(default_factory=list)


# Simplified checklists, inspired by real domains from Cochrane RoB2 (RCTs)
# and CASP (cohort / qualitative) — condensed for teaching, not a verbatim
# reproduction of either tool's full signalling-question set.

RCT_CHECKLIST = Checklist("RCT", [
    ChecklistItem("random_sequence", "Was the allocation sequence adequately randomized?"),
    ChecklistItem("allocation_concealment", "Was allocation adequately concealed until assignment?"),
    ChecklistItem("blinding", "Were participants/outcome assessors blinded to group assignment?"),
    ChecklistItem("incomplete_data", "Were incomplete outcome data adequately addressed?"),
    ChecklistItem("selective_reporting", "Is the study free of selective outcome reporting?"),
])

COHORT_CHECKLIST = Checklist("cohort", [
    ChecklistItem("representative_exposed", "Was the exposed cohort representative of the target population?"),
    ChecklistItem("comparability", "Were exposed/unexposed groups comparable (key confounders controlled)?"),
    ChecklistItem("outcome_assessment", "Was outcome assessment adequate (objective or blinded)?"),
    ChecklistItem("followup_adequate", "Was follow-up long enough and complete enough for outcomes to occur?"),
])

QUALITATIVE_CHECKLIST = Checklist("qualitative", [
    ChecklistItem("clear_aims", "Was there a clear statement of the research aims?"),
    ChecklistItem("appropriate_methodology", "Is a qualitative methodology appropriate for these aims?"),
    ChecklistItem("appropriate_design", "Was the research design appropriate to address the aims?"),
    ChecklistItem("rigorous_analysis", "Was the data analysis sufficiently rigorous?"),
])

CHECKLISTS_BY_DESIGN = {
    "RCT": RCT_CHECKLIST,
    "cohort": COHORT_CHECKLIST,
    "qualitative": QUALITATIVE_CHECKLIST,
}


@dataclass
class AppraisalResult:
    study_design: str
    answers: dict[str, str]
    proportion: float
    band: str  # "low risk" | "some concerns" | "high risk"
    lowest_scoring_item: str  # the single worst-answered item — see DECISIONS.md


def score_checklist(checklist: Checklist, answers: dict[str, str]) -> AppraisalResult:
    for item in checklist.items:
        if item.key not in answers:
            raise InvalidAnswerError(f'no answer given for "{item.key}" ({item.question})')
        if answers[item.key] not in VALID_ANSWERS:
            raise InvalidAnswerError(
                f'answer for "{item.key}" must be one of {sorted(VALID_ANSWERS)}, got {answers[item.key]!r}'
            )

    weighted = [(item.key, _WEIGHTS[answers[item.key]]) for item in checklist.items]
    proportion = sum(w for _k, w in weighted) / len(weighted)
    band = "low risk" if proportion >= 0.8 else "some concerns" if proportion >= 0.5 else "high risk"
    lowest_key = min(weighted, key=lambda kv: kv[1])[0]

    return AppraisalResult(
        study_design=checklist.study_design,
        answers=dict(answers),
        proportion=proportion,
        band=band,
        lowest_scoring_item=lowest_key,
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("Example 1: RCT with one seriously weak domain, four strong ones")
    print("=" * 70)
    answers = {
        "random_sequence": "yes",
        "allocation_concealment": "yes",
        "blinding": "no",  # no blinding at all — a serious, specific problem
        "incomplete_data": "yes",
        "selective_reporting": "yes",
    }
    result = score_checklist(RCT_CHECKLIST, answers)
    print(f"  proportion: {result.proportion:.2f}  band: {result.band!r}")
    print(f"  weakest domain: {result.lowest_scoring_item}")
    print(f"  NOTE: averaging rates this {result.band!r} — the missing blinding on")
    print("  its own is a serious, specific problem a real Cochrane RoB2 assessor")
    print("  would weigh heavily, but four strong domains pull the average high")
    print("  enough to hide it. See DECISIONS.md for why this is a known, real")
    print("  weakness of simple averaging, not a quirk of this module's numbers.")

    print()
    print("=" * 70)
    print("Example 2: Qualitative study, branch on design")
    print("=" * 70)
    qual_answers = {
        "clear_aims": "yes",
        "appropriate_methodology": "yes",
        "appropriate_design": "unclear",
        "rigorous_analysis": "yes",
    }
    qual_result = score_checklist(QUALITATIVE_CHECKLIST, qual_answers)
    print(f"  proportion: {qual_result.proportion:.2f}  band: {qual_result.band!r}")

    print()
    print("=" * 70)
    print("Example 3: missing/invalid answers are caught, not silently scored")
    print("=" * 70)
    try:
        score_checklist(RCT_CHECKLIST, {"random_sequence": "yes"})
    except InvalidAnswerError as e:
        print(f"  missing answer caught: {e}")
    try:
        score_checklist(RCT_CHECKLIST, {**answers, "blinding": "sort of"})
    except InvalidAnswerError as e:
        print(f"  invalid answer caught: {e}")


def _run_self_checks() -> None:
    all_yes = {item.key: "yes" for item in RCT_CHECKLIST.items}
    result = score_checklist(RCT_CHECKLIST, all_yes)
    assert result.proportion == 1.0
    assert result.band == "low risk"

    all_no = {item.key: "no" for item in RCT_CHECKLIST.items}
    result2 = score_checklist(RCT_CHECKLIST, all_no)
    assert result2.proportion == 0.0
    assert result2.band == "high risk"

    mixed = {**all_yes, "blinding": "no"}
    result3 = score_checklist(RCT_CHECKLIST, mixed)
    assert result3.proportion == 0.8, result3.proportion
    assert result3.band == "low risk"  # exactly the averaging weakness this module documents
    assert result3.lowest_scoring_item == "blinding"

    try:
        score_checklist(RCT_CHECKLIST, {})
        raise AssertionError("expected InvalidAnswerError for missing answers")
    except InvalidAnswerError:
        pass

    try:
        score_checklist(RCT_CHECKLIST, {**all_yes, "blinding": "maybe"})
        raise AssertionError("expected InvalidAnswerError for invalid answer value")
    except InvalidAnswerError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

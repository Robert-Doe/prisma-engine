"""
Module 1 — Research Question Formalizer

Turns a free-text research question into a structured, machine-checkable
specification under one of three frameworks: PICO, PEO, SPIDER.

This module does NOT contain a trained NLP model. Framework suggestion and
comparison-term extraction are deterministic keyword heuristics, clearly
labeled as suggestions a human confirms or overrides — never treated as
ground truth. See DECISIONS.md for why.
"""

from dataclasses import dataclass, field
from enum import Enum
import re


class Framework(str, Enum):
    PICO = "PICO"
    PEO = "PEO"
    SPIDER = "SPIDER"


FRAMEWORK_SLOTS: dict[Framework, list[str]] = {
    Framework.PICO: ["population", "intervention", "comparison", "outcome"],
    Framework.PEO: ["population", "exposure", "outcome"],
    Framework.SPIDER: [
        "sample",
        "phenomenon_of_interest",
        "design",
        "evaluation",
        "research_type",
    ],
}

SLOT_DESCRIPTIONS: dict[str, str] = {
    "population": "Who or what is being studied",
    "intervention": "The thing being done to the population",
    "comparison": "What the intervention is measured against",
    "outcome": "What is actually being measured",
    "exposure": "The exposure being studied (no intervention was assigned)",
    "sample": "Who was studied (qualitative — purposive, not representative)",
    "phenomenon_of_interest": "The experience or behavior being examined",
    "design": "How the studies gathered data",
    "evaluation": "What outcome or finding type is relevant",
    "research_type": "qualitative / quantitative / mixed",
}


class MissingSlotsError(ValueError):
    """Raised when a ResearchQuestion is validated before every required
    slot for its framework has been filled."""

    def __init__(self, framework: Framework, missing: list[str]):
        self.framework = framework
        self.missing = missing
        super().__init__(
            f"{framework.value} requires {FRAMEWORK_SLOTS[framework]}; "
            f"missing: {missing}"
        )


# --- Heuristic framework suggestion -------------------------------------
# Deterministic keyword matching, not a trained classifier. Order matters:
# SPIDER and PEO markers are checked first because their vocabulary is more
# specific; PICO is the default because most research questions are shaped
# like PICO questions and it's the safer fallback to put in front of a
# human for confirmation.

_SPIDER_MARKERS = [
    "experience", "perceive", "perception", "meaning", "feel", "lived",
    "perspective",
]
_PEO_MARKERS = ["exposed", "exposure", "associated with", "risk of", "linked to"]


def _first_match(text: str, markers: list[str]) -> str | None:
    lowered = text.lower()
    for marker in markers:
        if marker in lowered:
            return marker
    return None


def suggest_framework_verbose(question_text: str) -> tuple[Framework, str]:
    """Returns (suggested framework, human-readable reason)."""
    spider_hit = _first_match(question_text, _SPIDER_MARKERS)
    if spider_hit:
        return Framework.SPIDER, f'matched SPIDER marker "{spider_hit}"'

    peo_hit = _first_match(question_text, _PEO_MARKERS)
    if peo_hit:
        return Framework.PEO, f'matched PEO marker "{peo_hit}"'

    return Framework.PICO, "no SPIDER/PEO marker found — defaulting to PICO"


def suggest_framework(question_text: str) -> Framework:
    framework, _reason = suggest_framework_verbose(question_text)
    return framework


# --- Candidate comparison-term extraction --------------------------------
# Also a heuristic: splits the raw text on common comparison connectives to
# suggest (not decide) a Comparison slot value for PICO questions.

_COMPARISON_SPLIT_RE = re.compile(r"\bcompared to\b|\bversus\b|\bvs\.?\b", re.IGNORECASE)


def suggest_comparison(question_text: str) -> str | None:
    parts = _COMPARISON_SPLIT_RE.split(question_text)
    if len(parts) >= 2:
        return parts[-1].strip().rstrip("?.")
    return None


@dataclass
class ResearchQuestion:
    raw_text: str
    framework: Framework
    slots: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        required = FRAMEWORK_SLOTS[self.framework]
        missing = [s for s in required if not self.slots.get(s, "").strip()]
        if missing:
            raise MissingSlotsError(self.framework, missing)

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "framework": self.framework.value,
            "slots": dict(self.slots),
        }

    def render_summary(self) -> str:
        lines = [f"[{self.framework.value}] {self.raw_text}"]
        for slot in FRAMEWORK_SLOTS[self.framework]:
            value = self.slots.get(slot, "<missing>")
            lines.append(f"  {slot:>22}: {value}")
        return "\n".join(lines)


def formalize(
    question_text: str,
    framework: Framework | None = None,
    slots: dict[str, str] | None = None,
) -> ResearchQuestion:
    """Build and validate a ResearchQuestion. Raises MissingSlotsError if
    the given slots don't cover every field the framework requires."""
    framework = framework or suggest_framework(question_text)
    slots = dict(slots or {})

    if framework == Framework.PICO and "comparison" not in slots:
        suggested = suggest_comparison(question_text)
        if suggested:
            slots["comparison"] = suggested

    rq = ResearchQuestion(raw_text=question_text, framework=framework, slots=slots)
    rq.validate()
    return rq


# --- Demo / self-check ----------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("EXAMPLE 1 — PICO question, comparison auto-suggested")
    print("=" * 70)
    q1_text = "Does remote work affect employee productivity compared to in-office work?"
    framework, reason = suggest_framework_verbose(q1_text)
    print(f"Question: {q1_text}")
    print(f"Suggested framework: {framework.value}  ({reason})")
    q1 = formalize(
        q1_text,
        framework=framework,
        slots={
            "population": "knowledge workers",
            "intervention": "remote work arrangements",
            "outcome": "measured or self-reported productivity",
        },
    )
    print()
    print(q1.render_summary())

    print()
    print("=" * 70)
    print("EXAMPLE 2 — PEO question")
    print("=" * 70)
    q2_text = "What is the risk of burnout associated with excessive screen time among remote workers?"
    framework, reason = suggest_framework_verbose(q2_text)
    print(f"Question: {q2_text}")
    print(f"Suggested framework: {framework.value}  ({reason})")
    q2 = formalize(
        q2_text,
        framework=framework,
        slots={
            "population": "remote workers",
            "exposure": "excessive screen time",
            "outcome": "burnout",
        },
    )
    print()
    print(q2.render_summary())

    print()
    print("=" * 70)
    print("EXAMPLE 3 — SPIDER question")
    print("=" * 70)
    q3_text = "How do new remote workers experience isolation during their first year?"
    framework, reason = suggest_framework_verbose(q3_text)
    print(f"Question: {q3_text}")
    print(f"Suggested framework: {framework.value}  ({reason})")
    q3 = formalize(
        q3_text,
        framework=framework,
        slots={
            "sample": "new remote workers, first year of employment",
            "phenomenon_of_interest": "isolation",
            "design": "semi-structured interviews",
            "evaluation": "thematic description of isolation experiences",
            "research_type": "qualitative",
        },
    )
    print()
    print(q3.render_summary())

    print()
    print("=" * 70)
    print("EXAMPLE 4 — validation catching an incomplete question")
    print("=" * 70)
    q4_text = "Does remote work affect employee productivity?"
    print(f"Question: {q4_text}")
    print('Slots given: {"population": "knowledge workers"}  (outcome missing on purpose)')
    try:
        formalize(q4_text, slots={"population": "knowledge workers"})
    except MissingSlotsError as e:
        print(f"Raised MissingSlotsError as expected: {e}")


def _run_self_checks() -> None:
    # Framework suggestion is deterministic and correctly routes each
    # worked example to the framework a human would pick by hand.
    assert suggest_framework("Does X affect Y compared to Z?") == Framework.PICO
    assert suggest_framework("What is the risk of X associated with Y?") == Framework.PEO
    assert suggest_framework("How do people experience X?") == Framework.SPIDER

    # Comparison auto-suggestion strips trailing punctuation correctly.
    assert suggest_comparison("Does X affect Y compared to Z?") == "Z"
    assert suggest_comparison("Does X affect Y versus Z.") == "Z"
    assert suggest_comparison("No comparison connective here.") is None

    # A fully-slotted PICO question validates without raising.
    rq = formalize(
        "Does X affect Y compared to Z?",
        slots={"population": "P", "intervention": "I", "outcome": "O"},
    )
    assert rq.slots["comparison"] == "Z"

    # An incomplete question raises MissingSlotsError naming exactly the
    # missing slots, not a generic failure. No comparison connective is
    # present here, so "comparison" is never auto-filled either.
    try:
        formalize(
            "Does X affect Y?",
            slots={"population": "P", "intervention": "I"},
        )
        raise AssertionError("expected MissingSlotsError, none was raised")
    except MissingSlotsError as e:
        assert e.missing == ["comparison", "outcome"], e.missing

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

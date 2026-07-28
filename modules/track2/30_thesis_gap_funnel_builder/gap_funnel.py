"""
Module 30 — Thesis Gap-to-Research-Question Funnel Builder (Track 2: Applied
Layer — Beginner On-Ramp)

Takes Module 29's synthesis matrix and narrows it into a thesis's specific
research question: broad context -> the thin coverage the matrix's own
coverage() count surfaces -> one defensible gap statement -> a formalized
PICO question, built with Module 1's real formalize() — the same function
Module 1 used all the way back at the start of this course.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

MODULES_T1 = Path(__file__).resolve().parent.parent.parent / "track1"
sys.path.insert(0, str(MODULES_T1 / "01_research_question_formalizer"))
sys.path.insert(0, str(MODULES_T1 / "03_bibliographic_record_model"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "29_synthesis_matrix_builder"))

from formalizer import formalize, Framework, ResearchQuestion  # noqa: E402
from record_model import Record  # noqa: E402
from synthesis_matrix import SynthesisMatrix  # noqa: E402


@dataclass
class FunnelStage:
    label: str
    text: str


def identify_thin_themes(matrix: SynthesisMatrix, threshold: int = 1) -> list[str]:
    """Themes only `threshold` or fewer sources address — real, computed
    evidence of where the literature's coverage is thinnest, reusing
    Module 29's own coverage() count directly."""
    return [theme for theme, count in matrix.coverage().items() if count <= threshold]


def build_funnel(matrix: SynthesisMatrix, broad_topic: str) -> list[FunnelStage]:
    thin = identify_thin_themes(matrix)
    stages = [
        FunnelStage(
            "1. Broad context",
            f"The literature on {broad_topic} organizes around {len(matrix.themes)} recurring "
            f"themes: {', '.join(matrix.themes)}.",
        ),
        FunnelStage(
            "2. Narrowing",
            f"Coverage across these themes is uneven — "
            + (f"{', '.join(thin)} " + ("is" if len(thin) == 1 else "are")
               + f" addressed by only {1} source, while the others draw on multiple."
               if thin else "no theme is thinly covered in this matrix.")
        ),
    ]
    if thin:
        focus = thin[0]
        stages.append(FunnelStage(
            "3. Gap",
            f'"{focus}" is where this literature has the least to say — a specific, '
            f"defensible gap for a thesis to address, grounded directly in the synthesis "
            f"matrix's own coverage count, not asserted from a general sense that 'more "
            f"research is needed.'",
        ))
    else:
        stages.append(FunnelStage("3. Gap", "No thin theme found — this matrix doesn't yet support a specific gap claim."))
    return stages


def formalize_thesis_question(gap_theme: str, population: str, comparison: str) -> ResearchQuestion:
    """Builds a natural-language question targeting the identified gap
    theme, then hands it to Module 1's REAL formalize() — the exact
    function this course's very first module built."""
    question_text = (
        f"Does {gap_theme.lower()} moderate the effect of remote work on productivity "
        f"among {population}, compared to {comparison}?"
    )
    return formalize(
        question_text,
        framework=Framework.PICO,
        slots={
            "population": population,
            "intervention": "remote work arrangements",
            "comparison": comparison,
            "outcome": f"productivity, as moderated by {gap_theme.lower()}",
        },
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    matrix = SynthesisMatrix()
    smith = Record(title="Smith (2020)", year=2020)
    jones = Record(title="Jones (2019)", year=2019)
    lee = Record(title="Lee (2021)", year=2021)
    for s in (smith, jones, lee):
        matrix.add_source(s)
    for theme in ("Self-reported outcomes", "Objectively measured outcomes", "Task-type dependence"):
        matrix.add_theme(theme)
    matrix.add_note(smith.title, "Self-reported outcomes", "reported higher job satisfaction under remote work")
    matrix.add_note(jones.title, "Objectively measured outcomes", "found no significant change in output per hour")
    matrix.add_note(lee.title, "Self-reported outcomes", "found increased self-reported productivity")
    matrix.add_note(lee.title, "Objectively measured outcomes", "found decreased measured output on collaborative tasks")
    matrix.add_note(lee.title, "Task-type dependence", "explicitly noted the divergence between task types")

    print("=" * 70)
    print("The funnel, narrowing from broad context to one specific gap")
    print("=" * 70)
    for stage in build_funnel(matrix, "remote work and productivity"):
        print(f"\n{stage.label}")
        print(f"  {stage.text}")

    print()
    print("=" * 70)
    print("Formalized into an actual research question — reusing Module 1")
    print("=" * 70)
    rq = formalize_thesis_question(
        gap_theme="Task-type dependence",
        population="knowledge workers performing both solo and collaborative tasks",
        comparison="in-office work",
    )
    print(rq.render_summary())


def _run_self_checks() -> None:
    matrix = SynthesisMatrix()
    a, b, c = Record(title="A"), Record(title="B"), Record(title="C")
    for s in (a, b, c):
        matrix.add_source(s)
    matrix.add_theme("Well covered")
    matrix.add_theme("Thin")
    matrix.add_note("A", "Well covered", "note1")
    matrix.add_note("B", "Well covered", "note2")
    matrix.add_note("C", "Thin", "note3")

    thin = identify_thin_themes(matrix)
    assert thin == ["Thin"]

    stages = build_funnel(matrix, "test topic")
    assert len(stages) == 3
    assert "Thin" in stages[2].text

    rq = formalize_thesis_question("Thin", "students", "a control group")
    assert rq.framework == Framework.PICO
    assert "thin" in rq.slots["outcome"].lower()
    rq.validate()  # must not raise — every required PICO slot must be filled

    # A matrix where every theme has MORE than the threshold's worth of
    # sources (no thin themes) is handled without crashing.
    even_matrix = SynthesisMatrix()
    even_matrix.add_source(a)
    even_matrix.add_source(b)
    even_matrix.add_theme("Even")
    even_matrix.add_note("A", "Even", "note-a")
    even_matrix.add_note("B", "Even", "note-b")
    even_stages = build_funnel(even_matrix, "test")
    assert "No thin theme found" in even_stages[2].text

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

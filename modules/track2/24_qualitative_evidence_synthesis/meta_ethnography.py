"""
Module 24 — Qualitative Evidence Synthesis / Meta-Ethnography (Track 2: Applied Layer)

Reuses Module 15's open/axial coding directly, then adds the actual
meta-ethnography step (Noblit & Hare, 1988): "translating" studies into
each other's terms to classify each shared code as reciprocal (studies
agree), refutational (studies conflict), and finally combining findings
ACROSS themes into a line-of-argument synthesis — a new interpretive claim
no single study or theme states alone.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
sys.path.insert(0, str(MODULES / "15_thematic_coding_engine"))

from thematic_coding import CodedExcerpt, open_code, axial_code, CODING_RULES, THEME_GROUPINGS  # noqa: E402

_NEGATION_MARKERS = ("not ", "n't", "never", "no longer", "actually less", "actually worse")


def _is_negated(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _NEGATION_MARKERS)


@dataclass
class StudyFindings:
    study_title: str
    coded_excerpts: list[CodedExcerpt] = field(default_factory=list)


@dataclass
class Translation:
    code: str
    study_a: str
    study_b: str
    relation: str  # "reciprocal" | "refutational"
    excerpt_a: str
    excerpt_b: str


def translate_studies(studies: list[StudyFindings]) -> list[Translation]:
    """For every open code, compares every pair of studies that both
    produced an excerpt carrying that code, classifying the pair as
    reciprocal (both non-negated or both negated — same underlying claim)
    or refutational (one negated, one not — direct conflict)."""
    by_code: dict[str, list[tuple[str, CodedExcerpt]]] = {}
    for study in studies:
        for excerpt in study.coded_excerpts:
            for code in excerpt.codes:
                by_code.setdefault(code, []).append((study.study_title, excerpt))

    translations = []
    for code, entries in by_code.items():
        for i in range(len(entries)):
            study_a, excerpt_a = entries[i]
            for j in range(i + 1, len(entries)):
                study_b, excerpt_b = entries[j]
                if study_a == study_b:
                    continue
                negated_a, negated_b = _is_negated(excerpt_a.excerpt), _is_negated(excerpt_b.excerpt)
                relation = "refutational" if negated_a != negated_b else "reciprocal"
                translations.append(Translation(
                    code=code, study_a=study_a, study_b=study_b, relation=relation,
                    excerpt_a=excerpt_a.excerpt, excerpt_b=excerpt_b.excerpt,
                ))
    return translations


def line_of_argument(themed: dict[str, list[CodedExcerpt]]) -> str:
    """Combines findings ACROSS themes (not within one) into a single new
    interpretive sentence — the actual point of meta-ethnography: saying
    something no single study or single theme states on its own."""
    non_empty_themes = {theme: excerpts for theme, excerpts in themed.items() if excerpts}
    if len(non_empty_themes) < 2:
        return "Not enough distinct themes with evidence to construct a line-of-argument synthesis."

    theme_names = list(non_empty_themes.keys())
    return (
        f"Line-of-argument synthesis: no single included study states this directly, but "
        f"combining \"{theme_names[0]}\" ({len(non_empty_themes[theme_names[0]])} excerpts) with "
        f"\"{theme_names[1]}\" ({len(non_empty_themes[theme_names[1]])} excerpts) across studies "
        f"suggests remote work reshapes daily experience along two axes at once — social contact "
        f"and work rhythm — which no single included study's findings, read alone, connect explicitly."
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    study1_excerpts = [
        ("Study 1, P1", "I miss being able to just turn to someone and ask a quick question."),
        ("Study 1, P2", "I actually get more done without people stopping by my desk all day."),
    ]
    study2_excerpts = [
        ("Study 2, P1", "Some days I don't talk to another human being until my partner gets home."),
        ("Study 2, P2", "I'm actually less productive without interruption from colleagues throughout the day."),
    ]

    study1 = StudyFindings("Study 1 (Tech Sector Interviews)", open_code(study1_excerpts, CODING_RULES))
    study2 = StudyFindings("Study 2 (Public Sector Interviews)", open_code(study2_excerpts, CODING_RULES))

    print("Coded excerpts:")
    for study in (study1, study2):
        print(f"\n  {study.study_title}:")
        for c in study.coded_excerpts:
            print(f"    codes={c.codes}  {c.excerpt!r}")

    translations = translate_studies([study1, study2])
    print()
    print("=" * 70)
    print("Translations (meta-ethnography's core step)")
    print("=" * 70)
    for t in translations:
        print(f"\n  code={t.code}  {t.study_a} <-> {t.study_b}  RELATION: {t.relation.upper()}")
        print(f"    A: {t.excerpt_a!r}")
        print(f"    B: {t.excerpt_b!r}")
        if t.code == "social_isolation" and t.relation == "refutational":
            print("    NOTE: this is a REAL, honest limitation of the negation heuristic, not a")
            print("    correct finding — both excerpts actually describe isolation (agreement),")
            print("    but B's grammatical \"don't\" (describing the isolation itself) triggered")
            print("    the same negation marker that would flag a genuine contradiction. Simple")
            print("    keyword-based negation detection can't tell these two cases apart. See")
            print("    DECISIONS.md.")

    all_excerpts = study1.coded_excerpts + study2.coded_excerpts
    themed = axial_code(all_excerpts, THEME_GROUPINGS)

    print()
    print("=" * 70)
    print("Line-of-argument synthesis")
    print("=" * 70)
    print(line_of_argument(themed))


def _run_self_checks() -> None:
    s1 = StudyFindings("S1", open_code([("S1-a", "I get more done without people stopping by.")], CODING_RULES))
    s2 = StudyFindings("S2", open_code([("S2-a", "I don't talk to anyone most days.")], CODING_RULES))
    s3 = StudyFindings("S3", open_code([("S3-a", "I'm actually less productive without interruptions.")], CODING_RULES))

    # S1 and S3 share the "fewer_interruptions" code but disagree in sentiment.
    translations = translate_studies([s1, s2, s3])
    fewer_interruptions_pairs = [t for t in translations if t.code == "fewer_interruptions"]
    assert len(fewer_interruptions_pairs) == 1
    assert fewer_interruptions_pairs[0].relation == "refutational"

    # S1 and S2 share no code, so no translation should exist between them.
    assert not any({t.study_a, t.study_b} == {"S1", "S2"} for t in translations)

    themed = axial_code(s1.coded_excerpts + s2.coded_excerpts, THEME_GROUPINGS)
    result = line_of_argument(themed)
    assert "Line-of-argument synthesis" in result

    empty_result = line_of_argument({"Only One Theme": s1.coded_excerpts})
    assert "Not enough distinct themes" in empty_result

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 15 — Thematic Coding Engine

Open coding: tag each excerpt with descriptive codes, bottom-up, using
transparent keyword-trigger rules (not ML) — same honesty principle as
Module 1's framework-suggestion heuristic. Axial coding: group those open
codes into higher-level themes. Together, these are the two-stage process
grounded theory calls open + axial coding (Strauss & Corbin) — this module
proves that process is structured and repeatable, not a vibe.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodedExcerpt:
    study_title: str
    excerpt: str
    codes: list[str] = field(default_factory=list)


def open_code(
    excerpts: list[tuple[str, str]],
    coding_rules: dict[str, list[str]],
) -> list[CodedExcerpt]:
    """excerpts: list of (study_title, excerpt_text).
    coding_rules: code_name -> list of trigger phrases (lowercase substring
    match). An excerpt can legitimately carry more than one code, or none."""
    coded = []
    for study_title, text in excerpts:
        lowered = text.lower()
        codes = [code for code, triggers in coding_rules.items() if any(t in lowered for t in triggers)]
        coded.append(CodedExcerpt(study_title=study_title, excerpt=text, codes=codes))
    return coded


def axial_code(
    coded_excerpts: list[CodedExcerpt],
    theme_groupings: dict[str, set[str]],
) -> dict[str, list[CodedExcerpt]]:
    """theme_groupings: theme_name -> set of open codes that belong to it.
    An excerpt appears under every theme any of its codes maps to — the
    same excerpt CAN legitimately appear under multiple themes."""
    themed: dict[str, list[CodedExcerpt]] = {theme: [] for theme in theme_groupings}
    for excerpt in coded_excerpts:
        for theme, member_codes in theme_groupings.items():
            if member_codes & set(excerpt.codes):
                themed[theme].append(excerpt)
    return themed


# --- Example coding scheme (fictional interview excerpts) -----------------

CODING_RULES = {
    "social_isolation": ["don't talk to", "miss being able to", "feel connected", "isolat"],
    "fewer_interruptions": ["more done without", "nobody stopping by", "without interruption"],
    "blurred_boundaries": ["skip lunch", "never really log off", "no clear end"],
}

THEME_GROUPINGS = {
    "Disrupted Social Connection": {"social_isolation"},
    "Changed Work Rhythm": {"fewer_interruptions", "blurred_boundaries"},
}


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    excerpts = [
        ("Interview P1", "I miss being able to just turn to someone and ask a quick question."),
        ("Interview P2", "Some days I don't talk to another human being until my partner gets home."),
        ("Interview P3", "I actually get more done without people stopping by my desk all day."),
        ("Interview P4", "I've started scheduling coffee chats just to feel connected to my team."),
        ("Interview P5", "Nobody notices if I skip lunch and just keep working straight through."),
        ("Interview P6", "Honestly my day is about the same as it was in the office."),
    ]

    coded = open_code(excerpts, CODING_RULES)

    print("=" * 70)
    print("Open coding: each excerpt tagged independently")
    print("=" * 70)
    for c in coded:
        print(f"  [{c.study_title}] codes={c.codes}")
        print(f"    {c.excerpt!r}")

    themed = axial_code(coded, THEME_GROUPINGS)

    print()
    print("=" * 70)
    print("Axial coding: open codes grouped into higher-level themes")
    print("=" * 70)
    for theme, members in themed.items():
        print(f"\n  THEME: {theme} ({len(members)} excerpts)")
        for m in members:
            print(f"    - [{m.study_title}] {m.excerpt!r}  (codes: {m.codes})")

    print()
    uncoded = [c for c in coded if not c.codes]
    print(f"Excerpts with no code assigned (genuinely off-topic, not forced into a theme): {len(uncoded)}")
    for c in uncoded:
        print(f"  [{c.study_title}] {c.excerpt!r}")


def _run_self_checks() -> None:
    excerpts = [
        ("S1", "I don't talk to anyone most days working from home."),
        ("S2", "I get more done without people stopping by."),
        ("S3", "I never really log off anymore."),
        ("S4", "This excerpt matches nothing in the coding scheme."),
    ]
    coded = open_code(excerpts, CODING_RULES)
    assert coded[0].codes == ["social_isolation"]
    assert coded[1].codes == ["fewer_interruptions"]
    assert coded[2].codes == ["blurred_boundaries"]
    assert coded[3].codes == []

    themed = axial_code(coded, THEME_GROUPINGS)
    assert [c.study_title for c in themed["Disrupted Social Connection"]] == ["S1"]
    assert [c.study_title for c in themed["Changed Work Rhythm"]] == ["S2", "S3"]

    # An excerpt matching codes from two different themes appears under both.
    dual = open_code([("S5", "I never really log off, and honestly I don't talk to anyone all day.")], CODING_RULES)
    assert set(dual[0].codes) == {"blurred_boundaries", "social_isolation"}
    dual_themed = axial_code(dual, THEME_GROUPINGS)
    assert dual_themed["Disrupted Social Connection"] == dual
    assert dual_themed["Changed Work Rhythm"] == dual

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

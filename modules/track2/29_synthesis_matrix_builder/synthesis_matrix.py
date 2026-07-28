"""
Module 29 — Synthesis Matrix Builder (Track 2: Applied Layer — Beginner On-Ramp)

The classic writing-center tool: a grid of sources (rows) x themes
(columns), filled in row-by-row but read back out column-by-column. This
module proves, mechanically, that reading the SAME underlying notes
organized by source vs. organized by theme produces a summary in one case
and synthesis in the other — the distinction from Prerequisite 9, made
concrete in code rather than just described in prose.

Deliberately depends on nothing but Module 3's Record — this is the
course's lightest-weight entry point, usable without the full pipeline.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "track1" / "03_bibliographic_record_model"))
from record_model import Record  # noqa: E402


@dataclass
class SynthesisMatrix:
    sources: list[Record] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    cells: dict[tuple[str, str], str] = field(default_factory=dict)

    def add_source(self, source: Record) -> None:
        if source.title not in [s.title for s in self.sources]:
            self.sources.append(source)

    def add_theme(self, theme: str) -> None:
        if theme not in self.themes:
            self.themes.append(theme)

    def add_note(self, source_title: str, theme: str, note: str) -> None:
        if source_title not in [s.title for s in self.sources]:
            raise ValueError(f'unknown source "{source_title}" — call add_source() first')
        if theme not in self.themes:
            raise ValueError(f'unknown theme "{theme}" — call add_theme() first')
        self.cells[(source_title, theme)] = note

    def render_by_source(self) -> str:
        """Reading across rows, source by source — this IS a summary,
        mechanically: one paragraph per source, themes never combined."""
        lines = []
        for source in self.sources:
            notes = [self.cells.get((source.title, theme)) for theme in self.themes]
            notes = [n for n in notes if n]
            if notes:
                lines.append(f"{source.title} ({source.year}): " + " ".join(notes))
        return "\n".join(lines)

    def render_by_theme(self) -> str:
        """Reading down columns, theme by theme — this IS synthesis,
        mechanically: each theme's paragraph cites whichever sources have
        a note there, and a source can appear under multiple themes."""
        lines = []
        for theme in self.themes:
            contributions = []
            for source in self.sources:
                note = self.cells.get((source.title, theme))
                if note:
                    contributions.append(f"{note} ({source.title.split(':')[0]}, {source.year})")
            if contributions:
                lines.append(f"{theme}: " + " ".join(contributions))
        return "\n".join(lines)

    def coverage(self) -> dict[str, int]:
        """How many sources actually have a note under each theme —
        thin themes (low coverage) are exactly what Module 30 looks for."""
        return {
            theme: sum(1 for s in self.sources if (s.title, theme) in self.cells)
            for theme in self.themes
        }


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
    print("render_by_source() — reading across rows: this IS a summary")
    print("=" * 70)
    print(matrix.render_by_source())

    print()
    print("=" * 70)
    print("render_by_theme() — reading down columns: this IS synthesis")
    print("=" * 70)
    print(matrix.render_by_theme())

    print()
    print("=" * 70)
    print("Coverage — which themes are thin (few sources)")
    print("=" * 70)
    for theme, count in matrix.coverage().items():
        print(f"  {theme!r}: {count} source(s)")
    print()
    print("Notice Lee (2021) appears under THREE different themes — reading")
    print("by source, that's three separate mentions of one paper. Reading by")
    print("theme, its findings get distributed to exactly where they're")
    print("relevant to the argument, alongside other sources making related")
    print("points. Same underlying data, mechanically different organization.")


def _run_self_checks() -> None:
    matrix = SynthesisMatrix()
    a = Record(title="A", year=2020)
    b = Record(title="B", year=2021)
    matrix.add_source(a)
    matrix.add_source(b)
    matrix.add_theme("Theme 1")
    matrix.add_theme("Theme 2")
    matrix.add_note("A", "Theme 1", "note-a1")
    matrix.add_note("B", "Theme 1", "note-b1")
    matrix.add_note("B", "Theme 2", "note-b2")

    by_source = matrix.render_by_source()
    assert "A (2020): note-a1" in by_source
    assert "note-b1" in by_source and "note-b2" in by_source

    by_theme = matrix.render_by_theme()
    assert by_theme.startswith("Theme 1:")
    assert "note-a1" in by_theme.split("\n")[0]
    assert "note-b1" in by_theme.split("\n")[0]

    assert matrix.coverage() == {"Theme 1": 2, "Theme 2": 1}

    try:
        matrix.add_note("Unknown Source", "Theme 1", "x")
        raise AssertionError("expected ValueError for unknown source")
    except ValueError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

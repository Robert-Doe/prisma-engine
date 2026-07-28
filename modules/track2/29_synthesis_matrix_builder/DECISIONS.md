# Module 29 — Decisions: Synthesis Matrix Builder

## Line-by-line / unit-by-unit

### `render_by_source()` and `render_by_theme()` read from the exact same `cells` dict — no separate data structures
**(c) Convention, and the module's entire point.** If summary and synthesis came from two different underlying representations, the module would only be asserting they're different, not proving it. Both rendering functions iterate the identical `cells` dictionary; the only thing that changes is which axis the outer loop walks first (sources, or themes). That one difference — not two different datasets — is what mechanically produces a summary in one case and synthesis in the other.

### Only Module 3's `Record` is a dependency — no Module 1, no search, no screening
**(c) Convention — the deliberate beginner-track scope decision.** This module is this course's stated lightest-weight entry point (see the ROADMAP's non-linear stopping-point row). A beginner writing a first thesis chapter needs to internalize the synthesis-vs-summary distinction before anything else in this course matters to them; requiring the full search-and-screen pipeline first would bury that lesson under machinery irrelevant to it.

### `add_note()` raises `ValueError` if the source or theme wasn't registered first via `add_source()`/`add_theme()`
**(c) Convention.** A synthesis matrix's whole value depends on its rows and columns being decided deliberately, not accumulated ad hoc as notes get added — the same discipline a real synthesis matrix worksheet enforces by literally being a pre-drawn grid you fill cells into, not a free-form notepad.

### `coverage()` counts how many sources have a note under each theme
**(c) Convention, directly setting up Module 30.** A theme only one source touches is exactly what Module 30 needs to identify as "thin" — an area worth flagging as under-covered when narrowing toward a specific gap. Building this count here, next to the data it's counting, means Module 30 doesn't need its own duplicate pass over the matrix.

### The demo reuses the exact fictional Smith/Jones/Lee example from Prerequisite 9, verbatim
**(c) Convention.** Prerequisite 9 already walked through what summary and synthesis look like as prose, using these three sources. Building the actual code that generates both versions from the same three sources — rather than a new, unrelated example — lets a learner directly compare the prerequisite's hand-written illustration against this module's generated output and see they match.

## Decisions We Made

| Decision | Category |
|---|---|
| Both renderers read the same `cells` dict, differing only in loop order | (c) Convention (the module's central proof) |
| Only Module 3 required — deliberately minimal beginner entry point | (c) Convention |
| `add_note()` requires pre-registered sources/themes | (c) Convention |
| `coverage()` counts per-theme source counts, feeding Module 30 | (c) Convention |
| Demo reuses Prerequisite 9's exact Smith/Jones/Lee example | (c) Convention |

## What We Proved

Running [`synthesis_matrix.py`](synthesis_matrix.py) generated both a
summary and a synthesis from identical underlying data, and:

1. **The exact same three sources' notes produced recognizably different prose depending only on which axis was read first** — `render_by_source()`'s output is three source-by-source paragraphs; `render_by_theme()`'s output is three theme-by-theme paragraphs, each one pulling from whichever sources are relevant. Nothing about the underlying facts changed.
2. **A single source legitimately appeared under three different themes**, confirmed directly in the output — Lee (2021) contributes to "Self-reported outcomes," "Objectively measured outcomes," AND "Task-type dependence," which is only visible once the matrix is read by theme, not by source.
3. **Coverage counts correctly identified the thinnest theme** — "Task-type dependence" has exactly 1 source, versus 2 each for the other two themes — real, computed evidence of exactly the kind of gap Module 30 will use to argue toward a specific research question.

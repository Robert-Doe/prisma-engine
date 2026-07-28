# Module 1 — Decisions: Research Question Formalizer

This document explains every non-obvious choice in [`formalizer.py`](formalizer.py),
categorized by *why* the choice was made:

- **(a) Forced by the platform/language** — not a real choice; Python's own semantics required it
- **(b) Forced by an external contract** — a published methodology or this course's own stated architecture target required it
- **(c) Our own convention** — chosen for safety/clarity; another consistent choice could have replaced it

---

## Line-by-line / unit-by-unit

### `class Framework(str, Enum)`
**(c) Convention.** Subclassing both `str` and `Enum` means `Framework.PICO == "PICO"` is `True` and `Framework.PICO.value` serializes cleanly to JSON without a custom encoder. A plain `Enum` (not `str`-backed) would have worked too, but every call site that needs the raw string (JSON output, print statements) would need an explicit `.value` everywhere instead of just where clarity demands it.

### `FRAMEWORK_SLOTS` — the exact slot names per framework
**(b) Forced by external contract.** `population/intervention/comparison/outcome` for PICO, `population/exposure/outcome` for PEO, and `sample/phenomenon_of_interest/design/evaluation/research_type` for SPIDER are not invented here — they come from the published frameworks themselves (Richardson et al., 1995 for PICO; Cooke, Smith & Booth, 2012 for SPIDER; standard epidemiological usage for PEO — see [Prerequisite 1](../../../prerequisites/prereq_pico_frameworks.html)). Renaming or dropping a slot would mean the tool no longer implements the framework it claims to.

### `slots: dict[str, str] = field(default_factory=dict)`
**(a) Forced by the platform.** Python's dataclasses (and functions in general) share one mutable default object across every instance if you write `slots: dict = {}` directly — a well-documented language gotcha, not a style preference. `field(default_factory=dict)` is the only correct way to give each `ResearchQuestion` its own independent dict.

### `class MissingSlotsError(ValueError)`
**(c) Convention.** Subclassing `ValueError` (rather than bare `Exception`) means any caller already written to catch `ValueError` for bad input also catches this specific error without extra code. A custom exception hierarchy rooted at `Exception` would work identically at the call sites actually used in this module, but would surprise a caller relying on the standard-library convention that invalid-argument errors are `ValueError`s.

### `_SPIDER_MARKERS`, `_PEO_MARKERS`, and checking SPIDER → PEO → default-PICO in that order
**(c) Convention.** These keyword lists are a deterministic heuristic, not a trained classifier — see the module docstring. The order (SPIDER and PEO checked first, PICO as the fallback) is a deliberate safety choice: PICO is the framework most reviewers already expect for an "effect of X" question, so defaulting to it when no more specific marker fires means the *worst case* for an unmatched question is "the tool suggested the most common framework," never a wrong exotic one. Reversing the priority order, or requiring explicit framework selection with no suggestion at all, would have been an equally valid, more conservative alternative — we chose the suggestion because Module 1's tutorial explicitly wants to demonstrate a real (if simple) decomposition step, not just a data-entry form.

### `suggest_comparison()`'s connective list (`compared to`, `versus`, `vs.`)
**(c) Convention.** This is a small, English-language-specific set of common academic phrasings, not a formal specification. Extending it (more connectives, other languages) or removing it entirely (always requiring the user to type the comparison manually) are both consistent alternatives.

### Validation treats whitespace-only strings as missing (`.strip()` before checking)
**(c) Convention.** A slot filled with `"   "` is, for every practical purpose, not filled. Treating it as present (skipping `.strip()`) would let a copy-paste accident silently pass validation.

### `formalize()` only injects the suggested comparison if `"comparison" not in slots`
**(c) Convention, safety-motivated.** The heuristic suggestion must never silently overwrite something a human explicitly provided. If a caller passes an empty string as `slots["comparison"]`, that's a deliberate choice by the caller (even if arguably a mistake) and is left alone — the heuristic only fills a slot that's entirely absent from the dict.

### Self-checks live inside `formalizer.py` (`_run_self_checks()`), not a separate `pytest` file
**(b) Forced by external contract.** The course's own [Tools / Architecture Target](../../../ROADMAP.md) commits to "minimal deps... dependency-light on purpose." Adding `pytest` as a dependency for Module 1 alone would violate that stated constraint; plain `assert` statements need nothing beyond the standard library.

### `render_summary()`'s fixed-width, right-aligned slot labels (`{slot:>22}`)
**(c) Convention.** Purely cosmetic — makes the terminal output scannable. Any other formatting would be equally correct.

---

## Decisions We Made

| Decision | Category |
|---|---|
| `Framework` is a `str`-backed `Enum` | (c) Convention |
| Exact slot names per framework | (b) External contract (published methodology) |
| `field(default_factory=dict)` for mutable default | (a) Forced by platform |
| `MissingSlotsError` subclasses `ValueError` | (c) Convention |
| SPIDER → PEO → PICO-default suggestion order | (c) Convention (safety-motivated) |
| Comparison-connective list is English, extensible | (c) Convention |
| Whitespace-only slots count as missing | (c) Convention |
| Heuristic never overwrites an explicitly-provided slot | (c) Convention (safety-motivated) |
| Self-checks use bare `assert`, no `pytest` | (b) External contract (course architecture target) |
| Summary formatting width | (c) Convention |

## What We Proved

Running [`formalizer.py`](formalizer.py) end to end (see the tutorial's
"Run It" section for the exact captured output) demonstrated, with real
executed code rather than a description of intended behavior:

1. **Three differently-shaped real questions were routed to three different frameworks** by a transparent, inspectable heuristic — not a black box. The reasoning (`matched SPIDER marker "experience"`, etc.) is printed alongside the decision, so a human can audit *why* the tool suggested what it suggested, and override it.
2. **A fuzzy question became a structured, validated object.** "Does remote work affect employee productivity compared to in-office work?" — an ordinary sentence — became a `ResearchQuestion` with four named, independently addressable fields, one of which (`comparison`) was correctly extracted from the sentence itself.
3. **Incompleteness is mechanically detectable, not silently ignored.** Calling `formalize()` on a question missing required slots didn't produce a half-built object — it raised `MissingSlotsError` naming exactly which slots were absent (`['comparison', 'outcome']`), which is what "machine-checkable" in this module's stated goal actually cashes out to.

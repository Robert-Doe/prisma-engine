"""
Module 2 — Boolean Query Builder

Mechanically compiles a Module 1 ResearchQuestion into a reproducible
boolean search string: one parenthesized OR-group of synonyms per slot,
joined by AND, following the pattern in Prerequisite 2 (Boolean Search &
Controlled Vocabulary).

Only some slots become search clauses by default (DEFAULT_SEARCH_SLOTS) —
Comparison and Outcome are deliberately left out of the search itself in
the common case. This mirrors real search-strategy guidance (e.g. the
Cochrane Handbook's advice on search sensitivity): many relevant papers
never mention the outcome or comparator in their title/abstract, so
requiring those terms in the *search* would silently drop real studies.
Outcome/Comparison get applied later, during screening (Module 8), not here.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Module 1 lives in a sibling directory. See DECISIONS.md for why this
# course uses sys.path injection instead of a proper installable package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "01_research_question_formalizer"))
from formalizer import Framework, ResearchQuestion, FRAMEWORK_SLOTS  # noqa: E402


DEFAULT_SEARCH_SLOTS: dict[Framework, list[str]] = {
    Framework.PICO: ["population", "intervention"],
    Framework.PEO: ["population", "exposure"],
    Framework.SPIDER: ["sample", "phenomenon_of_interest"],
}


class MissingTermsError(ValueError):
    """Raised when build_query() needs search terms for a slot that
    weren't provided in the `terms` dict."""

    def __init__(self, slot: str):
        self.slot = slot
        super().__init__(f'no SlotTerms provided for search slot "{slot}"')


class EmptySlotTermsError(ValueError):
    """Raised when a SlotTerms has neither free-text nor controlled-vocab
    terms — an OR-group with nothing in it isn't a valid boolean clause."""

    def __init__(self, slot: str):
        self.slot = slot
        super().__init__(f'SlotTerms for "{slot}" has no free_text or controlled_vocab terms')


@dataclass
class SlotTerms:
    """Search terms for one slot: free-text synonyms plus optional
    controlled-vocabulary headings (e.g. MeSH)."""

    free_text: list[str] = field(default_factory=list)
    controlled_vocab: list[str] = field(default_factory=list)


def quote_if_phrase(term: str) -> str:
    """Multi-word terms need phrase quoting; single words (including
    truncated ones like 'employ*') don't."""
    return f'"{term}"' if " " in term else term


def build_or_group(slot: str, slot_terms: SlotTerms, vocab_tag: str = "MeSH") -> str:
    if not slot_terms.free_text and not slot_terms.controlled_vocab:
        raise EmptySlotTermsError(slot)
    parts = [quote_if_phrase(t) for t in slot_terms.free_text]
    parts += [f'{vocab_tag}:"{t}"' for t in slot_terms.controlled_vocab]
    return "(" + " OR ".join(parts) + ")"


def build_query(
    rq: ResearchQuestion,
    terms: dict[str, SlotTerms],
    search_slots: list[str] | None = None,
) -> str:
    """Compile a ResearchQuestion + per-slot synonym terms into one boolean
    search string. `search_slots` overrides which slots participate;
    defaults to DEFAULT_SEARCH_SLOTS[rq.framework] if not given."""
    search_slots = search_slots or DEFAULT_SEARCH_SLOTS[rq.framework]
    groups = []
    for slot in search_slots:
        if slot not in terms:
            raise MissingTermsError(slot)
        groups.append(build_or_group(slot, terms[slot]))
    return " AND ".join(groups)


# --- Demo / self-check ----------------------------------------------------

def _run_demo() -> None:
    rq = ResearchQuestion(
        raw_text="Does remote work affect employee productivity compared to in-office work?",
        framework=Framework.PICO,
        slots={
            "population": "knowledge workers",
            "intervention": "remote work arrangements",
            "comparison": "in-office work",
            "outcome": "measured or self-reported productivity",
        },
    )
    rq.validate()

    # NOTE: "Telework" is illustrative of the *pattern* a controlled-vocab
    # term follows, not independently verified against a live MeSH lookup
    # in this exercise — see DECISIONS.md.
    terms = {
        "population": SlotTerms(
            free_text=["knowledge workers", "office workers", "employees"],
        ),
        "intervention": SlotTerms(
            free_text=["remote work", "telecommut*", "work from home", "hybrid work"],
            controlled_vocab=["Telework"],
        ),
        "outcome": SlotTerms(
            free_text=["productivity", "job performance", "work output"],
        ),
    }

    print("=" * 70)
    print("EXAMPLE 1 — default search slots (population + intervention only)")
    print("=" * 70)
    query = build_query(rq, terms)
    print(query)

    print()
    print("=" * 70)
    print("EXAMPLE 2 — explicitly widening to include outcome")
    print("=" * 70)
    query_with_outcome = build_query(rq, terms, search_slots=["population", "intervention", "outcome"])
    print(query_with_outcome)
    print()
    print("Notice this is a STRICTER (lower-recall) search: any real study")
    print("that never says 'productivity' or a synonym in its title/abstract")
    print("would now be excluded, even if it's exactly what we're looking for.")

    print()
    print("=" * 70)
    print("EXAMPLE 3 — missing terms raises MissingTermsError")
    print("=" * 70)
    try:
        build_query(rq, {"population": terms["population"]}, search_slots=["population", "intervention"])
    except MissingTermsError as e:
        print(f"Raised as expected: {e}")


def _run_self_checks() -> None:
    assert quote_if_phrase("remote work") == '"remote work"'
    assert quote_if_phrase("telecommut*") == "telecommut*"

    group = build_or_group(
        "intervention",
        SlotTerms(free_text=["remote work", "telecommut*"], controlled_vocab=["Telework"]),
    )
    assert group == '("remote work" OR telecommut* OR MeSH:"Telework")', group

    rq = ResearchQuestion(
        raw_text="Does remote work affect productivity compared to in-office work?",
        framework=Framework.PICO,
        slots={"population": "p", "intervention": "i", "comparison": "in-office work", "outcome": "o"},
    )
    query = build_query(
        rq,
        {
            "population": SlotTerms(free_text=["knowledge workers"]),
            "intervention": SlotTerms(free_text=["remote work"]),
        },
    )
    assert query == '("knowledge workers") AND ("remote work")', query

    try:
        build_query(rq, {"population": SlotTerms(free_text=["x"])})
        raise AssertionError("expected MissingTermsError")
    except MissingTermsError as e:
        assert e.slot == "intervention"

    try:
        build_or_group("outcome", SlotTerms())
        raise AssertionError("expected EmptySlotTermsError")
    except EmptySlotTermsError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

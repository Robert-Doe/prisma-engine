"""
Module 21 — Scoping Review Mapper (Track 2: Applied Layer)

Adapts Track 1's engine for a different question shape — not "what is the
effect of X" but "what does this field look like." Reuses real code from
four Track 1 modules directly:
  - Module 2's build_or_group() for a WIDENED (not narrowed) search
  - Module 8's screen()/ScreeningRule for relevance-only screening
  - Module 10's ExtractionSchema/extract() for a charting form (not a
    quantitative data-extraction form)
  - Module 14's build_evidence_table() to assemble the charted records

Deliberately does NOT call Module 11's risk-of-bias scorer at all — a
scoping review maps what exists, it doesn't judge study quality. See
DECISIONS.md.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
for name in ["02_boolean_query_builder", "03_bibliographic_record_model",
             "08_screening_engine", "10_data_extraction_engine", "14_evidence_table_builder"]:
    sys.path.insert(0, str(MODULES / name))

from query_builder import build_or_group, SlotTerms  # noqa: E402
from record_model import Record  # noqa: E402
from screening_engine import screen, ScreeningRule  # noqa: E402
from extraction_engine import ExtractionField, ExtractionSchema, extract, one_of  # noqa: E402
from evidence_table import build_evidence_table  # noqa: E402


class MissingPCCSlotsError(ValueError):
    """Same role as Module 1's MissingSlotsError, for the PCC framework
    instead of PICO/PEO/SPIDER — see DECISIONS.md for why this is a new,
    parallel class rather than a literal reuse of Module 1's."""


PCC_REQUIRED_SLOTS = ["population", "concept", "context"]


@dataclass
class PCCQuestion:
    """Population, Concept, Context — the real question framework JBI
    (Joanna Briggs Institute) methodology recommends for scoping reviews,
    used instead of PICO precisely because PICO's Intervention/Comparison
    slots assume an effect is being measured, which a scoping review
    doesn't do."""

    raw_text: str
    slots: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        missing = [s for s in PCC_REQUIRED_SLOTS if not self.slots.get(s, "").strip()]
        if missing:
            raise MissingPCCSlotsError(f"PCC requires {PCC_REQUIRED_SLOTS}; missing: {missing}")


def build_widened_query(terms: dict[str, SlotTerms]) -> str:
    """Reuses Module 2's build_or_group() directly, but — unlike Module 2's
    DEFAULT_SEARCH_SLOTS, which deliberately excludes some slots to keep a
    systematic review's search sensitive without becoming unmanageable —
    a scoping review wants maximum breadth: every slot with terms gets
    included in the search, not a narrowed default subset."""
    groups = [build_or_group(slot, slot_terms) for slot, slot_terms in terms.items()]
    return " AND ".join(groups)


# --- Charting form (reuses Module 10/14's machinery, new field set) -------

CHARTING_SCHEMA = ExtractionSchema(fields=[
    ExtractionField("population_type", str, required=True,
                     validator=one_of({"knowledge workers", "healthcare workers", "students", "general population"})),
    ExtractionField("study_design", str, required=True,
                     validator=one_of({"RCT", "cohort", "cross-sectional", "qualitative", "survey", "case study"})),
    ExtractionField("geographic_region", str, required=False),
    ExtractionField("topic_focus", str, required=True,
                     validator=one_of({"productivity", "wellbeing", "policy", "technology adoption"})),
])


def summarize_breadth(table) -> dict[str, dict[str, int]]:
    """A breadth map: for each charting field, how many charted records
    fall into each observed value. This is the scoping review's actual
    output — not a pooled effect, a picture of the field's shape."""
    breadth: dict[str, dict[str, int]] = {f.name: {} for f in table.schema.fields}
    for row in table.to_dict_rows():
        for field_name in breadth:
            value = row.get(field_name)
            if value:
                breadth[field_name][value] = breadth[field_name].get(value, 0) + 1
    return breadth


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    pcc = PCCQuestion(
        raw_text="What research exists on remote work practices among knowledge workers?",
        slots={
            "population": "knowledge workers",
            "concept": "remote and hybrid work practices",
            "context": "post-pandemic organizational settings",
        },
    )
    pcc.validate()
    print(f"PCC question validated: {pcc.slots}")

    terms = {
        "population": SlotTerms(free_text=["knowledge workers", "office workers", "employees", "professionals"]),
        "concept": SlotTerms(free_text=["remote work", "telecommut*", "hybrid work", "work from home", "distributed teams"]),
        "context": SlotTerms(free_text=["organization*", "workplace", "post-pandemic"]),
    }
    query = build_widened_query(terms)
    print()
    print("Widened scoping search (every slot included, unlike Module 2's default narrowing):")
    print(f"  {query}")

    # Relevance-only screening, reusing Module 8's screen() directly —
    # no publication-year or design filtering, since breadth is the goal.
    def mentions_remote_work(rec: Record) -> bool:
        text = f"{rec.title} {rec.abstract or ''}".lower()
        return any(kw in text for kw in ("remote", "telecommut", "hybrid work", "work from home"))

    candidate_records = [
        Record(title="Remote Work Adoption Patterns in Tech Firms", abstract="A survey of adoption patterns."),
        Record(title="Distributed Teams and Organizational Culture", abstract="Examines hybrid work and culture."),
        Record(title="Office Layout and Ergonomics", abstract="Examines desk height and chair design in traditional offices."),
    ]
    rules = [ScreeningRule("not about remote/hybrid work", mentions_remote_work)]
    result = screen(candidate_records, rules)
    print()
    print(f"Relevance screening (no design/date filtering): {len(result.included)}/{len(candidate_records)} kept")

    # Charting (reuses Module 10/14) — no risk-of-bias appraisal call at all.
    charted = [
        extract(candidate_records[0], CHARTING_SCHEMA,
                {"population_type": "knowledge workers", "study_design": "survey",
                 "geographic_region": "North America", "topic_focus": "technology adoption"}),
        extract(candidate_records[1], CHARTING_SCHEMA,
                {"population_type": "knowledge workers", "study_design": "qualitative",
                 "geographic_region": "Europe", "topic_focus": "wellbeing"}),
    ]
    table = build_evidence_table(charted, CHARTING_SCHEMA)
    breadth = summarize_breadth(table)

    print()
    print("=" * 70)
    print("Breadth map (the scoping review's actual output)")
    print("=" * 70)
    for field_name, counts in breadth.items():
        print(f"  {field_name}: {counts}")


def _run_self_checks() -> None:
    pcc = PCCQuestion("test", {"population": "p", "concept": "c"})
    try:
        pcc.validate()
        raise AssertionError("expected MissingPCCSlotsError")
    except MissingPCCSlotsError as e:
        assert "context" in str(e)

    pcc2 = PCCQuestion("test", {"population": "p", "concept": "c", "context": "x"})
    pcc2.validate()  # should not raise

    query = build_widened_query({
        "population": SlotTerms(free_text=["a", "b"]),
        "concept": SlotTerms(free_text=["c"]),
    })
    assert query == "(a OR b) AND (c)", query

    r1 = extract(Record(title="R1"), CHARTING_SCHEMA, {
        "population_type": "students", "study_design": "survey", "topic_focus": "wellbeing",
    })
    r2 = extract(Record(title="R2"), CHARTING_SCHEMA, {
        "population_type": "students", "study_design": "qualitative", "topic_focus": "wellbeing",
    })
    table = build_evidence_table([r1, r2], CHARTING_SCHEMA)
    breadth = summarize_breadth(table)
    assert breadth["population_type"] == {"students": 2}
    assert breadth["study_design"] == {"survey": 1, "qualitative": 1}

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 14 — Evidence Table Builder

Assembles many Module 10 ExtractedRecords — each independently validated
against the SAME schema — into one table where studies become directly
comparable, column by column. Re-validates every row against the target
schema at assembly time, catching the real failure case where one study
was extracted against a different (or looser) schema than the rest.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "10_data_extraction_engine"))
from extraction_engine import (  # noqa: E402
    ExtractedRecord,
    ExtractionSchema,
    ExtractionValidationError,
    REMOTE_WORK_SCHEMA,
    validate_extraction,
)


class SchemaMismatchError(ValueError):
    """Raised when a row's extracted data doesn't satisfy the table's
    target schema — e.g. it was extracted against a different, looser
    schema than the rest of the table."""


@dataclass
class EvidenceTable:
    schema: ExtractionSchema
    rows: list[ExtractedRecord] = field(default_factory=list)

    def column_names(self) -> list[str]:
        return ["title", "year"] + [f.name for f in self.schema.fields]

    def to_dict_rows(self) -> list[dict]:
        out = []
        for er in self.rows:
            row = {"title": er.record.title, "year": er.record.year}
            row.update(er.data)
            out.append(row)
        return out

    def render_markdown(self) -> str:
        cols = self.column_names()
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for row in self.to_dict_rows():
            lines.append("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
        return "\n".join(lines)


def build_evidence_table(extracted_records: list[ExtractedRecord], schema: ExtractionSchema) -> EvidenceTable:
    for er in extracted_records:
        try:
            validate_extraction(schema, er.data)
        except ExtractionValidationError as e:
            raise SchemaMismatchError(
                f'"{er.record.title}" does not satisfy the target schema: {e}'
            ) from e
    return EvidenceTable(schema=schema, rows=list(extracted_records))


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
    from record_model import Record  # noqa: E402
    from extraction_engine import extract  # noqa: E402

    studies = [
        (Record(title="A Longitudinal Comparison of Remote and In-Office Knowledge Worker Output", year=2023),
         {"sample_size": 210, "study_design": "RCT", "effect_direction": "positive",
          "comparison_group": "in-office workers", "outcome_measure": "output per hour"}),
        (Record(title="Telecommuting and Job Performance: A Cohort Study", year=2021),
         {"sample_size": 640, "study_design": "cohort", "effect_direction": "no effect",
          "comparison_group": "pre-pandemic baseline"}),
        (Record(title="Mixed Effects of Hybrid Schedules on Team Productivity", year=2022),
         {"sample_size": 88, "study_design": "cross-sectional", "effect_direction": "mixed",
          "comparison_group": "fully in-office teams", "outcome_measure": "self-reported productivity"}),
    ]

    extracted = [extract(record, REMOTE_WORK_SCHEMA, data) for record, data in studies]
    table = build_evidence_table(extracted, REMOTE_WORK_SCHEMA)

    print("=" * 70)
    print(f"Evidence table: {len(table.rows)} studies, {len(table.column_names())} columns")
    print("=" * 70)
    print(table.render_markdown())

    print()
    print("Now what wasn't possible before assembly: reading straight down a")
    print("column instead of one study at a time.")
    directions = [row["effect_direction"] for row in table.to_dict_rows()]
    print(f"  effect_direction column: {directions}")
    print(f"  -> {directions.count('positive')} positive, {directions.count('no effect')} no effect, "
          f"{directions.count('mixed')} mixed")

    print()
    print("=" * 70)
    print("A study extracted with an incompatible schema is caught, not silently added")
    print("=" * 70)
    bad_record = Record(title="A Study Missing Required Fields", year=2020)
    bad_extracted = ExtractedRecord(record=bad_record, data={"sample_size": 40})  # bypasses extract()'s own validation
    try:
        build_evidence_table(extracted + [bad_extracted], REMOTE_WORK_SCHEMA)
    except SchemaMismatchError as e:
        print(f"  Raised as expected: {e}")


def _run_self_checks() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
    from record_model import Record  # noqa: E402
    from extraction_engine import extract  # noqa: E402

    r1 = extract(Record(title="Study A", year=2020), REMOTE_WORK_SCHEMA, {
        "sample_size": 100, "study_design": "RCT", "effect_direction": "positive", "comparison_group": "x",
    })
    r2 = extract(Record(title="Study B", year=2021), REMOTE_WORK_SCHEMA, {
        "sample_size": 50, "study_design": "cohort", "effect_direction": "negative", "comparison_group": "y",
    })
    table = build_evidence_table([r1, r2], REMOTE_WORK_SCHEMA)
    assert table.column_names() == ["title", "year", "sample_size", "study_design", "effect_direction",
                                     "comparison_group", "outcome_measure"]
    rows = table.to_dict_rows()
    assert rows[0]["title"] == "Study A"
    assert rows[1]["sample_size"] == 50

    md = table.render_markdown()
    assert "Study A" in md and "Study B" in md
    assert md.count("\n") == 3  # header + separator + 2 rows

    # A row bypassing extract()'s own validation is still caught here.
    bad = ExtractedRecord(record=Record(title="Bad Study"), data={"sample_size": 10})
    try:
        build_evidence_table([r1, bad], REMOTE_WORK_SCHEMA)
        raise AssertionError("expected SchemaMismatchError")
    except SchemaMismatchError as e:
        assert "Bad Study" in str(e)

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

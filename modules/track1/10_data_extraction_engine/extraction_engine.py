"""
Module 10 — Data Extraction Form Engine

Defines a validated extraction schema (field name, expected type, required-
ness, and an optional value constraint) and checks hand-entered data against
it. This module does NOT auto-extract data from free text with NLP — see
DECISIONS.md for why that's a deliberate scope boundary, not a missing
feature. It proves the narrower, still-real claim: a validated schema turns
"whatever a reviewer typed" into structured, comparable, checked data.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
from record_model import Record  # noqa: E402


@dataclass
class ExtractionField:
    name: str
    field_type: type
    required: bool = True
    validator: Callable[[Any], bool] | None = None
    description: str = ""


@dataclass
class ExtractionSchema:
    fields: list[ExtractionField] = field(default_factory=list)


class ExtractionValidationError(ValueError):
    """Raised when hand-entered extraction data doesn't satisfy the schema
    — a missing required field, a wrong type, or a failed value constraint."""


def one_of(allowed: set) -> Callable[[Any], bool]:
    """Builds a validator confirming a value is in a fixed, controlled set
    — the extraction-schema equivalent of Module 1's framework slots."""
    return lambda v: v in allowed


def positive_int(v: Any) -> bool:
    return isinstance(v, int) and v > 0


def validate_extraction(schema: ExtractionSchema, data: dict[str, Any]) -> None:
    for f in schema.fields:
        if f.name not in data:
            if f.required:
                raise ExtractionValidationError(f'missing required field "{f.name}"')
            continue
        value = data[f.name]
        if not isinstance(value, f.field_type):
            raise ExtractionValidationError(
                f'field "{f.name}" expected {f.field_type.__name__}, got {type(value).__name__} ({value!r})'
            )
        if f.validator is not None and not f.validator(value):
            raise ExtractionValidationError(f'field "{f.name}" failed validation: {value!r}')


@dataclass
class ExtractedRecord:
    record: Record
    data: dict[str, Any]


def extract(record: Record, schema: ExtractionSchema, data: dict[str, Any]) -> ExtractedRecord:
    validate_extraction(schema, data)
    return ExtractedRecord(record=record, data=dict(data))


# --- Example schema for this course's running remote-work example ---------

REMOTE_WORK_SCHEMA = ExtractionSchema(fields=[
    ExtractionField("sample_size", int, required=True, validator=positive_int,
                     description="Number of participants in the study"),
    ExtractionField("study_design", str, required=True,
                     validator=one_of({"RCT", "cohort", "cross-sectional", "qualitative"}),
                     description="Design category (see Prerequisite 4)"),
    ExtractionField("effect_direction", str, required=True,
                     validator=one_of({"positive", "negative", "no effect", "mixed"}),
                     description="Direction of the reported productivity effect"),
    ExtractionField("comparison_group", str, required=True,
                     description="What remote work was compared against"),
    ExtractionField("outcome_measure", str, required=False,
                     description="How productivity was actually measured (optional — not always reported)"),
])


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    record = Record(
        title="A Longitudinal Comparison of Remote and In-Office Knowledge Worker Output",
        authors=["Osei, Kwame", "Duarte, Ines"], year=2023, doi="10.9999/fake-c",
    )

    print("=" * 70)
    print("A valid extraction")
    print("=" * 70)
    good_data = {
        "sample_size": 210,
        "study_design": "RCT",
        "effect_direction": "positive",
        "comparison_group": "in-office workers",
        "outcome_measure": "output per hour",
    }
    extracted = extract(record, REMOTE_WORK_SCHEMA, good_data)
    print(f"Extracted OK: {extracted.data}")

    print()
    print("=" * 70)
    print("Three ways bad data gets caught, not silently accepted")
    print("=" * 70)

    attempts = [
        ("missing required field", {"sample_size": 210, "effect_direction": "positive", "comparison_group": "in-office"}),
        ("wrong type", {"sample_size": "about two hundred", "study_design": "RCT",
                         "effect_direction": "positive", "comparison_group": "in-office"}),
        ("value outside controlled set", {"sample_size": 210, "study_design": "focus group",
                                           "effect_direction": "positive", "comparison_group": "in-office"}),
    ]
    for label, bad_data in attempts:
        try:
            extract(record, REMOTE_WORK_SCHEMA, bad_data)
            print(f"  [{label}] unexpectedly succeeded — this would be a bug")
        except ExtractionValidationError as e:
            print(f"  [{label}] caught: {e}")


def _run_self_checks() -> None:
    record = Record(title="Test Study")

    good = extract(record, REMOTE_WORK_SCHEMA, {
        "sample_size": 50, "study_design": "cohort", "effect_direction": "mixed",
        "comparison_group": "in-office workers",
    })
    assert good.data["sample_size"] == 50

    # optional field can be omitted
    assert "outcome_measure" not in good.data

    try:
        extract(record, REMOTE_WORK_SCHEMA, {"study_design": "cohort", "effect_direction": "mixed", "comparison_group": "x"})
        raise AssertionError("expected missing-field error")
    except ExtractionValidationError as e:
        assert "sample_size" in str(e)

    try:
        extract(record, REMOTE_WORK_SCHEMA, {
            "sample_size": -5, "study_design": "cohort", "effect_direction": "mixed", "comparison_group": "x",
        })
        raise AssertionError("expected positive_int validation error")
    except ExtractionValidationError:
        pass

    try:
        extract(record, REMOTE_WORK_SCHEMA, {
            "sample_size": 50, "study_design": "interview study", "effect_direction": "mixed", "comparison_group": "x",
        })
        raise AssertionError("expected controlled-set validation error")
    except ExtractionValidationError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

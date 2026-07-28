"""
Module 28 — Positioning & Gap-Statement Generator (Track 2: Applied Layer)

Takes Module 27's real comparison matrix and mechanically derives a
novelty/gap claim: does any existing paper already satisfy every dimension
a hypothetical new contribution would need? If not, WHY not — grounded back
in each near-miss paper's actual real title/abstract text via
verify_claim_grounded(), not just trusted from the extracted table.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODULES_T1 = Path(__file__).resolve().parent.parent.parent / "track1"
MODULES_T2 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MODULES_T1 / "03_bibliographic_record_model"))
sys.path.insert(0, str(MODULES_T2 / "27_related_work_comparison_matrix"))

from record_model import Record  # noqa: E402
from comparison_matrix import COMPARISON_SCHEMA, extract_dimensions  # noqa: E402
sys.path.insert(0, str(MODULES_T1 / "10_data_extraction_engine"))
from extraction_engine import extract  # noqa: E402
sys.path.insert(0, str(MODULES_T1 / "14_evidence_table_builder"))
from evidence_table import build_evidence_table  # noqa: E402


@dataclass
class GapCriteria:
    required_dimensions: dict[str, Any] = field(default_factory=dict)


def find_satisfying_papers(table, criteria: GapCriteria) -> list[dict]:
    """Rows that satisfy EVERY required dimension simultaneously."""
    return [
        row for row in table.to_dict_rows()
        if all(row.get(k) == v for k, v in criteria.required_dimensions.items())
    ]


def find_near_misses(table, criteria: GapCriteria) -> list[tuple[dict, list[str]]]:
    """Rows satisfying SOME but not all required dimensions, paired with
    exactly which dimensions they're missing."""
    near_misses = []
    for row in table.to_dict_rows():
        missing = [k for k, v in criteria.required_dimensions.items() if row.get(k) != v]
        if missing and len(missing) < len(criteria.required_dimensions):
            near_misses.append((row, missing))
    return near_misses


def verify_claim_grounded(record: Record, dimension: str, claimed_value: Any) -> bool:
    """Re-derives a dimension DIRECTLY from the record's real text, right
    now, rather than trusting whatever the comparison table already says —
    an audit step, same spirit as Module 4's verify_mesh_term(). Returns
    True if the claim is actually grounded in the record's real text."""
    fresh = extract_dimensions(record)
    return fresh.get(dimension) == claimed_value


def generate_gap_statement(records: list[Record], criteria: GapCriteria, contribution_name: str) -> str:
    extracted = [extract(r, COMPARISON_SCHEMA, extract_dimensions(r)) for r in records]
    table = build_evidence_table(extracted, COMPARISON_SCHEMA)

    satisfying = find_satisfying_papers(table, criteria)
    if satisfying:
        titles = [r["title"] for r in satisfying]
        return f"NOT A GAP: existing work already satisfies every required dimension: {titles}"

    near_misses = find_near_misses(table, criteria)
    lines = [
        f"Gap statement for \"{contribution_name}\":",
        f"  No existing paper in this corpus satisfies all of: {criteria.required_dimensions}",
    ]
    if near_misses:
        lines.append("  Closest prior work, and exactly what each is missing:")
        record_by_title = {r.title: r for r in records}
        for row, missing in near_misses:
            rec = record_by_title.get(row["title"])
            grounded_ok = all(
                verify_claim_grounded(rec, dim, criteria.required_dimensions[dim]) is False
                for dim in missing
            ) if rec else False
            audit = "grounded in its real abstract text (re-checked, not assumed)" if grounded_ok else "COULD NOT RE-VERIFY — flag for manual check"
            lines.append(f"    - {row['title']!r} — missing: {missing}  [{audit}]")
    else:
        lines.append("  No near-misses either — this corpus offers no partial precedent at all.")
    return "\n".join(lines)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    sys.path.insert(0, str(MODULES_T1 / "05_multi_source_aggregator"))
    sys.path.insert(0, str(MODULES_T1 / "06_deduplication_engine"))
    sys.path.insert(0, str(MODULES_T1 / "13_citation_snowballing_engine"))
    from aggregator import fetch_arxiv, merge_sources  # noqa: E402
    from dedup_engine import deduplicate  # noqa: E402
    from snowball import backward_snowball  # noqa: E402

    query = '(abs:spectre OR abs:meltdown) AND (abs:"side channel" OR abs:"side-channel") AND cat:cs.CR'
    arxiv_records, _total = fetch_arxiv(query, max_results=5)
    snowballed = backward_snowball("10.1145/3316781.3317903", max_resolve=2)
    corpus, _stats = merge_sources(arxiv_records, snowballed)
    dedup_result = deduplicate(corpus)

    print(f"Real corpus: {len(dedup_result.unique_records)} unique papers (same as Module 27)")
    print()

    criteria = GapCriteria(required_dimensions={
        "approach_type": "detection", "targets_spectre": True,
        "targets_meltdown": True, "ml_based": False,
    })
    statement = generate_gap_statement(
        dedup_result.unique_records, criteria,
        contribution_name="A non-ML detection technique covering both Spectre and Meltdown",
    )
    print(statement)

    print()
    print("=" * 70)
    print("A criteria set that IS already satisfied (sanity check)")
    print("=" * 70)
    already_done = GapCriteria(required_dimensions={"approach_type": "mitigation", "targets_spectre": True})
    print(generate_gap_statement(dedup_result.unique_records, already_done, "Yet another Spectre mitigation"))


def _run_self_checks() -> None:
    r1 = Record(title="ML Detection of Spectre", abstract="We use machine learning to detect Spectre attacks.")
    r2 = Record(title="Meltdown Mitigation via Hardware", abstract="A hardware technique to prevent Meltdown.")
    # NOTE: deliberately avoids the phrase "machine learning" entirely, even
    # negated — extract_dimensions()'s substring check can't distinguish
    # "uses machine learning" from "without machine learning" (the same
    # negation-blindness limitation Module 24 documents at length). Using
    # "rule-based" here keeps this self-check about gap-statement logic,
    # not a second demonstration of that already-documented limitation.
    r3 = Record(title="Rule-Based Spectre and Meltdown Detector", abstract="A rule-based tool to detect both Spectre and Meltdown.")

    criteria_satisfied = GapCriteria({"approach_type": "detection", "targets_spectre": True, "ml_based": True})
    stmt = generate_gap_statement([r1, r2, r3], criteria_satisfied, "test")
    assert stmt.startswith("NOT A GAP")

    criteria_gap = GapCriteria({"approach_type": "detection", "targets_meltdown": True, "ml_based": True})
    stmt2 = generate_gap_statement([r1, r2, r3], criteria_gap, "test2")
    assert "No existing paper" in stmt2
    assert "Rule-Based Spectre and Meltdown Detector" in stmt2  # a real near-miss, correctly cited

    assert verify_claim_grounded(r1, "ml_based", True) is True
    assert verify_claim_grounded(r3, "ml_based", True) is False

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

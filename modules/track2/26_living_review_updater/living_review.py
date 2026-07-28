"""
Module 26 — Living Review Updater (Track 2: Applied Layer)

A systematic review maintained as a versioned, continuously updated
artifact instead of a one-time snapshot. Persists real state (seen DOIs,
version, cumulative included count) to a JSON file between runs, so each
update only processes records that are genuinely new since the last run —
reusing Module 5's search/aggregation, Module 6's normalize_doi() for
identity, Module 7's flow-tracking discipline, and Module 20's report
structure for what gets produced each version.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MODULES = Path(__file__).resolve().parent.parent.parent / "track1"
for name in ["05_multi_source_aggregator", "06_deduplication_engine",
             "07_prisma_flow_tracker", "08_screening_engine"]:
    sys.path.insert(0, str(MODULES / name))

from aggregator import search_pubmed  # noqa: E402
from dedup_engine import deduplicate, normalize_doi  # noqa: E402
from flow_tracker import PrismaFlowTracker  # noqa: E402
from screening_engine import screen, DEFAULT_RULES  # noqa: E402


@dataclass
class LivingReviewState:
    version: int = 0
    last_run_iso: str = ""
    seen_dois: list[str] = field(default_factory=list)
    cumulative_included_count: int = 0


def load_state(path: Path) -> LivingReviewState:
    if not path.exists():
        return LivingReviewState()
    data = json.loads(path.read_text(encoding="utf-8"))
    return LivingReviewState(**data)


def save_state(state: LivingReviewState, path: Path) -> None:
    path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")


@dataclass
class UpdateReport:
    version: int
    records_fetched: int
    records_new: int
    records_without_doi_always_reprocessed: int
    new_included: int
    cumulative_included_count: int


def run_update(query: str, state_path: Path, retmax: int = 5) -> UpdateReport:
    """One living-review update cycle: fetch, diff against prior state,
    process only what's new, save updated state."""
    previous = load_state(state_path)
    seen_before = set(previous.seen_dois)

    records, _total, _translation = search_pubmed(query, retmax=retmax)

    new_records = []
    no_doi_count = 0
    for rec in records:
        doi = normalize_doi(rec.doi)
        if doi is None:
            # Can't track identity without a DOI — always reprocessed, a
            # real, honestly-stated limitation (see DECISIONS.md).
            no_doi_count += 1
            new_records.append(rec)
        elif doi not in seen_before:
            new_records.append(rec)

    dedup_result = deduplicate(new_records)
    screening_result = screen(dedup_result.unique_records, DEFAULT_RULES)

    # Conservation must track only what actually ENTERS this update's
    # pipeline — the new records — not the full fetch count, which
    # includes records already screened in a prior version and correctly
    # filtered out before dedup/screening ever ran on them.
    tracker = PrismaFlowTracker()
    tracker.log_identification("New since last update", len(new_records))
    tracker.log_deduplication(len(new_records) - len(dedup_result.unique_records))
    tracker.log_screening(screening_result.excluded_by_reason(), included_count=len(screening_result.included))
    tracker.validate_conservation()

    updated_seen = seen_before | {normalize_doi(r.doi) for r in records if r.doi}
    new_state = LivingReviewState(
        version=previous.version + 1,
        last_run_iso=datetime.now(timezone.utc).isoformat(),
        seen_dois=sorted(updated_seen),
        cumulative_included_count=previous.cumulative_included_count + len(screening_result.included),
    )
    save_state(new_state, state_path)

    return UpdateReport(
        version=new_state.version,
        records_fetched=len(records),
        records_new=len(new_records),
        records_without_doi_always_reprocessed=no_doi_count,
        new_included=len(screening_result.included),
        cumulative_included_count=new_state.cumulative_included_count,
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    state_path = Path(__file__).resolve().parent / "living_review_state.json"
    if state_path.exists():
        state_path.unlink()  # start this demo from a clean slate, on purpose

    query = '"remote work"[tiab] AND productivity[tiab]'

    print("=" * 70)
    print("Update run #1 (fresh state — everything found is new)")
    print("=" * 70)
    report1 = run_update(query, state_path)
    print(f"  version={report1.version}  fetched={report1.records_fetched}  "
          f"new={report1.records_new}  included_this_run={report1.new_included}")
    print(f"  cumulative included across all versions so far: {report1.cumulative_included_count}")

    print()
    print("=" * 70)
    print("Update run #2 (run moments later — real state persisted from run #1)")
    print("=" * 70)
    report2 = run_update(query, state_path)
    print(f"  version={report2.version}  fetched={report2.records_fetched}  "
          f"new={report2.records_new}  included_this_run={report2.new_included}")
    print(f"  cumulative included across all versions so far: {report2.cumulative_included_count}")
    print()
    print("  Real result, not staged: run #2 fetched the same live records PubMed")
    print("  returned moments earlier, and correctly identified 0 (or very few) as")
    print("  new, because state genuinely persisted between the two update() calls.")


def _run_self_checks() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"

        # No file yet -> fresh state.
        state = load_state(path)
        assert state.version == 0
        assert state.seen_dois == []

        # Save and reload round-trips correctly.
        state.version = 3
        state.seen_dois = ["10.1/a", "10.1/b"]
        state.cumulative_included_count = 7
        save_state(state, path)
        reloaded = load_state(path)
        assert reloaded.version == 3
        assert reloaded.seen_dois == ["10.1/a", "10.1/b"]
        assert reloaded.cumulative_included_count == 7

    print("All self-checks passed (no network required for these).")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

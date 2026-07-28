"""
Module 6 — Deduplication Engine

Two passes over a corpus of Records: exact DOI matching first (cheap,
unambiguous), then fuzzy title+author matching for whatever's left
(expensive, probabilistic — needs a threshold and produces an auditable
score, never a silent merge).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "03_bibliographic_record_model"))
from record_model import Record  # noqa: E402


def normalize_doi(doi: str | None) -> str | None:
    """Strips URL-prefix and case differences so '10.1037/xyz',
    'https://doi.org/10.1037/XYZ', and 'DOI.ORG/10.1037/xyz' all compare
    equal — DOIs are case-insensitive by the DOI specification itself."""
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


def normalize_title(title: str) -> str:
    t = title.lower()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def _last_names(authors: list[str]) -> set[str]:
    names = set()
    for a in authors:
        # Handles both "Smith, Jane" (RIS/BibTeX/Crossref) and "Smith J"
        # (PubMed) shapes — take the first comma-or-space-delimited token.
        token = re.split(r"[,\s]", a.strip())[0].lower()
        if token:
            names.add(token)
    return names


def author_overlap(a: list[str], b: list[str]) -> float:
    """Jaccard overlap of last-name sets. Returns 0.0 if either side has
    no authors at all (can't confirm overlap from nothing)."""
    names_a, names_b = _last_names(a), _last_names(b)
    if not names_a or not names_b:
        return 0.0
    return len(names_a & names_b) / len(names_a | names_b)


@dataclass
class DuplicateMatch:
    kept_index: int
    duplicate_index: int
    reason: str  # "exact_doi" | "fuzzy_title"
    score: float


@dataclass
class DedupeResult:
    unique_records: list[Record] = field(default_factory=list)
    matches: list[DuplicateMatch] = field(default_factory=list)


def deduplicate(
    records: list[Record],
    title_threshold: float = 0.90,
    min_author_overlap: float = 0.0,
) -> DedupeResult:
    """Pass 1: exact-DOI grouping. Pass 2: fuzzy title/author matching on
    whatever Pass 1 didn't already remove. `min_author_overlap` guards
    against flagging two different papers that merely share a generic
    title pattern — set to 0.0 to disable (title score alone decides)."""
    n = len(records)
    removed = [False] * n
    matches: list[DuplicateMatch] = []

    # --- Pass 1: exact DOI ---
    doi_to_first_index: dict[str, int] = {}
    for i, rec in enumerate(records):
        norm = normalize_doi(rec.doi)
        if norm is None:
            continue
        if norm in doi_to_first_index:
            kept = doi_to_first_index[norm]
            removed[i] = True
            matches.append(DuplicateMatch(kept_index=kept, duplicate_index=i, reason="exact_doi", score=1.0))
        else:
            doi_to_first_index[norm] = i

    # --- Pass 2: fuzzy title + author, only among survivors of Pass 1 ---
    survivors = [i for i in range(n) if not removed[i]]
    for a_pos in range(len(survivors)):
        i = survivors[a_pos]
        if removed[i]:
            continue
        for b_pos in range(a_pos + 1, len(survivors)):
            j = survivors[b_pos]
            if removed[j]:
                continue
            score = title_similarity(records[i].title, records[j].title)
            if score < title_threshold:
                continue
            if min_author_overlap > 0.0 and author_overlap(records[i].authors, records[j].authors) < min_author_overlap:
                continue
            removed[j] = True
            matches.append(DuplicateMatch(kept_index=i, duplicate_index=j, reason="fuzzy_title", score=score))

    unique = [records[i] for i in range(n) if not removed[i]]
    return DedupeResult(unique_records=unique, matches=matches)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    records = [
        Record(title="Remote Work and Productivity: A Longitudinal Study", authors=["Smith, Jane", "Lee, Amrita"],
               doi="10.1037/xyz", source_format="RIS"),
        Record(title="Remote Work and Productivity - A Longitudinal Study", authors=["Smith J", "Lee A"],
               doi=None, source_format="ArXivAtom"),  # same paper, no DOI on the preprint copy
        Record(title="Remote Work and Productivity: A Longitudinal Study", authors=["Smith, Jane", "Lee, Amrita"],
               doi="HTTPS://DOI.ORG/10.1037/XYZ", source_format="CrossrefJSON"),  # exact DOI dup, different case/prefix
        Record(title="Remote Work and Employee Wellbeing", authors=["Nguyen, Thi", "Park, Soo"],
               doi="10.1037/abc", source_format="PubMedESummary"),  # genuinely different paper
        Record(title="Does Remote Work Affect Productivity?", authors=["Okoye, Chidi"],
               doi="10.1037/def", source_format="PubMedESummary"),  # also genuinely different
    ]

    print("Input corpus:")
    for i, r in enumerate(records):
        print(f"  [{i}] {r.title!r}  doi={r.doi}  authors={r.authors}")

    result = deduplicate(records, title_threshold=0.90, min_author_overlap=0.5)

    print()
    print("=" * 70)
    print("Matches found")
    print("=" * 70)
    for m in result.matches:
        print(f"  duplicate_index={m.duplicate_index} -> kept_index={m.kept_index}  "
              f"reason={m.reason}  score={m.score:.3f}")

    print()
    print(f"Started with {len(records)} records, {len(result.unique_records)} remain after dedup:")
    for r in result.unique_records:
        print(f"  - {r.title!r}")


def _run_self_checks() -> None:
    assert normalize_doi("https://doi.org/10.1037/XYZ") == "10.1037/xyz"
    assert normalize_doi("DOI.ORG/10.1037/xyz") == "doi.org/10.1037/xyz"  # only strips http(s):// prefix, not bare host
    assert normalize_doi(None) is None
    assert normalize_doi("") is None

    assert title_similarity(
        "Remote Work and Productivity: A Longitudinal Study",
        "Remote Work and Productivity - A Longitudinal Study",
    ) == 1.0

    score = title_similarity("Remote Work and Employee Wellbeing", "Remote Work and Employee Productivity")
    assert score < 0.90, score  # different papers, must stay below the dedup threshold

    assert author_overlap(["Smith, Jane"], ["Smith J"]) == 1.0
    assert author_overlap(["Smith, Jane"], ["Nguyen, Thi"]) == 0.0
    assert author_overlap([], ["Smith J"]) == 0.0

    records = [
        Record(title="A Study of X", doi="10.1/a", authors=["Smith, J"]),
        Record(title="A Study of X", doi="10.1/A", authors=["Smith, J"]),  # exact DOI dup (case)
        Record(title="A Completely Different Study of Y", doi="10.1/b", authors=["Nguyen, T"]),
    ]
    result = deduplicate(records)
    assert len(result.unique_records) == 2
    assert len(result.matches) == 1
    assert result.matches[0].reason == "exact_doi"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

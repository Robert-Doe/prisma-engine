"""
Module 3 — Bibliographic Record Model

Defines one canonical Record shape, and parsers that normalize three
genuinely different real-world export formats (RIS, BibTeX, and a
Crossref-API-shaped JSON dict) into it. The same underlying paper, fed in
through all three parsers, must come out as the same Record in every field
that matters — that equivalence is the thing this module proves.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Record:
    """The canonical shape every source gets normalized into."""

    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    source_format: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "venue": self.venue,
            "abstract": self.abstract,
            "doi": self.doi,
            "source_format": self.source_format,
        }


class ParseError(ValueError):
    """Raised when an input string doesn't contain the fields a parser
    needs to build a minimally valid Record (a title, at minimum)."""


# --- RIS -------------------------------------------------------------------
# RIS is tag-based: two-letter tag, spaces, a dash, a space, then the
# value, one field per line. AU may repeat for multiple authors.

_RIS_LINE_RE = re.compile(r"^([A-Z0-9]{2})\s+-\s?(.*)$")


def parse_ris(text: str) -> Record:
    authors: list[str] = []
    fields: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("ER"):
            continue
        m = _RIS_LINE_RE.match(line)
        if not m:
            continue
        tag, value = m.group(1), m.group(2).strip()
        if tag == "AU":
            authors.append(value)
        else:
            fields[tag] = value

    if "TI" not in fields:
        raise ParseError("RIS record has no TI (title) field")

    year = int(fields["PY"]) if fields.get("PY", "").isdigit() else None
    return Record(
        title=fields["TI"],
        authors=authors,
        year=year,
        venue=fields.get("JO"),
        abstract=fields.get("AB"),
        doi=fields.get("DO"),
        source_format="RIS",
    )


# --- BibTeX ------------------------------------------------------------------
# A simplified field extractor, not a full BibTeX grammar — see DECISIONS.md
# for why that's an intentional, documented scope limit rather than a bug.

_BIBTEX_FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^{}]*)\}")


def parse_bibtex(text: str) -> Record:
    fields = {k.lower(): v.strip() for k, v in _BIBTEX_FIELD_RE.findall(text)}

    if "title" not in fields:
        raise ParseError("BibTeX record has no title field")

    authors = [a.strip() for a in fields.get("author", "").split(" and ") if a.strip()]
    year = int(fields["year"]) if fields.get("year", "").isdigit() else None
    return Record(
        title=fields["title"],
        authors=authors,
        year=year,
        venue=fields.get("journal"),
        abstract=fields.get("abstract"),
        doi=fields.get("doi"),
        source_format="BibTeX",
    )


# --- Crossref-shaped JSON ------------------------------------------------
# Matches the field names Crossref's public REST API actually returns
# (https://api.crossref.org/works/{doi}) — title/container-title are lists,
# authors are {given, family} dicts, dates are {"date-parts": [[Y, M, D]]}.
# Module 4 calls this same shape from a live response; here it's a literal
# dict standing in for one, so this module has no network dependency.

def parse_crossref_json(data: dict) -> Record:
    titles = data.get("title") or []
    if not titles:
        raise ParseError("Crossref-shaped record has no title")

    authors = []
    for a in data.get("author", []):
        given, family = a.get("given", ""), a.get("family", "")
        name = f"{family}, {given}".strip(", ") if family else given
        if name:
            authors.append(name)

    date_parts = (
        data.get("published", {}).get("date-parts")
        or data.get("issued", {}).get("date-parts")
        or [[None]]
    )
    year = date_parts[0][0] if date_parts and date_parts[0] else None

    containers = data.get("container-title") or []
    abstract = data.get("abstract")
    if abstract:
        # Crossref abstracts are frequently wrapped in JATS XML tags
        # (e.g. <jats:p>...</jats:p>) — strip tags for a plain-text field.
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()

    return Record(
        title=titles[0],
        authors=authors,
        year=year,
        venue=containers[0] if containers else None,
        abstract=abstract,
        doi=data.get("DOI"),
        source_format="CrossrefJSON",
    )


# --- Demo / self-check ----------------------------------------------------

_SAMPLE_RIS = """TY  - JOUR
AU  - Smith, Jane
TI  - Remote Work and Productivity
PY  - 2023
JO  - Journal of Applied Psychology
DO  - 10.1037/xyz
AB  - An examination of productivity outcomes under remote work arrangements.
ER  -
"""

_SAMPLE_BIBTEX = """@article{smith2023remote,
  title    = {Remote Work and Productivity},
  author   = {Smith, Jane},
  year     = {2023},
  journal  = {Journal of Applied Psychology},
  doi      = {10.1037/xyz},
  abstract = {An examination of productivity outcomes under remote work arrangements.}
}"""

_SAMPLE_CROSSREF = {
    "title": ["Remote Work and Productivity"],
    "author": [{"given": "Jane", "family": "Smith"}],
    "published": {"date-parts": [[2023, 6, 1]]},
    "container-title": ["Journal of Applied Psychology"],
    "DOI": "10.1037/xyz",
    "abstract": "<jats:p>An examination of productivity outcomes under remote work arrangements.</jats:p>",
}


def _run_demo() -> None:
    ris_record = parse_ris(_SAMPLE_RIS)
    bibtex_record = parse_bibtex(_SAMPLE_BIBTEX)
    crossref_record = parse_crossref_json(_SAMPLE_CROSSREF)

    for label, rec in [("RIS", ris_record), ("BibTeX", bibtex_record), ("Crossref JSON", crossref_record)]:
        print("=" * 70)
        print(f"Parsed from {label}")
        print("=" * 70)
        for k, v in rec.to_dict().items():
            print(f"  {k:>13}: {v}")
        print()

    print("=" * 70)
    print("Do all three normalize to the same title/authors/year/doi?")
    print("=" * 70)
    same = (
        ris_record.title == bibtex_record.title == crossref_record.title
        and ris_record.authors == bibtex_record.authors == crossref_record.authors
        and ris_record.year == bibtex_record.year == crossref_record.year
        and ris_record.doi == bibtex_record.doi == crossref_record.doi
    )
    print(f"  -> {same} (source_format differs, everything else matches)")


def _run_self_checks() -> None:
    ris = parse_ris(_SAMPLE_RIS)
    assert ris.title == "Remote Work and Productivity"
    assert ris.authors == ["Smith, Jane"]
    assert ris.year == 2023
    assert ris.doi == "10.1037/xyz"
    assert ris.source_format == "RIS"

    bib = parse_bibtex(_SAMPLE_BIBTEX)
    assert bib.title == ris.title
    assert bib.authors == ris.authors
    assert bib.year == ris.year
    assert bib.doi == ris.doi

    xref = parse_crossref_json(_SAMPLE_CROSSREF)
    assert xref.title == ris.title
    assert xref.authors == ris.authors
    assert xref.year == ris.year
    assert xref.doi == ris.doi
    assert "<jats:p>" not in (xref.abstract or "")

    try:
        parse_ris("AU  - Nobody\n")
        raise AssertionError("expected ParseError for missing TI")
    except ParseError:
        pass

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

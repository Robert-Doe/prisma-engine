"""
Module 12 — PRISMA Diagram Generator

Renders a Module 7 PrismaFlowTracker's accumulated state into the actual
field-standard PRISMA flow diagram artifact — real SVG, generated from
real tracker state, not a description of what a diagram would look like.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "07_prisma_flow_tracker"))
from flow_tracker import PrismaFlowTracker  # noqa: E402

BOX_WIDTH = 420
SIDE_BOX_WIDTH = 340
SIDE_X_OFFSET = 470
LINE_HEIGHT = 16
BOX_PADDING = 10
GAP_BETWEEN_STAGES = 50


def _wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        trial = f"{current} {w}".strip()
        if len(trial) > max_chars and current:
            lines.append(current)
            current = w
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [""]


def _box(x: float, y: float, width: float, text_lines: list[str], fill: str) -> tuple[str, float]:
    height = BOX_PADDING * 2 + LINE_HEIGHT * len(text_lines)
    parts = [
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{fill}" stroke="#333333" stroke-width="1.5" rx="5"/>'
    ]
    text_y = y + BOX_PADDING + LINE_HEIGHT * 0.75
    for i, line in enumerate(text_lines):
        parts.append(
            f'<text x="{x + width / 2}" y="{text_y + i * LINE_HEIGHT}" '
            f'font-size="12.5" font-family="Arial, sans-serif" text-anchor="middle">{escape(line)}</text>'
        )
    return "\n".join(parts), height


def _arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333333" stroke-width="1.5" marker-end="url(#arrowhead)"/>'


def render_prisma_svg(tracker: PrismaFlowTracker, title: str = "PRISMA Flow Diagram") -> str:
    """Builds real SVG markup from the tracker's actual logged state.
    Gracefully renders a partial diagram if eligibility hasn't been
    logged yet (only identification/dedup/screening)."""
    main_x = 60.0
    side_x = main_x + SIDE_X_OFFSET
    y = 50.0
    elements: list[str] = []

    per_source = "; ".join(f"{src} (n = {count})" for src, count in tracker.identification.items())
    id_lines = _wrap_text(
        f"Records identified from: {per_source}. Total identified (n = {tracker.total_identified()})", 55
    )
    box_svg, h = _box(main_x, y, BOX_WIDTH, id_lines, "#dbe9f7")
    elements.append(box_svg)
    id_bottom = y + h

    if tracker.duplicates_removed:
        dup_lines = _wrap_text(f"Duplicate records removed (n = {tracker.duplicates_removed})", 42)
        dup_svg, dup_h = _box(side_x, y, SIDE_BOX_WIDTH, dup_lines, "#f7e3d8")
        elements.append(dup_svg)
        elements.append(_arrow(main_x + BOX_WIDTH, y + h / 2, side_x, y + dup_h / 2))

    y = id_bottom + GAP_BETWEEN_STAGES
    elements.append(_arrow(main_x + BOX_WIDTH / 2, id_bottom, main_x + BOX_WIDTH / 2, y))

    screened_lines = _wrap_text(f"Records screened (title/abstract) (n = {tracker.after_dedup()})", 55)
    box_svg, h = _box(main_x, y, BOX_WIDTH, screened_lines, "#dbe9f7")
    elements.append(box_svg)
    screened_bottom = y + h

    if tracker.screening_included is not None:
        reasons = "; ".join(f"{reason} (n = {count})" for reason, count in tracker.screening_excluded.items())
        excl_lines = _wrap_text(
            f"Records excluded (n = {tracker.total_screening_excluded()}): {reasons}", 42
        )
        excl_svg, excl_h = _box(side_x, y, SIDE_BOX_WIDTH, excl_lines, "#f7e3d8")
        elements.append(excl_svg)
        elements.append(_arrow(main_x + BOX_WIDTH, y + h / 2, side_x, y + excl_h / 2))

        y = screened_bottom + GAP_BETWEEN_STAGES
        elements.append(_arrow(main_x + BOX_WIDTH / 2, screened_bottom, main_x + BOX_WIDTH / 2, y))

        elig_lines = _wrap_text(f"Reports assessed for eligibility (n = {tracker.screening_included})", 55)
        box_svg, h = _box(main_x, y, BOX_WIDTH, elig_lines, "#dbe9f7")
        elements.append(box_svg)
        elig_bottom = y + h

        if tracker.eligibility_included is not None:
            elig_reasons = "; ".join(f"{reason} (n = {count})" for reason, count in tracker.eligibility_excluded.items())
            excl2_lines = _wrap_text(
                f"Reports excluded (n = {tracker.total_eligibility_excluded()}): {elig_reasons}", 42
            )
            excl2_svg, excl2_h = _box(side_x, y, SIDE_BOX_WIDTH, excl2_lines, "#f7e3d8")
            elements.append(excl2_svg)
            elements.append(_arrow(main_x + BOX_WIDTH, y + h / 2, side_x, y + excl2_h / 2))

            y = elig_bottom + GAP_BETWEEN_STAGES
            elements.append(_arrow(main_x + BOX_WIDTH / 2, elig_bottom, main_x + BOX_WIDTH / 2, y))

            included_lines = _wrap_text(f"Studies included in review (n = {tracker.eligibility_included})", 55)
            box_svg, h = _box(main_x, y, BOX_WIDTH, included_lines, "#d9f0dc")
            elements.append(box_svg)
            y = y + h

    total_height = y + 40
    total_width = side_x + SIDE_BOX_WIDTH + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" '
        f'viewBox="0 0 {total_width} {total_height}">',
        '<defs><marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
        '<path d="M0,0 L8,4 L0,8 Z" fill="#333333"/></marker></defs>',
        f'<rect x="0" y="0" width="{total_width}" height="{total_height}" fill="white"/>',
        f'<text x="{total_width / 2}" y="25" font-size="16" font-family="Arial, sans-serif" '
        f'text-anchor="middle" font-weight="bold">{escape(title)}</text>',
    ]
    svg.extend(elements)
    svg.append("</svg>")
    return "\n".join(svg)


def save_svg(svg_markup: str, path: Path) -> None:
    path.write_text(svg_markup, encoding="utf-8")


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "05_multi_source_aggregator"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "06_deduplication_engine"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "08_screening_engine"))
    from aggregator import fetch_arxiv, merge_sources, search_pubmed  # noqa: E402
    from dedup_engine import deduplicate  # noqa: E402
    from screening_engine import screen, DEFAULT_RULES  # noqa: E402

    print("=" * 70)
    print("Real pipeline: Modules 4-8 chained, then rendered as a real diagram")
    print("=" * 70)
    pubmed_query = (
        '("knowledge workers" OR "office workers" OR employees) '
        'AND ("remote work" OR telecommut* OR "work from home" OR "hybrid work" OR MeSH:"Teleworking")'
    )
    arxiv_query = '(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)'

    pubmed_records, _t1, _t2 = search_pubmed(pubmed_query, retmax=5)
    arxiv_records, _t3 = fetch_arxiv(arxiv_query, max_results=5)
    corpus, _stats = merge_sources(pubmed_records, arxiv_records)
    dedup_result = deduplicate(corpus)
    screening_result = screen(dedup_result.unique_records, DEFAULT_RULES)

    tracker = PrismaFlowTracker()
    tracker.log_identification("PubMed", len(pubmed_records))
    tracker.log_identification("arXiv", len(arxiv_records))
    tracker.log_deduplication(len(corpus) - len(dedup_result.unique_records))
    tracker.log_screening(screening_result.excluded_by_reason(), included_count=len(screening_result.included))
    tracker.validate_conservation()

    svg = render_prisma_svg(tracker, title="Remote Work & Productivity — PRISMA Flow (Modules 4-8)")
    out_path = Path(__file__).resolve().parent / "prisma_flow_demo.svg"
    save_svg(svg, out_path)

    print(f"Rendered SVG: {len(svg)} characters, saved to {out_path.name}")

    # Prove it's well-formed XML, not just a string that looks like SVG.
    root = ET.fromstring(svg)
    rects = root.findall(".//{http://www.w3.org/2000/svg}rect")
    texts = root.findall(".//{http://www.w3.org/2000/svg}text")
    print(f"Parsed as valid XML: {len(rects)} rect elements, {len(texts)} text elements")
    print(f"SVG root tag: {root.tag}")


def _run_self_checks() -> None:
    tracker = PrismaFlowTracker()
    tracker.log_identification("SourceA", 20)
    tracker.log_deduplication(4)
    tracker.log_screening({"wrong population": 6}, included_count=10)
    tracker.log_eligibility({"no full text": 2}, included_count=8)
    tracker.validate_conservation()

    svg = render_prisma_svg(tracker)
    root = ET.fromstring(svg)  # raises if malformed
    assert root.tag == "{http://www.w3.org/2000/svg}svg"

    all_text = "".join(t.text or "" for t in root.iter("{http://www.w3.org/2000/svg}text"))
    assert "n = 20" in all_text  # total identified
    assert "n = 4" in all_text  # duplicates removed
    assert "n = 10" in all_text  # passed screening -> assessed for eligibility
    assert "n = 8" in all_text  # final included

    # Partial diagram (no eligibility logged) still renders as valid SVG.
    partial = PrismaFlowTracker()
    partial.log_identification("X", 5)
    partial.log_deduplication(0)
    partial_svg = render_prisma_svg(partial)
    partial_root = ET.fromstring(partial_svg)
    assert partial_root.tag == "{http://www.w3.org/2000/svg}svg"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

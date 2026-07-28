"""
Module 20 — Review Report Compiler

The capstone of Track 1: compiles the real output of nearly every prior
module into one publishable HTML report. The search-and-screen section
(Modules 1-2, 4-8) runs a real, live pipeline. The synthesis section
(Modules 10, 14, 16-19) uses this course's established fictional
remote-work studies, consistent with every prior module that used them.
Both halves are about the same real-world topic — this module is where
they finally converge into one document.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULES = HERE.parent

for name in [
    "01_research_question_formalizer", "02_boolean_query_builder",
    "03_bibliographic_record_model", "05_multi_source_aggregator",
    "06_deduplication_engine", "07_prisma_flow_tracker", "08_screening_engine",
    "10_data_extraction_engine", "12_prisma_diagram_generator",
    "14_evidence_table_builder", "16_effect_size_calculator",
    "17_meta_analysis_engine", "18_forest_plot_renderer", "19_publication_bias_detector",
]:
    sys.path.insert(0, str(MODULES / name))

from formalizer import formalize, Framework  # noqa: E402
from query_builder import build_query, SlotTerms  # noqa: E402
from record_model import Record  # noqa: E402
from aggregator import search_pubmed, fetch_arxiv, merge_sources  # noqa: E402
from dedup_engine import deduplicate  # noqa: E402
from flow_tracker import PrismaFlowTracker  # noqa: E402
from screening_engine import screen, DEFAULT_RULES  # noqa: E402
from diagram_generator import render_prisma_svg, save_svg  # noqa: E402
from extraction_engine import extract, REMOTE_WORK_SCHEMA  # noqa: E402
from evidence_table import build_evidence_table  # noqa: E402
from effect_size import odds_ratio  # noqa: E402
from meta_analysis import from_effect_size_result, fixed_effect_meta_analysis, random_effects_meta_analysis  # noqa: E402
from forest_plot import render_forest_plot  # noqa: E402
from publication_bias import eggers_test, render_funnel_plot  # noqa: E402


def _evidence_table_html(table) -> str:
    cols = table.column_names()
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    rows_html = []
    for row in table.to_dict_rows():
        cells = "".join(f"<td>{escape(str(row.get(c, '')))}</td>" for c in cols)
        rows_html.append(f"<tr>{cells}</tr>")
    return f"<table><tr>{head}</tr>{''.join(rows_html)}</table>"


def compile_report(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Section 1-2: research question + search query (Modules 1-2) ---
    rq = formalize(
        "Does remote work affect employee productivity compared to in-office work?",
        framework=Framework.PICO,
        slots={
            "population": "knowledge workers",
            "intervention": "remote work arrangements",
            "outcome": "measured or self-reported productivity",
        },
    )
    query_terms = {
        "population": SlotTerms(free_text=["knowledge workers", "office workers", "employees"]),
        "intervention": SlotTerms(
            free_text=["remote work", "telecommut*", "work from home", "hybrid work"],
            controlled_vocab=["Teleworking"],
        ),
    }
    search_query = build_query(rq, query_terms)

    # --- Section 3: real, live search-and-screen pipeline (Modules 4-8) ---
    # search_pubmed() (Module 4) translates the MeSH:"..." tag internally.
    pubmed_records, pm_total, _t = search_pubmed(search_query, retmax=5)
    arxiv_records, ax_total = fetch_arxiv(
        '(abs:"remote work" OR abs:telecommuting) AND (abs:productivity OR abs:performance)', max_results=5
    )
    corpus, _stats = merge_sources(pubmed_records, arxiv_records)
    dedup_result = deduplicate(corpus)
    screening_result = screen(dedup_result.unique_records, DEFAULT_RULES)

    tracker = PrismaFlowTracker()
    tracker.log_identification("PubMed", len(pubmed_records))
    tracker.log_identification("arXiv", len(arxiv_records))
    tracker.log_deduplication(len(corpus) - len(dedup_result.unique_records))
    tracker.log_screening(screening_result.excluded_by_reason(), included_count=len(screening_result.included))
    tracker.validate_conservation()

    prisma_svg = render_prisma_svg(tracker, title="Remote Work & Productivity — PRISMA Flow")
    save_svg(prisma_svg, output_dir / "prisma_flow.svg")

    # --- Section 4: evidence table (Modules 10, 14) ---
    studies_data = [
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
    extracted = [extract(r, REMOTE_WORK_SCHEMA, d) for r, d in studies_data]
    evidence_table = build_evidence_table(extracted, REMOTE_WORK_SCHEMA)

    # --- Section 5: meta-analysis + forest plot (Modules 16-18) ---
    or_studies = {
        "Study A": odds_ratio(a=30, b=10, c=15, d=25),
        "Study B": odds_ratio(a=25, b=15, c=12, d=28),
        "Study C": odds_ratio(a=40, b=20, c=20, d=40),
        "Study D": odds_ratio(a=18, b=22, c=20, d=20),
        "Study E": odds_ratio(a=12, b=28, c=22, d=18),
    }
    effects = [from_effect_size_result(label, r) for label, r in or_studies.items()]
    fixed = fixed_effect_meta_analysis(effects)
    random = random_effects_meta_analysis(effects)
    render_forest_plot(effects, random, output_dir / "forest_plot.png", measure_name="Odds Ratio")

    # --- Section 6: publication bias (Module 19) ---
    eggers = eggers_test(effects)
    render_funnel_plot(effects, fixed.pooled_y, output_dir / "funnel_plot.png")

    # --- Assemble the report ---
    pooled_est, pooled_lo, pooled_hi = random.display_estimate()
    html = _render_html(
        rq=rq, search_query=search_query, tracker=tracker,
        evidence_table_html=_evidence_table_html(evidence_table),
        pooled_est=pooled_est, pooled_lo=pooled_lo, pooled_hi=pooled_hi,
        i2=random.I2, eggers=eggers,
    )
    out_path = output_dir / "review_report.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _render_html(*, rq, search_query, tracker, evidence_table_html, pooled_est, pooled_lo, pooled_hi, i2, eggers) -> str:
    significance = "does not cross" if not (pooled_lo <= 1.0 <= pooled_hi) else "crosses"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Review Report: Remote Work and Productivity</title>
<style>
body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
h1, h2 {{ font-family: Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #999; padding: 6px 10px; text-align: left; font-size: 0.9em; }}
th {{ background: #eee; }}
img {{ max-width: 100%; }}
.stage {{ font-family: monospace; background: #f5f5f5; padding: 8px 12px; margin: 4px 0; }}
</style>
</head>
<body>
<h1>Systematic Review Report: Remote Work and Productivity</h1>

<h2>1. Research Question</h2>
<p><strong>Framework:</strong> {escape(rq.framework.value)}</p>
<p><strong>Question:</strong> {escape(rq.raw_text)}</p>
<ul>{"".join(f"<li><strong>{escape(k)}:</strong> {escape(v)}</li>" for k, v in rq.slots.items())}</ul>

<h2>2. Search Strategy</h2>
<p><code>{escape(search_query)}</code></p>

<h2>3. Study Selection (PRISMA)</h2>
<div class="stage">Identified: {tracker.total_identified()} ({", ".join(f"{s}: {c}" for s, c in tracker.identification.items())})</div>
<div class="stage">After deduplication: {tracker.after_dedup()} ({tracker.duplicates_removed} duplicates removed)</div>
<div class="stage">Passed title/abstract screening: {tracker.screening_included} ({tracker.total_screening_excluded()} excluded: {tracker.screening_excluded})</div>
<img src="prisma_flow.svg" alt="PRISMA flow diagram">

<h2>4. Evidence Table</h2>
<p>Illustrative extracted studies (see Modules 10/14):</p>
{evidence_table_html}

<h2>5. Meta-Analysis</h2>
<p>Pooled odds ratio (random-effects): <strong>{pooled_est:.3f}</strong>
95% CI [{pooled_lo:.3f}, {pooled_hi:.3f}] — heterogeneity I² = {i2:.1f}%</p>
<img src="forest_plot.png" alt="Forest plot">

<h2>6. Publication Bias</h2>
<p>Egger's test intercept = {eggers.intercept:.3f}, t = {eggers.t_statistic:.3f}
(df={eggers.df}), significant at p&lt;0.05: {eggers.significant_at_05}.
<em>Caveat: only {eggers.n_studies} studies — below the ~10-study threshold the
Cochrane Handbook recommends for interpreting this test.</em></p>
<img src="funnel_plot.png" alt="Funnel plot">

<h2>7. Narrative Synthesis</h2>
<p>Across the {tracker.screening_included if tracker.screening_included else 0} records that passed
title/abstract screening in the live search, and the illustrative set of
quantitative studies synthesized above, the pooled random-effects odds
ratio of {pooled_est:.2f} suggests a possible positive association between
remote work and productivity, but its 95% confidence interval
[{pooled_lo:.3f}, {pooled_hi:.3f}] {significance} the no-effect value of 1.0,
and heterogeneity is substantial (I² = {i2:.1f}%). This combination — a
point estimate favoring an effect, but a confidence interval that does not
rule out no effect, alongside high heterogeneity — means the honest
conclusion is "an effect in this direction is plausible but not
established," not "remote work improves productivity."</p>

</body>
</html>"""


# --- Demo / self-check ------------------------------------------------------

def _run_demo() -> None:
    out_path = compile_report(HERE)
    text = out_path.read_text(encoding="utf-8")
    print(f"Report compiled: {out_path.name} ({len(text)} characters)")
    for required in ["Research Question", "Search Strategy", "PRISMA", "Evidence Table",
                      "Meta-Analysis", "Publication Bias", "Narrative Synthesis"]:
        print(f"  contains section '{required}': {required in text}")
    for asset in ["prisma_flow.svg", "forest_plot.png", "funnel_plot.png"]:
        exists = (HERE / asset).exists()
        print(f"  asset {asset} exists: {exists}")


def _run_self_checks() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out_path = compile_report(Path(tmp))
        assert out_path.exists()
        text = out_path.read_text(encoding="utf-8")
        assert "<h1>Systematic Review Report" in text
        assert "<table>" in text
        assert (Path(tmp) / "prisma_flow.svg").exists()
        assert (Path(tmp) / "forest_plot.png").exists()
        assert (Path(tmp) / "funnel_plot.png").exists()
        assert (Path(tmp) / "prisma_flow.svg").stat().st_size > 500
        assert (Path(tmp) / "forest_plot.png").stat().st_size > 1000
    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

# Module 20 — Decisions: Review Report Compiler

## Line-by-line / unit-by-unit

### The search-and-screen section uses a real, live pipeline (Modules 1-2, 4-8); the synthesis section uses this course's established fictional studies (Modules 10, 14, 16-19)
**(c) Convention, carried forward from every prior module's own honesty requirements.** This isn't a compromise specific to this module — it's the accumulated consequence of decisions made all the way back in Modules 9 and 16: this course has real access to live search results, but not to real papers' full text or raw statistical data, and inventing either would misrepresent real, identifiable work. Module 20 doesn't relax that boundary just because it's the capstone; it compiles both halves faithfully, each honest about what it actually is.

### Both halves are kept on the same real-world topic (remote work and productivity)
**(c) Convention.** Nothing forces the search-and-screen section and the synthesis section to discuss the same subject — they're structurally independent pipelines. Keeping them thematically aligned is what makes the final report read as one coherent document instead of two unrelated demos stapled together, even though a reader should understand (and the report says directly) that the synthesized studies are illustrative rather than the actual results of screening the live-fetched records.

### The report is one self-contained HTML file plus three sibling asset files (SVG + 2 PNGs), not one giant inlined document
**(c) Convention, following Module 12 and Module 18's existing precedent.** Both of those modules already save real image files to disk rather than inlining raster data as base64 — Module 20 continues that pattern rather than inventing a new one. A reviewer can open `review_report.html` in any browser and it "just works" as long as the three asset files stay alongside it, the same deployment model as this course's own tutorials.

### `_evidence_table_html()` is a new, small HTML-table renderer, not a reuse of Module 14's `render_markdown()`
**(c) Convention.** Module 14's Markdown output is the right format for a terminal or a Markdown-rendering context; a real HTML report needs a real `<table>` element, not literal pipe characters. Both functions read from the exact same `EvidenceTable.to_dict_rows()` data — only the output format differs, matching the same "one data source, format-specific renderers" pattern Module 12 and Module 18 already established for other artifacts.

### Every value embedded in the report is escaped with `html.escape()`
**(b) Forced by external contract.** Any string value (a study title, a slot value) that happened to contain `<`, `>`, or `&` would corrupt the HTML output if inserted unescaped — this isn't a hypothetical for a review report specifically, since paper titles legitimately contain characters like `&` reasonably often. Escaping every interpolated value is the correct, standard defense, not an optional nicety.

### The narrative synthesis paragraph is templated from real computed numbers, not freely-written prose
**(c) Convention.** Every number quoted in Section 7 (`pooled_est`, `pooled_lo`, `pooled_hi`, `i2`) is pulled directly from the same `MetaAnalysisResult` object Section 5 displays — the template can't drift out of sync with the numbers above it, because there's only one source for both. The conclusion's careful hedging ("plausible but not established," not "remote work improves productivity") is deliberately written to match what a CI crossing 1.0 with I²=84.8% actually supports, not to oversell the result.

## Decisions We Made

| Decision | Category |
|---|---|
| Real live pipeline + established fictional studies, kept separate and honest | (c) Convention, carried forward from Modules 9/16 |
| Both halves share one real-world topic for narrative coherence | (c) Convention |
| One HTML file + sibling asset files, not one inlined document | (c) Convention, following Modules 12/18 |
| New HTML table renderer, not reuse of Module 14's Markdown renderer | (c) Convention |
| Every interpolated value HTML-escaped | (b) External contract (HTML injection prevention) |
| Narrative paragraph templated from the same numbers displayed above it | (c) Convention |

## What We Proved

Running [`report_compiler.py`](report_compiler.py) is the single largest
integration test in this course — it imports and calls real functions from
fourteen prior modules in one run, and:

1. **A complete, real review report was produced end to end** — from a formalized research question (Module 1) through a live PubMed+arXiv search, dedup, and screen (Modules 4-8), through a rendered PRISMA diagram (Module 12), an evidence table (Module 14), a meta-analysis with forest plot (Modules 16-18), and a publication-bias check (Module 19) — genuinely compiled into one HTML file, not described as if it could be.
2. **Every section's content is traceable to a real computed value**, verified directly: the self-checks assert the compiled HTML actually contains each expected section heading, and that all three referenced asset files exist on disk with non-trivial size — not just that `compile_report()` returned without raising.
3. **The report's own conclusion correctly reflects its own uncertain evidence.** The narrative synthesis states the confidence interval crosses 1.0 and heterogeneity is high, and hedges its conclusion accordingly — the compiler doesn't overstate what the (illustrative) numbers support, mirroring the same honesty this course has required of every module that came before it.

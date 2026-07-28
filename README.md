# prisma-engine

**A PRISMA-compliant systematic-literature-review pipeline — built one verifiable stage at a
time, not assembled from a library you'd have to trust blindly.**

prisma-engine is a real, runnable engine that takes a research question in and produces a
publishable systematic review out: search formalization → live multi-source retrieval →
deduplication → PRISMA-tracked screening → data extraction → risk-of-bias appraisal → citation
snowballing → thematic and statistical synthesis → meta-analysis → publication-bias detection →
a compiled report with its PRISMA flow diagram and forest plots. Every stage is a small, working
Python module against free, no-key academic APIs (Crossref, arXiv, PubMed E-utilities), so the
whole pipeline is actually runnable, not a diagram of what a review "would" involve.

This repository doubles as the course that builds it: each stage ships a `tutorial.html`
walkthrough and a `DECISIONS.md` explaining the implementation choices, so the finished tool and
the reasoning behind it are inseparable. But the product is the pipeline — 30 modules that
compose into one system, not 30 independent exercises.

## Why a kernel/userland split

The architecture mirrors an OS course on purpose. **Track 1 is the kernel** — the 20 modules
every systematic review needs regardless of type: formalizing a question, searching, deduping,
screening, extracting, appraising, synthesizing, reporting. **Track 2 is userland** — 10 modules
proving that kernel generalizes, by adapting it to scoping reviews, rapid reviews, bibliometric
analysis, qualitative (meta-ethnographic) synthesis, umbrella reviews, living reviews, and even
non-PRISMA use cases like a systems-conference Related Work section or a first thesis chapter.
If the kernel only ever ran one program, it wouldn't prove much; Track 2 is the proof it doesn't.

A **Module 0 orientation** (`modules/track0_orientation/`) sits before both tracks as a reference
map of all ~19 named review types in the literature (grounded in Grant & Booth's 2009 SALSA
typology), so every later module can say "you are here" instead of implying it invented the only
kind of review that exists. A **Prerequisites layer** (`prerequisites/`) covers the primitives —
PICO/PEO frameworks, boolean search logic, bibliographic metadata, study-design taxonomy,
eligibility-criteria logic, effect-size statistics, and the PRISMA standard itself — that every
later module assumes without re-explaining.

## Repository layout

| Path | What lives there |
|---|---|
| [`prerequisites/`](prerequisites/) | Standalone primitives every module assumes (PICO, boolean search, DOI/RIS, PRISMA, effect sizes, synthesis-vs-summary) |
| [`modules/track0_orientation/`](modules/track0_orientation/) | Module 0 — the full review-type landscape and how this engine's modules map onto it |
| [`modules/track1/`](modules/track1/) | Modules 1–20 — the core engine (kernel) |
| [`modules/track2/`](modules/track2/) | Modules 21–30 — applied review-methodology adaptations (userland) |
| [`lessons/`](lessons/) | Cross-cutting concept clusters spanning multiple modules (deduplication patterns, statistical pooling, heuristic text classification and its limits) |
| [`assets/`](assets/) | Shared tutorial design system (dark-theme CSS used by every `tutorial.html`) |
| [`GLOSSARY.md`](GLOSSARY.md) | Append-only glossary, each term tagged with the module that first introduced it |
| [`ROADMAP.md`](ROADMAP.md) | Full course/engine design doc: module-by-module specs, recommended stopping points, architecture targets |

## Module map

### Track 1 — Core engine

| # | Module | Proves |
|---|--------|--------|
| 1 | [Research Question Formalizer](modules/track1/01_research_question_formalizer/) | A natural-language question decomposes into structured, machine-checkable PICO/PEO fields |
| 2 | [Boolean Query Builder](modules/track1/02_boolean_query_builder/) | A structured question compiles into a reproducible boolean search string with synonym expansion |
| 3 | [Bibliographic Record Model](modules/track1/03_bibliographic_record_model/) | Heterogeneous citation formats (RIS, BibTeX, API JSON) normalize into one canonical schema |
| 4 | [Live API Connector](modules/track1/04_live_api_connector/) | The query builder's output retrieves real results from a live academic database |
| 5 | [Multi-Source Aggregator](modules/track1/05_multi_source_aggregator/) | Independently-shaped sources merge into one corpus without losing provenance |
| 6 | [Deduplication Engine](modules/track1/06_deduplication_engine/) | Duplicates across sources are caught via exact (DOI) and fuzzy (title/author) matching |
| 7 | [PRISMA Flow Tracker](modules/track1/07_prisma_flow_tracker/) | Every record's fate is counted and audited at each pipeline stage |
| 8 | [Title/Abstract Screening Engine](modules/track1/08_screening_engine/) | Inclusion/exclusion criteria apply systematically, every decision logged with a reason |
| 9 | [Full-Text Eligibility Engine](modules/track1/09_fulltext_eligibility_engine/) | A second full-text pass catches false inclusions title/abstract screening let through |
| 10 | [Data Extraction Form Engine](modules/track1/10_data_extraction_engine/) | Unstructured study text converts into structured, cross-study-comparable data |
| 11 | [Risk-of-Bias / Quality Appraisal Scorer](modules/track1/11_risk_of_bias_scorer/) | Study quality quantifies via a checklist rubric instead of being asserted by feel |
| 12 | [PRISMA Diagram Generator](modules/track1/12_prisma_diagram_generator/) | The flow tracker's state renders into the field-standard PRISMA diagram |
| 13 | [Citation Snowballing Engine](modules/track1/13_citation_snowballing_engine/) | The corpus expands beyond the initial search via backward/forward citation traversal |
| 14 | [Evidence Table Builder](modules/track1/14_evidence_table_builder/) | Heterogeneous included studies become directly comparable in one normalized table |
| 15 | [Thematic Coding Engine](modules/track1/15_thematic_coding_engine/) | Qualitative synthesis (open + axial coding) is structured and repeatable, not a vibe |
| 16 | [Effect Size Calculator](modules/track1/16_effect_size_calculator/) | Standardized effect sizes (OR, RR, SMD) with CIs derive correctly from raw study numbers |
| 17 | [Meta-Analysis Engine](modules/track1/17_meta_analysis_engine/) | Study effects pool statistically (fixed/random effects) with a heterogeneity measure (I²) |
| 18 | [Forest Plot Renderer](modules/track1/18_forest_plot_renderer/) | A pooled result renders in the field-standard forest plot format |
| 19 | [Publication Bias Detector](modules/track1/19_publication_bias_detector/) | The pooled result is checked for selection bias via funnel plot asymmetry and Egger's test |
| 20 | [Review Report Compiler](modules/track1/20_review_report_compiler/) | Every artifact the pipeline produced converges into one publishable report |

### Track 2 — Applied layer

| # | Module | Proves |
|---|--------|--------|
| 21 | [Scoping Review Mapper](modules/track2/21_scoping_review_mapper/) | The pipeline answers "what does the field look like," not just "what is the effect" |
| 22 | [Rapid Review Adapter](modules/track2/22_rapid_review_adapter/) | The pipeline degrades gracefully under a time-box while documenting the rigor traded away |
| 23 | [Bibliometric / Citation Network Analyzer](modules/track2/23_bibliometric_network_analyzer/) | The corpus itself is analyzable as a network (centrality, co-citation clustering) |
| 24 | [Qualitative Evidence Synthesis](modules/track2/24_qualitative_evidence_synthesis/) | Qualitative studies synthesize into new interpretive findings without pooling numbers |
| 25 | [Umbrella Review Aggregator](modules/track2/25_umbrella_review_aggregator/) | The pipeline is recursive — it can treat other reviews as its unit of analysis |
| 26 | [Living Review Updater](modules/track2/26_living_review_updater/) | The pipeline runs as a maintained system, incrementally processing only new records |
| 27 | [Related-Work Comparison Matrix Builder](modules/track2/27_related_work_comparison_matrix/) | Systems/security-paper prior work organizes as a dimension-by-system matrix, not a PRISMA table |
| 28 | [Positioning & Gap-Statement Generator](modules/track2/28_positioning_gap_statement_generator/) | A novelty claim derives mechanically from the comparison matrix, grounded in cited abstracts |
| 29 | [Synthesis Matrix Builder](modules/track2/29_synthesis_matrix_builder/) *(beginner on-ramp)* | Organizing sources by theme instead of by source is the mechanical difference between synthesis and summary |
| 30 | [Thesis Gap-to-Research-Question Funnel Builder](modules/track2/30_thesis_gap_funnel_builder/) *(beginner on-ramp)* | A thesis research question can be argued into existence by funneling from broad context to one defensible gap |

## Tech stack

- **Python 3.11+** — every pipeline stage, stdlib plus `requests` and `matplotlib`; deliberately
  dependency-light so every artifact stays inspectable
- **Crossref, arXiv, PubMed E-utilities, Semantic Scholar** — free, no-API-key academic data
  sources, so the pipeline runs without credential setup
- **Flat JSON / SQLite** — per-module persistence, no external database service, state always
  inspectable as a file
- **Generated SVG/HTML** for PRISMA and citation-network diagrams; **matplotlib** for forest and
  funnel plots
- Static HTML tutorials with one shared dark-theme design system (`assets/style.css`) — no build
  step, no JS framework

Explicitly out of scope (documented in `ROADMAP.md`): ML/NLP-based screening classifiers
(rule-based screening only), reference-manager GUI integrations, multi-user review platforms,
manuscript/LaTeX templating, and paywalled full-text retrieval.

## Status

All 30 modules built (20 core-engine + 10 applied-layer), plus the Module 0 orientation cluster,
the Prerequisites layer, and 3 cross-cutting lesson clusters. See `ROADMAP.md`'s "Recommended
Stopping Points" table for shorter paths through the pipeline (e.g. stop at Module 6 for a
reproducible search-and-dedupe tool, Module 20 for a full quantitative review, or jump straight
to Module 30 for a minimal thesis-chapter workflow).

## How to run

Each module is self-contained under its own directory with its own Python script and
`DECISIONS.md`:

```bash
cd modules/track1/01_research_question_formalizer
python formalizer.py
```

Start with `prerequisites/index.html`, then `modules/track0_orientation/` for the review-type
map, then work through `modules/track1/01` → `20` in order — each stage's output feeds the next.
`GLOSSARY.md` and `ROADMAP.md` are the two reference documents worth keeping open throughout.

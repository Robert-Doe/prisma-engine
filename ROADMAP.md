# ROADMAP — Literature Review & Research Methods, From Scratch

A code-first course that builds a real, working systematic-literature-review
pipeline, one small verifiable module at a time. By the end of Track 1 you
will have built (not used) a PRISMA-compliant search → dedupe → screen →
extract → appraise → synthesize → report engine, driven against live
academic APIs. Track 2 builds the applied review methodologies (scoping,
rapid, bibliometric, qualitative, umbrella, living, conference-paper
positioning, and thesis-chapter writing) as adaptations layered on top of
that engine.

This mirrors an OS course's kernel/userland split: Track 1 is the "kernel" —
the mechanics every review needs regardless of type. Track 2 is "userland" —
the different things you can run on that kernel once it exists.

---

## Module 0 — Orientation: The Literature Review Landscape
*No code — this is a reference cluster, built using the same "vocabulary web" pattern the course uses later for any cluster of terms learners conflate (Phase 4 in the course methodology). It exists so that every numbered module below can say "you are here" against the full map of review types instead of implying it invented the only kind that exists.*

**Directory:** `modules/track0_orientation/00_literature_review_landscape/`

**Files (Head First style throughout — vivid analogy first, jargon second):**
- `tutorial.html` — why so many review types exist (different questions demand different evidence), a decision-tree diagram ("what are you trying to find out? → which review type fits"), and an explicit map of which later module builds which type.
- One `concept_<type>.html` per review type (list below) — each ends with a "how this connects to the other types" callout plus links to its closest siblings, per your Phase 4 pattern.
- `concept_how_they_connect.html` — hub page: a definitions side-by-side grid, one visual chain/diagram placing every type on axes of *breadth vs. depth* and *aggregative (pools findings) vs. configurative (arranges findings)*, a "commonly confused pairs" table (e.g. "systematic review" vs. "systematic**ized**  review," "scoping review" vs. "mapping review," "meta-analysis" vs. "meta-synthesis" vs. "meta-ethnography," "umbrella review" vs. "overview," "rapid review" vs. "rapid evidence assessment"), and a scenario-matching quiz.

**Proposed type list** (grounded primarily in Grant & Booth's 2009 14-type SALSA typology — the standard citation for "a typology of reviews" — plus a few well-established additions, and explicit cross-links to the genres this course already builds):

*From Grant & Booth (2009):*
1. Critical review
2. Literature review / traditional (narrative) review
3. Mapping review / systematic map
4. Meta-analysis
5. Mixed studies / mixed methods review
6. Overview
7. Qualitative systematic review / meta-synthesis
8. Rapid review
9. Scoping review
10. State-of-the-art review
11. Systematic review
12. Systematic search and review
13. Systematized review
14. Umbrella review

*Additional established types:*
15. Integrative review
16. Realist review (realist synthesis)
17. Meta-ethnography
18. Bibliometric review / citation analysis
19. Living systematic review

*Cross-linked, not re-explained (already have full modules elsewhere in this course):*
- Positioning / "Related Work" review (USENIX/OSDI/NSDI-style) → Modules 27–28
- Thesis narrative-synthesis review → Modules 29–30

That's **19 concept pages + 1 tutorial + 1 hub page = 21 files**. **Built.**

---

## Track 1 — Core Engine (the review pipeline itself)

### Phase 1: Bare Metal Foundation
*Turning a fuzzy research question into a reproducible, auditable search-and-screen machine.*

| # | Module name | What it proves | Directory | Status |
|---|---|---|---|---|
| 1 | Research Question Formalizer | Proves a natural-language research question can be decomposed into structured, machine-checkable fields (PICO/PEO) instead of staying implicit in the reviewer's head | `modules/track1/01_research_question_formalizer/` | **Built** |
| 2 | Boolean Query Builder | Proves a structured question can be mechanically compiled into a reproducible boolean search string with synonym/controlled-vocabulary expansion | `modules/track1/02_boolean_query_builder/` | **Built** |
| 3 | Bibliographic Record Model | Proves heterogeneous citation formats (RIS, BibTeX, API JSON) can be normalized into one canonical `Record` schema | `modules/track1/03_bibliographic_record_model/` | **Built** |
| 4 | Live API Connector | Proves the query builder's output actually retrieves real results from a live academic database (Crossref/arXiv/PubMed E-utilities) | `modules/track1/04_live_api_connector/` | **Built** |
| 5 | Multi-Source Aggregator | Proves results from independently-shaped sources can be merged into one unified corpus without losing provenance | `modules/track1/05_multi_source_aggregator/` | **Built** |
| 6 | Deduplication Engine | Proves duplicate records across sources can be detected automatically via exact (DOI) and fuzzy (title/author) matching | `modules/track1/06_deduplication_engine/` | **Built** |
| 7 | PRISMA Flow Tracker | Proves every record's fate (identified/deduped/screened/excluded-with-reason/included) can be counted and audited at each pipeline stage | `modules/track1/07_prisma_flow_tracker/` | **Built** |
| 8 | Title/Abstract Screening Engine | Proves inclusion/exclusion criteria can be applied systematically and every decision logged with a reason, not made ad hoc | `modules/track1/08_screening_engine/` | **Built** |
| 9 | Full-Text Eligibility Engine | Proves a second screening pass on full text catches false inclusions that title/abstract screening alone lets through | `modules/track1/09_fulltext_eligibility_engine/` | **Built** |
| 10 | Data Extraction Form Engine | Proves unstructured study text can be converted into structured, cross-study-comparable data via a validated extraction schema | `modules/track1/10_data_extraction_engine/` | **Built** |
| 11 | Risk-of-Bias / Quality Appraisal Scorer | Proves study quality can be quantified via a checklist rubric (simplified Cochrane RoB / CASP) instead of asserted by feel | `modules/track1/11_risk_of_bias_scorer/` | **Built** |
| 12 | PRISMA Diagram Generator | Proves the flow tracker's internal state can be rendered into the field-standard PRISMA flow diagram artifact | `modules/track1/12_prisma_diagram_generator/` | **Built** |

### Phase 2: Synthesis & Provenance
*Turning a set of included, extracted, appraised studies into a defensible, reportable answer.*

| # | Module name | What it proves | Directory | Status |
|---|---|---|---|---|
| 13 | Citation Snowballing Engine | Proves the corpus can be expanded beyond the initial search via backward/forward citation traversal | `modules/track1/13_citation_snowballing_engine/` | **Built** |
| 14 | Evidence Table Builder | Proves heterogeneous included studies become directly comparable once assembled into one normalized table | `modules/track1/14_evidence_table_builder/` | **Built** |
| 15 | Thematic Coding Engine | Proves qualitative synthesis (open + axial coding into themes) is a structured, repeatable process, not a vibe | `modules/track1/15_thematic_coding_engine/` | **Built** |
| 16 | Effect Size Calculator | Proves standardized effect sizes (OR, RR, SMD) with confidence intervals can be correctly derived from raw study numbers | `modules/track1/16_effect_size_calculator/` | **Built** |
| 17 | Meta-Analysis Engine | Proves individual study effects can be statistically pooled (fixed/random effects) into one estimate with a heterogeneity measure (I²) | `modules/track1/17_meta_analysis_engine/` | **Built** |
| 18 | Forest Plot Renderer | Proves a pooled meta-analysis result can be communicated visually in the field-standard forest plot format | `modules/track1/18_forest_plot_renderer/` | **Built** |
| 19 | Publication Bias Detector | Proves the pooled result can be checked for selection/reporting bias via funnel plot asymmetry and Egger's test | `modules/track1/19_publication_bias_detector/` | **Built** |
| 20 | Review Report Compiler | Proves every artifact the pipeline produced (PRISMA diagram, evidence table, forest plot, narrative synthesis) converges into one publishable report | `modules/track1/20_review_report_compiler/` | **Built** |

---

## Track 2 — Applied Layer (review methodology variants)

*Each row reuses or adapts specific Track 1 modules — this track proves the "kernel" generalizes rather than only ever running one program.*

| # | Module name | What it proves | Directory | Depends on (Track 1) | Status |
|---|---|---|---|---|---|
| 21 | Scoping Review Mapper | Proves the pipeline can answer "what does the field look like" instead of "what is the effect," by swapping eligibility criteria for a breadth-charting form and dropping formal appraisal | `modules/track2/21_scoping_review_mapper/` | Modules 1, 2, 8, 10 | **Built** |
| 22 | Rapid Review Adapter | Proves the pipeline degrades gracefully under a time-box (single reviewer, restricted sources, simplified appraisal) while still documenting exactly what rigor was traded away | `modules/track2/22_rapid_review_adapter/` | Modules 5, 8, 11, 12 | **Built** |
| 23 | Bibliometric / Citation Network Analyzer | Proves the corpus itself — not just the findings inside it — is analyzable as a network (centrality, co-citation clustering) | `modules/track2/23_bibliometric_network_analyzer/` | Modules 5, 13 | **Built** |
| 24 | Qualitative Evidence Synthesis (Meta-Ethnography) | Proves qualitative studies can be synthesized into new interpretive findings without pooling any numbers, via cross-study "translation" | `modules/track2/24_qualitative_evidence_synthesis/` | Module 15 | **Built** |
| 25 | Umbrella Review Aggregator | Proves the pipeline is recursive — it can treat other systematic reviews as its unit of analysis and synthesize reviews-of-reviews | `modules/track2/25_umbrella_review_aggregator/` | Modules 11, 14 | **Built** |
| 26 | Living Review Updater | Proves the pipeline can run as a maintained, continuously-updated system by incrementally processing only records new since the last run | `modules/track2/26_living_review_updater/` | Modules 5, 6, 7, 20 | **Built** |
| 27 | Related-Work Comparison Matrix Builder | Proves prior work for a systems/security paper (USENIX/OSDI/NSDI/CCS-style venues) is organized as a dimension-by-system comparison matrix — the field's actual convention — instead of a PRISMA-style chronological evidence table, because the goal here is positioning a contribution, not synthesizing an effect | `modules/track2/27_related_work_comparison_matrix/` | Modules 5, 6, 13, 14 | **Built** |
| 28 | Positioning & Gap-Statement Generator | Proves a paper's novelty claim ("no prior work satisfies dimension X") can be mechanically derived from the comparison matrix and grounded back in each cited paper's actual abstract text, rather than asserted without support — matching the standard of scrutiny USENIX-style reviewers apply to related-work claims | `modules/track2/28_positioning_gap_statement_generator/` | Module 27 (Track 2), Module 3 (Track 1) | **Built** |
| 29 | Synthesis Matrix Builder *(Beginner On-Ramp)* | Proves that organizing sources **by theme** (columns) instead of **by source** (rows) is the exact mechanical difference between synthesis and summary — the single most common mistake beginners make in a thesis lit review chapter | `modules/track2/29_synthesis_matrix_builder/` | Module 3 (Track 1) only — deliberately minimal | **Built** |
| 30 | Thesis Gap-to-Research-Question Funnel Builder *(Beginner On-Ramp)* | Proves a thesis's specific research question can be argued into existence by narrowing from broad thematic context, through the thin/contested areas the synthesis matrix surfaces, down to one defensible gap statement — the "funnel" structure thesis committees expect | `modules/track2/30_thesis_gap_funnel_builder/` | Module 29 (Track 2), Module 1 (Track 1) | **Built** |

**Total: 30 modules (20 core engine + 10 applied layer).**

---

## Recommended Stopping Points

| Your goal | Stop after module |
|---|---|
| Understand what a literature review actually *is*, structurally | 3 — Bibliographic Record Model |
| Be able to run one real, reproducible systematic search against live sources | 6 — Deduplication Engine |
| Have a fully auditable, PRISMA-compliant screening pipeline (no synthesis yet) | 12 — PRISMA Diagram Generator |
| Produce a complete systematic review, including quantitative meta-analysis | 20 — Review Report Compiler |
| I'm a complete beginner writing my first thesis literature-review chapter and want the shortest possible path, no systematic-review rigor needed | 30 — Thesis Gap-to-Research-Question Funnel Builder (start here directly — only needs Module 3 as background reading, not the full pipeline) |
| Skip meta-analysis entirely; go straight from search/dedupe to a rigorous, comparison-matrix-driven Related Work section for a systems/security conference paper (USENIX/OSDI/NSDI/CCS-style) — only needs Modules 1–6, 13–14, then 27–28 | 28 — Positioning & Gap-Statement Generator (non-linear path) |
| Understand how the same engine adapts to every review type: scoping, rapid, bibliometric, qualitative, umbrella, living, conference-paper positioning, *and* thesis-chapter writing | 30 — Thesis Gap-to-Research-Question Funnel Builder (full course) |

---

## Tools / Architecture Target

- **Language:** Python 3.11+ for all pipeline code (stdlib + `requests`, `matplotlib`, minimal deps — dependency-light on purpose so every artifact is inspectable).
- **Data sources:** free, no-API-key academic APIs — Crossref, arXiv, PubMed E-utilities, Semantic Scholar's open API — so every module is actually runnable by the learner without credential setup.
- **Persistence:** flat JSON/SQLite per module (no external database service) so state is always inspectable as a file.
- **Diagrams/plots:** PRISMA diagrams and network graphs as generated SVG/HTML; forest/funnel plots via `matplotlib`.
- **Platform:** Windows 11 + PowerShell, cross-platform Python (no OS-specific calls).
- **Tutorials:** static HTML (`tutorial.html` per module), one shared dark-theme design system, Playfair Display headers, monospace code — no build step, no framework.
- **Explicitly out of scope:** ML/NLP-based screening classifiers (rule-based screening only — noted as a real future extension, not built here), reference-manager GUI integrations (Zotero/EndNote plugins), multi-user/collaborative review platforms, manuscript/LaTeX submission templating, paywalled full-text retrieval (full-text modules operate on open-access text or user-supplied text).

---

## Prerequisites Layer (built in Phase 1 of the course structure, before Module 1's tutorial)

The handful of primitives every module assumes, each getting one page in `prerequisites.html`:

1. Research question frameworks (PICO / PEO / SPIDER)
2. Boolean search logic & controlled vocabulary (MeSH-style thesauri)
3. Bibliographic metadata & identifiers (DOI, RIS/BibTeX)
4. Study design taxonomy & evidence hierarchy (RCT, cohort, case-control, qualitative, etc.)
5. Inclusion/exclusion (eligibility) criteria logic
6. Effect sizes & statistical primitives (OR/RR/SMD, confidence intervals)
7. The PRISMA reporting standard (what it requires and why it exists)
8. Positioning-based vs. evidence-synthesis literature review — how a CS systems/security conference paper's "Related Work" section (comparison-by-dimension, novelty/gap claim, reviewer expectations at venues like USENIX Security/OSDI/NSDI/CCS) differs in purpose and structure from a PRISMA-style systematic review
9. The synthesis-vs-summary distinction — why organizing sources by theme instead of by source is what makes a literature review an argument instead of an annotated bibliography (the beginner starting point for Modules 29–30)

---

## Open questions — resolved with defaults (2026-07-27, "go ahead")

Proceeding with sensible defaults rather than blocking on each answer; any
of these can still be redirected at any time:

- **Live APIs:** on, using free no-key sources (Crossref, arXiv, PubMed E-utilities)
- **USENIX worked example (Modules 27–28):** microarchitectural side-channel attacks/defenses (Spectre/Meltdown-class)
- **Thesis worked example (Modules 29–30):** "remote work and employee productivity"
- **Module 0 type list:** keeping the 19 types as proposed

Original open questions, kept for reference:

1. **Scope confirmation:** does 30 modules across 2 tracks match what you want, or should Track 2 be trimmed/expanded (e.g. drop Umbrella Review, or add a "Grey Literature Search" module)?
2. **Live API dependency:** Module 4 onward makes real network calls to public academic APIs during the course. Confirm that's acceptable (vs. a offline/cached-corpus mode as a fallback module).
3. **Module 27/28 source corpus:** for the USENIX-style comparison matrix to feel real, I'd want it built against actual papers — e.g. a small real set of USENIX Security/OSDI/NSDI papers on a topic you pick (via the arXiv/Crossref connector from Module 4, or DBLP). Any topic preference, or should I choose one for the worked example?
4. **Module 29/30 worked example:** same question for the beginner thesis track — a made-up example topic (e.g. "remote work and employee productivity") works fine and keeps it approachable, or do you have a real thesis topic you'd like the worked example to use?
5. **Module 0 type list:** does the 19-type list above match what you mean by "all the types that have ever existed," or should I add/cut any (e.g. add "concept analysis review," "historical review," "methodological review" — all real but more niche — or trim to a shorter core set)?
6. Anything from this list you'd rather I cut to hit a smaller course, per the Recommended Stopping Points table?

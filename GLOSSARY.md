# Glossary

Alphabetical. Append-only — new modules add entries here, existing entries
are never deleted or rewritten, only corrected if genuinely wrong. Each
entry is tagged with where it was first introduced.

---

**A priori protocol** — Eligibility criteria and search strategy written down and fixed *before* screening begins, so decisions can't be unconsciously shaped by results already seen.
*First seen: Prerequisites Layer (Eligibility Criteria Logic)*

**Aggregative synthesis** — Combining study findings by pooling/adding them together, assuming they measure comparable things (e.g. meta-analysis); contrasted with configurative synthesis.
*First seen: Module 0 (The Literature Review Landscape)*

**APIError** — The exception `connector.py` raises when PubMed's E-utilities API returns something other than a usable result (e.g. a malformed query it couldn't parse).
*First seen: Module 4 (Live API Connector)*

**Backward / forward snowballing** — Expanding a corpus via citation traversal: backward follows a paper's reference list to find older, cited work (Crossref); forward follows a citation index to find newer work that cites it (Semantic Scholar). Structurally can't overlap in one hop, since cited work predates and citing work postdates the seed.
*First seen: Module 13 (Citation Snowballing Engine)*

**Bibliographic record** — The normalized bundle of fields (title, authors, year, venue, abstract, identifiers) representing one citation, regardless of which source it came from.
*First seen: Prerequisites Layer (Bibliographic Metadata & Identifiers)*

**Bibliometric review** — A review analyzing the literature itself as structured data (citation counts, co-authorship, co-citation clusters) rather than synthesizing what individual studies found.
*First seen: Module 0*

**BibTeX** — A LaTeX-oriented plain-text citation export format, keyed by a user-chosen citation key (e.g. `@article{smith2023, ...}`).
*First seen: Prerequisites Layer (Bibliographic Metadata & Identifiers)*

**Boolean operator** — `AND` / `OR` / `NOT`, used to combine search terms; `AND` narrows results, `OR` widens them, `NOT` excludes.
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**Breadth map** — A scoping review's actual deliverable: a tally of charted records by category (population type, design, topic, etc.), produced by `summarize_breadth()` — answers "what exists," not "what is the effect."
*First seen: Module 21 (Scoping Review Mapper)*

**Case-control study** — A study design that starts from the outcome (people with a condition) and looks backward for exposure differences vs. matched controls; efficient for rare outcomes, more vulnerable to recall bias.
*First seen: Prerequisites Layer (Study Design Taxonomy & Evidence Hierarchy)*

**CitationGraph** — `bibliometric_analyzer.py`'s shape: a set of (citing, cited) DOI edges, with node identity kept consistent via Module 6's `normalize_doi()`, supporting real degree-centrality and co-citation computation.
*First seen: Module 23 (Bibliometric / Citation Network Analyzer)*

**CMO configuration (Context-Mechanism-Outcome)** — The core analytic unit of a realist review: a mechanism, the context it depends on, and the outcome it produces — used to explain why an intervention works in some settings and not others, instead of just whether it works on average.
*First seen: Module 0*

**CodedExcerpt** — `thematic_coding.py`'s shape: one excerpt plus whichever open codes actually matched it (zero, one, or several) — never forced into exactly one category.
*First seen: Module 15 (Thematic Coding Engine)*

**Cohort study** — A study design that follows a group over time comparing exposed vs. unexposed subjects, without randomization.
*First seen: Prerequisites Layer (Study Design Taxonomy & Evidence Hierarchy)*

**classify_approach() / COMPARISON_SCHEMA** — `comparison_matrix.py`'s dimension-extraction: classifies each real paper's approach type from its own title/abstract text via transparent keyword heuristics, falling back to "unspecified" (not a guess) when no abstract is available.
*First seen: Module 27 (Related-Work Comparison Matrix Builder)*

**Comparison dimension** — One axis (e.g. threat model, performance overhead) along which competing systems are contrasted in a positioning-style related-work comparison matrix.
*First seen: Prerequisites Layer (Positioning vs. Evidence-Synthesis Review)*

**compile_report()** — `report_compiler.py`'s capstone function: imports and calls real functions from fourteen prior modules to assemble one complete, self-contained HTML review report plus its PRISMA/forest/funnel image assets.
*First seen: Module 20 (Review Report Compiler)*

**Confidence interval (CI)** — The range an effect's true value plausibly falls in, given sample size and variability; wider = less certain, narrower = more certain.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**Configurative synthesis** — Combining study findings by arranging and interpreting diverse results into a new argument, rather than pooling them into one number; contrasted with aggregative synthesis.
*First seen: Module 0*

**Confounding** — A distortion in a study's result caused by some other, unaccounted-for difference between compared groups — the main threat evidence-hierarchy ranking tries to account for.
*First seen: Prerequisites Layer (Study Design Taxonomy & Evidence Hierarchy)*

**Controlled vocabulary** — A database's own fixed, hand-curated thesaurus (e.g. MeSH) that every record is manually tagged with, independent of the words the author actually used.
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**CorpusStats** — The per-`source_format` record count returned by `merge_sources()`, computed from the merged corpus itself rather than assumed — proof provenance survives merging.
*First seen: Module 5 (Multi-Source Aggregator)*

**Critical review** — A review that evaluates and critiques existing literature to reconceptualize a field, often producing a new conceptual model, rather than describing or pooling existing findings.
*First seen: Module 0*

**Cross-sectional study** — A single-point-in-time study design; can show association but not which came first, exposure or outcome.
*First seen: Prerequisites Layer (Study Design Taxonomy & Evidence Hierarchy)*

**DedupeResult / DuplicateMatch** — `dedup_engine.py`'s output shape: the surviving unique records, plus one `DuplicateMatch` per removal naming which record was kept, which was removed, why (`"exact_doi"` or `"fuzzy_title"`), and the exact similarity score — every removal is logged, never silent.
*First seen: Module 6 (Deduplication Engine)*

**DOI (Digital Object Identifier)** — A permanent, globally unique, resolvable identifier assigned to a publication at registration time; the closest thing academic publishing has to a stable primary key.
*First seen: Prerequisites Layer (Bibliographic Metadata & Identifiers)*

**Effect size** — A standardized numeric measure of a finding's magnitude (e.g. Odds Ratio, Mean Difference) that lets results from differently-designed studies be compared or pooled.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**EffectSizeResult** — `effect_size.py`'s shape: an effect-size estimate plus confidence interval that knows its own no-effect reference value (1.0 for OR/RR, 0.0 for SMD) and can check `crosses_no_effect()` against it directly.
*First seen: Module 16 (Effect Size Calculator)*

**Egger's test** — A linear regression of standardized effect (`y/se`) on precision (`1/se`) whose intercept tests for funnel-plot asymmetry; requires variation in SE across studies and at least 3 studies to compute, and per Cochrane Handbook guidance shouldn't be over-interpreted with fewer than ~10.
*First seen: Module 19 (Publication Bias Detector)*

**Eligibility criteria** — The combined inclusion/exclusion rules a record must satisfy to remain in a review, decided a priori.
*First seen: Prerequisites Layer (Eligibility Criteria Logic)*

**EligibilityRule / EligibilityResult / FullTextRecord** — `fulltext_engine.py`'s shapes: a `Record` paired with its full text (`FullTextRecord`), screened by ordered rules that inspect full text rather than just title/abstract, mirroring Module 8's first-failure-wins design.
*First seen: Module 9 (Full-Text Eligibility Engine)*

**EmptySlotTermsError** — The exception `query_builder.py` raises when a `SlotTerms` was supplied for a search slot but contains no free-text or controlled-vocabulary terms — an OR-group with nothing inside isn't a valid boolean clause.
*First seen: Module 2 (Boolean Query Builder)*

**E-utilities (esearch / esummary)** — NCBI's public PubMed API. `esearch` runs a query and returns matching PMIDs, a total count, and PubMed's own parsed interpretation of the query; `esummary` fetches compact metadata (no abstract) for a batch of PMIDs.
*First seen: Module 4 (Live API Connector)*

**Evidence hierarchy** — A ranking of study designs by how exposed their conclusions are to bias/confounding (RCT > cohort > case-control > cross-sectional > case series), used as a starting point rather than a final verdict on quality.
*First seen: Prerequisites Layer (Study Design Taxonomy & Evidence Hierarchy)*

**Evidence-synthesis review** — A review whose goal is to objectively pool/summarize what all available evidence shows about a question (e.g. a PRISMA-style systematic review), as distinct from a positioning review.
*First seen: Prerequisites Layer (Positioning vs. Evidence-Synthesis Review)*

**Exclusion criteria** — Properties that disqualify a record from a review even if it satisfies every inclusion criterion.
*First seen: Prerequisites Layer (Eligibility Criteria Logic)*

**ExtractionSchema / ExtractionField / ExtractedRecord** — `extraction_engine.py`'s shapes: a list of typed, validated fields (`ExtractionSchema`) that hand-entered study data must satisfy before becoming an `ExtractedRecord` — guarantees shape, not correctness (see `ExtractionValidationError`).
*First seen: Module 10 (Data Extraction Form Engine)*

**FlowConservationError** — The exception `flow_tracker.py` raises when a PRISMA stage's logged inputs don't arithmetically equal its logged outputs (included + excluded) — proof, not assumption, that no record was silently lost.
*First seen: Module 7 (PRISMA Flow Tracker)*

**Free-text term** — A search keyword matched against whatever words appear literally in a record, as opposed to a controlled-vocabulary tag.
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**Framework suggestion heuristic** — A deterministic, keyword-based (not machine-learned) function that guesses which question framework (PICO/PEO/SPIDER) fits a free-text question, always reporting *why*, so a human can confirm or override it rather than trust it blindly.
*First seen: Module 1 (Research Question Formalizer)*

**FunnelStage / build_funnel() / identify_thin_themes()** — `gap_funnel.py`'s shapes: three narrowing stages (broad context, narrowing, gap) derived from Module 29's real `coverage()` count, ending in a gap statement that names its own evidentiary basis rather than asserting "more research is needed."
*First seen: Module 30 (Thesis Gap-to-Research-Question Funnel Builder)*

**Gap statement** — A claim, grounded in a comparison matrix, that no existing prior work satisfies some specific combination of dimensions — the core novelty argument of a positioning review.
*First seen: Prerequisites Layer (Positioning vs. Evidence-Synthesis Review)*

**GapCriteria / find_satisfying_papers() / find_near_misses()** — `gap_statement.py`'s mechanism: a gap exists only if NO paper satisfies every required dimension simultaneously (full conjunction, not majority); near-misses are reported with exactly which dimension each lacks, re-verified against real text via `verify_claim_grounded()`.
*First seen: Module 28 (Positioning & Gap-Statement Generator)*

**Heterogeneity (Cochran's Q, I², τ²)** — Statistics quantifying how much pooled studies disagree beyond what sampling noise alone predicts. Q and its degrees of freedom feed I² (percentage of variation due to real heterogeneity, not chance) and τ² (estimated between-study variance, used to widen a random-effects pooled estimate).
*First seen: Module 17 (Meta-Analysis Engine)*

**IncludedReview / compute_overlap()** — `umbrella_review.py`'s shapes: an included systematic review carries its own primary-study DOI set; `compute_overlap()` and `total_unique_primary_studies()` catch the real hazard of double-counted primary studies shared across overlapping included reviews.
*First seen: Module 25 (Umbrella Review Aggregator)*

**Inclusion criteria** — Properties a record must have to proceed past screening.
*First seen: Prerequisites Layer (Eligibility Criteria Logic)*

**InvalidAnswerError** — The exception `rob_scorer.py` raises when a checklist item is unanswered or answered with something other than `yes`/`unclear`/`no`.
*First seen: Module 11 (Risk-of-Bias / Quality Appraisal Scorer)*

**Integrative review** — A review that deliberately combines findings from studies of different methodologies (experimental, qualitative, theoretical) into one synthesis.
*First seen: Module 0*

**Living systematic review** — A systematic review maintained as a continuously updated, versioned artifact via periodic re-search, rather than a one-time snapshot.
*First seen: Module 0*

**LivingReviewState / run_update()** — `living_review.py`'s shapes: JSON-persisted state (version, seen DOIs, cumulative included count) diffed against each fresh live search so only genuinely new records are dedup'd and screened each update cycle.
*First seen: Module 26 (Living Review Updater)*

**Mapping review / systematic map** — A review that systematically codes existing studies by characteristics (design, population, topic) to visualize where evidence clusters and gaps exist.
*First seen: Module 0*

**Mean Difference (MD)** — An effect size for continuous outcomes measured on the same scale across studies; "no effect" = 0.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**MeSH (Medical Subject Headings)** — PubMed's controlled vocabulary; the standard example of a database-specific thesaurus.
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**Meta-analysis** — A statistical technique that pools effect sizes from multiple studies into one combined estimate, usually built on a systematic review's included studies.
*First seen: Module 0*

**MetaAnalysisResult / PoolableEffect** — `meta_analysis.py`'s shapes: a `PoolableEffect` reconstructs a study's pooling-scale estimate and SE from its reported CI; `MetaAnalysisResult` holds a fixed- or random-effects pooled estimate plus Q/I²/τ², with `display_estimate()` converting back to natural scale.
*First seen: Module 17 (Meta-Analysis Engine)*

**Meta-ethnography** — A specific meta-synthesis technique that "translates" each qualitative study's concepts into the others' terms to find reciprocal, refutational, or line-of-argument relationships between them.
*First seen: Module 0*

**Metadata field** — Any single named attribute of a bibliographic record (title, year, DOI, etc.).
*First seen: Prerequisites Layer (Bibliographic Metadata & Identifiers)*

**Meta-synthesis** — Systematic synthesis of qualitative study findings into new interpretive conclusions, without pooling numbers; also called qualitative systematic review.
*First seen: Module 0*

**MissingPCCSlotsError** — The exception `scoping_mapper.py` raises when a `PCCQuestion` is missing a required slot — the PCC-framework parallel to Module 1's `MissingSlotsError`, built separately because Python enums can't be extended to add a new framework after the fact.
*First seen: Module 21 (Scoping Review Mapper)*

**MissingSlotsError** — The exception `formalizer.py` raises when a `ResearchQuestion` is validated before every slot its framework requires has been filled; names the exact missing slots rather than failing generically.
*First seen: Module 1 (Research Question Formalizer)*

**MissingTermsError** — The exception `query_builder.py` raises when `build_query()` needs search terms for a slot that wasn't provided in the `terms` dict at all.
*First seen: Module 2 (Boolean Query Builder)*

**Mixed studies / mixed methods review** — A review that systematically includes and synthesizes quantitative, qualitative, and mixed-methods primary studies side by side.
*First seen: Module 0*

**MixedScaleError** — The exception `meta_analysis.py` raises when effects on different pooling scales (log for OR/RR, linear for SMD) are pooled together, which would silently average incomparable quantities.
*First seen: Module 17 (Meta-Analysis Engine)*

**Narrative review** — An author-guided, non-systematic account of a topic organized to build understanding or argument, without a comprehensive reproducible search; also called a traditional review.
*First seen: Module 0*

**Novelty claim** — The specific assertion that a paper's contribution does something no prior work does, typically derived from a related-work comparison matrix.
*First seen: Prerequisites Layer (Positioning vs. Evidence-Synthesis Review)*

**Odds Ratio (OR)** — An effect size for binary outcomes, typically from case-control studies; "no effect" = 1.0.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**Open coding / axial coding** — The two-stage grounded-theory coding process: open coding tags excerpts with bottom-up descriptive codes first; axial coding then groups those already-assigned codes into higher-level themes. An excerpt can legitimately carry multiple codes and appear under multiple themes.
*First seen: Module 15 (Thematic Coding Engine)*

**OR-group** — One parenthesized clause of synonyms joined by `OR`, representing all the ways one concept (a PICO/PEO/SPIDER slot) might be phrased; a full search string is multiple OR-groups joined by `AND`.
*First seen: Module 2 (Boolean Query Builder)*

**Overview** — A broad, audience-facing summary of a body of evidence (often existing reviews) aimed at non-specialists, with no fixed methodology of its own.
*First seen: Module 0*

**ParseError** — The exception `record_model.py` raises when a source-format input has no title, the one field nothing downstream can meaningfully work without.
*First seen: Module 3 (Bibliographic Record Model)*

**PCC (Population, Concept, Context)** — The real JBI (Joanna Briggs Institute) question framework recommended for scoping reviews, used instead of PICO because PICO's Intervention/Comparison slots presuppose an effect is being measured.
*First seen: Module 21 (Scoping Review Mapper)*

**PEO (Population, Exposure, Outcome)** — A research-question framework for observational/etiology questions where no intervention was assigned.
*First seen: Prerequisites Layer (Research Question Frameworks)*

**PICO (Population, Intervention, Comparison, Outcome)** — A research-question framework for questions about whether doing X changes Y.
*First seen: Prerequisites Layer (Research Question Frameworks)*

**Positioning review** — A review whose goal is to justify a specific new contribution's novelty by comparing it against prior work along chosen dimensions (e.g. a USENIX/OSDI/NSDI-style Related Work section), as distinct from an evidence-synthesis review.
*First seen: Prerequisites Layer (Positioning vs. Evidence-Synthesis Review)*

**PRISMA (Preferred Reporting Items for Systematic reviews and Meta-Analyses)** — The reporting standard requiring a checklist and flow diagram documenting exactly how a systematic review's search, screening, and inclusion decisions were made.
*First seen: Prerequisites Layer (The PRISMA Reporting Standard)*

**PRISMA flow diagram** — The standard visual accounting of record counts at each review stage: identification, deduplication, screening, eligibility, included.
*First seen: Prerequisites Layer (The PRISMA Reporting Standard)*

**render_prisma_svg()** — `diagram_generator.py`'s function that reads a `PrismaFlowTracker`'s real logged state and produces real, parseable SVG markup, rendering progressively (stopping cleanly) at however far the pipeline has actually gotten.
*First seen: Module 12 (PRISMA Diagram Generator)*

**Rapid review** — A systematic review's methodology compressed under a time constraint, with the specific simplifications explicitly documented.
*First seen: Module 0*

**RapidReviewLog / Simplification** — `rapid_review.py`'s disclosure mechanism: every methodology shortcut is logged as a `Simplification` (stage, standard practice, what was done instead, and why) rather than applied silently — the discipline that separates a legitimate rapid review from a systematic review done sloppily.
*First seen: Module 22 (Rapid Review Adapter)*

**Realist review** — A review asking what works, for whom, under what circumstances, and through what mechanism, built around context-mechanism-outcome (CMO) configurations rather than a simple effect estimate.
*First seen: Module 0*

**Record** — The canonical seven-field shape (`title, authors, year, venue, abstract, doi, source_format`) every source format gets normalized into, so records from different origins become directly comparable.
*First seen: Module 3 (Bibliographic Record Model)*

**render_forest_plot()** — `forest_plot.py`'s function rendering a real forest plot (matplotlib): one row per study with a weight-sized square marker and CI line, a diamond for the pooled estimate, a no-effect reference line, and a log-scaled x-axis for ratio measures.
*First seen: Module 18 (Forest Plot Renderer)*

**ResearchQuestion** — The structured, validated object `formalizer.py` produces: raw question text plus a chosen framework plus its filled slots, ready to hand to Module 2's query builder.
*First seen: Module 1 (Research Question Formalizer)*

**Risk Ratio / Relative Risk (RR)** — An effect size for binary outcomes from cohort studies/RCTs with a known baseline risk; "no effect" = 1.0.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**RIS format** — A plain-text, tag-based citation export format (e.g. `TY -`, `AU -`, `TI -`) used by EndNote, Zotero, and most databases.
*First seen: Prerequisites Layer (Bibliographic Metadata & Identifiers)*

**SchemaMismatchError** — The exception `evidence_table.py` raises when a row's extracted data doesn't satisfy the table's target schema — catches rows that bypassed Module 10's own validation before they join a supposedly-comparable table.
*First seen: Module 14 (Evidence Table Builder)*

**Scoping review** — A review that maps the breadth of a field — what exists, what's studied, where the gaps are — without assessing study quality or pooling an effect.
*First seen: Module 0*

**Screening decision** — The logged outcome (include/exclude + reason) of applying eligibility criteria to one record.
*First seen: Prerequisites Layer (Eligibility Criteria Logic)*

**ScreeningRule / ScreeningResult** — `screening_engine.py`'s shapes: an ordered `ScreeningRule` list (name + predicate) applied to each record, with the first failing rule's name logged as the exclusion reason; `ScreeningResult.excluded_by_reason()` matches Module 7's `log_screening()` input shape exactly.
*First seen: Module 8 (Title/Abstract Screening Engine)*

**Search slot** — A PICO/PEO/SPIDER slot that participates in the actual search string, as opposed to one (like Comparison or Outcome, by default) that's reserved for eligibility screening instead.
*First seen: Module 2 (Boolean Query Builder)*

**Search string** — The fully assembled boolean query, built from OR-groups of synonyms per PICO/PEO/SPIDER slot joined by AND, submitted to a database or API.
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**SlotTerms** — The dataclass holding one slot's free-text synonyms and optional controlled-vocabulary terms, supplied separately from the `ResearchQuestion` itself so a search can use many synonyms per concept.
*First seen: Module 2 (Boolean Query Builder)*

**SMD (Standardized Mean Difference, e.g. Cohen's d)** — An effect size for continuous outcomes measured on different scales/instruments across studies, expressed in units of standard deviation; "no effect" = 0.
*First seen: Prerequisites Layer (Effect Sizes & Statistical Primitives)*

**SPIDER (Sample, Phenomenon of Interest, Design, Evaluation, Research type)** — A research-question framework for qualitative questions about experience or meaning, where PICO's Intervention/Comparison slots don't apply.
*First seen: Prerequisites Layer (Research Question Frameworks)*

**State-of-the-art review** — A review surveying the current, most recent understanding of a fast-moving topic, prioritizing recency over historical completeness.
*First seen: Module 0*

**Summary (vs. synthesis)** — Literature-review prose organized by source (one paragraph per paper) rather than by idea; the default failure mode of a first-draft literature review.
*First seen: Prerequisites Layer (Synthesis vs. Summary)*

**Synthesis** — Literature-review prose organized by theme, where each source is cited only where it supports a specific claim, and a single source can appear under multiple themes.
*First seen: Prerequisites Layer (Synthesis vs. Summary)*

**Synthesis matrix** — A grid (sources × themes) filled in row-by-row but read back out column-by-column, used as a mechanical tool to force synthesis instead of summary.
*First seen: Prerequisites Layer (Synthesis vs. Summary)*

**SynthesisMatrix (class)** — `synthesis_matrix.py`'s working implementation of the synthesis-matrix concept: `render_by_source()` and `render_by_theme()` read the identical `cells` dict in different loop orders, mechanically producing a summary in one case and synthesis in the other from the same underlying notes.
*First seen: Module 29 (Synthesis Matrix Builder)*

**Systematic review** — A review answering a focused question through exhaustive, protocol-driven search, pre-registered eligibility criteria, quality appraisal, and PRISMA-compliant reporting.
*First seen: Module 0*

**Systematic search and review** — A review combining a systematic, reproducible search strategy with a narrative (non-systematic) synthesis of the results.
*First seen: Module 0*

**Systematized review** — A review applying elements of systematic-review methodology without meeting the full standard, typically due to a single-reviewer resource constraint (e.g. a student thesis).
*First seen: Module 0*

**Thematic organization** — Structuring a review's content around ideas/themes rather than around individual sources.
*First seen: Prerequisites Layer (Synthesis vs. Summary)*

**Translation (reciprocal / refutational)** — Meta-ethnography's core step: comparing two studies' excerpts sharing an open code and classifying them as reciprocal (agree) or refutational (conflict) — implemented here via a negation-marker heuristic with a real, documented failure mode (can't distinguish negation describing a phenomenon from negation of a claim).
*First seen: Module 24 (Qualitative Evidence Synthesis)*

**Truncation (wildcard)** — A search technique (e.g. `employ*`) that matches all word forms sharing a stem (employee, employment, employer, employed).
*First seen: Prerequisites Layer (Boolean Search & Controlled Vocabulary)*

**Umbrella review** — A review treating other systematic reviews (rather than primary studies) as its unit of analysis.
*First seen: Module 0*

**Vocabulary tag translation** — Converting an internal, illustrative controlled-vocabulary tag (e.g. Module 2's `MeSH:"X"`) into the exact field-tag syntax a specific live API actually recognizes (e.g. PubMed's `"X"[mesh]`) before submitting a query — necessary because sending the internal convention literally produces a wrong, silently-misparsed query rather than an error.
*First seen: Module 4 (Live API Connector)*

**ZeroCellError** — The exception `effect_size.py` raises when a 2x2 table has a zero cell, which breaks the standard log-scale standard-error formula; resolved via `continuity_correction=True` (the standard +0.5-per-cell fix), not a silent default.
*First seen: Module 16 (Effect Size Calculator)*

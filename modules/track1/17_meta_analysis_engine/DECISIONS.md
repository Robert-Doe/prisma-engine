# Module 17 — Decisions: Meta-Analysis Engine

## Line-by-line / unit-by-unit

### Pooling formulas (inverse-variance fixed-effect, DerSimonian-Laird random-effects, Cochran's Q, I²)
**(b) Forced by external contract.** These are the standard, published meta-analysis formulas (Cochrane Handbook Chapter 10; Borenstein, Hedges, Higgins & Rothstein, *Introduction to Meta-Analysis*). `Q = Σwᵢ(yᵢ − ŷ)²`, `I² = max(0, (Q−df)/Q × 100%)`, and DerSimonian-Laird's `τ² = max(0, (Q−df)/C)` with `C = Σwᵢ − Σwᵢ²/Σwᵢ` are the actual textbook definitions, not approximations invented for this course.

### `from_effect_size_result()` reconstructs the pooling-scale SE from a reported confidence interval, rather than requiring raw study data
**(c) Convention — and a real, common technique.** Real meta-analyses frequently only have a study's reported point estimate and CI available (from a published paper), not its underlying raw 2×2 table or group means. Back-calculating `SE = (ln(CI_upper) − ln(CI_lower)) / (2 × 1.96)` from a reported CI is the standard real-world technique for exactly this situation — this module demonstrates it directly rather than assuming raw data is always available.

### `MixedScaleError` is raised, not silently averaged, when log-scale and linear-scale effects are pooled together
**(c) Convention.** Averaging `ln(OR) = 0.8` with `SMD = 0.3` would produce a number with no coherent meaning — the two live on fundamentally different scales measuring fundamentally different things. The self-checks confirm this is caught directly: an SMD result mixed into a list of OR-based `PoolableEffect`s raises immediately, before any arithmetic happens.

### `random_effects_meta_analysis()` calls `fixed_effect_meta_analysis()` internally to get `Q` and `df`, rather than recomputing them
**(c) Convention.** The DerSimonian-Laird `τ²` calculation needs `Q` computed from fixed-effect weights specifically — that's part of the method's actual definition, not an implementation shortcut. Reusing the fixed-effect function's own `Q`/`df` output means there's exactly one place in this module that computes heterogeneity statistics, not two that could silently drift apart.

### `MetaAnalysisResult.display_estimate()` exponentiates back to the natural scale, mirroring Module 16's own log-scale-then-exponentiate pattern
**(c) Convention.** Pooling has to happen on the log scale for ratio measures (same reasoning as Module 16), but nobody wants to read a meta-analysis's answer as `ln(OR) = 0.65` — converting back to a real odds ratio for display is the same "work in log space, present in natural space" pattern Module 16 already established, applied one level up.

### The demo deliberately includes one study whose effect direction disagrees with the others (Study E: OR = 0.351, favoring control, against four studies favoring treatment)
**(c) Convention — chosen for real, honest heterogeneity, not a tidy example.** A demo where every study agrees would produce `I² ≈ 0%` and make fixed- and random-effects models look interchangeable, hiding the actual reason random-effects modeling exists. Including real disagreement between studies produces genuinely high heterogeneity (`I² = 84.8%`, confirmed by running the code, not chosen in advance) and a real, substantively important divergence between the two models' conclusions — see What We Proved below.

## Decisions We Made

| Decision | Category |
|---|---|
| Pooling/heterogeneity formulas match published references exactly | (b) External contract (Cochrane Handbook / Borenstein et al.) |
| SE reconstructed from a reported CI, not assumed to need raw data | (c) Convention (real-world technique) |
| Mixed-scale pooling raises `MixedScaleError` | (c) Convention |
| Random-effects reuses fixed-effect's `Q`/`df` internally | (c) Convention (single source of truth) |
| `display_estimate()` exponentiates back for log-scale measures | (c) Convention, mirroring Module 16 |
| Demo includes a genuinely disagreeing study | (c) Convention (honest heterogeneity over a tidy example) |

## What We Proved

Running [`meta_analysis.py`](meta_analysis.py) pooled five real,
independently-computed odds ratios (via Module 16's actual `odds_ratio()`
function) and produced a genuinely consequential result:

1. **Fixed- and random-effects models reached different practical conclusions from the same five studies.** The fixed-effect model's 95% CI was `[1.297, 2.851]` — entirely above 1, a statistically significant pooled effect. The random-effects model's CI was `[0.675, 5.154]` — crossing 1, not significant. This is not a rounding difference; it's the real, well-documented consequence of `I² = 84.8%` (substantial heterogeneity): the random-effects model correctly widens its uncertainty to account for genuine disagreement between studies, while the fixed-effect model — which assumes all five studies estimate the exact same true effect — does not.
2. **A perfectly homogeneous case reproduced a known-correct answer exactly.** Two identical studies pooled together returned the same odds ratio as either study alone, with `I² = 0.0` and `Q ≈ 0` — confirming the pooling math is correct in the trivial case before trusting it in the complex one.
3. **An attempt to pool incompatible scales was caught before producing a meaningless number**, rather than silently averaging a log-odds-ratio with a standardized mean difference.

# Module 16 — Decisions: Effect Size Calculator

## Line-by-line / unit-by-unit

### The formulas themselves (OR, RR, SMD, and their standard errors)
**(b) Forced by external contract.** These are the actual published statistical formulas (Cochrane Handbook Chapter 10; Altman, *Practical Statistics for Medical Research*, 1991) — `OR = ad/bc`, `SE[ln(OR)] = sqrt(1/a+1/b+1/c+1/d)`, `SE[ln(RR)] = sqrt(1/a - 1/n1 + 1/c - 1/n2)`, Cohen's `d` with pooled SD and its large-sample SE approximation. Nothing here was invented for this course; changing any of them would mean computing a different, non-standard statistic while still calling it by a name reviewers would recognize and trust.

### `Z_95 = 1.96` is a fixed constant, not computed from a distribution function
**(c) Convention.** 1.96 is the standard normal distribution's 97.5th percentile, the conventional critical value for a 95% confidence interval — precise enough for four decimal places and avoids pulling in `scipy.stats` as a dependency just to compute a widely-known fixed constant. A module supporting arbitrary confidence levels (90%, 99%) would need a proper inverse-normal function instead; this module's scope is the standard 95% case.

### Confidence intervals for OR and RR are computed on the log scale, then exponentiated back
**(b) Forced by external contract — mathematical necessity, not style.** OR and RR are ratios, bounded below by 0 and asymmetric around 1 — a symmetric interval computed directly on the ratio scale can (and often does) produce a nonsensical negative lower bound. The standard approach works on `ln(OR)`, where the sampling distribution is much closer to normal and symmetric, then converts the interval's endpoints back with `exp()`. This is why `crosses_no_effect()` compares against `1.0` for OR/RR but `0.0` for SMD — the two families live on genuinely different scales.

### A zero cell raises `ZeroCellError` by default; `continuity_correction=True` applies the standard +0.5-per-cell fix instead of a silent default
**(c) Convention.** `1/0` in the standard error formula is a real, common failure mode with small or rare-event studies — not an edge case worth ignoring. Raising by default forces a caller to consciously decide how to handle it, rather than silently returning `inf` or crashing with a bare `ZeroDivisionError` that gives no indication of what actually went wrong or how real practice handles it. The correction itself (adding 0.5 to every cell of a 2x2 table, or to the two zero-event counts for RR) is the standard fix recommended in the Cochrane Handbook, not this course's own invention.

### `EffectSizeResult.crosses_no_effect()` is a method on the result, not a separate free function
**(c) Convention.** Every `EffectSizeResult` already carries its own `no_effect_value` (1.0 or 0.0, decided correctly at construction time by whichever function built it) — putting the check as a method means a caller never has to remember which no-effect value applies to which measure; the result already knows.

## Decisions We Made

| Decision | Category |
|---|---|
| OR/RR/SMD formulas match published statistical references exactly | (b) External contract (Cochrane Handbook / Altman 1991) |
| `Z_95 = 1.96` fixed constant, no `scipy` dependency | (c) Convention |
| OR/RR confidence intervals computed on the log scale | (b) External contract (mathematical necessity) |
| Zero cells raise by default; continuity correction is opt-in | (c) Convention |
| `crosses_no_effect()` as a method carrying its own reference value | (c) Convention |

## What We Proved

Running [`effect_size.py`](effect_size.py) verified real statistical
formulas against hand-computable known cases, not just plausible-looking
output:

1. **A hand-computable odds ratio matched exactly.** `a=10, b=40, c=5, d=45` gives `OR = (10×45)/(40×5) = 2.25` by hand — the function returned exactly that, confirmed by assertion, not eyeballed.
2. **A perfectly balanced table produced exactly no effect.** A symmetric 20/20/20/20 table returned `OR = 1.0` exactly, and its own confidence interval correctly contained that no-effect value — proof the CI logic and the no-effect convention agree with each other, not just individually plausible.
3. **The zero-cell failure mode is real and was caught, then correctly handled.** `odds_ratio(a=10, b=0, c=5, d=10)` raises `ZeroCellError` by default (a genuine division-by-zero the raw formula can't survive), and the same inputs with `continuity_correction=True` produced a finite, sensible result — a large odds ratio with a wide confidence interval, correctly reflecting how little certainty a near-zero cell actually supports.

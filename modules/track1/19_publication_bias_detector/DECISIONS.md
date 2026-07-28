# Module 19 — Decisions: Publication Bias Detector

## Line-by-line / unit-by-unit

### Egger's test regresses `y/se` on `1/se`, not the raw effect on SE directly
**(b) Forced by external contract.** This is Egger's actual published regression specification (Egger et al., 1997, *BMJ*): the standardized effect (`y/se`) as the dependent variable, precision (`1/se`) as the independent variable. The intercept of *this specific* regression is what tests for funnel-plot asymmetry — regressing the raw, unstandardized effect against SE directly is a different (and not the validated) calculation.

### Egger's regression is undefined when every study shares the same SE — discovered empirically, not assumed
**(a) Forced by mathematics, discovered the hard way.** The first version of this module's self-checks used four studies with identical `se=0.10`, and `eggers_test()` raised a real `ZeroDivisionError` — `1/se` was identical for every study, so the regression's `x` values had zero variance (`ss_xx = 0`), making the slope mathematically undefined. This isn't a bug to patch around; a regression genuinely cannot be fit against a predictor that doesn't vary. The self-checks were fixed to use varying SEs, which is also how real included studies actually look (different studies virtually never share the exact same standard error).

### A small hardcoded t-critical-value lookup table, not a full t-distribution implementation
**(c) Convention, driven by (b) the course's architecture target.** Computing exact t-distribution p-values requires either `scipy.stats` or a non-trivial numerical implementation of the incomplete beta function — real complexity for a course committed to minimal dependencies. A lookup table of standard two-tailed 95% critical values for small df (where meta-analyses with few studies actually live), falling back to the normal approximation (1.96) for df > 20, is accurate enough for this module's purpose: a significant/not-significant flag, not a precise p-value.

### `InsufficientStudiesError` requires at least 3 studies (not 2)
**(c) Convention, following directly from the regression's mathematics.** Egger's regression fits a line with an intercept and a slope — two parameters — from `n` data points, leaving `n - 2` degrees of freedom. With only 2 studies, `df = 0`, and there's no residual variance left to estimate a standard error for the intercept from. Three is the actual minimum for the calculation to produce any meaningful number at all, not an arbitrary safety margin.

### The funnel plot's y-axis is inverted (0 at the top, increasing downward)
**(b) Forced by external contract.** This is the field-standard funnel-plot convention: precision decreases as you move down the plot, so the most precise (smallest SE) studies appear at the top, near the plot's apex, and less precise studies scatter more widely near the bottom — visually mimicking a funnel shape when there's no bias, which is where the plot's name comes from.

### The demo explicitly states, in its own printed output, that 5 studies is too few to draw a real publication-bias conclusion
**(b) Forced by external contract — and an honesty requirement this course holds itself to.** The Cochrane Handbook explicitly recommends against interpreting funnel-plot asymmetry tests with fewer than about 10 studies, because statistical power to detect real asymmetry is too low below that. Running the demo on the same 5 studies used throughout Modules 16-18 (for continuity) without stating this caveat would present a real methodological result in a misleading way — exactly what this course's quality bar prohibits.

## Decisions We Made

| Decision | Category |
|---|---|
| Regression specification matches Egger's actual published test | (b) External contract (Egger et al., 1997) |
| Identical-SE studies make the regression undefined | (a) Forced by mathematics (discovered via a real crash) |
| Small t-critical lookup table instead of full t-distribution | (c) Convention, driven by (b) architecture target |
| Minimum 3 studies required (df ≥ 1) | (c) Convention, following the regression's degrees of freedom |
| Inverted y-axis (precision increases upward) | (b) External contract (funnel-plot convention) |
| Demo states the "fewer than 10 studies" caveat explicitly | (b) External contract (Cochrane Handbook), honesty requirement |

## What We Proved

Running [`publication_bias.py`](publication_bias.py) computed a real
Egger's regression and rendered a real funnel plot from Module 17's actual
five studies, and:

1. **The regression's real mathematical requirement was discovered, not assumed.** Development hit an actual `ZeroDivisionError` when test data had no variance in precision — concrete proof the implementation is really doing linear regression, with a real failure mode, not producing plausible-looking numbers from a shortcut.
2. **A real funnel plot was rendered and visually shows the same asymmetry the numeric test measured.** Studies A, B, and C cluster to the right of the pooled estimate; D and E sit to the left — visible asymmetry in the actual image, consistent with (though not proof of) the negative Egger's intercept computed alongside it.
3. **The result was reported honestly alongside its own limitation.** `significant_at_05 = False` on 5 studies is presented with an explicit statement that this test lacks the power to be conclusive at this sample size — the module demonstrates the mechanism without overstating what its own demo's output can actually support.

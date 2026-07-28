"""
Module 17 — Meta-Analysis Engine

Pools several studies' effect sizes (Module 16) into one combined estimate,
two ways: fixed-effect (inverse-variance weighting) and random-effects
(DerSimonian-Laird), plus Cochran's Q and I² heterogeneity statistics. Real
formulas from the Cochrane Handbook / Borenstein et al., "Introduction to
Meta-Analysis" — not invented for this course.

Pooling always happens on the LOG scale for ratio measures (OR/RR) and the
raw scale for difference measures (SMD) — see Module 16's tutorial for why
ratios need the log scale at all.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "16_effect_size_calculator"))
from effect_size import EffectSizeResult, Z_95, odds_ratio  # noqa: E402


class MixedScaleError(ValueError):
    """Raised when effects on different scales (log vs. linear) are pooled
    together — that would silently average incomparable quantities."""


@dataclass
class PoolableEffect:
    study_label: str
    scale: str  # "log" (OR/RR) or "linear" (SMD)
    y: float    # effect estimate on the pooling scale
    se: float   # standard error on that same scale


def from_effect_size_result(label: str, result: EffectSizeResult) -> PoolableEffect:
    """Reconstructs the pooling-scale estimate and SE from an
    EffectSizeResult's reported CI — the same technique real meta-analyses
    use when only a study's point estimate and CI are available, not its
    raw underlying data."""
    if result.measure in ("OR", "RR"):
        y = math.log(result.estimate)
        se = (math.log(result.ci_upper) - math.log(result.ci_lower)) / (2 * Z_95)
        return PoolableEffect(label, "log", y, se)
    se = (result.ci_upper - result.ci_lower) / (2 * Z_95)
    return PoolableEffect(label, "linear", result.estimate, se)


@dataclass
class MetaAnalysisResult:
    model: str  # "fixed" | "random"
    scale: str
    pooled_y: float
    pooled_se: float
    ci_lower_y: float
    ci_upper_y: float
    Q: float
    df: int
    I2: float
    tau2: float | None

    def display_estimate(self) -> tuple[float, float, float]:
        """Converts the pooled result back to its natural display scale
        (exponentiated for log-scale measures)."""
        if self.scale == "log":
            return math.exp(self.pooled_y), math.exp(self.ci_lower_y), math.exp(self.ci_upper_y)
        return self.pooled_y, self.ci_lower_y, self.ci_upper_y


def _check_same_scale(effects: list[PoolableEffect]) -> str:
    scales = {e.scale for e in effects}
    if len(scales) > 1:
        raise MixedScaleError(f"cannot pool effects on different scales: {scales}")
    return effects[0].scale


def _heterogeneity(effects: list[PoolableEffect], fixed_pooled_y: float) -> tuple[float, int]:
    weights = [1 / e.se ** 2 for e in effects]
    q = sum(w * (e.y - fixed_pooled_y) ** 2 for w, e in zip(weights, effects))
    df = len(effects) - 1
    return q, df


def fixed_effect_meta_analysis(effects: list[PoolableEffect]) -> MetaAnalysisResult:
    if len(effects) < 2:
        raise ValueError("meta-analysis needs at least 2 studies")
    scale = _check_same_scale(effects)

    weights = [1 / e.se ** 2 for e in effects]
    pooled_y = sum(w * e.y for w, e in zip(weights, effects)) / sum(weights)
    pooled_se = math.sqrt(1 / sum(weights))

    q, df = _heterogeneity(effects, pooled_y)
    i2 = max(0.0, (q - df) / q * 100) if q > 0 else 0.0

    return MetaAnalysisResult(
        model="fixed", scale=scale, pooled_y=pooled_y, pooled_se=pooled_se,
        ci_lower_y=pooled_y - Z_95 * pooled_se, ci_upper_y=pooled_y + Z_95 * pooled_se,
        Q=q, df=df, I2=i2, tau2=None,
    )


def random_effects_meta_analysis(effects: list[PoolableEffect]) -> MetaAnalysisResult:
    """DerSimonian-Laird random-effects model."""
    if len(effects) < 2:
        raise ValueError("meta-analysis needs at least 2 studies")
    scale = _check_same_scale(effects)

    fixed = fixed_effect_meta_analysis(effects)
    weights = [1 / e.se ** 2 for e in effects]
    c = sum(weights) - sum(w ** 2 for w in weights) / sum(weights)
    tau2 = max(0.0, (fixed.Q - fixed.df) / c) if c > 0 else 0.0

    random_weights = [1 / (e.se ** 2 + tau2) for e in effects]
    pooled_y = sum(w * e.y for w, e in zip(random_weights, effects)) / sum(random_weights)
    pooled_se = math.sqrt(1 / sum(random_weights))

    return MetaAnalysisResult(
        model="random", scale=scale, pooled_y=pooled_y, pooled_se=pooled_se,
        ci_lower_y=pooled_y - Z_95 * pooled_se, ci_upper_y=pooled_y + Z_95 * pooled_se,
        Q=fixed.Q, df=fixed.df, I2=fixed.I2, tau2=tau2,
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    # Five fictional studies' 2x2 tables, computed with Module 16's real
    # odds_ratio() function — deliberately including one study whose
    # effect direction disagrees with the others, to produce real,
    # non-zero heterogeneity rather than a suspiciously tidy example.
    studies = {
        "Study A": odds_ratio(a=30, b=10, c=15, d=25),
        "Study B": odds_ratio(a=25, b=15, c=12, d=28),
        "Study C": odds_ratio(a=40, b=20, c=20, d=40),
        "Study D": odds_ratio(a=18, b=22, c=20, d=20),  # near null
        "Study E": odds_ratio(a=12, b=28, c=22, d=18),  # favors control
    }

    print("Individual study effects:")
    effects = []
    for label, result in studies.items():
        print(f"  {label}: OR = {result.estimate:.3f}  95% CI [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")
        effects.append(from_effect_size_result(label, result))

    print()
    print("=" * 70)
    print("Fixed-effect model")
    print("=" * 70)
    fixed = fixed_effect_meta_analysis(effects)
    est, lo, hi = fixed.display_estimate()
    print(f"  Pooled OR = {est:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    print(f"  Q = {fixed.Q:.2f}  df = {fixed.df}  I2 = {fixed.I2:.1f}%")

    print()
    print("=" * 70)
    print("Random-effects model (DerSimonian-Laird)")
    print("=" * 70)
    random = random_effects_meta_analysis(effects)
    est, lo, hi = random.display_estimate()
    print(f"  Pooled OR = {est:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    print(f"  tau2 = {random.tau2:.4f}")
    print()
    if random.pooled_se > fixed.pooled_se:
        print("  Random-effects CI is wider than fixed-effect's — expected, since")
        print("  random-effects also accounts for between-study heterogeneity, not")
        print("  just each study's own sampling error.")


def _run_self_checks() -> None:
    # Two identical studies: pooling should reproduce that same estimate
    # exactly, with zero heterogeneity.
    identical = [
        from_effect_size_result("S1", odds_ratio(a=20, b=20, c=10, d=30)),
        from_effect_size_result("S2", odds_ratio(a=20, b=20, c=10, d=30)),
    ]
    fixed = fixed_effect_meta_analysis(identical)
    single = odds_ratio(a=20, b=20, c=10, d=30)
    assert abs(math.exp(fixed.pooled_y) - single.estimate) < 1e-9
    assert fixed.I2 == 0.0
    assert fixed.Q < 1e-9

    # Mixed scales must be rejected.
    from effect_size import standardized_mean_difference
    smd_effect = from_effect_size_result("S3", standardized_mean_difference(5, 1, 30, 4, 1, 30))
    try:
        fixed_effect_meta_analysis(identical + [smd_effect])
        raise AssertionError("expected MixedScaleError")
    except MixedScaleError:
        pass

    # Random-effects pooled SE must be >= fixed-effect's pooled SE whenever
    # there is any heterogeneity (tau2 > 0) — a real, checkable property
    # of the DerSimonian-Laird model, not just true in the demo by luck.
    heterogeneous = [
        from_effect_size_result("A", odds_ratio(a=30, b=10, c=15, d=25)),
        from_effect_size_result("B", odds_ratio(a=12, b=28, c=22, d=18)),
    ]
    f = fixed_effect_meta_analysis(heterogeneous)
    r = random_effects_meta_analysis(heterogeneous)
    if r.tau2 > 0:
        assert r.pooled_se >= f.pooled_se

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

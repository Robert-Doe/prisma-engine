"""
Module 16 — Effect Size Calculator

Real, standard formulas (Cochrane Handbook / Altman 1991) for the three
effect-size families from Prerequisite 6: Odds Ratio and Risk Ratio (binary
outcomes, 2x2 tables) and Standardized Mean Difference (continuous
outcomes). Every formula here is the actual textbook formula, not an
approximation invented for this course.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Z_95 = 1.96  # standard normal critical value for a 95% CI


class ZeroCellError(ValueError):
    """Raised when a 2x2 table has a zero cell, which makes the standard
    log-scale standard error formula divide by zero. Real meta-analysis
    practice (Cochrane Handbook) applies a continuity correction (+0.5 to
    every cell) rather than silently producing NaN or crashing uninformatively."""


@dataclass
class EffectSizeResult:
    measure: str  # "OR" | "RR" | "SMD"
    estimate: float
    ci_lower: float
    ci_upper: float
    no_effect_value: float  # 1.0 for OR/RR, 0.0 for SMD

    def crosses_no_effect(self) -> bool:
        return self.ci_lower <= self.no_effect_value <= self.ci_upper


def odds_ratio(a: int, b: int, c: int, d: int, continuity_correction: bool = False) -> EffectSizeResult:
    """a, b = events, non-events in the treatment group.
    c, d = events, non-events in the control group."""
    if 0 in (a, b, c, d):
        if not continuity_correction:
            raise ZeroCellError(
                f"zero cell in table (a={a}, b={b}, c={c}, d={d}) — the standard "
                f"log-odds SE formula divides by zero here. Pass continuity_correction=True "
                f"to apply the standard +0.5-per-cell correction, per Cochrane Handbook guidance."
            )
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    or_estimate = (a * d) / (b * c)
    se_ln = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    ln_or = math.log(or_estimate)
    return EffectSizeResult(
        measure="OR",
        estimate=or_estimate,
        ci_lower=math.exp(ln_or - Z_95 * se_ln),
        ci_upper=math.exp(ln_or + Z_95 * se_ln),
        no_effect_value=1.0,
    )


def risk_ratio(a: int, n1: int, c: int, n2: int, continuity_correction: bool = False) -> EffectSizeResult:
    """a = events in treatment group (of n1 total). c = events in control
    group (of n2 total)."""
    if a == 0 or c == 0:
        if not continuity_correction:
            raise ZeroCellError(
                f"zero event count (a={a}, c={c}) — the standard log-risk SE formula "
                f"divides by zero here. Pass continuity_correction=True to apply the "
                f"standard +0.5 correction, per Cochrane Handbook guidance."
            )
        a, c = a + 0.5, c + 0.5

    rr_estimate = (a / n1) / (c / n2)
    se_ln = math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)
    ln_rr = math.log(rr_estimate)
    return EffectSizeResult(
        measure="RR",
        estimate=rr_estimate,
        ci_lower=math.exp(ln_rr - Z_95 * se_ln),
        ci_upper=math.exp(ln_rr + Z_95 * se_ln),
        no_effect_value=1.0,
    )


def standardized_mean_difference(
    mean1: float, sd1: float, n1: int, mean2: float, sd2: float, n2: int,
) -> EffectSizeResult:
    """Cohen's d using the pooled standard deviation. Group 1 is typically
    the intervention/exposed group, group 2 the comparator."""
    pooled_sd = math.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    d = (mean1 - mean2) / pooled_sd
    se = math.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return EffectSizeResult(
        measure="SMD",
        estimate=d,
        ci_lower=d - Z_95 * se,
        ci_upper=d + Z_95 * se,
        no_effect_value=0.0,
    )


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    print("=" * 70)
    print("Odds Ratio — a fictional case-control study")
    print("=" * 70)
    print("Treatment group: 30 events / 10 non-events. Control: 15 events / 25 non-events.")
    result = odds_ratio(a=30, b=10, c=15, d=25)
    print(f"  OR = {result.estimate:.3f}  95% CI [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")
    print(f"  Crosses no-effect (1.0)? {result.crosses_no_effect()}")

    print()
    print("=" * 70)
    print("Risk Ratio — a fictional cohort study")
    print("=" * 70)
    print("Treatment: 40 events of 200. Control: 60 events of 200.")
    result = risk_ratio(a=40, n1=200, c=60, n2=200)
    print(f"  RR = {result.estimate:.3f}  95% CI [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")
    print(f"  Crosses no-effect (1.0)? {result.crosses_no_effect()}")

    print()
    print("=" * 70)
    print("Standardized Mean Difference — a fictional RCT, two instruments")
    print("=" * 70)
    print("Remote group: mean=7.2, sd=1.4, n=85. In-office group: mean=6.5, sd=1.6, n=90.")
    result = standardized_mean_difference(mean1=7.2, sd1=1.4, n1=85, mean2=6.5, sd2=1.6, n2=90)
    print(f"  SMD = {result.estimate:.3f}  95% CI [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")
    print(f"  Crosses no-effect (0.0)? {result.crosses_no_effect()}")

    print()
    print("=" * 70)
    print("A zero cell breaks the standard formula — caught, not silently wrong")
    print("=" * 70)
    try:
        odds_ratio(a=12, b=0, c=8, d=20)
    except ZeroCellError as e:
        print(f"  Raised as expected: {e}")
    print("  With continuity_correction=True, the standard +0.5 fix is applied instead:")
    result = odds_ratio(a=12, b=0, c=8, d=20, continuity_correction=True)
    print(f"  OR = {result.estimate:.3f}  95% CI [{result.ci_lower:.3f}, {result.ci_upper:.3f}]")


def _run_self_checks() -> None:
    # Odds ratio: known hand-computable example.
    # a=10, b=40, c=5, d=45 -> OR = (10*45)/(40*5) = 450/200 = 2.25
    result = odds_ratio(a=10, b=40, c=5, d=45)
    assert abs(result.estimate - 2.25) < 1e-9
    assert result.no_effect_value == 1.0
    assert result.ci_lower < 2.25 < result.ci_upper

    # A balanced 1:1 table (no real effect) should have OR = 1.0 exactly,
    # and its CI must therefore cross the no-effect line.
    balanced = odds_ratio(a=20, b=20, c=20, d=20)
    assert abs(balanced.estimate - 1.0) < 1e-9
    assert balanced.crosses_no_effect()

    # Risk ratio: a=50/n1=100 vs c=25/n2=100 -> RR = 0.5/0.25 = 2.0
    rr = risk_ratio(a=50, n1=100, c=25, n2=100)
    assert abs(rr.estimate - 2.0) < 1e-9

    # SMD: identical groups -> d = 0.0 exactly, CI must cross 0.
    smd_null = standardized_mean_difference(mean1=5.0, sd1=1.0, n1=50, mean2=5.0, sd2=1.0, n2=50)
    assert abs(smd_null.estimate - 0.0) < 1e-9
    assert smd_null.crosses_no_effect()

    # Zero cell raises by default, and the continuity-corrected version
    # produces a finite, sane result instead.
    try:
        odds_ratio(a=10, b=0, c=5, d=10)
        raise AssertionError("expected ZeroCellError")
    except ZeroCellError:
        pass
    corrected = odds_ratio(a=10, b=0, c=5, d=10, continuity_correction=True)
    assert math.isfinite(corrected.estimate)
    assert corrected.estimate > 1.0  # treatment still favored after correction

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

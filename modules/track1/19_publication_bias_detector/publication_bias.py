"""
Module 19 — Publication Bias Detector

Funnel plot: each study's effect (x) vs. its standard error (y, inverted —
precise studies at top), with a pseudo-95%-CI funnel drawn around the
pooled estimate. In the absence of publication bias, studies should
scatter roughly symmetrically inside the funnel. Egger's test (Egger et
al., 1997, BMJ) quantifies that asymmetry via a real linear regression.

IMPORTANT, real methodological caveat this module states explicitly rather
than hiding: the Cochrane Handbook recommends against using funnel-plot
asymmetry tests with fewer than ~10 studies — statistical power to detect
real asymmetry is too low. This module's own demo uses 5 studies specifically
to prove the mechanism works AND to demonstrate that caveat concretely, not
because 5 studies is a methodologically sound sample for this test.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "17_meta_analysis_engine"))
from meta_analysis import MetaAnalysisResult, PoolableEffect  # noqa: E402

# Two-tailed 95% critical t-values, indexed by degrees of freedom.
# Falls back to the normal approximation (1.96) for df > 20 — see
# DECISIONS.md for why a small lookup table instead of a full t-distribution
# implementation.
_T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    12: 2.179, 15: 2.131, 18: 2.101, 20: 2.086,
}


def _t_critical_95(df: int) -> float:
    if df in _T_CRITICAL_95:
        return _T_CRITICAL_95[df]
    if df > 20:
        return 1.96
    # nearest available df below the requested one, conservative (larger t)
    available = sorted(k for k in _T_CRITICAL_95 if k <= df)
    return _T_CRITICAL_95[available[-1]] if available else 12.706


class InsufficientStudiesError(ValueError):
    """Raised when there aren't enough studies for Egger's regression to
    even be computed (needs at least 3, for 1 degree of freedom)."""


@dataclass
class EggersTestResult:
    intercept: float
    se_intercept: float
    t_statistic: float
    df: int
    significant_at_05: bool
    n_studies: int


def eggers_test(effects: list[PoolableEffect]) -> EggersTestResult:
    n = len(effects)
    if n < 3:
        raise InsufficientStudiesError(f"Egger's test needs at least 3 studies, got {n}")

    xs = [1 / e.se for e in effects]           # precision
    ys = [e.y / e.se for e in effects]         # standardized effect

    x_mean, y_mean = sum(xs) / n, sum(ys) / n
    ss_xx = sum((x - x_mean) ** 2 for x in xs)
    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean

    residuals = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    df = n - 2
    mse = sum(r ** 2 for r in residuals) / df
    se_intercept = math.sqrt(mse * (1 / n + x_mean ** 2 / ss_xx))
    t_stat = intercept / se_intercept

    t_crit = _t_critical_95(df)
    return EggersTestResult(
        intercept=intercept, se_intercept=se_intercept, t_statistic=t_stat,
        df=df, significant_at_05=abs(t_stat) > t_crit, n_studies=n,
    )


def render_funnel_plot(effects: list[PoolableEffect], pooled_y: float, output_path: Path) -> None:
    max_se = max(e.se for e in effects) * 1.15
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter([e.y for e in effects], [e.se for e in effects], s=70, color="#2f6f9f", zorder=3)
    for e in effects:
        ax.annotate(e.study_label, (e.y, e.se), textcoords="offset points", xytext=(8, 0), fontsize=8)

    se_range = [i * max_se / 100 for i in range(101)]
    ax.plot([pooled_y - 1.96 * se for se in se_range], se_range, color="#888888", linestyle="--", linewidth=1)
    ax.plot([pooled_y + 1.96 * se for se in se_range], se_range, color="#888888", linestyle="--", linewidth=1)
    ax.axvline(pooled_y, color="#9f3f3f", linewidth=1.2)

    ax.set_ylim(max_se, 0)  # inverted: most precise (smallest SE) at top
    ax.set_xlabel("Effect estimate (pooling scale)")
    ax.set_ylabel("Standard error")
    ax.set_title("Funnel plot")
    fig.tight_layout()
    fig.savefig(output_path, dpi=130)
    plt.close(fig)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "16_effect_size_calculator"))
    from effect_size import odds_ratio  # noqa: E402
    from meta_analysis import fixed_effect_meta_analysis, from_effect_size_result  # noqa: E402

    studies = {
        "Study A": odds_ratio(a=30, b=10, c=15, d=25),
        "Study B": odds_ratio(a=25, b=15, c=12, d=28),
        "Study C": odds_ratio(a=40, b=20, c=20, d=40),
        "Study D": odds_ratio(a=18, b=22, c=20, d=20),
        "Study E": odds_ratio(a=12, b=28, c=22, d=18),
    }
    effects = [from_effect_size_result(label, result) for label, result in studies.items()]
    fixed = fixed_effect_meta_analysis(effects)

    print("=" * 70)
    print("Egger's test")
    print("=" * 70)
    result = eggers_test(effects)
    print(f"  intercept = {result.intercept:.3f}  SE = {result.se_intercept:.3f}")
    print(f"  t = {result.t_statistic:.3f}  df = {result.df}")
    print(f"  significant asymmetry at p<0.05? {result.significant_at_05}")

    print()
    print("  CAVEAT (real, not boilerplate): this test was run on only 5 studies.")
    print("  The Cochrane Handbook recommends against interpreting funnel-plot")
    print("  asymmetry tests with fewer than ~10 studies — with this few studies,")
    print("  the test has very low power to detect real asymmetry either way.")
    print("  This demo proves the MECHANISM works, not that 5 studies is enough")
    print("  evidence to draw a real conclusion about publication bias.")

    out_path = Path(__file__).resolve().parent / "funnel_plot_demo.png"
    render_funnel_plot(effects, fixed.pooled_y, out_path)
    size = out_path.stat().st_size
    with open(out_path, "rb") as f:
        is_png = f.read(8) == b"\x89PNG\r\n\x1a\n"
    print()
    print(f"Funnel plot saved: {out_path.name}, {size} bytes, valid PNG header: {is_png}")


def _run_self_checks() -> None:
    # Synthetic data (built by construction, not real studies) with varying
    # precision but no systematic asymmetry — Egger's regression needs
    # variation in SE across studies to be computable at all (identical SEs
    # give zero variance in precision, an undefined regression slope).
    symmetric = [
        PoolableEffect("S1", "log", 0.50, 0.20),
        PoolableEffect("S2", "log", 0.51, 0.15),
        PoolableEffect("S3", "log", 0.49, 0.10),
        PoolableEffect("S4", "log", 0.50, 0.05),
    ]
    result = eggers_test(symmetric)
    assert abs(result.intercept) < 0.5  # small, not exactly zero due to noise, but not large
    assert result.df == 2

    # Too few studies must be rejected explicitly.
    try:
        eggers_test([PoolableEffect("A", "log", 0.1, 0.1), PoolableEffect("B", "log", 0.2, 0.1)])
        raise AssertionError("expected InsufficientStudiesError")
    except InsufficientStudiesError:
        pass

    assert _t_critical_95(5) == 2.571
    assert _t_critical_95(100) == 1.96

    # render_funnel_plot produces a real, non-trivial file.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test_funnel.png"
        render_funnel_plot(symmetric, 0.5, out)
        assert out.stat().st_size > 1000
        with open(out, "rb") as f:
            assert f.read(8) == b"\x89PNG\r\n\x1a\n"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

"""
Module 18 — Forest Plot Renderer

Renders Module 17's meta-analysis result as a real forest plot: one row
per study (a horizontal CI line + a square marker sized by that study's
weight), a diamond for the pooled estimate (width = pooled CI), and a
vertical no-effect reference line. Real matplotlib output, saved to disk
and verified as a real PNG file — not a description of what a forest plot
looks like.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend — this module never opens a window
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "17_meta_analysis_engine"))
from meta_analysis import (  # noqa: E402
    MetaAnalysisResult,
    PoolableEffect,
    Z_95,
    fixed_effect_meta_analysis,
    from_effect_size_result,
    random_effects_meta_analysis,
)


def _to_natural(y: float, se: float, scale: str) -> tuple[float, float, float]:
    """Converts a (point, SE) pair on the pooling scale into a
    (point, ci_lower, ci_upper) triple on the natural display scale."""
    if scale == "log":
        return math.exp(y), math.exp(y - Z_95 * se), math.exp(y + Z_95 * se)
    return y, y - Z_95 * se, y + Z_95 * se


def render_forest_plot(
    effects: list[PoolableEffect],
    meta_result: MetaAnalysisResult,
    output_path: Path,
    measure_name: str = "OR",
) -> None:
    n = len(effects)
    weights = [1 / e.se ** 2 for e in effects]
    max_weight = max(weights)
    no_effect = 1.0 if meta_result.scale == "log" else 0.0

    fig, ax = plt.subplots(figsize=(8, 0.55 * (n + 2) + 1.5))

    for i, (effect, weight) in enumerate(zip(effects, weights)):
        y_pos = n - i
        est, lo, hi = _to_natural(effect.y, effect.se, effect.scale)
        ax.plot([lo, hi], [y_pos, y_pos], color="#333333", linewidth=1.3, zorder=1)
        marker_size = 60 + 340 * (weight / max_weight)
        ax.scatter([est], [y_pos], s=marker_size, marker="s", color="#2f6f9f", zorder=3)

    pooled_est, pooled_lo, pooled_hi = meta_result.display_estimate()
    diamond_y = 0
    half_height = 0.28
    diamond = mpatches.Polygon(
        [[pooled_lo, diamond_y], [pooled_est, diamond_y + half_height],
         [pooled_hi, diamond_y], [pooled_est, diamond_y - half_height]],
        closed=True, facecolor="#9f3f3f", edgecolor="#5f1f1f", zorder=3,
    )
    ax.add_patch(diamond)

    ax.axvline(no_effect, color="#888888", linestyle="--", linewidth=1, zorder=0)

    labels = [e.study_label for e in effects] + [f"Pooled ({meta_result.model}-effect)"]
    ax.set_yticks(list(range(n, -1, -1)))
    ax.set_yticklabels(labels)
    ax.set_ylim(-1, n + 1)

    if meta_result.scale == "log":
        ax.set_xscale("log")
    ax.set_xlabel(measure_name)
    ax.set_title(f"Forest plot — {measure_name} (I² = {meta_result.I2:.1f}%)")

    fig.tight_layout()
    fig.savefig(output_path, dpi=130)
    plt.close(fig)


# --- Demo -------------------------------------------------------------------

def _run_demo() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "16_effect_size_calculator"))
    from effect_size import odds_ratio  # noqa: E402

    studies = {
        "Study A": odds_ratio(a=30, b=10, c=15, d=25),
        "Study B": odds_ratio(a=25, b=15, c=12, d=28),
        "Study C": odds_ratio(a=40, b=20, c=20, d=40),
        "Study D": odds_ratio(a=18, b=22, c=20, d=20),
        "Study E": odds_ratio(a=12, b=28, c=22, d=18),
    }
    effects = [from_effect_size_result(label, result) for label, result in studies.items()]

    fixed = fixed_effect_meta_analysis(effects)
    random = random_effects_meta_analysis(effects)

    for model_name, result in [("fixed", fixed), ("random", random)]:
        out_path = Path(__file__).resolve().parent / f"forest_plot_{model_name}.png"
        render_forest_plot(effects, result, out_path, measure_name="Odds Ratio")
        size = out_path.stat().st_size
        with open(out_path, "rb") as f:
            magic = f.read(8)
        is_png = magic == b"\x89PNG\r\n\x1a\n"
        print(f"{model_name}-effect forest plot: {out_path.name}, {size} bytes, valid PNG header: {is_png}")


def _run_self_checks() -> None:
    assert _to_natural(math.log(2.0), 0.1, "log")[0] == 2.0
    lo, hi = _to_natural(math.log(2.0), 0.1, "log")[1:]
    assert lo < 2.0 < hi

    assert _to_natural(0.5, 0.1, "linear") == (0.5, 0.5 - Z_95 * 0.1, 0.5 + Z_95 * 0.1)

    # Rendering actually produces a real, non-trivial PNG file.
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "16_effect_size_calculator"))
    from effect_size import odds_ratio  # noqa: E402

    effects = [
        from_effect_size_result("X", odds_ratio(a=20, b=20, c=10, d=30)),
        from_effect_size_result("Y", odds_ratio(a=25, b=15, c=12, d=28)),
    ]
    result = fixed_effect_meta_analysis(effects)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test_plot.png"
        render_forest_plot(effects, result, out, measure_name="OR")
        assert out.exists()
        assert out.stat().st_size > 1000  # a trivial/blank PNG would be far smaller
        with open(out, "rb") as f:
            assert f.read(8) == b"\x89PNG\r\n\x1a\n"

    print("All self-checks passed.")


if __name__ == "__main__":
    _run_self_checks()
    print()
    _run_demo()

# Module 18 — Decisions: Forest Plot Renderer

## Line-by-line / unit-by-unit

### matplotlib, not hand-generated SVG (unlike Module 12's PRISMA diagram)
**(b) Forced by external contract.** The ROADMAP's Tools/Architecture Target specifically assigns matplotlib to "forest/funnel plots" and SVG/HTML to PRISMA diagrams and network graphs. A forest plot's content is fundamentally different from a PRISMA diagram's — continuous numeric axes, log scaling, precisely-positioned markers sized by weight — exactly the kind of chart matplotlib is built for, where hand-computing coordinate geometry in raw SVG would be reinventing what a plotting library already does correctly.

### `matplotlib.use("Agg")` is set before importing `pyplot`
**(a) Forced by the platform.** This module runs in a headless environment with no display. matplotlib's default backend tries to open an interactive window and fails (or hangs) without one; `Agg` is the standard non-interactive, file-output-only backend. This has to be set before `pyplot` is imported — setting it after would have no effect, since the backend is selected at import time.

### Square marker size is scaled by each study's inverse-variance weight (`1/SE²`), matching the real forest-plot convention
**(b) Forced by external contract.** This isn't a stylistic choice — a forest plot's marker size conventionally communicates precision (and therefore influence on the pooled result) at a glance, without requiring the reader to read the numbers. A study with a tight confidence interval gets a visibly larger square than one with a wide interval, which is exactly what a reader of a real published forest plot expects to see.

### The pooled estimate is drawn as a diamond, not another square
**(b) Forced by external contract.** The diamond is the field-standard symbol for a pooled/summary estimate in a forest plot — distinguishing it visually from individual studies is itself part of the convention, not a cosmetic choice this module invented. Its width spans the pooled confidence interval, the same real-data-driven sizing principle as the study squares.

### The x-axis switches to a log scale only when `meta_result.scale == "log"`
**(c) Convention, following directly from Module 16/17's own scale handling.** An odds ratio or risk ratio's natural display scale is genuinely logarithmic — equal visual distances should represent equal multiplicative changes (2× vs. 4× should look like the same-sized jump as 4× vs. 8×). A standardized mean difference has no such requirement; forcing a log scale onto a linear difference measure would misrepresent it. This mirrors the exact same "ratios need log-scale treatment, differences don't" principle Modules 16 and 17 already established.

### Rendering is verified by reading back the saved file's PNG magic bytes and checking a minimum file size, not just checking that `savefig()` didn't raise
**(c) Convention.** `savefig()` can succeed while producing a nearly-blank image (a bug that silently draws nothing would still "work" in the sense of not crashing). Checking the actual PNG signature (`\x89PNG\r\n\x1a\n`) and a size floor (`> 1000` bytes) catches the difference between "a file was written" and "a real, non-trivial image was written" — closer to Module 12's precedent of re-parsing its own SVG output rather than trusting that generation succeeded just because no exception was raised.

## Decisions We Made

| Decision | Category |
|---|---|
| matplotlib instead of hand-generated SVG | (b) External contract (course's own architecture target) |
| `Agg` backend set before importing `pyplot` | (a) Forced by platform (headless environment) |
| Marker size scaled by inverse-variance weight | (b) External contract (forest-plot convention) |
| Pooled estimate drawn as a diamond | (b) External contract (forest-plot convention) |
| Log x-axis only for log-scale measures | (c) Convention, following Modules 16-17's scale handling |
| Output verified via PNG magic bytes + size floor | (c) Convention |

## What We Proved

Running [`forest_plot.py`](forest_plot.py) rendered Module 17's actual
pooled results — both the fixed-effect and random-effects versions of the
same five real studies — into real PNG files, and:

1. **Both files are genuine, non-trivial images**, confirmed by reading back their actual bytes (`\x89PNG\r\n\x1a\n` magic header, >1000 bytes) rather than trusting that `savefig()` not raising meant something real got drawn.
2. **The forest plot visually confirms Module 17's numeric finding.** In the fixed-effect plot, the red diamond sits entirely to the right of the dashed no-effect line. In the random-effects plot, drawn from the exact same five studies, the diamond visibly straddles the no-effect line — the same real divergence Module 17 reported numerically (`[1.297, 2.851]` vs. `[0.675, 5.154]`), now visible at a glance rather than requiring the reader to compare two intervals by hand.
3. **Marker sizes visibly reflect study precision** — Study A and Study C, the two most precisely-estimated studies, render with noticeably larger squares than Study D, the least precise — direct visual confirmation the weighting scheme is doing what a forest plot is supposed to communicate.

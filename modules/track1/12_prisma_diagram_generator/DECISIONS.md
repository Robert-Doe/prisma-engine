# Module 12 — Decisions: PRISMA Diagram Generator

## Line-by-line / unit-by-unit

### Output is hand-generated SVG markup, not a matplotlib figure or an image library
**(c) Convention, driven by (b) the course's architecture target.** The ROADMAP commits specifically to "PRISMA diagrams and network graphs as generated SVG/HTML." SVG is plain text, diffable, embeddable directly in any of this course's HTML tutorials with no image file to manage separately, and requires no dependency beyond the standard library — matplotlib is reserved for the forest/funnel plots later in the course, where an image-style chart genuinely fits the content better than boxes and arrows do.

### The diagram renders progressively — a partial pipeline (no eligibility logged yet) still produces valid SVG
**(c) Convention.** Nothing about this module requires a fully-finished review to exist. Checking `tracker.screening_included is not None` and `tracker.eligibility_included is not None` before adding each subsequent stage means the same function correctly renders a diagram for a review that's only gotten as far as Module 8, and a full diagram once Module 9's stage is logged too — verified directly in the self-checks, which render both a full and a partial tracker.

### Box height is computed from wrapped text, not fixed
**(c) Convention.** A real PRISMA diagram's exclusion-reason box can contain anywhere from one short reason to several long ones — Module 8's real demo run alone produced a two-reason list. A fixed box height would either clip a long list or waste space on a short one; computing height from `len(text_lines) * LINE_HEIGHT` means the box is exactly as tall as its actual content, every time.

### `render_prisma_svg()` never mutates the tracker, and re-reads its state fresh
**(c) Convention.** The generator has no reason to know or care how the tracker's counts were produced — real live data (as the demo uses) or a hand-constructed example (as the self-checks use) look identical to this function. That's a deliberate separation: Module 7 owns tracking and validating counts, Module 12 only ever reads and renders them.

### The demo re-imports and re-runs Modules 4, 5, 6, and 8's real functions rather than hardcoding example numbers
**(c) Convention.** This module's whole claim is that a tracker's *real* state can become a *real* diagram — hardcoding plausible-looking numbers would only demonstrate that the rendering code can draw boxes, not that it correctly reflects genuine upstream pipeline state. Re-running the real chain and then parsing the resulting SVG back out to confirm the actual counts appear in it (`"n = 20" in all_text`, etc.) is what makes this module's self-checks a real end-to-end proof rather than a rendering-only unit test.

### The generated SVG is validated by parsing it back with `xml.etree.ElementTree`, not just by eyeballing it
**(c) Convention.** A string that merely *looks* like SVG (unclosed tags, malformed attributes) would still print successfully and might even render tolerantly in some browsers. Round-tripping the output through a real XML parser and asserting on the parsed structure (`root.tag`, element counts) is what actually proves the output is well-formed markup, not just plausible-looking text.

## Decisions We Made

| Decision | Category |
|---|---|
| Hand-generated SVG, not matplotlib/image library | (c) Convention, driven by (b) architecture target |
| Diagram renders progressively for partial pipelines | (c) Convention |
| Box height computed from wrapped text | (c) Convention |
| Generator never mutates the tracker | (c) Convention |
| Demo re-runs real Modules 4-8, doesn't hardcode numbers | (c) Convention |
| Output validated by re-parsing as XML | (c) Convention |

## What We Proved

Running [`diagram_generator.py`](diagram_generator.py) chained real,
live-fetched data from Modules 4 through 8 into Module 7's tracker, then:

1. **A real PRISMA flow diagram was rendered from real pipeline state** — the identification, deduplication, and screening counts baked into the generated SVG are the actual counts from an actual live run, not placeholder numbers.
2. **The output is genuinely valid SVG, not just SVG-shaped text.** Re-parsing it with `ElementTree` succeeded and found the expected `rect`/`text` element counts — proof the markup is well-formed, confirmed by round-tripping it through a real parser rather than assumed from how the generation code was written.
3. **The renderer correctly adapts to how much of the pipeline has actually run.** The self-checks render both a full tracker (identification through eligibility) and a partial one (identification and dedup only) and confirm both produce valid SVG — this module doesn't assume a finished review, it renders whatever real state actually exists.

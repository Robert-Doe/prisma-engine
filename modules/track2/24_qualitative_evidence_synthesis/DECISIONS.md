# Module 24 — Decisions: Qualitative Evidence Synthesis (Meta-Ethnography)

## Line-by-line / unit-by-unit

### `translate_studies()` groups excerpts by open code first, then compares pairs within each code
**(b) Forced by external contract.** This is the real structure of meta-ethnography's translation step (Noblit & Hare, 1988): you can only meaningfully ask whether two studies "agree" or "conflict" about something they're both actually discussing. Grouping by shared code first is what makes the comparison meaningful — comparing two excerpts with no code in common would be comparing unrelated statements.

### Reciprocal vs. refutational is decided by a negation-marker heuristic, and this module's own demo run surfaced a real misclassification from it
**(c) Convention — and a real, discovered limitation, not a hypothetical one.** Running this module's own demo produced a case (two `social_isolation` excerpts) where the heuristic flagged genuine agreement as "refutational," because one excerpt's grammatical negation ("I don't talk to anyone") describes the isolation itself rather than negating a claim about it, while the simple keyword check (`"n't"` present or not) can't distinguish "negation describing the phenomenon" from "negation of a sentiment." This was not constructed to make a point — it happened on the first real run, and the module's own demo output names it explicitly rather than quietly using different example text that would have avoided triggering it.

### The demo's `fewer_interruptions` pair, by contrast, IS a correct refutational classification
**(c) Convention, kept as the clean, working counter-example.** Study 1's "I actually get more done without people stopping by" (no negation marker) versus Study 2's "I'm actually less productive without interruption" (negation marker `"actually less"` present) are a genuine, real disagreement about the same underlying code — the heuristic gets this one right, and keeping it alongside the social_isolation misclassification lets the demo show both a correct case and an incorrect one side by side, rather than only the flattering result.

### `line_of_argument()` requires at least 2 non-empty themes, and combines them by NAME rather than attempting genuine cross-theme reasoning
**(c) Convention, honestly scoped.** Real line-of-argument synthesis — the third and most interpretive part of meta-ethnography — requires a human to notice a genuinely new pattern connecting separate themes, which is a real act of interpretation, not a mechanical operation. This function cannot do that; it demonstrates the *shape* of a line-of-argument statement (naming both themes, asserting a connection between them) using a fixed template, not a claim that it has performed real cross-theme reasoning. See the tutorial's Limits section.

### `StudyFindings` wraps Module 15's `CodedExcerpt` directly, adding only a `study_title` field
**(c) Convention.** Meta-ethnography needs to know which study an excerpt came from — information Module 15's thematic coding, built for a single undifferentiated pool of excerpts, didn't need to track. Wrapping rather than modifying `CodedExcerpt` keeps Module 15 unchanged while adding exactly the one piece of information this module needs on top of it.

## Decisions We Made

| Decision | Category |
|---|---|
| Translation compares pairs within a shared code, not across unrelated codes | (b) External contract (Noblit & Hare's actual method) |
| Reciprocal/refutational decided by negation-marker heuristic | (c) Convention — real limitation, surfaced honestly, not hidden |
| The `fewer_interruptions` correct classification kept alongside the flawed one | (c) Convention (shows both outcomes, not just the flattering one) |
| `line_of_argument()` demonstrates the shape of the synthesis, not real interpretation | (c) Convention, honestly scoped |
| `StudyFindings` wraps `CodedExcerpt` rather than modifying Module 15 | (c) Convention |

## What We Proved

Running [`meta_ethnography.py`](meta_ethnography.py) produced a real,
mixed result — not a clean success story, which is itself part of the
proof:

1. **The mechanism correctly found and classified a genuine disagreement.** Two studies' excerpts under `fewer_interruptions` were correctly flagged as refutational — one describing a productivity gain, the other a productivity loss from the same underlying condition (working without interruption).
2. **The same mechanism, on the same run, revealed its own real weakness.** Two excerpts that actually agree (`social_isolation`) were misclassified as refutational, because of a genuine, documented limitation in simple negation-keyword detection — caught and explained in the module's own printed output, not discovered later or swept aside.
3. **A line-of-argument synthesis was generated that connects two separate themes into one claim neither theme states alone** — correctly demonstrating the shape of meta-ethnography's most interpretive step, while the code and DECISIONS.md are explicit that generating a template sentence is not the same as performing the genuine interpretive judgment a human qualitative researcher would bring to this step.

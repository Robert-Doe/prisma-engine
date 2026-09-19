# PRISMA Engine — Web Demo

A real, in-browser TypeScript port of two of this course's Python modules:

- **Module 6 — Deduplication Engine** (`dedup_engine.py`): exact-DOI grouping,
  then fuzzy title similarity (Ratcliff/Obershelp, matching Python's
  `difflib.SequenceMatcher.ratio()`) gated by a Jaccard last-name overlap
  guard.
- **Module 12 — PRISMA Diagram Generator** (`diagram_generator.py`): renders
  the actual PRISMA flow-diagram SVG structure from a `PrismaFlowTracker`
  (Module 7), with the same stage labels, box geometry, and colors as the
  Python source.

See `src/lib/` for the ported algorithms — each file documents exactly which
Python module it mirrors and where the two intentionally diverge (only the
screening stage, which the course itself only ever simulates, is synthetic).

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

Outputs a static site to `dist/`.

## Deploy

This is a static Vite build — deploy `dist/` to any static host.

**Vercel / Netlify / Cloudflare Pages:**

- Root directory: `webapp`
- Build command: `npm run build`
- Output directory: `dist`

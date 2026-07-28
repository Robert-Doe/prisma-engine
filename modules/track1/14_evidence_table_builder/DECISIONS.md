# Module 14 — Decisions: Evidence Table Builder

## Line-by-line / unit-by-unit

### `build_evidence_table()` re-validates every row against the target schema, even though `extract()` already validated it once in Module 10
**(c) Convention — the central safety check of this module.** `ExtractedRecord` is a plain dataclass; nothing stops someone from constructing one directly with `ExtractedRecord(record=..., data={...})`, bypassing Module 10's `extract()` entirely and its validation with it. The self-checks and demo both construct exactly that bypass on purpose, to prove the table builder doesn't just trust that every row was properly validated somewhere upstream — it checks again, at assembly time, against the one schema the whole table is supposed to share.

### `SchemaMismatchError` is a distinct exception type from Module 10's `ExtractionValidationError`, even though it wraps one
**(c) Convention.** The two errors mean different things to a caller. `ExtractionValidationError` means "this one row's data is invalid." `SchemaMismatchError` means "this row can't join this specific table" — a table-level concern, not a row-level one. Chaining the original error (`raise SchemaMismatchError(...) from e`) keeps the underlying reason visible while still letting table-assembly code catch one specific, table-scoped exception type.

### `column_names()` always starts with `title` and `year`, then the schema's fields, in schema-declaration order
**(c) Convention.** Every evidence table needs some way to identify which row is which study — `title` and `year` are the two fields every `Record` reliably carries (see Module 3), and putting them first means a human reading the table left to right sees "which study" before "what it found," matching how a person would naturally read a table built for comparison.

### `render_markdown()` renders every value with `str(...)`, including a blank string for a genuinely missing optional field
**(c) Convention.** Real data in the demo has exactly this case — one study's `outcome_measure` was left out entirely, since Module 10 marked that field optional. Rendering it as an empty table cell (rather than the literal text `"None"` or raising) keeps the table readable without disguising the fact that particular cell has no recorded value.

### The table assumes one shared schema for the whole table, not a per-row schema
**(c) Convention.** A genuinely comparable table requires every row to answer the same questions — that's what "comparable" means here. A future module handling studies extracted under genuinely different schemas (say, RCTs and qualitative studies needing different extraction fields entirely) would need a different design; this module's scope is the more common, narrower case of one review's one extraction form applied consistently.

## Decisions We Made

| Decision | Category |
|---|---|
| Every row re-validated at assembly time, not trusted from Module 10 | (c) Convention (this module's core safety check) |
| `SchemaMismatchError` distinct from, but chained to, `ExtractionValidationError` | (c) Convention |
| Column order: title, year, then schema fields in declaration order | (c) Convention |
| Missing optional values render as blank cells | (c) Convention |
| One shared schema per table, not per-row schemas | (c) Convention |

## What We Proved

Running [`evidence_table.py`](evidence_table.py) demonstrated the module's
exact claim — heterogeneous studies become directly comparable once
assembled:

1. **Three independently-extracted studies became one table where a column can be read straight down.** `[row["effect_direction"] for row in table.to_dict_rows()]` pulled `['positive', 'no effect', 'mixed']` in one line — reading across three separate `ExtractedRecord`s individually could never produce that same directly-comparable list without first assembling them.
2. **A row that bypassed Module 10's own validation was still caught here.** Constructing an `ExtractedRecord` directly (skipping `extract()`) with an incomplete data dict and feeding it into `build_evidence_table()` correctly raised `SchemaMismatchError`, naming the specific study and the specific missing field — proof this module doesn't just assume every row already passed validation somewhere else.

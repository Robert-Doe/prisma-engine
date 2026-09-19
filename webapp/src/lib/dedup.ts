/**
 * Faithful port of modules/track1/06_deduplication_engine/dedup_engine.py.
 *
 * Two passes over the corpus:
 *   1. Exact-DOI grouping (cheap, unambiguous) — normalize away URL
 *      prefixes and case, then group by exact match.
 *   2. Fuzzy title + author matching on whatever pass 1 didn't already
 *      remove — Ratcliff/Obershelp title similarity (see similarity.ts)
 *      gated by a Jaccard last-name-overlap guard, exactly like the
 *      Python original.
 *
 * Every function name, default threshold, and control-flow decision below
 * mirrors dedup_engine.py line for line.
 */

import { sequenceRatio } from './similarity';
import type { BibRecord } from './record';

export function normalizeDoi(doi: string | null): string | null {
  if (!doi) return null;
  let d = doi.trim().toLowerCase();
  d = d.replace(/^https?:\/\/(dx\.)?doi\.org\//, '');
  return d || null;
}

export function normalizeTitle(title: string): string {
  let t = title.toLowerCase();
  t = t.replace(/[^\w\s]/g, '');
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

export function titleSimilarity(a: string, b: string): number {
  return sequenceRatio(normalizeTitle(a), normalizeTitle(b));
}

function lastNames(authors: string[]): Set<string> {
  const names = new Set<string>();
  for (const a of authors) {
    // Handles both "Smith, Jane" (RIS/BibTeX/Crossref) and "Smith J"
    // (PubMed) shapes — take the first comma-or-space-delimited token.
    const token = a.trim().split(/[,\s]/)[0].toLowerCase();
    if (token) names.add(token);
  }
  return names;
}

export function authorOverlap(a: string[], b: string[]): number {
  const namesA = lastNames(a);
  const namesB = lastNames(b);
  if (namesA.size === 0 || namesB.size === 0) return 0.0;
  let intersectionSize = 0;
  for (const n of namesA) if (namesB.has(n)) intersectionSize++;
  const unionSize = new Set([...namesA, ...namesB]).size;
  return intersectionSize / unionSize;
}

export interface DuplicateMatch {
  keptIndex: number;
  duplicateIndex: number;
  reason: 'exact_doi' | 'fuzzy_title';
  score: number;
}

export interface DedupeResult {
  uniqueRecords: BibRecord[];
  uniqueIndices: number[];
  matches: DuplicateMatch[];
}

export function deduplicate(
  records: BibRecord[],
  titleThreshold = 0.9,
  minAuthorOverlap = 0.5
): DedupeResult {
  const n = records.length;
  const removed = new Array<boolean>(n).fill(false);
  const matches: DuplicateMatch[] = [];

  // --- Pass 1: exact DOI ---
  const doiToFirstIndex = new Map<string, number>();
  for (let i = 0; i < n; i++) {
    const norm = normalizeDoi(records[i].doi);
    if (norm === null) continue;
    if (doiToFirstIndex.has(norm)) {
      const kept = doiToFirstIndex.get(norm)!;
      removed[i] = true;
      matches.push({ keptIndex: kept, duplicateIndex: i, reason: 'exact_doi', score: 1.0 });
    } else {
      doiToFirstIndex.set(norm, i);
    }
  }

  // --- Pass 2: fuzzy title + author, only among survivors of Pass 1 ---
  const survivors: number[] = [];
  for (let i = 0; i < n; i++) if (!removed[i]) survivors.push(i);

  for (let aPos = 0; aPos < survivors.length; aPos++) {
    const i = survivors[aPos];
    if (removed[i]) continue;
    for (let bPos = aPos + 1; bPos < survivors.length; bPos++) {
      const j = survivors[bPos];
      if (removed[j]) continue;
      const score = titleSimilarity(records[i].title, records[j].title);
      if (score < titleThreshold) continue;
      if (minAuthorOverlap > 0.0 && authorOverlap(records[i].authors, records[j].authors) < minAuthorOverlap) {
        continue;
      }
      removed[j] = true;
      matches.push({ keptIndex: i, duplicateIndex: j, reason: 'fuzzy_title', score });
    }
  }

  const uniqueIndices: number[] = [];
  const uniqueRecords: BibRecord[] = [];
  for (let i = 0; i < n; i++) {
    if (!removed[i]) {
      uniqueIndices.push(i);
      uniqueRecords.push(records[i]);
    }
  }

  return { uniqueRecords, uniqueIndices, matches };
}

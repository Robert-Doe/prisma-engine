/**
 * A faithful TypeScript port of Python's difflib.SequenceMatcher, restricted
 * to the subset dedup_engine.py actually relies on: `.ratio()`.
 *
 * This is the Ratcliff/Obershelp algorithm: recursively find the longest
 * contiguous matching block between two strings, then recurse on the
 * left and right remainders, summing matched-character counts. The final
 * ratio is 2 * matches / (len(a) + len(b)), exactly what CPython's
 * difflib computes (autojunk is a no-op here: it only ever kicks in for
 * sequences of 200+ characters, far longer than any paper title).
 */

interface Match {
  a: number;
  b: number;
  size: number;
}

function buildB2J(b: string): Map<string, number[]> {
  const b2j = new Map<string, number[]>();
  for (let j = 0; j < b.length; j++) {
    const ch = b[j];
    const list = b2j.get(ch);
    if (list) list.push(j);
    else b2j.set(ch, [j]);
  }
  return b2j;
}

function findLongestMatch(
  a: string,
  b: string,
  b2j: Map<string, number[]>,
  alo: number,
  ahi: number,
  blo: number,
  bhi: number
): Match {
  let besti = alo;
  let bestj = blo;
  let bestsize = 0;

  let j2len = new Map<number, number>();
  for (let i = alo; i < ahi; i++) {
    const newj2len = new Map<number, number>();
    const indices = b2j.get(a[i]);
    if (indices) {
      for (const j of indices) {
        if (j < blo) continue;
        if (j >= bhi) break;
        const k = (j2len.get(j - 1) ?? 0) + 1;
        newj2len.set(j, k);
        if (k > bestsize) {
          besti = i - k + 1;
          bestj = j - k + 1;
          bestsize = k;
        }
      }
    }
    j2len = newj2len;
  }

  return { a: besti, b: bestj, size: bestsize };
}

function getMatchingBlocks(a: string, b: string): Match[] {
  const b2j = buildB2J(b);
  const queue: [number, number, number, number][] = [[0, a.length, 0, b.length]];
  const matchingBlocks: Match[] = [];

  while (queue.length) {
    const [alo, ahi, blo, bhi] = queue.pop()!;
    const match = findLongestMatch(a, b, b2j, alo, ahi, blo, bhi);
    const { a: i, b: j, size: k } = match;
    if (k > 0) {
      matchingBlocks.push(match);
      if (alo < i && blo < j) queue.push([alo, i, blo, j]);
      if (i + k < ahi && j + k < bhi) queue.push([i + k, ahi, j + k, bhi]);
    }
  }

  matchingBlocks.sort((x, y) => x.a - y.a || x.b - y.b);
  return matchingBlocks;
}

/** Equivalent to Python's `SequenceMatcher(None, a, b).ratio()`. */
export function sequenceRatio(a: string, b: string): number {
  if (a.length === 0 && b.length === 0) return 1.0;
  const blocks = getMatchingBlocks(a, b);
  const matches = blocks.reduce((sum, m) => sum + m.size, 0);
  return (2.0 * matches) / (a.length + b.length);
}

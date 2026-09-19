import './style.css';
import { EXAMPLE_CORPUS, parseCorpus, type BibRecord } from './lib/record';
import { deduplicate, type DedupeResult } from './lib/dedup';
import { PrismaFlowTracker } from './lib/flow';
import { renderPrismaSvg } from './lib/diagram';

const app = document.querySelector<HTMLDivElement>('#app')!;

app.innerHTML = `
  <div class="wrap">
    <div class="topbar">
      <div class="brand">PRISMA<span class="dot">·</span>Engine</div>
      <div class="topnav">
        <a href="https://github.com/Robert-Doe/prisma-engine" target="_blank" rel="noopener">GitHub</a>
        <a href="https://robertdoe.com">&larr; robertdoe.com</a>
      </div>
    </div>

    <div class="hero">
      <h1>Systematic Review <span class="accent">Pipeline</span></h1>
      <p>
        A real, in-browser port of the PRISMA Engine course's core modules: the
        exact-DOI + fuzzy-title deduplication engine (Module 6) and the PRISMA
        flow-diagram generator (Module 12) — same algorithms, same stage names,
        running on whatever bibliographic records you paste in below.
      </p>
    </div>

    <div class="demo">
      <div class="panes">
        <div class="card">
          <h2><span class="step">1</span>Paste your corpus</h2>
          <p class="subtitle">One record per line: <code>Title | Authors (separated by ;) | Year | DOI</code></p>
          <textarea id="corpus-input" spellcheck="false"></textarea>
          <div class="actions">
            <button class="secondary" id="load-example">Load example</button>
            <button class="primary" id="run-dedup">Run Deduplication</button>
          </div>
        </div>

        <div class="card">
          <h2><span class="step">2</span>Deduplication decisions</h2>
          <p class="subtitle">Exact DOI match, then fuzzy title + author-overlap match (threshold 0.90 / 0.50)</p>
          <div class="output" id="dedup-output"><span class="placeholder">Run deduplication to see per-record decisions.</span></div>
        </div>
      </div>

      <div class="card flow-card">
        <h2><span class="step">3</span>Generate PRISMA flow</h2>
        <p class="subtitle">Renders the real PRISMA flow diagram (Module 12) from your deduplicated corpus, with a simulated screening split labeled exactly like the course's own Module 7 demo.</p>
        <div class="actions" style="margin-top:0; margin-bottom:14px;">
          <button class="primary" id="run-flow" disabled>Generate PRISMA Flow</button>
        </div>
        <div id="flow-output"></div>
      </div>
    </div>

    <footer>
      <span>PRISMA Engine — course-companion demo</span>
      <span>Deduplication + PRISMA flow, ported faithfully from the Python source</span>
    </footer>
  </div>
`;

const corpusInput = document.querySelector<HTMLTextAreaElement>('#corpus-input')!;
const loadExampleBtn = document.querySelector<HTMLButtonElement>('#load-example')!;
const runDedupBtn = document.querySelector<HTMLButtonElement>('#run-dedup')!;
const runFlowBtn = document.querySelector<HTMLButtonElement>('#run-flow')!;
const dedupOutput = document.querySelector<HTMLDivElement>('#dedup-output')!;
const flowOutput = document.querySelector<HTMLDivElement>('#flow-output')!;

corpusInput.value = EXAMPLE_CORPUS;

let lastResult: DedupeResult | null = null;
let lastRecords: BibRecord[] = [];

loadExampleBtn.addEventListener('click', () => {
  corpusInput.value = EXAMPLE_CORPUS;
});

runDedupBtn.addEventListener('click', () => {
  const records = parseCorpus(corpusInput.value);
  if (records.length === 0) {
    dedupOutput.innerHTML = '<span class="placeholder">Paste at least one record first.</span>';
    runFlowBtn.disabled = true;
    return;
  }

  const result = deduplicate(records, 0.9, 0.5);
  lastResult = result;
  lastRecords = records;

  if (result.matches.length === 0) {
    dedupOutput.innerHTML =
      '<div class="summary-line">No duplicates found among <strong>' +
      records.length +
      '</strong> records — all considered unique.</div>';
  } else {
    const rows = result.matches
      .map((m) => {
        const badgeClass = m.reason === 'exact_doi' ? 'exact' : 'fuzzy';
        const badgeLabel = m.reason === 'exact_doi' ? 'exact DOI' : 'fuzzy title';
        const dup = records[m.duplicateIndex];
        const kept = records[m.keptIndex];
        return `<div class="match-row">
          <span class="badge ${badgeClass}">${badgeLabel}</span>
          <span>#${m.duplicateIndex} "${escapeHtml(dup.title)}"</span>
          <span class="score">&rarr; duplicate of #${m.keptIndex} "${escapeHtml(kept.title)}" (score ${m.score.toFixed(3)})</span>
        </div>`;
      })
      .join('');
    dedupOutput.innerHTML =
      rows +
      `<div class="summary-line">Started with <strong>${records.length}</strong> records, <strong>${result.uniqueRecords.length}</strong> remain after dedup (<strong>${result.matches.length}</strong> duplicates removed).</div>`;
  }

  runFlowBtn.disabled = false;
  flowOutput.innerHTML = '';
});

runFlowBtn.addEventListener('click', () => {
  if (!lastResult) return;

  const tracker = new PrismaFlowTracker();
  tracker.logIdentification('Pasted corpus', lastRecords.length);
  tracker.logDeduplication(lastRecords.length - lastResult.uniqueRecords.length);

  // Same simulated screening split the course's own Module 7 demo uses
  // (Modules 8-9, the real screening engine, aren't part of this port) —
  // a clearly-labeled synthetic split of the real deduplicated count.
  const n = lastResult.uniqueRecords.length;
  const excludedWrongPopulation = Math.floor(n / 3);
  const excludedWrongDesign = Math.floor(n / 4);
  const included = n - excludedWrongPopulation - excludedWrongDesign;
  tracker.logScreening(
    { 'wrong population': excludedWrongPopulation, 'wrong study design': excludedWrongDesign },
    included
  );

  tracker.validateConservation();

  const svg = renderPrismaSvg(tracker, 'PRISMA Flow — your corpus');

  flowOutput.innerHTML = `
    <div class="stat-row">
      <div class="stat"><span class="value">${tracker.totalIdentified()}</span><span class="label">Identified</span></div>
      <div class="stat"><span class="value">${tracker.duplicatesRemoved}</span><span class="label">Duplicates removed</span></div>
      <div class="stat"><span class="value">${tracker.afterDedup()}</span><span class="label">Screened</span></div>
      <div class="stat"><span class="value">${tracker.screeningIncluded}</span><span class="label">Assessed for eligibility</span></div>
    </div>
    <div class="flow-scroll">${svg}</div>
    <p class="note">Conservation check passed: every stage's outputs sum back to its inputs (<code>validateConservation()</code>, ported from <code>flow_tracker.py</code>). Screening exclusion reasons are a simulated split, exactly as labeled in the course's own Module 7 reference demo.</p>
  `;
});

function escapeHtml(s: string): string {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

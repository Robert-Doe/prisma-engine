/**
 * Port of modules/track1/12_prisma_diagram_generator/diagram_generator.py.
 *
 * Same box geometry constants, same text-wrapping routine, same stage
 * labels ("Records identified from: ...", "Duplicate records removed",
 * "Records screened (title/abstract)", "Records excluded: <reasons>",
 * "Reports assessed for eligibility") and same fill colors as the real
 * generator. This demo only logs identification/dedup/screening (see
 * flow.ts), so it renders the same *partial* diagram the Python
 * generator itself renders when eligibility hasn't been logged yet —
 * that graceful partial-render path is exercised in the original's own
 * self-checks.
 */

import type { PrismaFlowTracker } from './flow';

const BOX_WIDTH = 420;
const SIDE_BOX_WIDTH = 340;
const SIDE_X_OFFSET = 470;
const LINE_HEIGHT = 16;
const BOX_PADDING = 10;
const GAP_BETWEEN_STAGES = 50;

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function wrapText(text: string, maxChars: number): string[] {
  const words = text.split(/\s+/).filter(Boolean);
  const lines: string[] = [];
  let current = '';
  for (const w of words) {
    const trial = `${current} ${w}`.trim();
    if (trial.length > maxChars && current) {
      lines.push(current);
      current = w;
    } else {
      current = trial;
    }
  }
  if (current) lines.push(current);
  return lines.length ? lines : [''];
}

function box(x: number, y: number, width: number, textLines: string[], fill: string): { svg: string; height: number } {
  const height = BOX_PADDING * 2 + LINE_HEIGHT * textLines.length;
  const parts = [
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="${fill}" stroke="#333333" stroke-width="1.5" rx="5"/>`,
  ];
  const textY = y + BOX_PADDING + LINE_HEIGHT * 0.75;
  textLines.forEach((line, i) => {
    parts.push(
      `<text x="${x + width / 2}" y="${textY + i * LINE_HEIGHT}" font-size="12.5" font-family="Arial, sans-serif" text-anchor="middle">${escapeXml(line)}</text>`
    );
  });
  return { svg: parts.join('\n'), height };
}

function arrow(x1: number, y1: number, x2: number, y2: number): string {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#333333" stroke-width="1.5" marker-end="url(#arrowhead)"/>`;
}

export function renderPrismaSvg(tracker: PrismaFlowTracker, title = 'PRISMA Flow Diagram'): string {
  const mainX = 60;
  const sideX = mainX + SIDE_X_OFFSET;
  let y = 50;
  const elements: string[] = [];

  const perSource = [...tracker.identification.entries()].map(([src, count]) => `${src} (n = ${count})`).join('; ');
  const idLines = wrapText(`Records identified from: ${perSource}. Total identified (n = ${tracker.totalIdentified()})`, 55);
  let { svg: boxSvg, height: h } = box(mainX, y, BOX_WIDTH, idLines, '#dbe9f7');
  elements.push(boxSvg);
  const idBottom = y + h;

  if (tracker.duplicatesRemoved) {
    const dupLines = wrapText(`Duplicate records removed (n = ${tracker.duplicatesRemoved})`, 42);
    const dup = box(sideX, y, SIDE_BOX_WIDTH, dupLines, '#f7e3d8');
    elements.push(dup.svg);
    elements.push(arrow(mainX + BOX_WIDTH, y + h / 2, sideX, y + dup.height / 2));
  }

  y = idBottom + GAP_BETWEEN_STAGES;
  elements.push(arrow(mainX + BOX_WIDTH / 2, idBottom, mainX + BOX_WIDTH / 2, y));

  const screenedLines = wrapText(`Records screened (title/abstract) (n = ${tracker.afterDedup()})`, 55);
  ({ svg: boxSvg, height: h } = box(mainX, y, BOX_WIDTH, screenedLines, '#dbe9f7'));
  elements.push(boxSvg);
  const screenedBottom = y + h;

  if (tracker.screeningIncluded !== null) {
    const reasons = [...tracker.screeningExcluded.entries()].map(([reason, count]) => `${reason} (n = ${count})`).join('; ');
    const exclLines = wrapText(`Records excluded (n = ${tracker.totalScreeningExcluded()}): ${reasons}`, 42);
    const excl = box(sideX, y, SIDE_BOX_WIDTH, exclLines, '#f7e3d8');
    elements.push(excl.svg);
    elements.push(arrow(mainX + BOX_WIDTH, y + h / 2, sideX, y + excl.height / 2));

    y = screenedBottom + GAP_BETWEEN_STAGES;
    elements.push(arrow(mainX + BOX_WIDTH / 2, screenedBottom, mainX + BOX_WIDTH / 2, y));

    const eligLines = wrapText(`Reports assessed for eligibility (n = ${tracker.screeningIncluded})`, 55);
    ({ svg: boxSvg, height: h } = box(mainX, y, BOX_WIDTH, eligLines, '#dbe9f7'));
    elements.push(boxSvg);
    y = y + h;
  }

  const totalHeight = y + 40;
  const totalWidth = sideX + SIDE_BOX_WIDTH + 40;

  const svg = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="${totalHeight}" viewBox="0 0 ${totalWidth} ${totalHeight}">`,
    '<defs><marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#333333"/></marker></defs>',
    `<rect x="0" y="0" width="${totalWidth}" height="${totalHeight}" fill="white"/>`,
    `<text x="${totalWidth / 2}" y="25" font-size="16" font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">${escapeXml(title)}</text>`,
  ];
  svg.push(...elements);
  svg.push('</svg>');
  return svg.join('\n');
}

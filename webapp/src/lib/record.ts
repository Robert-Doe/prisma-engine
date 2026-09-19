/**
 * Port of modules/track1/03_bibliographic_record_model/record_model.py's
 * `Record` shape (the fields dedup_engine.py actually consumes) plus a
 * tiny pipe-delimited parser so a visitor can paste a corpus by hand.
 *
 * Input format, one record per line:
 *   Title | Author One; Author Two | Year | DOI
 * Year and DOI are optional trailing fields.
 */

export interface BibRecord {
  title: string;
  authors: string[];
  year: number | null;
  doi: string | null;
}

export function parseCorpus(text: string): BibRecord[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith('#'))
    .map(parseLine);
}

function parseLine(line: string): BibRecord {
  const parts = line.split('|').map((p) => p.trim());
  const [title = '', authorsField = '', yearField = '', doiField = ''] = parts;
  const authors = authorsField
    .split(';')
    .map((a) => a.trim())
    .filter(Boolean);
  const year = /^\d{4}$/.test(yearField) ? Number(yearField) : null;
  const doi = doiField.length > 0 ? doiField : null;
  return { title, authors, year, doi };
}

export const EXAMPLE_CORPUS = `Remote Work and Productivity: A Longitudinal Study | Smith, Jane; Lee, Amrita | 2023 | 10.1037/xyz
Remote Work and Productivity - A Longitudinal Study | Smith J; Lee A | 2023 |
Remote Work and Productivity: A Longitudinal Study | Smith, Jane; Lee, Amrita | 2023 | HTTPS://DOI.ORG/10.1037/XYZ
Remote Work and Employee Wellbeing | Nguyen, Thi; Park, Soo | 2022 | 10.1037/abc
Does Remote Work Affect Productivity? | Okoye, Chidi | 2021 | 10.1037/def
Hybrid Work Arrangements and Team Cohesion | Alvarez, Marco; Kim, Douglas | 2023 | 10.1037/ghi
Hybrid Work Arrangements and Team Cohesion | Alvarez M; Kim D | 2023 |`;

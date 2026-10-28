// Mirrors pipeline/score.py and pipeline/questions.py for commitments loaded from a user's own file.
// data/golden/score.json and data/golden/questions.json keep both implementations identical.
import { readCsv } from "./engine";
import { MAX_TERM_QUESTIONS, QUESTION_TEMPLATES, TERM_TEMPLATE } from "./questionText";
import type { Commitment, Question, Score } from "./types";

export const CHECKS = ["numeric_target", "unit_defined", "dated_deadline", "owner_named", "measurement_source", "terms_defined"] as const;
const NO_NUMBER_NEEDED = ["deliverable", "assessment"];
export const KINDS = ["target", "milestone", "deliverable", "input", "projection", "assessment", "vision"] as const;

/** The fields the score and the questions read. A public Commitment has all of them. */
export type ScoreInput = Pick<
  Commitment,
  "id" | "title" | "title_ar" | "kind" | "owner" | "unit" | "target_number" | "deadline_precision" | "measurement_source" | "undefined_terms"
>;

const round4 = (x: number) => Math.round(x * 1e4) / 1e4;

export function scoreCommitment(c: ScoreInput): Score {
  const numericApplies = !NO_NUMBER_NEEDED.includes(c.kind);
  const checks: Record<string, boolean | null> = {
    numeric_target: numericApplies ? c.target_number !== null : null,
    unit_defined: numericApplies ? c.unit !== null : null,
    dated_deadline: ["day", "month", "year"].includes(c.deadline_precision),
    owner_named: c.owner !== null,
    measurement_source: c.measurement_source !== null,
    terms_defined: c.undefined_terms.length === 0,
  };
  const applicable = CHECKS.map((k) => checks[k]).filter((v) => v !== null);
  const passed = applicable.filter((v) => v).length;
  const ratio = passed / applicable.length;
  const band = ratio >= 0.8 ? "checkable" : ratio >= 0.5 ? "partly-checkable" : "not-yet-checkable";
  return {
    commitment_id: c.id, checks, applicable: applicable.length, passed, ratio: round4(ratio), band,
    missing: CHECKS.filter((k) => checks[k] === false),
  };
}

const fill = (tpl: string, vars: Record<string, string>) => tpl.replace(/\{(\w+)\}/g, (_, k: string) => vars[k] ?? `{${k}}`);

export function questionsFor(c: ScoreInput, s: Score): Question[] {
  const out: Question[] = [];
  for (const check of s.missing) {
    const tpl = QUESTION_TEMPLATES[check];
    if (tpl) out.push({ check, en: fill(tpl[0], { title: c.title }), ar: fill(tpl[1], { title: c.title_ar }) });
  }
  if (s.missing.includes("terms_defined")) {
    for (const term of c.undefined_terms.slice(0, MAX_TERM_QUESTIONS)) {
      out.push({
        check: "terms_defined",
        en: fill(TERM_TEMPLATE[0], { title: c.title, term }),
        ar: fill(TERM_TEMPLATE[1], { title: c.title_ar, term }),
      });
    }
  }
  return out;
}

// ---------------------------------------------------------------- reading a user's file

export const MY_COLUMNS = [
  "id", "title", "owner", "metric", "unit", "target_number", "deadline", "measurement_source", "undefined_terms", "kind",
] as const;
export type MyColumn = (typeof MY_COLUMNS)[number];
export const REQUIRED: MyColumn[] = ["id", "title", "kind"];

export const MY_TEMPLATE =
  MY_COLUMNS.join(",") +
  '\nX01,Move half of services to the new platform,Example Office,services moved,services,50,2027-12-31,Annual service report,"agentic; service",target\n';

const SYNONYMS: Record<MyColumn, string[]> = {
  id: ["id", "code", "ref", "reference", "commitmentid"],
  title: ["title", "name", "commitment", "target", "statement"],
  owner: ["owner", "entity", "responsible", "accountable", "lead"],
  metric: ["metric", "measure", "indicator", "kpi"],
  unit: ["unit", "units", "unitofmeasure"],
  target_number: ["targetnumber", "targetvalue", "value", "number"],
  deadline: ["deadline", "due", "duedate", "date", "by"],
  measurement_source: ["measurementsource", "source", "datasource", "measuredby"],
  undefined_terms: ["undefinedterms", "terms", "undefined", "openterms"],
  kind: ["kind", "type", "category"],
};
const squash = (h: string) => h.toLowerCase().replace(/[^a-z]/g, "");

export type MyMapping = Partial<Record<MyColumn, number>>;

export function mapColumns(headers: string[]): MyMapping {
  const m: MyMapping = {};
  const used = new Set<number>();
  for (const col of MY_COLUMNS) {
    const exact = headers.findIndex((h, i) => !used.has(i) && h.toLowerCase().trim() === col);
    const idx = exact >= 0 ? exact : headers.findIndex((h, i) => !used.has(i) && SYNONYMS[col].includes(squash(h)));
    if (idx >= 0) { m[col] = idx; used.add(idx); }
  }
  return m;
}

const MONTHS = "jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?";
const MONTH_ABBR = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
const DIGITS = "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹";
/** Arabic-Indic and Persian digits become ASCII digits. Other scripts are left alone and so are not numbers. */
const asciiDigits = (s: string) => s.replace(/[٠-٩۰-۹]/g, (d) => String(DIGITS.indexOf(d) % 10));

const isLeap = (y: number) => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
const daysIn = (y: number, m: number) => (m === 2 ? (isLeap(y) ? 29 : 28) : [4, 6, 9, 11].includes(m) ? 30 : 31);
const realDate = (y: number, m: number, d: number) => y >= 1 && y <= 9999 && m >= 1 && m <= 12 && d >= 1 && d <= daysIn(y, m);
const validDay = (a: number, b: number, y: number) => realDate(y, b, a) || realDate(y, a, b);

function namedDay(s: string): boolean {
  let m = s.match(new RegExp(`^(\\d{1,2})\\s+(${MONTHS})\\.?,?\\s+(\\d{4})$`, "i"));
  if (m) return realDate(+m[3], MONTH_ABBR.indexOf(m[2].slice(0, 3).toLowerCase()) + 1, +m[1]);
  m = s.match(new RegExp(`^(${MONTHS})\\.?\\s+(\\d{1,2}),?\\s+(\\d{4})$`, "i"));
  return !!m && realDate(+m[3], MONTH_ABBR.indexOf(m[1].slice(0, 3).toLowerCase()) + 1, +m[2]);
}

/** How precisely a deadline is dated: a real calendar date is a day, a month or quarter a month, a year a year. Else relative. */
export function deadlinePrecision(v: string): Commitment["deadline_precision"] {
  const s = asciiDigits(v).trim().replace(/\s+/g, " ");
  if (!s) return "none";
  let m: RegExpMatchArray | null;
  if ((m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/))) return realDate(+m[1], +m[2], +m[3]) ? "day" : "relative";
  if ((m = s.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$/))) return validDay(+m[1], +m[2], +m[3]) ? "day" : "relative";
  if ((m = s.match(/^(\d{4})[/.](\d{1,2})[/.](\d{1,2})$/))) return realDate(+m[1], +m[2], +m[3]) ? "day" : "relative";
  if (new RegExp(`^\\d{1,2}\\s+(?:${MONTHS})\\.?,?\\s+\\d{4}$`, "i").test(s) || new RegExp(`^(?:${MONTHS})\\.?\\s+\\d{1,2},?\\s+\\d{4}$`, "i").test(s)) {
    return namedDay(s) ? "day" : "relative";
  }
  if ((m = s.match(/^(\d{4})-(\d{2})$/))) return +m[2] >= 1 && +m[2] <= 12 ? "month" : "relative";
  if ((m = s.match(/^(\d{1,2})[/-](\d{4})$/))) return +m[1] >= 1 && +m[1] <= 12 ? "month" : "relative";
  if (new RegExp(`^(?:${MONTHS})\\.?\\s+\\d{4}$`, "i").test(s)) return "month";
  if (/^(?:q[1-4]\s*[-/ ]?\s*\d{4}|\d{4}\s*[-/ ]?\s*q[1-4])$/i.test(s)) return "month";
  if (/^(?:(?:by|before|until)\s+)?(?:(?:the\s+)?end\s+of\s+)?\d{4}$/i.test(s)) return "year";
  return "relative";
}

/** A plain number. Thousands commas, spaces and a trailing percent sign are ignored. Null when empty, NaN when invalid. */
export function parseNumber(raw: string): number | null {
  let s = asciiDigits(raw).trim().replace(/[, ]/g, "");
  if (s.endsWith("%")) s = s.slice(0, -1);
  if (s === "") return null;
  const n = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(s) ? Number(s) : Number.NaN;
  return Number.isFinite(n) ? n : Number.NaN;
}

export type MyCommitment = ScoreInput & { metric: string | null; deadline: string | null; row: number };
export type MyReport = { rows: number; accepted: number; rejected: number; duplicates: number; unmapped: MyColumn[]; truncated: boolean };
export type MyResult = { items: MyCommitment[]; errors: string[]; report: MyReport; headers: string[]; mapping: MyMapping };

const orNull = (s: string) => (s.trim() === "" ? null : s.trim());

export function convertRows(headers: string[], rows: string[][], mapping: MyMapping, truncated = false): MyResult {
  const unmapped = MY_COLUMNS.filter((c) => mapping[c] === undefined);
  const report: MyReport = { rows: rows.length, accepted: 0, rejected: 0, duplicates: 0, unmapped, truncated };
  if (rows.length === 0) return { items: [], errors: ["The file needs at least one commitment."], report, headers, mapping };
  const missingRequired = REQUIRED.filter((c) => mapping[c] === undefined);
  if (missingRequired.length) {
    return { items: [], errors: [`Missing columns: ${missingRequired.join(", ")}.`], report, headers, mapping };
  }
  const items: MyCommitment[] = [];
  const errors: string[] = [];
  const seen = new Set<string>();
  rows.forEach((f, n) => {
    const row = n + 2;
    const get = (c: MyColumn) => (mapping[c] === undefined ? "" : f[mapping[c] as number] ?? "");
    const bad: string[] = [];
    const id = get("id").trim();
    const kind = get("kind").trim().toLowerCase();
    const num = parseNumber(get("target_number"));
    if (!id) bad.push("id is empty");
    if (seen.has(id)) { bad.push("duplicate id"); report.duplicates++; }
    if (!get("title").trim()) bad.push("title is empty");
    if (!(KINDS as readonly string[]).includes(kind)) bad.push(`kind must be one of ${KINDS.join(", ")}`);
    if (Number.isNaN(num)) bad.push("target_number must be a number or empty");
    if (bad.length) { errors.push(`Row ${row}: ${bad.join("; ")}.`); return; }
    seen.add(id);
    const title = get("title").trim();
    items.push({
      id, title, title_ar: title, kind: kind as Commitment["kind"], row,
      owner: orNull(get("owner")), metric: orNull(get("metric")), unit: orNull(get("unit")),
      target_number: num,
      deadline: orNull(get("deadline")), deadline_precision: deadlinePrecision(get("deadline")),
      measurement_source: orNull(get("measurement_source")),
      undefined_terms: get("undefined_terms").split(/[;|]/).map((s) => s.trim()).filter(Boolean),
    });
  });
  report.accepted = items.length;
  report.rejected = rows.length - items.length;
  return { items, errors, report, headers, mapping };
}

/** Read a CSV or a JSON array of objects into headers and rows. Throws a readable error on bad JSON. */
export function readMyFile(name: string, text: string): { headers: string[]; rows: string[][]; truncated: boolean } {
  const looksJson = name.toLowerCase().endsWith(".json") || /^\s*[[{]/.test(text.replace(/^\uFEFF/, ""));
  if (!looksJson) return readCsv(text);
  let parsed: unknown;
  try { parsed = JSON.parse(text.replace(/^\uFEFF/, "")); } catch { throw new Error("The file is not valid JSON."); }
  const list = Array.isArray(parsed) ? parsed : parsed !== null && typeof parsed === "object" ? (parsed as { commitments?: unknown }).commitments : undefined;
  if (!Array.isArray(list)) throw new Error("JSON must be an array of commitments, or an object with a commitments array.");
  const headers = [...new Set(list.flatMap((o) => (o && typeof o === "object" ? Object.keys(o as object) : [])))];
  const cell = (v: unknown): string =>
    v === null || v === undefined ? "" : Array.isArray(v) ? v.map(cell).join("; ") : typeof v === "object" ? "" : String(v);
  return { headers, rows: list.map((o) => headers.map((h) => (o && typeof o === "object" ? cell((o as Record<string, unknown>)[h]) : ""))), truncated: false };
}

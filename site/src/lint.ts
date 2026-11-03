// Mirrors pipeline/lint.py. data/config/lint_rules.json holds the rules, and the golden files
// data/golden/lint_inputs.json and data/golden/lint_outputs.json keep both implementations identical.
import rulesJson from "../../data/config/lint_rules.json";
import { deadlinePrecision, questionsFor, scoreCommitment } from "./commitments";
import type { Question, Score } from "./types";

type Rules = {
  units: Record<string, string[]>;
  magnitudes: Record<string, number>;
  percent_words: string[];
  half_words: string[];
  month_names: string;
  relative_cues: string[];
  owner_patterns: string[];
  measure_cues: string[];
  definition_cues: string[];
  vague_terms: { term: string; patterns: string[] }[];
};
const R = rulesJson as unknown as Rules;

export const MAX_TEXT = 4000;
export const SLOTS: Record<string, string> = {
  numeric_target: "target_number",
  unit_defined: "unit",
  dated_deadline: "deadline",
  owner_named: "owner",
  measurement_source: "measurement_source",
  terms_defined: "defined_terms",
};

const DIGITS = "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹";
const ASCII = "01234567890123456789";

export function normalise(text: string): string {
  let t = text.slice(0, MAX_TEXT);
  t = [...t].map((ch) => { const i = DIGITS.indexOf(ch); return i >= 0 ? ASCII[i] : ch; }).join("");
  t = t.replace(/٪/g, "%").replace(/٫/g, ".").replace(/٬/g, ",");
  return t.trim().split(/\s+/).filter((x) => x !== "").join(" ");
}

export function shortTitle(t: string): string {
  if (t.length <= 80) return t;
  const cut = t.slice(0, 80);
  const i = cut.lastIndexOf(" ");
  return (i < 0 ? cut : cut.slice(0, i)) + "…";
}

const ci = (p: string, flags = "") => new RegExp(p, "i" + flags);
const alt = (list: string[]) => ci(list.map((p) => `(?:${p})`).join("|"));
const escapeRe = (w: string) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

export type Parsed = {
  target_number: number | null; unit: string | null; deadline_text: string | null; deadline_precision: string;
  owner: string | null; measurement_source: string | null; undefined_terms: string[];
};

const START_WORDS = /(?:since|from|after|announced|dated|following|as of|of the)\s*$/i;

type Span = [number, number, string];

function datePhrases(n: string): Span[] {
  const m = R.month_names;
  const pats = [
    "\\d{4}-\\d{2}-\\d{2}",
    `\\d{1,2} (?:${m})\\.?,? \\d{4}`,
    `(?:${m})\\.? \\d{1,2},? \\d{4}`,
    `(?:${m})\\.?,? \\d{4}`,
    "q[1-4] \\d{4}",
    "(?<![\\d.,])(?:19|20)\\d{2}(?![\\d%])",
  ];
  const taken: Span[] = [];
  for (const p of pats) {
    for (const mt of n.matchAll(ci(p, "g"))) {
      const s = mt.index!, e = s + mt[0].length;
      if (taken.some(([a, b]) => s < b && a < e)) continue;
      taken.push([s, e, mt[0]]);
    }
  }
  return taken.sort((x, y) => x[0] - y[0] || x[1] - y[1] || (x[2] < y[2] ? -1 : x[2] > y[2] ? 1 : 0));
}

const yearOf = (phrase: string): number => {
  const ys = phrase.match(/(?:19|20)\d{2}/g);
  return ys ? Number(ys[ys.length - 1]) : 0;
};
const PREC_RANK: Record<string, number> = { day: 3, month: 2, year: 1 };

function firstNumber(rest: string): { value: number | null; start: number; end: number; kind: string } {
  let best: { start: number; value: number; end: number; kind: string } | null = null;
  const pw = R.percent_words.map(escapeRe).join("|");
  let mt = ci(`(\\d+(?:\\.\\d+)?)\\s*(?:${pw})`).exec(rest);
  if (mt) best = { start: mt.index, value: parseFloat(mt[1]), end: mt.index + mt[0].length, kind: "percent" };
  const hw = R.half_words.map(escapeRe).join("|");
  mt = ci(`(?<![a-z])(?:${hw})(?![a-z])`).exec(rest);
  if (mt && (best === null || mt.index < best.start)) best = { start: mt.index, value: 50, end: mt.index + mt[0].length, kind: "percent" };
  const mags = R.magnitudes;
  const mg = Object.keys(mags).sort((a, b) => b.length - a.length).map(escapeRe).join("|");
  const re = ci(`(?<![\\d.,a-z])(\\d[\\d,]*(?:\\.\\d+)?)(?:\\s*(${mg})(?![a-z]))?`, "g");
  for (const m2 of rest.matchAll(re)) {
    const raw = m2[1].replace(/,+$/, "").replace(/,/g, "");
    let v = parseFloat(raw);
    if (Number.isNaN(v)) continue;
    if (m2[2]) v *= mags[m2[2].toLowerCase()];
    if (best === null || m2.index! < best.start) best = { start: m2.index!, value: v, end: m2.index! + m2[0].length, kind: "amount" };
    break;
  }
  return best ? { value: best.value, start: best.start, end: best.end, kind: best.kind } : { value: null, start: 0, end: 0, kind: "" };
}

function findUnit(rest: string, start: number, end: number): string | null {
  const cur = ci("(aed|usd|\\$|dh|درهم)\\s*$").exec(rest.slice(0, start));
  if (cur) return ["usd", "$"].includes(cur[1].toLowerCase()) ? "usd" : "aed";
  const after = rest.slice(end, end + 80);
  let best: [number, number, string] | null = null;
  Object.entries(R.units).forEach(([unit, words], order) => {
    const m = ci("(?<![a-z0-9])(?:" + words.join("|") + ")(?![a-z0-9])").exec(after);
    if (m && (best === null || m.index < best[0] || (m.index === best[0] && order < best[1]))) best = [m.index, order, unit];
  });
  return best ? (best as [number, number, string])[2] : null;
}

export function parse(text: string): Parsed {
  const n = normalise(text);
  const out: Parsed = {
    target_number: null, unit: null, deadline_text: null, deadline_precision: "none",
    owner: null, measurement_source: null, undefined_terms: [],
  };
  const all = datePhrases(n);
  const dates = all.filter((d) => !START_WORDS.test(n.slice(Math.max(0, d[0] - 14), d[0])));
  let pick: [number, number, string] | null = null;
  for (const [, , ph] of dates) {
    const prec = deadlinePrecision(ph);
    if (!(prec in PREC_RANK)) continue;
    const key: [number, number] = [yearOf(ph), PREC_RANK[prec]];
    if (pick === null || key[0] > pick[0] || (key[0] === pick[0] && key[1] > pick[1])) pick = [key[0], key[1], ph];
  }
  if (pick) {
    out.deadline_text = pick[2];
    out.deadline_precision = deadlinePrecision(pick[2]);
  } else {
    const rel = alt(R.relative_cues).exec(n.toLowerCase());
    if (rel) { out.deadline_text = rel[0].replace(/^[ .,;:]+|[ .,;:]+$/g, ""); out.deadline_precision = "relative"; }
  }
  const chars = [...n];
  for (const [s, e] of all) for (let i = s; i < e; i++) chars[i] = " ";
  const rest = chars.join("");
  const num = firstNumber(rest);
  out.target_number = num.value;
  if (num.value !== null) out.unit = findUnit(rest, num.start, num.end);
  let best: [number, number, string] | null = null;
  R.owner_patterns.forEach((p, order) => {
    const m = new RegExp(p).exec(n);
    if (m && (best === null || m.index < best[0] || (m.index === best[0] && order < best[1]))) best = [m.index, order, m[0].trim()];
  });
  out.owner = best ? (best as [number, number, string])[2] : null;
  const low = n.toLowerCase();
  const m2 = alt(R.measure_cues).exec(low);
  out.measurement_source = m2 ? m2[0].trim() : null;
  if (!alt(R.definition_cues).test(low)) {
    for (const v of R.vague_terms) {
      if (ci("(?<![a-z])(?:" + v.patterns.join("|") + ")(?![a-z])").test(low)) out.undefined_terms.push(v.term);
    }
  }
  return out;
}

export type LintFields = {
  target_number?: number | null; unit?: string | null; deadline?: string | null; owner?: string | null;
  measurement_source?: string | null; defined_terms?: string[] | null;
};
export type LintQuestion = Question & { slot: string };
export type LintScore = Pick<Score, "checks" | "applicable" | "passed" | "ratio" | "band" | "missing">;
export type LintFound = {
  target_number: number | null; unit: string | null; deadline_text: string | null; deadline_precision: string;
  owner: string | null; measurement_source: string | null; undefined_terms: string[];
};
export type LintResult = {
  kind: string; text: string; found: LintFound; before: LintScore; questions: LintQuestion[];
  after: LintScore | null; after_found: LintFound | null;
};

const rowFor = (title: string, kind: string, p: Parsed) => ({
  id: "LINT", title, title_ar: title, kind: kind as never, owner: p.owner, unit: p.unit, target_number: p.target_number,
  deadline_precision: p.deadline_precision as never, measurement_source: p.measurement_source, undefined_terms: p.undefined_terms,
});
const resultOf = (row: ReturnType<typeof rowFor>): LintScore => {
  const s = scoreCommitment(row as never);
  return { checks: s.checks, applicable: s.applicable, passed: s.passed, ratio: s.ratio, band: s.band, missing: s.missing };
};
const foundOf = (p: Parsed): LintFound => ({
  target_number: p.target_number, unit: p.unit, deadline_text: p.deadline_text, deadline_precision: p.deadline_precision,
  owner: p.owner, measurement_source: p.measurement_source, undefined_terms: p.undefined_terms,
});
const present = (v: unknown) => !(v === null || v === undefined || v === "" || (Array.isArray(v) && v.length === 0));

export function lint(text: string, kind = "target", fields: LintFields | null = null): LintResult {
  const n = normalise(text);
  const p = parse(text);
  const title = shortTitle(n);
  const beforeRow = rowFor(title, kind, p);
  const before = resultOf(beforeRow);
  const sc = scoreCommitment(beforeRow as never);
  const questions = questionsFor(beforeRow as never, sc).map((q) => ({ ...q, slot: SLOTS[q.check] }));
  const out: LintResult = { kind, text: n, found: foundOf(p), before, questions, after: null, after_found: null };
  const f = Object.fromEntries(Object.entries(fields ?? {}).filter(([, v]) => present(v))) as LintFields;
  if (Object.keys(f).length) {
    const a: Parsed = { ...p, undefined_terms: [...p.undefined_terms] };
    if ("target_number" in f) a.target_number = Number(f.target_number);
    if ("unit" in f) a.unit = String(f.unit).trim() || a.unit;
    if ("deadline" in f) { a.deadline_text = String(f.deadline).trim(); a.deadline_precision = deadlinePrecision(a.deadline_text); }
    if ("owner" in f) a.owner = String(f.owner).trim() || a.owner;
    if ("measurement_source" in f) a.measurement_source = String(f.measurement_source).trim() || a.measurement_source;
    if ("defined_terms" in f) {
      const done = new Set((f.defined_terms ?? []).map((t) => String(t).trim().toLowerCase()));
      a.undefined_terms = a.undefined_terms.filter((t) => !done.has(t.toLowerCase()));
    }
    out.after = resultOf(rowFor(title, kind, a));
    out.after_found = foundOf(a);
  }
  return out;
}

// Mirrors pipeline/sensitivity.py. A golden file (data/golden/sensitivity.json) keeps both identical.
import type { Definition, Item } from "./types";

export const SECTOR_SHARE_REQUIRED = 0.5;
export const UNITS = ["services", "transactions", "entities", "sectors"] as const;
export const SCOPES = ["citizen-services", "all-services", "services-and-operations"] as const;
export const THRESHOLDS = [2, 3, 4] as const;
export const GUARDRAILS = ["none", "required"] as const;

export function inScope(it: Item, scope: Definition["scope"]): boolean {
  if (scope === "citizen-services") return it.kind === "service" && it.audience === "citizen";
  if (scope === "all-services") return it.kind === "service";
  return true;
}

export function qualifies(it: Item, threshold: number, guardrails: Definition["guardrails"]): boolean {
  if (it.maturity < threshold) return false;
  if (guardrails === "required") return it.oversight && it.audit_trail && it.uae_residency && it.fallback;
  return true;
}

export function share(items: Item[], d: Definition): number | null {
  const scoped = items.filter((i) => inScope(i, d.scope));
  if (scoped.length === 0) return null;
  if (d.unit === "services") {
    return scoped.filter((i) => qualifies(i, d.threshold, d.guardrails)).length / scoped.length;
  }
  if (d.unit === "transactions") {
    const total = scoped.reduce((a, i) => a + i.annual_transactions, 0);
    if (total === 0) return null;
    const ok = scoped.filter((i) => qualifies(i, d.threshold, d.guardrails));
    return ok.reduce((a, i) => a + i.annual_transactions, 0) / total;
  }
  const groups = new Map<string, Item[]>();
  for (const i of scoped) {
    const k = d.unit === "entities" ? i.entity_id : i.sector;
    groups.set(k, [...(groups.get(k) ?? []), i]);
  }
  let ok = 0;
  for (const g of groups.values()) {
    const q = g.filter((i) => qualifies(i, d.threshold, d.guardrails)).length;
    if (q / g.length >= SECTOR_SHARE_REQUIRED) ok += 1;
  }
  return ok / groups.size;
}

export function allDefinitions(): Definition[] {
  const out: Definition[] = [];
  for (const unit of UNITS)
    for (const scope of SCOPES)
      for (const threshold of THRESHOLDS)
        for (const guardrails of GUARDRAILS) out.push({ unit, scope, threshold, guardrails });
  return out;
}

export function round6(x: number | null): number | null {
  return x === null ? null : Math.round(x * 1e6) / 1e6;
}

export function sweep(items: Item[]) {
  return allDefinitions().map((d) => ({ ...d, share: round6(share(items, d)) }));
}

// ---------------------------------------------------------------- CSV

export const CSV_COLUMNS = [
  "id", "entity", "sector", "kind", "audience", "annual_transactions", "maturity",
  "oversight", "audit_trail", "uae_residency", "fallback",
] as const;
export type CsvColumn = (typeof CSV_COLUMNS)[number];

export const CSV_TEMPLATE =
  CSV_COLUMNS.join(",") + "\nexample-1,Example Entity,Health,service,citizen,12000,2,true,true,true,false\n";

export const MAX_CSV_ROWS = 200_000;

function splitLine(line: string): string[] {
  const out: string[] = [];
  let cur = "";
  let q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') q = false;
      else cur += c;
    } else if (c === '"') q = true;
    else if (c === ",") { out.push(cur); cur = ""; }
    else cur += c;
  }
  out.push(cur);
  return out.map((s) => s.trim());
}

const BOOL = (v: string): boolean | null => {
  const s = v.toLowerCase();
  if (["true", "yes", "1", "y"].includes(s)) return true;
  if (["false", "no", "0", "n"].includes(s)) return false;
  return null;
};

/** Words that commonly stand for each required column. Matched after lowercasing and stripping non-letters. */
const SYNONYMS: Record<CsvColumn, string[]> = {
  id: ["id", "serviceid", "code", "reference", "ref"],
  entity: ["entity", "department", "authority", "organisation", "organization", "agency", "owner"],
  sector: ["sector", "domain", "cluster"],
  kind: ["kind", "type", "category"],
  audience: ["audience", "customer", "user", "segment"],
  annual_transactions: ["annualtransactions", "transactions", "volume", "annualvolume", "requests"],
  maturity: ["maturity", "level", "automationlevel", "autonomy"],
  oversight: ["oversight", "humanoversight", "humanreview"],
  audit_trail: ["audittrail", "audit", "logging"],
  uae_residency: ["uaeresidency", "residency", "dataresidency", "sovereign"],
  fallback: ["fallback", "humanfallback", "manualfallback"],
};

const squash = (h: string) => h.toLowerCase().replace(/[^a-z]/g, "");

export type Mapping = Partial<Record<CsvColumn, number>>;

export function readCsv(text: string): { headers: string[]; rows: string[][]; truncated: boolean } {
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter((l) => l.trim() !== "");
  if (lines.length === 0) return { headers: [], rows: [], truncated: false };
  const truncated = lines.length - 1 > MAX_CSV_ROWS;
  return {
    headers: splitLine(lines[0]),
    rows: lines.slice(1, MAX_CSV_ROWS + 1).map(splitLine),
    truncated,
  };
}

export function autoMap(headers: string[]): Mapping {
  const m: Mapping = {};
  const used = new Set<number>();
  for (const col of CSV_COLUMNS) {
    const exact = headers.findIndex((h, i) => !used.has(i) && h.toLowerCase().trim() === col);
    const idx = exact >= 0 ? exact : headers.findIndex((h, i) => !used.has(i) && SYNONYMS[col].includes(squash(h)));
    if (idx >= 0) { m[col] = idx; used.add(idx); }
  }
  return m;
}

export type QualityReport = {
  rows: number;
  accepted: number;
  rejected: number;
  duplicates: number;
  zeroTransactionShare: number;
  citizenShare: number;
  entities: number;
  sectors: number;
  truncated: boolean;
  unmapped: CsvColumn[];
};

export type CsvResult = { items: Item[]; errors: string[]; report: QualityReport; headers: string[]; mapping: Mapping };

export function convert(headers: string[], rows: string[][], mapping: Mapping, truncated = false): CsvResult {
  const unmapped = CSV_COLUMNS.filter((c) => mapping[c] === undefined);
  const empty: QualityReport = {
    rows: rows.length, accepted: 0, rejected: 0, duplicates: 0, zeroTransactionShare: 0, citizenShare: 0,
    entities: 0, sectors: 0, truncated, unmapped,
  };
  if (rows.length === 0) {
    return { items: [], errors: ["The file needs a header row and at least one data row."], report: empty, headers, mapping };
  }
  if (unmapped.length) {
    return { items: [], errors: [`Missing columns: ${unmapped.join(", ")}.`], report: empty, headers, mapping };
  }
  const items: Item[] = [];
  const errors: string[] = [];
  const seen = new Set<string>();
  let duplicates = 0;
  rows.forEach((f, n) => {
    const row = n + 2;
    const get = (c: CsvColumn) => f[mapping[c] as number] ?? "";
    const kind = get("kind").toLowerCase();
    const audience = get("audience").toLowerCase();
    const mat = Number(get("maturity"));
    const tx = Number(get("annual_transactions"));
    const flags = (["oversight", "audit_trail", "uae_residency", "fallback"] as const).map((c) => BOOL(get(c)));
    const bad: string[] = [];
    if (!get("id")) bad.push("id is empty");
    if (seen.has(get("id"))) { bad.push("duplicate id"); duplicates++; }
    if (kind !== "service" && kind !== "operation") bad.push("kind must be service or operation");
    if (!["citizen", "business", "internal"].includes(audience)) bad.push("audience must be citizen, business or internal");
    if (kind === "operation" && audience !== "internal") bad.push("operations must be internal");
    if (kind === "service" && audience === "internal") bad.push("services must be citizen or business");
    if (!Number.isInteger(mat) || mat < 0 || mat > 4) bad.push("maturity must be 0 to 4");
    if (!Number.isFinite(tx) || tx < 0) bad.push("annual_transactions must be 0 or more");
    if (flags.some((x) => x === null)) bad.push("flags must be true or false");
    if (bad.length) { errors.push(`Row ${row}: ${bad.join("; ")}.`); return; }
    seen.add(get("id"));
    items.push({
      id: get("id"), entity_id: get("entity") || "unnamed", sector: get("sector") || "unspecified",
      kind: kind as Item["kind"], audience: audience as Item["audience"], name: get("id"),
      annual_transactions: tx, maturity: mat as Item["maturity"],
      oversight: flags[0] as boolean, audit_trail: flags[1] as boolean,
      uae_residency: flags[2] as boolean, fallback: flags[3] as boolean,
    });
  });
  const n = Math.max(1, items.length);
  const report: QualityReport = {
    rows: rows.length, accepted: items.length, rejected: rows.length - items.length, duplicates,
    zeroTransactionShare: items.filter((i) => i.annual_transactions === 0).length / n,
    citizenShare: items.filter((i) => i.audience === "citizen").length / n,
    entities: new Set(items.map((i) => i.entity_id)).size,
    sectors: new Set(items.map((i) => i.sector)).size,
    truncated, unmapped,
  };
  return { items, errors, report, headers, mapping };
}

export function parseCsv(text: string, mapping?: Mapping): CsvResult {
  const { headers, rows, truncated } = readCsv(text);
  return convert(headers, rows, mapping ?? autoMap(headers), truncated);
}

/** Quote a value for CSV and neutralise spreadsheet formula injection (leading = + - @ tab or CR). */
export function csvCell(v: unknown): string {
  let s = String(v ?? "");
  if (/^[=+\-@\t\r]/.test(s)) s = `'${s}`;
  return `"${s.replace(/"/g, '""')}"`;
}

export type PortfolioCol = { threshold: (typeof THRESHOLDS)[number]; guardrails: Definition["guardrails"] };
export const PORTFOLIO_COLS: PortfolioCol[] = THRESHOLDS.flatMap((threshold) => GUARDRAILS.map((guardrails) => ({ threshold, guardrails })));
export type PortfolioRow = {
  entity: string; sector: string; items: number; shares: (number | null)[]; ranks: (number | null)[];
  rankMin: number | null; rankMax: number | null;
};

/** Per-entity share of in-scope items that qualify, under six definitions, with the rank under each. */
export function portfolio(items: Item[], scope: Definition["scope"]): PortfolioRow[] {
  const by = new Map<string, Item[]>();
  for (const it of items) if (inScope(it, scope)) by.set(it.entity_id, [...(by.get(it.entity_id) ?? []), it]);
  const rows: PortfolioRow[] = [...by.entries()].map(([entity, list]) => ({
    entity, sector: list[0].sector, items: list.length,
    shares: PORTFOLIO_COLS.map((c) => list.filter((i) => qualifies(i, c.threshold, c.guardrails)).length / list.length),
    ranks: [], rankMin: null, rankMax: null,
  }));
  PORTFOLIO_COLS.forEach((_, ci) => {
    const order = [...rows].sort((a, b) => (b.shares[ci] as number) - (a.shares[ci] as number));
    // ties share the best rank so equal shares are never ordered arbitrarily
    for (const r of order) r.ranks[ci] = order.findIndex((o) => o.shares[ci] === r.shares[ci]) + 1;
  });
  for (const r of rows) {
    const rk = r.ranks as number[];
    r.rankMin = Math.min(...rk); r.rankMax = Math.max(...rk);
  }
  return rows.sort((a, b) => a.entity.localeCompare(b.entity));
}

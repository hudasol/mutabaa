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

export const CSV_TEMPLATE =
  CSV_COLUMNS.join(",") + "\nexample-1,Example Entity,Health,service,citizen,12000,2,true,true,true,false\n";

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

export type CsvResult = { items: Item[]; errors: string[] };

export function parseCsv(text: string): CsvResult {
  const lines = text.replace(/^﻿/, "").split(/\r?\n/).filter((l) => l.trim() !== "");
  const errors: string[] = [];
  if (lines.length < 2) return { items: [], errors: ["The file needs a header row and at least one data row."] };
  const header = splitLine(lines[0]).map((h) => h.toLowerCase());
  const missing = CSV_COLUMNS.filter((c) => !header.includes(c));
  if (missing.length) return { items: [], errors: [`Missing columns: ${missing.join(", ")}.`] };
  const idx = (c: string) => header.indexOf(c);
  const items: Item[] = [];
  const seen = new Set<string>();
  lines.slice(1).forEach((line, n) => {
    const row = n + 2;
    const f = splitLine(line);
    const get = (c: string) => f[idx(c)] ?? "";
    const kind = get("kind");
    const audience = get("audience");
    const mat = Number(get("maturity"));
    const tx = Number(get("annual_transactions"));
    const flags = ["oversight", "audit_trail", "uae_residency", "fallback"].map((c) => BOOL(get(c)));
    const bad: string[] = [];
    if (!get("id")) bad.push("id is empty");
    if (seen.has(get("id"))) bad.push("duplicate id");
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
  return { items, errors };
}

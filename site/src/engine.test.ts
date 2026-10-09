import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parseCsv, sweep, allDefinitions, CSV_TEMPLATE, share } from "./engine";
import type { Registry } from "./types";

const root = resolve(__dirname, "../..");
const registry: Registry = JSON.parse(readFileSync(resolve(root, "data/synthetic/registry.json"), "utf8"));
const golden = JSON.parse(readFileSync(resolve(root, "data/golden/sensitivity.json"), "utf8"));

describe("engine parity with the Python reference", () => {
  it("has 72 definitions", () => expect(allDefinitions()).toHaveLength(72));
  it("matches the golden file on every definition", () => {
    expect(sweep(registry.items)).toEqual(golden);
  });
});

describe("share", () => {
  it("is null for an empty scope", () => {
    expect(share([], { unit: "services", scope: "all-services", threshold: 2, guardrails: "none" })).toBeNull();
  });
});

describe("csv", () => {
  it("accepts the template", () => {
    const r = parseCsv(CSV_TEMPLATE);
    expect(r.errors).toEqual([]);
    expect(r.items).toHaveLength(1);
  });
  it("reports a missing column", () => {
    expect(parseCsv("id,kind\na,service").errors[0]).toMatch(/Missing columns/);
  });
  it("reports row-level problems with the row number", () => {
    const bad = CSV_TEMPLATE + "x,E,H,operation,citizen,5,9,maybe,true,true,true\n";
    const r = parseCsv(bad);
    expect(r.errors[0]).toMatch(/^Row 3:/);
    expect(r.errors[0]).toMatch(/maturity/);
    expect(r.items).toHaveLength(1);
  });
  it("handles quoted commas", () => {
    const r = parseCsv(CSV_TEMPLATE.replace("Example Entity", '"Entity, with comma"'));
    expect(r.items[0].entity_id).toBe("Entity, with comma");
  });
});

import { csvCell } from "./engine";
describe("csvCell", () => {
  it("quotes and escapes", () => expect(csvCell('a"b')).toBe('"a""b"'));
  it("neutralises formulas", () => {
    for (const bad of ["=1+1", "+cmd", "-2+3", "@SUM(A1)"]) expect(csvCell(bad)).toBe(`"'${bad}"`);
  });
  it("keeps plain numbers and null", () => { expect(csvCell(0.5)).toBe('"0.5"'); expect(csvCell(null)).toBe('""'); });
});

import { MAX_CSV_ROWS, readCsv } from "./engine";
describe("csv size cap", () => {
  it("flags truncation and keeps only the cap", () => {
    const text = "a,b\n" + Array.from({ length: MAX_CSV_ROWS + 5 }, () => "1,2").join("\n");
    const r = readCsv(text);
    expect(r.truncated).toBe(true);
    expect(r.rows).toHaveLength(MAX_CSV_ROWS);
  });
  it("does not flag a small file", () => expect(readCsv("a,b\n1,2").truncated).toBe(false));
});

import { PORTFOLIO_COLS, portfolio } from "./engine";
describe("portfolio", () => {
  const mk = (e: string, m: 0 | 1 | 2 | 3 | 4, n = 4) => Array.from({ length: n }, (_, i) => ({
    id: `${e}${i}`, entity_id: e, sector: "Health", kind: "service" as const, audience: "citizen" as const, name: "x",
    annual_transactions: 1, maturity: m, oversight: true, audit_trail: true, uae_residency: true, fallback: i === 0,
  }));
  const rows = portfolio([...mk("A", 4), ...mk("B", 2)], "all-services");
  it("has one row per entity and six columns", () => {
    expect(rows).toHaveLength(2);
    expect(rows[0].shares).toHaveLength(PORTFOLIO_COLS.length);
  });
  it("ranks the more advanced entity first at threshold 4", () => {
    const col = PORTFOLIO_COLS.findIndex((c) => c.threshold === 4 && c.guardrails === "none");
    expect(rows.find((r) => r.entity === "A")!.ranks[col]).toBe(1);
    expect(rows.find((r) => r.entity === "B")!.ranks[col]).toBe(2);
  });
  it("shares ties rather than ordering arbitrarily", () => {
    const tie = portfolio([...mk("A", 3), ...mk("B", 3)], "all-services");
    expect(tie.every((r) => r.rankMin === 1 && r.rankMax === 1)).toBe(true);
  });
});

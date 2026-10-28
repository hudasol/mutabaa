import { describe, expect, it } from "vitest";
import inputs from "../../data/golden/own_inputs.json";
import outputs from "../../data/golden/own_outputs.json";
import { convertRows, mapColumns, readMyFile } from "./commitments";

type Case = { name: string; text: string };
type Expected = {
  name: string; fatal?: string; errors?: string[]; rows?: number; rejected?: number; duplicates?: number;
  unmapped?: string[]; truncated?: boolean;
  items?: { id: string; title: string; kind: string; owner: string | null; metric: string | null; unit: string | null;
    target_number: number | null; deadline: string | null; deadline_precision: string; measurement_source: string | null;
    undefined_terms: string[]; row: number }[];
};

function run(c: Case) {
  try {
    const { headers, rows, truncated } = readMyFile(c.name, c.text);
    const r = convertRows(headers, rows, mapColumns(headers), truncated);
    return {
      name: c.name,
      items: r.items.map((i) => ({
        id: i.id, title: i.title, kind: i.kind, owner: i.owner, metric: i.metric, unit: i.unit,
        target_number: i.target_number, deadline: i.deadline, deadline_precision: i.deadline_precision,
        measurement_source: i.measurement_source, undefined_terms: i.undefined_terms, row: i.row,
      })),
      errors: r.errors, rows: r.report.rows, rejected: r.report.rejected, duplicates: r.report.duplicates,
      unmapped: r.report.unmapped, truncated: r.report.truncated,
    };
  } catch (e) {
    return { name: c.name, fatal: String(e instanceof Error ? e.message : e) };
  }
}

describe("parity with pipeline/own.py on data/golden/own_inputs.json", () => {
  const expected = outputs as unknown as Expected[];
  it("has one expected result per input", () => expect(expected.map((e) => e.name)).toEqual((inputs as Case[]).map((c) => c.name)));
  for (const [i, c] of (inputs as Case[]).entries()) {
    it(`reads ${c.name} as Python does`, () => expect(run(c)).toEqual(expected[i]));
  }
});

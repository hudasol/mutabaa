import { describe, expect, it } from "vitest";
import { MAX_CSV_ROWS } from "./engine";
import { convertRows, mapColumns, readMyFile, scoreCommitment } from "./commitments";

// A regression guard, not a benchmark: the ceilings are several times the time measured on a development machine
// (see docs/PERFORMANCE.md), so a slow CI runner does not fail it but an accidental quadratic loop does.
function make(n: number, quoted: boolean): string {
  const kinds = ["target", "milestone", "deliverable", "input", "projection", "assessment", "vision"];
  const out = ["id,title,kind,owner,metric,unit,target_number,deadline,measurement_source,undefined_terms"];
  for (let i = 0; i < n; i++) {
    const title = quoted ? `"Commitment ${i}, with a comma"` : `Commitment ${i}`;
    out.push(`C${i},${title},${kinds[i % 7]},${i % 3 ? `Office ${i % 40}` : ""},services,services,${i % 100},${2026 + (i % 5)}-12-31,${i % 2 ? "Annual report" : ""},${i % 4 === 0 ? (quoted ? '"agentic; service"' : "agentic") : ""}`);
  }
  return out.join("\n") + "\n";
}

describe("reading a large file", () => {
  for (const quoted of [true, false]) {
    it(`reads, converts and scores ${MAX_CSV_ROWS} ${quoted ? "quoted" : "unquoted"} rows within the ceiling`, () => {
      const text = make(MAX_CSV_ROWS, quoted);
      const t0 = performance.now();
      const { headers, rows, truncated } = readMyFile("big.csv", text);
      const r = convertRows(headers, rows, mapColumns(headers), truncated);
      const scored = r.items.map((c) => scoreCommitment({ ...c, title_ar: c.title }));
      const ms = performance.now() - t0;
      console.log(`${quoted ? "quoted  " : "unquoted"} ${MAX_CSV_ROWS} rows: ${Math.round(ms)} ms`);
      expect(r.items).toHaveLength(MAX_CSV_ROWS);
      expect(scored).toHaveLength(MAX_CSV_ROWS);
      expect(ms).toBeLessThan(15_000);
    }, 30_000);
  }
  it("flags a file longer than the row cap", () => {
    expect(readMyFile("big.csv", make(MAX_CSV_ROWS + 3, false)).truncated).toBe(true);
  });
});

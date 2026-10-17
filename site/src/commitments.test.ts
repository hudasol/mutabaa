import { describe, expect, it } from "vitest";
import goldenQuestions from "../../data/golden/questions.json";
import goldenScores from "../../data/golden/score.json";
import raw from "./data/real.json";
import { convertRows, deadlinePrecision, mapColumns, questionsFor, readMyFile, scoreCommitment, MY_TEMPLATE } from "./commitments";
import { csvCell } from "./engine";
import type { Payload } from "./types";

const data = raw as unknown as Payload;

describe("parity with pipeline/score.py and pipeline/questions.py", () => {
  it("scores every public commitment exactly as Python does", () => {
    expect(data.commitments.length).toBeGreaterThan(0);
    expect(data.commitments.map((c) => scoreCommitment(c))).toEqual(goldenScores);
  });
  it("asks exactly the same questions as Python for every public commitment", () => {
    const qs = Object.fromEntries(data.commitments.map((c) => [c.id, questionsFor(c, scoreCommitment(c))]));
    expect(qs).toEqual(goldenQuestions);
  });
});

describe("reading a user's commitments", () => {
  it("dates deadlines by their precision", () => {
    expect(["2027-12-31", "2027-12", "2027", "", "within two years"].map(deadlinePrecision))
      .toEqual(["day", "month", "year", "none", "relative"]);
  });
  it("reads the template and scores it", () => {
    const { headers, rows } = readMyFile("t.csv", MY_TEMPLATE);
    const r = convertRows(headers, rows, mapColumns(headers));
    expect(r.errors).toEqual([]);
    expect(r.items[0].undefined_terms).toEqual(["agentic", "service"]);
    const s = scoreCommitment(r.items[0]);
    expect(s.missing).toEqual(["terms_defined"]);
    expect(questionsFor(r.items[0], s).map((q) => q.check)).toEqual(["terms_defined", "terms_defined"]);
  });
  it("maps renamed columns and reports rejected rows", () => {
    const csv = "Code,Commitment,Type,Due date\nA1,Do a thing,target,2026\nA1,Dup,target,\nA2,Bad,wish,\n";
    const { headers, rows } = readMyFile("x.csv", csv);
    const m = mapColumns(headers);
    expect(m.id).toBe(0); expect(m.title).toBe(1); expect(m.kind).toBe(2); expect(m.deadline).toBe(3);
    const r = convertRows(headers, rows, m);
    expect(r.report).toMatchObject({ rows: 3, accepted: 1, rejected: 2, duplicates: 1 });
    expect(r.errors.join(" ")).toMatch(/duplicate id/);
    expect(r.errors.join(" ")).toMatch(/kind must be one of/);
  });
  it("fails clearly when required columns are missing", () => {
    const { headers, rows } = readMyFile("x.csv", "name,owner\nA,B\n");
    const r = convertRows(headers, rows, mapColumns(headers));
    expect(r.items).toEqual([]);
    expect(r.errors[0]).toMatch(/Missing columns: id, kind/);
  });
  it("reads a JSON array, with terms given as a list", () => {
    const json = JSON.stringify([{ id: "J1", title: "T", kind: "deliverable", undefined_terms: ["a", "b"], owner: "O" }]);
    const { headers, rows } = readMyFile("x.json", json);
    const r = convertRows(headers, rows, mapColumns(headers));
    expect(r.items[0].undefined_terms).toEqual(["a", "b"]);
    const s = scoreCommitment(r.items[0]);
    expect(s.checks.numeric_target).toBeNull();
    expect(s.applicable).toBe(4);
  });
  it("rejects malformed JSON with a readable message", () => {
    expect(() => readMyFile("x.json", "[{oops")).toThrow(/not valid JSON/);
    expect(() => readMyFile("x.json", '{"a": 1}')).toThrow(/array of commitments/);
  });
  it("neutralises formulas in exported cells", () => {
    expect(csvCell("=HYPERLINK(1)")).toBe(`"'=HYPERLINK(1)"`);
  });
});

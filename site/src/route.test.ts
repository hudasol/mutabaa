import { describe, expect, it } from "vitest";
import { buildHash, parseHash } from "./route";
import { sortCommitments } from "./ledgerSort";
import { dict } from "./i18n";
import type { Commitment, Score, Status } from "./types";

describe("route", () => {
  it("round-trips state", () => {
    const h = buildHash("lab", { u: "services", s: "all-services", t: "3", g: undefined });
    expect(h).toBe("#/lab?s=all-services&t=3&u=services");
    expect(parseHash(h)).toEqual({ page: "lab", params: { u: "services", s: "all-services", t: "3" } });
  });
  it("defaults to overview", () => expect(parseHash("")).toEqual({ page: "overview", params: {} }));
});

describe("sorting", () => {
  const c = (id: string, title: string) => ({ id, title, title_ar: title }) as Commitment;
  const rows = [c("C02", "b"), c("C01", "c"), c("C03", "a")];
  const scores = [
    { commitment_id: "C01", ratio: 0.2 }, { commitment_id: "C02", ratio: 0.9 }, { commitment_id: "C03", ratio: 0.5 },
  ] as Score[];
  const st = [] as Status[];
  it("sorts by id", () => expect(sortCommitments(rows, scores, st, "id", "asc", "en").map((r) => r.id)).toEqual(["C01", "C02", "C03"]));
  it("sorts by checks descending", () =>
    expect(sortCommitments(rows, scores, st, "checks", "desc", "en").map((r) => r.id)).toEqual(["C02", "C03", "C01"]));
});

describe("i18n parity", () => {
  const keys = (o: object) => Object.keys(o).sort();
  it("English and Arabic have the same keys", () => expect(keys(dict.ar)).toEqual(keys(dict.en)));
  it("nested label maps have the same keys", () => {
    for (const k of ["st", "band", "jur", "kinds", "src_kind", "checks", "oc", "vf"] as const) {
      expect(keys(dict.ar[k])).toEqual(keys(dict.en[k]));
    }
  });
  it("every string is non-empty and arrays line up", () => {
    for (const k of keys(dict.en) as (keyof typeof dict.en)[]) {
      const e = dict.en[k], a = dict.ar[k];
      expect(typeof a).toBe(typeof e);
      if (typeof e === "string") expect((a as string).length).toBeGreaterThan(0);
      if (Array.isArray(e)) expect((a as unknown[]).length).toBe(e.length);
    }
  });
});

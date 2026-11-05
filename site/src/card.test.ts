import { describe, expect, it } from "vitest";
import cases from "../../data/golden/card_cases.json";
import { labLink, validateCard } from "./card";

describe("card validation agrees with pipeline/card.py on data/golden/card_cases.json", () => {
  for (const c of cases as { name: string; card: unknown; valid: boolean }[]) {
    it(`${c.name}`, () => expect(validateCard(c.card).length === 0).toBe(c.valid));
  }
  it("builds a Definition Lab link", () => {
    expect(labLink({ unit: "services", scope: "all-services", threshold: 2, guardrails: "none" })).toBe("#/lab?g=none&s=all-services&t=2&u=services");
  });
});

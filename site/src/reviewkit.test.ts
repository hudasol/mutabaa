import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { dict } from "./i18n";

describe("Arabic review kit", () => {
  it("lists every string-valued key of the interface", () => {
    const csv = readFileSync(new URL("../../docs/review_kits/arabic_strings.csv", import.meta.url), "utf8");
    const keys = Object.entries(dict.en).filter(([, v]) => typeof v === "string" || typeof v === "function").map(([k]) => k);
    const missing = keys.filter((k) => !csv.includes(`\n"${k}",`));
    expect(missing).toEqual([]);
  });
  it("says in the guide that no native speaker has reviewed the text", () => {
    const md = readFileSync(new URL("../../docs/review_kits/arabic_review.md", import.meta.url), "utf8");
    expect(md).toMatch(/No native Arabic speaker has reviewed/);
  });
});

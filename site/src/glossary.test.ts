import { describe, expect, it } from "vitest";
import glossary from "../../data/glossary/glossary.json";
import { dict } from "./i18n";

type Term = { id: string; en: string; en_match: string; ar: string; ar_forms: string[] };

function flat(o: unknown, p = ""): Record<string, string> {
  if (typeof o === "string") return { [p]: o };
  if (o === null || typeof o !== "object") return {};
  return Object.assign({}, ...Object.entries(o).map(([k, v]) => flat(v, p ? `${p}.${k}` : k)));
}

describe("Arabic text uses the glossary terms", () => {
  const en = flat(dict.en), ar = flat(dict.ar);
  const terms = glossary.terms as Term[];
  it("glossary is not reviewed by a native speaker, and says so", () => expect(glossary.reviewed_by_native_speaker).toBe(false));
  for (const term of terms) {
    it(`wherever English says "${term.en_match}", Arabic uses ${term.ar}`, () => {
      const bad = Object.keys(en).filter((k) =>
        new RegExp(term.en_match, "i").test(en[k]) && k in ar && !term.ar_forms.some((f) => ar[k].includes(f)));
      expect(bad).toEqual([]);
    });
  }
});

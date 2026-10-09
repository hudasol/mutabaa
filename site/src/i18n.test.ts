import { describe, expect, it } from "vitest";
import { dict } from "./i18n";

function flat(o: unknown, p = ""): Record<string, unknown> {
  if (o === null || typeof o !== "object" || Array.isArray(o)) return { [p]: o };
  return Object.assign({}, ...Object.entries(o).map(([k, v]) => flat(v, p ? `${p}.${k}` : k)));
}

describe("en/ar parity", () => {
  const en = flat(dict.en), ar = flat(dict.ar);
  it("has the same keys", () => expect(Object.keys(ar).sort()).toEqual(Object.keys(en).sort()));
  it("has the same value types and no blanks", () => {
    for (const k of Object.keys(en)) {
      expect(typeof ar[k], k).toBe(typeof en[k]);
      if (typeof ar[k] === "string") expect((ar[k] as string).trim(), k).not.toBe("");
      if (Array.isArray(en[k])) expect((ar[k] as unknown[]).length, k).toBe((en[k] as unknown[]).length);
    }
  });
  it("no retired band labels", () => {
    const all = JSON.stringify(dict.en);
    expect(all).not.toMatch(/Not yet checkable/i);
  });
});

import { describe, expect, it } from "vitest";
import inputs from "../../data/golden/lint_inputs.json";
import outputs from "../../data/golden/lint_outputs.json";
import { lint, type LintFields } from "./lint";

type Case = { name: string; text: string; kind?: string; fields?: LintFields | null };

describe("parity with pipeline/lint.py on data/golden/lint_inputs.json", () => {
  const expected = outputs as unknown as ({ name: string } & Record<string, unknown>)[];
  it("has one expected result per input", () => expect(expected.map((e) => e.name)).toEqual((inputs as Case[]).map((c) => c.name)));
  for (const [i, c] of (inputs as Case[]).entries()) {
    it(`lints ${c.name} as Python does`, () => {
      const { name, ...rest } = expected[i];
      expect(name).toBe(c.name);
      expect(lint(c.text, c.kind ?? "target", c.fields ?? null)).toEqual(rest);
    });
  }
});

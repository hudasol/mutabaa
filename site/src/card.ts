// Mirrors pipeline/card.py and the DefinitionCard model in pipeline/schemas.py. data/golden/card_cases.json
// holds valid and invalid cards that both implementations must judge the same way.
import { GUARDRAILS, SCOPES, THRESHOLDS, UNITS } from "./engine";
import type { Definition } from "./types";

export type DefinitionCard = {
  card_version: "1"; title: string; headline_claim: string; definition: Definition;
  as_of: string; declared_by: string; notes?: string | null; is_synthetic: boolean;
};

const KEYS = ["card_version", "title", "headline_claim", "definition", "as_of", "declared_by", "notes", "is_synthetic"];
const text = (v: unknown, max: number) => typeof v === "string" && v.length >= 1 && v.length <= max;

export function validateCard(raw: unknown): string[] {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) return ["a card is one JSON object"];
  const c = raw as Record<string, unknown>;
  const errors: string[] = [];
  for (const k of Object.keys(c)) if (!KEYS.includes(k)) errors.push(`${k}: extra field`);
  if (c.card_version !== undefined && c.card_version !== "1") errors.push("card_version: must be 1");
  if (!text(c.title, 120)) errors.push("title: 1 to 120 characters");
  if (!text(c.headline_claim, 400)) errors.push("headline_claim: 1 to 400 characters");
  if (!text(c.declared_by, 120)) errors.push("declared_by: 1 to 120 characters");
  if (c.notes !== undefined && c.notes !== null && !(typeof c.notes === "string" && c.notes.length <= 500)) errors.push("notes: at most 500 characters");
  if (typeof c.as_of !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(c.as_of) || Number.isNaN(Date.parse(c.as_of))) errors.push("as_of: a date as YYYY-MM-DD");
  if (typeof c.is_synthetic !== "boolean") errors.push("is_synthetic: true or false");
  const d = c.definition as Record<string, unknown> | null;
  if (d === null || typeof d !== "object") errors.push("definition: required");
  else {
    if (!(UNITS as readonly unknown[]).includes(d.unit)) errors.push("definition.unit: not allowed");
    if (!(SCOPES as readonly unknown[]).includes(d.scope)) errors.push("definition.scope: not allowed");
    if (!(THRESHOLDS as readonly unknown[]).includes(d.threshold)) errors.push("definition.threshold: not allowed");
    if (!(GUARDRAILS as readonly unknown[]).includes(d.guardrails)) errors.push("definition.guardrails: not allowed");
  }
  return errors;
}

/** The Definition Lab link that recomputes the headline under the card's definition. */
export function labLink(d: Definition): string {
  return `#/lab?g=${d.guardrails}&s=${d.scope}&t=${d.threshold}&u=${d.unit}`;
}

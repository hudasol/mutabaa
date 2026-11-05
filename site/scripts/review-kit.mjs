// Writes docs/review_kits/arabic_strings.csv: every interface string with its English source,
// the Arabic text, and empty columns for a native reviewer. Run: npm run review-kit
import { writeFileSync } from "node:fs";
import { dict } from "../src/i18n.ts";

const glossary = JSON.parse((await import("node:fs")).readFileSync(new URL("../../data/glossary/glossary.json", import.meta.url), "utf8"));
const q = (s) => `"${String(s).replaceAll('"', '""')}"`;
const show = (v) => {
  if (typeof v === "string") return v;
  if (typeof v === "function") {
    try { return String(v(3, 7, 5)); } catch { return "(text built from numbers; see source)"; }
  }
  return null;
};
const rows = [["key", "english", "arabic", "glossary_terms_in_english", "reviewer_verdict (ok / change)", "reviewer_correction", "reviewer_note"]];
for (const [k, en] of Object.entries(dict.en)) {
  const e = show(en), a = show(dict.ar[k]);
  if (e === null || a === null) continue;
  const terms = glossary.terms.filter((t) => new RegExp(t.en_match, "i").test(e)).map((t) => `${t.en}=${t.ar}`).join("; ");
  rows.push([k, e, a, terms, "", "", ""]);
}
writeFileSync(new URL("../../docs/review_kits/arabic_strings.csv", import.meta.url), "﻿" + rows.map((r) => r.map(q).join(",")).join("\n") + "\n");
console.log(`${rows.length - 1} strings written`);

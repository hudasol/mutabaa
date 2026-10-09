import type { Commitment, Score, Status } from "./types";

export type SortKey = "id" | "title" | "checks" | "status";
const STATUS_ORDER: Status["status"][] = [
  "target-claimed-met", "milestone-reported", "activity-reported", "no-public-evidence", "not-checkable",
];

export function sortCommitments(
  rows: Commitment[], scores: Score[], statuses: Status[], key: SortKey, dir: "asc" | "desc", lang: string,
): Commitment[] {
  const sc = new Map(scores.map((s) => [s.commitment_id, s]));
  const st = new Map(statuses.map((s) => [s.commitment_id, s]));
  const val = (c: Commitment): number | string => {
    if (key === "id") return c.id;
    if (key === "title") return lang === "ar" ? c.title_ar : c.title;
    if (key === "checks") return sc.get(c.id)?.ratio ?? 0;
    return STATUS_ORDER.indexOf(st.get(c.id)?.status ?? "not-checkable");
  };
  const out = [...rows].sort((a, b) => {
    const x = val(a), y = val(b);
    const r = typeof x === "number" && typeof y === "number" ? x - y : String(x).localeCompare(String(y), lang);
    return r || a.id.localeCompare(b.id);
  });
  return dir === "desc" ? out.reverse() : out;
}

export type Anchor = { source_id: string; text: string };
export type Commitment = {
  id: string; title: string; title_ar: string; statement: string; statement_ar: string;
  jurisdiction: "federal" | "abu-dhabi" | "national";
  kind: "target" | "milestone" | "deliverable" | "input" | "projection" | "assessment" | "vision";
  owner: string | null; metric: string | null; unit: string | null; baseline: string | null;
  target_value: string | null; target_number: number | null; target_comparator: string | null;
  deadline: string | null; deadline_text: string | null; deadline_precision: string;
  measurement_source: string | null; undefined_terms: string[]; announced: string | null;
  tags: string[]; source_ids: string[]; anchors: Anchor[]; notes: string;
};
export type Evidence = {
  id: string; commitment_ids: string[]; kind: "activity" | "quantified-progress" | "target-met-claim";
  summary: string; summary_ar: string; as_of: string | null; as_of_note: string | null;
  value: number | null; value_text: string | null; unit: string | null; source_id: string;
  anchor: string; corroboration: string; note: string;
};
export type Source = {
  id: string; title: string; publisher: string; url: string;
  kind: "official-statement" | "official-self-report" | "secondary-media" | "third-party";
  published: string | null; published_note: string | null; retrieved: string;
  extract_file: string; content_hash: string; ai_assisted: boolean; notes: string;
  expect_present: string[]; expect_absent: string[];
};
export type Claim = {
  id: string; text: string; text_ar: string; source_id: string; anchor: string;
  corroboration: string; official_sources_checked: string[]; commitment_ids: string[]; note: string;
};
export type Score = {
  commitment_id: string; checks: Record<string, boolean | null>; applicable: number; passed: number;
  ratio: number; band: "checkable" | "partly-checkable" | "not-yet-checkable"; missing: string[];
};
export type Status = {
  commitment_id: string;
  status: "not-checkable" | "no-public-evidence" | "activity-reported" | "milestone-reported" | "target-claimed-met";
  reasons: string[]; evidence_ids: string[]; excluded_evidence_ids: string[];
  self_reported_only: boolean; unit_mismatch: boolean; progress_ratio: number | null; progress_as_of: string | null;
  latest_evidence_date: string | null; evidence_age_days: number | null; stale: boolean;
};
export type Question = { check: string; en: string; ar: string };
export type Coverage = { commitment_id: string; searches: number; last_searched: string | null; found_sources: string[]; outcomes: string[] };
export type SearchEntry = {
  id: string; searched_on: string; tool: string; query: string; commitment_ids: string[];
  outcome: "progress-found" | "target-restatement-only" | "nothing-official-found"; found_source_ids: string[]; note: string;
};
export type VerifyResult = {
  result: "verified" | "failed" | "unreachable" | "no-expectations"; checked_at: string; http_status: number | null;
  checked_present: number; checked_absent: number; missing: string[]; unexpected: string[]; error?: string;
};
export type Verification = { run_at: string; results: Record<string, VerifyResult> };
export type Item = {
  id: string; entity_id: string; sector: string; kind: "service" | "operation";
  audience: "citizen" | "business" | "internal"; name: string; annual_transactions: number;
  maturity: 0 | 1 | 2 | 3 | 4; oversight: boolean; audit_trail: boolean; uae_residency: boolean; fallback: boolean;
};
export type Registry = {
  meta: { seed: number; generator_version: string; is_synthetic: true; disclaimer: string };
  entities: { id: string; name: string; sector: string; advancement: number }[];
  items: Item[];
};
export type Definition = {
  unit: "services" | "transactions" | "entities" | "sectors";
  scope: "citizen-services" | "all-services" | "services-and-operations";
  threshold: 2 | 3 | 4;
  guardrails: "none" | "required";
};
export type SweepRow = Definition & { share: number | null };
export type Payload = {
  sources: Source[]; commitments: Commitment[]; evidence: Evidence[]; claims: Claim[];
  scores: Score[]; statuses: Status[]; synthetic: Registry; sweep: SweepRow[];
  questions: Record<string, Question[]>; coverage: Coverage[]; searches: SearchEntry[];
  analysis: Analysis; verification: Verification; build: { data_as_of: string; payload_sha256: string; schema: number };
};

export type Ci = [number, number];
export type Analysis = {
  robustness: {
    registries: number; flip_rate: number; effects: Record<string, number>;
    by_profile: Record<string, { registries: number; flip_rate: number; median_spread: number; median_core_spread: number }>;
  };
  calibration: {
    bands: { max_changed: number; n: number };
    weights: { spearman_median: number; spearman_p05: number; pass_rate: Record<string, number | null> };
    consistency: Record<"numeric_target" | "dated_deadline", { n: number; agree: number; kappa: number | null; ci95: Ci }> & { disagreements: string[] };
  };
  agreement: {
    recall: { found: number; n: number; rate: number; ci95: Ci };
    numeric_recall: { found: number; n: number; rate: number; ci95: Ci };
    missed: string[];
  };
};

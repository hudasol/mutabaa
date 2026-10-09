import { useMemo, useState } from "react";
import { copyText, download, pct, useCtx } from "./ctx";
import { CSV_COLUMNS, CSV_TEMPLATE, autoMap, convert, readCsv, type CsvColumn, type CsvResult, type Mapping } from "./engine";
import type { Definition, Item, Score, Status } from "./types";

export function Head({ title, sub }: { title: string; sub?: string }) {
  return <header className="page-head"><h1>{title}</h1>{sub && <p className="sub">{sub}</p>}</header>;
}

export function StatusPill({ s }: { s: Status["status"] }) {
  const { t } = useCtx();
  return <span className={`pill is-${s}${s === "not-checkable" ? " hatch" : ""}`}><i />{t.st[s]}</span>;
}

export function Ticks({ score }: { score: Score }) {
  const { t } = useCtx();
  const keys = Object.keys(t.checks) as (keyof typeof t.checks)[];
  const label = keys.map((k) => `${t.checks[k]}: ${score.checks[k] === null ? "n/a" : score.checks[k] ? "yes" : "no"}`).join("; ");
  return (
    <span className="ticks" role="img" aria-label={`${score.passed} / ${score.applicable}. ${label}`} title={label}>
      {keys.map((k) => <span key={k} className={score.checks[k] === null ? "na" : score.checks[k] ? "y" : "n"} />)}
    </span>
  );
}

export function SourceBanner({ kind }: { kind: "synthetic" | "yours" }) {
  const { t } = useCtx();
  return (
    <div className={`banner ${kind}`} role="note">
      <span className={`badge ${kind}`}>{kind === "synthetic" ? t.synthetic : t.yours}</span>
      <span>{kind === "synthetic" ? t.synthetic_long : t.yours_long}</span>
    </div>
  );
}

export function VerifyChip({ sourceId }: { sourceId: string }) {
  const { t, data } = useCtx();
  const r = data.verification.results[sourceId];
  const key = r ? r.result : "none";
  return (
    <span className={`chip vf-${key}`} title={r?.error ?? ""}>
      {t.vf[key as keyof typeof t.vf]}{r && key === "verified" ? ` ${t.vf_on(r.checked_at)}` : ""}
    </span>
  );
}

export function CopyLink({ label }: { label?: string }) {
  const { t } = useCtx();
  const [done, setDone] = useState(false);
  return (
    <button className="btn ghost" onClick={async () => { if (await copyText(location.href)) { setDone(true); setTimeout(() => setDone(false), 1800); } }}>
      {done ? t.lg_copied : label ?? t.lg_copy}
    </button>
  );
}

// ------------------------------------------------------------------ strip

type Row = { share: number | null; d: Definition };
export function Strip({ current, rows, label }: { current?: Definition; rows: Row[]; label: string }) {
  const W = 760, H = 200, pad = 28;
  const x = (v: number) => pad + v * (W - 2 * pad);
  const vals = rows.filter((r) => r.share !== null).sort((a, b) => (a.share as number) - (b.share as number));
  const placed: { cx: number; cy: number; r: Row; i: number }[] = [];
  vals.forEach((r, i) => {
    const cx = x(r.share as number);
    let row = 0;
    while (placed.some((p) => p.cy === 150 - row * 11 && Math.abs(p.cx - cx) < 10)) row++;
    placed.push({ cx, cy: 150 - row * 11, r, i });
  });
  const same = (d: Definition, c?: Definition) => !!c && d.unit === c.unit && d.scope === c.scope && d.threshold === c.threshold && d.guardrails === c.guardrails;
  return (
    <svg className="strip" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
      <line className="axis" x1={pad} x2={W - pad} y1={162} y2={162} />
      {[0, 0.25, 0.5, 0.75, 1].map((v) => (
        <g key={v}><line className="axis" x1={x(v)} x2={x(v)} y1={162} y2={168} /><text x={x(v)} y={184} textAnchor="middle">{pct(v)}</text></g>
      ))}
      <line className="target" x1={x(0.5)} x2={x(0.5)} y1={8} y2={162} />
      <text className="t-label" x={x(0.5) + 6} y={16}>50%</text>
      {placed.map((p) => (
        <circle key={p.i} className={`dot hero-dot${same(p.r.d, current) ? " on" : ""}`} style={{ ["--i" as string]: p.i }}
          cx={p.cx} cy={p.cy} r={same(p.r.d, current) ? 9 : 5}><title>{pct(p.r.share, 1)}</title></circle>
      ))}
    </svg>
  );
}

// ------------------------------------------------------------------ data source + CSV

export type ItemsHook = {
  items: Item[]; kind: "synthetic" | "yours"; csv: (CsvResult & { name: string }) | null;
  setCsv: (c: (CsvResult & { name: string }) | null) => void; source: "syn" | "csv"; setSource: (s: "syn" | "csv") => void;
};

export function useItems(): ItemsHook {
  const { data } = useCtx();
  const [csv, setCsv] = useState<(CsvResult & { name: string }) | null>(null);
  const [source, setSource] = useState<"syn" | "csv">("syn");
  const usingCsv = source === "csv" && !!csv && csv.items.length > 0;
  return { items: usingCsv ? csv.items : data.synthetic.items, kind: usingCsv ? "yours" : "synthetic", csv, setCsv, source, setSource };
}

export function CsvLoader({ h }: { h: ItemsHook }) {
  const { t } = useCtx();
  const [raw, setRaw] = useState<{ name: string; headers: string[]; rows: string[][]; truncated: boolean } | null>(null);
  const [mapping, setMapping] = useState<Mapping>({});
  const apply = (name: string, headers: string[], rows: string[][], m: Mapping, tr: boolean) => {
    h.setCsv({ ...convert(headers, rows, m, tr), name });
  };
  const onFile = async (f: File | undefined) => {
    if (!f) return;
    const { headers, rows, truncated } = readCsv(await f.text());
    const m = autoMap(headers);
    setRaw({ name: f.name, headers, rows, truncated }); setMapping(m);
    apply(f.name, headers, rows, m, truncated);
    h.setSource("csv");
  };
  const unmapped = useMemo(() => CSV_COLUMNS.filter((c) => mapping[c] === undefined), [mapping]);
  const rep = h.csv?.report;
  const colName = (c: CsvColumn) => c;
  return (
    <div className="panel">
      <div className="seg" role="group" aria-label={t.lb_data}>
        <button aria-pressed={h.source === "syn"} onClick={() => h.setSource("syn")}>{t.lb_data_syn}</button>
        <button aria-pressed={h.source === "csv"} onClick={() => h.setSource("csv")}>{t.lb_data_csv}</button>
      </div>
      {h.source === "csv" && (
        <>
          <label className="field">{t.lb_upload}<input type="file" accept=".csv,text/csv" onChange={(e) => onFile(e.target.files?.[0])} /></label>
          <p className="small">{t.lb_csv_help} <span className="mono">{CSV_COLUMNS.join(", ")}</span></p>
          <button className="btn ghost" style={{ justifySelf: "start" }} onClick={() => download("mutabaa-template.csv", CSV_TEMPLATE, "text/csv")}>{t.lb_template}</button>
          {raw && (
            <details className="mapper" open={unmapped.length > 0}>
              <summary><b>{t.lb_map_title}</b></summary><p className="small">{t.lb_map_help}</p>
              <div className="cols">
                {CSV_COLUMNS.map((c) => (
                  <label className="field" key={c}><span className="mono">{colName(c)}</span>
                    <select value={mapping[c] ?? ""} onChange={(e) => {
                      const m = { ...mapping }; if (e.target.value === "") delete m[c]; else m[c] = Number(e.target.value); setMapping(m);
                    }}>
                      <option value="">{t.lb_pick}</option>
                      {raw.headers.map((hd, i) => <option key={i} value={i}>{hd}</option>)}
                    </select></label>
                ))}
              </div>
              <button className="btn" style={{ justifySelf: "start", marginTop: ".75rem" }} disabled={unmapped.length > 0}
                onClick={() => apply(raw.name, raw.headers, raw.rows, mapping, raw.truncated)}>{t.lb_apply}</button>
            </details>
          )}
          {h.csv && rep && (
            <div>
              <h3>{t.lb_quality}</h3>
              <dl className="kv quality">
                <div><dt>{t.q_rows}</dt><dd>{rep.rows}</dd></div>
                <div><dt>{t.q_accepted}</dt><dd>{rep.accepted}</dd></div>
                <div><dt>{t.q_rejected}</dt><dd>{rep.rejected}</dd></div>
                <div><dt>{t.q_dupes}</dt><dd>{rep.duplicates}</dd></div>
                <div><dt>{t.q_zero}</dt><dd>{pct(rep.zeroTransactionShare)}</dd></div>
                <div><dt>{t.q_citizen}</dt><dd>{pct(rep.citizenShare)}</dd></div>
                <div><dt>{t.q_entities}</dt><dd>{rep.entities}</dd></div>
                <div><dt>{t.q_sectors}</dt><dd>{rep.sectors}</dd></div>
              </dl>
              {rep.truncated && <p className="small">{t.q_trunc(200000)}</p>}
              <p className="small">{h.csv.name}: {t.lb_loaded(h.csv.items.length)}</p>
              {h.csv.errors.length > 0 && (
                <div><b>{t.lb_errors(h.csv.errors.length)}</b>
                  <ul className="errlist">{h.csv.errors.slice(0, 8).map((e) => <li key={e}>{e}</li>)}</ul></div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

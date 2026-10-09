import { useMemo, useState } from "react";
import { download, L, pct, useCtx } from "./ctx";
import { StatusPill, SourceBanner, Ticks } from "./parts";
import {
  CSV_COLUMNS, CSV_TEMPLATE, GUARDRAILS, SCOPES, THRESHOLDS, UNITS, allDefinitions, parseCsv, share,
} from "./engine";
import type { Commitment, Definition, Item } from "./types";

const TODAY = new Date();
const dayDiff = (iso: string) => Math.round((new Date(iso).getTime() - TODAY.getTime()) / 86400000);

function Head({ title, sub }: { title: string; sub?: string }) {
  return <header className="page-head"><h1>{title}</h1>{sub && <p className="sub">{sub}</p>}</header>;
}

// ------------------------------------------------------------------ strip

function Strip({ current, rows }: { current?: Definition; rows: { share: number | null; d: Definition }[] }) {
  const { t } = useCtx();
  const W = 760, H = 200, pad = 28;
  const x = (v: number) => pad + v * (W - 2 * pad);
  const vals = rows.filter((r) => r.share !== null).sort((a, b) => (a.share as number) - (b.share as number));
  // stack dots that land close together
  const placed: { cx: number; cy: number; r: (typeof vals)[number]; i: number }[] = [];
  vals.forEach((r, i) => {
    const cx = x(r.share as number);
    let row = 0;
    while (placed.some((p) => p.cy === 150 - row * 11 && Math.abs(p.cx - cx) < 10)) row++;
    placed.push({ cx, cy: 150 - row * 11, r, i });
  });
  const same = (d: Definition, c?: Definition) => c && d.unit === c.unit && d.scope === c.scope && d.threshold === c.threshold && d.guardrails === c.guardrails;
  return (
    <svg className="strip" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={t.ov_strip_title}>
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

// ------------------------------------------------------------------ overview

export function Overview() {
  const { t, data } = useCtx();
  const rows = useMemo(() => data.sweep.map((r) => ({ share: r.share, d: r as Definition })), [data]);
  const vals = rows.map((r) => r.share).filter((v): v is number => v !== null);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const reach = vals.filter((v) => v >= 0.5).length;
  const st = data.statuses, sc = data.scores;
  return (
    <>
      <Head title={t.ov_title(pct(lo), pct(hi))} sub={t.ov_sub} />
      <section className="panel" aria-labelledby="strip-h">
        <div style={{ display: "flex", gap: ".75rem", alignItems: "center", flexWrap: "wrap" }}>
          <h2 id="strip-h">{t.ov_strip_title}</h2><span className="badge synthetic">{t.synthetic}</span>
        </div>
        <p className="small">{t.ov_strip_note}</p>
        <Strip rows={rows} />
        <p className="small">{t.ov_axis}. <b>{t.ov_reach(reach, vals.length)}</b></p>
      </section>
      <section className="stats" aria-label="Summary">
        <div className="stat"><b>{data.commitments.length}</b><span>{t.ov_stat_c}</span></div>
        <div className="stat"><b>{st.filter((s) => s.status === "no-public-evidence").length}</b><span>{t.ov_stat_nopub}</span></div>
        <div className="stat"><b>{sc.filter((s) => s.band === "not-yet-checkable").length}</b><span>{t.ov_stat_notcheck}</span></div>
        <div className="stat"><b>{data.claims.length}</b><span>{t.ov_stat_claims}</span></div>
      </section>
      <section className="panel">
        <h2>{t.ov_why_title}</h2>
        <ul style={{ margin: 0, paddingInlineStart: "1.1rem", display: "grid", gap: ".5rem", maxWidth: "68ch" }}>
          {t.ov_why.map((w) => <li key={w}>{w}</li>)}
        </ul>
      </section>
    </>
  );
}

// ------------------------------------------------------------------ ledger

function Detail({ c, onClose }: { c: Commitment; onClose: () => void }) {
  const { t, lang, data } = useCtx();
  const sc = data.scores.find((s) => s.commitment_id === c.id)!;
  const stt = data.statuses.find((s) => s.commitment_id === c.id)!;
  const ev = data.evidence.filter((e) => e.commitment_ids.includes(c.id));
  const srcs = data.sources.filter((s) => c.source_ids.includes(s.id));
  const ns = t.lg_not_stated;
  return (
    <div className="detail">
      <p>{L(lang, c.statement, c.statement_ar)}</p>
      <dl className="kv">
        <div><dt>{t.lg_owner}</dt><dd>{c.owner ?? ns}</dd></div>
        <div><dt>{t.lg_kind}</dt><dd>{t.kinds[c.kind]}</dd></div>
        <div><dt>{t.lg_metric}</dt><dd>{c.metric ?? ns}</dd></div>
        <div><dt>{t.lg_target}</dt><dd>{c.target_value ?? ns}</dd></div>
        <div><dt>{t.lg_unit}</dt><dd>{c.unit ?? ns}</dd></div>
        <div><dt>{t.lg_deadline}</dt><dd>{c.deadline ?? c.deadline_text ?? ns}</dd></div>
        <div><dt>{t.lg_announced}</dt><dd>{c.announced ?? ns}</dd></div>
        {stt.progress_ratio !== null && <div><dt>{t.lg_ratio}</dt><dd>{pct(stt.progress_ratio, 1)}</dd></div>}
      </dl>
      <div className="cols">
        <div>
          <h3>{t.lg_checks}</h3>
          <ul className="checklist">
            {(Object.keys(t.checks) as (keyof typeof t.checks)[]).map((k) => (
              <li key={k}>
                <span className="ticks"><span className={sc.checks[k] === null ? "na" : sc.checks[k] ? "y" : "n"} /></span>
                <span>{t.checks[k]}{sc.checks[k] === null ? " (n/a)" : ""}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3>{t.lg_undefined}</h3>
          {c.undefined_terms.length ? <ul className="checklist">{c.undefined_terms.map((u) => <li key={u}>{u}</li>)}</ul> : <p className="small">{t.lg_none_undefined}</p>}
        </div>
      </div>
      <div>
        <h3>{t.lg_evidence}</h3>
        {ev.length === 0 && <p className="small">{t.lg_no_evidence}</p>}
        <div style={{ display: "grid", gap: ".8rem", marginTop: ".5rem" }}>
          {ev.map((e) => {
            const s = data.sources.find((x) => x.id === e.source_id)!;
            const excluded = stt.excluded_evidence_ids.includes(e.id);
            return (
              <div key={e.id} className={`ev${excluded ? " excluded" : ""}`}>
                <div><b>{e.id}</b> {L(lang, e.summary, e.summary_ar)}</div>
                <div className="small">
                  <span className={`chip${s.kind === "secondary-media" ? " media" : ""}`}>{t.src_kind[s.kind]}</span>{" "}
                  {e.as_of ?? e.as_of_note ?? ""} · {s.id} · {e.kind}
                </div>
                {excluded && <div className="small" style={{ color: "var(--flag)" }}>{t.lg_excluded}</div>}
              </div>
            );
          })}
        </div>
        {stt.unit_mismatch && <p className="small" style={{ marginTop: ".5rem" }}>{t.lg_unit_mismatch}</p>}
        {stt.self_reported_only && <p className="small">{t.lg_self_reported}</p>}
      </div>
      <div>
        <h3>{t.lg_anchors}</h3>
        {c.anchors.map((a) => <blockquote key={a.text}>“{a.text}” <span className="mono">({a.source_id})</span></blockquote>)}
        {c.notes && <p className="small" style={{ marginTop: ".5rem" }}>{c.notes}</p>}
      </div>
      <div>
        <h3>{t.lg_sources}</h3>
        <ul className="checklist">
          {srcs.map((s) => (
            <li key={s.id}><span className="mono">{s.id}</span> <a href={s.url} target="_blank" rel="noreferrer noopener">{s.title}</a> <span className={`chip${s.kind === "secondary-media" ? " media" : ""}`}>{t.src_kind[s.kind]}</span></li>
          ))}
        </ul>
      </div>
      <button className="btn ghost" onClick={onClose} style={{ justifySelf: "start" }}>{t.lg_close}</button>
    </div>
  );
}

export function Ledger() {
  const { t, lang, data } = useCtx();
  const [q, setQ] = useState(""), [jur, setJur] = useState(""), [stat, setStat] = useState(""), [band, setBand] = useState("");
  const [open, setOpen] = useState<string | null>(null);
  const rows = data.commitments.filter((c) => {
    const s = data.statuses.find((x) => x.commitment_id === c.id)!;
    const k = data.scores.find((x) => x.commitment_id === c.id)!;
    const hay = `${c.id} ${c.title} ${c.title_ar} ${c.statement} ${c.tags.join(" ")}`.toLowerCase();
    return (!q || hay.includes(q.toLowerCase())) && (!jur || c.jurisdiction === jur) && (!stat || s.status === stat) && (!band || k.band === band);
  });
  const exportCsv = () => {
    const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const head = ["id", "title", "jurisdiction", "kind", "owner", "target", "unit", "deadline", "status", "verifiability", "band"];
    const lines = rows.map((c) => {
      const s = data.statuses.find((x) => x.commitment_id === c.id)!, k = data.scores.find((x) => x.commitment_id === c.id)!;
      return [c.id, c.title, c.jurisdiction, c.kind, c.owner, c.target_value, c.unit, c.deadline ?? c.deadline_text, s.status, k.ratio, k.band].map(esc).join(",");
    });
    download("mutabaa-ledger.csv", "﻿" + [head.join(","), ...lines].join("\n"), "text/csv;charset=utf-8");
  };
  const opts = (o: Record<string, string>) => Object.entries(o).map(([k, v]) => <option key={k} value={k}>{v}</option>);
  return (
    <>
      <Head title={t.lg_title} sub={t.lg_sub} />
      <div className="filters" role="search">
        <label className="field">{t.lg_search}<input type="search" value={q} onChange={(e) => setQ(e.target.value)} /></label>
        <label className="field">{t.lg_jur}<select value={jur} onChange={(e) => setJur(e.target.value)}><option value="">{t.lg_all}</option>{opts(t.jur)}</select></label>
        <label className="field">{t.lg_status}<select value={stat} onChange={(e) => setStat(e.target.value)}><option value="">{t.lg_all}</option>{opts(t.st)}</select></label>
        <label className="field">{t.lg_band}<select value={band} onChange={(e) => setBand(e.target.value)}><option value="">{t.lg_all}</option>{opts(t.band)}</select></label>
        <button className="btn ghost" onClick={exportCsv}>{t.lg_export_csv}</button>
        <button className="btn ghost" onClick={() => download("mutabaa-data.json", JSON.stringify({ commitments: rows }, null, 1), "application/json")}>{t.lg_export_json}</button>
      </div>
      <div className="table-wrap">
        <table className="ledger">
          <thead><tr><th>ID</th><th>{t.lg_title}</th><th>{t.lg_jur}</th><th>{t.lg_checks}</th><th>{t.lg_status}</th></tr></thead>
          <tbody>
            {rows.length === 0 && <tr><td colSpan={5}>{t.lg_none}</td></tr>}
            {rows.map((c) => {
              const s = data.statuses.find((x) => x.commitment_id === c.id)!, k = data.scores.find((x) => x.commitment_id === c.id)!;
              const isOpen = open === c.id;
              return [
                <tr key={c.id} className={`row${isOpen ? " open" : ""}`} onClick={() => setOpen(isOpen ? null : c.id)}>
                  <td className="id">{c.id}</td>
                  <td><button className="title" aria-expanded={isOpen} onClick={(e) => { e.stopPropagation(); setOpen(isOpen ? null : c.id); }}>{L(lang, c.title, c.title_ar)}</button>
                    <div className="small">{t.kinds[c.kind]}</div></td>
                  <td>{t.jur[c.jurisdiction]}</td>
                  <td><Ticks score={k} /><div className="small">{t.band[k.band]}</div></td>
                  <td><StatusPill s={s.status} /></td>
                </tr>,
                isOpen && <tr key={c.id + "d"} className="open"><td /><td colSpan={4}><Detail c={c} onClose={() => setOpen(null)} /></td></tr>,
              ];
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ------------------------------------------------------------------ clocks

export function Clocks() {
  const { t, lang, data } = useCtx();
  const dated = data.commitments.filter((c) => c.deadline).sort((a, b) => (a.deadline as string).localeCompare(b.deadline as string));
  const undated = data.commitments.filter((c) => !c.deadline && c.kind !== "projection");
  const start = new Date("2025-01-01").getTime(), end = new Date("2031-12-31").getTime();
  const pos = (iso: string | number) => `${((new Date(iso).getTime() - start) / (end - start)) * 100}%`;
  return (
    <>
      <Head title={t.ck_title} sub={t.ck_sub} />
      <section className="panel">
        <h2>{t.ck_dated}</h2>
        <div role="table">
          {dated.map((c) => (
            <div className="clock" role="row" key={c.id}>
              <span><b className="mono">{c.id}</b> {L(lang, c.title, c.title_ar)}</span>
              <span className="track" aria-hidden><span className="now" style={{ insetInlineStart: pos(TODAY.getTime()) }} /><span className="mark" style={{ insetInlineStart: pos(c.deadline as string) }} /></span>
              <span className="small">{c.deadline} · {t.ck_days(dayDiff(c.deadline as string))}</span>
            </div>
          ))}
        </div>
        <p className="small">2025 → 2031. {t.ck_today}: {TODAY.toISOString().slice(0, 10)}</p>
      </section>
      <section className="panel">
        <h2>{t.ck_undated}</h2>
        <ul className="checklist">
          {undated.map((c) => (
            <li key={c.id}><b className="mono">{c.id}</b> {L(lang, c.title, c.title_ar)} <span className="small muted">{c.deadline_text ?? t.lg_not_stated}</span></li>
          ))}
        </ul>
      </section>
    </>
  );
}

// ------------------------------------------------------------------ lab

const useItems = () => {
  const { data } = useCtx();
  const [csv, setCsv] = useState<{ items: Item[]; errors: string[]; name: string } | null>(null);
  const [source, setSource] = useState<"syn" | "csv">("syn");
  const items = source === "csv" && csv && csv.items.length ? csv.items : data.synthetic.items;
  const kind: "synthetic" | "yours" = source === "csv" && csv && csv.items.length ? "yours" : "synthetic";
  return { items, kind, csv, setCsv, source, setSource };
};

function CsvLoader({ h }: { h: ReturnType<typeof useItems> }) {
  const { t } = useCtx();
  const onFile = async (f: File | undefined) => {
    if (!f) return;
    const r = parseCsv(await f.text());
    h.setCsv({ ...r, name: f.name });
    h.setSource("csv");
  };
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
          {h.csv && <p className="small">{h.csv.name}: {t.lb_loaded(h.csv.items.length)}</p>}
          {h.csv && h.csv.errors.length > 0 && (
            <div><b>{t.lb_errors(h.csv.errors.length)}</b>
              <ul className="errlist">{h.csv.errors.slice(0, 8).map((e) => <li key={e}>{e}</li>)}</ul></div>
          )}
        </>
      )}
    </div>
  );
}

export function Lab() {
  const { t, lang } = useCtx();
  const h = useItems();
  const [d, setD] = useState<Definition>({ unit: "services", scope: "all-services", threshold: 3, guardrails: "none" });
  const result = share(h.items, d);
  const rows = useMemo(() => allDefinitions().map((x) => ({ d: x, share: share(h.items, x) })), [h.items]);
  const vals = rows.map((r) => r.share).filter((v): v is number => v !== null);
  const marg = <K extends keyof Definition>(key: K, values: readonly Definition[K][]) =>
    values.map((v) => {
      const sel = rows.filter((r) => r.d[key] === v && r.share !== null).map((r) => r.share as number);
      return { v, avg: sel.length ? sel.reduce((a, b) => a + b, 0) / sel.length : 0 };
    });
  const unitName = (u: string) => (t as unknown as Record<string, string>)[`u_${u}`];
  const scopeName = (s: Definition["scope"]) => ({ "citizen-services": t.s_citizen, "all-services": t.s_all, "services-and-operations": t.s_ops })[s];
  const seg = <K extends keyof Definition>(key: K, values: readonly Definition[K][], name: (v: Definition[K]) => string, label: string) => (
    <div className="field"><span id={`l-${key}`}>{label}</span>
      <div className="seg" role="group" aria-labelledby={`l-${key}`}>
        {values.map((v) => <button key={String(v)} aria-pressed={d[key] === v} onClick={() => setD({ ...d, [key]: v })}>{name(v)}</button>)}
      </div></div>
  );
  return (
    <>
      <Head title={t.lb_title} sub={t.lb_sub} />
      <SourceBanner kind={h.kind} />
      <CsvLoader h={h} />
      <section className="panel">
        <div className="cols">
          {seg("unit", UNITS, (v) => unitName(v), t.lb_unit)}
          {seg("scope", SCOPES, (v) => scopeName(v), t.lb_scope)}
          {seg("threshold", THRESHOLDS, (v) => `L${v}`, t.lb_threshold)}
          {seg("guardrails", GUARDRAILS, (v) => (v === "none" ? t.g_none : t.g_required), t.lb_guard)}
        </div>
        <p className="small">{t.lb_unit_help[d.unit]}</p>
      </section>
      <section className="panel" aria-live="polite">
        <div style={{ display: "flex", gap: "1rem", alignItems: "baseline", flexWrap: "wrap" }}>
          <span className="big-share">{result === null ? "n/a" : pct(result, 1)}</span>
          <span>{t.lb_result} · {t.lb_vs}</span>
          {result !== null && <span className={`verdict ${result >= 0.5 ? "meets" : "misses"}`}>{result >= 0.5 ? t.lb_meets : t.lb_misses}</span>}
        </div>
        {result === null && <p className="small">{t.lb_nodata}</p>}
        <Strip current={d} rows={rows.map((r) => ({ share: r.share, d: r.d }))} />
        <p className="small">{t.lb_sweep_ok}: {vals.length ? t.lb_range(pct(Math.min(...vals), 1), pct(Math.max(...vals), 1)) : "n/a"}</p>
      </section>
      <section className="panel">
        <h2>{t.lb_marginal_title}</h2><p className="small">{t.lb_marginal_note}</p>
        <div className="bars">
          {[
            ...marg("unit", UNITS).map((m) => ({ k: "u" + m.v, label: unitName(m.v as string), avg: m.avg })),
            ...marg("scope", SCOPES).map((m) => ({ k: "s" + m.v, label: scopeName(m.v as Definition["scope"]), avg: m.avg })),
            ...marg("threshold", THRESHOLDS).map((m) => ({ k: "t" + m.v, label: `${t.lb_threshold} L${m.v}`, avg: m.avg })),
            ...marg("guardrails", GUARDRAILS).map((m) => ({ k: "g" + m.v, label: `${t.lb_guard}: ${m.v === "none" ? t.g_none : lang === "ar" ? "مطلوبة" : "required"}`, avg: m.avg })),
          ].map((b) => (
            <div className="bar" key={b.k}><span>{b.label}</span>
              <span className="track"><span className={`fill${h.kind === "synthetic" ? " syn" : ""}`} style={{ width: `${b.avg * 100}%` }} /></span>
              <b>{pct(b.avg)}</b></div>
          ))}
        </div>
      </section>
    </>
  );
}

// ------------------------------------------------------------------ maturity

export function Maturity() {
  const { t } = useCtx();
  const h = useItems();
  const n = h.items.length;
  const by = [0, 1, 2, 3, 4].map((m) => h.items.filter((i) => i.maturity === m));
  const high = h.items.filter((i) => i.maturity >= 3);
  const lacking = high.filter((i) => !(i.oversight && i.audit_trail && i.uae_residency && i.fallback));
  const flags: [string, keyof Item][] = [[t.mt_oversight, "oversight"], [t.mt_audit, "audit_trail"], [t.mt_residency, "uae_residency"], [t.mt_fallback, "fallback"]];
  return (
    <>
      <Head title={t.mt_title} sub={t.mt_sub} />
      <SourceBanner kind={h.kind} />
      <CsvLoader h={h} />
      <section className="panel">
        <h2>{t.mt_ladder}</h2>
        <ol className="ladder">{t.mt_levels.map((l, i) => <li key={l}><b>{i}</b><span>{l}</span></li>)}</ol>
      </section>
      <section className="panel">
        <h2>{t.mt_dist}</h2>
        <div className="bars">
          {by.map((g, i) => (
            <div className="bar" key={i}><span>L{i} · {t.mt_levels[i]}</span>
              <span className="track"><span className={`fill${h.kind === "synthetic" ? " syn" : ""}`} style={{ width: `${(g.length / Math.max(1, n)) * 100}%` }} /></span>
              <b>{g.length}</b></div>
          ))}
        </div>
      </section>
      <section className="panel">
        <h2>{t.mt_flags}</h2>
        <p><b>{t.mt_gap(lacking.length, high.length)}</b></p>
        <div className="cols">
          {flags.map(([label, key]) => (
            <div key={key}><h3>{label}</h3>
              <div className="bars">{[0, 1, 2, 3, 4].map((m) => {
                const g = by[m]; const v = g.length ? g.filter((i) => i[key]).length / g.length : 0;
                return <div className="bar" key={m} style={{ gridTemplateColumns: "2.2rem 1fr 3rem" }}><span>L{m}</span>
                  <span className="track"><span className={`fill${h.kind === "synthetic" ? " syn" : ""}`} style={{ width: `${v * 100}%` }} /></span><b>{g.length ? pct(v) : "-"}</b></div>;
              })}</div></div>
          ))}
        </div>
      </section>
    </>
  );
}

// ------------------------------------------------------------------ brief

export function Brief() {
  const { t, lang, data } = useCtx();
  const byStatus = (s: string) => data.statuses.filter((x) => x.status === s).length;
  const worst = [...data.commitments]
    .filter((c) => c.kind === "target" || c.kind === "milestone" || c.kind === "input")
    .map((c) => ({ c, k: data.scores.find((s) => s.commitment_id === c.id)! }))
    .sort((a, b) => a.k.ratio - b.k.ratio).slice(0, 5);
  const vals = data.sweep.map((r) => r.share).filter((v): v is number => v !== null);
  return (
    <>
      <Head title={t.br_title} sub={t.br_sub} />
      <button className="btn no-print" style={{ justifySelf: "start" }} onClick={() => window.print()}>{t.br_print}</button>
      <section className="panel">
        <h2>{t.br_findings}</h2>
        <ul style={{ margin: 0, paddingInlineStart: "1.1rem", display: "grid", gap: ".4rem" }}>
          {(Object.keys(t.st) as (keyof typeof t.st)[]).map((k) => <li key={k}>{t.st[k]}: <b>{byStatus(k)}</b> / {data.commitments.length}</li>)}
          <li>{t.ov_stat_claims}: <b>{data.claims.length}</b></li>
        </ul>
      </section>
      <section className="panel">
        <h2>{t.br_gaps}</h2>
        <ul className="checklist">
          {worst.map(({ c, k }) => (
            <li key={c.id}><Ticks score={k} /> <span><b className="mono">{c.id}</b> {L(lang, c.title, c.title_ar)}</span></li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <div style={{ display: "flex", gap: ".6rem", alignItems: "center" }}><h2>{t.ov_strip_title}</h2><span className="badge synthetic">{t.synthetic}</span></div>
        <p>{t.ov_title(pct(Math.min(...vals)), pct(Math.max(...vals)))}</p>
        <p className="small">{t.br_note_synth}</p>
      </section>
      <p className="small">{t.br_generated} {data.sources[0].retrieved}.</p>
    </>
  );
}

// ------------------------------------------------------------------ method

export function Method() {
  const { t } = useCtx();
  return (
    <>
      <Head title={t.me_title} sub={t.me_sub} />
      <section className="panel"><h2>{t.me_score}</h2><p>{t.me_score_text}</p>
        <ul className="checklist">{Object.values(t.checks).map((c) => <li key={c}>{c}</li>)}</ul></section>
      <section className="panel"><h2>{t.me_status}</h2>
        <ol style={{ margin: 0, paddingInlineStart: "1.2rem", display: "grid", gap: ".4rem", maxWidth: "68ch" }}>{t.me_status_list.map((s) => <li key={s}>{s}</li>)}</ol></section>
      <section className="panel"><h2>{t.me_data}</h2><p>{t.me_data_text}</p></section>
      <section className="panel"><h2>{t.me_limits}</h2>
        <ul style={{ margin: 0, paddingInlineStart: "1.1rem", display: "grid", gap: ".4rem", maxWidth: "68ch" }}>{t.me_limits_list.map((s) => <li key={s}>{s}</li>)}</ul>
        <p className="small"><a href="https://github.com/hudasol/mutabaa" target="_blank" rel="noreferrer noopener">{t.me_repo}</a></p></section>
    </>
  );
}

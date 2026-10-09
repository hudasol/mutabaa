import { Fragment, useMemo } from "react";
import { copyText, download, L, pct, useCtx } from "../ctx";
import { sortCommitments, type SortKey } from "../ledgerSort";
import { CopyLink, Head, StatusPill, Ticks, VerifyChip } from "../parts";
import type { Commitment } from "../types";

function Detail({ c, onClose }: { c: Commitment; onClose: () => void }) {
  const { t, lang, data } = useCtx();
  const sc = data.scores.find((s) => s.commitment_id === c.id)!;
  const stt = data.statuses.find((s) => s.commitment_id === c.id)!;
  const cov = data.coverage.find((s) => s.commitment_id === c.id);
  const qs = data.questions[c.id] ?? [];
  const ev = data.evidence.filter((e) => e.commitment_ids.includes(c.id));
  const srcs = data.sources.filter((s) => c.source_ids.includes(s.id));
  const ns = t.lg_not_stated;
  const searches = data.searches.filter((q) => q.commitment_ids.includes(c.id));
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

      <div className="searched">
        <StatusPill s={stt.status} />
        <span className="small">
          {cov && cov.searches > 0 && cov.last_searched ? t.lg_coverage(cov.searches, cov.last_searched) : t.lg_not_searched}
          {stt.evidence_age_days !== null && ` ${t.lg_age(stt.evidence_age_days)}`}
          {stt.stale && <b className="stale"> {t.lg_stale}</b>}
        </span>
      </div>

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
        <div className="row-between"><h3>{t.lg_questions}</h3>
          {qs.length > 0 && <button className="btn ghost" onClick={() => copyText(qs.map((q, i) => `${i + 1}. ${L(lang, q.en, q.ar)}`).join("\n"))}>{t.lg_copy_q}</button>}
        </div>
        {qs.length === 0 ? <p className="small">{t.lg_no_q}</p> : <ol className="qlist">{qs.map((q) => <li key={q.en}>{L(lang, q.en, q.ar)}</li>)}</ol>}
      </div>

      <div>
        <h3>{t.lg_evidence}</h3>
        {ev.length === 0 && <p className="small">{t.lg_no_evidence}</p>}
        <div className="evlist">
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
                {excluded && <div className="small flag">{t.lg_excluded}</div>}
              </div>
            );
          })}
        </div>
        {stt.unit_mismatch && <p className="small">{t.lg_unit_mismatch}</p>}
        {stt.self_reported_only && <p className="small">{t.lg_self_reported}</p>}
        {searches.length > 0 && (
          <ul className="searchlist">
            {searches.map((q) => <li key={q.id}><span className="chip">{q.id}</span> {t.oc[q.outcome]}. <span className="muted">{q.note}</span></li>)}
          </ul>
        )}
      </div>

      <div>
        <h3>{t.lg_anchors}</h3>
        {c.anchors.map((a) => <blockquote key={a.text}>“{a.text}” <span className="mono">({a.source_id})</span></blockquote>)}
        {c.notes && <p className="small">{c.notes}</p>}
      </div>
      <div>
        <h3>{t.lg_sources}</h3>
        <ul className="checklist">
          {srcs.map((s) => (
            <li key={s.id}><span className="mono">{s.id}</span> <a href={s.url} target="_blank" rel="noreferrer noopener">{s.title}</a>{" "}
              <span className={`chip${s.kind === "secondary-media" ? " media" : ""}`}>{t.src_kind[s.kind]}</span> <VerifyChip sourceId={s.id} /></li>
          ))}
        </ul>
      </div>
      <div className="row">
        <CopyLink />
        <button className="btn ghost" onClick={onClose}>{t.lg_close}</button>
      </div>
    </div>
  );
}

export default function Ledger() {
  const { t, lang, data, route, setParams } = useCtx();
  const p = route.params;
  const q = p.q ?? "", jur = p.j ?? "", stat = p.st ?? "", band = p.b ?? "";
  const sortKey = (p.s as SortKey) || "id", dir = (p.d as "asc" | "desc") || "asc", group = p.g === "1";
  const open = p.open ?? null;

  const filtered = useMemo(() => data.commitments.filter((c) => {
    const s = data.statuses.find((x) => x.commitment_id === c.id)!;
    const k = data.scores.find((x) => x.commitment_id === c.id)!;
    const hay = `${c.id} ${c.title} ${c.title_ar} ${c.statement} ${c.tags.join(" ")}`.toLowerCase();
    return (!q || hay.includes(q.toLowerCase())) && (!jur || c.jurisdiction === jur) && (!stat || s.status === stat) && (!band || k.band === band);
  }), [data, q, jur, stat, band]);
  const rows = useMemo(() => sortCommitments(filtered, data.scores, data.statuses, sortKey, dir, lang), [filtered, data, sortKey, dir, lang]);

  const exportCsv = () => {
    const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const head = ["id", "title", "jurisdiction", "kind", "owner", "target", "unit", "deadline", "status", "specification_score", "band", "data_as_of"];
    const lines = rows.map((c) => {
      const s = data.statuses.find((x) => x.commitment_id === c.id)!, k = data.scores.find((x) => x.commitment_id === c.id)!;
      return [c.id, c.title, c.jurisdiction, c.kind, c.owner, c.target_value, c.unit, c.deadline ?? c.deadline_text, s.status, k.ratio, k.band, data.build.data_as_of].map(esc).join(",");
    });
    download("mutabaa-ledger.csv", "﻿" + [head.join(","), ...lines].join("\n"), "text/csv;charset=utf-8");
  };
  const opts = (o: Record<string, string>) => Object.entries(o).map(([k, v]) => <option key={k} value={k}>{v}</option>);
  const toggle = (k: SortKey) => setParams(sortKey === k ? { d: dir === "asc" ? "desc" : "asc" } : { s: k, d: "asc" });
  const ariaSort = (k: SortKey) => (sortKey === k ? (dir === "asc" ? "ascending" : "descending") : "none");
  const arrow = (k: SortKey) => (sortKey === k ? (dir === "asc" ? " ↑" : " ↓") : "");

  const renderRow = (c: Commitment) => {
    const s = data.statuses.find((x) => x.commitment_id === c.id)!, k = data.scores.find((x) => x.commitment_id === c.id)!;
    const isOpen = open === c.id;
    return (
      <Fragment key={c.id}>
        <tr className={`row${isOpen ? " open" : ""}`} onClick={() => setParams({ open: isOpen ? undefined : c.id })}>
          <td className="id">{c.id}</td>
          <td><button className="title" aria-expanded={isOpen} onClick={(e) => { e.stopPropagation(); setParams({ open: isOpen ? undefined : c.id }); }}>{L(lang, c.title, c.title_ar)}</button>
            <div className="small">{t.kinds[c.kind]}</div></td>
          <td>{t.jur[c.jurisdiction]}</td>
          <td><Ticks score={k} /><div className="small">{t.band[k.band]}</div></td>
          <td><StatusPill s={s.status} />{s.stale && <div className="small flag">{t.lg_stale}</div>}</td>
        </tr>
        {isOpen && <tr className="open"><td /><td colSpan={4}><Detail c={c} onClose={() => setParams({ open: undefined })} /></td></tr>}
      </Fragment>
    );
  };

  const groups = group ? (["federal", "abu-dhabi", "national"] as const).map((j) => [j, rows.filter((r) => r.jurisdiction === j)] as const) : null;

  return (
    <>
      <Head title={t.lg_title} sub={t.lg_sub} />
      <div className="filters" role="search">
        <label className="field">{t.lg_search}<input type="search" value={q} onChange={(e) => setParams({ q: e.target.value })} /></label>
        <label className="field">{t.lg_jur}<select value={jur} onChange={(e) => setParams({ j: e.target.value })}><option value="">{t.lg_all}</option>{opts(t.jur)}</select></label>
        <label className="field">{t.lg_status}<select value={stat} onChange={(e) => setParams({ st: e.target.value })}><option value="">{t.lg_all}</option>{opts(t.st)}</select></label>
        <label className="field">{t.lg_band}<select value={band} onChange={(e) => setParams({ b: e.target.value })}><option value="">{t.lg_all}</option>{opts(t.band)}</select></label>
        <label className="check"><input type="checkbox" checked={group} onChange={(e) => setParams({ g: e.target.checked ? "1" : undefined })} />{t.lg_group}</label>
        <button className="btn ghost" onClick={exportCsv}>{t.lg_export_csv}</button>
        <button className="btn ghost" onClick={() => download("mutabaa-data.json", JSON.stringify({ build: data.build, commitments: rows }, null, 1), "application/json")}>{t.lg_export_json}</button>
        <CopyLink />
      </div>
      <p className="small band-help">{t.band_help}</p>
      <div className="table-wrap">
        <table className="ledger">
          <thead><tr>
            <th aria-sort={ariaSort("id")}><button className="th" onClick={() => toggle("id")}>ID{arrow("id")}</button></th>
            <th aria-sort={ariaSort("title")}><button className="th" onClick={() => toggle("title")}>{t.lg_col_commitment}{arrow("title")}</button></th>
            <th>{t.lg_jur}</th>
            <th aria-sort={ariaSort("checks")}><button className="th" onClick={() => toggle("checks")}>{t.lg_checks}{arrow("checks")}</button></th>
            <th aria-sort={ariaSort("status")}><button className="th" onClick={() => toggle("status")}>{t.lg_status}{arrow("status")}</button></th>
          </tr></thead>
          <tbody>
            {rows.length === 0 && <tr><td colSpan={5}>{t.lg_none}</td></tr>}
            {groups
              ? groups.map(([j, list]) => list.length > 0 && (
                <Fragment key={j}><tr className="group-row"><th colSpan={5}>{t.jur[j]} · {list.length}</th></tr>{list.map(renderRow)}</Fragment>))
              : rows.map(renderRow)}
          </tbody>
        </table>
      </div>
    </>
  );
}

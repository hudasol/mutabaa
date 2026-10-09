import { useMemo } from "react";
import { L, pct, useCtx } from "../ctx";
import { Head, Strip, Ticks } from "../parts";
import { buildHash } from "../route";
import type { Definition, Status } from "../types";

const ORDER = ["federal", "abu-dhabi", "national"] as const;

export default function Overview() {
  const { t, lang, data } = useCtx();
  const stat = useMemo(() => new Map(data.statuses.map((s) => [s.commitment_id, s])), [data]);
  const score = useMemo(() => new Map(data.scores.map((s) => [s.commitment_id, s])), [data]);
  const nopub = data.statuses.filter((s) => s.status === "no-public-evidence").length;
  const under = data.scores.filter((s) => s.band === "not-yet-checkable").length;
  const rows = useMemo(() => data.sweep.map((r) => ({ share: r.share, d: r as Definition })), [data]);
  const vals = rows.map((r) => r.share).filter((v): v is number => v !== null);
  const lo = Math.min(...vals), hi = Math.max(...vals);

  const evKinds = useMemo(() => {
    const kind = new Map(data.sources.map((s) => [s.id, s.kind]));
    const c = { official: 0, self: 0, media: 0 };
    for (const e of data.evidence) {
      const k = kind.get(e.source_id);
      if (k === "official-statement") c.official++; else if (k === "official-self-report") c.self++; else c.media++;
    }
    return c;
  }, [data]);
  const totalEv = evKinds.official + evKinds.self + evKinds.media;
  const ver = Object.values(data.verification.results);
  const verified = ver.filter((r) => r.result === "verified").length;

  return (
    <>
      <Head title={t.ov_title(nopub, under, data.commitments.length)} sub={t.ov_sub2} />

      <section aria-labelledby="glance-h" className="glance">
        <div className="glance-head">
          <h2 id="glance-h">{t.ov_glance}</h2>
          <p className="small">{t.ov_glance_note}</p>
        </div>
        {ORDER.map((j) => {
          const list = data.commitments.filter((c) => c.jurisdiction === j);
          return (
            <div key={j} className="tile-group">
              <h3>{t.jur[j]} <span className="muted">{list.length}</span></h3>
              <div className="tiles">
                {list.map((c, i) => {
                  const s = stat.get(c.id) as { status: Status["status"] };
                  const sc = score.get(c.id)!;
                  return (
                    <a key={c.id} className={`tile s-${s.status}`} style={{ ["--i" as string]: i }}
                      href={buildHash("ledger", { open: c.id })}
                      aria-label={`${c.id}. ${L(lang, c.title, c.title_ar)}. ${t.st[s.status]}. ${t.band[sc.band]}`}>
                      <span className="tile-top"><b className="mono">{c.id}</b><Ticks score={sc} /></span>
                      <span className="tile-title">{L(lang, c.title, c.title_ar)}</span>
                    </a>
                  );
                })}
              </div>
            </div>
          );
        })}
        <div className="legend" aria-hidden>
          {(Object.keys(t.st) as (keyof typeof t.st)[]).map((k) => <span key={k} className={`pill is-${k}${k === "not-checkable" ? " hatch" : ""}`}><i />{t.st[k]}</span>)}
        </div>
        <p className="small">{t.ov_marks} {t.band_help}</p>
      </section>

      <div className="cols two">
        <section className="panel" aria-labelledby="ev-h">
          <h2 id="ev-h">{t.ov_evidence_title}</h2>
          <div className="stack" role="img" aria-label={`${evKinds.official} / ${evKinds.self} / ${evKinds.media}`}>
            <span className="seg-official" style={{ flexGrow: evKinds.official }} />
            <span className="seg-self" style={{ flexGrow: evKinds.self }} />
            <span className="seg-media" style={{ flexGrow: evKinds.media }} />
          </div>
          <ul className="legend-list">
            <li><i className="sw seg-official" />{t.ev_official}: <b>{evKinds.official}</b></li>
            <li><i className="sw seg-self" />{t.ev_self}: <b>{evKinds.self}</b></li>
            <li><i className="sw seg-media" />{t.ev_media}: <b>{evKinds.media}</b></li>
          </ul>
          <p className="small">{t.ev_items(totalEv)}</p>
          <p><b>{t.ov_verified(verified, data.sources.length)}</b></p>
          <p className="small">{t.ov_unreach}</p>
          <a className="textlink" href={buildHash("sources")}>{t.nav_sources}</a>
        </section>

        <section className="panel" aria-labelledby="def-h">
          <div style={{ display: "flex", gap: ".6rem", alignItems: "center", flexWrap: "wrap" }}>
            <h2 id="def-h">{t.ov_def_title}</h2><span className="badge synthetic">{t.synthetic}</span>
          </div>
          <p><b>{t.ov_def_title2(pct(lo), pct(hi))}</b></p>
          <Strip rows={rows} label={t.ov_def_title} />
          <p className="small">{t.ov_def_note}</p>
          <p className="small">{t.ov_rob(data.analysis.robustness.registries, pct(data.analysis.robustness.flip_rate))}</p>
          <p className="row-between"><a className="textlink" href={buildHash("lab")}>{t.ov_def_cta}</a>
            <a className="textlink" href={buildHash("assurance")}>{t.ov_rob_cta}</a></p>
        </section>
      </div>

      <section className="panel">
        <h2>{t.ov_howto}</h2>
        <ul className="plainlist">{t.ov_why.map((w) => <li key={w}>{w}</li>)}</ul>
      </section>
    </>
  );
}

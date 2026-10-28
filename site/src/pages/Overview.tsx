import { useMemo } from "react";
import { L, pct, useCtx } from "../ctx";
import { Head, StatusPill, Strip } from "../parts";
import { buildHash } from "../route";
import type { Definition, Status } from "../types";

/** Commitments shown on the overview: those with the most checks missing. The ledger has all of them. */
const START_ROWS = 8;

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

  const withEvidence = data.statuses.length - nopub;
  const start = useMemo(() => data.commitments
    .map((c) => ({ c, s: score.get(c.id)!, st: stat.get(c.id) as { status: Status["status"] } }))
    .sort((x, y) => y.s.missing.length - x.s.missing.length || x.c.id.localeCompare(y.c.id))
    .slice(0, START_ROWS), [data, score, stat]);

  return (
    <>
      <Head title={t.ov_title(nopub, under, data.commitments.length)} sub={t.ov_sub2} />

      <dl className="figures">
        <div><dt>{t.ov_fig_commitments}</dt><dd>{data.commitments.length}</dd></div>
        <div><dt>{t.ov_fig_evidence}</dt><dd>{withEvidence}<small>/{data.commitments.length}</small></dd></div>
        <div><dt>{t.ov_fig_loose}</dt><dd>{under}<small>/{data.commitments.length}</small></dd></div>
        <div><dt>{t.ov_fig_sources}</dt><dd>{verified}<small>/{data.sources.length}</small></dd></div>
      </dl>

      <section aria-labelledby="start-h" className="start">
        <div className="row-between">
          <h2 id="start-h">{t.ov_start}</h2>
          <a className="textlink" href={buildHash("ledger")}>{t.ov_all(data.commitments.length)}</a>
        </div>
        <p className="small">{t.ov_start_note}</p>
        <div className="table-wrap" tabIndex={0} role="region" aria-label={t.ov_start}>
          <table className="ledger">
            <thead><tr>
              <th scope="col">ID</th><th scope="col">{t.lg_col_commitment}</th>
              <th scope="col">{t.ov_col_missing}</th><th scope="col">{t.lg_status}</th>
            </tr></thead>
            <tbody>
              {start.map(({ c, s, st }) => (
                <tr key={c.id}>
                  <td className="mono"><a href={buildHash("ledger", { open: c.id })}>{c.id}</a></td>
                  <td>{L(lang, c.title, c.title_ar)}</td>
                  <td className="small">{s.missing.map((k) => t.checks[k as keyof typeof t.checks]).join("; ")}</td>
                  <td><StatusPill s={st.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
          <p className="small">{t.ev_items(totalEv)} {t.ov_verified(verified, data.sources.length)}</p>
          <a className="textlink" href={buildHash("sources")}>{t.nav_sources}</a>
        </section>

        <section className="panel" aria-labelledby="def-h">
          <div style={{ display: "flex", gap: ".6rem", alignItems: "center", flexWrap: "wrap" }}>
            <h2 id="def-h">{t.ov_def_title}</h2><span className="badge synthetic">{t.synthetic}</span>
          </div>
          <p><b>{t.ov_def_title2(pct(lo), pct(hi))}</b></p>
          <Strip rows={rows} label={t.ov_def_title} />
          <p className="small">{t.ov_def_note(data.sweep.length)}</p>
          <p className="small">{t.ov_rob(data.analysis.robustness.registries, pct(data.analysis.robustness.flip_rate))}</p>
          <p className="row-between"><a className="textlink" href={buildHash("lab")}>{t.ov_def_cta}</a>
            <a className="textlink" href={buildHash("assurance")}>{t.ov_rob_cta}</a></p>
        </section>
      </div>

    </>
  );
}

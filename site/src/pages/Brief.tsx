import { L, pct, useCtx } from "../ctx";
import { Head, Ticks } from "../parts";

export default function Brief() {
  const { t, lang, data } = useCtx();
  const byStatus = (s: string) => data.statuses.filter((x) => x.status === s).length;
  const ranked = [...data.commitments]
    .filter((c) => c.kind === "target" || c.kind === "milestone" || c.kind === "input")
    .map((c) => ({ c, k: data.scores.find((s) => s.commitment_id === c.id)! }))
    .sort((a, b) => a.k.ratio - b.k.ratio);
  const worst = ranked.slice(0, 5);
  const vals = data.sweep.map((r) => r.share).filter((v): v is number => v !== null);
  const ver = Object.values(data.verification.results).filter((r) => r.result === "verified").length;
  const topQ = worst.flatMap(({ c }) => (data.questions[c.id] ?? []).slice(0, 2).map((q) => ({ id: c.id, q })));
  return (
    <>
      <Head title={t.br_title} sub={t.br_sub} />
      <button className="btn no-print" style={{ justifySelf: "start" }} onClick={() => window.print()}>{t.br_print}</button>
      <section className="panel">
        <h2>{t.br_findings}</h2>
        <ul className="plainlist">
          {(Object.keys(t.st) as (keyof typeof t.st)[]).map((k) => <li key={k}>{t.st[k]}: <b>{byStatus(k)}</b> / {data.commitments.length}</li>)}
          <li>{t.ov_stat_claims}: <b>{data.claims.length}</b></li>
          <li>{t.br_verified}: <b>{ver}</b> / {data.sources.length}</li>
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
        <h2>{t.br_questions}</h2>
        <ol className="qlist">{topQ.map(({ id, q }) => <li key={q.en}><span className="mono">{id}</span> {L(lang, q.en, q.ar)}</li>)}</ol>
      </section>
      <section className="panel">
        <div className="row"><h2>{t.ov_def_title}</h2><span className="badge synthetic">{t.synthetic}</span></div>
        <p>{t.ov_def_title2(pct(Math.min(...vals)), pct(Math.max(...vals)))}</p>
        <p className="small">{t.br_note_synth}</p>
      </section>
      <p className="small">{t.ft_asof} {data.build.data_as_of}. {t.br_version}: <span className="mono">{data.build.payload_sha256.slice(0, 12)}</span></p>
    </>
  );
}

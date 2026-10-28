import { L, pct, useCtx } from "../ctx";
import { questionsFor } from "../commitments";
import { Head, StatusPill, Ticks } from "../parts";

/** Commitments taken into the meeting, and questions listed under each. */
const ITEMS = 5;
const PER_ITEM = 3;

export default function Brief() {
  const { t, lang, data } = useCtx();
  const byStatus = (s: string) => data.statuses.filter((x) => x.status === s).length;
  const status = new Map(data.statuses.map((s) => [s.commitment_id, s.status]));
  const ranked = [...data.commitments]
    .filter((c) => c.kind === "target" || c.kind === "milestone" || c.kind === "input")
    .map((c) => ({ c, k: data.scores.find((s) => s.commitment_id === c.id)! }))
    .sort((a, b) => a.k.ratio - b.k.ratio)
    .slice(0, ITEMS);
  const vals = data.sweep.map((r) => r.share).filter((v): v is number => v !== null);
  const ver = Object.values(data.verification.results).filter((r) => r.result === "verified").length;
  // The heading names the commitment, so the questions refer to it as "this commitment".
  const plain = (s: string) => s.replace(/[“«](this commitment|هذا الالتزام)[”»]/g, "$1");
  return (
    <>
      <Head title={t.br_title} sub={t.br_sub} />
      <button className="btn no-print" style={{ justifySelf: "start" }} onClick={() => window.print()}>{t.br_print}</button>

      <section aria-labelledby="br-f">
        <h2 id="br-f">{t.br_findings}</h2>
        <dl className="figures brief-figures">
          {(Object.keys(t.st) as (keyof typeof t.st)[]).map((k) => (
            <div key={k}><dt>{t.st[k]}</dt><dd>{byStatus(k)}<small>/{data.commitments.length}</small></dd></div>
          ))}
        </dl>
        <p className="small">{t.ov_stat_claims}: {data.claims.length}. {t.br_verified}: {ver} / {data.sources.length}.</p>
      </section>

      <section aria-labelledby="br-q">
        <h2 id="br-q">{t.br_questions}</h2>
        <div className="brief-items">
          {ranked.map(({ c, k }) => {
            const qs = questionsFor({ ...c, title: "this commitment", title_ar: "هذا الالتزام" }, k).slice(0, PER_ITEM);
            return (
              <article key={c.id} className="brief-item">
                <header>
                  <Ticks score={k} />
                  <h3><span className="mono">{c.id}</span> {L(lang, c.title, c.title_ar)}</h3>
                  <StatusPill s={status.get(c.id) as never} />
                </header>
                <ul>{qs.map((q, i) => <li key={i}>{plain(L(lang, q.en, q.ar))}</li>)}</ul>
              </article>
            );
          })}
        </div>
      </section>

      <section aria-labelledby="br-d">
        <div className="row"><h2 id="br-d">{t.ov_def_title}</h2><span className="badge synthetic">{t.synthetic}</span></div>
        <p>{t.ov_def_title2(pct(Math.min(...vals)), pct(Math.max(...vals)))}</p>
      </section>
      <p className="small">{t.ft_asof} {data.build.data_as_of}. {t.br_version}: <span className="mono">{data.build.payload_sha256.slice(0, 12)}</span></p>
    </>
  );
}

import { useCtx } from "../ctx";
import { Head } from "../parts";

export default function Method() {
  const { t } = useCtx();
  return (
    <>
      <Head title={t.me_title} sub={t.me_sub} />
      <section className="panel"><h2>{t.me_score}</h2><p>{t.me_score_text}</p>
        <ul className="checklist">{Object.values(t.checks).map((c) => <li key={c}>{c}</li>)}</ul></section>
      <section className="panel"><h2>{t.me_status}</h2>
        <ol className="plainlist">{t.me_status_list.map((s) => <li key={s}>{s}</li>)}</ol></section>
      <section className="panel"><h2>{t.me_data}</h2><p>{t.me_data_text}</p></section>
      <section className="panel"><h2>{t.me_limits}</h2>
        <ul className="plainlist">{t.me_limits_list.map((s) => <li key={s}>{s}</li>)}</ul>
        <p className="small"><a href="https://github.com/hudasol/mutabaa" target="_blank" rel="noreferrer noopener">{t.me_repo}</a></p></section>
    </>
  );
}

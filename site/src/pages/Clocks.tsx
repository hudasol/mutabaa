import { L, useCtx } from "../ctx";
import { Head } from "../parts";

const dayDiff = (iso: string, now: Date) => Math.round((new Date(iso).getTime() - now.getTime()) / 86400000);

export default function Clocks() {
  const { t, lang, data } = useCtx();
  const now = new Date(data.build.data_as_of);
  const dated = data.commitments.filter((c) => c.deadline).sort((a, b) => (a.deadline as string).localeCompare(b.deadline as string));
  const undated = data.commitments.filter((c) => !c.deadline && c.kind !== "projection");
  const start = new Date("2025-01-01").getTime(), end = new Date("2031-12-31").getTime();
  const pos = (iso: string | number) => `${((new Date(iso).getTime() - start) / (end - start)) * 100}%`;
  return (
    <>
      <Head title={t.ck_title} sub={t.ck_sub} />
      <section className="panel">
        <h2>{t.ck_dated}</h2>
        <ul className="clocks">
          {dated.map((c) => (
            <li className="clock" key={c.id}>
              <span><b className="mono">{c.id}</b> {L(lang, c.title, c.title_ar)}</span>
              <span className="track" aria-hidden><span className="now" style={{ insetInlineStart: pos(now.getTime()) }} /><span className="mark" style={{ insetInlineStart: pos(c.deadline as string) }} /></span>
              <span className="small">{c.deadline} · {t.ck_days(dayDiff(c.deadline as string, now))}</span>
            </li>
          ))}
        </ul>
        <p className="small">2025 → 2031. {t.ck_today}: {data.build.data_as_of}</p>
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

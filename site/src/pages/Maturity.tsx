import { pct, useCtx } from "../ctx";
import { CsvLoader, Head, SourceBanner, useItems } from "../parts";
import type { Item } from "../types";

export default function Maturity() {
  const { t } = useCtx();
  const h = useItems();
  const n = h.items.length;
  const by = [0, 1, 2, 3, 4].map((m) => h.items.filter((i) => i.maturity === m));
  const high = h.items.filter((i) => i.maturity >= 3);
  const lacking = high.filter((i) => !(i.oversight && i.audit_trail && i.uae_residency && i.fallback));
  const flags: [string, keyof Item][] = [[t.mt_oversight, "oversight"], [t.mt_audit, "audit_trail"], [t.mt_residency, "uae_residency"], [t.mt_fallback, "fallback"]];
  const syn = h.kind === "synthetic" ? " syn" : "";
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
              <span className="track"><span className={`fill${syn}`} style={{ width: `${(g.length / Math.max(1, n)) * 100}%` }} /></span>
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
                return <div className="bar narrow" key={m}><span>L{m}</span>
                  <span className="track"><span className={`fill${syn}`} style={{ width: `${v * 100}%` }} /></span><b>{g.length ? pct(v) : "-"}</b></div>;
              })}</div></div>
          ))}
        </div>
      </section>
    </>
  );
}

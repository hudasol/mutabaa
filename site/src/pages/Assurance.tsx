import { pct, useCtx } from "../ctx";
import { Head } from "../parts";

function Bars({ rows, cls = "" }: { rows: { k: string; label: string; v: number }[]; cls?: string }) {
  return (
    <div className="bars">
      {rows.map((r) => (
        <div className="bar" key={r.k}><span>{r.label}</span>
          <span className="track"><span className={`fill ${cls}`} style={{ width: `${Math.max(0, Math.min(1, r.v)) * 100}%` }} /></span>
          <b>{r.v > 0 && r.v < 0.005 ? "<1%" : pct(r.v)}</b></div>
      ))}
    </div>
  );
}

const f2 = (x: number | null) => (x === null ? "\u2013" : x.toFixed(2));

export default function Assurance() {
  const { t, data } = useCtx();
  const { robustness: rb, calibration: cal, agreement: ag } = data.analysis;
  const checks = Object.keys(cal.weights.pass_rate) as (keyof typeof t.checks)[];
  return (
    <>
      <Head title={t.as_title} sub={t.as_sub} />
      <p className="banner exploratory" role="note"><b>{t.as_exploratory_tag}.</b> {t.as_exploratory}</p>
      <section className="panel" aria-labelledby="rb-h">
        <div className="row-between"><h2 id="rb-h">{t.as_rob}</h2><span className="badge synthetic">{t.synthetic}</span></div>
        <p><b>{t.as_rob_text(rb.registries, pct(rb.flip_rate), rb.sizes.length, Object.keys(rb.profiles).length, rb.seeds[1] - rb.seeds[0] + 1)}</b></p>
        <h3>{t.as_rob_profile}</h3>
        <Bars cls="syn" rows={(["low", "mid", "high"] as (keyof typeof t.as_prof)[]).map((k) => ({ k, label: t.as_prof[k], v: rb.by_profile[k].flip_rate }))} />
        <p className="small">{t.as_rob_profile_note(pct(rb.by_profile.low.flip_rate), pct(rb.by_profile.mid.flip_rate), pct(rb.by_profile.high.flip_rate))}</p>
        <h3>{t.as_eff}</h3>
        <Bars cls="syn" rows={(["threshold", "guardrails", "unit", "scope"] as (keyof typeof t.as_eff_names)[]).map((k) => ({ k, label: t.as_eff_names[k], v: rb.effects[k] }))} />
      </section>
      <section className="panel" aria-labelledby="cal-h">
        <h2 id="cal-h">{t.as_cal}</h2>
        <h3>{t.as_pass}</h3>
        <Bars rows={checks.map((k) => ({ k, label: t.checks[k], v: cal.weights.pass_rate[k] ?? 0 }))} />
        <p className="small">{t.as_pass_note}</p>
        <p>{t.as_band(cal.bands.max_changed, cal.bands.n)}</p>
        <p>{t.as_weights(f2(cal.weights.spearman_median), f2(cal.weights.spearman_p05), cal.weights.draws.toLocaleString("en"))}</p>
        <h3>{t.as_cons}</h3>
        <ul className="plainlist">
          {(["numeric_target", "dated_deadline"] as const).map((k) => {
            const c = cal.consistency[k];
            return <li key={k}>{t.as_cons_line(t.as_cons_names[k], c.agree, c.n, f2(c.kappa), f2(c.ci95[0]), f2(c.ci95[1]))}</li>;
          })}
          <li className="small">{cal.consistency.disagreements.join(", ")}</li>
        </ul>
        <p className="small">{t.as_cons_note}</p>
      </section>
      <section className="panel" aria-labelledby="ag-h">
        <h2 id="ag-h">{t.as_agr}</h2>
        <p>{t.as_agr_line(ag.recall.found, ag.recall.n, pct(ag.recall.rate), pct(ag.recall.ci95[0]), pct(ag.recall.ci95[1]))} {t.as_agr_wilson(pct(ag.recall.wilson95[0]), pct(ag.recall.wilson95[1]))}</p>
        <p className="small">{t.as_boot_note(pct(data.evaluation.e4.bootstrap_coverage_at_095))}</p>
        <p>{t.as_agr_num(ag.numeric_recall.found, ag.numeric_recall.n, pct(ag.numeric_recall.rate))}</p>
        <p className="small">{t.as_agr_missed} <span className="mono">{ag.missed.join(", ")}</span></p>
        <p className="small">{t.as_agr_note} {t.as_small}</p>
      </section>
      <section className="panel" aria-labelledby="cmp-h">
        <h2 id="cmp-h">{t.as_cmp}</h2>
        <p>{t.as_cmp_intro(data.evaluation.e5.units, data.evaluation.e5.located)}</p>
        <div className="table-wrap" tabIndex={0} role="region" aria-label={t.as_cmp}>
          <table className="ledger">
            <thead><tr>
              <th scope="col">{t.as_cmp_cols.rule}</th><th scope="col">{t.as_cmp_cols.flagged}</th>
              <th scope="col">{t.as_cmp_cols.found}</th><th scope="col">{t.as_cmp_cols.numeric}</th>
              <th scope="col">{t.as_cmp_cols.other}</th><th scope="col">{t.as_cmp_cols.precision}</th>
            </tr></thead>
            <tbody>
              {(["x1", "x2", "x3", "x4"] as const).map((k) => {
                const r = data.evaluation.e5.rules[k];
                return (
                  <tr key={k}>
                    <th scope="row">{t.as_cmp_rules[k]}</th>
                    <td>{pct(r.flagged_share)}</td><td>{pct(r.recall)}</td>
                    <td>{pct(r.recall_numeric)}</td><td>{pct(r.recall_other)}</td><td>{pct(r.precision)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p>{t.as_cmp_blind(pct(data.evaluation.e5.blind_recall))}</p>
        <p className="small">{t.as_cmp_note}</p>
        <p>{t.as_inv(data.evaluation.e6.violations, data.evaluation.e6.killed, data.evaluation.e6.mutants)}</p>
      </section>
    </>
  );
}

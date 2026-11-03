import { useMemo, useState } from "react";
import { useCtx } from "../ctx";
import { lint, type LintFields } from "../lint";
import { Head, SourceBanner, Ticks } from "../parts";
import type { Score } from "../types";

const KINDS = ["target", "milestone", "deliverable", "assessment", "vision"] as const;

export default function Lint() {
  const { t, lang } = useCtx();
  const [text, setText] = useState("");
  const [kind, setKind] = useState<string>("target");
  const [ans, setAns] = useState({ number: "", unit: "", deadline: "", owner: "", source: "", terms: [] as string[] });
  const fields: LintFields = {
    target_number: ans.number.trim() !== "" && Number.isFinite(Number(ans.number)) ? Number(ans.number) : null,
    unit: ans.unit, deadline: ans.deadline, owner: ans.owner, measurement_source: ans.source, defined_terms: ans.terms,
  };
  const res = useMemo(() => (text.trim() === "" ? null : lint(text, kind, fields)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [text, kind, ans]);
  const f = res?.found;
  const row = (label: string, value: string | number | null) => (
    <div><dt>{label}</dt><dd>{value === null || value === "" ? <span className="small">{t.ln_not_stated}</span> : value}</dd></div>
  );
  const asScore = (s: NonNullable<typeof res>["before"]) => s as unknown as Score;
  return (
    <>
      <Head title={t.ln_title} sub={t.ln_sub} />
      <SourceBanner kind="yours" />
      <section className="panel" aria-labelledby="ln-in">
        <h2 id="ln-in">{t.ln_text}</h2>
        <p className="small">{t.ln_how}</p>
        <label className="field">{t.ln_text}
          <textarea rows={4} value={text} maxLength={4000} onChange={(e) => setText(e.target.value)} dir="auto" />
        </label>
        <label className="field">{t.ln_kind}
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {KINDS.map((k) => <option key={k} value={k}>{t.kinds[k]}</option>)}
          </select>
        </label>
        <p className="small"><b>{t.ln_examples}</b></p>
        <div className="row">
          {[t.ln_ex1, t.ln_ex2, t.ln_ex3].map((x) => (
            <button key={x} type="button" className="btn ghost" onClick={() => setText(x)} dir="ltr" lang="en">{x.length > 48 ? `${x.slice(0, 46)}…` : x}</button>
          ))}
        </div>
      </section>
      <section className="panel" aria-labelledby="ln-res" aria-live="polite">
        <h2 id="ln-res">{t.ln_found}</h2>
        {!res || !f ? <p>{t.ln_empty}</p> : (
          <>
            <dl className="kv quality">
              {row(t.ln_f_number, f.target_number)}
              {row(t.ln_f_unit, f.unit)}
              {row(t.ln_f_deadline, f.deadline_text)}
              {row(t.ln_f_owner, f.owner)}
              {row(t.ln_f_source, f.measurement_source)}
              {row(t.ln_f_terms, f.undefined_terms.length ? f.undefined_terms.join("; ") : t.ln_none)}
            </dl>
            <h3>{t.ln_before}</h3>
            <p><Ticks score={asScore(res.before)} /> {t.ln_checks_of(res.before.passed, res.before.applicable)}, {t.band[res.before.band]}</p>
            {res.after && (
              <>
                <h3>{t.ln_after}</h3>
                <p><Ticks score={asScore(res.after)} /> {t.ln_checks_of(res.after.passed, res.after.applicable)}, {t.band[res.after.band]}</p>
              </>
            )}
            <h3>{t.ln_questions}</h3>
            {res.questions.length === 0 ? <p>{t.ln_none_q}</p> : (
              <ol>{res.questions.map((q, i) => <li key={i}>{lang === "ar" ? q.ar : q.en}</li>)}</ol>
            )}
          </>
        )}
      </section>
      <section className="panel" aria-labelledby="ln-ans">
        <h2 id="ln-ans">{t.ln_answers}</h2>
        <p className="small">{t.ln_answers_help}</p>
        <div className="cols">
          <label className="field">{t.ln_a_number}
            <input type="text" inputMode="decimal" value={ans.number} onChange={(e) => setAns({ ...ans, number: e.target.value })} /></label>
          <label className="field">{t.ln_a_unit}
            <input type="text" value={ans.unit} onChange={(e) => setAns({ ...ans, unit: e.target.value })} /></label>
          <label className="field">{t.ln_a_deadline}
            <input type="text" value={ans.deadline} onChange={(e) => setAns({ ...ans, deadline: e.target.value })} /></label>
          <label className="field">{t.ln_a_owner}
            <input type="text" value={ans.owner} onChange={(e) => setAns({ ...ans, owner: e.target.value })} /></label>
          <label className="field">{t.ln_a_source}
            <input type="text" value={ans.source} onChange={(e) => setAns({ ...ans, source: e.target.value })} /></label>
        </div>
        {f && f.undefined_terms.length > 0 && (
          <fieldset className="field"><legend>{t.ln_a_terms}</legend>
            {f.undefined_terms.map((term) => (
              <label key={term} className="check">
                <input type="checkbox" checked={ans.terms.includes(term)}
                  onChange={(e) => setAns({ ...ans, terms: e.target.checked ? [...ans.terms, term] : ans.terms.filter((x) => x !== term) })} /> {term}
              </label>
            ))}
          </fieldset>
        )}
        <p className="small">{t.ln_limit}</p>
        <p className="small">{t.ln_ar_note}</p>
      </section>
    </>
  );
}

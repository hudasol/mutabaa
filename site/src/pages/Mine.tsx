import { useMemo, useState } from "react";
import { download, useCtx } from "../ctx";
import {
  MY_COLUMNS, MY_TEMPLATE, REQUIRED, convertRows, mapColumns, questionsFor, readMyFile, scoreCommitment,
  type MyColumn, type MyMapping, type MyResult,
} from "../commitments";
import { csvCell } from "../engine";
import { Head, SourceBanner, Ticks } from "../parts";

type Loaded = { name: string; headers: string[]; rows: string[][]; truncated: boolean };

export default function Mine() {
  const { t, lang } = useCtx();
  const [file, setFile] = useState<Loaded | null>(null);
  const [mapping, setMapping] = useState<MyMapping>({});
  const [result, setResult] = useState<MyResult | null>(null);
  const [readError, setReadError] = useState<string | null>(null);

  const onFile = async (f: File | undefined) => {
    if (!f) return;
    setReadError(null);
    try {
      const parsed = readMyFile(f.name, await f.text());
      const m = mapColumns(parsed.headers);
      setFile({ name: f.name, ...parsed }); setMapping(m);
      setResult(convertRows(parsed.headers, parsed.rows, m, parsed.truncated));
    } catch (e) {
      setFile(null); setResult(null); setReadError(e instanceof Error ? e.message : String(e));
    }
  };
  const scored = useMemo(
    () => (result?.items ?? []).map((c) => { const s = scoreCommitment(c); return { c, s, q: questionsFor(c, s) }; }),
    [result],
  );
  const missingRequired = REQUIRED.filter((c) => mapping[c] === undefined);
  const exportQuestions = () => {
    const head = ["id", "title", "check", "question_en", "question_ar"].map(csvCell).join(",");
    const lines = scored.flatMap(({ c, q }) => q.map((x) => [c.id, c.title, x.check, x.en, x.ar].map(csvCell).join(",")));
    download("mutabaa-questions.csv", "\uFEFF" + [head, ...lines].join("\r\n") + "\r\n", "text/csv");
  };
  const rep = result?.report;
  return (
    <>
      <Head title={t.my_title} sub={t.my_sub} />
      <SourceBanner kind="yours" />
      <section className="panel" aria-labelledby="my-load">
        <h2 id="my-load">{t.my_load}</h2>
        <label className="field">{t.my_upload}
          <input type="file" accept=".csv,.json,text/csv,application/json" onChange={(e) => onFile(e.target.files?.[0])} />
        </label>
        <p className="small">{t.my_help} <span className="mono">{MY_COLUMNS.join(", ")}</span></p>
        <p className="small">{t.my_terms_help}</p>
        <button className="btn ghost" style={{ justifySelf: "start" }} onClick={() => download("mutabaa-commitments-template.csv", MY_TEMPLATE, "text/csv")}>{t.lb_template}</button>
        {readError && <p className="small" role="alert"><b>{t.my_err_file}</b> {readError}</p>}
        {file && (
          <details className="mapper" open={missingRequired.length > 0}>
            <summary><b>{t.lb_map_title}</b></summary><p className="small">{t.lb_map_help}</p>
            <div className="cols">
              {MY_COLUMNS.map((c: MyColumn) => (
                <label className="field" key={c}><span className="mono">{c}{REQUIRED.includes(c) ? " *" : ""}</span>
                  <select value={mapping[c] ?? ""} onChange={(e) => {
                    const m = { ...mapping }; if (e.target.value === "") delete m[c]; else m[c] = Number(e.target.value); setMapping(m);
                  }}>
                    <option value="">{t.lb_pick}</option>
                    {file.headers.map((hd, i) => <option key={i} value={i}>{hd}</option>)}
                  </select></label>
              ))}
            </div>
            <button className="btn" style={{ justifySelf: "start", marginTop: ".75rem" }} disabled={missingRequired.length > 0}
              onClick={() => setResult(convertRows(file.headers, file.rows, mapping, file.truncated))}>{t.lb_apply}</button>
          </details>
        )}
        {rep && (
          <div>
            <h3>{t.lb_quality}</h3>
            <dl className="kv quality">
              <div><dt>{t.q_rows}</dt><dd>{rep.rows}</dd></div>
              <div><dt>{t.q_accepted}</dt><dd>{rep.accepted}</dd></div>
              <div><dt>{t.q_rejected}</dt><dd>{rep.rejected}</dd></div>
              <div><dt>{t.q_dupes}</dt><dd>{rep.duplicates}</dd></div>
            </dl>
            {result!.errors.length > 0 && (
              <div role="alert"><b>{t.lb_errors(result!.errors.length)}</b>
                <ul className="errlist">{result!.errors.slice(0, 8).map((e) => <li key={e}>{e}</li>)}</ul></div>
            )}
          </div>
        )}
      </section>
      <section className="panel" aria-labelledby="my-res" aria-live="polite">
        <div className="row-between"><h2 id="my-res">{t.my_results}</h2>
          {scored.length > 0 && <button className="btn" onClick={exportQuestions}>{t.my_export}</button>}</div>
        <p className="small">{t.my_no_status}</p>
        {scored.length === 0 ? <p>{t.my_empty}</p> : (
          <>
            <p>{t.my_count(scored.length)}</p>
            <div className="table-wrap" tabIndex={0} role="region" aria-label={t.my_results}>
              <table className="ledger">
                <thead><tr>
                  <th scope="col">{t.my_col_id}</th><th scope="col">{t.my_col_title}</th>
                  <th scope="col">{t.my_col_score}</th><th scope="col">{t.lg_band}</th><th scope="col">{t.my_col_missing}</th>
                </tr></thead>
                <tbody>
                  {scored.map(({ c, s }) => (
                    <tr key={c.id}>
                      <td className="mono">{c.id}</td>
                      <td>{c.title}</td>
                      <td><Ticks score={s} /> <span className="small">{s.passed} / {s.applicable}</span></td>
                      <td>{t.band[s.band]}</td>
                      <td>{s.missing.length ? s.missing.map((k) => t.checks[k as keyof typeof t.checks]).join("; ") : t.my_none_missing}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3>{t.my_questions}</h3>
            {scored.filter((x) => x.q.length > 0).map(({ c, q }) => (
              <details key={c.id} className="qblock">
                <summary><span className="mono">{c.id}</span> {c.title} <span className="small">({q.length})</span></summary>
                <ol>{q.map((x, i) => <li key={i}>{lang === "ar" ? x.ar : x.en}</li>)}</ol>
              </details>
            ))}
          </>
        )}
      </section>
    </>
  );
}

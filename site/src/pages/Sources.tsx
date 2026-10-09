import { useCtx } from "../ctx";
import { Head, VerifyChip } from "../parts";

export default function Sources() {
  const { t, data } = useCtx();
  return (
    <>
      <Head title={t.so_title} sub={t.so_sub} />
      <div className="table-wrap">
        <table className="ledger">
          <thead><tr><th>ID</th><th>{t.so_col_src}</th><th>{t.so_col_kind}</th><th>{t.so_col_date}</th><th>{t.so_col_check}</th><th>{t.so_col_figs}</th></tr></thead>
          <tbody>
            {data.sources.map((s) => {
              const v = data.verification.results[s.id];
              return (
                <tr key={s.id}>
                  <td className="id">{s.id}</td>
                  <td><a href={s.url} target="_blank" rel="noreferrer noopener">{s.title}</a>
                    <div className="small">{s.publisher}{s.ai_assisted ? ` · ${t.so_ai}` : ""}</div></td>
                  <td><span className={`chip${s.kind === "secondary-media" ? " media" : ""}`}>{t.src_kind[s.kind]}</span></td>
                  <td>{s.published ?? <span className="muted">{t.so_undated}</span>}</td>
                  <td><VerifyChip sourceId={s.id} />{v?.error && <div className="small muted">{v.error.slice(0, 70)}</div>}</td>
                  <td className="small">{v ? `${v.checked_present} + ${v.checked_absent}` : `${s.expect_present.length} + ${s.expect_absent.length}`}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="small">{t.so_how}</p>
    </>
  );
}

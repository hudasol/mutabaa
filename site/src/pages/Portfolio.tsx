import { useMemo } from "react";
import { pct, useCtx } from "../ctx";
import { PORTFOLIO_COLS, SCOPES, portfolio } from "../engine";
import { CsvLoader, Head, SourceBanner, useItems } from "../parts";
import type { Definition } from "../types";

const SORTS = ["name", "range", "share"] as const;
type Sort = (typeof SORTS)[number];

export default function Portfolio() {
  const { t, data, route, setParams } = useCtx();
  const h = useItems();
  const p = route.params;
  const scope = (SCOPES.find((s) => s === p.s) ?? "all-services") as Definition["scope"];
  const sort = (SORTS.find((s) => s === p.o) ?? "name") as Sort;
  const names = useMemo(() => new Map(data.synthetic.entities.map((e) => [e.id, e.name])), [data]);
  const rows = useMemo(() => {
    const r = portfolio(h.items, scope);
    const c3 = PORTFOLIO_COLS.findIndex((c) => c.threshold === 3 && c.guardrails === "none");
    if (sort === "range") r.sort((a, b) => (b.rankMax! - b.rankMin!) - (a.rankMax! - a.rankMin!) || a.entity.localeCompare(b.entity));
    if (sort === "share") r.sort((a, b) => (b.shares[c3] as number) - (a.shares[c3] as number) || a.entity.localeCompare(b.entity));
    return r;
  }, [h.items, scope, sort]);
  const moved = rows.filter((r) => r.rankMax! - r.rankMin! >= 3).length;
  const scopeName = (s: Definition["scope"]) => ({ "citizen-services": t.s_citizen, "all-services": t.s_all, "services-and-operations": t.s_ops })[s];
  const sortName: Record<Sort, string> = { name: t.pf_sort_name, range: t.pf_sort_range, share: t.pf_sort_share };
  const tone = h.kind === "synthetic" ? "var(--synthetic)" : "var(--yours)";
  return (
    <>
      <Head title={t.pf_title} sub={t.pf_sub} />
      <SourceBanner kind={h.kind} />
      <CsvLoader h={h} />
      <section className="panel">
        <div className="filters">
          <div className="field"><span id="pf-scope">{t.pf_scope}</span>
            <div className="seg" role="group" aria-labelledby="pf-scope">
              {SCOPES.map((s) => <button key={s} aria-pressed={scope === s} onClick={() => setParams({ s })}>{scopeName(s)}</button>)}
            </div></div>
          <div className="field"><span id="pf-sort">{t.pf_sort}</span>
            <div className="seg" role="group" aria-labelledby="pf-sort">
              {SORTS.map((s) => <button key={s} aria-pressed={sort === s} onClick={() => setParams({ o: s })}>{sortName[s]}</button>)}
            </div></div>
        </div>
        <p><b>{t.pf_note(rows.length, moved)}</b></p>
        <div className="table-wrap" tabIndex={0} role="region" aria-label={t.pf_title}>
          <table className="ledger heat">
            <thead>
              <tr>
                <th scope="col">{t.pf_entity}</th><th scope="col">{t.pf_range}</th><th scope="col">{t.pf_items}</th>
                {PORTFOLIO_COLS.map((c) => (
                  <th scope="col" key={`${c.threshold}${c.guardrails}`}>L{c.threshold}<br /><span className="muted">{c.guardrails === "none" ? t.pf_noguard : t.pf_guard}</span></th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.entity}>
                  <th scope="row"><span className="mono">{r.entity}</span> <span className="muted small ename">{names.get(r.entity) ?? r.sector}</span></th>
                  <td className="mono">{r.rankMin === r.rankMax ? `#${r.rankMin}` : `#${r.rankMin}–${r.rankMax}`}</td>
                  <td>{r.items}</td>
                  {r.shares.map((v, i) => (
                    <td key={i} className="cell" style={{ background: `color-mix(in srgb, ${tone} ${Math.round((v ?? 0) * 28)}%, transparent)` }}>
                      {pct(v)}<span className="muted small"> #{r.ranks[i]}</span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="small">{t.pf_caveat}</p>
      </section>
    </>
  );
}

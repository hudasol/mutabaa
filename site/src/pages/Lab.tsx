import { useMemo } from "react";
import { pct, useCtx } from "../ctx";
import { GUARDRAILS, SCOPES, THRESHOLDS, UNITS, allDefinitions, share } from "../engine";
import { CopyLink, CsvLoader, Head, SourceBanner, Strip, useItems } from "../parts";
import type { Definition } from "../types";

const pick = <T,>(v: string | undefined, allowed: readonly T[], fallback: T): T =>
  (allowed.find((a) => String(a) === v) as T | undefined) ?? fallback;

export default function Lab() {
  const { t, lang, route, setParams } = useCtx();
  const h = useItems();
  const p = route.params;
  const d: Definition = {
    unit: pick(p.u, UNITS, "services"), scope: pick(p.s, SCOPES, "all-services"),
    threshold: pick(p.t, THRESHOLDS, 3), guardrails: pick(p.g, GUARDRAILS, "none"),
  };
  const result = share(h.items, d);
  const rows = useMemo(() => allDefinitions().map((x) => ({ d: x, share: share(h.items, x) })), [h.items]);
  const vals = rows.map((r) => r.share).filter((v): v is number => v !== null);
  const marg = <K extends keyof Definition>(key: K, values: readonly Definition[K][]) =>
    values.map((v) => {
      const sel = rows.filter((r) => r.d[key] === v && r.share !== null).map((r) => r.share as number);
      return { v, avg: sel.length ? sel.reduce((a, b) => a + b, 0) / sel.length : 0 };
    });
  const unitName = (u: string) => (t as unknown as Record<string, string>)[`u_${u}`];
  const scopeName = (s: Definition["scope"]) => ({ "citizen-services": t.s_citizen, "all-services": t.s_all, "services-and-operations": t.s_ops })[s];
  const seg = <K extends keyof Definition>(key: K, short: string, values: readonly Definition[K][], name: (v: Definition[K]) => string, label: string) => (
    <div className="field"><span id={`l-${key}`}>{label}</span>
      <div className="seg" role="group" aria-labelledby={`l-${key}`}>
        {values.map((v) => <button key={String(v)} aria-pressed={d[key] === v} onClick={() => setParams({ [short]: String(v) })}>{name(v)}</button>)}
      </div></div>
  );
  return (
    <>
      <Head title={t.lb_title} sub={t.lb_sub} />
      <SourceBanner kind={h.kind} />
      <CsvLoader h={h} />
      <section className="panel">
        <div className="cols">
          {seg("unit", "u", UNITS, (v) => unitName(v), t.lb_unit)}
          {seg("scope", "s", SCOPES, (v) => scopeName(v), t.lb_scope)}
          {seg("threshold", "t", THRESHOLDS, (v) => `L${v}`, t.lb_threshold)}
          {seg("guardrails", "g", GUARDRAILS, (v) => (v === "none" ? t.g_none : t.g_required), t.lb_guard)}
        </div>
        <p className="small">{t.lb_unit_help[d.unit]}</p>
        <div><CopyLink /></div>
      </section>
      <section className="panel" aria-live="polite">
        <div className="bigrow">
          <span className="big-share">{result === null ? "n/a" : pct(result, 1)}</span>
          <span>{t.lb_result} · {t.lb_vs}</span>
          {result !== null && <span className={`verdict ${result >= 0.5 ? "meets" : "misses"}`}>{result >= 0.5 ? t.lb_meets : t.lb_misses}</span>}
        </div>
        {result === null && <p className="small">{t.lb_nodata}</p>}
        <Strip current={d} rows={rows.map((r) => ({ share: r.share, d: r.d }))} label={t.lb_title} />
        <p className="small">{t.lb_sweep_ok}: {vals.length ? t.lb_range(pct(Math.min(...vals), 1), pct(Math.max(...vals), 1)) : "n/a"}</p>
      </section>
      <section className="panel">
        <h2>{t.lb_marginal_title}</h2><p className="small">{t.lb_marginal_note}</p>
        <div className="bars">
          {[
            ...marg("unit", UNITS).map((m) => ({ k: "u" + m.v, label: unitName(m.v as string), avg: m.avg })),
            ...marg("scope", SCOPES).map((m) => ({ k: "s" + m.v, label: scopeName(m.v as Definition["scope"]), avg: m.avg })),
            ...marg("threshold", THRESHOLDS).map((m) => ({ k: "t" + m.v, label: `${t.lb_threshold} L${m.v}`, avg: m.avg })),
            ...marg("guardrails", GUARDRAILS).map((m) => ({ k: "g" + m.v, label: `${t.lb_guard}: ${m.v === "none" ? t.g_none : lang === "ar" ? "مطلوبة" : "required"}`, avg: m.avg })),
          ].map((b) => (
            <div className="bar" key={b.k}><span>{b.label}</span>
              <span className="track"><span className={`fill${h.kind === "synthetic" ? " syn" : ""}`} style={{ width: `${b.avg * 100}%` }} /></span>
              <b>{pct(b.avg)}</b></div>
          ))}
        </div>
      </section>
    </>
  );
}

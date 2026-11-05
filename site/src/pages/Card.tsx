import { useMemo, useState } from "react";
import { download, useCtx } from "../ctx";
import { labLink, validateCard, type DefinitionCard } from "../card";
import { GUARDRAILS, SCOPES, THRESHOLDS, UNITS } from "../engine";
import { Head, SourceBanner } from "../parts";

const blank: DefinitionCard = {
  card_version: "1", title: "", headline_claim: "",
  definition: { unit: "services", scope: "all-services", threshold: 3, guardrails: "none" },
  as_of: new Date().toISOString().slice(0, 10), declared_by: "", notes: "", is_synthetic: true,
};

export default function Card() {
  const { t } = useCtx();
  const [card, setCard] = useState<DefinitionCard>(blank);
  const [badFile, setBadFile] = useState(false);
  const out = useMemo(() => ({ ...card, notes: card.notes ? card.notes : undefined }), [card]);
  const errors = useMemo(() => validateCard(out), [out]);
  const json = JSON.stringify(out, null, 1);
  const d = card.definition;
  const set = <K extends keyof DefinitionCard>(k: K, v: DefinitionCard[K]) => setCard({ ...card, [k]: v });
  const setDef = <K extends keyof typeof d>(k: K, v: (typeof d)[K]) => setCard({ ...card, definition: { ...d, [k]: v } });
  const unitName = (u: string) => (t as unknown as Record<string, string>)[`u_${u}`];
  const scopeName = (s: string) => ({ "citizen-services": t.s_citizen, "all-services": t.s_all, "services-and-operations": t.s_ops })[s as "all-services"];
  const onFile = async (f: File | undefined) => {
    if (!f) return;
    setBadFile(false);
    try {
      const raw = JSON.parse(await f.text());
      setCard({ ...blank, ...raw, notes: raw.notes ?? "" });
    } catch { setBadFile(true); }
  };
  return (
    <>
      <Head title={t.dc_title} sub={t.dc_sub} />
      <SourceBanner kind="synthetic" />
      <section className="panel" aria-labelledby="dc-form">
        <h2 id="dc-form">{t.dc_title}</h2>
        <label className="field">{t.dc_load}
          <input type="file" accept=".json,application/json" onChange={(e) => onFile(e.target.files?.[0])} /></label>
        <p className="small">{t.dc_load_help}</p>
        {badFile && <p className="small" role="alert">{t.dc_bad_file}</p>}
        <label className="field">{t.dc_claim_title}
          <input type="text" maxLength={120} value={card.title} onChange={(e) => set("title", e.target.value)} dir="auto" /></label>
        <label className="field">{t.dc_claim}
          <textarea rows={3} maxLength={400} value={card.headline_claim} onChange={(e) => set("headline_claim", e.target.value)} dir="auto" /></label>
        <div className="cols">
          <label className="field">{t.lb_unit}
            <select value={d.unit} onChange={(e) => setDef("unit", e.target.value as typeof d.unit)}>
              {UNITS.map((u) => <option key={u} value={u}>{unitName(u)}</option>)}</select></label>
          <label className="field">{t.lb_scope}
            <select value={d.scope} onChange={(e) => setDef("scope", e.target.value as typeof d.scope)}>
              {SCOPES.map((s) => <option key={s} value={s}>{scopeName(s)}</option>)}</select></label>
          <label className="field">{t.lb_threshold}
            <select value={d.threshold} onChange={(e) => setDef("threshold", Number(e.target.value) as typeof d.threshold)}>
              {THRESHOLDS.map((n) => <option key={n} value={n}>L{n}</option>)}</select></label>
          <label className="field">{t.lb_guard}
            <select value={d.guardrails} onChange={(e) => setDef("guardrails", e.target.value as typeof d.guardrails)}>
              {GUARDRAILS.map((g) => <option key={g} value={g}>{g === "none" ? t.g_none : t.g_required}</option>)}</select></label>
        </div>
        <div className="cols">
          <label className="field">{t.dc_by}
            <input type="text" maxLength={120} value={card.declared_by} onChange={(e) => set("declared_by", e.target.value)} dir="auto" /></label>
          <label className="field">{t.dc_asof}
            <input type="text" inputMode="numeric" value={card.as_of} onChange={(e) => set("as_of", e.target.value)} dir="ltr" /></label>
        </div>
        <label className="field">{t.dc_notes}
          <textarea rows={2} maxLength={500} value={card.notes ?? ""} onChange={(e) => set("notes", e.target.value)} dir="auto" /></label>
        <label className="check"><input type="checkbox" checked={card.is_synthetic} onChange={(e) => set("is_synthetic", e.target.checked)} /> {t.dc_synth}</label>
        <p className="small">{t.dc_synth_help}</p>
      </section>
      <section className="panel" aria-labelledby="dc-out" aria-live="polite">
        <h2 id="dc-out">{t.dc_preview}</h2>
        {errors.length === 0 ? <p><b>{t.dc_valid}</b></p> : (
          <div role="alert"><b>{t.dc_problems}</b><ul className="errlist">{errors.map((e) => <li key={e} className="mono" dir="ltr">{e}</li>)}</ul></div>
        )}
        <pre className="mono" dir="ltr" tabIndex={0} style={{ overflow: "auto", maxWidth: "100%" }}>{json}</pre>
        <div className="row">
          <button className="btn" disabled={errors.length > 0} onClick={() => download("definition-card.json", json + "\n", "application/json")}>{t.dc_download}</button>
          <a className="btn ghost" href={labLink(d)}>{t.dc_open_lab}</a>
        </div>
        <p className="small">{t.dc_schema}</p>
      </section>
    </>
  );
}

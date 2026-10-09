import { useCtx } from "./ctx";
import type { Score, Status } from "./types";

export function StatusPill({ s }: { s: Status["status"] }) {
  const { t } = useCtx();
  return <span className={`pill is-${s}${s === "not-checkable" ? " hatch" : ""}`}><i />{t.st[s]}</span>;
}

export function Ticks({ score }: { score: Score }) {
  const { t } = useCtx();
  const keys = Object.keys(t.checks) as (keyof typeof t.checks)[];
  const label = keys.map((k) => `${t.checks[k]}: ${score.checks[k] === null ? "n/a" : score.checks[k] ? "yes" : "no"}`).join("; ");
  return (
    <span className="ticks" role="img" aria-label={`${score.passed} / ${score.applicable}. ${label}`} title={label}>
      {keys.map((k) => <span key={k} className={score.checks[k] === null ? "na" : score.checks[k] ? "y" : "n"} />)}
    </span>
  );
}

export function SourceBanner({ kind }: { kind: "synthetic" | "yours" }) {
  const { t } = useCtx();
  return (
    <div className={`banner ${kind}`} role="note">
      <span className={`badge ${kind}`}>{kind === "synthetic" ? t.synthetic : t.yours}</span>
      <span>{kind === "synthetic" ? t.synthetic_long : t.yours_long}</span>
    </div>
  );
}

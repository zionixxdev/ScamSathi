import { AlertTriangle, CheckCircle2, Info, ShieldAlert } from "lucide-react";
import type { Indicator, Mitigator } from "../lib/types";

const SEVERITY_STYLES: Record<string, string> = {
  high: "text-risk-critical border-risk-critical/30 bg-risk-critical/10",
  medium: "text-risk-high border-risk-high/30 bg-risk-high/10",
  low: "text-risk-medium border-risk-medium/30 bg-risk-medium/10",
  info: "text-slate-300 border-white/10 bg-white/5",
};

export function IndicatorCards({ indicators }: { indicators: Indicator[] }) {
  if (indicators.length === 0) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-risk-low/25 bg-risk-low/10 p-4">
        <CheckCircle2 className="mt-0.5 shrink-0 text-risk-low" size={18} aria-hidden="true" />
        <p className="text-sm text-slate-300">
          No known warning sign matched. That means the engine found no red flags — it does not prove
          the message is genuine.
        </p>
      </div>
    );
  }

  return (
    <ul className="space-y-3">
      {indicators.map((indicator) => (
        <li
          key={indicator.id}
          className="rounded-xl border border-white/[0.07] bg-white/[0.03] p-4 transition hover:border-white/15"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              {indicator.severity === "high" ? (
                <ShieldAlert size={16} className="text-risk-critical" aria-hidden="true" />
              ) : (
                <AlertTriangle size={16} className="text-risk-high" aria-hidden="true" />
              )}
              <p className="text-sm font-semibold text-white">{indicator.label}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="chip uppercase tracking-wide">{indicator.source}</span>
              <span
                className={`rounded-full border px-2 py-0.5 font-mono text-[11px] ${
                  SEVERITY_STYLES[indicator.severity] ?? SEVERITY_STYLES.info
                }`}
              >
                +{indicator.weight}
              </span>
            </div>
          </div>
          {indicator.explanation && (
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{indicator.explanation}</p>
          )}
          {indicator.evidence && (
            <p className="mt-2 rounded-lg border border-white/5 bg-ink-950/60 px-3 py-2 font-mono text-xs leading-relaxed text-slate-400">
              {indicator.evidence}
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}

export function MitigatorList({ mitigators }: { mitigators: Mitigator[] }) {
  if (mitigators.length === 0) return null;
  return (
    <div className="rounded-xl border border-risk-low/20 bg-risk-low/[0.06] p-4">
      <p className="flex items-center gap-2 text-sm font-semibold text-risk-low">
        <Info size={16} aria-hidden="true" /> Signals that lowered the score
      </p>
      <ul className="mt-2 space-y-1.5">
        {mitigators.map((mitigator) => (
          <li key={mitigator.id} className="text-sm text-slate-400">
            <span className="text-slate-300">{mitigator.label}</span>
            {mitigator.explanation ? ` — ${mitigator.explanation}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}

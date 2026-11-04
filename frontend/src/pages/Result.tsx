import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  Bot,
  CheckCircle2,
  Link2,
  ListChecks,
  Trash2,
} from "lucide-react";
import RiskGauge from "../components/RiskGauge";
import RiskBadge from "../components/RiskBadge";
import { IndicatorCards, MitigatorList } from "../components/IndicatorList";
import ErrorBanner from "../components/ErrorBanner";
import Loading from "../components/Loading";
import { api } from "../lib/api";
import { recallResult, rememberResult, forgetResult } from "../lib/resultsCache";
import { channelLabel, formatDateTime } from "../lib/format";
import type { AnalysisResult } from "../lib/types";

export default function Result() {
  const { scanId = "" } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState<AnalysisResult | null>(() => recallResult(scanId));
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(!result);

  useEffect(() => {
    if (result || !scanId) return;
    let active = true;
    setLoading(true);
    api
      .scan(scanId)
      .then((data) => {
        if (!active) return;
        rememberResult(data);
        setResult(data);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(
          err instanceof Error
            ? err.message
            : "This analysis is no longer available. Scans saved to history can be reopened here.",
        );
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [scanId, result]);

  async function handleDelete() {
    if (!result) return;
    try {
      await api.deleteScan(result.scan_id);
    } catch {
      // The record may already be gone or was never stored.
    }
    forgetResult(result.scan_id);
    navigate("/history");
  }

  if (loading) return <Loading label="Loading analysis…" />;

  if (!result) {
    return (
      <div className="space-y-4">
        {error && <ErrorBanner message={error} />}
        <Link to="/scan/message" className="btn-ghost">
          <ArrowLeft size={15} /> Back to the scanner
        </Link>
      </div>
    );
  }

  const isUrl = result.scan_type === "url";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button type="button" onClick={() => navigate(-1)} className="btn-ghost">
          <ArrowLeft size={15} /> Back
        </button>
        <div className="flex items-center gap-2">
          <Link to={isUrl ? "/scan/url" : "/scan/message"} className="btn-ghost">
            New scan
          </Link>
          {result.stored && (
            <button type="button" onClick={handleDelete} className="btn-ghost text-risk-critical">
              <Trash2 size={15} /> Delete
            </button>
          )}
        </div>
      </div>

      <section className="glass-strong animate-fade-up p-5 sm:p-6">
        <div className="grid gap-6 sm:grid-cols-[200px_1fr] sm:items-center">
          <RiskGauge score={result.risk_score} level={result.risk_level} confidence={result.confidence} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <RiskBadge level={result.risk_level} size="md" />
              <span className="chip">{result.category.label}</span>
              <span className="chip">{isUrl ? "Link" : channelLabel(result.channel)}</span>
              <span className="chip">Language: {result.language.toUpperCase()}</span>
              {!result.stored && <span className="chip">Not saved</span>}
            </div>
            <h1 className="mt-3 text-xl font-semibold tracking-tight text-white sm:text-2xl">
              {result.risk_level === "Low"
                ? "No strong warning signs found"
                : result.risk_level === "Uncertain"
                  ? "Not enough signal to be sure"
                  : "Treat this as unsafe"}
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">{result.explanation}</p>
            <p className="mt-3 text-xs text-slate-500">
              Scanned {formatDateTime(result.created_at)} · scan id{" "}
              <span className="font-mono">{result.scan_id.slice(0, 8)}</span>
            </p>
          </div>
        </div>

        {result.uncertainty && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-risk-uncertain/25 bg-risk-uncertain/10 p-4">
            <AlertTriangle size={17} className="mt-0.5 shrink-0 text-risk-uncertain" aria-hidden="true" />
            <p className="text-sm text-slate-300">{result.uncertainty}</p>
          </div>
        )}

        {result.secondary_categories.length > 0 && (
          <p className="mt-4 text-xs text-slate-500">
            Close alternatives considered:{" "}
            {result.secondary_categories.map((item) => `${item.label} (${item.score})`).join(", ")}
          </p>
        )}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <div className="space-y-4">
          <div className="glass p-5">
            <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
              Warning indicators ({result.indicators.length})
            </h2>
            <div className="mt-4">
              <IndicatorCards indicators={result.indicators} />
            </div>
            <div className="mt-4">
              <MitigatorList mitigators={result.mitigators} />
            </div>
          </div>

          {result.url_analysis && (
            <div className="glass p-5">
              <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
                <Link2 size={14} aria-hidden="true" /> Link analysis
              </h2>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div className="col-span-2">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Host</dt>
                  <dd className="mt-0.5 break-all font-mono text-xs text-slate-200">
                    {result.url_analysis.host}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-500">HTTPS</dt>
                  <dd className="mt-0.5 text-slate-200">{result.url_analysis.https ? "Yes" : "No"}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Shortener</dt>
                  <dd className="mt-0.5 text-slate-200">{result.url_analysis.is_shortener ? "Yes" : "No"}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Lookalike of</dt>
                  <dd className="mt-0.5 text-slate-200">
                    {result.url_analysis.lookalike_of ? result.url_analysis.lookalike_of.toUpperCase() : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Reputation</dt>
                  <dd className="mt-0.5 text-slate-200">
                    {result.url_analysis.reputation.checked ? "Checked" : "Not checked"}
                  </dd>
                </div>
              </dl>
              <p className="mt-3 rounded-lg border border-white/5 bg-ink-950/60 p-3 text-xs leading-relaxed text-slate-400">
                {result.url_analysis.reputation.note}
              </p>
              {result.url_analysis.findings.length > 0 && (
                <ul className="mt-4 space-y-2">
                  {result.url_analysis.findings.map((finding) => (
                    <li
                      key={finding.id}
                      className="rounded-lg border border-white/[0.07] bg-white/[0.03] px-3 py-2"
                    >
                      <p className="flex items-center justify-between gap-2 text-xs font-semibold text-slate-200">
                        {finding.label}
                        <span className="font-mono text-[11px] text-slate-500">+{finding.weight}</span>
                      </p>
                      {finding.evidence && (
                        <p className="mt-1 break-all font-mono text-[11px] text-slate-500">{finding.evidence}</p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              <p className="mt-3 text-[11px] leading-relaxed text-slate-500">{result.url_analysis.disclaimer}</p>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="glass p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
              <ListChecks size={14} aria-hidden="true" /> What to do now
            </h2>
            <ol className="mt-4 space-y-3">
              {result.recommended_actions.map((action, index) => (
                <li key={action} className="flex gap-3 text-sm leading-relaxed text-slate-300">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent/10 font-mono text-[11px] text-accent">
                    {index + 1}
                  </span>
                  {action}
                </li>
              ))}
            </ol>
          </div>

          <div className="glass p-5">
            <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">Content analysed</h2>
            <p className="mt-3 rounded-lg border border-white/5 bg-ink-950/60 p-3 font-mono text-xs leading-relaxed text-slate-400">
              {result.excerpt || "(empty)"}
            </p>
            <p className="mt-2 text-[11px] leading-relaxed text-slate-500">
              This preview is redacted: OTPs, card and account numbers, emails and phone numbers are masked
              before storage.
            </p>
          </div>

          <div className="glass p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
              <Bot size={14} aria-hidden="true" /> Engine
            </h2>
            <ul className="mt-3 space-y-2 text-xs leading-relaxed text-slate-400">
              <li className="flex items-start gap-2">
                <CheckCircle2 size={13} className="mt-0.5 shrink-0 text-risk-low" aria-hidden="true" />
                Rule engine and NLP layer always run locally.
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 size={13} className="mt-0.5 shrink-0 text-risk-low" aria-hidden="true" />
                {result.ai.used
                  ? `Contextual AI applied (${result.ai.provider}), adjustment ${result.ai.score_adjustment > 0 ? "+" : ""}${result.ai.score_adjustment}.`
                  : "No contextual AI was used for this scan."}
              </li>
            </ul>
            {result.ai.rationale && (
              <p className="mt-3 rounded-lg border border-white/5 bg-ink-950/60 p-3 text-xs leading-relaxed text-slate-300">
                {result.ai.rationale}
              </p>
            )}
            {result.ai.note && <p className="mt-2 text-[11px] leading-relaxed text-slate-500">{result.ai.note}</p>}
          </div>

          <div className="rounded-xl border border-risk-medium/25 bg-risk-medium/[0.07] p-4 text-[11px] leading-relaxed text-slate-300">
            {result.disclaimer}
          </div>
        </div>
      </section>
    </div>
  );
}

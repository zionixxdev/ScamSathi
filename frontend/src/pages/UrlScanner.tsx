import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Link2, Loader2, ShieldAlert, ShieldCheck } from "lucide-react";
import ErrorBanner from "../components/ErrorBanner";
import { api } from "../lib/api";
import { rememberResult } from "../lib/resultsCache";

const SAMPLES = [
  { label: "Lookalike domain", url: "http://sbi-kyc-verify.top/update" },
  { label: "Shortened link", url: "https://bit.ly/3xYzAbc" },
  { label: "Official domain", url: "https://www.sbi.co.in/" },
  { label: "Brand in subdomain", url: "https://sbi.co.in.secure-login.xyz/kyc" },
];

const CHECKS = [
  "Domain structure, length and subdomain depth",
  "Lookalike and typosquatted brand names",
  "Shorteners, punycode and raw IP addresses",
  "Bait paths such as /kyc-update or /login",
  "HTTPS — reported, but never treated as proof of safety",
];

export default function UrlScanner() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [store, setStore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = url.trim().length > 0 && !loading;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.analyzeUrl(url.trim(), store);
      rememberResult(result);
      navigate(`/result/${result.scan_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The scan failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">URL scanner</h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          The link is analysed as text. ScamSathi never opens it, never resolves it and never follows a
          redirect — so a malicious page cannot reach you through this tool.
        </p>
      </header>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <form onSubmit={handleSubmit} className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <div className="glass p-5">
          <label className="label" htmlFor="url">
            Link to analyse
          </label>
          <input
            id="url"
            type="text"
            inputMode="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            maxLength={2048}
            placeholder="https://example.com/kyc-update"
            className="input font-mono text-[13px]"
            required
            spellCheck={false}
            autoComplete="off"
          />
          <p className="mt-2 text-xs text-slate-500">
            Only http and https links can be analysed. Query strings are stripped before anything is
            stored or, if enabled, sent to a reputation service.
          </p>

          <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
            <input
              type="checkbox"
              checked={store}
              onChange={(event) => setStore(event.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-white/20 bg-ink-900 text-accent focus:ring-accent"
            />
            <span className="text-xs leading-relaxed text-slate-400">
              Save this scan to my history (host and score only, no page content).
            </span>
          </label>

          <button type="submit" className="btn-primary mt-5 w-full" disabled={!canSubmit}>
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Analysing…
              </>
            ) : (
              <>
                <Link2 size={16} /> Analyse link
              </>
            )}
          </button>

          <div className="mt-5 flex flex-wrap gap-2">
            {SAMPLES.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => {
                  setUrl(sample.url);
                  setError(null);
                }}
                className="chip transition hover:border-accent/40 hover:text-white"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="glass p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
              <ShieldCheck size={15} className="text-accent-mint" aria-hidden="true" /> What gets checked
            </h2>
            <ul className="mt-3 space-y-2 text-xs leading-relaxed text-slate-400">
              {CHECKS.map((check) => (
                <li key={check}>• {check}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-risk-high/25 bg-risk-high/[0.07] p-4">
            <p className="flex items-center gap-2 text-xs font-semibold text-risk-high">
              <ShieldAlert size={14} aria-hidden="true" /> HTTPS is not a safety certificate
            </p>
            <p className="mt-1.5 text-xs leading-relaxed text-slate-300">
              Anyone can obtain a free certificate. A padlock means the connection is encrypted, not that
              the site is honest.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-xs leading-relaxed text-slate-400">
            No reputation provider is configured by default, and the result will say so. ScamSathi never
            pretends a link was checked against a database when it was not.
          </div>
        </aside>
      </form>
    </div>
  );
}

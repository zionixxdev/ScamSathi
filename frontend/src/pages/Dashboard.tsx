import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  Gauge,
  Link2,
  MessageSquareWarning,
  RefreshCw,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import StatCard from "../components/StatCard";
import { CategoryDonut, RiskBars } from "../components/CategoryChart";
import RiskBadge from "../components/RiskBadge";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { api } from "../lib/api";
import { channelLabel, formatRelative } from "../lib/format";
import type { Stats } from "../lib/types";

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setStats(await api.stats());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">Security dashboard</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
            Your own scans, your own numbers. No platform-wide statistics are shown or invented.
          </p>
        </div>
        <button type="button" onClick={load} className="btn-ghost" disabled={loading}>
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </header>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {loading && !stats ? (
        <Loading label="Loading your dashboard…" />
      ) : (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Total scans"
              value={stats?.total_scans ?? 0}
              hint="Scans stored for this browser profile."
              icon={Activity}
            />
            <StatCard
              label="High risk"
              value={stats?.high_risk_scans ?? 0}
              hint="High and Critical detections."
              icon={ShieldAlert}
              accent="text-risk-critical"
            />
            <StatCard
              label="Categories seen"
              value={stats?.by_category.length ?? 0}
              hint="Distinct scam categories in your history."
              icon={Gauge}
              accent="text-risk-medium"
            />
            <StatCard
              label="Privacy mode"
              value="Anonymous"
              hint="No account, no email, no raw content stored."
              icon={Sparkles}
              accent="text-accent-mint"
            />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <div className="glass p-5">
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
                Category distribution
              </h2>
              <div className="mt-5">
                <CategoryDonut data={stats?.by_category ?? []} />
              </div>
            </div>
            <div className="glass p-5">
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
                Risk level mix
              </h2>
              <div className="mt-5">
                <RiskBars data={stats?.by_risk_level ?? {}} />
              </div>
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
            <div className="glass p-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">
                  Recent analyses
                </h2>
                <Link to="/history" className="text-xs font-semibold text-accent hover:underline">
                  View all
                </Link>
              </div>
              <div className="mt-4">
                {stats && stats.recent.length > 0 ? (
                  <ul className="divide-y divide-white/[0.06]">
                    {stats.recent.map((item) => (
                      <li key={item.scan_id}>
                        <Link
                          to={`/result/${item.scan_id}`}
                          className="flex items-start justify-between gap-3 py-3 transition hover:bg-white/[0.02]"
                        >
                          <div className="min-w-0">
                            <p className="truncate text-sm text-slate-300">{item.excerpt || "(no preview)"}</p>
                            <p className="mt-1 text-xs text-slate-500">
                              {item.category.label} · {channelLabel(item.channel)} · {formatRelative(item.created_at)}
                            </p>
                          </div>
                          <RiskBadge level={item.risk_level} score={item.risk_score} />
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <EmptyState
                    icon={MessageSquareWarning}
                    title="No scans yet"
                    description="Run your first scan and it will appear here with its risk level and category."
                    action={
                      <Link to="/scan/message" className="btn-primary">
                        Scan a message <ArrowRight size={15} />
                      </Link>
                    }
                  />
                )}
              </div>
            </div>

            <div className="glass p-5">
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-400">Quick scan</h2>
              <div className="mt-4 space-y-3">
                <Link
                  to="/scan/message"
                  className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-accent/30 hover:bg-accent/5"
                >
                  <span className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-accent">
                    <MessageSquareWarning size={16} aria-hidden="true" />
                  </span>
                  <span>
                    <span className="block text-sm font-semibold text-white">Scan a message</span>
                    <span className="block text-xs text-slate-500">SMS, WhatsApp, email, job offer</span>
                  </span>
                </Link>
                <Link
                  to="/scan/url"
                  className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-accent/30 hover:bg-accent/5"
                >
                  <span className="rounded-lg border border-white/10 bg-white/[0.04] p-2 text-accent-mint">
                    <Link2 size={16} aria-hidden="true" />
                  </span>
                  <span>
                    <span className="block text-sm font-semibold text-white">Check a link</span>
                    <span className="block text-xs text-slate-500">Never opened, analysed as text</span>
                  </span>
                </Link>
              </div>
              {stats?.note && <p className="mt-4 text-[11px] leading-relaxed text-slate-500">{stats.note}</p>}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

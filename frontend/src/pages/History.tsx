import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, History as HistoryIcon, RefreshCw, Trash2 } from "lucide-react";
import RiskBadge from "../components/RiskBadge";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import { api } from "../lib/api";
import { channelLabel, formatDateTime } from "../lib/format";
import { forgetResult } from "../lib/resultsCache";
import type { HistoryItem, HistoryPage } from "../lib/types";

const FILTERS = ["All", "Critical", "High", "Medium", "Low", "Uncertain"];
const PAGE_SIZE = 20;

export default function History() {
  const [page, setPage] = useState<HistoryPage | null>(null);
  const [filter, setFilter] = useState("All");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPage(
        await api.history({
          limit: PAGE_SIZE,
          offset,
          risk_level: filter === "All" ? undefined : filter,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load your scan history.");
    } finally {
      setLoading(false);
    }
  }, [filter, offset]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleDelete(item: HistoryItem) {
    try {
      await api.deleteScan(item.scan_id);
      forgetResult(item.scan_id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete this record.");
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">Scan history</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
            Stored against an anonymous id in this browser only. Delete any record permanently at any time.
          </p>
        </div>
        <button type="button" onClick={load} className="btn-ghost" disabled={loading}>
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </header>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by risk level">
        {FILTERS.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => {
              setFilter(option);
              setOffset(0);
            }}
            aria-pressed={filter === option}
            className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
              filter === option
                ? "border-accent/40 bg-accent/10 text-white"
                : "border-white/10 bg-white/[0.03] text-slate-400 hover:text-slate-200"
            }`}
          >
            {option}
          </button>
        ))}
      </div>

      {loading && !page ? (
        <Loading label="Loading history…" />
      ) : page && page.items.length === 0 ? (
        <EmptyState
          icon={HistoryIcon}
          title={filter === "All" ? "No scans yet" : `No ${filter.toLowerCase()} scans`}
          description="Every scan you save appears here with its risk level, category and a redacted preview."
          action={
            <Link to="/scan/message" className="btn-primary">
              Run a scan <ArrowRight size={15} />
            </Link>
          }
        />
      ) : (
        <>
          <ul className="space-y-3">
            {page?.items.map((item) => (
              <li key={item.scan_id} className="glass p-4 transition hover:border-white/15">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <Link to={`/result/${item.scan_id}`} className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <RiskBadge level={item.risk_level} score={item.risk_score} />
                      <span className="chip">{item.category.label}</span>
                      <span className="chip">{channelLabel(item.channel)}</span>
                    </div>
                    <p className="mt-2 line-clamp-2 text-sm text-slate-300">{item.excerpt || "(no preview)"}</p>
                    <p className="mt-1.5 text-xs text-slate-500">
                      {formatDateTime(item.created_at)} · confidence {Math.round(item.confidence * 100)}%
                    </p>
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleDelete(item)}
                    className="rounded-lg border border-white/10 p-2 text-slate-500 transition hover:border-risk-critical/40 hover:text-risk-critical"
                    aria-label="Delete this scan"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {page && page.total > PAGE_SIZE && (
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>
                Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, page.total)} of {page.total}
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn-ghost px-3 py-1.5 text-xs"
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  disabled={offset === 0}
                >
                  Previous
                </button>
                <button
                  type="button"
                  className="btn-ghost px-3 py-1.5 text-xs"
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                  disabled={offset + PAGE_SIZE >= page.total}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

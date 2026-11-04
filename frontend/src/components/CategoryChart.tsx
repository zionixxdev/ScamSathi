import type { Stats } from "../lib/types";

const PALETTE = ["#22d3ee", "#34d399", "#a78bfa", "#fbbf24", "#fb923c", "#f43f5e", "#38bdf8", "#818cf8"];

export function CategoryDonut({ data }: { data: Stats["by_category"] }) {
  const total = data.reduce((sum, item) => sum + item.count, 0);
  if (total === 0) {
    return (
      <p className="py-10 text-center text-sm text-slate-500">
        No scans yet. Run a scan to see your category breakdown.
      </p>
    );
  }

  let offset = 0;
  const radius = 60;
  const circumference = 2 * Math.PI * radius;

  return (
    <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-center">
      <svg viewBox="0 0 160 160" className="h-40 w-40 shrink-0" role="img" aria-label="Scam category distribution">
        <circle cx="80" cy="80" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="18" />
        {data.map((item, index) => {
          const fraction = item.count / total;
          const dash = fraction * circumference;
          const circle = (
            <circle
              key={item.category}
              cx="80"
              cy="80"
              r={radius}
              fill="none"
              stroke={PALETTE[index % PALETTE.length]}
              strokeWidth="18"
              strokeDasharray={`${dash} ${circumference - dash}`}
              strokeDashoffset={-offset}
              transform="rotate(-90 80 80)"
            />
          );
          offset += dash;
          return circle;
        })}
        <text x="80" y="76" textAnchor="middle" className="fill-white" style={{ fontSize: 22, fontWeight: 600 }}>
          {total}
        </text>
        <text x="80" y="94" textAnchor="middle" className="fill-slate-500" style={{ fontSize: 9, letterSpacing: 1.5 }}>
          SCANS
        </text>
      </svg>
      <ul className="w-full space-y-2">
        {data.slice(0, 6).map((item, index) => (
          <li key={item.category} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex min-w-0 items-center gap-2">
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ background: PALETTE[index % PALETTE.length] }}
                aria-hidden="true"
              />
              <span className="truncate text-slate-300">{item.label}</span>
            </span>
            <span className="font-mono text-xs text-slate-500">{item.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function RiskBars({ data }: { data: Record<string, number> }) {
  const levels = ["Critical", "High", "Medium", "Uncertain", "Low"];
  const total = Object.values(data).reduce((sum, value) => sum + value, 0);
  if (total === 0) {
    return <p className="py-6 text-center text-sm text-slate-500">No scans recorded yet.</p>;
  }
  const colors: Record<string, string> = {
    Critical: "bg-risk-critical",
    High: "bg-risk-high",
    Medium: "bg-risk-medium",
    Uncertain: "bg-risk-uncertain",
    Low: "bg-risk-low",
  };
  return (
    <ul className="space-y-3">
      {levels.map((level) => {
        const value = data[level] ?? 0;
        const width = total ? Math.round((value / total) * 100) : 0;
        return (
          <li key={level}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-slate-400">{level}</span>
              <span className="font-mono text-slate-500">{value}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
              <div className={`h-full rounded-full ${colors[level]}`} style={{ width: `${width}%` }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
